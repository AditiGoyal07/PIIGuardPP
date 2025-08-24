# context_filter.py

from transformers import pipeline

# Load zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define sensitive categories to detect
CATEGORIES = ["PII", "Sensitive data", "Confidential information", "General"]

def context_classify(text):
    result = classifier(text, CATEGORIES)
    label_scores = dict(zip(result["labels"], result["scores"]))
    top_label = result["labels"][0]
    top_score = result["scores"][0]
    
    return {
        "label": top_label,
        "score": round(top_score, 3),
        "details": label_scores
    }

# Example test
if __name__ == "__main__":
    test_input = "Can you tell me what salary the CTO is drawing this year?"
    result = context_classify(test_input)
    print(result)
