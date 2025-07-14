"""
Enhanced Legal AI Agents for SmartDispute.ai
Specialized agents for comprehensive Canadian legal analysis
"""
import os
from typing import Dict, List, Any
from agents import Agent, Runner

class CanadianLegalAgents:
    """
    Specialized AI agents for different aspects of Canadian legal work
    """
    
    def __init__(self):
        """Initialize specialized legal agents"""
        self.case_analyzer = Agent(
            name="CaseAnalyzer",
            instructions="""You are a specialized Canadian legal case analyzer with expertise in:
            - Family law and fathers' rights under Canadian Charter
            - Evidence evaluation and merit scoring
            - Jurisdiction-specific legal requirements
            - Charter Section 7, 15, and 24 applications
            
            Analyze cases objectively and provide actionable legal strategies.
            Focus on protecting fathers' rights and countering systematic bias."""
        )
        
        self.document_generator = Agent(
            name="DocumentGenerator", 
            instructions="""You are a Canadian legal document generator specializing in:
            - Court-ready applications and factums
            - Proper legal citations and formatting
            - Charter-based arguments and remedies
            - Family court procedures and requirements
            
            Generate professional documents that meet court standards.
            Include specific Charter protections and father-friendly legal strategies."""
        )
        
        self.strategy_advisor = Agent(
            name="StrategyAdvisor",
            instructions="""You are a Canadian legal strategy advisor focused on:
            - Self-representation guidance
            - Procedural protection strategies
            - Financial protection from court abuse
            - Bias mitigation and Charter challenges
            
            Provide comprehensive strategies that level the playing field for fathers.
            Emphasize constitutional protections and procedural safeguards."""
        )
    
    def analyze_case_evidence(self, case_facts: str, evidence_files: List[str]) -> Dict[str, Any]:
        """
        Comprehensive case analysis using specialized agent
        """
        prompt = f"""
        CASE ANALYSIS REQUEST
        
        Case Facts: {case_facts}
        Evidence Files: {', '.join(evidence_files)}
        
        Provide comprehensive analysis including:
        1. Merit Score (1-100) with detailed reasoning
        2. Key legal issues and Charter violations
        3. Strengths and weaknesses analysis
        4. Recommended legal strategy
        5. Potential bias risks and mitigation strategies
        6. Timeline and cost estimates
        7. Success probability assessment
        
        Focus on fathers' rights protection and Charter-based defenses.
        """
        
        try:
            result = Runner.run_sync(self.case_analyzer, prompt)
            return {
                'analysis': result.final_output if result else "Analysis unavailable",
                'agent_used': 'CaseAnalyzer',
                'success': bool(result)
            }
        except Exception as e:
            return {
                'analysis': f"Analysis error: {str(e)}",
                'agent_used': 'CaseAnalyzer',
                'success': False
            }
    
    def generate_court_document(self, document_type: str, case_data: Dict, user_info: Dict) -> Dict[str, Any]:
        """
        Generate professional court documents using specialized agent
        """
        prompt = f"""
        DOCUMENT GENERATION REQUEST
        
        Document Type: {document_type}
        Case Category: {case_data.get('category', 'Not specified')}
        User Province: {user_info.get('province', 'Not specified')}
        Case Facts: {case_data.get('facts', 'Not provided')}
        
        Generate a complete, court-ready {document_type} including:
        1. Proper legal formatting and structure
        2. Accurate legal citations (federal, provincial, municipal)
        3. Charter rights applications where applicable
        4. Factual allegations with evidence references
        5. Relief sought with specific remedies
        6. Legal arguments supporting the application
        7. Required signatures and filing information
        
        Ensure document follows Canadian court standards and protects fathers' rights.
        Include relevant Charter sections and constitutional arguments.
        """
        
        try:
            result = Runner.run_sync(self.document_generator, prompt)
            return {
                'document': result.final_output if result else "Document generation unavailable",
                'document_type': document_type,
                'agent_used': 'DocumentGenerator',
                'success': bool(result)
            }
        except Exception as e:
            return {
                'document': f"Document generation error: {str(e)}",
                'document_type': document_type,
                'agent_used': 'DocumentGenerator',
                'success': False
            }
    
    def get_legal_strategy(self, case_type: str, user_situation: str) -> Dict[str, Any]:
        """
        Comprehensive legal strategy recommendations
        """
        prompt = f"""
        LEGAL STRATEGY REQUEST
        
        Case Type: {case_type}
        User Situation: {user_situation}
        
        Provide comprehensive legal strategy including:
        1. Immediate actions to take
        2. Long-term strategic approach
        3. Procedural protections to implement
        4. Financial protection strategies
        5. Bias mitigation techniques
        6. Charter challenge opportunities
        7. Self-representation guidance
        8. Timeline and milestone planning
        
        Focus on protecting fathers from court abuse and financial ruin.
        Emphasize Charter protections and constitutional remedies.
        """
        
        try:
            result = Runner.run_sync(self.strategy_advisor, prompt)
            return {
                'strategy': result.final_output if result else "Strategy unavailable",
                'agent_used': 'StrategyAdvisor',
                'success': bool(result)
            }
        except Exception as e:
            return {
                'strategy': f"Strategy error: {str(e)}",
                'agent_used': 'StrategyAdvisor',
                'success': False
            }

# Global instance for use throughout the application
legal_agents = CanadianLegalAgents()

def init_legal_agents():
    """Initialize the legal agents system"""
    try:
        # Verify API key is available
        if not os.environ.get("OPENAI_API_KEY"):
            print("WARNING: OPENAI_API_KEY not found - AI agents disabled")
            return False
        
        print("Enhanced Legal AI Agents initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing legal agents: {e}")
        return False