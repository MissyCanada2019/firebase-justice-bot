"""
Multilingual Support System for SmartDispute.ai
Supports French, Punjabi, Arabic, and Simplified Chinese as requested
"""

import os
import json
import logging
from flask import request, session

# Language configuration
SUPPORTED_LANGUAGES = {
    'en': {'name': 'English', 'flag': '🇨🇦', 'rtl': False},
    'fr': {'name': 'Français', 'flag': '🇫🇷', 'rtl': False},
    'pa': {'name': 'ਪੰਜਾਬੀ', 'flag': '🇮🇳', 'rtl': False},
    'ar': {'name': 'العربية', 'flag': '🇸🇦', 'rtl': True},
    'zh': {'name': '简体中文', 'flag': '🇨🇳', 'rtl': False}
}

class MultilingualManager:
    def __init__(self):
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translation files for all supported languages"""
        translations_dir = 'translations'
        os.makedirs(translations_dir, exist_ok=True)
        
        for lang_code in SUPPORTED_LANGUAGES.keys():
            translation_file = os.path.join(translations_dir, f'{lang_code}.json')
            if os.path.exists(translation_file):
                try:
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    logging.warning(f"Could not load translations for {lang_code}: {e}")
                    self.translations[lang_code] = {}
            else:
                # Create default translation file
                self.create_default_translations(lang_code, translation_file)
    
    def create_default_translations(self, lang_code, file_path):
        """Create default translation files with key legal terms"""
        if lang_code == 'en':
            translations = {
                "app_name": "SmartDispute.ai",
                "tagline": "Empowering Canadians through Justice",
                "charter_protection": "Protected by the Canadian Charter of Rights and Freedoms",
                "legal_categories": {
                    "family_law": "Family Law",
                    "housing_law": "Housing & Tenant Law", 
                    "employment_law": "Employment Law",
                    "criminal_law": "Criminal Law",
                    "human_rights": "Human Rights"
                },
                "forms": {
                    "t2_application": "T2 Application (Tenant Rights)",
                    "t6_application": "T6 Application (Maintenance & Repairs)",
                    "hrto_application": "Human Rights Tribunal Application"
                },
                "dashboard": {
                    "upload_documents": "Upload Documents",
                    "case_dashboard": "Case Dashboard",
                    "merit_score": "Merit Score",
                    "legal_analysis": "Legal Analysis",
                    "recommended_actions": "Recommended Actions"
                },
                "legal_disclaimer": "This provides legal information, not legal advice. We are not lawyers."
            }
        elif lang_code == 'fr':
            translations = {
                "app_name": "SmartDispute.ai",
                "tagline": "Autonomiser les Canadiens par la Justice",
                "charter_protection": "Protégé par la Charte canadienne des droits et libertés",
                "legal_categories": {
                    "family_law": "Droit de la famille",
                    "housing_law": "Droit du logement et des locataires",
                    "employment_law": "Droit du travail",
                    "criminal_law": "Droit pénal",
                    "human_rights": "Droits de la personne"
                },
                "forms": {
                    "t2_application": "Demande T2 (Droits des locataires)",
                    "t6_application": "Demande T6 (Entretien et réparations)",
                    "hrto_application": "Demande au Tribunal des droits de la personne"
                },
                "dashboard": {
                    "upload_documents": "Télécharger des documents",
                    "case_dashboard": "Tableau de bord des dossiers",
                    "merit_score": "Score de mérite",
                    "legal_analysis": "Analyse juridique",
                    "recommended_actions": "Actions recommandées"
                },
                "legal_disclaimer": "Ceci fournit des informations juridiques, pas de conseils juridiques. Nous ne sommes pas des avocats."
            }
        elif lang_code == 'pa':
            translations = {
                "app_name": "SmartDispute.ai",
                "tagline": "ਨਿਆਂ ਰਾਹੀਂ ਕੈਨੇਡੀਅਨਾਂ ਨੂੰ ਸ਼ਕਤੀ ਦੇਣਾ",
                "charter_protection": "ਕੈਨੇਡੀਅਨ ਚਾਰਟਰ ਆਫ਼ ਰਾਈਟਸ ਐਂਡ ਫਰੀਡਮਜ਼ ਦੁਆਰਾ ਸੁਰੱਖਿਅਤ",
                "legal_categories": {
                    "family_law": "ਪਰਿਵਾਰਕ ਕਾਨੂੰਨ",
                    "housing_law": "ਹਾਊਸਿੰਗ ਅਤੇ ਕਿਰਾਏਦਾਰ ਕਾਨੂੰਨ",
                    "employment_law": "ਰੁਜ਼ਗਾਰ ਕਾਨੂੰਨ",
                    "criminal_law": "ਫੌਜਦਾਰੀ ਕਾਨੂੰਨ",
                    "human_rights": "ਮਨੁੱਖੀ ਅਧਿਕਾਰ"
                },
                "forms": {
                    "t2_application": "T2 ਅਰਜ਼ੀ (ਕਿਰਾਏਦਾਰ ਅਧਿਕਾਰ)",
                    "t6_application": "T6 ਅਰਜ਼ੀ (ਰੱਖ-ਰਖਾਅ ਅਤੇ ਮੁਰੰਮਤ)",
                    "hrto_application": "ਮਨੁੱਖੀ ਅਧਿਕਾਰ ਟ੍ਰਿਬਿਊਨਲ ਅਰਜ਼ੀ"
                },
                "dashboard": {
                    "upload_documents": "ਦਸਤਾਵੇਜ਼ ਅੱਪਲੋਡ ਕਰੋ",
                    "case_dashboard": "ਕੇਸ ਡੈਸ਼ਬੋਰਡ",
                    "merit_score": "ਮੈਰਿਟ ਸਕੋਰ",
                    "legal_analysis": "ਕਾਨੂੰਨੀ ਵਿਸ਼ਲੇਸ਼ਣ",
                    "recommended_actions": "ਸਿਫਾਰਸ਼ ਕੀਤੀਆਂ ਕਾਰਵਾਈਆਂ"
                },
                "legal_disclaimer": "ਇਹ ਕਾਨੂੰਨੀ ਜਾਣਕਾਰੀ ਪ੍ਰਦਾਨ ਕਰਦਾ ਹੈ, ਕਾਨੂੰਨੀ ਸਲਾਹ ਨਹੀਂ। ਅਸੀਂ ਵਕੀਲ ਨਹੀਂ ਹਾਂ।"
            }
        elif lang_code == 'ar':
            translations = {
                "app_name": "SmartDispute.ai",
                "tagline": "تمكين الكنديين من خلال العدالة",
                "charter_protection": "محمي بميثاق الحقوق والحريات الكندي",
                "legal_categories": {
                    "family_law": "قانون الأسرة",
                    "housing_law": "قانون الإسكان والمستأجرين",
                    "employment_law": "قانون العمل",
                    "criminal_law": "القانون الجنائي",
                    "human_rights": "حقوق الإنسان"
                },
                "forms": {
                    "t2_application": "طلب T2 (حقوق المستأجرين)",
                    "t6_application": "طلب T6 (الصيانة والإصلاحات)",
                    "hrto_application": "طلب محكمة حقوق الإنسان"
                },
                "dashboard": {
                    "upload_documents": "رفع المستندات",
                    "case_dashboard": "لوحة تحكم القضية",
                    "merit_score": "نقاط الجدارة",
                    "legal_analysis": "التحليل القانوني",
                    "recommended_actions": "الإجراءات الموصى بها"
                },
                "legal_disclaimer": "هذا يوفر معلومات قانونية، وليس استشارة قانونية. نحن لسنا محامين."
            }
        elif lang_code == 'zh':
            translations = {
                "app_name": "SmartDispute.ai",
                "tagline": "通过正义赋权加拿大人",
                "charter_protection": "受加拿大权利与自由宪章保护",
                "legal_categories": {
                    "family_law": "家庭法",
                    "housing_law": "住房和租户法",
                    "employment_law": "雇佣法",
                    "criminal_law": "刑法",
                    "human_rights": "人权"
                },
                "forms": {
                    "t2_application": "T2申请（租户权利）",
                    "t6_application": "T6申请（维护和维修）",
                    "hrto_application": "人权法庭申请"
                },
                "dashboard": {
                    "upload_documents": "上传文档",
                    "case_dashboard": "案例仪表板",
                    "merit_score": "案情评分",
                    "legal_analysis": "法律分析",
                    "recommended_actions": "推荐行动"
                },
                "legal_disclaimer": "这提供法律信息，不是法律建议。我们不是律师。"
            }
        
        self.translations[lang_code] = translations
        
        # Save to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Could not save translations for {lang_code}: {e}")

    def get_user_language(self):
        """Determine user's preferred language"""
        # Check session first
        if 'language' in session:
            return session['language']
        
        # Check Accept-Language header
        if request:
            accept_languages = request.headers.get('Accept-Language', '')
            for lang in accept_languages.split(','):
                lang_code = lang.split(';')[0].split('-')[0].strip()
                if lang_code in SUPPORTED_LANGUAGES:
                    return lang_code
        
        # Default to English
        return 'en'
    
    def set_user_language(self, lang_code):
        """Set user's language preference"""
        if lang_code in SUPPORTED_LANGUAGES:
            session['language'] = lang_code
            return True
        return False
    
    def translate(self, key, lang_code=None):
        """Get translation for a key"""
        if not lang_code:
            lang_code = self.get_user_language()
        
        if lang_code not in self.translations:
            lang_code = 'en'  # Fallback to English
        
        # Navigate nested keys (e.g., "dashboard.upload_documents")
        keys = key.split('.')
        value = self.translations[lang_code]
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            # Fallback to English if key not found
            if lang_code != 'en':
                return self.translate(key, 'en')
            return key  # Return key if no translation found
    
    def get_language_info(self, lang_code):
        """Get language metadata"""
        return SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES['en'])

# Global instance
multilingual_manager = MultilingualManager()

def init_multilingual_support(app):
    """Initialize multilingual support with Flask app"""
    @app.context_processor
    def inject_language_functions():
        return {
            'translate': multilingual_manager.translate,
            'current_language': multilingual_manager.get_user_language(),
            'supported_languages': SUPPORTED_LANGUAGES,
            'get_language_info': multilingual_manager.get_language_info
        }
    
    @app.route('/set-language/<lang_code>')
    def set_language(lang_code):
        """Set user language preference"""
        from flask import redirect, request as flask_request
        if multilingual_manager.set_user_language(lang_code):
            # Redirect back to referring page
            return redirect(flask_request.referrer or '/')
        return redirect('/')
    
    app.logger.info("Multilingual support initialized")
    return multilingual_manager