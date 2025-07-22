from huggingface_hub import snapshot_download

# Replace this with your target model
snapshot_download(
    repo_id="unsloth/Llama-3.2-3B-Instruct-GGUF",
    local_dir="./Llama-3.2-3B-Instruct-GGUF",  # local folder to store model
    local_dir_use_symlinks=False
)
