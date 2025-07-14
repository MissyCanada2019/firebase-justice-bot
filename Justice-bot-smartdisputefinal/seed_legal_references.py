"""
Seed legal references for the recommendation engine
"""
from datetime import datetime
from app import app, db
from models import LegalReference

def seed_legal_references():
    """Add sample Canadian legal references to the database"""
    
    sample_references = [
        {
            'title': 'Charter of Rights and Freedoms - Section 7',
            'citation': 'Constitution Act, 1982, s. 7',
            'source_type': 'legislation',
            'jurisdiction': 'canada',
            'content_snippet': 'Everyone has the right to life, liberty and security of the person and the right not to be deprived thereof except in accordance with the principles of fundamental justice.',
            'year': 1982,
            'relevance_score': 0.95,
            'tags': {'areas': ['constitutional', 'criminal', 'administrative'], 'keywords': ['liberty', 'security', 'fundamental justice']},
            'url': 'https://laws-lois.justice.gc.ca/eng/const/page-12.html'
        },
        {
            'title': 'Residential Tenancies Act - Tenant Rights',
            'citation': 'Residential Tenancies Act, 2006, S.O. 2006, c. 17',
            'source_type': 'legislation',
            'jurisdiction': 'ontario',
            'content_snippet': 'A landlord may terminate a tenancy only in accordance with this Act. The termination must be for a reason specified in this Act.',
            'year': 2006,
            'relevance_score': 0.85,
            'tags': {'areas': ['housing', 'tenant rights'], 'keywords': ['termination', 'landlord', 'tenant']},
            'url': 'https://www.ontario.ca/laws/statute/06r17'
        },
        {
            'title': 'Employment Standards Act - Wrongful Dismissal',
            'citation': 'Employment Standards Act, 2000, S.O. 2000, c. 41',
            'source_type': 'legislation',
            'jurisdiction': 'ontario',
            'content_snippet': 'An employer shall not terminate the employment of an employee without giving the employee notice of termination or pay in lieu of notice.',
            'year': 2000,
            'relevance_score': 0.88,
            'tags': {'areas': ['employment', 'wrongful dismissal'], 'keywords': ['termination', 'notice', 'employer']},
            'url': 'https://www.ontario.ca/laws/statute/00e41'
        },
        {
            'title': 'Human Rights Code - Discrimination',
            'citation': 'Human Rights Code, R.S.O. 1990, c. H.19',
            'source_type': 'legislation',
            'jurisdiction': 'ontario',
            'content_snippet': 'Every person has a right to equal treatment with respect to services, goods and facilities, without discrimination because of race, ancestry, place of origin, colour, ethnic origin, citizenship, creed, sex, sexual orientation, gender identity, gender expression, age, marital status, family status or disability.',
            'year': 1990,
            'relevance_score': 0.92,
            'tags': {'areas': ['discrimination', 'human rights'], 'keywords': ['equal treatment', 'discrimination', 'services']},
            'url': 'https://www.ontario.ca/laws/statute/90h19'
        },
        {
            'title': 'Consumer Protection Act - Unfair Practices',
            'citation': 'Consumer Protection Act, 2002, S.O. 2002, c. 30',
            'source_type': 'legislation',
            'jurisdiction': 'ontario',
            'content_snippet': 'No person shall engage in an unfair practice. A consumer agreement may be cancelled without penalty if entered into as a result of an unfair practice.',
            'year': 2002,
            'relevance_score': 0.80,
            'tags': {'areas': ['consumer protection'], 'keywords': ['unfair practice', 'consumer agreement', 'cancellation']},
            'url': 'https://www.ontario.ca/laws/statute/02c30'
        },
        {
            'title': 'R. v. Oakes - Charter Analysis Framework',
            'citation': '[1986] 1 S.C.R. 103',
            'source_type': 'case_law',
            'jurisdiction': 'canada',
            'content_snippet': 'The Oakes test establishes the framework for determining whether a limitation on Charter rights is justified under section 1. The limitation must be prescribed by law, serve a pressing and substantial objective, and be proportional.',
            'year': 1986,
            'relevance_score': 0.90,
            'tags': {'areas': ['constitutional', 'charter rights'], 'keywords': ['oakes test', 'proportional', 'justified']},
            'url': 'https://scc-csc.lexum.com/scc-csc/scc-csc/en/item/117/index.do'
        },
        {
            'title': 'Wilson v. British Columbia (Superintendent of Motor Vehicles)',
            'citation': '[2015] 3 S.C.R. 300',
            'source_type': 'case_law',
            'jurisdiction': 'canada',
            'content_snippet': 'Administrative decisions that affect Charter rights must be made in accordance with Charter values, even when the Charter does not directly apply.',
            'year': 2015,
            'relevance_score': 0.85,
            'tags': {'areas': ['administrative law', 'charter rights'], 'keywords': ['administrative decisions', 'charter values']},
            'url': 'https://scc-csc.lexum.com/scc-csc/scc-csc/en/item/15648/index.do'
        },
        {
            'title': 'Canada (Attorney General) v. Ward',
            'citation': '[1993] 2 S.C.R. 689',
            'source_type': 'case_law',
            'jurisdiction': 'canada',
            'content_snippet': 'Persecution must be for reasons of race, religion, nationality, political opinion or membership in a particular social group. The claimant must show that state protection is unavailable.',
            'year': 1993,
            'relevance_score': 0.75,
            'tags': {'areas': ['immigration', 'refugee law'], 'keywords': ['persecution', 'state protection', 'refugee']},
            'url': 'https://scc-csc.lexum.com/scc-csc/scc-csc/en/item/1023/index.do'
        }
    ]
    
    with app.app_context():
        # Check if references already exist
        existing_count = LegalReference.query.count()
        if existing_count > 0:
            print(f"Legal references already exist ({existing_count} found). Skipping seed.")
            return
        
        for ref_data in sample_references:
            reference = LegalReference(
                title=ref_data['title'],
                citation=ref_data['citation'],
                source_type=ref_data['source_type'],
                jurisdiction=ref_data['jurisdiction'],
                content_snippet=ref_data['content_snippet'],
                year=ref_data['year'],
                relevance_score=ref_data['relevance_score'],
                tags=ref_data['tags'],
                url=ref_data['url'],
                created_at=datetime.utcnow()
            )
            db.session.add(reference)
        
        db.session.commit()
        print(f"Successfully seeded {len(sample_references)} legal references")

if __name__ == "__main__":
    seed_legal_references()