#!/usr/bin/env python3
"""
Convert synthetic-data-kit command to Python script
Uses synthetic-data-kit as a CLI tool via subprocess
"""

import subprocess
import sys
import os

def run_synthetic_data_kit_ingest(input_file, config_file="synthetic_data_kit_config.yaml"):
    """
    Run synthetic-data-kit ingest command via subprocess.
    
    Args:
        input_file: Path to input file (PDF, URL, etc.)
        config_file: Path to config file
    """
    
    print(f"[INFO] Running synthetic-data-kit ingest")
    print(f"[INFO] Input: {input_file}")
    print(f"[INFO] Config: {config_file}")
    
    try:
        # Build the command
        cmd = [
            "synthetic-data-kit",
            "-c", config_file,
            "ingest",
            input_file
        ]
        
        print(f"[INFO] Command: {' '.join(cmd)}")
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"[SUCCESS] Command executed successfully!")
        print(f"[OUTPUT] {result.stdout}")
        
        return result.stdout.strip()
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed with exit code {e.returncode}")
        print(f"[STDOUT] {e.stdout}")
        print(f"[STDERR] {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"[ERROR] synthetic-data-kit command not found. Make sure it's installed.")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return None

def main():
    """Main function to run the ingest process."""
    
    # Configuration
    config_file = "synthetic_data_kit_config.yaml"
    input_file = "week3.pdf"
    
    print(f"[START] Synthetic Data Kit Ingest Process")
    
    # Run the ingest command
    result = run_synthetic_data_kit_ingest(input_file, config_file)
    
    if result:
        print(f"✅ Process completed successfully!")
        print(f"📄 Output: {result}")
    else:
        print(f"❌ Process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()