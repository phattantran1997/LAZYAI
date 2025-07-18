import boto3
import json
import os
import tempfile
from datetime import datetime
from pypdf import PdfReader
from sagemaker.predictor import retrieve_default
import re

# AWS config
s3_client = boto3.client("s3")
ENDPOINT_NAME = "jumpstart-dft-meta-textgeneration-l-20250718-042336"
INPUT_BUCKET = "lazyai-output-chunkdata"
OUTPUT_BUCKET = "lazyai-output"

# QA generation config
QA_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_generation_tokens": 512,
    "num_questions_per_doc": 5,
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "max_text_length": 2000,
    "retry_count": 2
}

def clean_text_ignore_redacted(text):
    """Loại bỏ các đoạn chứa [REDACTED] (ẩn PII) trước khi gửi sang LLM."""
    cleaned_lines = []
    for line in text.splitlines():
        tokens = line.split()
        redacted_count = sum(1 for t in tokens if t == "[REDACTED]")
        if len(tokens) == 0 or redacted_count / max(1, len(tokens)) > 0.5:
            continue
        line_cleaned = line.replace("[REDACTED]", "").strip()
        if line_cleaned:
            cleaned_lines.append(line_cleaned)
    return "\n".join(cleaned_lines)

def chunk_text(text, chunk_size=1000, overlap=200):
    """Chunk văn bản theo kiểu Unsloth: giữ ngữ cảnh, bỏ đoạn quá ngắn, làm sạch spacing."""
    text = clean_text_ignore_redacted(text)
    text = re.sub(r'\s+', ' ', text).strip()

    if not text:
        return []

    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        # cắt tại dấu câu gần cuối chunk để tự nhiên hơn
        while end < len(text) and end > start and text[end-1] not in '.!?':
            end -= 1
        if end <= start:
            end = min(len(text), start + chunk_size)

        chunk = text[start:end].strip()
        if len(chunk) > 50:  # bỏ đoạn quá ngắn
            chunks.append(chunk)
        start = max(end - overlap, end)
    return chunks

def extract_text_from_pdf(pdf_content):
    """Extract all text from a PDF file, ignore [REDACTED] segments."""
    try:
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
        return clean_text_ignore_redacted(text).strip()
    except Exception as e:
        print(f"[ERROR] PDF extraction failed: {e}")
        return ""

class UnslothJumpstartQAGenerator:
    def __init__(self, endpoint_name, config=None):
        self.endpoint_name = endpoint_name
        self.config = config or QA_CONFIG
        self.predictor = retrieve_default(endpoint_name)
        print(f"[INFO] QA Generator initialized with endpoint {endpoint_name}")

    def generate_for_chunk(self, text, num_pairs=5):
        """Generate QA pairs for a single text chunk using Jumpstart (ChatML format)."""
        if len(text) > self.config["max_text_length"]:
            text = text[:self.config["max_text_length"]] + "..."

        prompt = f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a dataset generator.
1) Structure the text below into a QA dataset in ChatML format for fine-tuning.
2) Each example must follow this JSON format:
{{
  "messages": [
    {{"role": "user", "content": "<question>"}},
    {{"role": "assistant", "content": "<answer>"}}
  ]
}}
3) Then, generate {num_pairs} additional synthetic QA examples on the same topic, also in this format.
4) Output ONLY a single valid JSON array. No commentary.
<|eot_id|><|start_header_id|>user<|end_header_id|>
Text:
{text}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.config["max_generation_tokens"],
                "temperature": self.config["temperature"],
                "top_p": self.config["top_p"],
                "stop": "<|eot_id|>"
            }
        }

        for attempt in range(self.config.get("retry_count", 2)):
            try:
                response = self.predictor.predict(payload)
                generated_text = ""
                if isinstance(response, dict) and "body" in response:
                    generated_text = response["body"].get("generated_text", "")
                elif isinstance(response, list) and len(response) > 0:
                    generated_text = response[0].get("generated_text", "")
                else:
                    generated_text = str(response)
                print(f"[DEBUG] Model output (first 200 chars): {generated_text[:200]}")

                # Extract JSON array
                match = re.search(r"\[.*\]", generated_text, re.S)
                if not match:
                    raise ValueError("No JSON array found in model output")
                json_str = match.group(0)
                qa_pairs = json.loads(json_str)

                # Validate and normalize structure
                valid_pairs = []
                for qa in qa_pairs:
                    if isinstance(qa, dict) and "messages" in qa:
                        valid_pairs.append(qa)
                    elif isinstance(qa, dict) and "question" in qa and "answer" in qa:
                        valid_pairs.append({
                            "messages": [
                                {"role": "user", "content": qa["question"]},
                                {"role": "assistant", "content": qa["answer"]}
                            ]
                        })
                if valid_pairs:
                    return valid_pairs
            except Exception as e:
                print(f"[WARNING] QA generation attempt {attempt+1} failed: {e}")

        print("[WARNING] Returning fallback QA due to repeated failure")
        return [{
            "messages": [
                {"role": "user", "content": "Summarize the text."},
                {"role": "assistant", "content": text[:200] + "..."}
            ]
        }]

def process_folder_from_s3(folder, generator):
    print(f"[INFO] Processing folder {folder}")
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=INPUT_BUCKET, Prefix=f"{folder}/")

    all_pairs = []
    file_count = 0

    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.lower().endswith(".pdf"):
                continue
            print(f"[INFO] Processing file {key}")
            pdf_data = s3_client.get_object(Bucket=INPUT_BUCKET, Key=key)["Body"].read()
            text = extract_text_from_pdf(pdf_data)
            if not text:
                print(f"[WARNING] No usable text (after redacted filter) in {key}")
                continue

            chunks = chunk_text(text, generator.config["chunk_size"], generator.config["chunk_overlap"])
            pairs_for_file = []

            total_questions = generator.config["num_questions_per_doc"]
            per_chunk = max(1, total_questions // len(chunks)) if chunks else 1

            for idx, chunk in enumerate(chunks):
                qa_pairs = generator.generate_for_chunk(chunk, num_pairs=per_chunk)
                # Thêm metadata cho tracking
                for qa in qa_pairs:
                    qa["source_file"] = key
                    qa["chunk_index"] = idx
                    qa["total_chunks"] = len(chunks)
                    qa["timestamp"] = datetime.utcnow().isoformat()
                pairs_for_file.extend(qa_pairs)
                print(f"[INFO] Generated {len(qa_pairs)} pairs from chunk {idx+1}/{len(chunks)}")

            all_pairs.extend(pairs_for_file)
            file_count += 1
            print(f"[SUCCESS] Generated {len(pairs_for_file)} pairs for {key}")
    return all_pairs, file_count

def save_to_s3_as_ft(qa_pairs, folder):
    if not qa_pairs:
        print("[WARNING] No QA pairs to save")
        return None
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    key = f"{folder}/qa_pairs_ft_{timestamp}.json"
    s3_client.put_object(
        Bucket=OUTPUT_BUCKET,
        Key=key,
        Body=json.dumps(qa_pairs, indent=2),
        ContentType="application/json"
    )
    print(f"[SUCCESS] Saved {len(qa_pairs)} QA conversations to s3://{OUTPUT_BUCKET}/{key}")
    return key

def lambda_handler(event, context):
    print("[START] Unsloth-Jumpstart QA Generator Lambda invoked")
    try:
        job_id = event.get("job_id")
        folder_path = event.get("folder_path")
        generator = UnslothJumpstartQAGenerator(ENDPOINT_NAME, QA_CONFIG)

        qa_pairs, file_count = process_folder_from_s3(folder_path, generator)
        output_key = save_to_s3_as_ft(qa_pairs, folder_path)

        return {
            "statusCode": 200,
            "body": {
                "status": "success",
                "job_id": job_id,
                "processed_files": file_count,
                "qa_pairs_generated": len(qa_pairs),
                "output_location": f"s3://{OUTPUT_BUCKET}/{output_key}" if output_key else "No data",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        print(f"[ERROR] Lambda failed: {e}")
        return {"statusCode": 500, "body": {"error": str(e)}}

# Local test
if __name__ == "__main__":
    test_event = {"job_id": "IFN666_QA", "folder_path": "IFN666"}
    print(json.dumps(lambda_handler(test_event, None), indent=2))