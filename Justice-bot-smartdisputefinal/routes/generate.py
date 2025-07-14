# routes/generate.py

from flask import Blueprint, render_template, request, session
from services.form_filler import autofill_form_fields

generate_bp = Blueprint('generate', __name__)

@generate_bp.route('/generate')
def generate():
    form_type = request.args.get('form')
    autofill = request.args.get('autofill') == 'true'

    form_data = {}
    if autofill and "case_profile" in session:
        form_data = autofill_form_fields(form_type, session["case_profile"])

    return render_template(f'forms/{form_type}.html', form_data=form_data)
