"""
Security Blocks for SmartDispute.ai
Blocks common vulnerability probe URLs like WordPress endpoints
"""

from flask import Blueprint, abort
import logging

security_bp = Blueprint('security', __name__)
logger = logging.getLogger(__name__)

# Block WordPress URLs
@security_bp.route('/wp-admin/', defaults={'path': ''})
@security_bp.route('/wp-admin/<path:path>')
def block_wp_admin(path):
    """Block WordPress admin URLs"""
    logger.warning(f"Blocked WordPress admin probe: /wp-admin/{path}")
    abort(404)

@security_bp.route('/wordpress/', defaults={'path': ''})
@security_bp.route('/wordpress/<path:path>')
def block_wordpress(path):
    """Block WordPress directory URLs"""
    logger.warning(f"Blocked WordPress directory probe: /wordpress/{path}")
    abort(404)

@security_bp.route('/xmlrpc.php')
def block_xmlrpc():
    """Block WordPress XML-RPC endpoint"""
    logger.warning("Blocked WordPress XML-RPC probe: /xmlrpc.php")
    abort(404)

@security_bp.route('/wp-login.php')
def block_wp_login():
    """Block WordPress login page"""
    logger.warning("Blocked WordPress login probe: /wp-login.php")
    abort(404)

# Block other common attack vectors
@security_bp.route('/wp-content/', defaults={'path': ''})
@security_bp.route('/wp-content/<path:path>')
def block_wp_content(path):
    """Block WordPress content directory"""
    logger.warning(f"Blocked WordPress content probe: /wp-content/{path}")
    abort(404)

@security_bp.route('/wp-includes/', defaults={'path': ''})
@security_bp.route('/wp-includes/<path:path>')
def block_wp_includes(path):
    """Block WordPress includes directory"""
    logger.warning(f"Blocked WordPress includes probe: /wp-includes/{path}")
    abort(404)

@security_bp.route('/.env')
def block_env():
    """Block .env file access"""
    logger.warning("Blocked .env file probe")
    abort(404)

@security_bp.route('/.git/', defaults={'path': ''})
@security_bp.route('/.git/<path:path>')
def block_git(path):
    """Block git directory access"""
    logger.warning(f"Blocked git directory probe: /.git/{path}")
    abort(404)

@security_bp.route('/phpmyadmin/', defaults={'path': ''})
@security_bp.route('/phpmyadmin/<path:path>')
def block_phpmyadmin(path):
    """Block phpMyAdmin access"""
    logger.warning(f"Blocked phpMyAdmin probe: /phpmyadmin/{path}")
    abort(404)

@security_bp.route('/admin.php')
def block_admin_php():
    """Block admin.php access"""
    logger.warning("Blocked admin.php probe")
    abort(404)

@security_bp.route('/config.php')
def block_config_php():
    """Block config.php access"""
    logger.warning("Blocked config.php probe")
    abort(404)