from transformers import AutoTokenizer
import numpy as np
import os

class SyntheticDataChunker:
    def __init__(self, model_name="llama3-3b-instruct", 
                 max_seq_length=2048, max_generation_tokens=512, overlap=64):
        """
        A CPU-only alternative to Unsloth's SyntheticDataKit for token-based chunking.
        Uses local Llama 3 model for tokenization.
        """
        # Use local model path - point to the backend/llama3-3b-instruct directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "..", "..", "..", model_name)
        model_path = os.path.abspath(model_path)
        
        print(f"[INFO] Loading tokenizer from: {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.max_seq_length = max_seq_length
        self.max_generation_tokens = max_generation_tokens
        self.overlap = overlap

    def chunk_data(self, filename):
        """
        Token-based chunking (same as Unsloth) — splits by token length, 
        with overlap for context, and saves chunks as files.
        """
        assert os.path.exists(filename), f"File not found: {filename}"
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()

        # Max tokens for each chunk (reserve space for generation + safety margin)
        max_tokens = self.max_seq_length - self.max_generation_tokens * 2 - 128
        if max_tokens <= 5:
            raise RuntimeError("Generation length is too long compared to sequence length!")

        # Tokenize entire text
        input_ids = self.tokenizer(text, add_special_tokens=False).input_ids
        length = len(input_ids)

        # Compute chunk boundaries
        n_chunks = int(np.ceil(length / (max_tokens - self.overlap)))
        boundaries = np.ceil(np.linspace(0, length - self.overlap, n_chunks)).astype(int)
        boundaries = np.stack((boundaries[:-1], (boundaries + self.overlap)[1:])).T
        boundaries = np.minimum(boundaries, length).tolist()

        # Save chunked text files
        base, ext = os.path.splitext(filename)
        chunk_files = []
        for i, (left, right) in enumerate(boundaries):
            chunk_text = self.tokenizer.decode(input_ids[left:right])
            out_file = f"{base}_chunk{i}{ext}"
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(chunk_text)
            chunk_files.append(out_file)

        print(f"[INFO] Chunked {filename} into {len(chunk_files)} parts")
        return chunk_files


# Usage Example:
if __name__ == "__main__":
    # Load CPU-safe chunker with local Llama 3 model
    chunker = SyntheticDataChunker(
        model_name="llama3-3b-instruct", 
        max_seq_length=2048,
        max_generation_tokens=512,
        overlap=64
    )
    
    # Chunk the extracted text file
    chunks = chunker.chunk_data("data/output/week3.txt")
    print("Generated chunks:", chunks)
