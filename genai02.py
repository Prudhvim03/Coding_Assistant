#!pip install streamlit groq python-dotenv requests

import streamlit as st
from groq import Groq
import requests
import os
from dotenv import load_dotenv

# Load .env if present
try:
    load_dotenv()
except:
    pass

# --- API Keys ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Tavily Search ---
def tavily_search(query):
    url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    params = {"query": query, "num_results": 3}
    try:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            return resp.json().get("results", [])
        else:
            return []
    except Exception as e:
        st.error(f"Tavily search error: {str(e)}")
        return []

# --- Groq LLM ---
def initialize_groq_client():
    return Groq(api_key=GROQ_API_KEY)

def generate_code_and_explanation(client, question, want_explanation=True):
    prompt = (
        f"Write a clear, efficient code snippet to solve the following coding question:\n\n"
        f"{question}\n\n"
        f"Return your answer in this format:\n"
        f"<code>\n[code here]\n</code>\n"
    )
    if want_explanation:
        prompt += "<explanation>\n[concise explanation here]\n</explanation>\n"

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Or your preferred Groq model
            messages=[
                {"role": "system", "content": "You are an expert coding tutor and problem solver."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1200
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Groq API error: {str(e)}")
        return None

# --- Streamlit UI ---
st.set_page_config(page_title="Coding Q&A Assistant", page_icon="💡", layout="wide")
st.markdown("""
<style>
.stApp { max-width: 900px; margin: 0 auto; }
.result-box { padding: 18px; border-radius: 10px; background-color: #f4f6fa; margin: 10px 0; }
.code-box { background-color: #23272f; color: #fff; border-radius: 8px; padding: 10px; }
.ref-link { font-size: 17px; }
.explanation-title { color: #1a73e8; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("💡 Coding Q&A Assistant")
st.write("Ask any coding question (e.g., 'Reverse a linked list in Python'). Get code, references, and explanation.")

coding_question = st.text_area(
    "Enter your coding question (like GeeksforGeeks, LeetCode, etc.)",
    height=80,
    placeholder="e.g., Find the intersection of two arrays in Python"
)
want_explanation = st.toggle("Show explanation", value=True)

if st.button("Get Answer", use_container_width=True) and coding_question.strip():
    client = initialize_groq_client()
    with st.spinner("🔎 Searching for reference links..."):
        links = tavily_search(coding_question)

    with st.spinner("🤖 Generating code and explanation..."):
        answer = generate_code_and_explanation(client, coding_question, want_explanation)

    # Parse code and explanation
    code_part, explanation_part = "", ""
    if answer:
        if "<code>" in answer and "</code>" in answer:
            code_part = answer.split("<code>")[1].split("</code>")[0].strip()
        if "<explanation>" in answer and "</explanation>" in answer:
            explanation_part = answer.split("<explanation>")[1].split("</explanation>")[0].strip()

    # Display Reference Links
    st.subheader("🔗 Reference Links")
    if links:
        for link in links:
            st.markdown(f"<div class='ref-link'>-  <a href='{link['url']}' target='_blank'>{link['title']}</a></div>", unsafe_allow_html=True)
    else:
        st.info("No reference links found.")

    # Display Code
    st.subheader("💻 Code Snippet")
    if code_part:
        st.code(code_part, language="python")
    else:
        st.info("No code generated.")

    # Display Explanation
    if want_explanation and explanation_part:
        st.markdown("<div class='explanation-title'>📝 Explanation</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-box'>{explanation_part}</div>", unsafe_allow_html=True)

    # Download Code
    if code_part:
        st.download_button("Download Code", code_part, file_name="solution.py")

with st.expander("💡 Tips for best results"):
    st.markdown("""
    - Ask clear, specific coding questions (e.g., 'Binary search in Java', 'Fibonacci using recursion').
    - Use the explanation toggle for a concise summary.
    - Always review generated code before using in production.
    """)
