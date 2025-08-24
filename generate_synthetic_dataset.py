from faker import Faker
import random
import json

fake = Faker("en_IN")

def generate_record():
    name = fake.name()
    email = fake.email()
    phone = fake.phone_number()
    aadhaar = "{}-{}-{}".format(
        random.randint(1000, 9999),
        random.randint(1000, 9999),
        random.randint(1000, 9999)
    )
    ip = fake.ipv4()
    city = fake.city()
    dob = fake.date_of_birth(minimum_age=18, maximum_age=60).strftime("%d/%m/%Y")
    salary = f"₹{random.randint(30000, 200000)}"

    # Generate a sensitive input statement
    input_options = [
        f"My name is {name} and I live in {city}.",
        f"Contact me at {phone} or email me at {email}.",
        f"My Aadhaar is {aadhaar} and DOB is {dob}.",
        f"The server IP is {ip}.",
        f"{name.split()[0]}'s salary is {salary}."
    ]
    user_input = random.choice(input_options)

    # Generate a plausible LLM response that reflects that input
    output_templates = [
        f"Thanks {name.split()[0]}, we’ve updated your address as {city}.",
        f"Okay, we will contact you at {email} or call on {phone}.",
        f"Aadhaar number {aadhaar} and DOB {dob} have been verified.",
        f"IP {ip} added to the server list.",
        f"Yes, the salary of {name.split()[0]} is noted as {salary}."
    ]
    llm_output = random.choice(output_templates)

    return {
        "input": user_input,
        "output": llm_output
    }

# Generate and save 20 synthetic examples
records = [generate_record() for _ in range(20)]

with open("test_dataset.json", "w") as f:
    json.dump(records, f, indent=2)

print("✅ Structured synthetic dataset saved to test_dataset.json")
