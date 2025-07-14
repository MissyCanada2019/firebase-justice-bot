# services/case_builder.py

def update_case_profile(profile, user_input):
    user_input = user_input.lower()

    if "ontario" in user_input or "toronto" in user_input:
        profile["province"] = "ON"
    elif "bc" in user_input or "vancouver" in user_input:
        profile["province"] = "BC"

    if "child" in user_input or "custody" in user_input:
        profile["issue"] = "custody"
    elif "eviction" in user_input or "landlord" in user_input:
        profile["issue"] = "tenant rights"

    if "father" in user_input or "dad" in user_input:
        profile["user_role"] = "father"
    elif "mother" in user_input or "mom" in user_input:
        profile["user_role"] = "mother"

    if "urgent" in user_input or "won’t return" in user_input or "danger":
        profile["urgency"] = True

    profile["facts"] = profile.get("facts", "") + " " + user_input
    return profile

def generate_reply(profile):
    missing = []
    if "province" not in profile:
        missing.append("What province are you in?")
    if "issue" not in profile:
        missing.append("What legal issue are you facing?")
    if "user_role" not in profile:
        missing.append("Are you the tenant, parent, or other?")
    
    if missing:
        return " ".join(missing)
    
    return f"Thanks! You're dealing with a {profile['issue']} issue in {profile['province']}. Let me find relevant forms and legal steps..."

def recommend_form(profile):
    if all(k in profile for k in ("issue", "province", "user_role")):
        issue = profile["issue"]
        if issue == "custody":
            return {
                "form": "Form 35.1",
                "url": "/generate?form=35.1&province=" + profile["province"]
            }
        elif issue == "tenant rights":
            return {
                "form": "T6",
                "url": "/generate?form=T6&province=" + profile["province"]
            }
    return None
