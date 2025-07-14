# services/timeline_builder.py

def generate_timeline(case_profile):
    issue = (case_profile.get("issue") or "general").strip().lower()

    if issue == "tenant rights":
        return [
            {
                "step": 1, "title": "Prepare Form T6", 
                "description": "We've pre-filled Form T6 based on your complaint.",
                "form_action": { "form_code": "T6", "autofill_url": "/generate?form=T6&autofill=true" }
            },
            {"step": 2, "title": "Serve the Landlord", "description": "Deliver a copy to your landlord. Save proof."},
            {"step": 3, "title": "File with LTB", "description": "Submit online or in person. Filing fee applies."},
            {"step": 4, "title": "Prepare for Hearing", "description": "Organize documents and witnesses."}
        ]

    elif issue == "custody":
        return [
            {
                "step": 1, "title": "Fill Form 35.1", 
                "description": "We started your parenting affidavit.",
                "form_action": { "form_code": "35.1", "autofill_url": "/generate?form=35.1&autofill=true" }
            },
            {"step": 2, "title": "File in Family Court", "description": "Online or in person."},
            {"step": 3, "title": "Serve the Other Parent", "description": "Serve with proof."},
            {"step": 4, "title": "Attend Conference", "description": "Prepare a parenting plan."}
        ]

    elif issue == "cas" or issue == "child protection":
        return [
            {
                "step": 1, "title": "Complete Form 33B", 
                "description": "We've started your response to CAS.",
                "form_action": { "form_code": "33B", "autofill_url": "/generate?form=33B&autofill=true" }
            },
            {"step": 2, "title": "Request Disclosure", "description": "Ask CAS for their file on you."},
            {"step": 3, "title": "Prepare for Case Conference", "description": "Submit affidavits and evidence."}
        ]

    elif issue == "divorce":
        return [
            {
                "step": 1, "title": "Start Divorce Form 8", 
                "description": "We've started Form 8 for you.",
                "form_action": { "form_code": "8", "autofill_url": "/generate?form=8&autofill=true" }
            },
            {"step": 2, "title": "Serve Spouse", "description": "Deliver court-stamped forms."},
            {"step": 3, "title": "Wait or Respond", "description": "Next steps depend on their reply."}
        ]

    elif issue == "human rights":
        return [
            {
                "step": 1, "title": "Submit Form 1", 
                "description": "This form starts your HRTO application.",
                "form_action": { "form_code": "HRTO-Form-1", "autofill_url": "/generate?form=HRTO-Form-1&autofill=true" }
            },
            {"step": 2, "title": "Gather Evidence", "description": "Upload communications, photos, documents."}
        ]

    return [
        {"step": 1, "title": "Determine your issue", "description": "Tell us more to recommend a form."},
        {"step": 2, "title": "Find correct court", "description": "We'll show you where to file."}
    ]
