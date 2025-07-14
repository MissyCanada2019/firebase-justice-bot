"""
Personalized Legal Resource Recommendation Engine for SmartDispute.ai
Analyzes user cases, legal history, and preferences to suggest relevant Canadian legal resources
"""
import logging
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Tuple, Optional
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, and_, or_
from app import db
from models import User, Case, Document, LegalReference, ChatMessage, ChatSession

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/recommendations')
logger = logging.getLogger(__name__)

class LegalRecommendationEngine:
    """
    Advanced recommendation engine for Canadian legal resources
    """
    
    def __init__(self):
        self.charter_sections = {
            1: "Guarantee of Rights and Freedoms",
            2: "Fundamental Freedoms",
            3: "Democratic Rights", 
            4: "Mobility Rights",
            5: "Legal Rights",
            6: "Equality Rights",
            7: "Life, Liberty and Security",
            8: "Search and Seizure",
            9: "Detention and Imprisonment", 
            10: "Arrest and Detention",
            11: "Criminal Proceedings",
            12: "Cruel and Unusual Treatment",
            13: "Self-Incrimination",
            14: "Interpreter Rights",
            15: "Equality Rights",
            16: "Official Languages",
            17: "Language of Parliament",
            18: "Parliamentary Records",
            19: "Court Proceedings",
            20: "Communications with Government",
            21: "Existing Constitutional Provisions",
            22: "Rights Preserved",
            23: "Minority Language Education",
            24: "Enforcement of Rights"
        }
        
        self.legal_categories = {
            'housing': ['tenant rights', 'landlord disputes', 'eviction', 'rent control', 'housing discrimination'],
            'employment': ['wrongful dismissal', 'workplace harassment', 'employment standards', 'human rights'],
            'consumer': ['unfair charges', 'consumer protection', 'contracts', 'warranty disputes'],
            'discrimination': ['human rights', 'charter rights', 'equality', 'accommodation'],
            'family': ['custody', 'support', 'divorce', 'domestic violence'],
            'immigration': ['refugee claims', 'deportation', 'citizenship', 'work permits'],
            'criminal': ['criminal defence', 'bail', 'sentencing', 'appeals'],
            'administrative': ['government decisions', 'benefits', 'licensing', 'regulatory'],
            'constitutional': ['charter challenges', 'constitutional law', 'government powers']
        }

    def analyze_user_profile(self, user_id: int) -> Dict:
        """Analyze user's legal profile and history"""
        user = User.query.get(user_id)
        if not user:
            return {}
        
        # Get user's cases
        cases = Case.query.filter_by(user_id=user_id).all()
        
        # Get user's documents
        documents = Document.query.filter_by(user_id=user_id).all()
        
        # Get user's chat history
        chat_sessions = ChatSession.query.filter_by(user_id=user_id).all()
        chat_messages = []
        for session in chat_sessions:
            messages = ChatMessage.query.filter_by(session_id=session.id).all()
            chat_messages.extend([msg.message for msg in messages])
        
        # Analyze case types
        case_types = [case.case_type for case in cases if case.case_type]
        case_type_frequency = Counter(case_types)
        
        # Analyze document types
        doc_types = [doc.file_type for doc in documents if doc.file_type]
        doc_type_frequency = Counter(doc_types)
        
        # Analyze keywords from chat messages
        keywords = self._extract_keywords_from_text(' '.join(chat_messages))
        
        # Determine user's legal interests
        legal_interests = self._categorize_legal_interests(case_types, keywords)
        
        # Calculate user experience level
        experience_level = self._calculate_experience_level(len(cases), len(documents), len(chat_messages))
        
        return {
            'user_id': user_id,
            'case_types': case_type_frequency,
            'document_types': doc_type_frequency,
            'legal_interests': legal_interests,
            'keywords': keywords,
            'experience_level': experience_level,
            'total_cases': len(cases),
            'total_documents': len(documents),
            'last_activity': max([case.updated_at for case in cases] + [datetime.utcnow()]) if cases else datetime.utcnow()
        }

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract legal keywords from text"""
        legal_keywords = [
            'charter', 'rights', 'discrimination', 'harassment', 'eviction', 'tenant', 'landlord',
            'employment', 'wrongful', 'dismissal', 'consumer', 'protection', 'contract', 'breach',
            'human rights', 'equality', 'accommodation', 'disability', 'privacy', 'defamation',
            'negligence', 'liability', 'damages', 'compensation', 'injunction', 'remedy',
            'tribunal', 'court', 'appeal', 'jurisdiction', 'statute', 'regulation', 'bylaw'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in legal_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))

    def _categorize_legal_interests(self, case_types: List[str], keywords: List[str]) -> Dict[str, float]:
        """Categorize user's legal interests by area"""
        interests = {}
        
        # Analyze case types
        for case_type in case_types:
            for category, terms in self.legal_categories.items():
                if any(term in case_type.lower() for term in terms):
                    interests[category] = interests.get(category, 0) + 1
        
        # Analyze keywords
        for keyword in keywords:
            for category, terms in self.legal_categories.items():
                if keyword in terms:
                    interests[category] = interests.get(category, 0) + 0.5
        
        # Normalize scores
        total_score = sum(interests.values())
        if total_score > 0:
            interests = {k: v/total_score for k, v in interests.items()}
        
        return interests

    def _calculate_experience_level(self, cases: int, documents: int, messages: int) -> str:
        """Calculate user's legal experience level"""
        total_activity = cases * 3 + documents * 2 + messages * 0.1
        
        if total_activity < 5:
            return 'beginner'
        elif total_activity < 20:
            return 'intermediate'
        else:
            return 'advanced'

    def get_charter_recommendations(self, legal_interests: Dict[str, float]) -> List[Dict]:
        """Get relevant Charter sections based on user interests"""
        charter_recommendations = []
        
        # Map legal interests to Charter sections
        charter_mapping = {
            'discrimination': [15, 2, 7],
            'housing': [7, 15, 8],
            'employment': [2, 7, 15],
            'consumer': [7, 8],
            'criminal': [7, 8, 9, 10, 11, 12, 13, 14, 24],
            'family': [7, 15],
            'immigration': [6, 7, 15],
            'administrative': [7, 24],
            'constitutional': [1, 24, 32]
        }
        
        section_scores = {}
        
        for interest, score in legal_interests.items():
            if interest in charter_mapping:
                for section in charter_mapping[interest]:
                    section_scores[section] = section_scores.get(section, 0) + score
        
        # Create recommendations
        for section, score in sorted(section_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
            charter_recommendations.append({
                'section': section,
                'title': self.charter_sections.get(section, f'Section {section}'),
                'relevance_score': round(score * 100, 1),
                'description': self._get_charter_description(section),
                'type': 'charter_section'
            })
        
        return charter_recommendations

    def _get_charter_description(self, section: int) -> str:
        """Get description for Charter section"""
        descriptions = {
            2: "Everyone has the fundamental freedoms of conscience, religion, thought, belief, opinion, expression, peaceful assembly and association.",
            7: "Everyone has the right to life, liberty and security of the person and the right not to be deprived thereof except in accordance with the principles of fundamental justice.",
            8: "Everyone has the right to be secure against unreasonable search or seizure.",
            15: "Every individual is equal before and under the law and has the right to the equal protection and equal benefit of the law without discrimination.",
            24: "Anyone whose rights or freedoms, as guaranteed by this Charter, have been infringed or denied may apply to a court for appropriate and just remedy."
        }
        return descriptions.get(section, f"Charter Section {section} - Fundamental Canadian Rights")

    def get_legal_precedent_recommendations(self, user_profile: Dict) -> List[Dict]:
        """Get relevant legal precedents and case law"""
        precedents = []
        
        # Get existing legal references from database
        references = LegalReference.query.filter(
            LegalReference.relevance_score > 0.5
        ).order_by(LegalReference.relevance_score.desc()).limit(10).all()
        
        # Score references based on user profile
        for ref in references:
            relevance_score = self._calculate_precedent_relevance(ref, user_profile)
            
            if relevance_score > 0.3:
                precedents.append({
                    'id': ref.id,
                    'title': ref.title,
                    'citation': ref.citation,
                    'source_type': ref.source_type,
                    'jurisdiction': ref.jurisdiction,
                    'year': ref.year,
                    'relevance_score': round(relevance_score * 100, 1),
                    'content_snippet': ref.content_snippet,
                    'url': ref.url,
                    'type': 'legal_precedent'
                })
        
        return sorted(precedents, key=lambda x: x['relevance_score'], reverse=True)[:5]

    def _calculate_precedent_relevance(self, reference: 'LegalReference', user_profile: Dict) -> float:
        """Calculate how relevant a legal precedent is to user"""
        relevance = reference.relevance_score
        
        # Boost based on user's legal interests
        ref_title_lower = reference.title.lower()
        ref_content_lower = (reference.content_snippet or '').lower()
        
        for interest, score in user_profile.get('legal_interests', {}).items():
            if interest in self.legal_categories:
                for term in self.legal_categories[interest]:
                    if term in ref_title_lower or term in ref_content_lower:
                        relevance += score * 0.3
        
        # Boost for recent cases
        if reference.year and reference.year > 2015:
            relevance += 0.1
        
        # Boost for Canadian jurisdiction
        if reference.jurisdiction and 'canada' in reference.jurisdiction.lower():
            relevance += 0.2
        
        return min(relevance, 1.0)

    def get_resource_recommendations(self, user_profile: Dict) -> List[Dict]:
        """Get recommended legal resources and tools"""
        resources = []
        
        experience_level = user_profile.get('experience_level', 'beginner')
        legal_interests = user_profile.get('legal_interests', {})
        
        # Canadian legal resources by category
        canadian_resources = {
            'housing': [
                {
                    'title': 'Residential Tenancies Act Guide',
                    'description': 'Comprehensive guide to tenant and landlord rights in Canada',
                    'url': '/resources/housing/residential-tenancies',
                    'difficulty': 'beginner',
                    'type': 'guide'
                },
                {
                    'title': 'Landlord and Tenant Board Forms',
                    'description': 'Official forms for housing disputes and applications',
                    'url': '/resources/housing/ltb-forms',
                    'difficulty': 'intermediate',
                    'type': 'forms'
                }
            ],
            'employment': [
                {
                    'title': 'Employment Standards Act Summary',
                    'description': 'Your rights and protections in the workplace',
                    'url': '/resources/employment/standards',
                    'difficulty': 'beginner',
                    'type': 'guide'
                },
                {
                    'title': 'Human Rights at Work',
                    'description': 'Understanding workplace discrimination and accommodation',
                    'url': '/resources/employment/human-rights',
                    'difficulty': 'intermediate',
                    'type': 'guide'
                }
            ],
            'consumer': [
                {
                    'title': 'Consumer Protection Laws',
                    'description': 'Understanding your rights when purchasing goods and services',
                    'url': '/resources/consumer/protection',
                    'difficulty': 'beginner',
                    'type': 'guide'
                }
            ],
            'discrimination': [
                {
                    'title': 'Human Rights Code Guide',
                    'description': 'Complete guide to human rights protections in Canada',
                    'url': '/resources/discrimination/human-rights',
                    'difficulty': 'intermediate',
                    'type': 'guide'
                }
            ]
        }
        
        # Add resources based on user interests
        for interest, score in legal_interests.items():
            if interest in canadian_resources and score > 0.1:
                for resource in canadian_resources[interest]:
                    # Filter by experience level
                    if (experience_level == 'beginner' and resource['difficulty'] in ['beginner', 'intermediate']) or \
                       (experience_level == 'intermediate' and resource['difficulty'] in ['beginner', 'intermediate', 'advanced']) or \
                       (experience_level == 'advanced'):
                        
                        resource_copy = resource.copy()
                        resource_copy['relevance_score'] = round(score * 100, 1)
                        resource_copy['category'] = interest
                        resources.append(resource_copy)
        
        return sorted(resources, key=lambda x: x['relevance_score'], reverse=True)[:8]

    def generate_recommendations(self, user_id: int) -> Dict:
        """Generate comprehensive recommendations for a user"""
        user_profile = self.analyze_user_profile(user_id)
        
        if not user_profile:
            return {'error': 'User not found or no data available'}
        
        recommendations = {
            'user_profile': user_profile,
            'charter_sections': self.get_charter_recommendations(user_profile.get('legal_interests', {})),
            'legal_precedents': self.get_legal_precedent_recommendations(user_profile),
            'resources': self.get_resource_recommendations(user_profile),
            'generated_at': datetime.utcnow().isoformat(),
            'next_update': (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        return recommendations

# Initialize the recommendation engine
recommendation_engine = LegalRecommendationEngine()

@recommendations_bp.route('/')
@login_required
def recommendations_dashboard():
    """Main recommendations dashboard"""
    recommendations = recommendation_engine.generate_recommendations(current_user.id)
    return render_template('recommendations/dashboard.html', recommendations=recommendations)

@recommendations_bp.route('/api/generate')
@login_required
def api_generate_recommendations():
    """API endpoint to generate recommendations"""
    recommendations = recommendation_engine.generate_recommendations(current_user.id)
    return jsonify(recommendations)

@recommendations_bp.route('/api/charter/<int:section>')
@login_required
def api_charter_section(section):
    """Get detailed information about a Charter section"""
    if section not in recommendation_engine.charter_sections:
        return jsonify({'error': 'Charter section not found'}), 404
    
    return jsonify({
        'section': section,
        'title': recommendation_engine.charter_sections[section],
        'description': recommendation_engine._get_charter_description(section),
        'full_text': f"Charter Section {section}: {recommendation_engine.charter_sections[section]}"
    })

@recommendations_bp.route('/api/update-interests', methods=['POST'])
@login_required
def api_update_interests():
    """Update user's legal interests manually"""
    try:
        data = request.get_json()
        interests = data.get('interests', {})
        
        # Store user preferences (you might want to add a UserPreferences model)
        # For now, we'll generate fresh recommendations
        recommendations = recommendation_engine.generate_recommendations(current_user.id)
        
        return jsonify({'success': True, 'recommendations': recommendations})
    
    except Exception as e:
        logger.error(f"Error updating user interests: {e}")
        return jsonify({'error': 'Failed to update interests'}), 500

def init_recommendation_engine(app):
    """Initialize recommendation engine with Flask app"""
    app.register_blueprint(recommendations_bp)
    logger.info("Legal recommendation engine initialized")