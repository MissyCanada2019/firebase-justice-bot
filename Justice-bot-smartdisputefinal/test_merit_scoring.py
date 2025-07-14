#!/usr/bin/env python3
"""Test merit scoring and document generation functionality"""

from app import app
from database_fix import db
from models import User, Case
from services.ai_service import analyze_legal_case, calculate_merit_score
import json

with app.app_context():
    # Find a test user
    user = User.query.filter_by(email='test@smartdispute.ai').first()
    
    if user:
        print("✓ Test user found")
        
        # Create a test case with good evidence
        test_case_text = """
        I have documented evidence of wrongful dismissal from my employer.
        I have termination letter, email correspondence, witness statements, 
        and pay stubs showing inconsistencies. The employer terminated me 
        without cause after I reported safety violations. I have photos of 
        the unsafe conditions and written complaints I filed with HR.
        """
        
        print("\nTesting AI Analysis...")
        try:
            # Test AI analysis
            ai_analysis = analyze_legal_case(test_case_text, 'employment')
            print(f"✓ AI Analysis completed")
            print(f"  - Classification: {ai_analysis.get('classification', 'N/A')}")
            print(f"  - Summary: {ai_analysis.get('summary', 'N/A')[:100]}...")
            print(f"  - Urgency: {ai_analysis.get('urgency', 'N/A')}")
            
            # Test merit scoring
            merit_score = calculate_merit_score(test_case_text, 'employment', ai_analysis)
            print(f"\n✓ Merit Score calculated: {merit_score}/100")
            
            # Create a test case in database
            case = Case(
                user_id=user.id,
                title="Test Employment Case - Wrongful Dismissal",
                description=test_case_text,
                legal_issue_type='employment',
                merit_score=merit_score,
                ai_summary=ai_analysis.get('summary', ''),
                recommended_actions=json.dumps(ai_analysis.get('recommendations', [])),
                status='analyzed'
            )
            
            db.session.add(case)
            db.session.commit()
            
            print(f"\n✓ Test case created with ID: {case.id}")
            print(f"✓ Merit scoring system is working!")
            print(f"\nDocument generation will be available when merit score >= 40")
            print(f"Your test case scored: {merit_score}/100")
            
        except Exception as e:
            print(f"\n✗ Error during testing: {e}")
            print("\nNote: AI analysis requires OpenAI API key to be set")
    else:
        print("✗ No test user found")