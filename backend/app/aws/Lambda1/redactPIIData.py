import boto3
import zipfile
import os
import shutil
import tempfile
from fpdf import FPDF
from pypdf import PdfReader
import spacy
import re
import unicodedata
import uuid
import json
from datetime import datetime

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Initialize AWS clients
s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
lambda_client = boto3.client("lambda")
track_table = dynamodb.Table("lazyai-track-user-input")

DESTINATION_BUCKET = "lazyai-output-chunkdata"
NEXT_LAMBDA = "LazyAI-QA-Generation"  # Replace with your QA & Fine-tune Lambda name

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

def sanitize_text(text):
    doc = nlp(text)
    redacted_text = redact_entities(text, doc)
    return redact_emails_and_phones(redacted_text)

def normalize_text_formatting(text):
    text = unicodedata.normalize("NFKD", text)
    replacements = {
        "•": "-", "–": "-", "—": "-", "“": '"', "”": '"',
        "‘": "'", "’": "'", "…": "...", "‐": "-", "\u00a0": " ",
        "‒": "-", "\u2028": "\n", "\u2029": "\n"
    }
    for key, val in replacements.items():
        text = text.replace(key, val)
    text = re.sub(r"\.{3,}", "...", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

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

def strip_non_latin1(text):
    return text.encode("latin-1", errors="replace").decode("latin-1")

def create_pdf_from_text(text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, strip_non_latin1(text))
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    pdf.output(temp_file.name)
    with open(temp_file.name, "rb") as f:
        content = f.read()
    os.remove(temp_file.name)
    return content

def log_to_dynamodb(original_name, s3_key_output):
    item = {
        "id": str(uuid.uuid4()),
        "filename": original_name,
        "s3_output_key": s3_key_output,
        "timestamp": datetime.utcnow().isoformat()
    }
    track_table.put_item(Item=item)
    print(f"[LOGGED] DynamoDB record created: {item['id']}")

def process_zip_file_from_s3(bucket_name, zip_key):
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "input.zip")

    folder_name = os.path.splitext(os.path.basename(zip_key))[0]
    print(f"[INFO] Processing ZIP: {zip_key} -> Output folder: {folder_name}")

    s3_client.download_file(bucket_name, zip_key, zip_path)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    processed_files = []
    for root, dirs, files in os.walk(temp_dir):
        for filename in files:
            if filename.lower().endswith(".pdf") and not filename.startswith("._"):
                file_path = os.path.join(root, filename)
                print(f"[INFO] Processing PDF: {filename}")
                extracted = extract_text_from_pdf_local(file_path)
                if extracted.strip():
                    sanitized = sanitize_text(extracted)
                    cleaned = normalize_text_formatting(sanitized)
                    output_pdf = create_pdf_from_text(cleaned)

                    output_name = f"{os.path.splitext(filename)[0]}.pdf"
                    s3_key_out = f"{folder_name}/{output_name}"

                    s3_client.put_object(
                        Body=output_pdf,
                        Bucket=DESTINATION_BUCKET,
                        Key=s3_key_out
                    )
                    print(f"[SUCCESS] Uploaded sanitized PDF to: {s3_key_out}")

                    log_to_dynamodb(filename, s3_key_out)
                    processed_files.append(output_name)
                else:
                    print(f"[WARNING] Skipping unreadable file: {filename}")

    print(f"[SUMMARY] Processed {len(processed_files)} files in folder: {folder_name}")
    shutil.rmtree(temp_dir)
    print("[CLEANUP] Temp directory removed")

    # Trigger next Lambda after all files processed
    if processed_files:
        print(f"[TRIGGER] Invoking next Lambda: {NEXT_LAMBDA}")
        payload = {
            "job_id": folder_name,
            "processed_files": processed_files,
            "output_bucket": DESTINATION_BUCKET,
            "output_prefix": folder_name
        }
        try:
            response = lambda_client.invoke(
                FunctionName=NEXT_LAMBDA,
                InvocationType="Event",  # Asynchronous
                Payload=json.dumps(payload)
            )
            print(f"[TRIGGER] Lambda invoke response: {response}")
            print(f"[TRIGGER] Successfully invoked {NEXT_LAMBDA} with payload: {json.dumps(payload)}")
        except Exception as e:
            print(f"[ERROR] Failed to invoke {NEXT_LAMBDA}: {str(e)}")
            print(f"[ERROR] Payload was: {json.dumps(payload)}")

def lambda_handler(event, context):
    print("[START] Lambda handler invoked")
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        if key.lower().endswith(".zip"):
            print(f"[EVENT] Triggered by file: {bucket}/{key}")
            process_zip_file_from_s3(bucket, key)
        else:
            print(f"[SKIPPED] Not a .zip file: {key}")
    return {"statusCode": 200, "body": "Processing complete."}
