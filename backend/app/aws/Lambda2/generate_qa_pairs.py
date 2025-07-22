#!/usr/bin/env python3
"""
Generate QA pairs from chunked data using Ollama API (no synthetic-data-kit CLI).
"""

import requests
import json
import os
import glob
from pathlib import Path
import time
from groq import Groq
import re
import ast

def fix_unescaped_quotes(json_str):
    # Replace unescaped double quotes inside values with single quotes
    # This is a simple heuristic: replace any double quote that is not part of a key or JSON structure
    # It will not affect the JSON keys or structure
    def replacer(match):
        inner = match.group(1)
        # Replace any double quote inside the value with single quote
        return '"' + inner.replace('"', "'") + '"'
    # Only match values inside quotes
    return re.sub(r'"([^"\n]*?)"(?=,|\})', replacer, json_str)

def extract_json_array(response_text):
    # Find the first [ and last ] to get the array
    start_idx = response_text.find('[')
    end_idx = response_text.rfind(']') + 1
    if start_idx == -1 or end_idx == -1:
        print("[WARN] Could not find JSON array in response. Attempting regex fallback.")
        return extract_qa_pairs_regex(response_text)
    json_str = response_text[start_idx:end_idx]
    # Remove trailing commas before closing ]
    json_str = re.sub(r',\s*\]', ']', json_str)
    # Replace single quotes with double quotes
    json_str = json_str.replace("'", '"')
    # Remove newlines inside JSON for safety
    json_str = re.sub(r'\n', ' ', json_str)
    # Fix unescaped quotes inside values
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

def extract_qa_pairs_regex(text):
    # Try to extract QA pairs from text using regex
    qa_pairs = []
    # This regex matches {"question": "...", "answer": "..."}
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

def generate_qa_pairs_from_text_groq(
    text,
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    num_pairs=25,
    api_key="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"
):
    # Truncate text if too long
    max_chars = 2000
    if len(text) > max_chars:
        text = text[:max_chars] + "..."

    prompt = f"""Create {num_pairs} question-answer pairs from this text. Return only a JSON array like this:
[
  {{"question": "What is the main topic?", "answer": "The main topic is..."}},
  {{"question": "What are the key points?", "answer": "The key points are..."}}
]

Text: {text}"""

    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    # Get the response text
    response_text = completion.choices[0].message.content

    qa_pairs = extract_json_array(response_text)
    if qa_pairs:
        return qa_pairs
    else:
        print(f"[ERROR] Could not parse QA pairs from model output.")
        print(f"[ERROR] Response preview: {response_text[:200]}...")
        return []

def process_chunk_file(file_path, output_dir="data/generated", model="llama2:latest", num_pairs=25):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f"[INFO] Processing {file_path} (length: {len(text)} chars)")
    cleaned_text = clean_text_ignore_redacted(text)
    qa_pairs = generate_qa_pairs_from_text_groq(
        cleaned_text,
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        num_pairs=25,
        api_key="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"
    )
    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(file_path).stem
    output_file = Path(output_dir) / f"{base_name}_qa.json"
    # Always write a JSON array to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        if isinstance(qa_pairs, list):
            json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
        else:
            # If it's a string (raw or cleaned), wrap in a list for valid JSON
            json.dump([qa_pairs], f, indent=2, ensure_ascii=False)
    if isinstance(qa_pairs, list) and qa_pairs:
        print(f"✅ Saved {len(qa_pairs)} QA pairs to {output_file}")
        return output_file
    else:
        print(f"❌ Failed to generate valid QA pairs for {file_path}, but output was saved as a JSON array.")
        return None

def main():
    output_dir = "data/output"
    save_dir = "data/generated"
    num_pairs = 25
    model = "llama2:latest"
    chunk_pattern = os.path.join(output_dir, "*_chunk*.txt")
    filenames = sorted(glob.glob(chunk_pattern))
    if not filenames:
        print(f"[ERROR] No chunked files found at: {chunk_pattern}")
        return False
    print(f"[INFO] Found {len(filenames)} chunk files:")
    for f in filenames:
        print(f"  - {f}")
    files_to_process = filenames[:3]
    print(f"[INFO] Processing {len(files_to_process)} files (out of {len(filenames)})")
    results = []
    for idx, filename in enumerate(files_to_process):
        print(f"\n[PROCESSING] ({idx+1}/{len(files_to_process)}) {os.path.basename(filename)}")
        result = process_chunk_file(filename, output_dir=save_dir, model=model, num_pairs=num_pairs)
        if result:
            results.append(result)
            print(f"✅ Done: {filename}")
        else:
            print(f"❌ Failed: {filename}")
        if idx < len(files_to_process) - 1:
            print("[INFO] Sleeping 2 seconds before next chunk...")
            time.sleep(2)
    print("\n[SUMMARY]")
    print(f"Processed files: {len(results)}/{len(files_to_process)}")
    print(f"QA pairs per file: {num_pairs}")
    print(f"Total QA pairs: {len(results) * num_pairs}")
    return True if results else False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
