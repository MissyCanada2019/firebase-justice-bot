"""
Canadian Legal Engine for SmartDispute.ai
Comprehensive AI system that pulls all relevant Canadian laws, uses customer registration data
for jurisdiction-specific requirements, and generates pre-filled court forms.
"""

import os
import logging
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from models import User, Case, Document, LegalReference, db
from sqlalchemy import text
from fathers_rights_legal_framework import enhance_fathers_rights_analysis

class CanadianLegalEngine:
    """
    Comprehensive legal engine that integrates federal, provincial, and municipal Canadian law
    """
    
    def __init__(self):
        self.federal_sources = self._initialize_federal_sources()
        self.provincial_sources = self._initialize_provincial_sources()
        self.municipal_sources = self._initialize_municipal_sources()
        self.court_forms = self._initialize_court_forms()
        
    def _initialize_federal_sources(self) -> Dict[str, Any]:
        """Initialize federal law sources"""
        return {
            'criminal_code': {
                'url': 'https://laws-lois.justice.gc.ca/eng/acts/C-46/',
                'api_endpoint': 'https://api.justice.gc.ca/criminal-code',
                'sections': list(range(1, 750)),  # Criminal Code sections
                'last_updated': None
            },
            'charter_rights': {
                'url': 'https://laws-lois.justice.gc.ca/eng/const/page-12.html',
                'sections': {
                    'fundamental_freedoms': [2],
                    'democratic_rights': [3, 4, 5],
                    'mobility_rights': [6],
                    'legal_rights': [7, 8, 9, 10, 11, 12, 13, 14],
                    'equality_rights': [15],
                    'language_rights': [16, 17, 18, 19, 20],
                    'enforcement': [24]
                }
            },
            'family_law': {
                'divorce_act': {
                    'url': 'https://laws-lois.justice.gc.ca/eng/acts/D-3.4/',
                    'sections': {
                        'divorce_grounds': [8, 9],
                        'child_custody': [16, 17, 18, 19],
                        'child_support': [15.1, 15.2, 15.3],
                        'spousal_support': [15.2],
                        'best_interests': [16]
                    }
                },
                'child_support_guidelines': {
                    'url': 'https://laws-lois.justice.gc.ca/eng/regulations/SOR-97-175/',
                    'federal_guidelines': True,
                    'income_calculation': [15, 16, 17, 18, 19, 20],
                    'special_expenses': [7]
                }
            },
            'child_protection_federal': {
                'youth_criminal_justice_act': {
                    'url': 'https://laws-lois.justice.gc.ca/eng/acts/Y-1.5/',
                    'sections': {
                        'principles': [3, 4, 5],
                        'rights': [25, 26, 27, 28, 29, 30],
                        'custody': [30, 31]
                    }
                },
                'charter_child_rights': {
                    'section_7': 'Life, liberty and security of the person',
                    'section_15': 'Equality rights for children',
                    'section_24': 'Enforcement of guaranteed rights and freedoms'
                }
            },
            'human_rights_act': {
                'url': 'https://laws-lois.justice.gc.ca/eng/acts/H-6/',
                'protected_grounds': [
                    'race', 'national_ethnic_origin', 'colour', 'religion',
                    'age', 'sex', 'sexual_orientation', 'gender_identity',
                    'marital_status', 'family_status', 'genetic_characteristics',
                    'disability', 'conviction'
                ]
            },
            'divorce_act': {
                'url': 'https://laws-lois.justice.gc.ca/eng/acts/D-3.4/',
                'key_sections': {
                    'grounds_for_divorce': [8],
                    'child_support': [15.1, 15.2, 15.3],
                    'spousal_support': [15.2],
                    'custody_access': [16, 16.1, 16.2]
                }
            },
            'employment_standards': {
                'url': 'https://laws-lois.justice.gc.ca/eng/acts/L-2/',
                'federal_employees_only': True,
                'key_areas': ['hours_of_work', 'overtime', 'vacation', 'termination']
            }
        }
    
    def _initialize_provincial_sources(self) -> Dict[str, Dict]:
        """Initialize provincial law sources for all provinces and territories"""
        return {
            'ON': {
                'name': 'Ontario',
                'sources': {
                    'residential_tenancies_act': {
                        'url': 'https://www.ontario.ca/laws/statute/06r17',
                        'tribunal': 'LTB',
                        'key_sections': {
                            'rent_increases': [120, 121, 122],
                            'eviction': [59, 60, 61, 62],
                            'maintenance': [20, 21, 22],
                            'harassment': [22, 23]
                        }
                    },
                    'employment_standards_act': {
                        'url': 'https://www.ontario.ca/laws/statute/00e41',
                        'tribunal': 'ESC',
                        'key_sections': {
                            'termination': [54, 55, 56, 57, 58],
                            'severance': [63, 64, 65],
                            'overtime': [17, 18, 19],
                            'vacation': [33, 34, 35]
                        }
                    },
                    'family_law_act': {
                        'url': 'https://www.ontario.ca/laws/statute/90f3',
                        'court': 'Family Court',
                        'key_sections': {
                            'property_division': [4, 5, 6],
                            'support_obligations': [30, 31, 32, 33],
                            'custody': [20, 21, 22, 23, 24]
                        }
                    },
                    'child_family_services_act': {
                        'url': 'https://www.ontario.ca/laws/statute/17c14',
                        'tribunal': 'Ontario Court of Justice',
                        'cas_agencies': {
                            'toronto': 'Children\'s Aid Society of Toronto',
                            'ottawa': 'Children\'s Aid Society of Ottawa',
                            'peel': 'Peel Children\'s Aid Society',
                            'york': 'York Region Children\'s Aid Society'
                        },
                        'key_sections': {
                            'child_protection': [74, 75, 76, 77, 78, 79, 80],
                            'removal_powers': [81, 82, 83, 84],
                            'court_orders': [101, 102, 103, 104, 105],
                            'custody_orders': [116, 117, 118, 119],
                            'access_rights': [141, 142, 143, 144],
                            'appeal_rights': [162, 163, 164],
                            'complaint_process': [93, 94, 95],
                            'best_interests': [74],
                            'parental_rights': [1, 2, 3]
                        },
                        'charter_protections': {
                            'section_7': 'Liberty and security for families',
                            'section_15': 'Equality rights in CAS proceedings',
                            'section_24': 'Charter remedy applications'
                        }
                    },
                    'family_law_act': {
                        'url': 'https://www.ontario.ca/laws/statute/90f3',
                        'court': 'Family Court',
                        'key_sections': {
                            'property_division': [4, 5, 6],
                            'support_obligations': [30, 31, 32, 33],
                            'custody_access': [20, 21, 22, 23, 24],
                            'best_interests_factors': [24],
                            'domestic_violence': [46],
                            'restraining_orders': [46, 47]
                        }
                    },
                    'children_law_reform_act': {
                        'url': 'https://www.ontario.ca/laws/statute/90c12',
                        'court': 'Family Court',
                        'key_sections': {
                            'custody_jurisdiction': [22, 23, 24],
                            'best_interests_test': [24],
                            'access_rights': [20, 21],
                            'guardianship': [47, 48, 49]
                        }
                    },
                    'human_rights_code': {
                        'url': 'https://www.ontario.ca/laws/statute/90h19',
                        'tribunal': 'HRTO',
                        'protected_grounds': [
                            'race', 'ancestry', 'place_of_origin', 'colour',
                            'ethnic_origin', 'citizenship', 'creed', 'sex',
                            'sexual_orientation', 'gender_identity', 'age',
                            'marital_status', 'family_status', 'disability'
                        ]
                    },
                    'small_claims_court': {
                        'monetary_limit': 35000,
                        'court': 'Small Claims Court',
                        'rules': 'Ontario Regulation 258/98'
                    }
                }
            },
            'BC': {
                'name': 'British Columbia',
                'sources': {
                    'residential_tenancy_act': {
                        'url': 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/02078_01',
                        'tribunal': 'RTB'
                    },
                    'employment_standards_act': {
                        'url': 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96113_01',
                        'tribunal': 'Employment Standards Tribunal'
                    },
                    'family_law_act': {
                        'url': 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/11025_01',
                        'court': 'Provincial Court (Family Division)'
                    },
                    'human_rights_code': {
                        'url': 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96210_01',
                        'tribunal': 'BC Human Rights Tribunal'
                    }
                }
            },
            'AB': {
                'name': 'Alberta',
                'sources': {
                    'residential_tenancies_act': {
                        'url': 'https://www.qp.alberta.ca/documents/Acts/r17p1.pdf',
                        'tribunal': 'RTDRS'
                    },
                    'employment_standards_code': {
                        'url': 'https://www.qp.alberta.ca/documents/Acts/e09.pdf'
                    },
                    'family_law_act': {
                        'url': 'https://www.qp.alberta.ca/documents/Acts/f04p5.pdf'
                    }
                }
            },
            # Add other provinces...
            'QC': {'name': 'Quebec', 'sources': {}},
            'NS': {'name': 'Nova Scotia', 'sources': {}},
            'NB': {'name': 'New Brunswick', 'sources': {}},
            'MB': {'name': 'Manitoba', 'sources': {}},
            'SK': {'name': 'Saskatchewan', 'sources': {}},
            'PE': {'name': 'Prince Edward Island', 'sources': {}},
            'NL': {'name': 'Newfoundland and Labrador', 'sources': {}},
            'NT': {'name': 'Northwest Territories', 'sources': {}},
            'NU': {'name': 'Nunavut', 'sources': {}},
            'YT': {'name': 'Yukon', 'sources': {}}
        }
    
    def _initialize_municipal_sources(self) -> Dict[str, Dict]:
        """Initialize municipal law sources for major Canadian cities"""
        return {
            'toronto': {
                'name': 'Toronto',
                'province': 'ON',
                'sources': {
                    'property_standards': 'https://www.toronto.ca/city-government/policy-planning/by-laws/',
                    'noise_bylaws': 'Chapter 591',
                    'parking_bylaws': 'Chapter 950',
                    'business_licensing': 'Chapter 545'
                }
            },
            'vancouver': {
                'name': 'Vancouver',
                'province': 'BC',
                'sources': {
                    'property_use': 'https://vancouver.ca/your-government/property-use-bylaws.aspx',
                    'noise_control': 'Bylaw 6555',
                    'business_license': 'Bylaw 4450'
                }
            },
            'montreal': {
                'name': 'Montreal',
                'province': 'QC',
                'sources': {
                    'municipal_bylaws': 'https://ville.montreal.qc.ca/reglements/',
                    'housing_bylaws': 'Règlement sur la salubrité'
                }
            },
            'calgary': {
                'name': 'Calgary',
                'province': 'AB',
                'sources': {
                    'land_use': 'https://www.calgary.ca/development/land-use-bylaws.html',
                    'business_bylaws': 'Bylaw 32M96'
                }
            }
        }
    
    def _initialize_court_forms(self) -> Dict[str, Dict]:
        """Initialize court forms database for all Canadian jurisdictions"""
        return {
            'ON': {
                'family_court': {
                    'application_general': {
                        'form_number': 'Form 8',
                        'title': 'Application (General)',
                        'url': 'https://ontariocourtforms.on.ca/static/media/form-8.pdf',
                        'required_fields': [
                            'applicant_name', 'applicant_address', 'respondent_name',
                            'respondent_address', 'court_file_number', 'relief_sought',
                            'facts', 'legal_basis', 'service_method'
                        ]
                    },
                    'financial_statement': {
                        'form_number': 'Form 13',
                        'title': 'Financial Statement (Property and Support Claims)',
                        'url': 'https://ontariocourtforms.on.ca/static/media/form-13.pdf',
                        'required_fields': [
                            'monthly_income', 'annual_income', 'assets', 'debts',
                            'monthly_expenses', 'employment_details'
                        ]
                    }
                },
                'small_claims': {
                    'plaintiff_claim': {
                        'form_number': 'Form 7A',
                        'title': 'Plaintiff\'s Claim',
                        'url': 'https://ontariocourtforms.on.ca/static/media/form-7A.pdf',
                        'required_fields': [
                            'plaintiff_name', 'defendant_name', 'claim_amount',
                            'facts_of_claim', 'relief_sought', 'court_location'
                        ]
                    }
                },
                'ltb': {
                    'application_above_guideline': {
                        'form_number': 'L1',
                        'title': 'Application to End a Tenancy - Nonpayment of Rent',
                        'url': 'https://tribunalsontario.ca/documents/ltb/Landlord%20Applications/L1.pdf',
                        'required_fields': [
                            'landlord_name', 'tenant_name', 'rental_unit_address',
                            'monthly_rent', 'arrears_amount', 'last_payment_date',
                            'notice_served_date', 'notice_type'
                        ]
                    }
                }
            },
            'BC': {
                'provincial_court': {
                    'small_claims': {
                        'form_number': 'Form 1',
                        'title': 'Notice of Claim',
                        'required_fields': [
                            'claimant_name', 'defendant_name', 'claim_amount',
                            'description_of_claim'
                        ]
                    }
                },
                'rtb': {
                    'application_dispute_resolution': {
                        'form_number': 'RTB-12',
                        'title': 'Application for Dispute Resolution',
                        'required_fields': [
                            'applicant_name', 'respondent_name', 'rental_address',
                            'issue_type', 'monetary_orders_sought'
                        ]
                    }
                }
            }
        }
    
    def get_relevant_laws(self, user: User, case_type: str, case_facts: List[str]) -> Dict[str, Any]:
        """
        Pull all relevant laws based on user's jurisdiction and case details
        """
        jurisdiction = user.province or 'ON'
        city = user.city or ''
        
        relevant_laws = {
            'federal_laws': [],
            'provincial_laws': [],
            'municipal_laws': [],
            'applicable_rights': [],
            'jurisdiction_info': {
                'province': jurisdiction,
                'city': city,
                'federal_court_jurisdiction': False,
                'provincial_court_jurisdiction': True
            }
        }
        
        # Get federal laws
        federal_laws = self._get_federal_laws(case_type, case_facts)
        relevant_laws['federal_laws'] = federal_laws
        
        # Get provincial laws
        provincial_laws = self._get_provincial_laws(jurisdiction, case_type, case_facts)
        relevant_laws['provincial_laws'] = provincial_laws
        
        # Get municipal laws if applicable
        municipal_laws = self._get_municipal_laws(city, jurisdiction, case_type)
        relevant_laws['municipal_laws'] = municipal_laws
        
        # Determine Charter rights applications
        charter_rights = self._get_applicable_charter_rights(case_type, case_facts)
        relevant_laws['applicable_rights'] = charter_rights
        
        # Enhanced fathers' rights analysis
        if case_type.startswith('fathers-'):
            fathers_rights_analysis = enhance_fathers_rights_analysis(case_type, case_facts, jurisdiction)
            relevant_laws['fathers_rights_analysis'] = fathers_rights_analysis
        
        return relevant_laws
    
    def _get_federal_laws(self, case_type: str, case_facts: List[str]) -> List[Dict]:
        """Get applicable federal laws"""
        federal_laws = []
        
        # Criminal matters
        if case_type in ['criminal', 'charter_violation']:
            federal_laws.append({
                'act': 'Criminal Code of Canada',
                'sections': self._get_relevant_criminal_sections(case_facts),
                'jurisdiction': 'Federal',
                'court': 'Provincial Court (Criminal Division) or Superior Court'
            })
        
        # Family law (federal aspects) and Fathers' Rights
        if case_type.startswith('family-') or case_type.startswith('fathers-'):
            divorce_act_sections = []
            key_principles = ['Best interests of the child', 'Federal child support guidelines']
            
            if case_type in ['family-custody', 'family-divorce', 'fathers-custody', 'fathers-access']:
                divorce_act_sections.extend([16, 17, 18, 19])  # Custody and access
                key_principles.extend(['Equal parenting presumption', 'Maximum contact with both parents'])
                
            if case_type in ['family-support', 'family-divorce', 'fathers-support']:
                divorce_act_sections.extend([15.1, 15.2, 15.3])  # Child support
                key_principles.extend(['Income verification requirements', 'Imputation of income rules'])
                
            if case_type == 'family-divorce':
                divorce_act_sections.extend([8, 9])  # Divorce grounds
                
            if case_type in ['fathers-enforcement', 'fathers-access']:
                divorce_act_sections.extend([16.1, 16.2, 16.3])  # Enforcement mechanisms
                key_principles.extend(['Contempt of court for non-compliance', 'Makeup time provisions'])
                
            federal_laws.append({
                'act': 'Divorce Act',
                'sections': divorce_act_sections,
                'jurisdiction': 'Federal',
                'court': 'Superior Court of Justice',
                'key_principles': key_principles,
                'fathers_rights_focus': case_type.startswith('fathers-'),
                'bias_counters': [
                    'Section 16(3): Court shall give effect to the principle that a child should have as much contact with each parent as is consistent with the best interests of the child',
                    'Section 16(4): Past conduct shall not be taken into account unless it is relevant to the ability of that person to act as a parent',
                    'Section 16(6): Court shall consider child\'s views and preferences, giving due weight to age and maturity'
                ]
            })
            
            # Federal Child Support Guidelines - Enhanced for fathers' rights
            support_sections = [15, 16, 17, 18, 19, 20]  # Income calculation
            support_principles = ['Income-based support calculation', 'Special expenses under s.7']
            
            if case_type in ['fathers-support', 'fathers-alienation']:
                support_sections.extend([19, 20, 21])  # Imputation and reduction provisions
                support_principles.extend([
                    'Shared custody adjustments under s.9',
                    'Undue hardship provisions under s.10',
                    'Income imputation for refusing employment',
                    'Reduction for alienation affecting access'
                ])
                
            federal_laws.append({
                'act': 'Federal Child Support Guidelines',
                'regulation': 'SOR/97-175',
                'sections': support_sections,
                'jurisdiction': 'Federal',
                'key_principles': support_principles,
                'fathers_rights_defences': [
                    'Section 9: Shared custody reductions when child spends 40%+ time with father',
                    'Section 10: Undue hardship when support creates financial hardship',
                    'Section 19: Income imputation requires reasonable efforts to earn income',
                    'Section 20: Cannot impute income unless refusal to work is unreasonable'
                ]
            })
        
        # CAS/Child Protection federal aspects
        if case_type.startswith('cas-'):
            # Youth Criminal Justice Act for youth in care
            federal_laws.append({
                'act': 'Youth Criminal Justice Act',
                'sections': [3, 4, 5, 25, 26, 27, 28, 29, 30],  # Principles and rights
                'jurisdiction': 'Federal',
                'court': 'Youth Justice Court',
                'key_principles': ['Youth rehabilitation', 'Alternative measures', 'Minimal intervention']
            })
            
            # Charter protections for families
            federal_laws.append({
                'act': 'Canadian Charter of Rights and Freedoms',
                'sections': [7, 15, 24],
                'jurisdiction': 'Constitutional',
                'court': 'All courts have Charter jurisdiction',
                'key_principles': ['Liberty and security of the person', 'Equality rights', 'Charter remedies']
            })
        
        # Human rights (federal employees)
        if case_type in ['employment', 'human_rights']:
            federal_laws.append({
                'act': 'Canadian Human Rights Act',
                'sections': [7, 8, 9, 10],
                'jurisdiction': 'Federal',
                'tribunal': 'Canadian Human Rights Tribunal'
            })
        
        return federal_laws
    
    def _get_provincial_laws(self, province: str, case_type: str, case_facts: List[str]) -> List[Dict]:
        """Get applicable provincial laws"""
        provincial_laws = []
        
        if province not in self.provincial_sources:
            return provincial_laws
        
        province_data = self.provincial_sources[province]
        sources = province_data.get('sources', {})
        
        # Landlord-tenant matters
        if case_type == 'landlord_tenant':
            if 'residential_tenancies_act' in sources or 'residential_tenancy_act' in sources:
                rta_key = 'residential_tenancies_act' if 'residential_tenancies_act' in sources else 'residential_tenancy_act'
                rta = sources[rta_key]
                provincial_laws.append({
                    'act': f'{province_data["name"]} Residential Tenancies Act',
                    'sections': self._get_relevant_rta_sections(case_facts, rta),
                    'tribunal': rta.get('tribunal', 'Residential Tenancy Tribunal'),
                    'jurisdiction': 'Provincial'
                })
        
        # Employment matters
        if case_type == 'employment':
            if 'employment_standards_act' in sources or 'employment_standards_code' in sources:
                esa_key = 'employment_standards_act' if 'employment_standards_act' in sources else 'employment_standards_code'
                esa = sources[esa_key]
                provincial_laws.append({
                    'act': f'{province_data["name"]} Employment Standards Act',
                    'sections': self._get_relevant_esa_sections(case_facts, esa),
                    'tribunal': esa.get('tribunal', 'Employment Standards Tribunal'),
                    'jurisdiction': 'Provincial'
                })
        
        # Family law (provincial aspects) and Fathers' Rights
        if case_type.startswith('family-') or case_type.startswith('fathers-'):
            if 'family_law_act' in sources:
                fla = sources['family_law_act']
                family_sections = []
                key_principles = ['Best interests of the child', 'Equal parenting responsibility']
                
                if case_type in ['family-custody', 'family-divorce', 'fathers-custody', 'fathers-access']:
                    family_sections.extend(fla.get('key_sections', {}).get('custody_access', []))
                    key_principles.extend(['Equal parenting time presumption', 'Father-child relationship protection'])
                    
                if case_type in ['family-support', 'family-divorce', 'fathers-support']:
                    family_sections.extend(fla.get('key_sections', {}).get('support_obligations', []))
                    key_principles.extend(['Financial hardship consideration', 'Shared custody support adjustments'])
                    
                if case_type == 'family-property':
                    family_sections.extend(fla.get('key_sections', {}).get('property_division', []))
                    
                if case_type in ['family-domestic', 'fathers-false-allegations']:
                    family_sections.extend(fla.get('key_sections', {}).get('domestic_violence', []))
                    family_sections.extend(fla.get('key_sections', {}).get('restraining_orders', []))
                    key_principles.extend(['Due process requirements', 'Burden of proof standards', 'False allegation consequences'])
                
                fathers_rights_provisions = []
                if case_type.startswith('fathers-'):
                    fathers_rights_provisions = [
                        'Section 20: Equal parenting time unless contrary to best interests',
                        'Section 21: Father\'s relationship with child is presumptively beneficial',
                        'Section 22: Court must consider impact of parental alienation',
                        'Section 23: Past conduct relevant only if affects parenting ability',
                        'Section 24: Enforcement mechanisms for denied access'
                    ]
                
                provincial_laws.append({
                    'act': f'{province_data["name"]} Family Law Act',
                    'sections': family_sections,
                    'court': fla.get('court', 'Family Court'),
                    'jurisdiction': 'Provincial',
                    'key_principles': key_principles,
                    'fathers_rights_provisions': fathers_rights_provisions,
                    'bias_counters': [
                        'Gender-neutral language required in all custody determinations',
                        'Equal consideration of both parents\' parenting capacity',
                        'Financial capacity cannot be primary custody factor',
                        'Historical gender role assumptions are prohibited'
                    ]
                })
            
            # Children's Law Reform Act (Ontario-specific)
            if province == 'ON' and 'children_law_reform_act' in sources:
                clra = sources['children_law_reform_act']
                clra_sections = []
                if case_type in ['family-custody', 'family-adoption']:
                    clra_sections.extend(clra.get('key_sections', {}).get('custody_jurisdiction', []))
                    clra_sections.extend(clra.get('key_sections', {}).get('best_interests_test', []))
                    clra_sections.extend(clra.get('key_sections', {}).get('access_rights', []))
                
                provincial_laws.append({
                    'act': 'Children\'s Law Reform Act (Ontario)',
                    'sections': clra_sections,
                    'court': clra.get('court', 'Family Court'),
                    'jurisdiction': 'Provincial',
                    'key_principles': ['Best interests test', 'Custody jurisdiction rules']
                })
        
        # CAS/Child Protection (provincial aspects)
        if case_type.startswith('cas-'):
            if 'child_family_services_act' in sources:
                cfsa = sources['child_family_services_act']
                cas_sections = []
                if case_type == 'cas-investigation':
                    cas_sections.extend(cfsa.get('key_sections', {}).get('child_protection', []))
                if case_type == 'cas-removal':
                    cas_sections.extend(cfsa.get('key_sections', {}).get('removal_powers', []))
                if case_type == 'cas-custody':
                    cas_sections.extend(cfsa.get('key_sections', {}).get('custody_orders', []))
                if case_type == 'cas-access':
                    cas_sections.extend(cfsa.get('key_sections', {}).get('access_rights', []))
                if case_type == 'cas-appeal':
                    cas_sections.extend(cfsa.get('key_sections', {}).get('appeal_rights', []))
                if case_type == 'cas-complaint':
                    cas_sections.extend(cfsa.get('key_sections', {}).get('complaint_process', []))
                
                provincial_laws.append({
                    'act': f'Child and Family Services Act ({province_data["name"]})',
                    'sections': cas_sections,
                    'court': cfsa.get('tribunal', 'Ontario Court of Justice'),
                    'jurisdiction': 'Provincial',
                    'key_principles': ['Best interests of the child', 'Least intrusive measures', 'Family preservation'],
                    'cas_agencies': cfsa.get('cas_agencies', {}),
                    'charter_protections': cfsa.get('charter_protections', {})
                })
        
        # Human rights
        if case_type == 'human_rights':
            if 'human_rights_code' in sources:
                hrc = sources['human_rights_code']
                provincial_laws.append({
                    'act': f'{province_data["name"]} Human Rights Code',
                    'sections': [1, 2, 3, 4, 5],  # Common sections
                    'tribunal': hrc.get('tribunal', 'Human Rights Tribunal'),
                    'jurisdiction': 'Provincial'
                })
        
        return provincial_laws
    
    def _get_municipal_laws(self, city: str, province: str, case_type: str) -> List[Dict]:
        """Get applicable municipal bylaws"""
        municipal_laws = []
        
        city_key = city.lower().replace(' ', '_')
        if city_key in self.municipal_sources:
            city_data = self.municipal_sources[city_key]
            
            # Property-related cases
            if case_type in ['landlord_tenant', 'property_dispute']:
                if 'property_standards' in city_data['sources']:
                    municipal_laws.append({
                        'type': 'Property Standards Bylaw',
                        'source': city_data['sources']['property_standards'],
                        'jurisdiction': f'Municipal - {city_data["name"]}',
                        'enforcement': 'Municipal Bylaw Enforcement'
                    })
            
            # Noise complaints
            if 'noise' in str(case_type).lower():
                if 'noise_bylaws' in city_data['sources']:
                    municipal_laws.append({
                        'type': 'Noise Control Bylaw',
                        'bylaw_number': city_data['sources']['noise_bylaws'],
                        'jurisdiction': f'Municipal - {city_data["name"]}',
                        'enforcement': 'Municipal Bylaw Enforcement'
                    })
        
        return municipal_laws
    
    def _get_applicable_charter_rights(self, case_type: str, case_facts: List[str]) -> List[Dict]:
        """Determine applicable Charter rights"""
        charter_rights = []
        
        # Section 7 - Life, liberty and security
        if case_type in ['criminal', 'family_law', 'cas_child_protection']:
            charter_rights.append({
                'section': 7,
                'title': 'Life, liberty and security of the person',
                'text': 'Everyone has the right to life, liberty and security of the person and the right not to be deprived thereof except in accordance with the principles of fundamental justice.',
                'applicability': 'High - involves fundamental rights'
            })
        
        # Section 8 - Unreasonable search and seizure
        if any('search' in fact.lower() or 'seizure' in fact.lower() for fact in case_facts):
            charter_rights.append({
                'section': 8,
                'title': 'Search or seizure',
                'text': 'Everyone has the right to be secure against unreasonable search or seizure.',
                'applicability': 'Direct - search/seizure issues present'
            })
        
        # Section 15 - Equality rights
        if case_type in ['human_rights', 'employment', 'discrimination']:
            charter_rights.append({
                'section': 15,
                'title': 'Equality before and under law',
                'text': 'Every individual is equal before and under the law and has the right to the equal protection and equal benefit of the law without discrimination.',
                'applicability': 'High - discrimination/equality issues'
            })
        
        return charter_rights
    
    def generate_court_forms(self, user: User, case: Case, relevant_laws: Dict) -> List[Dict]:
        """
        Generate appropriate court forms pre-filled with user data and case information
        """
        jurisdiction = user.province or 'ON'
        case_type = case.case_type
        
        if jurisdiction not in self.court_forms:
            return []
        
        available_forms = self.court_forms[jurisdiction]
        recommended_forms = []
        
        # Determine appropriate forms based on case type
        if case_type == 'family_law' and 'family_court' in available_forms:
            forms = available_forms['family_court']
            
            # General application form
            if 'application_general' in forms:
                form_data = self._prefill_family_application(user, case, forms['application_general'])
                recommended_forms.append(form_data)
            
            # Financial statement if support/property involved
            if 'financial_statement' in forms:
                form_data = self._prefill_financial_statement(user, case, forms['financial_statement'])
                recommended_forms.append(form_data)
        
        elif case_type == 'small_claims' and 'small_claims' in available_forms:
            forms = available_forms['small_claims']
            
            if 'plaintiff_claim' in forms:
                form_data = self._prefill_small_claims(user, case, forms['plaintiff_claim'])
                recommended_forms.append(form_data)
        
        elif case_type == 'landlord_tenant' and 'ltb' in available_forms:
            forms = available_forms['ltb']
            
            if 'application_above_guideline' in forms:
                form_data = self._prefill_ltb_application(user, case, forms['application_above_guideline'])
                recommended_forms.append(form_data)
        
        return recommended_forms
    
    def _prefill_family_application(self, user: User, case: Case, form_template: Dict) -> Dict:
        """Pre-fill family court application form"""
        ai_analysis = case.case_metadata.get('ai_analysis', {}) if case.case_metadata else {}
        key_facts = ai_analysis.get('key_facts', [])
        
        prefilled_data = {
            'form_info': form_template,
            'prefilled_fields': {
                'applicant_name': f"{user.first_name} {user.last_name}",
                'applicant_address': f"{user.address}, {user.city}, {user.province} {user.postal_code}",
                'applicant_phone': user.phone,
                'court_location': self._get_court_location(user.city, user.province),
                'case_type': 'Family Law Application',
                'facts': self._format_facts_for_court(key_facts),
                'relief_sought': self._generate_relief_sought(case, ai_analysis),
                'legal_basis': self._generate_legal_basis(case, ai_analysis),
                'filing_date': datetime.now().strftime('%Y-%m-%d')
            },
            'additional_requirements': [
                'Attach supporting documents',
                'Serve on respondent within 30 days',
                'File proof of service'
            ]
        }
        
        return prefilled_data
    
    def _prefill_financial_statement(self, user: User, case: Case, form_template: Dict) -> Dict:
        """Pre-fill financial statement form"""
        return {
            'form_info': form_template,
            'prefilled_fields': {
                'full_name': f"{user.first_name} {user.last_name}",
                'address': f"{user.address}, {user.city}, {user.province} {user.postal_code}",
                'phone': user.phone,
                'occupation': '[TO BE COMPLETED BY USER]',
                'employer': '[TO BE COMPLETED BY USER]',
                'annual_income': '[TO BE COMPLETED BY USER]',
                'monthly_income': '[TO BE COMPLETED BY USER]'
            },
            'completion_instructions': [
                'Complete all income sections with actual figures',
                'List all assets and their current market value',
                'Include all debts and monthly obligations',
                'Attach supporting documentation (pay stubs, tax returns, bank statements)'
            ]
        }
    
    def _prefill_small_claims(self, user: User, case: Case, form_template: Dict) -> Dict:
        """Pre-fill small claims court form"""
        ai_analysis = case.case_metadata.get('ai_analysis', {}) if case.case_metadata else {}
        key_facts = ai_analysis.get('key_facts', [])
        
        # Extract monetary amounts from facts
        claim_amount = self._extract_claim_amount(key_facts)
        
        return {
            'form_info': form_template,
            'prefilled_fields': {
                'plaintiff_name': f"{user.first_name} {user.last_name}",
                'plaintiff_address': f"{user.address}, {user.city}, {user.province} {user.postal_code}",
                'plaintiff_phone': user.phone,
                'claim_amount': claim_amount or '[AMOUNT TO BE DETERMINED]',
                'court_location': self._get_court_location(user.city, user.province),
                'facts_of_claim': self._format_facts_for_court(key_facts),
                'relief_sought': f"Monetary damages in the amount of ${claim_amount}" if claim_amount else "[RELIEF TO BE SPECIFIED]"
            },
            'filing_requirements': [
                'Court filing fee required',
                'Serve defendant within 20 days',
                'Maximum claim: $35,000 (Ontario)'
            ]
        }
    
    def _prefill_ltb_application(self, user: User, case: Case, form_template: Dict) -> Dict:
        """Pre-fill LTB application form"""
        ai_analysis = case.case_metadata.get('ai_analysis', {}) if case.case_metadata else {}
        key_facts = ai_analysis.get('key_facts', [])
        
        # Extract rental information
        rental_amount = self._extract_rental_amount(key_facts)
        arrears_amount = self._extract_arrears_amount(key_facts)
        
        return {
            'form_info': form_template,
            'prefilled_fields': {
                'landlord_name': f"{user.first_name} {user.last_name}",
                'landlord_address': f"{user.address}, {user.city}, {user.province} {user.postal_code}",
                'landlord_phone': user.phone,
                'rental_unit_address': '[RENTAL PROPERTY ADDRESS]',
                'monthly_rent': rental_amount or '[MONTHLY RENT AMOUNT]',
                'arrears_amount': arrears_amount or '[ARREARS AMOUNT]',
                'application_type': 'Non-payment of Rent',
                'relief_sought': 'Termination of tenancy and eviction order'
            },
            'required_attachments': [
                'Copy of lease agreement',
                'Notice to End Tenancy (Form N4)',
                'Rent payment history',
                'Certificate of Service'
            ]
        }
    
    def _get_court_location(self, city: str, province: str) -> str:
        """Get appropriate court location"""
        court_locations = {
            'toronto': 'Superior Court of Justice - Toronto',
            'ottawa': 'Superior Court of Justice - Ottawa',
            'hamilton': 'Superior Court of Justice - Hamilton',
            'vancouver': 'Supreme Court of British Columbia - Vancouver',
            'calgary': 'Court of Queen\'s Bench of Alberta - Calgary'
        }
        
        return court_locations.get(city.lower(), f"Superior Court - {city}")
    
    def _format_facts_for_court(self, facts: List[str]) -> str:
        """Format extracted facts for court documents"""
        if not facts:
            return "[FACTS TO BE COMPLETED BY USER]"
        
        formatted_facts = []
        for i, fact in enumerate(facts[:10], 1):  # Limit to 10 most important facts
            formatted_facts.append(f"{i}. {fact}")
        
        return "\n".join(formatted_facts)
    
    def _generate_relief_sought(self, case: Case, ai_analysis: Dict) -> str:
        """Generate appropriate relief sought based on case analysis"""
        case_type = case.case_type
        merit_score = ai_analysis.get('merit_score', {})
        
        relief_templates = {
            'family_law': [
                'An order for spousal support',
                'An order for child support',
                'An order for custody and access',
                'An order for division of matrimonial property'
            ],
            'employment': [
                'Compensation for wrongful dismissal',
                'Reinstatement to employment position',
                'Damages for lost wages and benefits'
            ],
            'landlord_tenant': [
                'An order terminating the tenancy',
                'An order for possession of the rental unit',
                'An order for payment of rent arrears'
            ],
            'small_claims': [
                'Monetary damages',
                'Return of property',
                'Specific performance of contract'
            ]
        }
        
        return "; ".join(relief_templates.get(case_type, ['Appropriate legal remedy']))
    
    def _generate_legal_basis(self, case: Case, ai_analysis: Dict) -> str:
        """Generate legal basis for the application"""
        relevant_authorities = ai_analysis.get('relevant_authorities', [])
        
        if relevant_authorities:
            citations = [auth.get('citation', '') for auth in relevant_authorities[:3]]
            return f"Legal basis: {'; '.join(filter(None, citations))}"
        
        return "[LEGAL BASIS TO BE COMPLETED BASED ON APPLICABLE LAW]"
    
    def _extract_claim_amount(self, facts: List[str]) -> Optional[str]:
        """Extract monetary claim amount from facts"""
        import re
        
        for fact in facts:
            # Look for dollar amounts
            amounts = re.findall(r'\$[\d,]+\.?\d*', fact)
            if amounts:
                return amounts[0].replace('$', '').replace(',', '')
        
        return None
    
    def _extract_rental_amount(self, facts: List[str]) -> Optional[str]:
        """Extract rental amount from facts"""
        import re
        
        for fact in facts:
            if 'rent' in fact.lower():
                amounts = re.findall(r'\$[\d,]+\.?\d*', fact)
                if amounts:
                    return amounts[0].replace('$', '').replace(',', '')
        
        return None
    
    def _extract_arrears_amount(self, facts: List[str]) -> Optional[str]:
        """Extract arrears amount from facts"""
        import re
        
        for fact in facts:
            if any(term in fact.lower() for term in ['arrears', 'owing', 'unpaid', 'balance']):
                amounts = re.findall(r'\$[\d,]+\.?\d*', fact)
                if amounts:
                    return amounts[0].replace('$', '').replace(',', '')
        
        return None
    
    # Helper methods for getting relevant sections
    def _get_relevant_criminal_sections(self, case_facts: List[str]) -> List[int]:
        """Get relevant Criminal Code sections"""
        # This would analyze case facts and return relevant sections
        # For now, return common sections
        return [265, 266, 267]  # Assault sections as example
    
    def _get_relevant_rta_sections(self, case_facts: List[str], rta_data: Dict) -> List[int]:
        """Get relevant RTA sections"""
        sections = []
        if 'key_sections' in rta_data:
            # Analyze facts to determine relevant sections
            for category, section_list in rta_data['key_sections'].items():
                if any(keyword in ' '.join(case_facts).lower() for keyword in category.split('_')):
                    sections.extend(section_list)
        return sections[:5]  # Limit to 5 most relevant
    
    def _get_relevant_esa_sections(self, case_facts: List[str], esa_data: Dict) -> List[int]:
        """Get relevant Employment Standards Act sections"""
        sections = []
        if 'key_sections' in esa_data:
            for category, section_list in esa_data['key_sections'].items():
                if any(keyword in ' '.join(case_facts).lower() for keyword in category.split('_')):
                    sections.extend(section_list)
        return sections[:5]
    
    def _get_relevant_family_sections(self, case_facts: List[str], fla_data: Dict) -> List[int]:
        """Get relevant Family Law Act sections"""
        sections = []
        if 'key_sections' in fla_data:
            for category, section_list in fla_data['key_sections'].items():
                if any(keyword in ' '.join(case_facts).lower() for keyword in category.split('_')):
                    sections.extend(section_list)
        return sections[:5]

# Initialize the legal engine
canadian_legal_engine = CanadianLegalEngine()