import os
import logging
import json
import re
from datetime import datetime

from utils.canlii_api import search_canlii, get_relevant_precedents, get_legislation

# Configure logging
logger = logging.getLogger(__name__)

def get_relevant_case_law(query, context=None, max_results=3):
    """
    Get relevant case law based on a user query
    
    Args:
        query (str): User query/message
        context (dict, optional): Additional context like case information
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of relevant case law citations
    """
    try:
        # Extract the legal category from context if available
        category = "general"
        jurisdiction = "on"
        
        if context and 'case' in context:
            case = context['case']
            if hasattr(case, 'category') and case.category:
                category = case.category
        
        # Extract key topics from the query
        topics = extract_legal_topics(query)
        
        # Prepare search query based on extracted topics and category
        search_query = f"{' '.join(topics)} {category}"
        
        # Search for relevant cases
        search_results = search_canlii(
            query=search_query,
            jurisdiction=jurisdiction,
            document_type='decisions',
            max_results=max_results
        )
        
        # If we have specific case context, also get precedents
        precedents = []
        if context and 'case' in context and hasattr(context['case'], 'category'):
            # Get relevant precedents for the case category
            precedent_results = get_relevant_precedents(
                category=context['case'].category,
                analysis=context.get('analysis'),
                jurisdiction=jurisdiction
            )
            
            # Extract the most relevant precedents
            if precedent_results and 'landmark_cases' in precedent_results:
                precedents = precedent_results['landmark_cases'][:max_results]
        
        # Combine and format results
        all_results = []
        
        # Add search results
        for result in search_results:
            all_results.append({
                'title': result.get('title', 'Unknown Case'),
                'citation': result.get('citation', ''),
                'snippet': result.get('snippet', ''),
                'url': result.get('url', ''),
                'relevance': result.get('relevance', 0.0),
                'source': 'search'
            })
        
        # Add precedents if not already in results
        for precedent in precedents:
            # Check if this precedent is already in results
            duplicate = False
            for result in all_results:
                if result.get('citation') == precedent.get('citation'):
                    duplicate = True
                    break
            
            if not duplicate:
                all_results.append({
                    'title': precedent.get('title', 'Unknown Case'),
                    'citation': precedent.get('citation', ''),
                    'snippet': precedent.get('snippet', ''),
                    'url': precedent.get('url', ''),
                    'relevance': precedent.get('relevance', 0.0),
                    'source': 'precedent'
                })
        
        # Sort by relevance and limit results
        sorted_results = sorted(all_results, key=lambda x: x.get('relevance', 0), reverse=True)
        return sorted_results[:max_results]
        
    except Exception as e:
        logger.error(f"Error getting relevant case law: {str(e)}")
        return []

def get_legislation_references(query, context=None, max_results=2):
    """
    Get relevant legislation references based on a user query
    
    Args:
        query (str): User query/message
        context (dict, optional): Additional context like case information
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of relevant legislation references
    """
    try:
        # Extract the legal category from context if available
        category = "general"
        jurisdiction = "on"
        
        if context and 'case' in context:
            case = context['case']
            if hasattr(case, 'category') and case.category:
                category = case.category
        
        # Map categories to common legislation
        legislation_mapping = {
            'landlord-tenant': ['residential-tenancies-act'],
            'credit': ['consumer-reporting-act', 'consumer-protection-act'],
            'human-rights': ['human-rights-code'],
            'small-claims': ['courts-of-justice-act', 'rules-of-civil-procedure'],
            'general': []
        }
        
        # Get legislation IDs based on category
        legislation_ids = legislation_mapping.get(category, [])
        
        # If no specific legislation found, search CanLII
        if not legislation_ids:
            # Extract key topics from the query
            topics = extract_legal_topics(query)
            
            # Prepare search query based on extracted topics
            search_query = f"{' '.join(topics)} act code regulation"
            
            # Search for relevant legislation
            search_results = search_canlii(
                query=search_query,
                jurisdiction=jurisdiction,
                document_type='legislation',
                max_results=max_results
            )
            
            # Format search results
            return [{
                'title': result.get('title', 'Unknown Legislation'),
                'citation': result.get('citation', ''),
                'snippet': result.get('snippet', ''),
                'url': result.get('url', ''),
                'relevance': result.get('relevance', 0.0)
            } for result in search_results]
        
        # Get details for each legislation ID
        legislation_references = []
        for legislation_id in legislation_ids[:max_results]:
            legislation = get_legislation(legislation_id, jurisdiction)
            if legislation:
                # Format legislation reference
                legislation_references.append({
                    'title': legislation.get('title', 'Unknown Legislation'),
                    'citation': legislation.get('citation', ''),
                    'snippet': format_legislation_snippet(legislation),
                    'url': f"https://www.canlii.org/en/on/laws/stat/{legislation_id}/latest/{legislation_id}.html",
                    'relevance': 0.9  # High relevance since it's category-matched
                })
        
        return legislation_references
        
    except Exception as e:
        logger.error(f"Error getting legislation references: {str(e)}")
        return []

def extract_legal_topics(query):
    """
    Extract key legal topics from a user query
    
    Args:
        query (str): User query/message
        
    Returns:
        list: List of extracted legal topics
    """
    # Convert to lowercase for better matching
    query_lower = query.lower()
    
    # Define common legal topics per category
    topic_keywords = {
        'landlord-tenant': [
            'eviction', 'rent', 'lease', 'repair', 'maintenance', 'landlord', 'tenant', 
            'security deposit', 'notice', 'termination', 'mold', 'habitability', 'rental'
        ],
        'credit': [
            'credit report', 'credit score', 'dispute', 'error', 'debt', 'collection',
            'equifax', 'transunion', 'account', 'bankruptcy', 'loan', 'interest'
        ],
        'human-rights': [
            'discrimination', 'harassment', 'accommodation', 'disability', 'gender', 
            'race', 'religion', 'equal', 'workplace', 'access', 'protected ground'
        ],
        'small-claims': [
            'claim', 'debt', 'damages', 'contract', 'breach', 'court', 'judgment',
            'plaintiff', 'defendant', 'settlement', 'sue', 'lawsuit'
        ],
        'procedure': [
            'file', 'application', 'form', 'deadline', 'hearing', 'evidence',
            'witness', 'testify', 'affidavit', 'service', 'notice', 'document'
        ]
    }
    
    # Extract topics from query
    found_topics = []
    
    # Check each category for topic keywords
    for category, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword in query_lower:
                found_topics.append(keyword)
    
    # If no topics found, use common words from the query
    if not found_topics:
        # Remove common words and punctuation
        common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 'when', 'where', 'how', 'why', 
                       'is', 'am', 'are', 'was', 'were', 'be', 'being', 'been', 'do', 'does', 'did', 'can', 'could', 'will',
                       'would', 'should', 'may', 'might', 'must', 'have', 'has', 'had', 'having', 'in', 'on', 'at', 'to', 'for']
        words = re.findall(r'\b\w+\b', query_lower)
        found_topics = [word for word in words if word not in common_words and len(word) > 3]
        
        # Limit to 3 keywords
        found_topics = found_topics[:3]
    
    return found_topics

def format_legislation_snippet(legislation):
    """
    Format a snippet from legislation data
    
    Args:
        legislation (dict): Legislation data
        
    Returns:
        str: Formatted snippet
    """
    snippet = ""
    
    # Include title
    if 'title' in legislation:
        snippet += f"{legislation['title']}"
    
    # Add relevant section if available
    if 'sections' in legislation and legislation['sections']:
        first_section = legislation['sections'][0]
        if 'number' in first_section and 'text' in first_section:
            snippet += f"\nSection {first_section['number']}: {first_section['text'][:150]}..."
    
    # Fallback if no sections found
    if not snippet:
        snippet = f"This legislation governs {legislation.get('title', 'legal matters')} in {legislation.get('jurisdiction', 'this jurisdiction')}."
    
    return snippet

def format_case_law_for_display(case_law_references):
    """
    Format case law references for display in the chat UI
    
    Args:
        case_law_references (list): List of case law references
        
    Returns:
        str: HTML-formatted case law references
    """
    if not case_law_references:
        return ""
    
    # Simple HTML that matches our CSS styling
    html = '<div class="legal-references" style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid rgba(255, 255, 255, 0.1);">'
    html += '<h5 style="margin-top: 0.75rem; margin-bottom: 0.5rem;">Relevant Legal References:</h5>'
    html += '<div class="list-group">'
    
    for ref in case_law_references:
        title = ref.get("title", "Case Reference").replace('"', '&quot;')
        citation = ref.get("citation", "").replace('"', '&quot;')
        snippet = ref.get("snippet", "").replace('"', '&quot;')
        url = ref.get("url", "#").replace('"', '&quot;')
        
        html += f'<div class="legal-reference" style="background-color: rgba(0, 123, 255, 0.1); border-left: 3px solid var(--bs-primary); margin-bottom: 0.5rem; padding: 0.75rem; border-radius: 0.25rem;">'
        html += f'<h6 style="margin-bottom: 0.25rem;"><a href="{url}" target="_blank" style="color: var(--bs-primary); text-decoration: none;">{title}</a></h6>'
        html += f'<p style="font-size: 0.8rem; color: #6c757d; margin-bottom: 0.4rem;">{citation}</p>'
        html += f'<p style="margin-bottom: 0;">{snippet}</p>'
        html += '</div>'
    
    html += '</div></div>'
    return html

def get_case_law_for_query(query, context=None):
    """
    Get combined case law and legislation references for a query
    
    Args:
        query (str): User query/message
        context (dict, optional): Additional context like case information
        
    Returns:
        list: Combined list of legal references
        str: HTML-formatted references for display
    """
    # Get case law references
    case_law = get_relevant_case_law(query, context, max_results=2)
    
    # Get legislation references
    legislation = get_legislation_references(query, context, max_results=1)
    
    # Combine results
    combined_references = case_law + legislation
    
    # Sort by relevance
    sorted_references = sorted(combined_references, key=lambda x: x.get('relevance', 0), reverse=True)
    
    # Format for display
    formatted_html = format_case_law_for_display(sorted_references)
    
    return sorted_references, formatted_html

def analyze_text_for_legal_references(text):
    """
    Analyze text for legal citation patterns and key legal terms
    
    Args:
        text (str): Text to analyze
        
    Returns:
        list: List of detected legal references and terms
    """
    # Define patterns for common legal citations
    citation_patterns = [
        # Canadian Supreme Court, e.g., "2015 SCC 5" or "R. v. Smith, 2015 SCC 5"
        r'(?:(?:[A-Z][\w\s\.\-\']+v\.[\s\w\.\-\']+,\s*)?)(20\d{2}|19\d{2})\s+SCC\s+\d+',
        
        # Canadian Federal Court, e.g., "2018 FC 123"
        r'(?:(?:[A-Z][\w\s\.\-\']+v\.[\s\w\.\-\']+,\s*)?)(20\d{2}|19\d{2})\s+FC\s+\d+',
        
        # Provincial Courts, e.g., "2019 ONSC 456" or "R. v. Smith, 2019 ONSC 456"
        r'(?:(?:[A-Z][\w\s\.\-\']+v\.[\s\w\.\-\']+,\s*)?)(20\d{2}|19\d{2})\s+(?:ON|BC|AB|SK|MB|NB|NS|PE|NL|YK|NT|NU)(?:SC|CA|CJ)\s+\d+',
        
        # Neutral citations, e.g., "2020 CanLII 12345"
        r'(?:(?:[A-Z][\w\s\.\-\']+v\.[\s\w\.\-\']+,\s*)?)(20\d{2}|19\d{2})\s+CanLII\s+\d+',
        
        # Case names, e.g., "Smith v. Jones"
        r'[A-Z][\w\s\.\-\']+\sv\.\s[\w\s\.\-\']+',
        
        # Legislation citations, e.g., "R.S.O. 1990, c. H-19"
        r'(?:R\.S\.O\.|S\.O\.|R\.S\.C\.|S\.C\.)\s+\d{4},\s+c\.\s+[A-Z0-9\-]+',
        
        # Section references, e.g., "section 5(1)" or "s. 5(1)"
        r'(?:section|s\.)\s+\d+(?:\(\d+\))?'
    ]
    
    # Find all matches for citation patterns
    detected_references = []
    for pattern in citation_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            detected_references.append({
                'type': 'citation',
                'text': match.group(0),
                'start': match.start(),
                'end': match.end()
            })
    
    # Check for key legal terms and phrases
    legal_terms = [
        'legislation', 'statute', 'regulation', 'precedent', 'ruling',
        'jurisprudence', 'case law', 'legal doctrine', 'common law',
        'federal court', 'supreme court', 'provincial court', 'tribunal',
        'tenant board', 'human rights tribunal'
    ]
    
    for term in legal_terms:
        pattern = r'\b' + re.escape(term) + r'\b'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            detected_references.append({
                'type': 'term',
                'text': match.group(0),
                'start': match.start(),
                'end': match.end()
            })
    
    # Sort by position in text
    detected_references.sort(key=lambda x: x['start'])
    
    return detected_references

def generate_inline_references(message, context=None):
    """
    Generate inline contextual references for key legal terms in a message
    
    Args:
        message (str): User message
        context (dict, optional): Additional context information
        
    Returns:
        dict: Original message plus enhanced version with inline references
    """
    # First analyze the message for legal references
    detected_references = analyze_text_for_legal_references(message)
    
    # If we found potential references, get relevant case law
    if detected_references:
        # Extract key terms from detected references
        reference_terms = []
        for ref in detected_references:
            if ref['type'] == 'citation':
                # Citations are high-value reference points
                reference_terms.append(ref['text'])
            elif ref['type'] == 'term':
                # Terms may be more general
                reference_terms.append(ref['text'])
        
        # Get relevant case law and legislation based on detected references
        reference_query = ' '.join(reference_terms[:3])  # Use top 3 references for query
        case_law = get_relevant_case_law(reference_query, context, max_results=3)
        
        # Prepare enhanced response
        if case_law:
            return {
                'original_message': message,
                'detected_references': detected_references,
                'contextual_references': case_law
            }
    
    # Default response with no enhancements
    return {
        'original_message': message,
        'detected_references': [],
        'contextual_references': []
    }

def format_message_with_inline_references(message, references):
    """
    Format a message with inline contextual references
    
    Args:
        message (str): Original message text
        references (list): List of reference objects
        
    Returns:
        str: HTML-formatted message with inline contextual references
    """
    # If we have no references, return the original message
    if not references or not references.get('contextual_references'):
        return message
    
    # Get detected references and contextual references
    detected_refs = references.get('detected_references', [])
    contextual_refs = references.get('contextual_references', [])
    
    # Sort references by relevance
    sorted_refs = sorted(contextual_refs, key=lambda x: x.get('relevance', 0), reverse=True)
    
    # Prepare HTML snippets for each reference
    ref_snippets = {}
    for i, ref in enumerate(sorted_refs):
        ref_id = f"ref-{i+1}"
        ref_title = ref.get('title', 'Case Reference')
        ref_citation = ref.get('citation', '')
        ref_url = ref.get('url', '#')
        
        # Format the tooltip content
        tooltip_html = f"""
        <div class="legal-reference-tooltip">
            <h6>{ref_title}</h6>
            <p class="text-muted">{ref_citation}</p>
            <p class="snippet">{ref.get('snippet', '').strip()[:150]}...</p>
            <a href="{ref_url}" target="_blank" class="btn btn-sm btn-outline-primary">Read More</a>
        </div>
        """
        
        # Format the reference snippet
        ref_snippets[ref_id] = {
            'tooltip': tooltip_html,
            'ref_data': ref
        }
    
    # If message already has HTML, process it differently
    if '<' in message and '>' in message:
        # This is a complex task that would require HTML parsing
        # For simplicity, just append the references below the message
        # In a full implementation, we would use a proper HTML parser
        references_html = format_case_law_for_display(sorted_refs)
        return f"{message}{references_html}"
    
    # If we have detected references in the text, add tooltip markers
    message_html = message
    
    # First convert plain text to HTML (handle line breaks, etc.)
    message_html = message.replace('\n', '<br>')
    
    # For each detected reference that matches our contextual references, add a tooltip
    if detected_refs:
        # Add reference tooltips
        for i, ref in enumerate(sorted_refs):
            ref_id = f"ref-{i+1}"
            ref_citation = ref.get('citation', '').lower()
            
            # Find all detected references that match this citation
            for detected in detected_refs:
                if ref_citation and ref_citation in detected['text'].lower():
                    # Create tooltip span
                    tooltip_span = f"""<span class="legal-reference-inline" 
                                   data-reference-id="{ref_id}" 
                                   data-toggle="tooltip"
                                   data-html="true"
                                   title="{ref.get('title', 'Case Reference')}">
                                   {detected['text']}
                                   <sup class="reference-marker">[{i+1}]</sup>
                                   </span>"""
                    
                    # Replace in message
                    message_html = message_html.replace(detected['text'], tooltip_span, 1)
    
    # Add the footnotes section at the end
    if ref_snippets:
        message_html += '<div class="legal-references">'
        message_html += '<h5 class="mt-3 mb-2">Relevant Legal References:</h5>'
        message_html += '<ol class="reference-list">'
        
        for i, (ref_id, ref_data) in enumerate(ref_snippets.items()):
            ref = ref_data['ref_data']
            message_html += f"""
            <li id="{ref_id}">
                <div class="legal-reference">
                    <h6><a href="{ref.get('url', '#')}" target="_blank">{ref.get('title', 'Case Reference')}</a></h6>
                    <p class="text-muted">{ref.get('citation', '')}</p>
                    <p>{ref.get('snippet', '')}</p>
                </div>
            </li>
            """
        
        message_html += '</ol>'
        message_html += '</div>'
    
    return message_html