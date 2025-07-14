"""
Case Management System for SmartDispute.ai
Handles multi-stage legal proceedings with persistent data across court processes
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from models import Case, Document, User

def determine_case_stage(case: Case, documents: List[Document]) -> Dict[str, Any]:
    """Determine current stage of legal proceedings based on case data"""
    
    stage_info = {
        'current_stage': case.status or 'evidence_gathering',
        'progress_percentage': 0,
        'estimated_timeline': '',
        'stage_description': '',
        'completion_date': None
    }
    
    # Map case stages to progress percentages and descriptions
    stage_mapping = {
        'evidence_gathering': {
            'progress': 10,
            'description': 'Collecting and organizing evidence documents',
            'timeline': '2-4 weeks'
        },
        'analysis_complete': {
            'progress': 20,
            'description': 'AI analysis complete, merit score calculated',
            'timeline': '1-2 weeks'
        },
        'document_preparation': {
            'progress': 35,
            'description': 'Preparing legal documents and applications',
            'timeline': '1-3 weeks'
        },
        'filing_submitted': {
            'progress': 50,
            'description': 'Documents filed with court/tribunal',
            'timeline': '2-6 weeks for response'
        },
        'awaiting_response': {
            'progress': 60,
            'description': 'Waiting for opposing party response',
            'timeline': '30-60 days typical'
        },
        'discovery': {
            'progress': 70,
            'description': 'Document exchange and discovery process',
            'timeline': '3-6 months'
        },
        'mediation': {
            'progress': 75,
            'description': 'Alternative dispute resolution attempt',
            'timeline': '1-3 months'
        },
        'pre_trial': {
            'progress': 85,
            'description': 'Pre-trial motions and case management',
            'timeline': '2-6 months'
        },
        'trial_scheduled': {
            'progress': 90,
            'description': 'Trial date set, final preparations',
            'timeline': '1-4 weeks to trial'
        },
        'trial_completed': {
            'progress': 95,
            'description': 'Trial complete, awaiting judgment',
            'timeline': '2-8 weeks for decision'
        },
        'settlement': {
            'progress': 100,
            'description': 'Case resolved through settlement',
            'timeline': 'Complete'
        },
        'closed': {
            'progress': 100,
            'description': 'Case closed - judgment rendered',
            'timeline': 'Complete'
        }
    }
    
    current_stage = case.status or 'evidence_gathering'
    if current_stage in stage_mapping:
        stage_data = stage_mapping[current_stage]
        stage_info.update({
            'progress_percentage': stage_data['progress'],
            'estimated_timeline': stage_data['timeline'],
            'stage_description': stage_data['description']
        })
        
        # Calculate estimated completion if not closed
        if stage_data['progress'] < 100:
            # Rough estimate based on typical legal timelines
            weeks_remaining = {
                'evidence_gathering': 12,
                'analysis_complete': 10,
                'document_preparation': 8,
                'filing_submitted': 6,
                'awaiting_response': 4,
                'discovery': 16,
                'mediation': 8,
                'pre_trial': 12,
                'trial_scheduled': 2
            }.get(current_stage, 8)
            
            stage_info['completion_date'] = datetime.now() + timedelta(weeks=weeks_remaining)
    
    return stage_info

def get_next_legal_actions(case: Case, ai_analysis) -> List[Dict[str, Any]]:
    """Determine next recommended actions based on case stage and analysis"""
    
    actions = []
    current_stage = case.status or 'evidence_gathering'
    case_type = case.case_type or 'general_legal'
    
    # Stage-specific action recommendations
    if current_stage == 'evidence_gathering':
        actions.extend([
            {
                'action': 'Upload Additional Evidence',
                'priority': 'high',
                'description': 'Add any missing documents, correspondence, or evidence',
                'deadline': 'ASAP'
            },
            {
                'action': 'Review AI Analysis',
                'priority': 'medium',
                'description': 'Verify AI-identified key facts and evidence strength',
                'deadline': '1 week'
            }
        ])
    
    elif current_stage == 'analysis_complete':
        # Handle ai_analysis safely - could be dict, int, or other type
        score = 0
        if isinstance(ai_analysis, dict):
            merit_score_data = ai_analysis.get('merit_score', {})
            if isinstance(merit_score_data, dict):
                score = merit_score_data.get('overall_score', 0)
            elif isinstance(merit_score_data, (int, float)):
                score = merit_score_data
        
        # Ensure score is numeric
        if not isinstance(score, (int, float)):
            score = 0
        
        if score >= 70:
            actions.append({
                'action': 'Proceed with Legal Action',
                'priority': 'high',
                'description': 'Strong case - begin document preparation immediately',
                'deadline': '2 weeks'
            })
        elif score >= 40:
            actions.append({
                'action': 'Consider Settlement Offer',
                'priority': 'medium',
                'description': 'Moderate case strength - explore settlement options',
                'deadline': '3 weeks'
            })
        else:
            actions.append({
                'action': 'Seek Legal Consultation',
                'priority': 'high',
                'description': 'Weak case - professional review recommended',
                'deadline': '1 week'
            })
    
    elif current_stage == 'document_preparation':
        recommended_docs = ai_analysis.get('recommended_documents', [])
        for doc in recommended_docs:
            actions.append({
                'action': f'Generate {doc.get("type", "Document")}',
                'priority': doc.get('priority', 'medium'),
                'description': doc.get('description', 'Legal document preparation'),
                'deadline': '1-2 weeks'
            })
    
    elif current_stage == 'filing_submitted':
        actions.extend([
            {
                'action': 'Monitor Filing Status',
                'priority': 'medium',
                'description': 'Check court/tribunal for acknowledgment and case number',
                'deadline': '1 week'
            },
            {
                'action': 'Prepare for Response',
                'priority': 'low',
                'description': 'Begin preparing response to expected counter-arguments',
                'deadline': '30 days'
            }
        ])
    
    elif current_stage == 'awaiting_response':
        actions.extend([
            {
                'action': 'Track Response Deadline',
                'priority': 'high',
                'description': 'Monitor opposing party response deadline',
                'deadline': 'Ongoing'
            },
            {
                'action': 'Prepare Reply Documents',
                'priority': 'medium',
                'description': 'Draft response to anticipated defence arguments',
                'deadline': '2 weeks after response'
            }
        ])
    
    # Case-type specific actions
    if case_type == 'landlord_tenant':
        if current_stage in ['evidence_gathering', 'analysis_complete']:
            actions.append({
                'action': 'Gather Rental History',
                'priority': 'high',
                'description': 'Collect all rent receipts, lease agreements, and notices',
                'deadline': '1 week'
            })
    
    elif case_type == 'employment':
        if current_stage in ['evidence_gathering', 'analysis_complete']:
            actions.append({
                'action': 'Document Employment Timeline',
                'priority': 'high',
                'description': 'Create detailed timeline of employment events',
                'deadline': '1 week'
            })
    
    elif case_type == 'family_law':
        if current_stage in ['evidence_gathering', 'analysis_complete']:
            actions.append({
                'action': 'Complete Financial Disclosure',
                'priority': 'high',
                'description': 'Prepare comprehensive financial statements',
                'deadline': '2 weeks'
            })
    
    # Sort actions by priority
    priority_order = {'high': 1, 'medium': 2, 'low': 3}
    actions.sort(key=lambda x: priority_order.get(x['priority'], 4))
    
    return actions[:6]  # Return top 6 actions

def get_case_timeline_milestones(case: Case) -> List[Dict[str, Any]]:
    """Generate expected timeline milestones for the case"""
    
    milestones = []
    case_type = case.case_type or 'general_legal'
    created_date = case.created_at or datetime.now()
    
    # Common milestones for most case types
    base_milestones = [
        {'name': 'Evidence Collection Complete', 'weeks_offset': 2},
        {'name': 'Documents Filed', 'weeks_offset': 4},
        {'name': 'Response Received', 'weeks_offset': 8},
        {'name': 'Discovery Complete', 'weeks_offset': 16},
        {'name': 'Trial/Hearing', 'weeks_offset': 24},
        {'name': 'Decision Rendered', 'weeks_offset': 28}
    ]
    
    # Case-type specific timeline adjustments
    if case_type == 'landlord_tenant':
        # LTB cases are typically faster
        base_milestones = [
            {'name': 'Application Filed', 'weeks_offset': 1},
            {'name': 'Hearing Scheduled', 'weeks_offset': 6},
            {'name': 'LTB Hearing', 'weeks_offset': 12},
            {'name': 'Order Issued', 'weeks_offset': 14}
        ]
    
    elif case_type == 'small_claims':
        # Small claims court timeline
        base_milestones = [
            {'name': 'Claim Filed', 'weeks_offset': 1},
            {'name': 'Defence Due', 'weeks_offset': 3},
            {'name': 'Settlement Conference', 'weeks_offset': 8},
            {'name': 'Trial Date', 'weeks_offset': 16},
            {'name': 'Judgment', 'weeks_offset': 18}
        ]
    
    elif case_type == 'family_law':
        # Family court proceedings
        base_milestones = [
            {'name': 'Application Filed', 'weeks_offset': 2},
            {'name': 'Financial Statements Due', 'weeks_offset': 6},
            {'name': 'Case Conference', 'weeks_offset': 12},
            {'name': 'Settlement Conference', 'weeks_offset': 20},
            {'name': 'Trial', 'weeks_offset': 32},
            {'name': 'Final Order', 'weeks_offset': 36}
        ]
    
    # Generate milestone dates
    for milestone in base_milestones:
        milestone_date = created_date + timedelta(weeks=milestone['weeks_offset'])
        milestones.append({
            'name': milestone['name'],
            'date': milestone_date,
            'status': 'upcoming' if milestone_date > datetime.now() else 'completed',
            'estimated': True
        })
    
    return milestones

def calculate_case_costs(case: Case, ai_analysis: Dict) -> Dict[str, Any]:
    """Calculate estimated costs for legal proceedings"""
    
    base_costs = {
        'filing_fees': 0,
        'service_costs': 0,
        'document_preparation': 0,
        'estimated_total': 0,
        'currency': 'CAD'
    }
    
    case_type = case.case_type or 'general_legal'
    jurisdiction = case.jurisdiction or 'ON'
    
    # Ontario court filing fees (2024 rates)
    if jurisdiction.upper() == 'ON':
        filing_fees = {
            'small_claims': 102,  # up to $25,000
            'superior_court': 225,  # general application
            'family_law': 224,  # family court application
            'landlord_tenant': 190,  # LTB application
            'human_rights': 0,  # HRTO - no fee
            'employment': 0  # ESC - no fee
        }
        
        base_costs['filing_fees'] = filing_fees.get(case_type, 200)
    
    # Service costs
    base_costs['service_costs'] = 50  # Process server or registered mail
    
    # Document preparation costs (our service)
    doc_count = len(ai_analysis.get('recommended_documents', []))
    base_costs['document_preparation'] = doc_count * 25  # $25 per document
    
    # Calculate total
    base_costs['estimated_total'] = (
        base_costs['filing_fees'] + 
        base_costs['service_costs'] + 
        base_costs['document_preparation']
    )
    
    return base_costs

def get_jurisdiction_specific_info(case: Case) -> Dict[str, Any]:
    """Get jurisdiction-specific legal information and requirements"""
    
    jurisdiction = case.jurisdiction or 'ON'
    case_type = case.case_type or 'general_legal'
    
    jurisdiction_info = {
        'court_name': '',
        'filing_location': '',
        'specific_requirements': [],
        'helpful_links': [],
        'time_limits': {}
    }
    
    if jurisdiction.upper() == 'ON':
        if case_type == 'landlord_tenant':
            jurisdiction_info.update({
                'court_name': 'Landlord and Tenant Board (LTB)',
                'filing_location': 'Online at tribunalsontario.ca',
                'specific_requirements': [
                    'Notice to End Tenancy required',
                    'Rent receipts and lease agreement',
                    'Photographs of property condition'
                ],
                'helpful_links': [
                    'https://tribunalsontario.ca/ltb/',
                    'https://www.ontario.ca/page/renting-ontario'
                ],
                'time_limits': {
                    'application_deadline': '1 year from incident',
                    'response_time': '7 days after service'
                }
            })
        
        elif case_type == 'small_claims':
            jurisdiction_info.update({
                'court_name': 'Small Claims Court',
                'filing_location': 'Local courthouse',
                'specific_requirements': [
                    'Claim limited to $35,000',
                    'Proof of damages required',
                    'Attempts at resolution documented'
                ],
                'helpful_links': [
                    'https://www.ontario.ca/page/suing-and-being-sued',
                    'https://www.attorneygeneral.jus.gov.on.ca/english/courts/scc/'
                ],
                'time_limits': {
                    'filing_deadline': '2 years from incident',
                    'defence_deadline': '20 days after service'
                }
            })
        
        elif case_type == 'family_law':
            jurisdiction_info.update({
                'court_name': 'Family Court',
                'filing_location': 'Family Court courthouse',
                'specific_requirements': [
                    'Financial Statement (Form 13 or 13.1)',
                    'Certificate of Financial Disclosure',
                    'Parenting plan if children involved'
                ],
                'helpful_links': [
                    'https://www.ontario.ca/page/family-court',
                    'https://www.attorneygeneral.jus.gov.on.ca/english/family/'
                ],
                'time_limits': {
                    'response_deadline': '30 days after service',
                    'financial_disclosure': '30 days after request'
                }
            })
    
    return jurisdiction_info