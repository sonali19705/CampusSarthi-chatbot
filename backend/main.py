from fastapi import FastAPI, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil, os, uuid, csv, json
from langdetect import detect
from deep_translator import GoogleTranslator
import chromadb
from chromadb.utils import embedding_functions
import asyncio
from PyPDF2 import PdfReader
from fastapi import Form

# ------------------ FASTAPI SETUP ------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ CHROMADB SETUP ------------------
chroma_client = chromadb.PersistentClient(path="vector_db")
sentence_transformer = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = chroma_client.get_or_create_collection(
    name="faqs_pdfs", embedding_function=sentence_transformer
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ------------------ MODELS ------------------
class ChatRequest(BaseModel):
    query: str
    lang: str | None = None   # optional language field

class AdminLogin(BaseModel):
    username: str
    password: str

# ------------------ SUPPORTED LANGUAGES ------------------
SUPPORTED_LANGUAGES = ['hi','mr','gu','bn','ta','te','kn','ml','pa','en','raj']

# ------------------ HELPER FUNCTIONS ------------------
async def translate_text(text: str, dest_lang: str) -> str:
    """Translate text asynchronously using deep-translator."""
    try:
        return await asyncio.to_thread(GoogleTranslator(source='auto', target=dest_lang).translate, text)
    except:
        return text

# ------------------ GREETING ------------------
# ------------------ GREETING ------------------
@app.get("/greet")
async def greet(
    lang: str = Query("en", description="Language code (hi, mr, gu, etc.)"),
    color: str = Query("default", description="Theme color (light, dark, etc.)")
):
    # Ensure the language is supported
    lang = lang.split("-")[0]
    lang = lang if lang in SUPPORTED_LANGUAGES else 'en'

    greetings = {
        'en': "Hi! I'm Campus Sarthi, your college assistant. How can I help you today?",
        'hi': "नमस्ते! मैं कैंपस सारथी हूँ, आपका कॉलेज सहायक। मैं आज आपकी किस प्रकार मदद कर सकता हूँ?",
        'mr': "नमस्कार! मी कॅम्पस सारथी, तुमचा कॉलेज सहाय्यक. मी आज तुम्हाला कशी मदत करू शकतो?",
        'gu': "નમસ્તે! હું કેમ્પસ સારથી છું, તમારો કોલેજ સહાયક. આજે હું તમને કેવી રીતે મદદ કરી શકું?",
        'bn': "হ্যালো! আমি ক্যাম্পাস সারথি, আপনার কলেজ সহায়ক। আজ আমি কিভাবে আপনাকে সাহায্য করতে পারি?",
        'ta': "வணக்கம்! நான் காம்பஸ் சாரதி, உங்கள் கல்லூரி உதவியாளர். இன்று நான் உங்களுக்கு எப்படி உதவலாம்?",
        'te': "హలో! నేను క్యాంపస్ సారథి, మీ కాలేజ్ సహాయకుడు. నేను ఈరోజు మీకు ఎలా సహాయం చేయగలను?",
        'kn': "ನಮಸ್ಕಾರ! ನಾನು ಕ್ಯಾಂಪಸ್ ಸಾರಥಿ, ನಿಮ್ಮ ಕಾಲೇಜು ಸಹಾಯಕ. ನಾನು ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        'ml': "ഹലോ! ഞാൻ ക്യാമ്പസ് സാരഥി, നിങ്ങളുടെ കോളേജ് സഹായി. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?",
        'pa': "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਕੈਂਪਸ ਸਾਰਥੀ ਹਾਂ, ਤੁਹਾਡਾ ਕਾਲਜ ਸਹਾਇਕ। ਮੈਂ ਅੱਜ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?",
        'raj': "राम राम! मैं कैंपस सारथी हूँ, आपका कॉलेज सहायक। मैं आज आपकी किस प्रकार मदद कर सकता हूँ?"
    }

    quick_replies_dict = {
        'en': [
            {"text": "Show me campus map", "payload": "campus map"},
            {"text": "College timings", "payload": "college timings"},
            {"text": "Contact info", "payload": "contact info"}
        ],
        'hi': [
            {"text": "कैंपस का नक्शा दिखाएँ", "payload": "campus map"},
            {"text": "कॉलेज का समय", "payload": "college timings"},
            {"text": "संपर्क जानकारी", "payload": "contact info"}
        ],
        'mr': [
            {"text": "कॅम्पस नकाशा दाखवा", "payload": "campus map"},
            {"text": "कॉलेजचे वेळापत्रक", "payload": "college timings"},
            {"text": "संपर्क माहिती", "payload": "contact info"}
        ],
        'gu': [
            {"text": "કેમ્પસ નકશો બતાવો", "payload": "campus map"},
            {"text": "કૉલેજના સમય", "payload": "college timings"},
            {"text": "સંપર્ક માહિતી", "payload": "contact info"}
        ],
        'bn': [
            {"text": "ক্যাম্পাস মানচিত্র দেখান", "payload": "campus map"},
            {"text": "কলেজ সময়সূচী", "payload": "college timings"},
            {"text": "যোগাযোগের তথ্য", "payload": "contact info"}
        ],
        'ta': [
            {"text": "கேம்பஸ் வரைபடத்தை காட்டவும்", "payload": "campus map"},
            {"text": "கல்லூரி நேரம்", "payload": "college timings"},
            {"text": "தொடர்பு தகவல்", "payload": "contact info"}
        ],
        'te': [
            {"text": "క్యాంపస్ మ్యాప్ చూపించండి", "payload": "campus map"},
            {"text": "కళాశాల సమయాలు", "payload": "college timings"},
            {"text": "సంపర్క్ సమాచారం", "payload": "contact info"}
        ],
        'kn': [
            {"text": "ಕ್ಯಾಂಪಸ್ ನಕ್ಷೆ ತೋರಿಸಿ", "payload": "campus map"},
            {"text": "ಕಾಲೇಜ್ ಸಮಯಗಳು", "payload": "college timings"},
            {"text": "ಸಂಪರ್ಕ ಮಾಹಿತಿ", "payload": "contact info"}
        ],
        'ml': [
            {"text": "ക്യാമ്പസ് മാപ്പ് കാണിക്കുക", "payload": "campus map"},
            {"text": "കോളേജ് സമയങ്ങൾ", "payload": "college timings"},
            {"text": "ബന്ധപ്പെടാനുള്ള വിവരങ്ങൾ", "payload": "contact info"}
        ],
        'pa': [
            {"text": "ਕੈਂਪਸ ਦਾ ਨਕਸ਼ਾ ਦਿਖਾਓ", "payload": "campus map"},
            {"text": "ਕਾਲਜ ਸਮੇਂ", "payload": "college timings"},
            {"text": "ਸੰਪਰਕ ਜਾਣਕਾਰੀ", "payload": "contact info"}
        ],
        'raj': [
            {"text": "कैंपस रो नक्शो देखावो", "payload": "campus map"},
            {"text": "कॉलेज रो टाइमिंग", "payload": "college timings"},
            {"text": "संपर्क जानकारी", "payload": "contact info"}
        ]
    }

    answer = greetings.get(lang, greetings['en'])
    quick_replies = quick_replies_dict.get(lang, quick_replies_dict['en'])

    return {
        "answer": greetings.get(lang, greetings['en']),
        "quick_replies": quick_replies_dict.get(lang, quick_replies_dict['en']),
        "selected_language": lang,
        "theme_color": color
    }
# ------------------ CHAT ------------------
@app.post("/chat")
async def chat(request: ChatRequest):
    user_query = request.query.strip()

    # --- Normalize language code ---
    if request.lang:
        lang = request.lang.split("-")[0]   # e.g., 'gu-IN' -> 'gu'
        if lang not in SUPPORTED_LANGUAGES:
            lang = 'en'
    else:
        try:
            detected_lang = detect(user_query)
        except:
            detected_lang = 'en'
        lang = detected_lang if detected_lang in SUPPORTED_LANGUAGES else 'en'

    # --- Translate user query to English for searching ---
    query_in_english = user_query if lang == "en" else await translate_text(user_query, "en")

    # --- Query vector DB ---
    results = collection.query(
        query_texts=[query_in_english],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    answer = None
    quick_replies = []

    if results.get("documents") and results["documents"][0]:
        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        # Pick best match within threshold
        best_idx = None
        for idx, dist in enumerate(distances):
            if dist <= 0.5:
                best_idx = idx
                break

        if best_idx is not None:
            answer = docs[best_idx]
            quick_replies_raw = [m.get("question", "") for i, m in enumerate(metadatas) if i != best_idx]
            quick_replies_raw = [q for q in quick_replies_raw if q.strip()]

            # --- Translate answer and quick replies to user language if needed ---
            if lang != "en":
                try:
                    answer = await translate_text(answer, lang)
                    translated_replies = []
                    for q in quick_replies_raw:
                        translated_replies.append(await translate_text(q, lang))
                    quick_replies_raw = translated_replies
                except:
                    pass

            quick_replies = [{"text": q, "payload": q} for q in quick_replies_raw]

    # --- Fallback if no match found ---
    if not answer:
        fallback_messages = {
            "en": "Sorry, I don't know the answer yet.",
            "hi": "क्षमा करें, मुझे अभी इसका उत्तर नहीं पता।",
            "mr": "माफ करा, मला अजून उत्तर माहिती नाही.",
            "gu": "માફ કરશો, મને હજી જવાબ ખબર નથી.",
            "bn": "দুঃখিত, আমি এখনো উত্তর জানি না।",
            "ta": "மன்னிக்கவும், எனக்கு இதற்கு பதில் தெரியவில்லை.",
            "te": "క్షమించండి, నాకు ఇంకా సమాధానం తెలియదు।",
            "kn": "ಕ್ಷಮಿಸಿ, ನನಗೆ ಇನ್ನೂ ಉತ್ತರ ತಿಳಿದಿಲ್ಲ।",
            "ml": "ക്ഷമിക്കണം, എനിക്ക് ഇതുവരെ ഉത്തരമറിയില്ല।",
            "pa": "ਮਾਫ਼ ਕਰਨਾ, ਮੈਨੂੰ ਹੁਣ ਤੱਕ ਜਵਾਬ ਨਹੀਂ ਪਤਾ।",
            "raj": "माफ करना, मुझे अभी इसका उत्तर नहीं पता।",
        }
        answer = fallback_messages.get(lang, fallback_messages["en"])
        quick_replies = []

    return {"answer": answer, "quick_replies": quick_replies}

# ------------------ ADMIN LOGIN ------------------
@app.post("/admin/login")
async def admin_login(data: AdminLogin):
    if data.username == "admin" and data.password == "admin123":
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ------------------ UPLOAD FAQ ------------------
@app.post("/admin/upload_faq")
async def upload_faq(question: str = None, answer: str = None, file: UploadFile = None):
    documents, metadatas, ids = [], [], []

    # Single FAQ
    if question and answer:
        doc_id = str(uuid.uuid4())
        documents.append(answer)
        metadatas.append({"question": question, "type": "faq"})
        ids.append(doc_id)
    
    # CSV/JSON file
    elif file:
        if not (file.filename.endswith(".csv") or file.filename.endswith(".json")):
            raise HTTPException(status_code=400, detail="Invalid file format")
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file.filename.endswith(".csv"):
            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    q, a = row.get("question"), row.get("answer")
                    if q and a:
                        doc_id = str(uuid.uuid4())
                        documents.append(a)
                        metadatas.append({"question": q, "type": "faq"})
                        ids.append(doc_id)
        elif file.filename.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as jsonfile:
                data = json.load(jsonfile)
                for item in data:
                    q, a = item.get("question"), item.get("answer")
                    if q and a:
                        doc_id = str(uuid.uuid4())
                        documents.append(a)
                        metadatas.append({"question": q, "type": "faq"})
                        ids.append(doc_id)
    else:
        raise HTTPException(status_code=400, detail="Provide question & answer or file")

    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    return {"message": "FAQ uploaded successfully", "count": len(documents)}


#--------------------admin statistics---------------------
# ------------------ ADMIN STATS ------------------
#--------------------admin statistics---------------------
# ------------------ ADMIN STATS ------------------
@app.get("/admin/stats")
async def admin_stats():
    try:
        data = collection.get(include=["documents", "metadatas"])
        # Flatten all metadata lists
        all_metadatas = [meta for batch in data.get("metadatas", []) for meta in batch]
        faqs_count = sum(1 for m in all_metadatas if m.get("type") == "faq")
    except:
        faqs_count = 0

    csv_count = len([f for f in os.listdir(UPLOAD_DIR) if f.endswith(".csv")])
    pdf_count = len([f for f in os.listdir(UPLOAD_DIR) if f.endswith(".pdf")])
    return {"faqs": faqs_count, "csv": csv_count, "pdf": pdf_count}



# ------------------ get FAQ ------------------
@app.get("/admin/get_faqs")
async def get_faqs():
    results = collection.query(
        query_texts=[""],
        n_results=1000,
        include=["documents", "metadatas"]
    )
    faqs = []
    if results.get("documents") and results["documents"][0]:
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            if meta.get("question") and doc:
                faqs.append({"question": meta.get("question"), "answer": doc})
    return {"faqs": faqs}

# Delete FAQ
@app.delete("/admin/delete_faq")
async def delete_faq(question: str):
    try:
        collection.delete(where={"question": question})
        return {"message": f"FAQ deleted: {question}"}
    except Exception as e:
        return {"message": str(e)}

# Update FAQ
@app.put("/admin/update_faq")
async def update_faq(
    question: str = Form(...),
    new_answer: str = Form(...)
):
    try:
        collection.delete(where={"question": question})
        collection.add(
            documents=[new_answer],
            metadatas=[{"question": question, "type": "faq"}],
            ids=[str(uuid.uuid4())]
        )
        return {"message": f"FAQ updated: {question}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------ UPLOAD PDF ------------------
@app.post("/admin/upload_pdf")
async def upload_pdf(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file format")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from PDF
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        if text.strip():
            doc_id = str(uuid.uuid4())
            collection.add(
                documents=[text],
                metadatas=[{"question": f"PDF: {file.filename}", "type": "pdf"}],
                ids=[doc_id]
            )
    except Exception as e:
        print(f"PDF parse error: {e}")

    pdf_count = len([f for f in os.listdir(UPLOAD_DIR) if f.endswith(".pdf")])
    return {"message": f"PDF uploaded: {file.filename}", "count": pdf_count}

# ------------------ STATIC FRONTEND ------------------
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")