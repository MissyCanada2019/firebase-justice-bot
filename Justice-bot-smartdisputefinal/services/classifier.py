# services/classifier.py
def classify_legal_issue(text):
    text = text.lower()
    if "repairs" in text or "maintenance" in text:
        return "Tenant Rights – Maintenance"
    elif "eviction" in text or "notice" in text:
        return "Eviction"
    elif "discrimination" in text:
        return "Human Rights"
    elif "deposit" in text:
        return "Security Deposit Issue"
    else:
        return "General Housing Issue"

# services/form_suggester.py
def suggest_form(issue):
    if "Maintenance" in issue:
        return "T6"
    elif "Eviction" in issue:
        return "T2 or S2"
    elif "Human Rights" in issue:
        return "HRTO Form 1"
    elif "Security Deposit" in issue:
        return "LTB T1"
    else:
        return "LTB General Application"
