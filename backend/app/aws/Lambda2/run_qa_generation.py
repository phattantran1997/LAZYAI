import os
import glob
import boto3
from unsloth.dataprep import SyntheticDataKit

# Paths from SageMaker Processing container
INPUT_DIR = "/opt/ml/processing/input/redacted"
OUTPUT_DIR = "/opt/ml/processing/output"

MODEL_PATH = "/opt/ml/model/llama3-3b-instruct"  # Or mount from S3

def load_model():
    print("[INFO] Loading SyntheticDataKit model...")
    generator = SyntheticDataKit.from_pretrained(
        model_name=MODEL_PATH,
        max_seq_length=2048,
    )
    return generator

def process_documents(generator):
    files = glob.glob(os.path.join(INPUT_DIR, "*.pdf"))
    if not files:
        print("[WARN] No redacted PDFs found.")
        return

    qa_pairs = []
    for file in files:
        print(f"[PROCESS] Generating QA for {file}")
        # Simple placeholder text (you’ll extract text from PDF if needed)
        text = f"Document from {file}"
        results = generator.generate(texts=[text], num_questions=5)
        qa_pairs.extend(results)

    # Save output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "qa_pairs.jsonl")
    with open(output_file, "w", encoding="utf-8") as f:
        for qa in qa_pairs:
            f.write(f"{qa}\n")
    print(f"[DONE] Saved QA pairs: {output_file}")

if __name__ == "__main__":
    generator = load_model()
    process_documents(generator)
