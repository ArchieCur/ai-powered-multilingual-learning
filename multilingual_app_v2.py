"""
Updated Multilingual Flask App with Enhanced 8-Language Detection
From punch cards to instant AI - the ultimate computational evolution! ⚡️
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
import logging
from enhanced_language_detection import detect_language_enhanced, get_language_name

# Initialize the Flask application
app = Flask(__name__)

# Enable CORS for global accessibility
CORS(app, origins=[
    "https://storage.googleapis.com",
    "https://*.storage.googleapis.com", 
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "file://",
    "*"  # Allow all origins for development
])

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def translate_with_gemini(text, target_language, api_key):
    """
    Enhanced translation supporting 8 languages!
    From hours of manual calculation to instant AI translation!
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Enhanced language mapping
    lang_names = {
        'es': 'Spanish', 
        'en': 'English', 
        'fr': 'French', 
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'nl': 'Dutch',
        'ru': 'Russian'
    }
    
    target_lang_name = lang_names.get(target_language, 'English')
    
    translation_prompt = f"""
Translate the following text to {target_lang_name}. 
Provide ONLY the translation, no explanations or additional text.

Text: {text}

Translation:"""
    
    try:
        response = model.generate_content(translation_prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text

def get_multilingual_answer(user_question):
    """
    Enhanced multilingual RAG with 8-language support!
    The computational dream realized - instant global communication!
    """
    try:
        # Load environment
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {
                'answer': 'Error: Google API Key not found. Please check configuration.',
                'language': 'en',
                'error': True
            }
        
        logger.info(f"🌍 Processing question: '{user_question}'")
        
        # STEP 1: Enhanced language detection with 8 languages!
        lang_detection = detect_language_enhanced(user_question)
        detected_lang = lang_detection['language']
        confidence = lang_detection['confidence']
        method = lang_detection['method']
        scores = lang_detection.get('scores', {})
        
        logger.info(f"🎯 Detected: {detected_lang.upper()} ({get_language_name(detected_lang)})")
        logger.info(f"   Confidence: {confidence:.3f} | Method: {method}")
        if scores:
            top_scores = {k: v for k, v in scores.items() if v > 0}
            if top_scores:
                logger.info(f"   Language scores: {top_scores}")
        
        # STEP 2: Translate to English if needed
        search_question = user_question
        if detected_lang != 'en':
            logger.info(f"🔄 Translating from {get_language_name(detected_lang)} to English...")
            search_question = translate_with_gemini(user_question, 'en', api_key)
            logger.info(f"📝 Search question: '{search_question}'")
        
        # STEP 3: RAG magic with our vector store
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load embeddings and vector store
        logger.info("📊 Loading knowledge base...")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        vector_store = FAISS.load_local(
            'multilingual_vector_store', 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        
        # Retrieve relevant chunks
        logger.info(f"🔍 Searching for relevant content...")
        retrieved_chunks = vector_store.similarity_search(search_question, k=3)
        
        # Create RAG prompt
        context_text = "\n---\n".join([chunk.page_content for chunk in retrieved_chunks])
        rag_prompt = f"""
You are an expert assistant for training field interviewers. Your task is to answer the user's question based *only* on the provided context from the training manual. If the answer cannot be found in the context, clearly state that. Be helpful, clear, and concise.

CONTEXT:
{context_text}

QUESTION:
{search_question}

ANSWER:
"""
        
        # Generate answer
        logger.info("🧠 Generating answer...")
        final_response = model.generate_content(rag_prompt)
        english_answer = final_response.text
        
        # STEP 4: Translate back if needed
        final_answer = english_answer
        if detected_lang != 'en':
            logger.info(f"🔄 Translating answer back to {get_language_name(detected_lang)}...")
            final_answer = translate_with_gemini(english_answer, detected_lang, api_key)
        
        logger.info(f"✅ Successfully processed multilingual query!")
        
        return {
            'answer': final_answer,
            'language': detected_lang,
            'language_name': get_language_name(detected_lang),
            'confidence': confidence,
            'method': method,
            'scores': scores,
            'translated_query': search_question if detected_lang != 'en' else None,
            'error': False
        }
        
    except Exception as e:
        logger.error(f"❌ Error in multilingual processing: {e}")
        error_msg = f"An error occurred while processing your question: {str(e)}"
        
        # Even translate error messages!
        if 'detected_lang' in locals() and detected_lang != 'en':
            try:
                error_msg = translate_with_gemini(error_msg, detected_lang, api_key)
            except:
                pass
        
        return {
            'answer': error_msg,
            'language': detected_lang if 'detected_lang' in locals() else 'en',
            'error': True
        }

@app.route('/ask', methods=['POST'])
def ask_question():
    """
    Main multilingual endpoint - now with 8-language support!
    """
    logger.info("🚀 Received new multilingual question...")
    
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'No question provided',
                'answer': 'Please provide a question in the request body.'
            }), 400
        
        user_question = data['question']
        
        # Process with our enhanced multilingual beast
        result = get_multilingual_answer(user_question)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ API error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'answer': 'An error occurred while processing your request.'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check - faster than slide rule calculations!
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Enhanced Multilingual AI Assistant ready to serve 8 languages!',
        'version': 'Claude Sonnet 4 Beast Edition v2.0',
        'supported_languages': 8,
        'speed': 'Infinitely faster than punch cards! ⚡️'
    }), 200

@app.route('/languages', methods=['GET'])
def supported_languages():
    """
    Show all supported languages - the computational dream realized!
    """
    return jsonify({
        'supported_languages': {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'nl': 'Dutch',
            'ru': 'Russian (basic support)'
        },
        'total_languages': 8,
        'detection_methods': ['keyword_detection', 'langdetect', 'fallback'],
        'note': 'Auto-detection enabled - from punch cards to instant multilingual AI!',
        'computational_evolution': 'Hours → Milliseconds ⚡️'
    })

# Enhanced test endpoints for all languages
@app.route('/test-english', methods=['GET'])
def test_english():
    result = get_multilingual_answer("What is the ACL study?")
    return jsonify(result)

@app.route('/test-spanish', methods=['GET'])  
def test_spanish():
    result = get_multilingual_answer("¿Qué es el estudio ACL?")
    return jsonify(result)

@app.route('/test-german', methods=['GET'])
def test_german():
    result = get_multilingual_answer("Was ist die ACL-Studie?")
    return jsonify(result)

@app.route('/test-italian', methods=['GET'])
def test_italian():
    result = get_multilingual_answer("Che cos'è lo studio ACL?")
    return jsonify(result)

@app.route('/test-portuguese', methods=['GET'])
def test_portuguese():
    result = get_multilingual_answer("O que é o estudo ACL?")
    return jsonify(result)

@app.route('/test-dutch', methods=['GET'])
def test_dutch():
    result = get_multilingual_answer("Wat is de ACL-studie?")
    return jsonify(result)

@app.route('/test-french', methods=['GET'])
def test_french():
    result = get_multilingual_answer("Qu'est-ce que l'étude ACL?")
    return jsonify(result)

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)