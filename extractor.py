import re

# Function to extract parameters
def extract_parameters(text):
    results = {}

    # Patterns to look for
    patterns = {
        "Hemoglobin": r"(Hemoglobin|Hb).*?(\d+\.?\d*)",
        "Blood Sugar": r"(Blood Sugar|FBS|Glucose).*?(\d+\.?\d*)",
        "Cholesterol": r"(Cholesterol).*?(\d+\.?\d*)"
    }

    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results[param] = float(match.group(2))  # convert to number

    return results

# Function to classify values
def classify(parameter, value):
    if parameter == "Hemoglobin":
        if value < 12:
            return "Low"
        elif value > 17:
            return "High"
        else:
            return "Normal"

    if parameter == "Blood Sugar":
        if value < 70:
            return "Low"
        elif value > 140:
            return "High"
        else:
            return "Normal"

    if parameter == "Cholesterol":
        if value > 200:
            return "High"
        else:
            return "Normal"

    return "Normal"
