from main_filter import filter_text, CONFIG, log_detection

def filter_input(user_input):
    result = filter_text(user_input)
    result["stage"] = "input"
    result["flagged"] = result["risk_score"] >= CONFIG["risk_threshold"]
    log_detection(result)
    return result

def filter_output(llm_response):
    result = filter_text(llm_response)
    result["stage"] = "output"
    result["flagged"] = result["risk_score"] >= CONFIG["risk_threshold"]
    log_detection(result)
    return result

# Example Demo
if __name__ == "__main__":
    prompt = "My name is Aditi Goyal and my email is aditi.goyal@company.com"
    output = "Sure, Aditi. I’ll email you at aditi.goyal@company.com."

    input_result = filter_input(prompt)
    output_result = filter_output(output)

    print("\n🟢 Input Filter:")
    print("Redacted:", input_result["redacted"])
    print("Risk Score:", input_result["risk_score"])
    print("Flagged:", input_result["flagged"])

    print("\n🔵 Output Filter:")
    print("Redacted:", output_result["redacted"])
    print("Risk Score:", output_result["risk_score"])
    print("Flagged:", output_result["flagged"])
