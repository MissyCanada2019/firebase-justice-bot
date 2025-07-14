"""
Pricing routes for SmartDispute.ai
"""

from flask import Blueprint, render_template

pricing_bp = Blueprint('pricing', __name__)

@pricing_bp.route('/pricing')
def pricing():
    """Pricing page for SmartDispute.ai services"""
    return render_template('pricing.html')

def init_pricing_routes(app):
    """Initialize pricing routes with the Flask app"""
    app.register_blueprint(pricing_bp)
    app.logger.info("Pricing routes registered successfully")