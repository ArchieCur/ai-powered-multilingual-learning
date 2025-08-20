import google.generativeai as genai
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv
import os
from langdetect import detect, detect_langs, LangDetectException
import re

# --- Enhanced multilingual question engine ---

def detect_language(text, confidence_threshold=0.7):
    """
    Detect language with smart fallbacks for maximum reliability
    """
    # Clean the text
    cleaned_text = re.sub(r'[^\w\s]', ' ', text).strip()
    
    # Smart word-based detection for short text
    spanish_score = 0
    text_lower = text.lower()
    
    # Check for obvious Spanish indicators
    if '¿' in text or '¡' in text:
        spanish_score += 2
    if any(indicator in text_lower for indicator in ['cómo', 'qué', 'cuáles', 'ayuda']):
        spanish_score += 2  
    if any(indicator in text_lower for indicator in ['con la', 'con el', 'una ', 'las ']):
        spanish_score += 1
        
    if spanish_score >= 2:
        return {
            'language': 'es',
            'confidence': 0.9,
            'method': 'keyword_detection'
        }
    
    if len(cleaned_text) < 3:
        return {
            'language': 'en',
            'confidence': 0.5,
            'method': 'default'
        }
    
    try:
        # Primary: langdetect (Google's library)
        detections = detect_langs(cleaned_text)
        top_detection = detections[0]
        
        # Smart filtering for common false positives
        suspicious_langs = ['cy', 'so', 'nl', 'tl']  # Welsh, Somali, Dutch, Tagalog
        
        if top_detection.lang in suspicious_langs and len(cleaned_text) < 20:
            return {
                'language': 'en',
                'confidence': 0.6,
                'method': 'filtered_default'
            }
        
        if top_detection.prob >= confidence_threshold:
            return {
                'language': top_detection.lang,
                'confidence': top_detection.prob,
                'method': 'langdetect'
            }
        
        # Fallback to English
        return {
            'language': 'en',
            'confidence': 0.6,
            'method': 'default_fallback'
        }
        
    except (LangDetectException, Exception):
        return {
            'language': 'en',
            'confidence': 0.3,
            'method': 'error_fallback'
        }

def translate_with_gemini(text, target_language, api_key):
    """
    Use Gemini for high-quality translation (FREE with your existing API key!)
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Language mapping
    lang_names = {
        'es': 'Spanish',
        'en': 'English', 
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese'
    }
    
    target_lang_name = lang_names.get(target_language, 'English')
    
    translation_prompt = f"""
Translate the following text to {target_lang_name}. 
Provide ONLY the translation, no explanations or additional text.

Text to translate: {text}

Translation:"""
    
    try:
        response = model.generate_content(translation_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original if translation fails

def get_answer(user_question):
    """
    Enhanced multilingual RAG engine!
    Takes a user's question in ANY language, performs RAG search, and returns answer in original language.
    """
    # --- SETUP ---
    load_dotenv('vector_store/.env')
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: Google API Key not found."
    
    print(f"Debug: API key starts with: {api_key[:10]}...")
    
    # --- STEP 1: DETECT LANGUAGE ---
    print(f"🌍 Detecting language for: '{user_question}'")
    lang_detection = detect_language(user_question)
    detected_lang = lang_detection['language']
    confidence = lang_detection['confidence']
    method = lang_detection['method']
    
    print(f"🎯 Detected: {detected_lang.upper()} (confidence: {confidence:.2f}, method: {method})")
    
    # --- STEP 2: TRANSLATE TO ENGLISH IF NEEDED ---
    search_question = user_question
    if detected_lang != 'en':
        print(f"🔄 Translating question to English for search...")
        search_question = translate_with_gemini(user_question, 'en', api_key)
        print(f"📝 Search question: '{search_question}'")
    
    # --- STEP 3: EXISTING RAG PROCESS ---
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    VECTOR_STORE_PATH = 'vector_store'

    # Initialize Embeddings and Load Vector Store
    print("...Loading knowledge base...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    vector_store = FAISS.load_local(
        VECTOR_STORE_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True 
    )
        
    # Retrieve Relevant Chunks (using translated question if needed)
    print(f"...Searching for chunks related to: '{search_question}'")
    retrieved_chunks = vector_store.similarity_search(search_question, k=3)
    
    # Create the RAG Prompt
    context_text = "\n---\n".join([chunk.page_content for chunk in retrieved_chunks])
    rag_prompt = f"""
You are an expert assistant for training field interviewers. Your task is to answer the user's question based *only* on the provided context from the training manual. If the answer cannot be found in the context, clearly state that. Be helpful, clear, and concise.

CONTEXT:
{context_text}

QUESTION:
{search_question}

ANSWER:
"""

    # Generate the Answer (in English)
    print("...Generating final answer...")
    try:
        final_response = model.generate_content(rag_prompt)
        english_answer = final_response.text
        
        # --- STEP 4: TRANSLATE ANSWER BACK IF NEEDED ---
        if detected_lang != 'en':
            print(f"🔄 Translating answer back to {detected_lang.upper()}...")
            final_answer = translate_with_gemini(english_answer, detected_lang, api_key)
            print(f"✅ Multilingual magic complete!")
            return final_answer
        else:
            print(f"✅ English response ready!")
            return english_answer
            
    except Exception as e:
        error_msg = f"An error occurred during generation: {e}"
        
        # Even translate error messages!
        if detected_lang != 'en':
            error_msg = translate_with_gemini(error_msg, detected_lang, api_key)
        
        return error_msg

# Test function
if __name__ == '__main__':
    # Test with multiple languages!
    test_questions = [
        "What should I do if a respondent is hard of hearing?",  # English
        "¿Qué debo hacer si un encuestado tiene problemas de audición?",  # Spanish
        "Que dois-je faire si un répondant a des problèmes d'audition?"  # French
    ]
    
    for question in test_questions:
        print("\n" + "="*70)
        print(f"QUESTION: {question}")
        print("-" * 70)
        answer = get_answer(question)
        print(f"ANSWER: {answer}")
        print("="*70 + "\n")