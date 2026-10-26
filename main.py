import os
import time
import streamlit as st
from pypdf import PdfReader
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Page Configuration
st.set_page_config(
    page_title="DocuMind AI | Document & Q&A Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

if not api_key:
    st.error("⚠️ GEMINI_API_KEY not found in .env file!")
    st.stop()

client = genai.Client(api_key=api_key)

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hi! Upload a PDF or TXT document in the sidebar to analyze it, or ask me any question directly below!"
        }
    ]

# 3. Sidebar: Theme Picker, Document Upload & Controls
with st.sidebar:
    st.header("🎨 Appearance")
    theme_choice = st.selectbox(
        "Background Theme",
        ["Midnight Cyber (Dark)", "Soft Lavender & Sky (Light)", "Emerald Mint (Light)"],
        index=0
    )
    st.divider()

    st.header("📂 Document Workspace")
    st.caption("Upload study notes, research papers, or resumes for instant AI analysis.")
    
    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
    document_text = ""
    raw_pdf_bytes = None
    page_count = 0

    if uploaded_file is not None:
        try:
            file_bytes = uploaded_file.getvalue()
            if uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                page_count = len(reader.pages)
                for page in reader.pages:
                    document_text += (page.extract_text() or "") + "\n"
                
                if len(document_text.strip()) < 50:
                    raw_pdf_bytes = file_bytes
                    st.info(f"📷 **Scanned PDF Detected**\n\n`{uploaded_file.name}` ({page_count} pages) will be analyzed using Gemini Vision.")
                else:
                    st.success(f"✅ **Active Document:** `{uploaded_file.name}`")
                    col1, col2 = st.columns(2)
                    col1.metric("Pages", page_count)
                    col2.metric("Words", f"{len(document_text.split()):,}")
                    with st.expander("🔍 Preview Extracted Text"):
                        st.text(document_text[:1200] + ("..." if len(document_text) > 1200 else ""))
            else:
                document_text = file_bytes.decode("utf-8", errors="ignore")
                st.success(f"✅ **Active Document:** `{uploaded_file.name}`")
                st.metric("Words", f"{len(document_text.split()):,}")
                with st.expander("🔍 Preview Extracted Text"):
                    st.text(document_text[:1200] + ("..." if len(document_text) > 1200 else ""))
        except Exception as e:
            st.error(f"Could not read file: {e}")
    else:
        st.info("💡 No file uploaded yet. Operating in general Q&A mode.")

    st.divider()
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Conversation cleared! Ask a new question below."
            }
        ]
        st.rerun()

# 4. Fixed CSS with Visible Input Box & Button Text
if theme_choice == "Midnight Cyber (Dark)":
    bg_css = """
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            color: #f8fafc;
        }
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid #374151;
        }
        [data-testid="stHeader"], [data-testid="stBottom"] > div {
            background: transparent !important;
        }
        /* Fix main text & headings without breaking white inputs */
        [data-testid="stMarkdownContainer"] p, 
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        label[data-testid="stWidgetLabel"] p,
        [data-testid="stCaptionContainer"] p {
            color: #f1f5f9 !important;
        }
        /* Fix Quick Action & Sidebar Buttons */
        .stButton > button {
            background-color: #1e293b !important;
            color: #f8fafc !important;
            border: 1px solid #4f46e5 !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
        .stButton > button p {
            color: #f8fafc !important;
        }
        .stButton > button:hover {
            background-color: #4f46e5 !important;
            border-color: #818cf8 !important;
        }
        /* Fix Bottom Chat Input Box Text Visibility */
        [data-testid="stChatInput"] {
            background-color: #1e293b !important;
            border: 1px solid #6366f1 !important;
            border-radius: 12px !important;
        }
        [data-testid="stChatInput"] textarea {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            caret-color: #38bdf8 !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: #94a3b8 !important;
            -webkit-text-fill-color: #94a3b8 !important;
        }
        /* Chat Message Cards */
        [data-testid="stChatMessage"] {
            background-color: rgba(30, 41, 59, 0.85) !important;
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 14px;
            padding: 14px;
            margin-bottom: 12px;
        }
        .hero-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        .hero-subtitle {
            color: #cbd5e1 !important;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """
elif theme_choice == "Soft Lavender & Sky (Light)":
    bg_css = """
    <style>
        .stApp {
            background: linear-gradient(135deg, #eef2ff 0%, #e0f2fe 50%, #f5f3ff 100%);
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0;
        }
        [data-testid="stHeader"], [data-testid="stBottom"] > div {
            background: transparent !important;
        }
        [data-testid="stChatMessage"] {
            background-color: rgba(255, 255, 255, 0.92);
            border: 1px solid #cbd5e1;
            border-radius: 14px;
            padding: 14px;
            margin-bottom: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }
        .hero-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, #4f46e5, #0284c7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        .hero-subtitle {
            color: #475569;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """
else:
    bg_css = """
    <style>
        .stApp {
            background: linear-gradient(135deg, #ecfdf5 0%, #f0fdfa 50%, #e0f2fe 100%);
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #d1fae5;
        }
        [data-testid="stHeader"], [data-testid="stBottom"] > div {
            background: transparent !important;
        }
        [data-testid="stChatMessage"] {
            background-color: rgba(255, 255, 255, 0.92);
            border: 1px solid #a7f3d0;
            border-radius: 14px;
            padding: 14px;
            margin-bottom: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        }
        .hero-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, #059669, #0284c7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        .hero-subtitle {
            color: #475569;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """

st.markdown(bg_css, unsafe_allow_html=True)

# 5. Main Header & Quick-Action Prompts
st.markdown('<div class="hero-title">✨ DocuMind AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Intelligent RAG Document Analyzer & Conversational Q&A powered by Google Gemini</div>', unsafe_allow_html=True)

triggered_prompt = None
if uploaded_file is not None:
    st.caption("⚡ **Quick Actions for Uploaded Document:**")
    q_col1, q_col2, q_col3 = st.columns(3)
    if q_col1.button("📝 Summarize Document", use_container_width=True):
        triggered_prompt = "Provide a structured executive summary of this document with key sections."
    if q_col2.button("🎯 Key Takeaways & Formulas", use_container_width=True):
        triggered_prompt = "Extract the most important concepts, definitions, or formulas from this document as bullet points."
    if q_col3.button("❓ Generate 5 Practice Questions", use_container_width=True):
        triggered_prompt = "Create 5 important exam/interview questions with brief answers based on this document."

st.divider()

# 6. Render Chat History
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 7. Chat Input Bar
chat_input_prompt = st.chat_input("Ask a question about your document or any topic...")
user_question = triggered_prompt or chat_input_prompt

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_question)

    if raw_pdf_bytes is not None:
        contents_payload = [
            types.Part.from_bytes(data=raw_pdf_bytes, mime_type="application/pdf"),
            user_question
        ]
    elif document_text.strip():
        contents_payload = (
            f"You are an expert AI document assistant. Use the following document content to answer the user's question clearly and accurately using clean Markdown formatting.\n\n"
            f"--- DOCUMENT CONTENT ---\n{document_text[:35000]}\n--- END DOCUMENT ---\n\n"
            f"User Question: {user_question}"
        )
    else:
        contents_payload = user_question

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking and analyzing..."):
            models = ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-pro-latest"]
            response_text = None

            for model_name in models:
                for attempt in range(2):
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=contents_payload
                        )
                        response_text = response.text
                        break
                    except Exception as e:
                        if "503" in str(e):
                            time.sleep(2)
                        else:
                            break
                if response_text:
                    break

            if response_text:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error("The AI server is temporarily busy. Please try sending your message again.")