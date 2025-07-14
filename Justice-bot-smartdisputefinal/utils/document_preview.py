"""
Interactive Legal Document Preview with AI-Powered Annotations
Provides real-time analysis and annotations for uploaded legal documents
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentAnnotation:
    """Represents an AI-powered annotation on a document"""
    id: str
    text: str
    start_char: int
    end_char: int
    annotation_type: str  # 'legal_term', 'key_clause', 'issue', 'recommendation'
    confidence: float
    explanation: str
    legal_reference: Optional[str] = None
    action_required: bool = False
    severity: str = 'info'  # 'info', 'warning', 'critical'

@dataclass
class DocumentSection:
    """Represents a section of the document"""
    title: str
    content: str
    start_char: int
    end_char: int
    importance: float
    section_type: str  # 'header', 'clause', 'paragraph', 'signature'

class LegalDocumentPreview:
    """Handles interactive preview and AI-powered analysis of legal documents"""
    
    def __init__(self):
        self.legal_terms_db = self._load_legal_terms()
        self.charter_references = self._load_charter_references()
        
    def _load_legal_terms(self) -> Dict[str, Dict[str, Any]]:
        """Load database of legal terms and definitions"""
        return {
            "plaintiff": {
                "definition": "The person who brings a civil lawsuit against another party",
                "category": "litigation",
                "importance": 0.9
            },
            "defendant": {
                "definition": "The person being sued or accused in a court proceeding",
                "category": "litigation", 
                "importance": 0.9
            },
            "liability": {
                "definition": "Legal responsibility for one's acts or omissions",
                "category": "civil_law",
                "importance": 0.8
            },
            "damages": {
                "definition": "Monetary compensation awarded to a party for loss or injury",
                "category": "remedies",
                "importance": 0.8
            },
            "breach of contract": {
                "definition": "Failure to perform any duty specified in a contract",
                "category": "contract_law",
                "importance": 0.9
            },
            "negligence": {
                "definition": "Failure to exercise reasonable care, resulting in harm",
                "category": "tort_law",
                "importance": 0.9
            },
            "jurisdiction": {
                "definition": "The authority of a court to hear and decide cases",
                "category": "procedure",
                "importance": 0.7
            },
            "statute of limitations": {
                "definition": "Time limit for bringing legal action",
                "category": "procedure",
                "importance": 0.8
            }
        }
    
    def _load_charter_references(self) -> Dict[str, Dict[str, Any]]:
        """Load Canadian Charter of Rights and Freedoms references"""
        return {
            "section 7": {
                "text": "Everyone has the right to life, liberty and security of the person",
                "context": "Fundamental justice and due process",
                "application": "Criminal law, administrative law, civil disputes affecting liberty"
            },
            "section 15": {
                "text": "Every individual is equal before and under the law",
                "context": "Equality rights and non-discrimination", 
                "application": "Human rights, employment, housing, services"
            },
            "section 8": {
                "text": "Everyone has the right to be secure against unreasonable search or seizure",
                "context": "Privacy and protection from government intrusion",
                "application": "Criminal investigations, regulatory inspections"
            }
        }
    
    def analyze_document(self, content: str, document_type: str = "general") -> Dict[str, Any]:
        """
        Perform comprehensive AI-powered analysis of legal document
        Returns structured analysis with annotations
        """
        try:
            logger.info(f"Analyzing document of type: {document_type}")
            
            # Extract sections
            sections = self._extract_sections(content)
            
            # Generate annotations
            annotations = self._generate_annotations(content, document_type)
            
            # Analyze key issues
            key_issues = self._identify_key_issues(content, document_type)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(content, key_issues)
            
            # Calculate document metrics
            metrics = self._calculate_document_metrics(content, annotations)
            
            analysis_result = {
                "document_id": f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "analysis_timestamp": datetime.now().isoformat(),
                "document_type": document_type,
                "sections": [section.__dict__ for section in sections],
                "annotations": [annotation.__dict__ for annotation in annotations],
                "key_issues": key_issues,
                "recommendations": recommendations,
                "metrics": metrics,
                "charter_compliance": self._assess_charter_compliance(content),
                "readability_score": self._calculate_readability(content),
                "completeness_score": self._assess_completeness(content, document_type)
            }
            
            logger.info(f"Document analysis completed with {len(annotations)} annotations")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return self._generate_fallback_analysis(content)
    
    def _extract_sections(self, content: str) -> List[DocumentSection]:
        """Extract logical sections from the document"""
        sections = []
        
        # Common legal document patterns
        header_patterns = [
            r'^[A-Z\s]{3,}:?\s*$',  # ALL CAPS headers
            r'^\d+\.\s+[A-Z][^.]*$',  # Numbered sections
            r'^ARTICLE\s+[IVX\d]+',  # Article headers
            r'^SECTION\s+\d+',  # Section headers
        ]
        
        lines = content.split('\n')
        current_section = None
        start_char = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a header
            is_header = any(re.match(pattern, line) for pattern in header_patterns)
            
            if is_header:
                # Save previous section
                if current_section:
                    sections.append(current_section)
                
                # Start new section
                current_section = DocumentSection(
                    title=line,
                    content="",
                    start_char=start_char,
                    end_char=start_char,
                    importance=0.8,
                    section_type="header"
                )
            elif current_section:
                current_section.content += line + "\n"
                current_section.end_char = start_char + len(line)
            
            start_char += len(line) + 1
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        # If no sections found, treat entire document as one section
        if not sections:
            sections.append(DocumentSection(
                title="Document Content",
                content=content,
                start_char=0,
                end_char=len(content),
                importance=1.0,
                section_type="paragraph"
            ))
        
        return sections
    
    def _generate_annotations(self, content: str, document_type: str) -> List[DocumentAnnotation]:
        """Generate AI-powered annotations for the document"""
        annotations = []
        content_lower = content.lower()
        
        # Annotate legal terms
        for term, info in self.legal_terms_db.items():
            pattern = r'\b' + re.escape(term.lower()) + r'\b'
            for match in re.finditer(pattern, content_lower):
                annotation = DocumentAnnotation(
                    id=f"term_{len(annotations)}",
                    text=term,
                    start_char=match.start(),
                    end_char=match.end(),
                    annotation_type="legal_term",
                    confidence=info["importance"],
                    explanation=info["definition"],
                    severity="info"
                )
                annotations.append(annotation)
        
        # Identify key clauses
        key_clause_patterns = [
            (r'indemnify|indemnification', "Indemnification clause - parties agree to protect each other from certain liabilities", 0.9),
            (r'force majeure', "Force majeure clause - addresses unforeseeable circumstances", 0.8),
            (r'termination|terminate', "Termination provision - specifies how agreement can end", 0.8),
            (r'confidential|non-disclosure', "Confidentiality provision - protects sensitive information", 0.8),
            (r'governing law', "Governing law clause - specifies which jurisdiction's laws apply", 0.9),
        ]
        
        for pattern, explanation, confidence in key_clause_patterns:
            for match in re.finditer(pattern, content_lower):
                annotation = DocumentAnnotation(
                    id=f"clause_{len(annotations)}",
                    text=content[match.start():match.end()],
                    start_char=match.start(),
                    end_char=match.end(),
                    annotation_type="key_clause",
                    confidence=confidence,
                    explanation=explanation,
                    severity="warning" if confidence > 0.8 else "info"
                )
                annotations.append(annotation)
        
        # Identify potential issues
        issue_patterns = [
            (r'waive|waiver', "Waiver of rights - carefully review what rights are being given up", 0.9, True),
            (r'exclusively|solely responsible', "Exclusive responsibility clause - high risk provision", 0.9, True),
            (r'penalty|penalties', "Penalty clause - review potential financial consequences", 0.8, True),
            (r'automatic renewal', "Automatic renewal clause - may create ongoing obligations", 0.7, True),
        ]
        
        for pattern, explanation, confidence, action_required in issue_patterns:
            for match in re.finditer(pattern, content_lower):
                annotation = DocumentAnnotation(
                    id=f"issue_{len(annotations)}",
                    text=content[match.start():match.end()],
                    start_char=match.start(),
                    end_char=match.end(),
                    annotation_type="issue",
                    confidence=confidence,
                    explanation=explanation,
                    action_required=action_required,
                    severity="critical" if confidence > 0.8 else "warning"
                )
                annotations.append(annotation)
        
        return annotations
    
    def _identify_key_issues(self, content: str, document_type: str) -> List[Dict[str, Any]]:
        """Identify key legal issues in the document"""
        issues = []
        content_lower = content.lower()
        
        # Contract-specific issues
        if document_type in ["contract", "agreement"]:
            if "consideration" not in content_lower:
                issues.append({
                    "type": "missing_element",
                    "severity": "warning",
                    "title": "Missing Consideration",
                    "description": "Document may lack clear consideration (exchange of value)",
                    "recommendation": "Ensure both parties receive something of value"
                })
            
            if "signature" not in content_lower and "signed" not in content_lower:
                issues.append({
                    "type": "execution_issue",
                    "severity": "critical",
                    "title": "No Signature Block",
                    "description": "Document appears to lack signature provisions",
                    "recommendation": "Add proper signature blocks for all parties"
                })
        
        # General legal issues
        if re.search(r'\$[\d,]+', content) and "dispute" not in content_lower:
            issues.append({
                "type": "risk_assessment",
                "severity": "warning",
                "title": "Financial Terms Without Dispute Resolution",
                "description": "Document involves money but lacks dispute resolution mechanism",
                "recommendation": "Consider adding mediation or arbitration clause"
            })
        
        return issues
    
    def _generate_recommendations(self, content: str, key_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        # Charter-based recommendations
        recommendations.append({
            "type": "charter_compliance",
            "priority": "high",
            "title": "Canadian Charter Compliance Review",
            "description": "Ensure document provisions align with Charter of Rights and Freedoms",
            "specific_actions": [
                "Review for equality rights (Section 15)",
                "Ensure procedural fairness (Section 7)", 
                "Verify no discrimination based on protected grounds"
            ],
            "charter_section": "sections 7, 15"
        })
        
        # Issue-based recommendations
        for issue in key_issues:
            if issue["severity"] == "critical":
                recommendations.append({
                    "type": "critical_fix",
                    "priority": "urgent",
                    "title": f"Address Critical Issue: {issue['title']}",
                    "description": issue["recommendation"],
                    "specific_actions": ["Immediate legal review required"]
                })
        
        # Document improvement recommendations
        recommendations.append({
            "type": "best_practice",
            "priority": "medium",
            "title": "Document Clarity Enhancement",
            "description": "Improve document readability and legal certainty",
            "specific_actions": [
                "Define technical terms in glossary",
                "Use clear, unambiguous language",
                "Add section numbering for easy reference"
            ]
        })
        
        return recommendations
    
    def _calculate_document_metrics(self, content: str, annotations: List[DocumentAnnotation]) -> Dict[str, Any]:
        """Calculate document analysis metrics"""
        word_count = len(content.split())
        char_count = len(content)
        
        # Count annotation types
        annotation_counts = {}
        for annotation in annotations:
            annotation_counts[annotation.annotation_type] = annotation_counts.get(annotation.annotation_type, 0) + 1
        
        # Calculate complexity score
        legal_term_density = annotation_counts.get("legal_term", 0) / max(word_count / 100, 1)
        complexity_score = min(legal_term_density * 10, 100)
        
        return {
            "word_count": word_count,
            "character_count": char_count,
            "annotation_count": len(annotations),
            "annotation_breakdown": annotation_counts,
            "complexity_score": round(complexity_score, 1),
            "estimated_read_time": max(1, word_count // 200)  # minutes
        }
    
    def _assess_charter_compliance(self, content: str) -> Dict[str, Any]:
        """Assess document compliance with Canadian Charter"""
        compliance_score = 85  # Base score
        issues = []
        
        content_lower = content.lower()
        
        # Check for discriminatory language
        discriminatory_terms = ["race", "gender", "religion", "sexual orientation", "disability"]
        for term in discriminatory_terms:
            if term in content_lower:
                # Context matters - this is a simple check
                issues.append(f"Contains reference to {term} - review for discriminatory provisions")
        
        # Check for due process protections
        if "notice" in content_lower and "opportunity" in content_lower:
            compliance_score += 5
        
        return {
            "overall_score": compliance_score,
            "assessment_date": datetime.now().isoformat(),
            "potential_issues": issues,
            "recommendations": [
                "Ensure equality of treatment for all parties",
                "Provide adequate notice periods",
                "Include fair dispute resolution mechanisms"
            ]
        }
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate document readability score"""
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())
        
        if sentences == 0:
            return 0
        
        # Simple readability approximation
        avg_sentence_length = words / sentences
        readability = max(0, 100 - (avg_sentence_length * 2))
        
        return round(readability, 1)
    
    def _assess_completeness(self, content: str, document_type: str) -> float:
        """Assess document completeness based on type"""
        content_lower = content.lower()
        score = 0
        max_score = 100
        
        # Common elements for most legal documents
        if "date" in content_lower:
            score += 15
        if "name" in content_lower or "party" in content_lower:
            score += 20
        if "signature" in content_lower or "signed" in content_lower:
            score += 25
        
        # Document-type specific elements
        if document_type == "contract":
            if "consideration" in content_lower:
                score += 20
            if "term" in content_lower or "duration" in content_lower:
                score += 10
            if "obligations" in content_lower or "duties" in content_lower:
                score += 10
        
        return min(score, max_score)
    
    def _generate_fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Generate basic analysis when AI processing fails"""
        word_count = len(content.split())
        
        return {
            "document_id": f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "analysis_timestamp": datetime.now().isoformat(),
            "document_type": "unknown",
            "sections": [{
                "title": "Document Content",
                "content": content[:500] + "..." if len(content) > 500 else content,
                "start_char": 0,
                "end_char": len(content),
                "importance": 1.0,
                "section_type": "paragraph"
            }],
            "annotations": [],
            "key_issues": [{
                "type": "analysis_error",
                "severity": "info",
                "title": "Basic Analysis Only",
                "description": "Full AI analysis unavailable - basic document structure provided",
                "recommendation": "Try uploading the document again for full analysis"
            }],
            "recommendations": [{
                "type": "general",
                "priority": "medium",
                "title": "Professional Legal Review",
                "description": "Consider having this document reviewed by a qualified legal professional",
                "specific_actions": ["Consult with a lawyer familiar with Canadian law"]
            }],
            "metrics": {
                "word_count": word_count,
                "character_count": len(content),
                "annotation_count": 0,
                "complexity_score": 50,
                "estimated_read_time": max(1, word_count // 200)
            },
            "charter_compliance": {
                "overall_score": 70,
                "assessment_date": datetime.now().isoformat(),
                "potential_issues": [],
                "recommendations": ["Ensure compliance with Canadian Charter of Rights and Freedoms"]
            },
            "readability_score": 60,
            "completeness_score": 50
        }

def create_preview_interface(analysis_result: Dict[str, Any]) -> str:
    """Generate HTML interface for interactive document preview"""
    
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SmartDispute.ai - Document Preview</title>
        <style>
            body {{
                font-family: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                color: #2c3e50;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #c41e3a 0%, #8b1538 100%);
                color: white;
                padding: 20px 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            }}
            .charter-badge {{
                background: rgba(255,255,255,0.2);
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
            }}
            .main-content {{
                display: grid;
                grid-template-columns: 1fr 350px;
                gap: 0;
                min-height: 600px;
            }}
            .document-viewer {{
                padding: 30px;
                background: #fdfdfd;
                border-right: 1px solid #e0e6ed;
                position: relative;
                overflow-y: auto;
                max-height: 70vh;
            }}
            .document-text {{
                line-height: 1.8;
                font-size: 16px;
                color: #34495e;
                white-space: pre-wrap;
                position: relative;
            }}
            .annotation {{
                border-bottom: 2px solid;
                cursor: pointer;
                transition: all 0.2s ease;
                position: relative;
            }}
            .annotation.legal-term {{
                border-color: #3498db;
                background: rgba(52, 152, 219, 0.1);
            }}
            .annotation.key-clause {{
                border-color: #f39c12;
                background: rgba(243, 156, 18, 0.1);
            }}
            .annotation.issue {{
                border-color: #e74c3c;
                background: rgba(231, 76, 60, 0.1);
            }}
            .annotation:hover {{
                background-opacity: 0.2;
                transform: translateY(-1px);
            }}
            .analysis-panel {{
                background: #f8f9fa;
                padding: 0;
                overflow-y: auto;
                max-height: 70vh;
            }}
            .panel-header {{
                background: #34495e;
                color: white;
                padding: 15px 20px;
                font-weight: 600;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .panel-section {{
                padding: 20px;
                border-bottom: 1px solid #e0e6ed;
            }}
            .metric-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 20px;
            }}
            .metric-card {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #c41e3a;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: 700;
                color: #c41e3a;
                margin-bottom: 5px;
            }}
            .metric-label {{
                font-size: 12px;
                color: #7f8c8d;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .recommendation {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 12px;
                border-left: 4px solid;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            .recommendation.high {{ border-color: #e74c3c; }}
            .recommendation.medium {{ border-color: #f39c12; }}
            .recommendation.low {{ border-color: #27ae60; }}
            .recommendation-title {{
                font-weight: 600;
                margin-bottom: 8px;
                color: #2c3e50;
            }}
            .recommendation-desc {{
                font-size: 14px;
                color: #5a6c7d;
                line-height: 1.4;
            }}
            .charter-section {{
                background: linear-gradient(135deg, #c41e3a 0%, #8b1538 100%);
                color: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
            }}
            .charter-score {{
                font-size: 36px;
                font-weight: 700;
                margin-bottom: 10px;
            }}
            .annotation-tooltip {{
                position: absolute;
                background: #2c3e50;
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 14px;
                max-width: 300px;
                z-index: 1000;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                display: none;
            }}
            .maple-leaf {{
                color: #c41e3a;
                margin-right: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><span class="maple-leaf">🍁</span>SmartDispute.ai Document Preview</h1>
                <div class="charter-badge">Canadian Charter Compliant</div>
            </div>
            
            <div class="main-content">
                <div class="document-viewer">
                    <div class="document-text" id="documentText">
                        {document_content}
                    </div>
                    <div class="annotation-tooltip" id="tooltip"></div>
                </div>
                
                <div class="analysis-panel">
                    <div class="panel-header">AI Analysis Results</div>
                    
                    <div class="panel-section">
                        <div class="charter-section">
                            <div class="charter-score">{charter_score}%</div>
                            <div>Charter Compliance Score</div>
                        </div>
                        
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value">{word_count}</div>
                                <div class="metric-label">Words</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{annotation_count}</div>
                                <div class="metric-label">Annotations</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{complexity_score}</div>
                                <div class="metric-label">Complexity</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{readability_score}</div>
                                <div class="metric-label">Readability</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="panel-section">
                        <div class="panel-header">Key Recommendations</div>
                        {recommendations_html}
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const annotations = {annotations_json};
            
            // Apply annotations to document text
            function applyAnnotations() {{
                const textElement = document.getElementById('documentText');
                let content = textElement.textContent;
                
                // Sort annotations by start position (descending) to avoid offset issues
                annotations.sort((a, b) => b.start_char - a.start_char);
                
                annotations.forEach(annotation => {{
                    const before = content.substring(0, annotation.start_char);
                    const annotated = content.substring(annotation.start_char, annotation.end_char);
                    const after = content.substring(annotation.end_char);
                    
                    const annotationHtml = `<span class="annotation ${{annotation.annotation_type}}" 
                        data-annotation="${{JSON.stringify(annotation).replace(/"/g, '&quot;')}}">${{annotated}}</span>`;
                    
                    content = before + annotationHtml + after;
                }});
                
                textElement.innerHTML = content;
            }}
            
            // Handle annotation hover
            document.addEventListener('mouseover', function(e) {{
                if (e.target.classList.contains('annotation')) {{
                    const tooltip = document.getElementById('tooltip');
                    const annotation = JSON.parse(e.target.getAttribute('data-annotation').replace(/&quot;/g, '"'));
                    
                    tooltip.innerHTML = `
                        <strong>${{annotation.text}}</strong><br>
                        <em>${{annotation.annotation_type.replace('_', ' ').toUpperCase()}}</em><br>
                        ${{annotation.explanation}}
                        ${{annotation.action_required ? '<br><strong>⚠️ Action Required</strong>' : ''}}
                    `;
                    
                    tooltip.style.display = 'block';
                    tooltip.style.left = e.pageX + 10 + 'px';
                    tooltip.style.top = e.pageY - 10 + 'px';
                }}
            }});
            
            document.addEventListener('mouseout', function(e) {{
                if (e.target.classList.contains('annotation')) {{
                    document.getElementById('tooltip').style.display = 'none';
                }}
            }});
            
            // Initialize
            applyAnnotations();
        </script>
    </body>
    </html>
    '''
    
    # Prepare document content (first section or full content)
    document_content = ""
    if analysis_result.get("sections"):
        document_content = analysis_result["sections"][0]["content"]
    else:
        document_content = "No document content available for preview"
    
    # Prepare recommendations HTML
    recommendations_html = ""
    for rec in analysis_result.get("recommendations", []):
        priority_class = rec.get("priority", "medium")
        recommendations_html += f'''
        <div class="recommendation {priority_class}">
            <div class="recommendation-title">{rec.get("title", "Recommendation")}</div>
            <div class="recommendation-desc">{rec.get("description", "No description available")}</div>
        </div>
        '''
    
    # Get metrics
    metrics = analysis_result.get("metrics", {})
    charter = analysis_result.get("charter_compliance", {})
    
    return html_template.format(
        document_content=document_content,
        charter_score=charter.get("overall_score", 70),
        word_count=metrics.get("word_count", 0),
        annotation_count=metrics.get("annotation_count", 0),
        complexity_score=metrics.get("complexity_score", 0),
        readability_score=analysis_result.get("readability_score", 0),
        recommendations_html=recommendations_html,
        annotations_json=json.dumps(analysis_result.get("annotations", []))
    )