import boto3
import zipfile
import os
import tempfile
from fpdf import FPDF
from pypdf import PdfReader
import spacy
import re
import unicodedata

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Initialize S3 client
s3_client = boto3.client('s3', region_name='us-east-1')

def redact_entities(text, doc):
    redacted = text
    offset = 0
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG']:
            start = ent.start_char + offset
            end = ent.end_char + offset
            length = end - start
            redacted = redacted[:start] + '[REDACTED]' + redacted[end:]
            offset += len('[REDACTED]') - length
    return redacted

def redact_emails_and_phones(text):
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[REDACTED]', text)
    phone_patterns = [
        r'\b\d{10,15}\b',
        r'\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b'
    ]
    for pattern in phone_patterns:
        text = re.sub(pattern, '[REDACTED]', text)
    return text

def sanitize_text(text):
    doc = nlp(text)
    redacted_text = redact_entities(text, doc)
    redacted_text = redact_emails_and_phones(redacted_text)
    return redacted_text

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
    text = strip_non_latin1(text)
    pdf.multi_cell(0, 10, text)
    pdf_output = tempfile.NamedTemporaryFile(delete=False)
    pdf.output(pdf_output.name)
    with open(pdf_output.name, 'rb') as f:
        pdf_content = f.read()
    os.remove(pdf_output.name)
    return pdf_content

def process_zip_file_from_s3(bucket_name, zip_key, destination_bucket):
    temp_dir = tempfile.mkdtemp()
    zip_file_path = os.path.join(temp_dir, zip_key)
    s3_client.download_file(bucket_name, zip_key, zip_file_path)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('.pdf'):
            print(f"[INFO] Processing: {filename}")
            extracted_text = extract_text_from_pdf_local(file_path)
            if extracted_text.strip():
                sanitized_text = sanitize_text(extracted_text)
                cleaned_text = normalize_text_formatting(sanitized_text)
                sanitized_pdf = create_pdf_from_text(cleaned_text)
                sanitized_key = f"chunkdata/{filename}"
                s3_client.put_object(Body=sanitized_pdf, Bucket=destination_bucket, Key=sanitized_key)
                print(f"[SUCCESS] Uploaded: {sanitized_key}")
            else:
                print(f"[WARNING] Skipping {filename}: No text extracted")

    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    if not os.listdir(temp_dir):
        os.rmdir(temp_dir)

# Example usage
if __name__ == "__main__":
    bucket_name = 'lazyai-input'
    zip_key = 'lecture.zip'
    destination_bucket = 'lazyai-output-chunkdata'
    process_zip_file_from_s3(bucket_name, zip_key, destination_bucket)
