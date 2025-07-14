"""
AI Service for Justice-Bot
Legal case analysis and merit scoring using OpenAI
"""

import os
import json
import re
from typing import Dict, Any, Optional
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Canadian legal issue classifications
LEGAL_CATEGORIES = {
    'family': ['divorce', 'custody', 'child support', 'spousal support', 'separation', 'parenting'],
    'landlord_tenant': ['eviction', 'rent', 'repairs', 'lease', 'deposit', 'ltb'],
    'small_claims': ['debt', 'property damage', 'breach of contract', 'services', 'money owed'],
    'employment': ['wrongful dismissal', 'harassment', 'wages', 'overtime', 'discrimination'],
    'criminal': ['assault', 'theft', 'fraud', 'driving', 'drug', 'court order'],
    'civil_rights': ['discrimination', 'human rights', 'privacy', 'charter rights'],
    'immigration': ['refugee', 'visa', 'citizenship', 'deportation', 'work permit'],
    'child_protection': ['cas', 'child welfare', 'custody', 'access', 'supervision']
}

def analyze_legal_case(case_text: str, issue_type: str) -> Dict[str, Any]:
    """
    Analyze legal case using OpenAI to classify and provide recommendations
    """
    try:
        prompt = f"""
        You are a Canadian legal assistant AI. Analyze this legal case and provide structured analysis.
        
        Case Type: {issue_type}
        Case Description: {case_text}
        
        Please provide analysis in JSON format with these fields:
        - classification: Specific legal issue classification
        - summary: Brief 2-3 sentence summary of the case
        - strength_factors: List of factors that strengthen the case
        - weakness_factors: List of factors that weaken the case
        - recommendations: List of recommended next steps
        - urgency: "low", "medium", or "high"
        - estimated_timeline: Estimated time to resolution
        - potential_costs: Estimated cost range in CAD
        
        Focus on Canadian law and provide practical, actionable advice.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Canadian legal analyst. Provide accurate, helpful analysis based on Canadian law."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse the response
        content = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        try:
            # Look for JSON block
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                # Fallback to basic parsing
                analysis = parse_text_analysis(content, case_text, issue_type)
        except json.JSONDecodeError:
            analysis = parse_text_analysis(content, case_text, issue_type)
        
        return analysis
        
    except Exception as e:
        # Fallback analysis
        return {
            "classification": classify_issue_basic(case_text, issue_type),
            "summary": f"Case involves {issue_type} matter requiring legal review.",
            "strength_factors": ["Documentation provided", "Clear description of issues"],
            "weakness_factors": ["Analysis incomplete due to technical issues"],
            "recommendations": ["Consult with legal professional", "Gather additional documentation"],
            "urgency": "medium",
            "estimated_timeline": "2-6 months",
            "potential_costs": "$500-$2000 CAD",
            "error": str(e)
        }

def calculate_merit_score(case_text: str, issue_type: str, ai_analysis: Dict[str, Any]) -> int:
    """
    Calculate merit score (1-100) based on case strength
    """
    try:
        base_score = 50  # Neutral starting point
        
        # Keyword-based scoring
        strength_keywords = {
            'family': ['documented', 'evidence', 'witnesses', 'income', 'records'],
            'landlord_tenant': ['lease', 'receipts', 'photos', 'notices', 'repairs'],
            'small_claims': ['contract', 'receipts', 'invoices', 'written agreement', 'proof'],
            'employment': ['termination letter', 'pay stubs', 'email', 'witnesses', 'records'],
            'criminal': ['alibi', 'witnesses', 'evidence', 'procedural error'],
            'civil_rights': ['documentation', 'witnesses', 'patterns', 'complaints']
        }
        
        weakness_keywords = {
            'general': ['unclear', 'no evidence', 'no documentation', 'verbal only', 'unsure']
        }
        
        # Score based on keywords
        text_lower = case_text.lower()
        category_keywords = strength_keywords.get(issue_type, strength_keywords.get('family', []))
        
        strength_count = sum(1 for keyword in category_keywords if keyword in text_lower)
        weakness_count = sum(1 for keyword in weakness_keywords['general'] if keyword in text_lower)
        
        # Adjust score based on keywords
        base_score += (strength_count * 8) - (weakness_count * 10)
        
        # Factor in AI analysis if available
        if ai_analysis:
            strength_factors = len(ai_analysis.get('strength_factors', []))
            weakness_factors = len(ai_analysis.get('weakness_factors', []))
            
            # Adjust based on AI analysis
            base_score += (strength_factors * 5) - (weakness_factors * 5)
            
            # Urgency adjustment
            urgency = ai_analysis.get('urgency', 'medium')
            if urgency == 'high':
                base_score += 10
            elif urgency == 'low':
                base_score -= 5
        
        # Length factor (more detailed cases tend to be stronger)
        if len(case_text) > 500:
            base_score += 5
        elif len(case_text) < 100:
            base_score -= 10
        
        # Ensure score is within bounds
        return max(1, min(100, base_score))
        
    except Exception:
        return 50  # Default neutral score

def classify_issue_basic(case_text: str, issue_type: str) -> str:
    """
    Basic classification using keyword matching
    """
    text_lower = case_text.lower()
    
    # Try to find more specific classification
    for category, keywords in LEGAL_CATEGORIES.items():
        if category == issue_type or any(keyword in text_lower for keyword in keywords):
            # Find the most specific match
            for keyword in keywords:
                if keyword in text_lower:
                    return f"{category.replace('_', ' ').title()} - {keyword.title()}"
    
    return issue_type.replace('_', ' ').title()

def parse_text_analysis(content: str, case_text: str, issue_type: str) -> Dict[str, Any]:
    """
    Parse analysis from text response when JSON parsing fails
    """
    return {
        "classification": classify_issue_basic(case_text, issue_type),
        "summary": extract_summary(content) or f"Legal matter involving {issue_type}",
        "strength_factors": extract_list_items(content, "strength") or ["Case details provided"],
        "weakness_factors": extract_list_items(content, "weakness") or ["Requires legal review"],
        "recommendations": extract_list_items(content, "recommend") or ["Seek legal advice"],
        "urgency": extract_urgency(content) or "medium",
        "estimated_timeline": extract_timeline(content) or "2-6 months",
        "potential_costs": extract_costs(content) or "$500-$2000 CAD"
    }

def extract_summary(text: str) -> Optional[str]:
    """Extract summary from text"""
    lines = text.split('\n')
    for line in lines:
        if 'summary' in line.lower() and len(line) > 20:
            return line.split(':', 1)[-1].strip()
    return None

def extract_list_items(text: str, keyword: str) -> list:
    """Extract list items containing keyword"""
    items = []
    lines = text.split('\n')
    in_section = False
    
    for line in lines:
        line = line.strip()
        if keyword.lower() in line.lower():
            in_section = True
        elif in_section and line.startswith('-'):
            items.append(line[1:].strip())
        elif in_section and not line:
            break
    
    return items[:5]  # Limit to 5 items

def extract_urgency(text: str) -> Optional[str]:
    """Extract urgency level"""
    text_lower = text.lower()
    if 'high' in text_lower and 'urgency' in text_lower:
        return 'high'
    elif 'low' in text_lower and 'urgency' in text_lower:
        return 'low'
    return 'medium'

def extract_timeline(text: str) -> Optional[str]:
    """Extract timeline information"""
    # Look for timeline patterns
    import re
    patterns = [
        r'(\d+[-\s]?\d*\s*(?:months?|weeks?|years?))',
        r'(timeline[:\s]+[^.\n]+)',
        r'(estimated[:\s]+[^.\n]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def extract_costs(text: str) -> Optional[str]:
    """Extract cost information"""
    import re
    # Look for cost patterns
    cost_patterns = [
        r'\$[\d,]+[-\s]?\$?[\d,]*\s*CAD',
        r'\$[\d,]+[-\s]?\$?[\d,]*',
        r'cost[s]?[:\s]+\$?[\d,]+',
    ]
    
    for pattern in cost_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return None