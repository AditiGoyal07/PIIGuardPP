# evaluate_filter.py
import json
from filter_engine import filter_input, filter_output

# Load synthetic test dataset (list of dicts with input & output)
with open("test_dataset.json", "r") as f:
    samples = json.load(f)

print("🔍 Running PIIGuard++ on synthetic dataset...\n")

for idx, sample in enumerate(samples, 1):
    user_input = sample.get("input", "")
    llm_output = sample.get("output", "")

    input_result = filter_input(user_input)
    output_result = filter_output(llm_output)

    print(f"📄 Sample #{idx}")
    print("🧾 User Input:")
    print("Original   :", input_result["original"])
    print("Redacted   :", input_result["redacted"])
    print("Risk Score :", input_result["risk_score"])
    print("Flagged    :", "⚠️ YES" if input_result["flagged"] else "✅ NO")

    print("\n🤖 LLM Output:")
    print("Original   :", output_result["original"])
    print("Redacted   :", output_result["redacted"])
    print("Risk Score :", output_result["risk_score"])
    print("Flagged    :", "⚠️ YES" if output_result["flagged"] else "✅ NO")
    print("=" * 80)
