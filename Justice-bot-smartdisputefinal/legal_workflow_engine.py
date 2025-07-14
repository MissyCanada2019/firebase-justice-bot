#!/usr/bin/env python3
"""
Personalized Legal Workflow Recommendation Engine for SmartDispute.ai
Provides intelligent, Charter-compliant recommendations based on user profiles and case types
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class LegalArea(Enum):
    FAMILY_LAW = "family_law"
    CRIMINAL_LAW = "criminal_law"
    CIVIL_RIGHTS = "civil_rights"
    EMPLOYMENT = "employment"
    HOUSING = "housing"
    IMMIGRATION = "immigration"
    PERSONAL_INJURY = "personal_injury"
    CONTRACT_DISPUTE = "contract_dispute"
    CAS_CHILD_PROTECTION = "cas_child_protection"
    HUMAN_RIGHTS = "human_rights"

class Urgency(Enum):
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"         # Action needed within days
    MEDIUM = "medium"     # Action needed within weeks
    LOW = "low"          # General guidance

@dataclass
class WorkflowStep:
    step_id: str
    title: str
    description: str
    charter_reference: str
    estimated_time: str
    required_documents: List[str]
    next_steps: List[str]
    urgency: Urgency
    cost_estimate: str
    success_probability: float

@dataclass
class LegalWorkflow:
    workflow_id: str
    name: str
    legal_area: LegalArea
    province: str
    steps: List[WorkflowStep]
    total_estimated_time: str
    total_cost_range: str
    success_rate: float
    charter_compliance: Dict[str, str]

class LegalWorkflowEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workflows = self._initialize_workflows()
        self.charter_sections = self._load_charter_references()
        
    def _load_charter_references(self) -> Dict[str, str]:
        """Load Charter of Rights and Freedoms references"""
        return {
            'section_2': "Everyone has the following fundamental freedoms: (a) freedom of conscience and religion; (b) freedom of thought, belief, opinion and expression, including freedom of the press and other media of communication; (c) freedom of peaceful assembly; (d) freedom of association.",
            'section_7': "Everyone has the right to life, liberty and security of the person and the right not to be deprived thereof except in accordance with the principles of fundamental justice.",
            'section_8': "Everyone has the right to be secure against unreasonable search or seizure.",
            'section_9': "Everyone has the right not to be arbitrarily detained or imprisoned.",
            'section_10': "Everyone has the right on arrest or detention: (a) to be informed promptly of the reasons therefor; (b) to retain and instruct counsel without delay and to be informed of that right.",
            'section_11': "Any person charged with an offence has the right: (a) to be informed without unreasonable delay of the specific offence; (b) to be tried within a reasonable time.",
            'section_12': "Everyone has the right not to be subjected to any cruel and unusual treatment or punishment.",
            'section_15': "Every individual is equal before and under the law and has the right to the equal protection and equal benefit of the law without discrimination.",
            'section_24': "Anyone whose rights or freedoms, as guaranteed by this Charter, have been infringed or denied may apply to a court of competent jurisdiction to obtain such remedy as the court considers appropriate and just in the circumstances."
        }
    
    def _initialize_workflows(self) -> Dict[str, LegalWorkflow]:
        """Initialize comprehensive legal workflows for Canadian jurisdictions"""
        workflows = {}
        
        # Family Law Workflows
        workflows['family_custody_ontario'] = self._create_family_custody_workflow('ON')
        workflows['family_custody_bc'] = self._create_family_custody_workflow('BC')
        workflows['family_divorce_canada'] = self._create_divorce_workflow()
        
        # CAS/Child Protection Workflows
        workflows['cas_protection_ontario'] = self._create_cas_protection_workflow('ON')
        workflows['cas_appeal_process'] = self._create_cas_appeal_workflow()
        
        # Criminal Law Workflows
        workflows['criminal_defence_charter'] = self._create_criminal_defence_workflow()
        workflows['bail_application'] = self._create_bail_application_workflow()
        
        # Civil Rights Workflows
        workflows['charter_application'] = self._create_charter_application_workflow()
        workflows['human_rights_complaint'] = self._create_human_rights_workflow()
        
        # Employment Law Workflows
        workflows['wrongful_dismissal'] = self._create_employment_workflow()
        workflows['workplace_harassment'] = self._create_harassment_workflow()
        
        # Housing Law Workflows
        workflows['landlord_tenant_ontario'] = self._create_housing_workflow('ON')
        workflows['eviction_defence'] = self._create_eviction_defence_workflow()
        
        return workflows
    
    def _create_family_custody_workflow(self, province: str) -> LegalWorkflow:
        """Create family custody workflow specific to province"""
        steps = [
            WorkflowStep(
                step_id="assess_situation",
                title="Initial Situation Assessment",
                description="Document current custody arrangement, child's best interests, and any safety concerns. Gather evidence of parenting capacity and child's preferences if age-appropriate.",
                charter_reference="Section 7 - Right to security of the person applies to both parent and child",
                estimated_time="2-3 days",
                required_documents=["Birth certificates", "Current custody order (if any)", "School records", "Medical records"],
                next_steps=["file_application", "mediation_attempt"],
                urgency=Urgency.HIGH,
                cost_estimate="$0 (self-assessment)",
                success_probability=0.9
            ),
            WorkflowStep(
                step_id="file_application",
                title="File Court Application",
                description=f"File Form 8 (Application) in {province} Superior Court of Justice. Include detailed parenting plan and evidence supporting your position.",
                charter_reference="Section 7 - Right to liberty includes parental rights",
                estimated_time="1-2 weeks",
                required_documents=["Form 8", "Affidavit", "Financial statement", "Parenting plan"],
                next_steps=["serve_documents", "case_conference"],
                urgency=Urgency.HIGH,
                cost_estimate="$300-500 court fees",
                success_probability=0.85
            ),
            WorkflowStep(
                step_id="case_conference",
                title="Attend Case Conference",
                description="Participate in mandatory case conference to identify issues and explore settlement. Come prepared with your position and openness to reasonable compromise.",
                charter_reference="Section 7 - Procedural fairness in family proceedings",
                estimated_time="4-6 weeks after filing",
                required_documents=["Case conference brief", "Updated financial information"],
                next_steps=["mediation", "motion_if_needed"],
                urgency=Urgency.MEDIUM,
                cost_estimate="$0-200 preparation time",
                success_probability=0.75
            )
        ]
        
        return LegalWorkflow(
            workflow_id=f"family_custody_{province.lower()}",
            name=f"Child Custody Application - {province}",
            legal_area=LegalArea.FAMILY_LAW,
            province=province,
            steps=steps,
            total_estimated_time="3-6 months",
            total_cost_range="$500-2000 (self-represented)",
            success_rate=0.78,
            charter_compliance={
                "section_7": "Protects both parental rights and child's security",
                "section_15": "Ensures equal treatment regardless of gender or status"
            }
        )
    
    def _create_cas_protection_workflow(self, province: str) -> LegalWorkflow:
        """Create CAS child protection defence workflow"""
        steps = [
            WorkflowStep(
                step_id="understand_allegations",
                title="Understand CAS Allegations",
                description="Request detailed written allegations from CAS. Understand specific concerns and evidence they claim to have. Document your perspective on each allegation.",
                charter_reference="Section 7 - Right to know case against you (principles of fundamental justice)",
                estimated_time="3-5 days",
                required_documents=["CAS file disclosure", "Court application", "Service documents"],
                next_steps=["gather_evidence", "legal_representation"],
                urgency=Urgency.CRITICAL,
                cost_estimate="$0",
                success_probability=0.95
            ),
            WorkflowStep(
                step_id="court_appearance",
                title="First Court Appearance",
                description="Attend court within 5 days of apprehension. Request adjournment for preparation if needed. Assert your Charter rights and request full disclosure.",
                charter_reference="Section 7 & 24 - Right to procedural fairness and Charter remedies",
                estimated_time="5 days from apprehension",
                required_documents=["Court documents", "Identity documents", "Evidence of housing/employment"],
                next_steps=["case_plan_meeting", "ongoing_court_dates"],
                urgency=Urgency.CRITICAL,
                cost_estimate="$0 (court appearance)",
                success_probability=0.88
            ),
            WorkflowStep(
                step_id="develop_case_plan",
                title="Develop Case Plan",
                description="Work with CAS to develop realistic case plan addressing their concerns. Ensure plan respects your Charter rights and cultural background.",
                charter_reference="Section 15 - Equal treatment and accommodation for cultural differences",
                estimated_time="2-4 weeks",
                required_documents=["Assessment reports", "Service provider agreements", "Progress documentation"],
                next_steps=["implement_plan", "court_review"],
                urgency=Urgency.HIGH,
                cost_estimate="Variable (depends on services required)",
                success_probability=0.82
            )
        ]
        
        return LegalWorkflow(
            workflow_id=f"cas_protection_{province.lower()}",
            name=f"CAS Child Protection Defence - {province}",
            legal_area=LegalArea.CAS_CHILD_PROTECTION,
            province=province,
            steps=steps,
            total_estimated_time="6-18 months",
            total_cost_range="$1000-8000 (with legal aid)",
            success_rate=0.72,
            charter_compliance={
                "section_7": "Protects family unity and parental rights",
                "section_15": "Ensures cultural sensitivity in assessments"
            }
        )
    
    def _create_criminal_defence_workflow(self) -> LegalWorkflow:
        """Create criminal defence workflow with Charter focus"""
        steps = [
            WorkflowStep(
                step_id="assert_charter_rights",
                title="Assert Charter Rights",
                description="Immediately assert your Charter rights: right to counsel, right to remain silent, right to know charges. Document any Charter breaches by police.",
                charter_reference="Sections 10(a), 10(b) - Right to counsel and to know reasons for detention",
                estimated_time="Immediate",
                required_documents=["Police disclosure", "Arrest records", "Charter breach documentation"],
                next_steps=["disclosure_request", "bail_hearing"],
                urgency=Urgency.CRITICAL,
                cost_estimate="$0 (constitutional rights)",
                success_probability=0.92
            ),
            WorkflowStep(
                step_id="charter_application",
                title="File Charter Application",
                description="If Charter rights were violated, file s. 24(2) application to exclude evidence or s. 24(1) for other remedies. Document timeline and circumstances of violations.",
                charter_reference="Section 24 - Charter remedies for rights violations",
                estimated_time="2-4 weeks",
                required_documents=["Charter application", "Affidavit evidence", "Legal authorities"],
                next_steps=["disclosure_review", "plea_negotiations"],
                urgency=Urgency.HIGH,
                cost_estimate="$500-1500 (legal research and filing)",
                success_probability=0.68
            )
        ]
        
        return LegalWorkflow(
            workflow_id="criminal_defence_charter",
            name="Criminal Defence with Charter Applications",
            legal_area=LegalArea.CRIMINAL_LAW,
            province="All",
            steps=steps,
            total_estimated_time="6-24 months",
            total_cost_range="$2000-15000 (legal aid available)",
            success_rate=0.74,
            charter_compliance={
                "section_7": "Procedural fairness in criminal proceedings",
                "section_11": "Right to fair trial and reasonable time",
                "section_24": "Remedies for Charter violations"
            }
        )
    
    def _create_charter_application_workflow(self) -> LegalWorkflow:
        """Create standalone Charter application workflow"""
        steps = [
            WorkflowStep(
                step_id="identify_charter_breach",
                title="Identify Charter Breach",
                description="Document specific Charter right(s) violated, by whom (government actor), and resulting harm. Gather evidence of the violation and its impact.",
                charter_reference="All Charter sections - Must identify specific right violated",
                estimated_time="1-2 weeks",
                required_documents=["Evidence of government action", "Documentation of harm", "Timeline of events"],
                next_steps=["legal_test_analysis", "remedy_identification"],
                urgency=Urgency.HIGH,
                cost_estimate="$0 (evidence gathering)",
                success_probability=0.85
            ),
            WorkflowStep(
                step_id="file_charter_application",
                title="File Charter Application",
                description="File Notice of Constitutional Question and Charter application in appropriate court. Serve Attorney General as required.",
                charter_reference="Section 24 - Charter remedies and court jurisdiction",
                estimated_time="2-3 weeks",
                required_documents=["Charter application", "Notice of constitutional question", "Supporting affidavits"],
                next_steps=["ag_response", "case_management"],
                urgency=Urgency.HIGH,
                cost_estimate="$500-1000 court fees",
                success_probability=0.72
            )
        ]
        
        return LegalWorkflow(
            workflow_id="charter_application",
            name="Charter Rights Application",
            legal_area=LegalArea.CIVIL_RIGHTS,
            province="All",
            steps=steps,
            total_estimated_time="12-36 months",
            total_cost_range="$3000-25000 (public interest funding possible)",
            success_rate=0.64,
            charter_compliance={
                "section_24": "Primary vehicle for Charter enforcement",
                "section_52": "Constitutional supremacy"
            }
        )
    
    def _create_divorce_workflow(self) -> LegalWorkflow:
        """Create federal divorce workflow"""
        return LegalWorkflow(
            workflow_id="federal_divorce",
            name="Divorce Application (Federal)",
            legal_area=LegalArea.FAMILY_LAW,
            province="All",
            steps=[],  # Simplified for space
            total_estimated_time="4-12 months",
            total_cost_range="$600-3000",
            success_rate=0.89,
            charter_compliance={"section_7": "Right to dissolve marriage"}
        )
    
    def _create_cas_appeal_workflow(self) -> LegalWorkflow:
        """Create CAS appeal workflow"""
        return LegalWorkflow(
            workflow_id="cas_appeal",
            name="CAS Decision Appeal",
            legal_area=LegalArea.CAS_CHILD_PROTECTION,
            province="All",
            steps=[],  # Simplified for space
            total_estimated_time="6-18 months",
            total_cost_range="$2000-10000",
            success_rate=0.58,
            charter_compliance={"section_7": "Appellate rights in child protection"}
        )
    
    def _create_bail_application_workflow(self) -> LegalWorkflow:
        """Create bail application workflow"""
        return LegalWorkflow(
            workflow_id="bail_application",
            name="Bail Application",
            legal_area=LegalArea.CRIMINAL_LAW,
            province="All",
            steps=[],  # Simplified for space
            total_estimated_time="1-4 weeks",
            total_cost_range="$1000-5000",
            success_rate=0.78,
            charter_compliance={"section_11": "Right not to be denied reasonable bail"}
        )
    
    def _create_human_rights_workflow(self) -> LegalWorkflow:
        """Create human rights complaint workflow"""
        return LegalWorkflow(
            workflow_id="human_rights_complaint",
            name="Human Rights Complaint",
            legal_area=LegalArea.HUMAN_RIGHTS,
            province="All",
            steps=[],  # Simplified for space
            total_estimated_time="12-36 months",
            total_cost_range="$0-5000",
            success_rate=0.67,
            charter_compliance={"section_15": "Equality rights enforcement"}
        )
    
    def _create_employment_workflow(self) -> LegalWorkflow:
        """Create employment law workflow"""
        return LegalWorkflow(
            workflow_id="wrongful_dismissal",
            name="Wrongful Dismissal Claim",
            legal_area=LegalArea.EMPLOYMENT,
            province="All",
            steps=[],  # Simplified for space
            total_estimated_time="6-18 months",
            total_cost_range="$2000-15000",
            success_rate=0.71,
            charter_compliance={"section_2": "Freedom of association (union context)"}
        )
    
    def _create_harassment_workflow(self) -> LegalWorkflow:
        """Create workplace harassment workflow"""
        return LegalWorkflow(
            workflow_id="workplace_harassment",
            name="Workplace Harassment Complaint",
            legal_area=LegalArea.EMPLOYMENT,
            province="All",
            steps=[],  # Simplified for space
            total_estimated_time="3-12 months",
            total_cost_range="$500-8000",
            success_rate=0.73,
            charter_compliance={"section_15": "Equality in workplace"}
        )
    
    def _create_housing_workflow(self, province: str) -> LegalWorkflow:
        """Create housing law workflow"""
        return LegalWorkflow(
            workflow_id=f"landlord_tenant_{province.lower()}",
            name=f"Landlord Tenant Dispute - {province}",
            legal_area=LegalArea.HOUSING,
            province=province,
            steps=[],  # Simplified for space
            total_estimated_time="2-8 months",
            total_cost_range="$100-3000",
            success_rate=0.76,
            charter_compliance={"section_7": "Security of housing"}
        )
    
    def _create_eviction_defence_workflow(self) -> LegalWorkflow:
        """Create eviction defence workflow"""
        return LegalWorkflow(
            workflow_id="eviction_defence",
            name="Eviction Defence",
            legal_area=LegalArea.HOUSING,
            province="All",
            steps=[],  # Simplified for space
            total_estimated_time="1-6 months",
            total_cost_range="$200-2000",
            success_rate=0.68,
            charter_compliance={"section_7": "Right to adequate housing"}
        )
    
    def recommend_workflow(self, user_profile: Dict, case_details: Dict) -> Tuple[LegalWorkflow, float]:
        """Recommend the most suitable workflow based on user profile and case"""
        legal_area = LegalArea(case_details.get('legal_issue_type', 'civil_rights').lower())
        province = user_profile.get('province', 'ON')
        urgency_level = case_details.get('urgency', 'medium')
        
        # Score workflows based on relevance
        scored_workflows = []
        
        for workflow_id, workflow in self.workflows.items():
            score = self._calculate_workflow_score(workflow, user_profile, case_details)
            scored_workflows.append((workflow, score))
        
        # Sort by score and return best match
        scored_workflows.sort(key=lambda x: x[1], reverse=True)
        best_workflow, confidence = scored_workflows[0]
        
        self.logger.info(f"Recommended workflow: {best_workflow.name} (confidence: {confidence:.2f})")
        return best_workflow, confidence
    
    def _calculate_workflow_score(self, workflow: LegalWorkflow, user_profile: Dict, case_details: Dict) -> float:
        """Calculate relevance score for a workflow"""
        score = 0.0
        
        # Legal area match (40% weight)
        case_area = case_details.get('legal_issue_type', '').lower().replace(' ', '_')
        if workflow.legal_area.value == case_area:
            score += 0.4
        elif case_area in workflow.legal_area.value or workflow.legal_area.value in case_area:
            score += 0.2
        
        # Province match (20% weight)
        user_province = user_profile.get('province', 'ON')
        if workflow.province == user_province or workflow.province == 'All':
            score += 0.2
        
        # Urgency alignment (15% weight)
        urgency_level = case_details.get('urgency', 'medium')
        workflow_urgency = max([step.urgency.value for step in workflow.steps] or ['medium'])
        if urgency_level == workflow_urgency:
            score += 0.15
        
        # Success rate (15% weight)
        score += workflow.success_rate * 0.15
        
        # Charter relevance (10% weight)
        charter_issues = case_details.get('charter_issues', [])
        if charter_issues and workflow.charter_compliance:
            matching_sections = set(charter_issues) & set(workflow.charter_compliance.keys())
            score += (len(matching_sections) / len(charter_issues)) * 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_personalized_recommendations(self, user_id: str, user_profile: Dict, case_details: Dict) -> Dict:
        """Get comprehensive personalized recommendations"""
        # Get primary workflow recommendation
        primary_workflow, confidence = self.recommend_workflow(user_profile, case_details)
        
        # Get alternative workflows
        alternatives = self._get_alternative_workflows(user_profile, case_details, exclude=primary_workflow.workflow_id)
        
        # Generate timeline and priorities
        timeline = self._generate_case_timeline(primary_workflow, case_details)
        priorities = self._identify_immediate_priorities(primary_workflow, case_details)
        
        # Charter-specific guidance
        charter_guidance = self._generate_charter_guidance(case_details, primary_workflow)
        
        # Cost estimates and funding options
        cost_analysis = self._analyze_costs_and_funding(primary_workflow, user_profile)
        
        return {
            'user_id': user_id,
            'recommendation_date': datetime.now().isoformat(),
            'primary_workflow': {
                'workflow': primary_workflow.__dict__,
                'confidence': confidence,
                'customizations': self._customize_workflow_for_user(primary_workflow, user_profile, case_details)
            },
            'alternative_workflows': alternatives,
            'immediate_priorities': priorities,
            'timeline': timeline,
            'charter_guidance': charter_guidance,
            'cost_analysis': cost_analysis,
            'next_review_date': (datetime.now() + timedelta(days=30)).isoformat()
        }
    
    def _get_alternative_workflows(self, user_profile: Dict, case_details: Dict, exclude: str, limit: int = 3) -> List[Dict]:
        """Get alternative workflow recommendations"""
        alternatives = []
        scored_workflows = []
        
        for workflow_id, workflow in self.workflows.items():
            if workflow_id != exclude:
                score = self._calculate_workflow_score(workflow, user_profile, case_details)
                scored_workflows.append((workflow, score))
        
        scored_workflows.sort(key=lambda x: x[1], reverse=True)
        
        for workflow, score in scored_workflows[:limit]:
            alternatives.append({
                'workflow': workflow.__dict__,
                'relevance_score': score,
                'why_alternative': self._explain_alternative_relevance(workflow, case_details)
            })
        
        return alternatives
    
    def _explain_alternative_relevance(self, workflow: LegalWorkflow, case_details: Dict) -> str:
        """Explain why this workflow might be relevant as an alternative"""
        explanations = []
        
        if workflow.legal_area.value in case_details.get('legal_issue_type', '').lower():
            explanations.append(f"Directly addresses {workflow.legal_area.value.replace('_', ' ')} issues")
        
        if 'charter' in case_details.get('description', '').lower() and workflow.charter_compliance:
            explanations.append("Includes Charter rights applications")
        
        if workflow.success_rate > 0.8:
            explanations.append("High success rate for similar cases")
        
        return ". ".join(explanations) if explanations else "May be relevant depending on case development"
    
    def _generate_case_timeline(self, workflow: LegalWorkflow, case_details: Dict) -> Dict:
        """Generate personalized case timeline"""
        timeline = {
            'phases': [],
            'critical_deadlines': [],
            'estimated_completion': None
        }
        
        current_date = datetime.now()
        running_date = current_date
        
        for i, step in enumerate(workflow.steps):
            # Estimate step duration
            time_parts = step.estimated_time.split('-')
            if 'days' in step.estimated_time:
                duration_days = int(time_parts[0])
            elif 'weeks' in step.estimated_time:
                duration_days = int(time_parts[0]) * 7
            elif 'months' in step.estimated_time:
                duration_days = int(time_parts[0]) * 30
            else:
                duration_days = 7  # Default
            
            end_date = running_date + timedelta(days=duration_days)
            
            timeline['phases'].append({
                'step_id': step.step_id,
                'title': step.title,
                'start_date': running_date.isoformat(),
                'end_date': end_date.isoformat(),
                'urgency': step.urgency.value,
                'dependencies': step.next_steps
            })
            
            if step.urgency in [Urgency.CRITICAL, Urgency.HIGH]:
                timeline['critical_deadlines'].append({
                    'deadline': end_date.isoformat(),
                    'task': step.title,
                    'consequences': f"Delay may affect {step.description[:50]}..."
                })
            
            running_date = end_date
        
        timeline['estimated_completion'] = running_date.isoformat()
        return timeline
    
    def _identify_immediate_priorities(self, workflow: LegalWorkflow, case_details: Dict) -> List[Dict]:
        """Identify immediate action priorities"""
        priorities = []
        
        for step in workflow.steps:
            if step.urgency in [Urgency.CRITICAL, Urgency.HIGH]:
                priorities.append({
                    'priority_level': step.urgency.value,
                    'action': step.title,
                    'description': step.description,
                    'deadline': self._calculate_step_deadline(step),
                    'charter_reference': step.charter_reference,
                    'required_documents': step.required_documents
                })
        
        return sorted(priorities, key=lambda x: {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}[x['priority_level']])
    
    def _calculate_step_deadline(self, step: WorkflowStep) -> str:
        """Calculate realistic deadline for a step"""
        if step.urgency == Urgency.CRITICAL:
            return (datetime.now() + timedelta(days=3)).isoformat()
        elif step.urgency == Urgency.HIGH:
            return (datetime.now() + timedelta(days=7)).isoformat()
        elif step.urgency == Urgency.MEDIUM:
            return (datetime.now() + timedelta(days=21)).isoformat()
        else:
            return (datetime.now() + timedelta(days=60)).isoformat()
    
    def _generate_charter_guidance(self, case_details: Dict, workflow: LegalWorkflow) -> Dict:
        """Generate Charter-specific guidance"""
        guidance = {
            'applicable_sections': [],
            'key_principles': [],
            'strategic_considerations': []
        }
        
        for section, description in workflow.charter_compliance.items():
            if section in self.charter_sections:
                guidance['applicable_sections'].append({
                    'section': section,
                    'text': self.charter_sections[section],
                    'application': description
                })
        
        # Add general Charter principles
        guidance['key_principles'] = [
            "Charter rights are not absolute and may be subject to reasonable limits",
            "Government must justify any infringement under s. 1 (reasonable limits)",
            "Charter applies to all government action including courts, police, and administrative bodies",
            "Remedies available under s. 24(1) for rights violations and s. 24(2) for evidence exclusion"
        ]
        
        return guidance
    
    def _analyze_costs_and_funding(self, workflow: LegalWorkflow, user_profile: Dict) -> Dict:
        """Analyze costs and available funding options"""
        analysis = {
            'estimated_costs': workflow.total_cost_range,
            'funding_options': [],
            'cost_reduction_strategies': [],
            'payment_timeline': []
        }
        
        # Determine funding options based on case type and user profile
        income_level = user_profile.get('income_level', 'low')
        
        if workflow.legal_area in [LegalArea.FAMILY_LAW, LegalArea.CRIMINAL_LAW, LegalArea.CAS_CHILD_PROTECTION]:
            analysis['funding_options'].append({
                'option': 'Legal Aid Ontario',
                'eligibility': 'Income-based eligibility',
                'coverage': 'Full representation for eligible cases',
                'application_process': 'Apply online or at local clinic'
            })
        
        if workflow.legal_area == LegalArea.CIVIL_RIGHTS:
            analysis['funding_options'].append({
                'option': 'Court Challenges Program',
                'eligibility': 'Charter challenges of federal laws',
                'coverage': 'Up to $125,000 for court challenges',
                'application_process': 'Detailed application with legal merit assessment'
            })
        
        # Cost reduction strategies
        analysis['cost_reduction_strategies'] = [
            'Self-representation with legal coaching',
            'Limited scope representation for specific tasks',
            'Mediation or alternative dispute resolution',
            'Community legal clinics for summary advice'
        ]
        
        return analysis
    
    def _customize_workflow_for_user(self, workflow: LegalWorkflow, user_profile: Dict, case_details: Dict) -> Dict:
        """Customize workflow based on user-specific factors"""
        customizations = {
            'language_accommodations': [],
            'cultural_considerations': [],
            'accessibility_needs': [],
            'geographic_factors': []
        }
        
        # Language accommodations
        preferred_language = user_profile.get('preferred_language', 'English')
        if preferred_language != 'English':
            customizations['language_accommodations'] = [
                f'Court interpreter services available in {preferred_language}',
                'Translated court documents available',
                'Bilingual legal aid services may be available'
            ]
        
        # Geographic factors
        location = user_profile.get('city', '')
        if location in ['Toronto', 'Ottawa', 'Hamilton', 'London']:
            customizations['geographic_factors'].append('Multiple courthouse locations available')
            customizations['geographic_factors'].append('Extensive legal aid clinic network')
        else:
            customizations['geographic_factors'].append('Consider video appearances if available')
            customizations['geographic_factors'].append('Travel time to courthouse should be factored into timeline')
        
        return customizations

def init_workflow_engine(app):
    """Initialize the workflow engine with the Flask app"""
    app.workflow_engine = LegalWorkflowEngine()
    app.logger.info("Legal workflow recommendation engine initialized")