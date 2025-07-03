import boto3
import zipfile
import os
import tempfile
from fpdf import FPDF
import time

# Initialize AWS clients with a specific region
s3_client = boto3.client('s3', region_name='us-east-1')  # Make sure it's the same region as your S3 bucket
textract_client = boto3.client('textract', region_name='us-east-1')
comprehend_client = boto3.client('comprehend', region_name='us-east-1')

def wait_for_job(job_id):
    """Poll Textract for job completion."""
    while True:
        response = textract_client.get_document_text_detection(JobId=job_id)
        status = response['JobStatus']
        if status in ['SUCCEEDED', 'FAILED']:
            return response
        time.sleep(5)  # Wait for 5 seconds before retrying

def extract_text_from_pdf(s3_bucket, s3_key):
    # Use Textract to extract text from a PDF file
    response = textract_client.start_document_text_detection(
        DocumentLocation={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}}
    )
    
    job_id = response['JobId']
    
    # Wait for Textract job to finish
    result = wait_for_job(job_id)
    
    if result['JobStatus'] != 'SUCCEEDED':
        print(f"Textract job failed for {s3_key}")
        return ""
    
    # If job succeeded, process the blocks
    extracted_text = ""
    if 'Blocks' in result:
        for item in result['Blocks']:
            if item['BlockType'] == 'LINE':
                extracted_text += item['Text'] + "\n"
    
    return extracted_text

def detect_pii(text):
    # Use Comprehend to detect PII entities in the extracted text
    response = comprehend_client.batch_detect_entities(
        TextList=[text],
        LanguageCode='en'
    )

    pii_entities = response['ResultList'][0]['Entities']
    sanitized_text = text
    
    # Redact PII by replacing detected PII with '[REDACTED]'
    for entity in pii_entities:
        entity_text = entity['Text']
        sanitized_text = sanitized_text.replace(entity_text, '[REDACTED]')
    
    return sanitized_text

def create_pdf_from_text(text):
    # Create a new PDF with the sanitized text
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    
    # Save the PDF to a temporary file
    pdf_output = tempfile.NamedTemporaryFile(delete=False)
    pdf.output(pdf_output.name)
    
    with open(pdf_output.name, 'rb') as f:
        pdf_content = f.read()
    
    os.remove(pdf_output.name)  # Remove the temporary file
    
    return pdf_content

def process_zip_file_from_s3(bucket_name, zip_key, destination_bucket):
    # Download ZIP file from S3
    temp_dir = tempfile.mkdtemp()
    zip_file_path = os.path.join(temp_dir, zip_key)
    
    s3_client.download_file(bucket_name, zip_key, zip_file_path)
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Process each PDF in the ZIP file
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('.pdf'):
            # Upload the PDF to S3 before passing it to Textract
            s3_key_pdf = f"unzipped/{filename}"
            s3_client.upload_file(file_path, bucket_name, s3_key_pdf)
            
            # Extract text from the PDF using Textract
            extracted_text = extract_text_from_pdf(bucket_name, s3_key_pdf)
            
            if extracted_text:
                # Detect PII and redact it
                sanitized_text = detect_pii(extracted_text)
                
                # Create a sanitized PDF
                sanitized_pdf = create_pdf_from_text(sanitized_text)
                
                # Upload the sanitized PDF back to S3
                sanitized_key = f"chunkdata/{filename}"
                s3_client.put_object(Body=sanitized_pdf, Bucket=destination_bucket, Key=sanitized_key)
            else:
                print(f"Skipping {filename} due to Textract extraction failure")
    
    # Clean up temporary files
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Ensure the directory is empty before attempting to remove it
    if not os.listdir(temp_dir):
        os.rmdir(temp_dir)  # Remove the empty directory
    else:
        print(f"Warning: Temporary directory {temp_dir} not empty!")

# Example usage: process the ZIP file from S3 and store sanitized PDFs back to S3
bucket_name = 'lazyai-input'  # S3 bucket containing the ZIP file
zip_key = 'CV.zip'   # S3 key for the uploaded ZIP file
destination_bucket = 'lazyai-output-chunkdata'  # S3 bucket to store sanitized PDFs

process_zip_file_from_s3(bucket_name, zip_key, destination_bucket)
