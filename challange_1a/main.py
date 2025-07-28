import os
import json
from outline_detector import extract_outline
from utils import save_json

INPUT_DIR = "input"
OUTPUT_DIR = "output"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(INPUT_DIR, filename)
            print(f"[INFO] Processing {filename}...")

            result = extract_outline(input_path)

            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            save_json(result, output_path)
            print(f"[✓] Saved output to {output_filename}\n")


if __name__ == "__main__":
    main()