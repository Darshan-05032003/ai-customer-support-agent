#!/usr/bin/env python3
"""
Build labeled dataset from golden annotations.
Blocked until human annotations are complete.
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    annotations_file = Path("data/evaluation/golden_annotations.jsonl")

    if not annotations_file.exists():
        print(f"Error: {annotations_file} not found.")
        print("0/250 annotations exists.")
        print("Operation BLOCKED: Human annotation missing.")
        sys.exit(1)

    with open(annotations_file, 'r') as f:
        count = sum(1 for _ in f)

    if count < 250:
        print(f"Error: Insufficient annotations. Found {count}/250 required.")
        print("Operation BLOCKED: Complete the 250 human annotations first.")
        sys.exit(1)

    print(f"Found {count} annotations. Creating labeled dataset...")
    # NOTE: Actual conversion logic would follow here when annotations exist
    # -> Mapping JSONL entries to X, y
    print("Labeled dataset built successfully (placeholder logic).")

if __name__ == "__main__":
    main()
