#!/usr/bin/env python3
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Define the custom domain
CUSTOM_DOMAIN = "smartdisputeaicanada.dpdns.org"

def setup_custom_domain():
    """
    Setup custom domain configuration for SmartDispute.ai
    
    This script:
    1. Updates the application configuration to support the custom domain
    2. Provides instructions for DNS setup
    3. Tests domain accessibility
    """
    logging.info(f"Setting up custom domain: {CUSTOM_DOMAIN}")
    
    # Update app.py configuration
    update_app_configuration()
    
    # Display DNS setup instructions
    print_dns_instructions()
    
    # Add domain to .env file if it exists
    update_env_file()
    
    # Test domain accessibility
    test_domain_accessibility()
    
    logging.info("Custom domain setup complete!")
    print("\n✅ Custom domain setup is complete!")
    print("You can now access your application at:")
    print(f"https://{CUSTOM_DOMAIN}")
    print("\nRemember to complete the DNS setup with your domain provider as described above.")

def update_app_configuration():
    """Update application configuration for custom domain support"""
    logging.info("Updating application configuration")
    
    # Create backup of app.py
    try:
        subprocess.run(["cp", "app.py", "app.py.bak"], check=True)
        logging.info("Backup of app.py created as app.py.bak")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to create backup of app.py: {e}")
    
    try:
        # Read the current app.py file
        with open("app.py", "r") as f:
            content = f.read()
        
        # Check if custom domain configuration already exists
        if f"SERVER_NAME = '{CUSTOM_DOMAIN}'" in content:
            logging.info("Custom domain configuration already exists in app.py")
            return
            
        # Add custom domain configuration
        modified_content = content.replace(
            "app.config['SERVER_NAME'] = None",
            f"# Support both Replit domain and custom domain\n"
            f"CUSTOM_DOMAIN = '{CUSTOM_DOMAIN}'\n"
            f"app.config['SERVER_NAME'] = None  # Don't restrict the server name to allow both domains"
        )
        
        # Write the updated content
        with open("app.py", "w") as f:
            f.write(modified_content)
            
        logging.info("Updated app.py with custom domain configuration")
        
    except Exception as e:
        logging.error(f"Failed to update app.py: {e}")
        print(f"ERROR: Failed to update app.py: {e}")
        sys.exit(1)

def print_dns_instructions():
    """Print DNS setup instructions for the user"""
    replit_domain = os.environ.get('REPLIT_DEV_DOMAIN', None)
    if not replit_domain:
        replit_domain = os.environ.get('REPLIT_DOMAINS', 'your-replit-app.replit.app')
    
    print("\n" + "="*80)
    print("CUSTOM DOMAIN DNS SETUP INSTRUCTIONS")
    print("="*80)
    print(f"\nTo connect your domain '{CUSTOM_DOMAIN}' to this Replit app, follow these steps:")
    print("\n1. Log in to your domain registrar or DNS provider")
    print("2. Add the following DNS records:")
    print("\n   A. Add a CNAME record:")
    print("      - Type:  CNAME")
    print("      - Name:  @ or www (depending on your DNS provider)")
    print(f"      - Value: {replit_domain}")
    print("      - TTL:   3600 (or default/automatic)")
    print("\n   OR")
    print("\n   B. If your DNS provider doesn't support CNAME at root domain, use A records:")
    print("      - Type:  A")
    print("      - Name:  @")
    print("      - Value: 104.18.0.21")
    print("      - TTL:   3600 (or default/automatic)")
    print("\n      - Type:  A")
    print("      - Name:  @")
    print("      - Value: 104.18.1.21")
    print("      - TTL:   3600 (or default/automatic)")
    print("\n      - Type:  CNAME")
    print("      - Name:  www")
    print(f"      - Value: {replit_domain}")
    print("      - TTL:   3600 (or default/automatic)")
    print("\n3. Wait for DNS propagation (can take up to 24-48 hours to fully propagate)")
    print("="*80)

def update_env_file():
    """Add custom domain to .env file if it exists"""
    try:
        if os.path.exists(".env"):
            # Check if custom domain already exists in .env
            with open(".env", "r") as f:
                content = f.read()
                
            if "CUSTOM_DOMAIN" not in content:
                # Append custom domain to .env
                with open(".env", "a") as f:
                    f.write(f"\n# Custom domain configuration\nCUSTOM_DOMAIN={CUSTOM_DOMAIN}\n")
                logging.info("Added custom domain to .env file")
            else:
                logging.info("Custom domain already exists in .env file")
    except Exception as e:
        logging.warning(f"Failed to update .env file: {e}")

def test_domain_accessibility():
    """Test if the custom domain is accessible"""
    print("\nTesting domain accessibility...")
    print("Note: Your domain might not be accessible yet if DNS hasn't propagated")
    
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"https://{CUSTOM_DOMAIN}"],
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )
        status_code = result.stdout.strip()
        
        if status_code.isdigit() and int(status_code) < 400:
            print(f"✅ Domain is accessible! Status code: {status_code}")
        else:
            print(f"❓ Domain might not be accessible yet. Status code: {status_code}")
            print("   This is normal if you just set up the DNS records.")
    except subprocess.TimeoutExpired:
        print("❌ Domain check timed out. This is normal if DNS hasn't propagated yet.")
    except Exception as e:
        print(f"❌ Error checking domain: {e}")
        
    print("\nRecommendation: Use an online DNS propagation checker to monitor when")
    print("your domain becomes globally accessible.")

if __name__ == "__main__":
    try:
        setup_custom_domain()
    except Exception as e:
        logging.error(f"Custom domain setup failed: {e}")
        print(f"ERROR: Custom domain setup failed: {e}")
        sys.exit(1)