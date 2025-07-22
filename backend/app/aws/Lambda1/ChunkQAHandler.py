import os
import json
import tempfile
import boto3
import re
from pathlib import Path
from pypdf import PdfReader
from transformers import AutoTokenizer
import numpy as np
from groq import Groq
import ast
import time
import zipfile
import spacy

# --- S3 Setup ---
s3_client = boto3.client("s3")
OUTPUT_BUCKET = "lazyai-output"
dynamodb = boto3.resource("dynamodb")
track_table = dynamodb.Table("lazyai-track-user-input")

# --- spaCy for PII Redaction ---
nlp = spacy.load("en_core_web_md")
PII_LABELS = {"PERSON", "GPE", "ORG", "LOC", "EMAIL", "DATE", "TIME", "MONEY", "CARDINAL"}

def redact_entities(text, doc):
    redacted = text
    offset = 0
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG"]:
            start = ent.start_char + offset
            end = ent.end_char + offset
            length = end - start
            redacted = redacted[:start] + "[REDACTED]" + redacted[end:]
            offset += len("[REDACTED]") - length
    return redacted

def redact_emails_and_phones(text):
    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[REDACTED]", text)
    phone_patterns = [
        r"\b\d{10,15}\b",
        r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b"
    ]
    for pattern in phone_patterns:
        text = re.sub(pattern, "[REDACTED]", text)
    return text

# --- PDF Extraction ---
def extract_text_from_pdf_local(filepath):
    text = ""
    try:
        reader = PdfReader(filepath)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"[ERROR] Failed to read {filepath}: {e}")
    return text
# Function to download model from S3
def download_model_from_s3(bucket_name, s3_key, local_path):
    s3_client.download_file(bucket_name, s3_key, local_path)
    print(f"Downloaded {s3_key} to {local_path}")

def load_model():
    model_name = "unsloth/Llama-3.2-3B-Instruct"
    cache_dir = "/tmp/huggingface_cache"
    # Remove any local directory with the same name to force download from Hugging Face
    local_model_dir = os.path.join(os.getcwd(), model_name)
    if os.path.isdir(local_model_dir):
        print(f"[INFO] Removing local directory {local_model_dir} to avoid loading incomplete files.")
        shutil.rmtree(local_model_dir)
    os.makedirs(cache_dir, exist_ok=True)
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        print("[INFO] Tokenizer loaded successfully from Hugging Face Hub.")
    except Exception as e:
        print(f"[ERROR] Failed to load tokenizer: {e}")
        raise
    return tokenizer

# --- Chunking (token-based) ---
class SyntheticDataChunker:
    def __init__(self, max_seq_length=2048, max_generation_tokens=512, overlap=64):
        self.tokenizer = load_model()
        self.max_seq_length = max_seq_length
        self.max_generation_tokens = max_generation_tokens
        self.overlap = overlap

    def chunk_data(self, text):
        max_tokens = self.max_seq_length - self.max_generation_tokens * 2 - 128
        input_ids = self.tokenizer(text, add_special_tokens=False).input_ids
        length = len(input_ids)
        n_chunks = int(np.ceil(length / (max_tokens - self.overlap)))
        boundaries = np.ceil(np.linspace(0, length - self.overlap, n_chunks)).astype(int)
        boundaries = np.stack((boundaries[:-1], (boundaries + self.overlap)[1:])).T
        boundaries = np.minimum(boundaries, length).tolist()
        chunks = [self.tokenizer.decode(input_ids[left:right]) for left, right in boundaries]
        return chunks

# --- Cleaning ---
def clean_text_ignore_redacted(text):
    cleaned_lines = []
    for line in text.splitlines():
        tokens = line.split()
        redacted_count = sum(1 for t in tokens if t == "[REDACTED]")
        if len(tokens) == 0 or redacted_count / max(1, len(tokens)) > 0.5:
            continue
        cleaned_lines.append(line.replace("[REDACTED]", "").strip())
    return "\n".join(cleaned_lines)

# --- QA Extraction Helpers ---
def fix_unescaped_quotes(json_str):
    # Handle leading zeros and string formatting
    json_str = re.sub(r'(?<=\d)0+(\d)', r'\1', json_str)  # Fix numbers with leading zeros
    json_str = re.sub(r'"([^"]*?)"', r'"\1"', json_str)  # Ensure proper quote usage
    return json_str

def extract_qa_pairs_regex(text):
    qa_pairs = []
    pattern = re.compile(r'\{\s*"question"\s*:\s*"(.*?)"\s*,\s*"answer"\s*:\s*"(.*?)"\s*\}')
    for match in pattern.finditer(text):
        question = match.group(1).replace('"', "'")
        answer = match.group(2).replace('"', "'")
        qa_pairs.append({"question": question, "answer": answer})
    if qa_pairs:
        print(f"[FALLBACK] Extracted {len(qa_pairs)} QA pairs using regex fallback.")
    else:
        print("[FALLBACK] No QA pairs could be extracted using regex fallback.")
    return qa_pairs

def extract_json_array(response_text):
    start_idx = response_text.find('[')
    end_idx = response_text.rfind(']') + 1
    if start_idx == -1 or end_idx == -1:
        print("[WARN] Could not find JSON array in response. Attempting regex fallback.")
        return extract_qa_pairs_regex(response_text)
    json_str = response_text[start_idx:end_idx]
    json_str = re.sub(r',\s*\]', ']', json_str)
    json_str = json_str.replace("'", '"')
    json_str = re.sub(r'\n', ' ', json_str)
    json_str = fix_unescaped_quotes(json_str)
    try:
        return json.loads(json_str)
    except Exception:
        try:
            return ast.literal_eval(json_str)
        except Exception as e:
            print(f"[ERROR] Still failed to parse JSON: {e}")
            print(f"[ERROR] Raw JSON string: {json_str[:200]}...")
            print("[WARN] Attempting regex fallback.")
            return extract_qa_pairs_regex(json_str)

def generate_qa_pairs_from_text_groq(
    text,
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    num_pairs=25,
    api_key=None
):
    if api_key is None:
        api_key = "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"
    max_chars = 2000
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
    prompt = f"""Create {num_pairs} question-answer pairs from this text. Return only a JSON array like this:\n[\n  {{\"question\": \"What is the main topic?\", \"answer\": \"The main topic is...\"}},\n  {{\"question\": \"What are the key points?\", \"answer\": \"The key points are...\"}}\n]\n\nText: {text}"""
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    response_text = completion.choices[0].message.content
    qa_pairs = extract_json_array(response_text)
    if qa_pairs:
        return qa_pairs
    else:
        print(f"[ERROR] Could not parse QA pairs from model output.")
        print(f"[ERROR] Response preview: {response_text[:200]}...")
        return []

# --- Get folder name from ZIP file key ---
def get_folder_name_from_zip(zip_key):
    """Extract folder name from ZIP file key."""
    # Remove .zip extension and any path prefixes
    zip_filename = os.path.basename(zip_key)
    folder_name = os.path.splitext(zip_filename)[0]
    return folder_name


# --- Lambda Handler ---
def lambda_handler(event, context):
    print("[START] Lambda handler invoked")
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        if key.lower().endswith(".zip"):
            print(f"[EVENT] Triggered by ZIP file: {bucket}/{key}")
            temp_dir = tempfile.mkdtemp()
            tmp_zip_path = os.path.join(temp_dir, os.path.basename(key))
            s3_client.download_file(bucket, key, tmp_zip_path)
            folder_name = get_folder_name_from_zip(key)
            try:
                with zipfile.ZipFile(tmp_zip_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                all_qa_pairs = []
                chunker = SyntheticDataChunker(max_seq_length=2048, max_generation_tokens=512, overlap=64)
                # Walk temp_dir for all PDFs (skip system files)
                for root, dirs, files in os.walk(temp_dir):
                    for filename in files:
                        if filename.lower().endswith(".pdf") and not filename.startswith("._"):
                            pdf_path = os.path.join(root, filename)
                            print(f"[INFO] Processing PDF in ZIP: {filename}")
                            extracted_text = extract_text_from_pdf_local(pdf_path)
                            if not extracted_text.strip():
                                print(f"[WARN] No extractable text in {filename}. Skipping.")
                                continue
                            # Redact PII before chunking
                            doc = nlp(extracted_text)
                            redacted_text = redact_entities(extracted_text, doc)
                            redacted_text = redact_emails_and_phones(redacted_text)
                            chunks = chunker.chunk_data(redacted_text)
                            for idx, chunk in enumerate(chunks):
                                cleaned_chunk = clean_text_ignore_redacted(chunk)
                                if not cleaned_chunk.strip() or len(cleaned_chunk.strip()) < 30:
                                    print(f"[WARN] Skipping empty or too-short chunk {idx} in {filename}")
                                    continue
                                qa_pairs = generate_qa_pairs_from_text_groq(cleaned_chunk, num_pairs=25)
                                for qa in qa_pairs:
                                    qa["source_file"] = filename
                                    qa["chunk_index"] = idx
                                all_qa_pairs.extend(qa_pairs)
                qa_output_key = f"{folder_name}/{os.path.splitext(key)[0]}_qa_pairs.json"
                s3_client.put_object(
                    Bucket=OUTPUT_BUCKET,
                    Key=qa_output_key,
                    Body=json.dumps(all_qa_pairs, indent=2),
                    ContentType="application/json"
                )
                print(f"[SUCCESS] Saved {len(all_qa_pairs)} QA pairs to s3://{OUTPUT_BUCKET}/{qa_output_key}")
            finally:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            print(f"[SKIPPED] Not a .zip file: {key}")
    return {"statusCode": 200, "body": "Processing complete."}
