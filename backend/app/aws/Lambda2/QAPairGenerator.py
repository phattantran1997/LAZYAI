import os
import json
import tempfile
import boto3
import re
from pathlib import Path
from pypdf import PdfReader
import spacy
from transformers import AutoTokenizer
import numpy as np
from groq import Groq
import time
import ast

# --- S3 Setup ---
s3_client = boto3.client("s3")
INPUT_BUCKET = "lazyai-output-chunkdata"
OUTPUT_BUCKET = "lazyai-output"

# --- PII Redaction with spaCy ---
nlp = spacy.load("en_core_web_sm")
PII_LABELS = {"PERSON", "GPE", "ORG", "LOC", "EMAIL", "DATE", "TIME", "MONEY", "CARDINAL"}

def redact_pii(text):
    doc = nlp(text)
    redacted = text
    for ent in reversed(doc.ents):
        if ent.label_ in PII_LABELS:
            redacted = redacted[:ent.start_char] + "[REDACTED]" + redacted[ent.end_char:]
    return redacted

# --- PDF Extraction ---
def extract_text_from_pdf(pdf_content):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file.write(pdf_content)
        temp_path = temp_file.name
    reader = PdfReader(temp_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    os.unlink(temp_path)
    return text.strip()

# --- Chunking (token-based) ---
class SyntheticDataChunker:
    def __init__(self, model_name="llama3-3b-instruct", max_seq_length=2048, max_generation_tokens=512, overlap=64):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "..", "..", "..", model_name)
        model_path = os.path.abspath(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
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

def clean_text_ignore_redacted(text):
    """Remove heavily redacted lines and strip leftover [REDACTED] tags."""
    cleaned_lines = []
    for line in text.splitlines():
        tokens = line.split()
        redacted_count = sum(1 for t in tokens if t == "[REDACTED]")
        if len(tokens) == 0 or redacted_count / max(1, len(tokens)) > 0.5:
            continue
        cleaned_lines.append(line.replace("[REDACTED]", "").strip())
    return "\n".join(cleaned_lines)

def fix_unescaped_quotes(json_str):
    def replacer(match):
        inner = match.group(1)
        return '"' + inner.replace('"', "'") + '"'
    return re.sub(r'"([^"\n]*?)"(?=,|\})', replacer, json_str)

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

# --- QA Generation (Groq) ---
def generate_qa_pairs_from_text_groq(
    text,
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    num_pairs=25,
    api_key=None
):
    if api_key is None:
        api_key = os.environ.get("GROQ_API_KEY")
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

# --- Main Pipeline ---
def process_pdf_from_s3(s3_key, chunker, num_pairs=25, model="meta-llama/llama-4-scout-17b-16e-instruct", api_key=None):
    print(f"[INFO] Processing file {s3_key}")
    pdf_data = s3_client.get_object(Bucket=INPUT_BUCKET, Key=s3_key)["Body"].read()
    text = extract_text_from_pdf(pdf_data)
    redacted_text = redact_pii(text)
    chunks = chunker.chunk_data(redacted_text)
    all_qa_pairs = []
    for idx, chunk in enumerate(chunks):
        cleaned_chunk = clean_text_ignore_redacted(chunk)
        if not cleaned_chunk.strip() or len(cleaned_chunk.strip()) < 30:
            print(f"[WARN] Skipping empty or too-short chunk {idx} in {s3_key}")
            continue
        qa_pairs = generate_qa_pairs_from_text_groq(cleaned_chunk, num_pairs=num_pairs, model=model, api_key=api_key)
        for qa in qa_pairs:
            qa["source_file"] = s3_key
            qa["chunk_index"] = idx
        all_qa_pairs.extend(qa_pairs)
    return all_qa_pairs

def save_to_s3(qa_pairs, output_key):
    s3_client.put_object(
        Bucket=OUTPUT_BUCKET,
        Key=output_key,
        Body=json.dumps(qa_pairs, indent=2),
        ContentType="application/json"
    )
    print(f"[SUCCESS] Saved {len(qa_pairs)} QA pairs to s3://{OUTPUT_BUCKET}/{output_key}")

