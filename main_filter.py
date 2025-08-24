import json
import unicodedata
import re
from ner_filter import extract_sensitive_entities
from context_filter import context_classify
from regex_filter import find_regex_patterns
from logger import log_detection

# Load configuration
with open("config.json") as f:
    CONFIG = json.load(f)

# Compile ORG ignore regex patterns
ORG_IGNORE_PATTERNS = [re.compile(p, flags=re.IGNORECASE) for p in CONFIG.get("org_ignore_patterns", [])]

# --- Normalize Text ---
def normalize_text(text):
    return unicodedata.normalize("NFKC", text)

# --- Check if text matches any ignore pattern ---
def is_ignored(text, patterns):
    return any(p.search(text) for p in patterns)

# --- Merge NER and Regex detections with conflict resolution ---
def merge_detections(ner_list, regex_list):
    """
    Merge NER and Regex detections:
    - If regex finds same text, its type overrides NER's
    - Remove NER items like ORG: DOB using ignore patterns
    """
    final = []

    for ner in ner_list:
        text = ner.get("text", "")
        type_ = ner.get("type", ner.get("label", "NER"))

        if type_ == "ORG" and is_ignored(text, ORG_IGNORE_PATTERNS):
            continue

        final.append({
            "text": text,
            "type": type_
        })

    for regex in regex_list:
        text = regex.get("text", "")
        r_type = regex.get("type", regex.get("label", "REGEX"))

        if not text:
            continue

        found = False
        for i, item in enumerate(final):
            if item["text"] == text:
                final[i]["type"] = r_type
                found = True
                break
        if not found:
            final.append({"text": text, "type": r_type})

    seen = set()
    deduped = []
    for d in final:
        key = (d["text"].lower(), d["type"].lower())
        if key not in seen:
            deduped.append(d)
            seen.add(key)

    return deduped

# --- Redaction ---
def redact(text, detections):
    for item in detections:
        if "text" in item and "type" in item:
            tag = item["type"].upper().replace(" ", "_")
            redaction = f"[REDACTED_{tag}]"
            text = text.replace(item["text"], redaction)
    return text

# --- Risk Scoring ---
def compute_risk_score(detections):
    weights = CONFIG.get("weights", {})
    score = 0
    print("\n🧮 Scoring breakdown:")
    for item in detections:
        t = item.get("type")
        if t:
            w = weights.get(t, 10)
            print(f"  - {t}: +{w}")
            score += w
    return min(score, 100)

# --- Main Filter Engine ---
def filter_text(text):
    text = normalize_text(text)
    ner_detections = extract_sensitive_entities(text)
    regex_detections = find_regex_patterns(text)
    all_detections = merge_detections(ner_detections, regex_detections)
    context = context_classify(text)

    if context["label"] != "General" and context["score"] > 0.6:
        all_detections.append({"type": context["label"], "text": "[Context]"})

    risk_score = compute_risk_score(all_detections)
    redacted_text = redact(text, all_detections)
    is_flagged = risk_score >= CONFIG.get("risk_threshold", 30)

    log_detection({
        "original": text,
        "redacted": redacted_text,
        "risk_score": risk_score,
        "flagged": is_flagged,
        "detections": all_detections,
        "context_scores": context["details"]  # <-- pass full label scores
    })

    return {
        "original": text,
        "redacted": redacted_text,
        "risk_score": risk_score,
        "detections": all_detections,
        "explanation": context["details"],
        "flagged": is_flagged
    }

# --- Standalone Test Run ---
if __name__ == "__main__":
    sample = "My Aadhaar is 1234-5678-9012 and DOB is 01/01/2000."
    result = filter_text(sample)

    print("\n🔍 Filtered Output:")
    print("Original Text:", result["original"])
    print("Redacted Text:", result["redacted"])
    print("Risk Score:", result["risk_score"])
    print("Detections:", result["detections"])
    print("Classification Explanation:", result["explanation"])
