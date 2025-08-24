import re
import ipaddress
from datetime import datetime

# Regex patterns with tighter specificity
PATTERNS = {
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "AADHAAR": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "PHONE": r"\b(?:\+91[-\s]?|0)?[6-9]\d{9}\b|\b0\d{2,4}[-\s]?\d{6,8}\b|\b\+?\d{2,4}[-\s]?\d{6,12}\b",
    "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    "IP_ADDRESS": r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b",
    "SALARY": r"(?:₹|rs\.?|INR|\$)\s*\d{2,7}(?:,\d{3})*(?:\.\d{1,2})?",
    "DATE": r"\b(?:\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|(?:19|20)\d{2}[-/\.](0?[1-9]|1[0-2])[-/\.](0?[1-9]|[12][0-9]|3[01]))\b"
}

INDIAN_CITIES = {
    "Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Pune",
    "Gandhinagar", "Aizawl", "Arrah", "Mangalore", "Malegaon", "Farrukhabad"
}

# Validation helpers
def is_valid_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except:
        return False

def is_valid_date(date_str):
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d"):
        try:
            datetime.strptime(date_str, fmt)
            return True
        except:
            continue
    return False

def find_regex_patterns(text):
    matches = []
    seen = set()
    matched_texts = set()  # ✅ Tracks already added match texts (for NAME/GPE)

    for label, pattern in PATTERNS.items():
        for m in re.finditer(pattern, text, re.IGNORECASE):
            span = m.span()
            if span in seen:
                continue

            matched_text = m.group().strip()

            # ✅ Specific validation rules
            if label == "DATE":
                digit_only = re.sub(r"[-/\. ]", "", matched_text)
                if digit_only.isdigit() and len(digit_only) > 8:
                    continue
                if not is_valid_date(matched_text):
                    continue

            elif label == "IP_ADDRESS":
                if not is_valid_ip(matched_text):
                    continue

            seen.add(span)
            matches.append({
                "text": matched_text,
                "type": label
            })
            matched_texts.add(matched_text)

    # Name detection from context clues
    name_matches = re.findall(
        r"(?:^|\b(?:I am|I'm|Thanks|My name's|salary of|named|name is|dear|hello)\b\s+)([A-Z][a-z]{2,}(?:\s[A-Z][a-z]{2,})?)", text)
    for name in name_matches:
        name_clean = name.strip()
        if name_clean and name_clean not in matched_texts:
            matches.append({
                "text": name_clean,
                "type": "NAME"
            })
            matched_texts.add(name_clean)

    # GPE from known cities
    for city in INDIAN_CITIES:
        if re.search(rf"\b{re.escape(city)}\b", text):
            if city not in matched_texts:
                matches.append({
                    "text": city,
                    "type": "GPE"
                })
                matched_texts.add(city)

    return matches

# Quick test
if __name__ == "__main__":
    sample = (
        "Leena's salary is ₹162609. Aadhaar is 1234-5678-9012. "
        "DOB is 01/01/2000 and 1928-05-05. IP is 192.168.1.1. "
        "Email: aditi.goyal@mail.com or phone 9876543210. "
        "Fake IP: 78.80.62 and 01119410603 and ₹120626. "
        "Thanks Ishaan from Gandhinagar."
    )
    for item in find_regex_patterns(sample):
        print(f"{item['type']:10} => {item['text']}")
