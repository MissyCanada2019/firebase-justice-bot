#!/usr/bin/env python3
"""
Content Management Workflow for SmartDispute.ai
Automates Charter quote updates, legal content management, and theme consistency
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Case, Document
import logging
from datetime import datetime
import json
import re

class ContentManagementWorkflow:
    def __init__(self):
        self.app = app
        self.charter_quotes = {
            'section_2': "Everyone has the following fundamental freedoms: (a) freedom of conscience and religion; (b) freedom of thought, belief, opinion and expression, including freedom of the press and other media of communication; (c) freedom of peaceful assembly; and (d) freedom of association.",
            'section_7': "Everyone has the right to life, liberty and security of the person and the right not to be deprived thereof except in accordance with the principles of fundamental justice.",
            'section_8': "Everyone has the right to be secure against unreasonable search or seizure.",
            'section_15': "Every individual is equal before and under the law and has the right to the equal protection and equal benefit of the law without discrimination.",
            'section_24': "Anyone whose rights or freedoms, as guaranteed by this Charter, have been infringed or denied may apply to a court of competent jurisdiction to obtain such remedy as the court considers appropriate and just in the circumstances.",
            'section_32': "This Charter applies (a) to the Parliament and government of Canada in respect of all matters within the authority of Parliament; and (b) to the legislature and government of each province in respect of all matters within the authority of the legislature of each province."
        }
        
    def update_charter_content(self):
        """Update all templates with fresh Charter quotes and Canadian themes"""
        templates_to_update = [
            'templates/index.html',
            'templates/dashboard.html',
            'templates/register.html',
            'templates/login.html',
            'templates/upload.html',
            'templates/payment/options.html'
        ]
        
        for template_path in templates_to_update:
            if os.path.exists(template_path):
                self._update_template_charter_content(template_path)
        
        print("Charter content updated across all templates")
    
    def _update_template_charter_content(self, template_path):
        """Update a specific template with Charter content"""
        try:
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Ensure Canadian color scheme is present
            if '--canadian-red: #FF0000' not in content:
                css_vars = """
        :root {
            --canadian-red: #FF0000;
            --canadian-white: #FFFFFF;
            --charter-blue: #003366;
            --justice-gold: #D4AF37;
            --maple-green: #228B22;
        }
                """
                # Insert CSS variables if not present
                if '<style>' in content:
                    content = content.replace('<style>', f'<style>{css_vars}')
            
            # Add Charter quotes if missing
            if 'Canadian Charter of Rights and Freedoms' not in content:
                charter_section = f"""
                    <div class="charter-quote">
                        "{self.charter_quotes['section_7']}"
                        <div class="charter-attribution">— Canadian Charter of Rights and Freedoms, Section 7</div>
                    </div>
                """
                # Insert before main content
                if '<div class="container">' in content:
                    content = content.replace('<div class="container">', f'{charter_section}<div class="container">')
            
            # Ensure maple leaf icons are present
            if 'fas fa-maple-leaf' not in content and 'index.html' in template_path:
                maple_leaves = """
    <!-- Floating maple leaves -->
    <div class="maple-leaf" style="top: 10%; left: 10%; animation-delay: 0s;">🍁</div>
    <div class="maple-leaf" style="top: 20%; right: 15%; animation-delay: 1s;">🍁</div>
    <div class="maple-leaf" style="top: 60%; left: 20%; animation-delay: 2s;">🍁</div>
                """
                content = content.replace('<body>', f'<body>{maple_leaves}')
            
            with open(template_path, 'w') as f:
                f.write(content)
                
            print(f"Updated {template_path} with Charter content")
            
        except Exception as e:
            logging.error(f"Error updating {template_path}: {e}")
    
    def generate_teresa_story_content(self):
        """Generate Teresa's story content for about page"""
        story_content = """
        <div class="teresa-story-section">
            <div class="story-header">
                <h2 class="story-title">Teresa's Journey: From Loss to Legal Advocacy</h2>
                <div class="charter-quote">
                    "Everyone has the right to life, liberty and security of the person and the right not to be deprived thereof except in accordance with the principles of fundamental justice."
                    <div class="charter-attribution">— Canadian Charter of Rights and Freedoms, Section 7</div>
                </div>
            </div>
            
            <div class="story-content">
                <div class="story-paragraph">
                    <h4>🍁 A Canadian Mom's Fight for Justice</h4>
                    <p>Seven years ago, I lost my children to the Children's Aid Society. For four years, I fought like hell to get them back, navigating a complex legal system that seemed designed to keep families apart rather than together.</p>
                </div>
                
                <div class="story-paragraph">
                    <h4>⚖️ Learning the System</h4>
                    <p>Through my journey, I learned that the Canadian legal system is not broken—it's working exactly as designed. But it's designed for those who can afford lawyers, who understand legal language, and who have the resources to fight back.</p>
                </div>
                
                <div class="story-paragraph">
                    <h4>🏛️ Building SmartDispute.ai</h4>
                    <p>After successfully representing myself and understanding how the system works, I realized that technology could level the playing field. SmartDispute.ai is my way of ensuring no Canadian has to face the legal system alone.</p>
                </div>
                
                <div class="charter-quote">
                    "Every individual is equal before and under the law and has the right to the equal protection and equal benefit of the law without discrimination."
                    <div class="charter-attribution">— Canadian Charter of Rights and Freedoms, Section 15</div>
                </div>
                
                <div class="story-paragraph">
                    <h4>🇨🇦 Our Mission</h4>
                    <p>SmartDispute.ai exists to make courtrooms a place of real fairness and justice—not a game of money and privilege. Every feature is built with the Canadian Charter of Rights and Freedoms as our foundation.</p>
                </div>
            </div>
        </div>
        """
        
        # Save to about.html template
        about_template_path = 'templates/about.html'
        if os.path.exists(about_template_path):
            with open(about_template_path, 'r') as f:
                content = f.read()
            
            # Replace or insert Teresa's story
            if 'teresa-story-section' in content:
                # Update existing story
                pattern = r'<div class="teresa-story-section">.*?</div>\s*</div>'
                content = re.sub(pattern, story_content, content, flags=re.DOTALL)
            else:
                # Insert new story before closing container
                content = content.replace('</div>\n</body>', f'{story_content}</div>\n</body>')
            
            with open(about_template_path, 'w') as f:
                f.write(content)
            
            print("Teresa's story content updated in about.html")
        
        return story_content
    
    def ensure_canadian_branding(self):
        """Ensure all pages have consistent Canadian branding"""
        branding_elements = {
            'title_suffix': ' - Empowering Canadians through Justice',
            'canadian_banner': '''
            <div class="canadian-banner">
                <div class="banner-text">
                    <i class="fas fa-maple-leaf maple-icon"></i>
                    Empowering Canadians through Justice – Protected by the Canadian Charter
                    <i class="fas fa-maple-leaf maple-icon"></i>
                </div>
            </div>
            ''',
            'footer_text': 'SmartDispute.ai - Proudly Canadian Legal Technology'
        }
        
        template_files = [f for f in os.listdir('templates') if f.endswith('.html')]
        
        for template_file in template_files:
            template_path = f'templates/{template_file}'
            try:
                with open(template_path, 'r') as f:
                    content = f.read()
                
                # Update title to include Canadian branding
                if 'SmartDispute.ai' in content and branding_elements['title_suffix'] not in content:
                    content = re.sub(
                        r'<title>([^<]*SmartDispute\.ai[^<]*)</title>',
                        f'<title>\\1{branding_elements["title_suffix"]}</title>',
                        content
                    )
                
                # Add Canadian banner if not present
                if 'canadian-banner' not in content and '<body>' in content:
                    content = content.replace('<body>', f'<body>{branding_elements["canadian_banner"]}')
                
                with open(template_path, 'w') as f:
                    f.write(content)
                    
            except Exception as e:
                logging.error(f"Error updating branding in {template_path}: {e}")
        
        print("Canadian branding consistency updated across all templates")
    
    def generate_legal_disclaimers(self):
        """Generate Canadian-specific legal disclaimers"""
        disclaimers = {
            'general': """
            This platform provides legal information and document generation tools. It does not provide legal advice. 
            Information provided is for general informational purposes only and should not be construed as legal advice. 
            For specific legal advice, please consult with a qualified lawyer licensed to practice in your Canadian jurisdiction.
            """,
            'privacy': """
            SmartDispute.ai complies with the Personal Information Protection and Electronic Documents Act (PIPEDA) 
            and applicable provincial privacy legislation. Your personal information is protected and used only 
            as outlined in our Privacy Policy.
            """,
            'charter_compliance': """
            All document generation and legal analysis is performed with respect for the Canadian Charter of Rights and Freedoms. 
            This platform is designed to support your Charter rights, including the right to equal protection and benefit of the law.
            """
        }
        
        # Save disclaimers to JSON file for easy access
        with open('legal_disclaimers.json', 'w') as f:
            json.dump(disclaimers, f, indent=2)
        
        print("Legal disclaimers generated and saved")
        return disclaimers

def main():
    """Run content management workflow based on command line argument"""
    if len(sys.argv) < 2:
        print("Usage: python content_management.py [update_charter|teresa_story|branding|disclaimers|all]")
        return
    
    workflow = ContentManagementWorkflow()
    command = sys.argv[1]
    
    if command == 'update_charter':
        workflow.update_charter_content()
    elif command == 'teresa_story':
        workflow.generate_teresa_story_content()
    elif command == 'branding':
        workflow.ensure_canadian_branding()
    elif command == 'disclaimers':
        workflow.generate_legal_disclaimers()
    elif command == 'all':
        workflow.update_charter_content()
        workflow.generate_teresa_story_content()
        workflow.ensure_canadian_branding()
        workflow.generate_legal_disclaimers()
        print("All content management tasks completed")
    else:
        print("Unknown command. Available: update_charter, teresa_story, branding, disclaimers, all")

if __name__ == '__main__':
    main()