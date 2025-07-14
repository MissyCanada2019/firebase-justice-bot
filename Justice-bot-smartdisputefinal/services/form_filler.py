# services/form_filler.py

def autofill_form_fields(form_type, profile):
    # Fake logic for now – expand per form type
    return {
        "full_name": profile.get("name", "Your Name"),
        "address": profile.get("address", "123 Main St"),
        "issue_summary": profile.get("summary", profile.get("message", "")),
        "date": profile.get("date", ""),
        "opponent": profile.get("opponent", ""),
        "requested_remedy": profile.get("remedy", "Compensation or action")
    }
