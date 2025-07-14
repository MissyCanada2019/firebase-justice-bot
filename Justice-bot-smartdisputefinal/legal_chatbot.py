"""
24/7 Legal Chatbot for SmartDispute.ai
Provides plain language legal guidance and hearing preparation
"""

import os
import logging
from datetime import datetime
from models import User, Case, db
from gemini_analyzer import get_gemini_client
from google.genai import types
from flask_login import login_required, current_user
import json

class LegalChatbot:
    def __init__(self):
        self.conversation_memory = {}
        self.legal_knowledge_base = self.load_legal_knowledge()
        self.conversation_templates = self.load_conversation_templates()
        
    def load_legal_knowledge(self):
        """Load Canadian legal knowledge base for chatbot responses"""
        return {
            'housing_law': {
                'key_acts': ['Residential Tenancies Act', 'Human Rights Code'],
                'common_issues': ['rent increases', 'evictions', 'maintenance', 'harassment'],
                'tribunals': ['Landlord and Tenant Board (LTB)', 'Human Rights Tribunal (HRTO)'],
                'forms': ['T2 Application', 'T6 Application', 'Form A (HRTO)']
            },
            'employment_law': {
                'key_acts': ['Employment Standards Act', 'Human Rights Code', 'Labour Relations Act'],
                'common_issues': ['wrongful dismissal', 'harassment', 'unpaid wages', 'discrimination'],
                'tribunals': ['Employment Standards Officer', 'Human Rights Tribunal', 'Labour Relations Board'],
                'forms': ['Employment Standards Complaint', 'HRTO Application']
            },
            'family_law': {
                'key_acts': ['Family Law Act', 'Divorce Act', 'Children\'s Law Reform Act'],
                'common_issues': ['custody', 'child support', 'spousal support', 'access'],
                'tribunals': ['Superior Court of Justice', 'Family Court'],
                'forms': ['Application to Court', 'Financial Statement', 'Parenting Plan']
            },
            'charter_rights': {
                'key_sections': {
                    'section_7': 'Liberty and security of the person',
                    'section_8': 'Unreasonable search and seizure',
                    'section_15': 'Equality rights',
                    'section_24': 'Enforcement of Charter rights'
                },
                'applications': ['Charter applications', 'Constitutional challenges', 'Human rights complaints']
            }
        }
    
    def load_conversation_templates(self):
        """Load conversation templates for different legal scenarios"""
        return {
            'greeting': {
                'message': "Hello! I'm your legal assistant. I can help you understand your rights and navigate the legal system in Canada. What legal issue are you facing today?",
                'options': [
                    "Housing/Tenant Issues",
                    "Employment Problems", 
                    "Family Law Matters",
                    "Human Rights Violations",
                    "I'm not sure - help me figure it out"
                ]
            },
            'housing_intake': {
                'questions': [
                    "Are you a tenant or landlord?",
                    "What province are you in?", 
                    "What's the main issue? (rent increase, eviction notice, maintenance, harassment, etc.)",
                    "When did this issue start?",
                    "Have you documented any communications with the other party?"
                ]
            },
            'employment_intake': {
                'questions': [
                    "Are you currently employed or were you terminated?",
                    "What province do you work in?",
                    "What's the issue? (dismissal, harassment, unpaid wages, discrimination, etc.)",
                    "How long were you employed?",
                    "Do you have any written documentation?"
                ]
            },
            'hearing_prep': {
                'checklist': [
                    "Organize your evidence chronologically",
                    "Prepare a timeline of events",
                    "Practice explaining your case in 5 minutes",
                    "Bring multiple copies of all documents",
                    "Arrive early and dress professionally",
                    "Bring a support person if allowed",
                    "Prepare questions for the other party's witnesses"
                ]
            }
        }
    
    def start_conversation(self, user_id, initial_message=None):
        """Start a new conversation with the chatbot"""
        conversation_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.conversation_memory[conversation_id] = {
            'user_id': user_id,
            'messages': [],
            'context': {},
            'current_flow': 'greeting',
            'created_at': datetime.now().isoformat()
        }
        
        if initial_message:
            return self.process_message(conversation_id, initial_message)
        else:
            return self.get_greeting_response(conversation_id)
    
    def get_greeting_response(self, conversation_id):
        """Get initial greeting response"""
        template = self.conversation_templates['greeting']
        
        response = {
            'message': template['message'],
            'options': template['options'],
            'conversation_id': conversation_id,
            'requires_selection': True
        }
        
        self.add_message_to_history(conversation_id, 'bot', response['message'])
        return response
    
    def process_message(self, conversation_id, user_message):
        """Process user message and generate appropriate response"""
        try:
            if conversation_id not in self.conversation_memory:
                return self.start_conversation(user_message.split('_')[0], user_message)
            
            conversation = self.conversation_memory[conversation_id]
            self.add_message_to_history(conversation_id, 'user', user_message)
            
            # Determine response based on current flow
            current_flow = conversation.get('current_flow', 'general')
            
            if current_flow == 'greeting':
                response = self.handle_initial_selection(conversation_id, user_message)
            elif current_flow == 'intake':
                response = self.handle_intake_questions(conversation_id, user_message)
            elif current_flow == 'legal_guidance':
                response = self.provide_legal_guidance(conversation_id, user_message)
            elif current_flow == 'hearing_prep':
                response = self.provide_hearing_preparation(conversation_id, user_message)
            else:
                response = self.generate_ai_response(conversation_id, user_message)
            
            self.add_message_to_history(conversation_id, 'bot', response['message'])
            return response
            
        except Exception as e:
            logging.error(f"Error processing chatbot message: {e}")
            return {
                'message': "I'm sorry, I encountered an error. Let me connect you with our legal guidance system.",
                'conversation_id': conversation_id,
                'error': True
            }
    
    def handle_initial_selection(self, conversation_id, selection):
        """Handle initial legal area selection"""
        conversation = self.conversation_memory[conversation_id]
        
        area_mapping = {
            'housing': 'housing_law',
            'tenant': 'housing_law', 
            'employment': 'employment_law',
            'family': 'family_law',
            'human rights': 'charter_rights'
        }
        
        selection_lower = selection.lower()
        legal_area = None
        
        for key, area in area_mapping.items():
            if key in selection_lower:
                legal_area = area
                break
        
        if not legal_area:
            return {
                'message': "I can help you identify the right legal area. Can you describe your situation in a few sentences?",
                'conversation_id': conversation_id,
                'requires_input': True
            }
        
        conversation['context']['legal_area'] = legal_area
        conversation['current_flow'] = 'intake'
        
        # Start intake questions
        if legal_area == 'housing_law':
            template = self.conversation_templates['housing_intake']
        elif legal_area == 'employment_law':
            template = self.conversation_templates['employment_intake']
        else:
            template = {'questions': ["Can you describe your legal situation in detail?"]}
        
        conversation['context']['intake_questions'] = template['questions']
        conversation['context']['current_question'] = 0
        
        return {
            'message': f"I'll help you with your {legal_area.replace('_', ' ')} matter. Let's start with some questions to understand your situation better.\n\n{template['questions'][0]}",
            'conversation_id': conversation_id,
            'requires_input': True
        }
    
    def handle_intake_questions(self, conversation_id, answer):
        """Handle intake questionnaire"""
        conversation = self.conversation_memory[conversation_id]
        context = conversation['context']
        
        # Store the answer
        question_index = context['current_question']
        questions = context['intake_questions']
        
        if 'answers' not in context:
            context['answers'] = {}
        
        context['answers'][f'question_{question_index}'] = answer
        
        # Move to next question
        next_question_index = question_index + 1
        
        if next_question_index < len(questions):
            context['current_question'] = next_question_index
            return {
                'message': questions[next_question_index],
                'conversation_id': conversation_id,
                'requires_input': True
            }
        else:
            # Intake complete, provide guidance
            conversation['current_flow'] = 'legal_guidance'
            return self.provide_initial_legal_guidance(conversation_id)
    
    def provide_initial_legal_guidance(self, conversation_id):
        """Provide initial legal guidance based on intake"""
        conversation = self.conversation_memory[conversation_id]
        context = conversation['context']
        legal_area = context.get('legal_area', 'general')
        
        knowledge = self.legal_knowledge_base.get(legal_area, {})
        
        guidance = f"Based on your answers, here's what I can tell you about your {legal_area.replace('_', ' ')} situation:\n\n"
        
        # Add relevant information
        if 'key_acts' in knowledge:
            guidance += f"**Relevant Laws:** {', '.join(knowledge['key_acts'])}\n\n"
        
        if 'tribunals' in knowledge:
            guidance += f"**Where to File:** {', '.join(knowledge['tribunals'])}\n\n"
        
        if 'forms' in knowledge:
            guidance += f"**Required Forms:** {', '.join(knowledge['forms'])}\n\n"
        
        guidance += "What would you like to know more about?\n"
        
        options = [
            "What are my legal rights?",
            "What evidence do I need?",
            "How do I file my case?",
            "How do I prepare for a hearing?",
            "What are my chances of winning?"
        ]
        
        return {
            'message': guidance,
            'options': options,
            'conversation_id': conversation_id,
            'requires_selection': True
        }
    
    def provide_legal_guidance(self, conversation_id, question):
        """Provide specific legal guidance"""
        conversation = self.conversation_memory[conversation_id]
        legal_area = conversation['context'].get('legal_area', 'general')
        
        question_lower = question.lower()
        
        if 'rights' in question_lower:
            return self.explain_legal_rights(conversation_id, legal_area)
        elif 'evidence' in question_lower:
            return self.explain_evidence_requirements(conversation_id, legal_area)
        elif 'file' in question_lower or 'forms' in question_lower:
            return self.explain_filing_process(conversation_id, legal_area)
        elif 'hearing' in question_lower or 'prepare' in question_lower:
            return self.provide_hearing_preparation(conversation_id, question)
        elif 'chances' in question_lower or 'winning' in question_lower:
            return self.assess_case_strength(conversation_id)
        else:
            return self.generate_ai_response(conversation_id, question)
    
    def explain_legal_rights(self, conversation_id, legal_area):
        """Explain legal rights for specific area"""
        rights_info = {
            'housing_law': "As a tenant in Canada, you have the right to:\n• Live in a safe, well-maintained home\n• Privacy and quiet enjoyment\n• Protection from illegal rent increases\n• Protection from harassment or discrimination\n• Proper notice before eviction\n• Keep your deposit (with some exceptions)",
            
            'employment_law': "As an employee in Canada, you have the right to:\n• Minimum wage and overtime pay\n• Safe working conditions\n• Protection from discrimination and harassment\n• Reasonable notice of termination\n• Employment Insurance benefits if eligible\n• Accommodation for disabilities",
            
            'family_law': "In family law matters, you have the right to:\n• Equal treatment regardless of gender\n• Fair division of family property\n• Child and spousal support if eligible\n• Access to your children (best interests standard)\n• Legal representation\n• Mediation services"
        }
        
        message = rights_info.get(legal_area, "Your rights depend on your specific situation. Let me help you identify the applicable laws.")
        
        return {
            'message': message + "\n\nWould you like me to explain how to enforce these rights?",
            'conversation_id': conversation_id,
            'requires_input': True
        }
    
    def provide_hearing_preparation(self, conversation_id, question):
        """Provide hearing preparation guidance"""
        conversation = self.conversation_memory[conversation_id]
        conversation['current_flow'] = 'hearing_prep'
        
        checklist = self.conversation_templates['hearing_prep']['checklist']
        
        message = "Here's your hearing preparation checklist:\n\n"
        for i, item in enumerate(checklist, 1):
            message += f"{i}. {item}\n"
        
        message += "\nWould you like me to explain any of these steps in detail?"
        
        return {
            'message': message,
            'conversation_id': conversation_id,
            'requires_input': True
        }
    
    def generate_ai_response(self, conversation_id, user_message):
        """Generate AI response using Gemini for complex questions"""
        try:
            conversation = self.conversation_memory[conversation_id]
            legal_area = conversation['context'].get('legal_area', 'general')
            
            client = get_gemini_client()
            if not client:
                return self.get_fallback_response(conversation_id, user_message)
            
            # Build context from conversation history
            history = conversation.get('messages', [])
            context_messages = []
            for msg in history[-6:]:  # Last 6 messages for context
                context_messages.append(f"{msg['role']}: {msg['content']}")
            
            conversation_context = "\n".join(context_messages)
            
            system_prompt = f"""You are a Canadian legal assistant chatbot specializing in {legal_area.replace('_', ' ')}. 

Provide helpful, accurate legal information in plain language. Always:
- Focus on Canadian federal and provincial law
- Include relevant Charter rights where applicable  
- Suggest practical next steps
- Remind users this is information, not legal advice
- Keep responses conversational and under 200 words

Current conversation context:
{conversation_context}

User's current question: {user_message}"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=system_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=300
                )
            )
            
            if response.text:
                ai_response = response.text.strip()
                ai_response += "\n\n*This is legal information, not legal advice. Consider consulting with a qualified lawyer for your specific situation.*"
                
                return {
                    'message': ai_response,
                    'conversation_id': conversation_id,
                    'requires_input': True
                }
            else:
                return self.get_fallback_response(conversation_id, user_message)
                
        except Exception as e:
            logging.error(f"Error generating AI response: {e}")
            return self.get_fallback_response(conversation_id, user_message)
    
    def get_fallback_response(self, conversation_id, user_message):
        """Provide fallback response when AI is unavailable"""
        return {
            'message': "I understand you're asking about a complex legal matter. While I'd love to give you detailed guidance, I recommend:\n\n1. Reviewing the relevant laws and regulations\n2. Documenting your situation thoroughly\n3. Consulting with a qualified lawyer\n4. Checking our legal resource library\n\nIs there a specific aspect of the legal process I can help clarify?",
            'conversation_id': conversation_id,
            'requires_input': True
        }
    
    def add_message_to_history(self, conversation_id, role, content):
        """Add message to conversation history"""
        if conversation_id in self.conversation_memory:
            self.conversation_memory[conversation_id]['messages'].append({
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })

# Global instance
legal_chatbot = LegalChatbot()

def init_legal_chatbot(app):
    """Initialize legal chatbot with Flask app"""
    @app.route('/chat')
    def chat_interface():
        """Chat interface page"""
        from flask import render_template, request
        from flask_login import login_required, current_user
        
        case_id = request.args.get('case_id')
        return render_template('chat.html', case_id=case_id)
    
    @app.route('/chat/start', methods=['POST'])
    def start_chat():
        """Start new chat session"""
        from flask import request, jsonify
        from flask_login import login_required, current_user
        
        initial_message = request.json.get('message')
        response = legal_chatbot.start_conversation(current_user.id, initial_message)
        return jsonify(response)
    
    @app.route('/chat/message', methods=['POST'])
    def send_message():
        """Send message to chatbot"""
        from flask import request, jsonify
        from flask_login import login_required
        
        data = request.json
        conversation_id = data.get('conversation_id')
        message = data.get('message')
        
        response = legal_chatbot.process_message(conversation_id, message)
        return jsonify(response)
    
    app.logger.info("Legal chatbot initialized")
    return legal_chatbot