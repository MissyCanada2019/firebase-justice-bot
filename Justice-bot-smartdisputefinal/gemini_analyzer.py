"""
Gemini AI Legal Analysis System for SmartDispute.ai
Uses Google's Gemini API for free legal document analysis
"""

import os
import logging
import json
from datetime import datetime
from google import genai
from google.genai import types
from pydantic import BaseModel

# Initialize Gemini client
def get_gemini_client():
    """Get Gemini client with API key"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.warning("GEMINI_API_KEY not found - falling back to basic analysis")
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Gemini client: {e}")
        return None

class LegalAnalysis(BaseModel):
    merit_score: int
    confidence_level: str
    key_facts: list
    legal_strengths: list
    legal_weaknesses: list
    recommended_actions: list
    relevant_laws: list
    timeline_estimate: str
    cost_estimate: str
    settlement_potential: str

def analyze_evidence_with_gemini(combined_text, processed_files, user):
    """
    Analyze legal evidence using Google Gemini AI
    Provides comprehensive merit scores and legal strategies
    """
    client = get_gemini_client()
    if not client:
        return get_enhanced_fallback_analysis(combined_text, processed_files, user)
    
    try:
        # Create comprehensive legal analysis prompt
        system_prompt = f"""You are a Canadian legal AI assistant specializing in legal document analysis.

Analyze the following legal documents and evidence for a case in {getattr(user, 'province', 'Ontario')}, Canada.

Provide a comprehensive legal analysis in JSON format with these exact fields:
- merit_score: Integer from 0-100 indicating case strength
- confidence_level: "high", "moderate", or "low"
- key_facts: Array of important facts extracted from documents
- legal_strengths: Array of strengths in the legal case
- legal_weaknesses: Array of potential weaknesses
- recommended_actions: Array of specific next steps
- relevant_laws: Array of applicable Canadian laws/statutes
- timeline_estimate: String describing expected timeline
- cost_estimate: String describing potential costs
- settlement_potential: "high", "moderate", or "low"

Focus on Canadian federal and provincial law, Charter rights, and jurisdiction-specific procedures.
Consider the user's legal issue type: {getattr(user, 'legal_issue_types', 'general legal matter')}

IMPORTANT: Respond only with valid JSON. Do not include explanatory text outside the JSON."""

        user_prompt = f"""Legal Documents and Evidence to Analyze:

{combined_text[:8000]}  # Limit to avoid token limits

Document Summary:
- Total documents: {len(processed_files)}
- User location: {getattr(user, 'city', 'Unknown')}, {getattr(user, 'province', 'Ontario')}
- Case type: {getattr(user, 'legal_issue_types', 'General legal matter')}

Provide detailed Canadian legal analysis in the specified JSON format."""

        # Generate analysis with Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=LegalAnalysis,
                temperature=0.3
            ),
        )

        if not response.text:
            logging.error("Empty response from Gemini")
            return get_enhanced_fallback_analysis(combined_text, processed_files, user)

        # Parse and enhance the response
        ai_analysis = json.loads(response.text)
        
        # Add metadata
        ai_analysis.update({
            'evidence_summary': f"Analyzed {len(processed_files)} documents with {len(combined_text)} characters",
            'ai_provider': 'Google Gemini',
            'analysis_date': datetime.now().isoformat(),
            'disclaimer': "This AI analysis provides legal information, not legal advice. We are not lawyers. Review all analysis with qualified legal counsel."
        })
        
        logging.info(f"Gemini analysis completed with merit score: {ai_analysis.get('merit_score', 'N/A')}")
        return ai_analysis
        
    except json.JSONDecodeError:
        logging.error("Failed to parse Gemini JSON response")
        return get_enhanced_fallback_analysis(combined_text, processed_files, user)
        
    except Exception as gemini_error:
        logging.error(f"Gemini API error: {gemini_error}")
        return get_enhanced_fallback_analysis(combined_text, processed_files, user)

def get_enhanced_fallback_analysis(combined_text, processed_files, user):
    """
    Enhanced fallback analysis when AI services are unavailable
    Provides structured legal guidance based on document content
    """
    
    # Analyze document content for key legal indicators
    text_lower = combined_text.lower()
    
    # Determine case type and base merit score
    family_keywords = ['custody', 'child support', 'divorce', 'separation', 'access', 'visitation']
    housing_keywords = ['landlord', 'tenant', 'rent', 'eviction', 'lease', 'housing']
    employment_keywords = ['termination', 'wrongful dismissal', 'employment', 'workplace', 'fired']
    criminal_keywords = ['charges', 'criminal', 'police', 'arrest', 'court date']
    
    case_type = "General Legal Matter"
    base_score = 50
    
    if any(keyword in text_lower for keyword in family_keywords):
        case_type = "Family Law"
        base_score = 55
    elif any(keyword in text_lower for keyword in housing_keywords):
        case_type = "Housing/Tenant Law"
        base_score = 60
    elif any(keyword in text_lower for keyword in employment_keywords):
        case_type = "Employment Law"
        base_score = 58
    elif any(keyword in text_lower for keyword in criminal_keywords):
        case_type = "Criminal Law"
        base_score = 45
    
    # Calculate merit score based on document strength indicators
    positive_indicators = ['evidence', 'witness', 'documentation', 'correspondence', 'agreement', 'contract']
    negative_indicators = ['dispute', 'denial', 'insufficient', 'unclear', 'missing']
    
    positive_count = sum(1 for indicator in positive_indicators if indicator in text_lower)
    negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
    
    merit_score = base_score + (positive_count * 3) - (negative_count * 2)
    merit_score = max(20, min(85, merit_score))  # Keep within reasonable bounds
    
    return {
        'merit_score': merit_score,
        'confidence_level': 'moderate',
        'key_facts': [
            f"Identified as {case_type} case",
            f"Analysis based on {len(processed_files)} uploaded documents",
            f"Document content: {len(combined_text)} characters analyzed"
        ],
        'legal_strengths': [
            "Documented evidence provided",
            "Multiple supporting documents available",
            "Clear timeline of events established"
        ],
        'legal_weaknesses': [
            "Full AI analysis unavailable - basic assessment only",
            "Professional legal review recommended",
            "Additional documentation may strengthen case"
        ],
        'recommended_actions': [
            f"Consult with a qualified {case_type.lower()} lawyer",
            "Organize all documentation chronologically",
            "Prepare detailed timeline of events",
            "Consider mediation or settlement options",
            "Research relevant provincial and federal laws"
        ],
        'relevant_laws': [
            "Canadian Charter of Rights and Freedoms",
            f"Provincial laws for {getattr(user, 'province', 'Ontario')}",
            "Federal legislation as applicable",
            "Municipal bylaws where relevant"
        ],
        'timeline_estimate': "2-12 months depending on case complexity and court availability",
        'cost_estimate': "$500-$5000+ depending on legal representation and case duration",
        'settlement_potential': 'moderate',
        'evidence_summary': f"Basic analysis of {len(processed_files)} documents",
        'ai_provider': 'Fallback Analysis System',
        'analysis_date': datetime.now().isoformat(),
        'disclaimer': "This is a basic analysis. For comprehensive AI-powered legal assessment, API credits are required. We are not lawyers - this provides legal information, not legal advice."
    }