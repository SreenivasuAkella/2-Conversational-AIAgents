import json
import os

def save_transcript(messages, path="outputs/transcript.json"):
    # Create the directory structure
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(messages, f, indent=2)


def save_text_transcript(messages, path="outputs/transcript.txt"):
    # Create the directory structure
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for msg in messages:
            f.write(f"{msg}\n")