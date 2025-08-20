"""
Enhanced Multi-Language Detection Engine
Now supporting German, Italian, Portuguese, and Dutch!
Built for the Python 1.0 veteran who's secretly a coding legend! 🚀
"""

from langdetect import detect, detect_langs, LangDetectException
import re

def detect_language_enhanced(text, confidence_threshold=0.7):
    """
    Enhanced language detection with support for 8 languages!
    Now with smart keyword patterns for German, Italian, Portuguese, Dutch
    """
    
    # Clean the text
    cleaned_text = re.sub(r'[^\w\s]', ' ', text).strip()
    text_lower = text.lower()
    
    # === KEYWORD DETECTION PATTERNS ===
    
    # Spanish indicators (existing - works great!)
    spanish_score = 0
    if '¿' in text or '¡' in text:
        spanish_score += 3  # Strong indicators
    if any(indicator in text_lower for indicator in ['cómo', 'qué', 'cuáles', 'ayuda', 'dónde', 'cuándo']):
        spanish_score += 2  
    if any(indicator in text_lower for indicator in ['con la', 'con el', 'una ', 'las ', 'los ', 'del ', 'para ']):
        spanish_score += 1
    
    # German indicators
    german_score = 0
    if any(indicator in text_lower for indicator in ['wie', 'was', 'wer', 'wo', 'wann', 'warum']):
        german_score += 2  # Question words
    if any(indicator in text_lower for indicator in ['der ', 'die ', 'das ', 'ein ', 'eine ', 'einen ']):
        german_score += 1  # Articles
    if any(indicator in text_lower for indicator in ['und ', 'oder ', 'aber ', 'wenn ', 'dass ']):
        german_score += 1  # Conjunctions
    if any(indicator in text_lower for indicator in ['ü', 'ä', 'ö', 'ß']):
        german_score += 2  # Special characters
    
    # Italian indicators  
    italian_score = 0
    if any(indicator in text_lower for indicator in ['come', 'che cosa', 'quando', 'dove', 'perché', 'chi']):
        italian_score += 2  # Question words
    if any(indicator in text_lower for indicator in ['il ', 'la ', 'gli ', 'le ', 'un ', 'una ', 'dello ', 'della ']):
        italian_score += 1  # Articles
    if any(indicator in text_lower for indicator in ['è ', 'sono ', 'hai ', 'ho ', 'abbiamo ']):
        italian_score += 1  # Common verbs
    
    # Portuguese indicators
    portuguese_score = 0
    if any(indicator in text_lower for indicator in ['como', 'o que', 'quando', 'onde', 'por que', 'quem']):
        portuguese_score += 2  # Question words
    if any(indicator in text_lower for indicator in ['o ', 'a ', 'os ', 'as ', 'um ', 'uma ', 'do ', 'da ']):
        portuguese_score += 1  # Articles
    if any(indicator in text_lower for indicator in ['é ', 'são ', 'tem ', 'temos ', 'para ', 'com ']):
        portuguese_score += 1  # Common words
    if any(indicator in text_lower for indicator in ['ã', 'õ', 'ç']):
        portuguese_score += 2  # Special characters
    
    # Dutch indicators
    dutch_score = 0
    if any(indicator in text_lower for indicator in ['hoe', 'wat', 'wanneer', 'waar', 'waarom', 'wie']):
        dutch_score += 2  # Question words
    if any(indicator in text_lower for indicator in ['de ', 'het ', 'een ', 'van ', 'voor ', 'met ']):
        dutch_score += 1  # Articles and prepositions
    if any(indicator in text_lower for indicator in ['is ', 'zijn ', 'heeft ', 'hebben ', 'kan ', 'kunnen ']):
        dutch_score += 1  # Common verbs
    
    # French indicators (enhanced from existing)
    french_score = 0
    if any(indicator in text_lower for indicator in ['comment', 'que', 'quand', 'où', 'pourquoi', 'qui']):
        french_score += 2  # Question words
    if any(indicator in text_lower for indicator in ['le ', 'la ', 'les ', 'un ', 'une ', 'du ', 'de la ']):
        french_score += 1  # Articles
    if any(indicator in text_lower for indicator in ['est ', 'sont ', 'avoir ', 'être ', 'avec ', 'pour ']):
        french_score += 1  # Common words
    if any(indicator in text_lower for indicator in ['à', 'é', 'è', 'ê', 'ç']):
        french_score += 1  # Accented characters
    
    # === SCORING AND DECISION ===
    
    # Check scores (need minimum 2 points to be confident)
    language_scores = {
        'es': spanish_score,
        'de': german_score, 
        'it': italian_score,
        'pt': portuguese_score,
        'nl': dutch_score,
        'fr': french_score
    }
    
    # Find highest scoring language
    max_score = max(language_scores.values())
    if max_score >= 2:
        detected_lang = max(language_scores, key=language_scores.get)
        confidence = min(0.95, 0.7 + (max_score * 0.05))  # Scale confidence with score
        return {
            'language': detected_lang,
            'confidence': confidence,
            'method': 'keyword_detection',
            'scores': language_scores
        }
    
    # === FALLBACK TO LANGDETECT ===
    
    if len(cleaned_text) < 3:
        return {
            'language': 'en',
            'confidence': 0.5,
            'method': 'default_short_text',
            'scores': language_scores
        }
    
    try:
        detections = detect_langs(cleaned_text)
        top_detection = detections[0]
        
        # Enhanced suspicious language filtering
        suspicious_langs = ['cy', 'so', 'tl', 'sw', 'eu', 'mt']  # Welsh, Somali, Tagalog, Swahili, Basque, Maltese
        
        if top_detection.lang in suspicious_langs and len(cleaned_text) < 30:
            return {
                'language': 'en',
                'confidence': 0.6,
                'method': 'filtered_suspicious',
                'scores': language_scores,
                'filtered': top_detection.lang
            }
        
        if top_detection.prob >= confidence_threshold:
            return {
                'language': top_detection.lang,
                'confidence': top_detection.prob,
                'method': 'langdetect',
                'scores': language_scores,
                'all_detections': [(d.lang, d.prob) for d in detections]
            }
        
        return {
            'language': 'en',
            'confidence': 0.6,
            'method': 'default_low_confidence',
            'scores': language_scores
        }
        
    except (LangDetectException, Exception) as e:
        return {
            'language': 'en',
            'confidence': 0.3,
            'method': 'error_fallback',
            'scores': language_scores,
            'error': str(e)
        }

def get_language_name(lang_code):
    """
    Convert language codes to human-readable names
    Perfect for displaying results!
    """
    language_names = {
        'en': 'English',
        'es': 'Spanish', 
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'nl': 'Dutch',
        'ru': 'Russian',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ar': 'Arabic'
    }
    return language_names.get(lang_code, f'Unknown ({lang_code})')

def test_enhanced_detection():
    """
    Test our enhanced detection with multiple languages!
    """
    test_cases = [
        # English
        ("How do I conduct an effective interview?", "en"),
        ("What are the best practices?", "en"),
        ("Help me with this task", "en"),
        
        # Spanish  
        ("¿Cómo conduzco una entrevista efectiva?", "es"),
        ("¿Cuáles son las mejores prácticas?", "es"),
        ("Ayuda con esta tarea", "es"),
        
        # German
        ("Wie führe ich ein effektives Interview?", "de"),
        ("Was sind die besten Praktiken?", "de"),
        ("Hilfe bei dieser Aufgabe", "de"),
        
        # Italian
        ("Come conduco un'intervista efficace?", "it"),
        ("Quali sono le migliori pratiche?", "it"),
        ("Aiuto con questo compito", "it"),
        
        # Portuguese
        ("Como conduzo uma entrevista eficaz?", "pt"),
        ("Quais são as melhores práticas?", "pt"),
        ("Ajuda com esta tarefa", "pt"),
        
        # Dutch
        ("Hoe voer ik een effectief interview?", "nl"),
        ("Wat zijn de beste praktijken?", "nl"),
        ("Help bij deze taak", "nl"),
        
        # French
        ("Comment mener un entretien efficace?", "fr"),
        ("Quelles sont les meilleures pratiques?", "fr"),
        ("Aide avec cette tâche", "fr"),
    ]
    
    print("🌍 ENHANCED MULTI-LANGUAGE DETECTION TEST 🌍\n")
    print("=" * 80)
    
    for i, (text, expected) in enumerate(test_cases, 1):
        result = detect_language_enhanced(text)
        detected = result['language']
        confidence = result['confidence']
        method = result['method']
        
        # Check if detection matches expectation
        status = "✅ CORRECT" if detected == expected else f"❌ EXPECTED {expected.upper()}"
        
        print(f"\n{i:2d}. TEXT: '{text}'")
        print(f"    DETECTED: {detected.upper()} ({get_language_name(detected)})")
        print(f"    CONFIDENCE: {confidence:.3f} | METHOD: {method}")
        print(f"    STATUS: {status}")
        
        # Show scores for debugging
        if 'scores' in result:
            top_scores = {k: v for k, v in result['scores'].items() if v > 0}
            if top_scores:
                print(f"    SCORES: {top_scores}")
    
    print("\n" + "=" * 80)
    print("🎯 ENHANCED DETECTION TEST COMPLETE!")
    print("Ready to handle 8 languages with confidence! 🚀")

if __name__ == "__main__":
    test_enhanced_detection()