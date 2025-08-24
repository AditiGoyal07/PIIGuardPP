import json
import os
from datetime import datetime

LOG_FILE = "logs/detection_logs.jsonl"  # 1 JSON per line

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_detection(entry):
    """
    Logs redacted message and risk metadata (excluding raw sensitive data unless debugging).
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        # "original": entry.get("original"),  # include only if needed
        "redacted": entry.get("redacted"),
        "risk_score": entry.get("risk_score"),
        "flagged": entry.get("flagged"),
        "detections": entry.get("detections", []),
        "context_scores": entry.get("context_scores", {})  # NEW: log full context probs
    }

    # Write to file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
