#!/usr/bin/env python3
"""
Cloud Run deployment script for SmartDispute.ai
Optimized for 8 GiB limit with environment variable configuration
"""
import os
import subprocess
import sys
import json

def run_command(cmd, description):
    """Run shell command with error handling"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_environment():
    """Check required environment variables"""
    required_vars = [
        'DATABASE_URL',
        'SESSION_SECRET',
        'GOOGLE_OAUTH_CLIENT_ID',
        'GOOGLE_OAUTH_CLIENT_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these environment variables before deployment")
        return False
    return True

def build_docker_image():
    """Build Docker image for Cloud Run"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        return False
    
    image_name = f"gcr.io/{project_id}/smartdispute-ai"
    
    # Build image
    build_cmd = f"docker build -t {image_name} ."
    if not run_command(build_cmd, "Building Docker image"):
        return False
    
    # Push to Container Registry
    push_cmd = f"docker push {image_name}"
    if not run_command(push_cmd, "Pushing image to Container Registry"):
        return False
    
    return image_name

def deploy_to_cloud_run(image_name):
    """Deploy to Cloud Run"""
    service_name = "smartdispute-ai"
    region = "us-central1"
    
    # Set environment variables for deployment
    env_vars = [
        f"DATABASE_URL={os.getenv('DATABASE_URL')}",
        f"SESSION_SECRET={os.getenv('SESSION_SECRET')}",
        f"GOOGLE_OAUTH_CLIENT_ID={os.getenv('GOOGLE_OAUTH_CLIENT_ID')}",
        f"GOOGLE_OAUTH_CLIENT_SECRET={os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')}"
    ]
    
    # Optional environment variables
    optional_vars = [
        'OPENAI_API_KEY',
        'STRIPE_SECRET_KEY',
        'SENDGRID_API_KEY',
        'SLACK_BOT_TOKEN'
    ]
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            env_vars.append(f"{var}={value}")
    
    env_string = ",".join(env_vars)
    
    deploy_cmd = f"""
    gcloud run deploy {service_name} \
        --image {image_name} \
        --platform managed \
        --region {region} \
        --port 8080 \
        --memory 1Gi \
        --cpu 1 \
        --allow-unauthenticated \
        --set-env-vars "{env_string}"
    """
    
    if run_command(deploy_cmd, "Deploying to Cloud Run"):
        print(f"🚀 Deployment successful!")
        print(f"Your app is available at: https://{service_name}-{region}-run.app")
        return True
    
    return False

def main():
    """Main deployment function"""
    print("🚀 Starting Cloud Run deployment for SmartDispute.ai")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Build and push Docker image
    image_name = build_docker_image()
    if not image_name:
        sys.exit(1)
    
    # Deploy to Cloud Run
    if not deploy_to_cloud_run(image_name):
        sys.exit(1)
    
    print("✅ Deployment completed successfully!")

if __name__ == "__main__":
    main()