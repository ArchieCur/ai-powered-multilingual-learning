"""
Magic 2-Step Pipeline: PDF to Multilingual AI Assistant
The complete automation you've been dreaming of!

Step 1: PDF → Clean Markdown
Step 2: Keywords → Chunking → Vector Store → AI Ready!
"""

import os
from pathlib import Path
import PyPDF2
import pdfplumber
import google.generativeai as genai
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from dotenv import load_dotenv
import re

def extract_with_pdfplumber(pdf_path):
    """Extract text using pdfplumber"""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += f"\n\n# Page {page_num}\n\n{page_text}\n"
            return text
    except Exception as e:
        print(f"pdfplumber error: {e}")
        return None

def smart_markdown_formatting(text):
    """Convert plain text to proper markdown structure"""
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append('')
            continue
            
        # Page headers - use HTML comments (cleanest)
        if line.startswith('# Page'):
            page_num = line.replace('# Page', '').strip()
            formatted_lines.append(f"\n<!-- Page {page_num} -->\n")
        # Section headers (ALL CAPS, longer lines)
        elif line.isupper() and len(line) > 8 and not line.startswith('ACL'):
            formatted_lines.append(f"\n## {line}\n")
        # Subsection headers (Title Case or shorter ALL CAPS)
        elif (line.istitle() or (line.isupper() and len(line) <= 8)) and len(line.split()) <= 4:
            formatted_lines.append(f"\n### {line}\n")
        # Regular content
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def generate_keywords_with_ai(text, api_key):
    """Generate contextual keywords using Gemini"""
    print("🏷️ Generating keywords with AI...")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Split text into chunks for keyword generation
    chunks = text.split('<!-- Page')
    enhanced_text = ""
    
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        # Restore page marker if needed
        if i > 0:
            chunk = '<!-- Page' + chunk
            
        # Generate keywords for this section
        keyword_prompt = f"""
        Analyze the following text and generate 5-8 relevant keywords that would help someone find this content.
        Focus on: main concepts, key people, important terms, methodologies, and topics covered.
        
        Text: {chunk[:2000]}...
        
        Keywords (comma-separated):
        """
        
        try:
            response = model.generate_content(keyword_prompt)
            keywords = response.text.strip()
            
            # Add keywords as metadata
            enhanced_chunk = f"{chunk}\n\n**Keywords:** {keywords}\n"
            enhanced_text += enhanced_chunk
            
        except Exception as e:
            print(f"Keyword generation error: {e}")
            enhanced_text += chunk
    
    return enhanced_text

def create_vector_store(text, store_name="multilingual_vector_store"):
    """Create FAISS vector store from processed text"""
    print(f"🧠 Creating vector store: {store_name}")
    
    # Initialize embeddings
    print("📊 Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    # Clean and chunk the text
    print("✂️ Chunking text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    print(f"📄 Created {len(chunks)} chunks")
    
    # Create Document objects
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "chunk_id": i,
                "source": "training_manual",
                "chunk_size": len(chunk)
            }
        )
        documents.append(doc)
    
    # Create vector store
    print("🔍 Creating FAISS vector store...")
    vector_store = FAISS.from_documents(documents, embeddings)
    
    # Save to disk
    vector_store_path = Path(store_name)
    vector_store.save_local(vector_store_path)
    print(f"💾 Vector store saved to: {vector_store_path}")
    
    return vector_store, len(chunks)

def magic_pipeline():
    """The complete 2-step automation pipeline!"""
    print("🎪 MAGIC PIPELINE STARTING! 🎪")
    print("From PDF to Multilingual AI in 2 easy steps!")
    print("=" * 60)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in .env file")
        return
    
    # Find PDFs in input folder
    input_dir = Path("input")
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in input/ folder")
        return
    
    for pdf_file in pdf_files:
        print(f"\n🎯 Processing: {pdf_file.name}")
        print("-" * 40)
        
        # STEP 1: PDF → Clean Markdown
        print("\n📚 STEP 1: Extracting and formatting content...")
        
        # Extract text
        print("📖 Extracting text with pdfplumber...")
        raw_text = extract_with_pdfplumber(pdf_file)
        
        if not raw_text or len(raw_text.strip()) < 100:
            print(f"❌ Failed to extract text from {pdf_file.name}")
            continue
        
        # Format as clean markdown
        print("✨ Applying smart markdown formatting...")
        formatted_text = smart_markdown_formatting(raw_text)
        
        # Save formatted markdown
        markdown_file = f"formatted_{pdf_file.stem}.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        print(f"✅ Clean markdown saved to: {markdown_file}")
        print(f"📊 Extracted {len(formatted_text)} characters")
        
        # STEP 2: Keywords → Chunking → Vector Store
        print("\n🏷️ STEP 2: Adding keywords and building AI brain...")
        
        # Generate keywords
        enhanced_text = generate_keywords_with_ai(formatted_text, api_key)
        
        # Save enhanced version
        enhanced_file = f"enhanced_{pdf_file.stem}.md"
        with open(enhanced_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_text)
        
        print(f"💾 Enhanced content saved to: {enhanced_file}")
        
        # Create vector store
        vector_store, chunk_count = create_vector_store(enhanced_text)
        
        print(f"\n🎉 SUCCESS! Pipeline complete for {pdf_file.name}")
        print(f"📚 {chunk_count} chunks created")
        print(f"🤖 Multilingual AI assistant ready!")
        print(f"🌍 Global learners can now access this content!")
        
    print("\n" + "=" * 60)
    print("🚀 MAGIC PIPELINE COMPLETE! 🚀")
    print("Your content is now ready for multilingual AI magic!")

if __name__ == "__main__":
    magic_pipeline()