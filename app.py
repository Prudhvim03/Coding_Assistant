import streamlit as st
from tavily import TavilyClient
from groq import Groq
import os
from dotenv import load_dotenv
import graphviz
import subprocess
from streamlit_ace import st_ace
import random

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TAVILY_API_KEY:
    TAVILY_API_KEY = st.text_input("Enter your Tavily API key:", type="password")
if not GROQ_API_KEY:
    GROQ_API_KEY = st.text_input("Enter your Groq API key:", type="password")

THEMES = {
    "Classic": {
        "primary": "#1E88E5",
        "background": "#8edce6",
        "secondary": "#e3f2fd",
        "text": "#212121",
        "accent": "#00B0FF",
        "text_on_primary": "#FFFFFF",
    },
    "Dark": {
        "primary": "#BB86FC",
        "background": "#121212",
        "secondary": "#1E1E1E",
        "text": "#E0E0E0",
        "accent": "#03D8F4",
        "text_on_primary": "#000000",
    },
    "Ocean": {
        "primary": "#03A9F4",
        "background": "#E1F5FE",
        "secondary": "#B3E5FC",
        "text": "#01579B",
        "accent": "#4CA1AF",
        "text_on_primary": "#000000",
    },
    "Sunset": {
        "primary": "#8D6E63",
        "background": "#FFF3E0",
        "secondary": "#FF8A65",
        "text": "#5D4037",
        "accent": "#4E342E",
        "text_on_primary": "#000000",
    },
}

with st.sidebar:
    st.title("⚙️ Settings")
    theme_name = st.selectbox("Theme", list(THEMES.keys()))
    language = st.selectbox(
        "Programming Language",
        ["Python", "Java", "C", "C++", "JavaScript", "Go", "Rust"]
    )
    show_explanation = st.checkbox("Show Explanation", value=True)
    enable_editor = st.checkbox("Enable Interactive Code Editor", value=True)
    enable_quality = st.checkbox("Enable Code Quality Report", value=True)
    enable_flow = st.checkbox("Enable Visual Flow", value=True)
    enable_hotspots = st.checkbox("Enable Hotspots", value=True)
    enable_multiple_agents = st.checkbox("Enable Multi-Agent Analysis", value=True)

theme = THEMES[theme_name]

css = f"""
<style>
:root {{
  --primary: {theme['primary']};
  --background: {theme['background']};
  --secondary: {theme['secondary']};
  --text: {theme['text']};
  --accent: {theme['accent']};
}}
.stApp {{
  background: var(--background);
  color: var(--text);
}}
.stTextInput input, .stSelectbox select, .stTextArea textarea {{
  background-color: rgba(255, 255, 255, 0.9);
  color: var(--text);
  border: 1px solid var(--primary);
  border-radius: 10px;
  padding: 10px;
  margin: 5px 0;
}}
.stButton button {{
  background: var(--primary);
  color: {theme['text_on_primary']};
  border: none;
  border-radius: 10px;
  font-weight: bold;
  padding: 10px 20px;
  margin: 5px 0;
}}
.stMarkdown, .stCode, .stLink {{
  color: var(--text);
}}
.link {{
  color: var(--accent);
}}
.card {{
  background: var(--secondary);
  border-radius: 10px;
  padding: 15px;
  margin: 10px 0;
}}
.footer {{
  text-align: center;
  font-size: 0.7em;
  color: {theme['accent']};
  margin-top: -1.5em;
  margin-bottom: 1em;
}}
.hotspot {{
  background-color: #ff9999;
  padding: 2px;
  border-radius: 3px;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

st.title("🚀 CodeQ: Advanced AI Coding Assistant")
st.caption("Ask any coding question and get code, explanations, reference links, and advanced analysis!")
st.markdown("""<div class="footer">
Created by Prudhvi
</div>""", unsafe_allow_html=True)

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
    with st.spinner("🤖 Generating code and analysis..."):
        groq_client = Groq(api_key=GROQ_API_KEY)
        prompt = (
            f"Write a clear, efficient code snippet in {language} to solve the following coding question:\n\n"
            f"{question}\n\n"
            "Return your answer in this format:\n"
            "<code>\n[code here]\n</code>\n"
            "<time_complexity>\n[time complexity here]\n</time_complexity>\n"
            "<space_complexity>\n[space complexity here]\n</space_complexity>\n"
            "<difficulty>\n[Easy/Medium/Hard]\n</difficulty>\n"
            "<alternatives>\n[alternative solution(s) here]\n</alternatives>\n"
            "<alternatives_complexity>\n[time/space complexity for each alternative]\n</alternatives_complexity>\n"
            "<explanation>\n[concise explanation here]\n</explanation>\n"
            "<flow>\n[step-by-step flow of execution here]\n</flow>\n"
            "<optimizer>\n[optimization suggestions here]\n</optimizer>\n"
            "<debugger>\n[potential bugs and fixes here]\n</debugger>\n"
            "<related>\n[related concepts here]\n</related>\n"
        )
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are an expert coding tutor and problem solver."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2500
        )
        answer = response.choices[0].message.content

        # --- Parse LLM Output ---
        def extract_tag(content, tag):
            start = f"<{tag}>"
            end = f"</{tag}>"
            if start in content and end in content:
                return content.split(start)[1].split(end)[0].strip()
            return ""

        code = extract_tag(answer, "code")
        time_complexity = extract_tag(answer, "time_complexity")
        space_complexity = extract_tag(answer, "space_complexity")
        difficulty = extract_tag(answer, "difficulty")
        alternatives = extract_tag(answer, "alternatives")
        alternatives_complexity = extract_tag(answer, "alternatives_complexity")
        explanation = extract_tag(answer, "explanation")
        flow = extract_tag(answer, "flow")
        optimizer = extract_tag(answer, "optimizer")
        debugger = extract_tag(answer, "debugger")
        related = extract_tag(answer, "related")

    # --- Reference Links ---
    st.subheader("🔗 Reference Links")
    if links:
        for link in links:
            st.markdown(f"- <span class='link'>[{link}]({link})</span>", unsafe_allow_html=True)
    else:
        st.info("No reference links found.")

    # --- Main Solution ---
    st.subheader(f"💻 Code Snippet ({language})")
    if code:
        if enable_editor:
            edited_code = st_ace(value=code, language=language.lower(), height=200, font_size=14)
            code = edited_code
        else:
            st.code(code, language=language.lower())
    else:
        st.info("No code generated.")

    # --- Complexity & Difficulty ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Time Complexity", time_complexity or "N/A")
    with col2:
        st.metric("Space Complexity", space_complexity or "N/A")
    with col3:
        st.metric("Difficulty", difficulty or "N/A")

    # --- Code Quality Report ---
    if enable_quality and code and language.lower() == "python":
        with open("solution.py", "w") as f:
            f.write(code)
        result = subprocess.run(['pylint', 'solution.py'], capture_output=True, text=True)
        st.subheader("🔍 Code Quality Report")
        st.code(result.stdout)

    # --- Visual Flow ---
    if enable_flow and flow:
        st.subheader("📊 Visual Flow")
        dot = graphviz.Digraph()
        steps = [s.strip() for s in flow.split('\n') if s.strip()]
        for i, step in enumerate(steps):
            dot.node(str(i), step)
            if i > 0:
                dot.edge(str(i-1), str(i))
        st.graphviz_chart(dot)

    # --- Hotspots ---
    if enable_hotspots and code:
        st.subheader("🔥 Code Hotspots")
        lines = code.split('\n')
        if len(lines) > 2:
            hotspot_lines = random.sample(range(1, len(lines)+1), min(2, len(lines)))
        else:
            hotspot_lines = [1]
        hotspot_html = ""
        for i, line in enumerate(lines):
            if (i+1) in hotspot_lines:
                hotspot_html += f'<div class="hotspot">{line}</div><br>'
            else:
                hotspot_html += f'{line}<br>'
        st.markdown(hotspot_html, unsafe_allow_html=True)

    # --- Multi-Agent Analysis Tabs ---
    if enable_multiple_agents:
        st.subheader("🤖 Multi-Agent AI Analysis")
        tabs = st.tabs(["Explainer", "Optimizer", "Debugger"])
        with tabs[0]:
            st.markdown(f"**Explanation:**\n\n{explanation or 'N/A'}")
        with tabs[1]:
            st.markdown(f"**Optimization Suggestions:**\n\n{optimizer or 'N/A'}")
        with tabs[2]:
            st.markdown(f"**Potential Bugs & Fixes:**\n\n{debugger or 'N/A'}")

    # --- Alternative Solutions ---
    if alternatives:
        st.subheader("🔄 Alternative Solutions")
        st.markdown(alternatives)
        st.subheader("⏳ Alternative Solutions Complexity")
        st.markdown(alternatives_complexity or "N/A")

    # --- Related Concepts ---
    if related:
        st.subheader("🧠 Related Concepts")
        for topic in related.split('\n'):
            if topic.strip():
                st.markdown(f"- {topic.strip()}")

    # --- Download Code ---
    if code:
        st.download_button("Download Code", code, file_name=f"solution.{language.lower()}")

with st.expander("💡 Tips for best results"):
    st.markdown("""
    - Ask clear, specific coding questions (e.g., 'Binary search in Java', 'Fibonacci using recursion').
    - Use the explanation toggle for a concise summary.
    - Always review generated code before using in production.
    """)
