import json
import os

def save_transcript(messages, path="outputs/transcript.json"):
    os.makedirs("outputs", exist_ok=True)
    with open(path, "w") as f:
        json.dump(messages, f, indent=2)


def save_text_transcript(messages, path="outputs/transcript.txt"):
    with open(path, "w") as f:
        for msg in messages:
            f.write(f"{msg}\n")