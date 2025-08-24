from flask import Flask, render_template, request
from faker import Faker
from regex_filter import find_regex_patterns

app = Flask(__name__)
fake = Faker('en_IN')  # Indian context

def redact_text(text, detections):
    redacted = text
    for item in detections:
        redacted = redacted.replace(item['text'], f"[REDACTED_{item['type']}]")
    return redacted

def get_risk_badge(score):
    if score >= 40:
        return "🔴 High"
    elif score >= 20:
        return "⚠️ Moderate"
    else:
        return "✅ Low"

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_text = ""
    detections = []
    redacted_text = ""
    score = 0

    if request.method == 'POST':
        if 'generate' in request.form:
            # Generate synthetic data
            generated_text = (
                f"My name is {fake.name()}, I live in {fake.city()}. "
                f"My Aadhaar is {fake.random_number(digits=12)}, and my email is {fake.email()}. "
                f"My phone is {fake.phone_number()} and my IP is {fake.ipv4()}. "
                f"My PAN is ABCDE1234F and DOB is {fake.date_of_birth()}."
                f" Salary: ₹{fake.random_int(min=30000, max=120000)}"
            )

        elif 'analyze' in request.form:
            generated_text = request.form['text']
            detections = find_regex_patterns(generated_text)
            redacted_text = redact_text(generated_text, detections)
            score = len(detections) * 10

    return render_template(
        'index.html',
        original_text=generated_text,
        redacted_text=redacted_text,
        detections=detections,
        score=score,
        risk_badge=get_risk_badge(score)  # 👈 pass badge here
    )

if __name__ == '__main__':
    app.run(debug=True)
