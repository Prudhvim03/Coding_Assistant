import streamlit as st
from tavily import TavilyClient
from groq import Groq
import os
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TAVILY_API_KEY:
    TAVILY_API_KEY = st.text_input("Enter your Tavily API key:", type="password")
if not GROQ_API_KEY:
    GROQ_API_KEY = st.text_input("Enter your Groq API key:", type="password")

# --- Custom CSS for Futuristic UI ---
css = """
<style>
:root {
  --primary: #2b5876;
  --secondary: #4e4376;
  --accent: #f6d365;
  --text: #ffffff;
}
.stApp {
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: var(--text);
}
.stTextInput input, .stSelectbox select, .stTextArea textarea {
  background-color: rgba(255,255,255,0.2);
  color: var(--text);
  border: 1px solid var(--secondary);
  border-radius: 10px;
  padding: 10px;
  margin: 5px 0;
}
.stButton button {
  background: linear-gradient(90deg, var(--accent) 0%, #f6d365 100%);
  color: black;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  padding: 10px 20px;
  margin: 5px 0;
}
.stMarkdown, .stCode, .stLink {
  color: var(--text);
}
.link {
  color: var(--accent);
}
.card {
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 15px;
  margin: 10px 0;
}
.footer {
  text-align: center;
  font-size: 0.7em;
  color: #ccc;
  margin-top: -1.5em;
  margin-bottom: 1em;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- App Title and Caption ---
st.title("🚀 CodeQ: AI Coding Assistant")
st.caption("Ask any coding question and get code, explanations, and reference links!")
st.markdown("""<div class="footer">
Created by Prudhvi
</div>""", unsafe_allow_html=True)

# --- Sidebar: Settings ---
with st.sidebar:
    st.title("⚙️ Settings")
    language = st.selectbox(
        "Programming Language",
        ["Python", "Java", "C", "C++", "JavaScript", "Go", "Rust"]
    )
    show_explanation = st.checkbox("Show Explanation", value=True)

# --- Main UI ---
question = st.text_area(
    "Enter your coding question (like GeeksforGeeks questions):",
    height=100,
    placeholder="e.g., Reverse a linked list in Python"
)

if st.button("Get Answer", use_container_width=True) and question.strip():
    # --- Tavily Search ---
    with st.spinner("🔎 Searching for reference links..."):
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        response = tavily_client.search(question)
        links = [result["url"] for result in response.get("results", [])[:5]]

    # --- Groq LLM ---
    with st.spinner("🤖 Generating code and explanation..."):
        groq_client = Groq(api_key=GROQ_API_KEY)
        prompt = (
            f"Write a clear, efficient code snippet in {language} to solve the following coding question:\n\n"
            f"{question}\n\n"
            f"Return your answer in this format:\n"
            f"<code>\n[code here]\n</code>\n"
        )
        if show_explanation:
            prompt += "<explanation>\n[concise explanation here]\n</explanation>\n"

        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",  # Or your preferred Groq model
            messages=[
                {"role": "system", "content": "You are an expert coding tutor and problem solver."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1200
        )
        answer = response.choices[0].message.content

        # Parse code and explanation
        code_part, explanation_part = "", ""
        if "<code>" in answer and "</code>" in answer:
            code_part = answer.split("<code>")[1].split("</code>")[0].strip()
        if show_explanation and "<explanation>" in answer and "</explanation>" in answer:
            explanation_part = answer.split("<explanation>")[1].split("</explanation>")[0].strip()

    # --- Display Reference Links ---
    st.subheader("🔗 Reference Links")
    if links:
        for link in links:
            st.markdown(f"- <span class='link'>[{link}]({link})</span>", unsafe_allow_html=True)
    else:
        st.info("No reference links found.")

    # --- Display Code ---
    st.subheader(f"💻 Code Snippet ({language})")
    if code_part:
        st.code(code_part, language=language.lower())
    else:
        st.info("No code generated.")

    # --- Display Explanation ---
    if show_explanation and explanation_part:
        st.subheader("📝 Explanation")
        st.markdown(explanation_part)

    # --- Download Code ---
    if code_part:
        st.download_button("Download Code", code_part, file_name=f"solution.{language.lower()}")

with st.expander("💡 Tips for best results"):
    st.markdown("""
    - Ask clear, specific coding questions (e.g., 'Binary search in Java', 'Fibonacci using recursion').
    - Use the explanation toggle for a concise summary.
    - Always review generated code before using in production.
    """)
