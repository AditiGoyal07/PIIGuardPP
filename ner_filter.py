# ner_filter.py

import spacy
import re
from nltk.corpus import names
from nameparser import HumanName

# Load spaCy's English NER model
nlp = spacy.load("en_core_web_sm")

# Load NLTK name corpus
MALE_NAMES = set(name.lower() for name in names.words('male.txt'))
FEMALE_NAMES = set(name.lower() for name in names.words('female.txt'))
ALL_FIRST_NAMES = MALE_NAMES.union(FEMALE_NAMES)

with open("indian_names.txt") as f:
    INDIAN_NAMES = set(line.strip().lower() for line in f)

ALL_FIRST_NAMES = ALL_FIRST_NAMES.union(INDIAN_NAMES)

# Define the entity labels you want to consider as sensitive
SENSITIVE_ENTITY_LABELS = {
    "PERSON",    # names
    "GPE",       # countries, cities, states
    "ORG",       # company or institution names
    "LOC",       # non-GPE locations, mountain ranges, bodies of water
    "DATE",      # full dates, months, years
    "TIME",      # times
    "MONEY",     # monetary values
    "CARDINAL",  # numerical values (e.g. number of employees)
    "QUANTITY",  # e.g. "20 liters"
    "FAC",       # facilities (airports, buildings, highways)
    "NORP"       # nationalities, religious or political groups
}

def is_probable_name(entity_text):
    entity = entity_text.strip()

    # Skip if contains digits or looks like time
    if any(char.isdigit() for char in entity):
        return False
    if re.match(r"^\d{1,2} ?[APap][Mm]$", entity):
        return False

    # Full names: check if both first and last exist
    if len(entity.split()) > 1:
        name_obj = HumanName(entity)
        return bool(name_obj.first and name_obj.last)
    else:
        return entity.lower() in ALL_FIRST_NAMES

def extract_sensitive_entities(text):
    doc = nlp(text)
    sensitive_entities = []

    for ent in doc.ents:
        entity_text = ent.text.strip()
        entity_label = ent.label_

        # First: override misclassified GPEs if they are probable names
        if is_probable_name(entity_text):
            sensitive_entities.append({
                "text": entity_text,
                "type": "Name"
            })

        # Else: keep all true sensitive entities (including GPEs that are not names)
        elif entity_label in SENSITIVE_ENTITY_LABELS:
            sensitive_entities.append({
                "text": entity_text,
                "type": entity_label
            })

    return sensitive_entities

# Test the function
if __name__ == "__main__":
    test = "My name is Aditi Goyal. I work at Thales. I live in Ghaziabad and my salary is 12 lakh rupees."
    entities = extract_sensitive_entities(test)
    for entity in entities:
        print(f"Detected: {entity['text']} ({entity['type']})")