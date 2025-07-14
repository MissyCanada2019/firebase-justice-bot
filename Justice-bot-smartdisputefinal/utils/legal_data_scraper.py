"""
Legal Data Scraper for SmartDispute.ai

This module provides functionality to scrape and extract legal information from various
Canadian legal sources including:
- Justice Laws Website (laws-lois.justice.gc.ca)
- Federal Court and Federal Court of Appeal websites
- Supreme Court of Canada (scc-csc.ca)
- Provincial Court Websites
- Canada Gazette (gazette.gc.ca)
- SOQUIJ (Quebec-specific)
- Court bulletins / Trial updates via Court Twitter/X accounts
- Provincial Bar Associations
- Slaw.ca
- University Law Libraries
- Google Scholar (Canada region, case law)

The scraper respects robots.txt rules and implements rate limiting to avoid
overwhelming the source websites.
"""

import os
import re
import json
import time
import logging
import datetime
import random
import hashlib
import urllib.parse
import urllib.robotparser
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import trafilatura

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define constants
USER_AGENT = 'SmartDispute.ai Legal Information Scraper (+https://smartdispute.ai/legal-scraper)'
REQUEST_TIMEOUT = 30  # seconds
MIN_DELAY = 2  # seconds
MAX_DELAY = 5  # seconds

# Define legal sources
LEGAL_SOURCES = {
    'justice-laws': {
        'name': 'Justice Laws Website',
        'url': 'https://laws-lois.justice.gc.ca/eng/',
        'description': 'Official source for federal laws and regulations of Canada.',
        'recent_url': 'https://laws-lois.justice.gc.ca/eng/acts/A-1/recent.html'
    },
    'scc': {
        'name': 'Supreme Court of Canada',
        'url': 'https://www.scc-csc.ca/case-dossier/index-eng.aspx',
        'description': 'Judgments from the Supreme Court of Canada.',
        'recent_url': 'https://www.scc-csc.ca/case-dossier/cb/index-eng.aspx'
    },
    'federal-court': {
        'name': 'Federal Court of Canada',
        'url': 'https://decisions.fct-cf.gc.ca/fc-cf/en/nav.do',
        'description': 'Decisions from the Federal Court of Canada.',
        'recent_url': 'https://decisions.fct-cf.gc.ca/fc-cf/en/d/r/index.do?col=54'
    },
    'federal-court-appeal': {
        'name': 'Federal Court of Appeal',
        'url': 'https://decisions.fca-caf.gc.ca/fca-caf/en/nav.do',
        'description': 'Decisions from the Federal Court of Appeal.',
        'recent_url': 'https://decisions.fca-caf.gc.ca/fca-caf/en/d/r/index.do?col=54'
    },
    'canada-gazette': {
        'name': 'Canada Gazette',
        'url': 'https://gazette.gc.ca/rp-pr/publications-eng.html',
        'description': 'Official newspaper of the Government of Canada.',
        'recent_url': 'https://gazette.gc.ca/rp-pr/publications-eng.html'
    },
    'ontario-courts': {
        'name': 'Ontario Courts',
        'url': 'https://www.ontariocourts.ca/decisions_index/en/',
        'description': 'Court decisions from Ontario.',
        'recent_url': 'https://www.ontariocourts.ca/decisions_index/en/'
    },
    'canlii': {
        'name': 'CanLII',
        'url': 'https://www.canlii.org/en/',
        'description': 'Canadian Legal Information Institute - comprehensive source of Canadian legal decisions.',
        'recent_url': 'https://www.canlii.org/en/blog/'
    },
    'bc-courts': {
        'name': 'British Columbia Courts',
        'url': 'https://www.bccourts.ca/index.aspx',
        'description': 'Court judgments from British Columbia.',
        'recent_url': 'https://www.bccourts.ca/supreme_court/recent_Judgments.aspx'
    },
    'alberta-courts': {
        'name': 'Alberta Courts',
        'url': 'https://www.albertacourts.ca/qb/resources/judgments',
        'description': 'Court judgments from Alberta.',
        'recent_url': 'https://www.albertacourts.ca/qb/resources/judgments'
    },
    'quebec-laws': {
        'name': 'Quebec Laws and Regulations',
        'url': 'http://legisquebec.gouv.qc.ca/en',
        'description': 'Laws and regulations of Quebec.',
        'recent_url': 'http://legisquebec.gouv.qc.ca/en/WhatsNew'
    },
    'soquij': {
        'name': 'SOQUIJ',
        'url': 'https://soquij.qc.ca/',
        'description': 'Société québécoise d\'information juridique - Quebec legal information.',
        'recent_url': 'https://soquij.qc.ca/fr/services-aux-citoyens/decisions-des-tribunaux'
    },
    'lsbc': {
        'name': 'Law Society of British Columbia',
        'url': 'https://www.lawsociety.bc.ca/',
        'description': 'Legal profession updates and regulation from BC.',
        'recent_url': 'https://www.lawsociety.bc.ca/newsroom/'
    },
    'lso': {
        'name': 'Law Society of Ontario',
        'url': 'https://lso.ca/',
        'description': 'Legal profession updates and regulation from Ontario.',
        'recent_url': 'https://lso.ca/news-events/latest-news'
    },
    'slaw': {
        'name': 'Slaw.ca',
        'url': 'http://www.slaw.ca/',
        'description': 'Canada\'s online legal magazine with analysis and commentary.',
        'recent_url': 'http://www.slaw.ca/'
    },
    'parliament-bills': {
        'name': 'Parliament of Canada - Bills',
        'url': 'https://www.parl.ca/legisinfo/en/bills',
        'description': 'Current and recent bills before Parliament.',
        'recent_url': 'https://www.parl.ca/legisinfo/en/bills/house?view=progress'
    },
    'parliament-proceedings': {
        'name': 'Parliament of Canada - Proceedings',
        'url': 'https://www.ourcommons.ca/en/sitting-calendar',
        'description': 'Parliamentary proceedings and debates.',
        'recent_url': 'https://www.ourcommons.ca/DocumentViewer/en/house/latest/hansard'
    },
    'senate-bills': {
        'name': 'Senate of Canada - Bills',
        'url': 'https://sencanada.ca/en/sencaplus/',
        'description': 'Senate bills and proceedings.',
        'recent_url': 'https://sencanada.ca/en/committees/current-bills/'
    },
    'royal-assent': {
        'name': 'Royal Assent - New Laws',
        'url': 'https://www.parl.ca/legisinfo/en/bills?view=royal-assent',
        'description': 'Recently enacted legislation through Royal Assent.',
        'recent_url': 'https://www.parl.ca/legisinfo/en/bills?view=royal-assent'
    },
    'order-in-council': {
        'name': 'Orders in Council',
        'url': 'https://orders-in-council.canada.ca/',
        'description': 'Government Orders in Council and regulatory changes.',
        'recent_url': 'https://orders-in-council.canada.ca/recent'
    },
    'steps-to-justice': {
        'name': 'Steps to Justice',
        'url': 'https://stepstojustice.ca/',
        'description': 'Legal information and self-help resources for Canadians.',
        'recent_url': 'https://stepstojustice.ca/legal-topic'
    },
    'indigenous-law': {
        'name': 'Indigenous Law Portal',
        'url': 'https://www.justice.gc.ca/eng/csj-sjc/ilp-pda/',
        'description': 'Indigenous law and legal developments.',
        'recent_url': 'https://www.justice.gc.ca/eng/csj-sjc/ilp-pda/index.html'
    },
    # Provincial Laws - All 10 Provinces
    'ontario-laws': {
        'name': 'Ontario Laws (e-Laws)',
        'url': 'https://www.ontario.ca/laws',
        'description': 'Ontario statutes and regulations.',
        'recent_url': 'https://www.ontario.ca/laws/recent'
    },
    'quebec-laws-statutes': {
        'name': 'Quebec Statutes and Regulations',
        'url': 'http://legisquebec.gouv.qc.ca/en',
        'description': 'Quebec provincial laws and regulations.',
        'recent_url': 'http://legisquebec.gouv.qc.ca/en/WhatsNew'
    },
    'bc-laws': {
        'name': 'BC Laws',
        'url': 'https://www.bclaws.gov.bc.ca/',
        'description': 'British Columbia statutes and regulations.',
        'recent_url': 'https://www.bclaws.gov.bc.ca/civix/content/complete/statreg/news'
    },
    'alberta-laws': {
        'name': 'Alberta Laws Online',
        'url': 'https://www.alberta.ca/alberta-laws-online.aspx',
        'description': 'Alberta statutes and regulations.',
        'recent_url': 'https://www.alberta.ca/alberta-laws-online.aspx'
    },
    'saskatchewan-laws': {
        'name': 'Saskatchewan Laws',
        'url': 'https://www.saskatchewan.ca/government/government-structure/acts-regulations-policies',
        'description': 'Saskatchewan statutes and regulations.',
        'recent_url': 'https://www.saskatchewan.ca/government/government-structure/acts-regulations-policies'
    },
    'manitoba-laws': {
        'name': 'Manitoba Laws',
        'url': 'https://web2.gov.mb.ca/laws/',
        'description': 'Manitoba statutes and regulations.',
        'recent_url': 'https://web2.gov.mb.ca/laws/statutes/recent.php'
    },
    'newfoundland-laws': {
        'name': 'Newfoundland and Labrador Laws',
        'url': 'https://www.assembly.nl.ca/legislation/',
        'description': 'Newfoundland and Labrador statutes.',
        'recent_url': 'https://www.assembly.nl.ca/legislation/sr/'
    },
    'nova-scotia-laws': {
        'name': 'Nova Scotia Laws',
        'url': 'https://nslegislature.ca/legislative-business/statutes-regulations',
        'description': 'Nova Scotia statutes and regulations.',
        'recent_url': 'https://nslegislature.ca/legislative-business/statutes-regulations'
    },
    'new-brunswick-laws': {
        'name': 'New Brunswick Laws',
        'url': 'https://laws.gnb.ca/en/',
        'description': 'New Brunswick statutes and regulations.',
        'recent_url': 'https://laws.gnb.ca/en/news'
    },
    'pei-laws': {
        'name': 'Prince Edward Island Laws',
        'url': 'https://www.princeedwardisland.ca/en/topic/statutes-and-regulations',
        'description': 'PEI statutes and regulations.',
        'recent_url': 'https://www.princeedwardisland.ca/en/topic/statutes-and-regulations'
    },
    # Territorial Laws
    'yukon-laws': {
        'name': 'Yukon Laws',
        'url': 'https://laws.yukon.ca/',
        'description': 'Yukon Territory statutes and regulations.',
        'recent_url': 'https://laws.yukon.ca/news'
    },
    'nwt-laws': {
        'name': 'Northwest Territories Laws',
        'url': 'https://www.justice.gov.nt.ca/en/legislation/',
        'description': 'NWT statutes and regulations.',
        'recent_url': 'https://www.justice.gov.nt.ca/en/legislation/'
    },
    'nunavut-laws': {
        'name': 'Nunavut Laws',
        'url': 'https://www.nunavutlegislation.ca/',
        'description': 'Nunavut Territory statutes and regulations.',
        'recent_url': 'https://www.nunavutlegislation.ca/'
    },
    # Major Municipal Bylaws - Top 20 Canadian Cities
    'toronto-bylaws': {
        'name': 'City of Toronto Bylaws',
        'url': 'https://www.toronto.ca/city-government/accountability-operations-customer-service/long-term-vision-plans-and-strategies/bylaws/',
        'description': 'Toronto municipal bylaws and regulations.',
        'recent_url': 'https://www.toronto.ca/city-government/accountability-operations-customer-service/long-term-vision-plans-and-strategies/bylaws/'
    },
    'montreal-bylaws': {
        'name': 'City of Montreal Bylaws',
        'url': 'https://ville.montreal.qc.ca/portal/page?_pageid=5798,85513711&_dad=portal&_schema=PORTAL',
        'description': 'Montreal municipal bylaws and regulations.',
        'recent_url': 'https://ville.montreal.qc.ca/portal/page?_pageid=5798,85513711&_dad=portal&_schema=PORTAL'
    },
    'vancouver-bylaws': {
        'name': 'City of Vancouver Bylaws',
        'url': 'https://vancouver.ca/your-government/bylaws.aspx',
        'description': 'Vancouver municipal bylaws.',
        'recent_url': 'https://vancouver.ca/your-government/bylaws.aspx'
    },
    'calgary-bylaws': {
        'name': 'City of Calgary Bylaws',
        'url': 'https://www.calgary.ca/content/www/en/home/our-government/bylaws.html',
        'description': 'Calgary municipal bylaws.',
        'recent_url': 'https://www.calgary.ca/content/www/en/home/our-government/bylaws.html'
    },
    'edmonton-bylaws': {
        'name': 'City of Edmonton Bylaws',
        'url': 'https://www.edmonton.ca/city_government/bylaws',
        'description': 'Edmonton municipal bylaws.',
        'recent_url': 'https://www.edmonton.ca/city_government/bylaws'
    },
    'ottawa-bylaws': {
        'name': 'City of Ottawa Bylaws',
        'url': 'https://ottawa.ca/en/city-hall/bylaws-and-regulatory-services',
        'description': 'Ottawa municipal bylaws.',
        'recent_url': 'https://ottawa.ca/en/city-hall/bylaws-and-regulatory-services'
    },
    'winnipeg-bylaws': {
        'name': 'City of Winnipeg Bylaws',
        'url': 'https://www.winnipeg.ca/clerks/bylaws/',
        'description': 'Winnipeg municipal bylaws.',
        'recent_url': 'https://www.winnipeg.ca/clerks/bylaws/'
    },
    'quebec-city-bylaws': {
        'name': 'Quebec City Bylaws',
        'url': 'https://www.ville.quebec.qc.ca/citoyens/reglements/',
        'description': 'Quebec City municipal bylaws.',
        'recent_url': 'https://www.ville.quebec.qc.ca/citoyens/reglements/'
    },
    'hamilton-bylaws': {
        'name': 'City of Hamilton Bylaws',
        'url': 'https://www.hamilton.ca/government-information/bylaws',
        'description': 'Hamilton municipal bylaws.',
        'recent_url': 'https://www.hamilton.ca/government-information/bylaws'
    },
    'kitchener-bylaws': {
        'name': 'City of Kitchener Bylaws',
        'url': 'https://www.kitchener.ca/en/city-services/bylaws.aspx',
        'description': 'Kitchener municipal bylaws.',
        'recent_url': 'https://www.kitchener.ca/en/city-services/bylaws.aspx'
    },
    'london-bylaws': {
        'name': 'City of London Bylaws',
        'url': 'https://london.ca/government/city-administration/city-bylaws-licences-permits',
        'description': 'London, Ontario municipal bylaws.',
        'recent_url': 'https://london.ca/government/city-administration/city-bylaws-licences-permits'
    },
    'halifax-bylaws': {
        'name': 'Halifax Regional Municipality Bylaws',
        'url': 'https://www.halifax.ca/city-hall/legislation-by-laws',
        'description': 'Halifax municipal bylaws.',
        'recent_url': 'https://www.halifax.ca/city-hall/legislation-by-laws'
    },
    'victoria-bylaws': {
        'name': 'City of Victoria Bylaws',
        'url': 'https://www.victoria.ca/EN/main/city/bylaws.html',
        'description': 'Victoria, BC municipal bylaws.',
        'recent_url': 'https://www.victoria.ca/EN/main/city/bylaws.html'
    },
    'saskatoon-bylaws': {
        'name': 'City of Saskatoon Bylaws',
        'url': 'https://www.saskatoon.ca/city-hall/bylaws',
        'description': 'Saskatoon municipal bylaws.',
        'recent_url': 'https://www.saskatoon.ca/city-hall/bylaws'
    },
    'regina-bylaws': {
        'name': 'City of Regina Bylaws',
        'url': 'https://www.regina.ca/bylaws-permits-licences/bylaws/',
        'description': 'Regina municipal bylaws.',
        'recent_url': 'https://www.regina.ca/bylaws-permits-licences/bylaws/'
    },
    'stjohns-bylaws': {
        'name': 'City of St. Johns Bylaws',
        'url': 'https://www.stjohns.ca/city-hall/legislation-and-bylaws',
        'description': 'St. Johns, NL municipal bylaws.',
        'recent_url': 'https://www.stjohns.ca/city-hall/legislation-and-bylaws'
    },
    # Regional and County Laws
    'york-region-bylaws': {
        'name': 'York Region Bylaws',
        'url': 'https://www.york.ca/wps/portal/yorkhome/yorkregion/yr/bylaws/',
        'description': 'York Region municipal bylaws.',
        'recent_url': 'https://www.york.ca/wps/portal/yorkhome/yorkregion/yr/bylaws/'
    },
    'peel-region-bylaws': {
        'name': 'Peel Region Bylaws',
        'url': 'https://www.peelregion.ca/bylaws/',
        'description': 'Peel Region municipal bylaws.',
        'recent_url': 'https://www.peelregion.ca/bylaws/'
    },
    'durham-region-bylaws': {
        'name': 'Durham Region Bylaws',
        'url': 'https://www.durham.ca/en/regional-government/bylaws.aspx',
        'description': 'Durham Region municipal bylaws.',
        'recent_url': 'https://www.durham.ca/en/regional-government/bylaws.aspx'
    },
    # Legal Information Portals
    'canlii-municipal': {
        'name': 'CanLII Municipal Law',
        'url': 'https://www.canlii.org/en/commentary/municipal-law/',
        'description': 'Municipal law decisions and commentary.',
        'recent_url': 'https://www.canlii.org/en/commentary/municipal-law/'
    },
    'municipal-world': {
        'name': 'Municipal World',
        'url': 'https://www.municipalworld.com/',
        'description': 'Municipal government news and legal updates.',
        'recent_url': 'https://www.municipalworld.com/news/'
    },
    # Criminal Law Sources
    'criminal-code': {
        'name': 'Criminal Code of Canada',
        'url': 'https://laws-lois.justice.gc.ca/eng/acts/C-46/',
        'description': 'Canadian Criminal Code and amendments.',
        'recent_url': 'https://laws-lois.justice.gc.ca/eng/acts/C-46/page-1.html'
    },
    'criminal-cases-scc': {
        'name': 'Supreme Court Criminal Cases',
        'url': 'https://www.scc-csc.ca/case-dossier/index-eng.aspx',
        'description': 'Supreme Court criminal law decisions.',
        'recent_url': 'https://www.scc-csc.ca/case-dossier/cb/index-eng.aspx'
    },
    'canlii-criminal': {
        'name': 'CanLII Criminal Law',
        'url': 'https://www.canlii.org/en/ca/scc/doc/recent-criminal.html',
        'description': 'Recent criminal law decisions across Canada.',
        'recent_url': 'https://www.canlii.org/en/ca/scc/doc/recent-criminal.html'
    },
    'youth-criminal-justice': {
        'name': 'Youth Criminal Justice Act',
        'url': 'https://laws-lois.justice.gc.ca/eng/acts/Y-1.5/',
        'description': 'Youth Criminal Justice Act and related provisions.',
        'recent_url': 'https://laws-lois.justice.gc.ca/eng/acts/Y-1.5/'
    },
    'controlled-drugs-substances': {
        'name': 'Controlled Drugs and Substances Act',
        'url': 'https://laws-lois.justice.gc.ca/eng/acts/C-38.8/',
        'description': 'Drug offences and controlled substances law.',
        'recent_url': 'https://laws-lois.justice.gc.ca/eng/acts/C-38.8/'
    },
    # Family Law Sources
    'divorce-act': {
        'name': 'Divorce Act',
        'url': 'https://laws-lois.justice.gc.ca/eng/acts/D-3.4/',
        'description': 'Federal Divorce Act and family law provisions.',
        'recent_url': 'https://laws-lois.justice.gc.ca/eng/acts/D-3.4/'
    },
    'family-orders-enforcement': {
        'name': 'Family Orders and Agreements Enforcement Assistance Act',
        'url': 'https://laws-lois.justice.gc.ca/eng/acts/F-1.4/',
        'description': 'Family support enforcement across Canada.',
        'recent_url': 'https://laws-lois.justice.gc.ca/eng/acts/F-1.4/'
    },
    'ontario-family-law': {
        'name': 'Ontario Family Law Act',
        'url': 'https://www.ontario.ca/laws/statute/90f3',
        'description': 'Ontario provincial family law statutes.',
        'recent_url': 'https://www.ontario.ca/laws/statute/90f3'
    },
    'ontario-children-law-reform': {
        'name': 'Ontario Children\'s Law Reform Act',
        'url': 'https://www.ontario.ca/laws/statute/90c12',
        'description': 'Ontario children\'s custody and access laws.',
        'recent_url': 'https://www.ontario.ca/laws/statute/90c12'
    },
    'bc-family-law': {
        'name': 'BC Family Law Act',
        'url': 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/11025_01',
        'description': 'British Columbia Family Law Act.',
        'recent_url': 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/11025_01'
    },
    'quebec-civil-code-family': {
        'name': 'Quebec Civil Code - Family Law',
        'url': 'http://legisquebec.gouv.qc.ca/en/ShowDoc/cs/CCQ-1991',
        'description': 'Quebec Civil Code family law provisions.',
        'recent_url': 'http://legisquebec.gouv.qc.ca/en/ShowDoc/cs/CCQ-1991'
    },
    'alberta-family-law': {
        'name': 'Alberta Family Law Act',
        'url': 'https://www.alberta.ca/family-law-act-overview.aspx',
        'description': 'Alberta family law statutes and regulations.',
        'recent_url': 'https://www.alberta.ca/family-law-act-overview.aspx'
    },
    'family-court-decisions': {
        'name': 'Family Court Decisions (CanLII)',
        'url': 'https://www.canlii.org/en/commentary/family-law/',
        'description': 'Recent family court decisions across Canada.',
        'recent_url': 'https://www.canlii.org/en/commentary/family-law/'
    },
    # Children\'s Aid Society (CAS) and Child Protection
    'child-family-services-act-ontario': {
        'name': 'Ontario Child, Youth and Family Services Act',
        'url': 'https://www.ontario.ca/laws/statute/17c14',
        'description': 'Ontario CAS and child protection laws.',
        'recent_url': 'https://www.ontario.ca/laws/statute/17c14'
    },
    'bc-child-family-community-service': {
        'name': 'BC Child, Family and Community Service Act',
        'url': 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96046_01',
        'description': 'BC child protection and family services.',
        'recent_url': 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96046_01'
    },
    'alberta-child-youth-family-enhancement': {
        'name': 'Alberta Child, Youth and Family Enhancement Act',
        'url': 'https://www.alberta.ca/child-intervention-legislation.aspx',
        'description': 'Alberta child protection and intervention.',
        'recent_url': 'https://www.alberta.ca/child-intervention-legislation.aspx'
    },
    'quebec-youth-protection': {
        'name': 'Quebec Youth Protection Act',
        'url': 'http://legisquebec.gouv.qc.ca/en/ShowDoc/cs/P-34.1',
        'description': 'Quebec DPJ and youth protection laws.',
        'recent_url': 'http://legisquebec.gouv.qc.ca/en/ShowDoc/cs/P-34.1'
    },
    'saskatchewan-child-family-services': {
        'name': 'Saskatchewan Child and Family Services Act',
        'url': 'https://www.saskatchewan.ca/residents/family-and-social-support/child-and-family-services',
        'description': 'Saskatchewan child protection legislation.',
        'recent_url': 'https://www.saskatchewan.ca/residents/family-and-social-support/child-and-family-services'
    },
    'manitoba-child-family-services': {
        'name': 'Manitoba Child and Family Services Act',
        'url': 'https://web2.gov.mb.ca/laws/statutes/ccsm/c080e.php',
        'description': 'Manitoba CFS and child protection.',
        'recent_url': 'https://web2.gov.mb.ca/laws/statutes/ccsm/c080e.php'
    },
    'nova-scotia-children-family-services': {
        'name': 'Nova Scotia Children and Family Services Act',
        'url': 'https://nslegislature.ca/sites/default/files/legc/statutes/children%20and%20family%20services.pdf',
        'description': 'Nova Scotia child protection laws.',
        'recent_url': 'https://nslegislature.ca/sites/default/files/legc/statutes/children%20and%20family%20services.pdf'
    },
    'new-brunswick-family-services': {
        'name': 'New Brunswick Family Services Act',
        'url': 'https://laws.gnb.ca/en/showdoc/cs/F-2.2',
        'description': 'New Brunswick child and family services.',
        'recent_url': 'https://laws.gnb.ca/en/showdoc/cs/F-2.2'
    },
    'pei-child-protection': {
        'name': 'PEI Child Protection Act',
        'url': 'https://www.princeedwardisland.ca/en/legislation/child-protection-act',
        'description': 'Prince Edward Island child protection.',
        'recent_url': 'https://www.princeedwardisland.ca/en/legislation/child-protection-act'
    },
    'newfoundland-children-youth-families': {
        'name': 'Newfoundland Children, Youth and Families Act',
        'url': 'https://www.assembly.nl.ca/legislation/sr/statutes/c12-1.htm',
        'description': 'Newfoundland child protection legislation.',
        'recent_url': 'https://www.assembly.nl.ca/legislation/sr/statutes/c12-1.htm'
    },
    # CAS-specific Resources
    'ontario-cas-websites': {
        'name': 'Ontario Association of Children\'s Aid Societies',
        'url': 'https://www.oacas.org/',
        'description': 'Ontario CAS policies and updates.',
        'recent_url': 'https://www.oacas.org/news-and-events/'
    },
    'child-welfare-information-gateway': {
        'name': 'Child Welfare Information Gateway',
        'url': 'https://www.childwelfare.gov/',
        'description': 'Child welfare policies and practices.',
        'recent_url': 'https://www.childwelfare.gov/news/'
    },
    # Specialized Legal Resources
    'family-law-central': {
        'name': 'Family Law Central',
        'url': 'https://www.familylawcentral.ca/',
        'description': 'Canadian family law resources and updates.',
        'recent_url': 'https://www.familylawcentral.ca/news/'
    },
    'criminal-lawyers-association': {
        'name': 'Criminal Lawyers\' Association',
        'url': 'https://www.criminallawyers.ca/',
        'description': 'Criminal law updates and legal advocacy.',
        'recent_url': 'https://www.criminallawyers.ca/news/'
    },
    'legal-aid-ontario': {
        'name': 'Legal Aid Ontario',
        'url': 'https://www.legalaid.on.ca/',
        'description': 'Legal aid services and family/criminal law resources.',
        'recent_url': 'https://www.legalaid.on.ca/news/'
    },
    'domestic-violence-resources': {
        'name': 'Domestic Violence Court Resources',
        'url': 'https://www.justice.gc.ca/eng/cj-jp/fv-vf/',
        'description': 'Federal domestic violence and family violence resources.',
        'recent_url': 'https://www.justice.gc.ca/eng/cj-jp/fv-vf/'
    }
}


class LegalDataScraper:
    """
    Main class for scraping legal information from various Canadian sources
    """

    def __init__(self, data_dir="data/legal_source_data"):
        """
        Initialize the scraper
        
        Args:
            data_dir (str): Directory to store scraped data
        """
        self.data_dir = data_dir
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        
        # Create source directories
        os.makedirs(data_dir, exist_ok=True)
        for source_id in LEGAL_SOURCES:
            os.makedirs(os.path.join(data_dir, source_id), exist_ok=True)
        
        # Cache for robots.txt
        self.robots_cache = {}
        
        # Rate limiting tracking
        self.last_request_time = {}

    def _respect_robots_txt(self, url):
        """
        Check if the URL is allowed by robots.txt
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if allowed, False if disallowed
        """
        parsed_url = urllib.parse.urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Check if we already have the robots parser in cache
        if base_url not in self.robots_cache:
            try:
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(f"{base_url}/robots.txt")
                rp.read()
                self.robots_cache[base_url] = rp
            except Exception as e:
                logger.warning(f"Error reading robots.txt for {base_url}: {e}")
                # Default to True (allowed) if we can't read robots.txt
                return True
                
        return self.robots_cache[base_url].can_fetch(USER_AGENT, url)

    def _rate_limit_request(self, url):
        """
        Apply rate limiting to avoid overwhelming servers
        
        Args:
            url (str): URL being requested
        """
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc
        
        current_time = time.time()
        if domain in self.last_request_time:
            elapsed = current_time - self.last_request_time[domain]
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            
            if elapsed < delay:
                time.sleep(delay - elapsed)
                
        self.last_request_time[domain] = time.time()

    def fetch_page(self, url):
        """
        Fetch a web page with appropriate rate limiting and error handling
        
        Args:
            url (str): URL to fetch
            
        Returns:
            str or None: HTML content of the page, or None on error
        """
        # Check if URL is allowed by robots.txt
        if not self._respect_robots_txt(url):
            logger.warning(f"URL disallowed by robots.txt: {url}")
            return None
        
        # Apply rate limiting
        self._rate_limit_request(url)
        
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_text_content(self, html, url=""):
        """
        Extract cleaned text content from HTML
        
        Args:
            html (str): HTML content
            url (str): Source URL for reference
            
        Returns:
            str: Cleaned text content
        """
        try:
            # Try trafilatura first (best for article content)
            extracted_text = trafilatura.extract(html)
            
            # Fall back to BeautifulSoup if trafilatura fails
            if not extracted_text:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script, style, and navigation elements
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.decompose()
                
                extracted_text = soup.get_text(separator='\n')
                
                # Clean up whitespace
                extracted_text = re.sub(r'\n+', '\n', extracted_text)
                extracted_text = re.sub(r'\s+', ' ', extracted_text)
                extracted_text = extracted_text.strip()
            
            return extracted_text
        except Exception as e:
            logger.error(f"Error extracting text from {url}: {e}")
            return ""

    def extract_legal_metadata(self, html, url, source_id):
        """
        Extract relevant metadata from legal documents
        
        Args:
            html (str): HTML content
            url (str): Source URL
            source_id (str): Identifier for the legal source
            
        Returns:
            dict: Extracted metadata
        """
        metadata = {
            'url': url,
            'source_id': source_id,
            'title': '',
            'date': '',
            'document_type': '',
            'citation': '',
            'scraped_at': datetime.datetime.now().isoformat()
        }
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title - look for the most prominent heading
        for heading in ['h1', 'h2', 'title']:
            if soup.find(heading):
                title_text = soup.find(heading).get_text().strip()
                if title_text:
                    metadata['title'] = title_text
                    break
        
        # Source-specific extraction logic
        if source_id == 'justice-laws':
            # Look for act title
            act_title = soup.find('span', class_='Title')
            if act_title:
                metadata['title'] = act_title.get_text().strip()
                
            # Look for date
            date_span = soup.find('span', class_='CurrentToDate')
            if date_span:
                date_text = date_span.get_text().strip()
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_text)
                if date_match:
                    metadata['date'] = date_match.group(0)
        
        elif source_id == 'scc':
            # Look for judgment title
            judgment_title = soup.find('h1', class_='judgmentTitle')
            if judgment_title:
                metadata['title'] = judgment_title.get_text().strip()
                
            # Look for citation
            citation = soup.find('div', class_='citation')
            if citation:
                metadata['citation'] = citation.get_text().strip()
                
            # Look for date
            date_div = soup.find('div', class_='dateDecision')
            if date_div:
                date_text = date_div.get_text().strip()
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_text)
                if date_match:
                    metadata['date'] = date_match.group(0)
        
        # If no specific date found, try to find a date pattern in the HTML
        if not metadata['date']:
            # Look for dates in common formats
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # ISO format
                r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'[A-Z][a-z]{2,8} \d{1,2}, \d{4}'  # Month Day, Year
            ]
            
            for pattern in date_patterns:
                matches = re.search(pattern, html)
                if matches:
                    metadata['date'] = matches.group(0)
                    break
        
        return metadata

    def save_document(self, content, metadata, source_id):
        """
        Save scraped document and metadata
        
        Args:
            content (str): Text content of the document
            metadata (dict): Document metadata
            source_id (str): Identifier for the legal source
            
        Returns:
            str: Path to saved document
        """
        # Create a unique identifier based on URL
        url_hash = hashlib.md5(metadata['url'].encode()).hexdigest()
        
        # Create source directory if it doesn't exist
        source_dir = os.path.join(self.data_dir, source_id)
        os.makedirs(source_dir, exist_ok=True)
        
        # Prepare filenames
        content_file = os.path.join(source_dir, f"{url_hash}.txt")
        metadata_file = os.path.join(source_dir, f"{url_hash}.json")
        
        # Save content
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Save metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return content_file

    def process_document(self, url, source_id):
        """
        Process a single document: fetch, extract content and metadata, and save
        
        Args:
            url (str): URL of the document
            source_id (str): Identifier for the legal source
            
        Returns:
            dict or None: Document metadata if successful, None otherwise
        """
        try:
            logger.info(f"Processing document: {url}")
            
            # Fetch page
            html = self.fetch_page(url)
            if not html:
                logger.warning(f"Failed to fetch document: {url}")
                return None
            
            # Extract content
            content = self.extract_text_content(html, url)
            if not content:
                logger.warning(f"Failed to extract content from document: {url}")
                return None
            
            # Extract metadata
            metadata = self.extract_legal_metadata(html, url, source_id)
            
            # Save document
            self.save_document(content, metadata, source_id)
            
            logger.info(f"Successfully processed document: {metadata['title']}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing document {url}: {e}")
            return None

    def discover_recent_documents(self, source_id):
        """
        Discover recent documents from a legal source
        
        Args:
            source_id (str): Identifier for the legal source
            
        Returns:
            list: List of document URLs
        """
        source = LEGAL_SOURCES.get(source_id)
        if not source:
            logger.error(f"Unknown source: {source_id}")
            return []
        
        recent_url = source.get('recent_url')
        if not recent_url:
            logger.error(f"No recent URL defined for source: {source_id}")
            return []
        
        # Fetch recent page
        html = self.fetch_page(recent_url)
        if not html:
            logger.warning(f"Failed to fetch recent page for {source_id}: {recent_url}")
            return []
        
        # Parse URLs
        soup = BeautifulSoup(html, 'html.parser')
        document_urls = []
        
        # Source-specific URL extraction
        if source_id == 'justice-laws':
            # Look for links to acts
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and '/acts/' in href and href.endswith('.html'):
                    full_url = urllib.parse.urljoin(recent_url, href)
                    document_urls.append(full_url)
        
        elif source_id == 'scc':
            # Look for links to judgments
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and '/decision/' in href and href.endswith('.html'):
                    full_url = urllib.parse.urljoin(recent_url, href)
                    document_urls.append(full_url)
        
        elif source_id in ['federal-court', 'federal-court-appeal']:
            # Look for links to decisions
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and '/decisions/' in href:
                    full_url = urllib.parse.urljoin(recent_url, href)
                    document_urls.append(full_url)
        
        elif source_id == 'canlii':
            # Look for links to decisions
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and '/t/' in href:
                    full_url = urllib.parse.urljoin(recent_url, href)
                    document_urls.append(full_url)
        
        # Default extraction for other sources
        else:
            # Get all links
            all_links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and not href.startswith(('#', 'javascript:', 'mailto:')):
                    full_url = urllib.parse.urljoin(recent_url, href)
                    # Only include links to the same domain
                    if urllib.parse.urlparse(full_url).netloc == urllib.parse.urlparse(recent_url).netloc:
                        all_links.append(full_url)
            
            # For default extraction, we take the first 10 unique links
            document_urls = list(set(all_links))[:10]
        
        logger.info(f"Discovered {len(document_urls)} document URLs for {source_id}")
        return document_urls[:20]  # Limit to 20 documents per source

    def scrape_source(self, source_id):
        """
        Scrape recent documents from a legal source
        
        Args:
            source_id (str): Identifier for the legal source
            
        Returns:
            list: List of processed document metadata
        """
        logger.info(f"Scraping source: {source_id}")
        
        if source_id not in LEGAL_SOURCES:
            logger.error(f"Unknown source: {source_id}")
            return []
        
        # Discover recent document URLs
        document_urls = self.discover_recent_documents(source_id)
        
        # Process each document
        results = []
        for url in document_urls:
            metadata = self.process_document(url, source_id)
            if metadata:
                results.append(metadata)
                
        logger.info(f"Scraped {len(results)} documents from {source_id}")
        return results

    def scrape_all_sources(self):
        """
        Scrape recent documents from all configured legal sources
        
        Returns:
            dict: Results organized by source
        """
        results = {}
        
        for source_id in LEGAL_SOURCES:
            try:
                source_results = self.scrape_source(source_id)
                results[source_id] = source_results
            except Exception as e:
                logger.error(f"Error scraping source {source_id}: {e}")
                results[source_id] = []
        
        return results

    def run_scheduled_scrape(self):
        """
        Run a scheduled scrape of all sources and report results
        
        Returns:
            dict: Summary of scraping results
        """
        start_time = time.time()
        
        logger.info("Starting scheduled legal data scrape")
        
        # Run the scrape
        results = self.scrape_all_sources()
        
        # Calculate summary
        total_documents = sum(len(docs) for docs in results.values())
        sources_scraped = sum(1 for docs in results.values() if len(docs) > 0)
        documents_by_source = {source_id: len(docs) for source_id, docs in results.items()}
        
        end_time = time.time()
        duration_seconds = end_time - start_time
        
        summary = {
            'started_at': datetime.datetime.fromtimestamp(start_time).isoformat(),
            'completed_at': datetime.datetime.fromtimestamp(end_time).isoformat(),
            'duration_seconds': duration_seconds,
            'total_documents': total_documents,
            'sources_scraped': sources_scraped,
            'documents_by_source': documents_by_source
        }
        
        logger.info(f"Scheduled scrape completed in {duration_seconds:.2f} seconds")
        logger.info(f"Scraped {total_documents} documents from {sources_scraped} sources")
        
        return summary

    def run_targeted_scrape(self, source_ids):
        """
        Run a targeted scrape of specific sources (for Parliament bills, Royal Assent, etc.)
        
        Args:
            source_ids (list): List of source IDs to scrape
            
        Returns:
            dict: Summary of scraping results
        """
        start_time = time.time()
        
        logger.info(f"Starting targeted scrape of sources: {', '.join(source_ids)}")
        
        results = {}
        
        for source_id in source_ids:
            if source_id in LEGAL_SOURCES:
                try:
                    logger.info(f"Scraping {LEGAL_SOURCES[source_id]['name']}")
                    documents = self.scrape_source(source_id)
                    results[source_id] = documents
                    logger.info(f"Scraped {len(documents)} documents from {source_id}")
                except Exception as e:
                    logger.error(f"Error scraping {source_id}: {e}")
                    results[source_id] = []
            else:
                logger.warning(f"Unknown source ID: {source_id}")
                results[source_id] = []
        
        # Calculate summary
        total_documents = sum(len(docs) for docs in results.values())
        sources_scraped = sum(1 for docs in results.values() if len(docs) > 0)
        documents_by_source = {source_id: len(docs) for source_id, docs in results.items()}
        
        end_time = time.time()
        duration_seconds = end_time - start_time
        
        summary = {
            'started_at': datetime.datetime.fromtimestamp(start_time).isoformat(),
            'completed_at': datetime.datetime.fromtimestamp(end_time).isoformat(),
            'duration_seconds': duration_seconds,
            'total_documents': total_documents,
            'sources_scraped': sources_scraped,
            'documents_by_source': documents_by_source,
            'targeted_sources': source_ids
        }
        
        logger.info(f"Targeted scrape completed in {duration_seconds:.2f} seconds")
        logger.info(f"Scraped {total_documents} documents from {sources_scraped} sources")
        
        return summary


def run_one_time_scrape():
    """
    Run a one-time scrape of all legal sources
    """
    data_dir = "data/legal_source_data"
    os.makedirs(data_dir, exist_ok=True)
    
    scraper = LegalDataScraper(data_dir=data_dir)
    summary = scraper.run_scheduled_scrape()
    
    print(f"Scrape completed in {summary['duration_seconds']:.2f} seconds")
    print(f"Scraped {summary['total_documents']} documents from {summary['sources_scraped']} sources")
    
    for source_id, count in summary['documents_by_source'].items():
        if count > 0:
            print(f"  {LEGAL_SOURCES[source_id]['name']}: {count} documents")


def find_documents_by_keyword(keyword, data_dir="data/legal_source_data", max_results=10):
    """
    Search for documents containing a specific keyword
    
    Args:
        keyword (str): Keyword to search for
        data_dir (str): Directory containing scraped documents
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of matching documents with metadata
    """
    results = []
    keyword = keyword.lower()
    
    # Recursively find all .txt files
    for txt_file in Path(data_dir).glob('**/*.txt'):
        # Check if we've reached the maximum results
        if len(results) >= max_results:
            break
            
        # Get corresponding metadata file
        metadata_file = txt_file.with_suffix('.json')
        if not metadata_file.exists():
            continue
            
        try:
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            # Load content
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                
            # Check if keyword is in content
            if keyword in content:
                # Get a snippet around the keyword
                snippet = get_text_snippet(content, keyword)
                
                # Add to results
                result = {
                    'title': metadata.get('title', 'Untitled'),
                    'url': metadata.get('url', ''),
                    'date': metadata.get('date', ''),
                    'source_id': metadata.get('source_id', ''),
                    'snippet': snippet
                }
                results.append(result)
                
        except Exception as e:
            logger.error(f"Error searching document {txt_file}: {e}")
    
    return results


def get_text_snippet(text, keyword, context_size=100):
    """
    Get a text snippet around a keyword
    
    Args:
        text (str): Full text content
        keyword (str): Keyword to find
        context_size (int): Number of characters around the keyword
        
    Returns:
        str: Text snippet
    """
    # Find the first occurrence of the keyword
    pos = text.find(keyword)
    if pos == -1:
        return ""
        
    # Calculate start and end positions
    start = max(0, pos - context_size)
    end = min(len(text), pos + len(keyword) + context_size)
    
    # Extract the snippet
    snippet = text[start:end]
    
    # Add ellipsis if needed
    if start > 0:
        snippet = '...' + snippet
    if end < len(text):
        snippet = snippet + '...'
        
    # Highlight the keyword
    snippet = snippet.replace(keyword, f"**{keyword}**")
    
    return snippet


def analyze_source_updates(data_dir="data/legal_source_data", days=7):
    """
    Analyze recent updates from legal sources
    
    Args:
        data_dir (str): Directory containing scraped documents
        days (int): Number of days to look back
        
    Returns:
        dict: Analysis of recent updates by source
    """
    analysis = {}
    now = datetime.datetime.now()
    cutoff_date = now - datetime.timedelta(days=days)
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        return {source_id: {'documents': []} for source_id in LEGAL_SOURCES}
    
    # Process each source
    for source_id in LEGAL_SOURCES:
        source_dir = os.path.join(data_dir, source_id)
        if not os.path.exists(source_dir):
            analysis[source_id] = {
                'documents': []
            }
            continue
            
        # Get all metadata files
        metadata_files = list(Path(source_dir).glob('*.json'))
        
        # Parse metadata files
        documents = []
        
        for metadata_file in metadata_files:
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                # Get and parse scraped_at datetime
                scraped_at = metadata.get('scraped_at')
                if scraped_at:
                    try:
                        scraped_dt = datetime.datetime.fromisoformat(scraped_at)
                        
                        # Add to documents if within cutoff
                        if scraped_dt >= cutoff_date:
                            documents.append({
                                'title': metadata.get('title', 'Untitled'),
                                'date': metadata.get('date', 'Unknown'),
                                'url': metadata.get('url', ''),
                                'description': metadata.get('document_type', '')
                            })
                    except (ValueError, TypeError):
                        pass
                        
            except Exception as e:
                logger.error(f"Error analyzing metadata file {metadata_file}: {e}")
        
        
        # Sort documents by date (newest first)
        documents.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Store results
        analysis[source_id] = {
            'documents': documents[:5]  # Limit to 5 most recent
        }
    
    return analysis