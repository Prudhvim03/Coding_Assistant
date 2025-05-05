import streamlit as st
from tavily import TavilyClient
from groq import Groq
import os
from dotenv import load_dotenv

# --- Page Config ---
st.set_page_config(
    page_title="CodeQ: AI Coding Assistant",
    page_icon="🧑‍💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Env Vars ---
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- THEMES ---
THEMES = {
    "Neon": {
        "primary": "#1E88E5",
        "secondary": "#00B0FF",
        "accent": "#4CA1AF",
        "background": "linear-gradient(135deg, #1E88E5 0%, #00B0FF 50%, #4CA1AF 100%)",
        "card_bg": "rgba(255, 255, 255, 0.2)",
        "text": "white",
        "text_on_primary": "black"
    },
    "Sunset": {
        "primary": "#FF7043",
        "secondary": "#8D6E63",
        "accent": "#4CA1AF",
        "background": "linear-gradient(135deg, #8D6E63 0%, #8D6E63 25%, #4CA1AF 75%, #4CA1AF 100%)",
        "card_bg": "rgba(255, 255, 255, 0.2)",
        "text": "white",
        "text_on_primary": "white"
    },
    "Cyber": {
        "primary": "#BB86FC",
        "secondary": "#03D8F4",
        "accent": "#03D8F4",
        "background": "linear-gradient(135deg, #121212 0%, #1E1E1E 50%, #03D8F4 100%)",
        "card_bg": "rgba(30, 30, 30, 0.7)",
        "text": "#E0E0E0",
        "text_on_primary": "black"
    },
    "Forest": {
        "primary": "#388E3C",
        "secondary": "#81C784",
        "accent": "#FFD600",
        "background": "linear-gradient(135deg, #388E3C 0%, #81C784 100%)",
        "card_bg": "rgba(255, 255, 255, 0.15)",
        "text": "white",
        "text_on_primary": "black"
    },
    "Ocean": {
        "primary": "#0288D1",
        "secondary": "#26C6DA",
        "accent": "#00B8D4",
        "background": "linear-gradient(135deg, #0288D1 0%, #00B8D4 100%)",
        "card_bg": "rgba(255, 255, 255, 0.12)",
        "text": "white",
        "text_on_primary": "black"
    },
    "Lavender": {
        "primary": "#9575CD",
        "secondary": "#D1C4E9",
        "accent": "#F8BBD0",
        "background": "linear-gradient(135deg, #9575CD 0%, #F8BBD0 100%)",
        "card_bg": "rgba(255, 255, 255, 0.18)",
        "text": "#2D133B",
        "text_on_primary": "white"
    },
    "Solarized": {
        "primary": "#268BD2",
        "secondary": "#2AA198",
        "accent": "#B58900",
        "background": "linear-gradient(135deg, #073642 0%, #268BD2 100%)",
        "card_bg": "rgba(38, 139, 210, 0.12)",
        "text": "#FDF6E3",
        "text_on_primary": "#073642"
    },
    "Candy": {
        "primary": "#FF6F91",
        "secondary": "#FF9671",
        "accent": "#FFC75F",
        "background": "linear-gradient(135deg, #FF6F91 0%, #FF9671 50%, #FFC75F 100%)",
        "card_bg": "rgba(255, 255, 255, 0.25)",
        "text": "#4A1A1A",
        "text_on_primary": "white"
    }
}

# --- Sidebar: Settings ---
with st.sidebar:
    st.title("⚙️ Settings")
    theme_name = st.selectbox("Theme", list(THEMES.keys()))
    language = st.selectbox(
        "Programming Language",
        ["Python", "Java", "C", "C++", "JavaScript", "Go", "Rust"]
    )
    show_explanation = st.checkbox("Show Explanation", value=True)
    show_flow = st.checkbox("Show Execution Flow", value=True)
    st.markdown("---")
    if not TAVILY_API_KEY:
        TAVILY_API_KEY = st.text_input("Tavily API Key", type="password", key="tavily_key")
    if not GROQ_API_KEY:
        GROQ_API_KEY = st.text_input("Groq API Key", type="password", key="groq_key")

theme = THEMES[theme_name]

# --- Custom CSS for Section Patterns ---
css = f"""
<style>
:root {{
  --primary: {theme['primary']};
  --secondary: {theme['secondary']};
  --accent: {theme['accent']};
  --background: {theme['background']};
  --card-bg: {theme['card_bg']};
  --text: {theme['text']};
  --text-on-primary: {theme['text_on_primary']};
}}
.stApp {{
  background: var(--background);
  color: var(--text);
}}
/* General card style */
.card {{
  border-radius: 16px;
  margin: 18px 0 18px 0;
  padding: 18px 22px;
  color: var(--text);
  position: relative;
  overflow: hidden;
}}
/* Section-specific patterns */
.pattern-header {{
  background: repeating-linear-gradient(135deg, var(--primary), var(--primary) 10px, var(--secondary) 10px, var(--secondary) 20px);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 25px 20px 15px 20px;
  font-size: 2.1rem;
  font-weight: bold;
  letter-spacing: 2px;
  position: relative;
}}
.pattern-links {{
  background: radial-gradient(circle at 20% 40%, var(--accent) 10%, transparent 70%), var(--card-bg);
  border-left: 8px solid var(--primary);
}}
.pattern-code {{
  background: linear-gradient(120deg, var(--primary) 20%, var(--secondary) 100%);
  box-shadow: 0 4px 24px 0 var(--accent);
  color: var(--text-on-primary);
}}
.pattern-metrics {{
  background: repeating-linear-gradient(90deg, var(--secondary), var(--secondary) 8px, transparent 8px, transparent 16px), var(--card-bg);
  border-radius: 16px;
}}
.pattern-explanation {{
  background: repeating-linear-gradient(45deg, var(--accent), var(--accent) 8px, transparent 8px, transparent 16px), var(--card-bg);
}}
.pattern-flow {{
  background: radial-gradient(circle, var(--primary) 0%, var(--secondary) 100%);
  color: var(--text-on-primary);
}}
.pattern-alternatives {{
  background: repeating-linear-gradient(135deg, var(--secondary), var(--secondary) 10px, transparent 10px, transparent 20px), var(--card-bg);
}}
/* Prudhvi badge */
.prudhvi-badge {{
  position: absolute;
  top: 8px;
  right: 18px;
  background: var(--accent);
  color: var(--text-on-primary);
  border-radius: 12px;
  padding: 4px 16px;
  font-size: 0.9rem;
  font-weight: bold;
  box-shadow: 0 2px 10px 0 rgba(0,0,0,0.08);
  z-index: 2;
}}
/* Footer */
.footer {{
  text-align: center;
  font-size: 0.9em;
  color: var(--accent);
  margin-top: 2em;
  margin-bottom: 1em;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Main UI ---
st.markdown(f"""
<div class="card pattern-header" style="margin-bottom:0;">
  <span>🧑‍💻 CodeQ: AI Coding Assistant</span>
  <span class="prudhvi-badge">Created by Ƥ𝔯ü𝑑hѵ𝖎</span>
</div>
""", unsafe_allow_html=True)
st.caption("Ask any coding question and get code, explanations, reference links, and more!")

# --- Question Input ---
with st.container():
    st.markdown('<div class="card" style="background: var(--card-bg);">', unsafe_allow_html=True)
    question = st.text_area(
        "📝 **Enter your coding question** (like GeeksforGeeksLeetCode, etc. questions):",
        height=80,
        placeholder="e.g., Reverse a linked list in Python"
    )
    col_q1, col_q2 = st.columns([4,1])
    with col_q2:
        get_answer = st.button("Get Answer", use_container_width=True)
    st.markdown('<span class="prudhvi-badge">Created by Ƥ𝔯ü𝑑hѵ𝖎</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def extract_tag(content, tag):
    start = f"<{tag}>"
    end = f"</{tag}>"
    if start in content and end in content:
        return content.split(start)[1].split(end)[0].strip()
    return ""

if get_answer and question.strip():
    # --- Reference Links & LLM ---
    with st.spinner("🔎 Searching for reference links..."):
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        response = tavily_client.search(question)
        links = [result["url"] for result in response.get("results", [])[:5]]

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
        )
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are an expert coding tutor and problem solver."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        answer = response.choices[0].message.content

        code = extract_tag(answer, "code")
        time_complexity = extract_tag(answer, "time_complexity")
        space_complexity = extract_tag(answer, "space_complexity")
        difficulty = extract_tag(answer, "difficulty")
        alternatives = extract_tag(answer, "alternatives")
        alternatives_complexity = extract_tag(answer, "alternatives_complexity")
        explanation = extract_tag(answer, "explanation")
        flow = extract_tag(answer, "flow")

    # --- Reference Links ---
    st.markdown('<div class="card pattern-links"><span class="prudhvi-badge">Created by Prudhvi</span>', unsafe_allow_html=True)
    st.subheader("🔗 Reference Links")
    if links:
        for link in links:
            st.markdown(f"- <span class='link'>[{link}]({link})</span>", unsafe_allow_html=True)
    else:
        st.info("No reference links found.")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Main Solution ---
    st.markdown(f'<div class="card pattern-code"><span class="prudhvi-badge">Created by Ƥ𝔯ü𝑑hѵ𝖎</span>', unsafe_allow_html=True)
    st.subheader(f"💻 Code Snippet ({language})")
    if code:
        st.code(code, language=language.lower())
    else:
        st.info("No code generated.")
    if code:
        st.download_button("⬇️ Download Code", code, file_name=f"solution.{language.lower()}")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Complexity & Difficulty ---
    st.markdown('<div class="card pattern-metrics"><span class="prudhvi-badge">Created by Ƥ𝔯ü𝑑hѵ𝖎</span>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Time Complexity", time_complexity or "N/A")
    with col2:
        st.metric("Space Complexity", space_complexity or "N/A")
    with col3:
        st.metric("Difficulty", difficulty or "N/A")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Explanation & Flow ---
    if show_explanation and explanation:
        st.markdown('<div class="card pattern-explanation"><span class="prudhvi-badge">Created by Ƥ𝔯ü𝑑hѵ𝖎</span>', unsafe_allow_html=True)
        st.subheader("📝 Explanation")
        st.markdown(explanation)
        st.markdown('</div>', unsafe_allow_html=True)
    if show_flow and flow:
        st.markdown('<div class="card pattern-flow"><span class="prudhvi-badge">Created by Ƥ𝔯ü𝑑hѵ𝖎</span>', unsafe_allow_html=True)
        st.subheader("🔍 Flow of Execution")
        st.markdown(flow)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Alternative Solutions ---
    if alternatives:
        st.markdown('<div class="card pattern-alternatives"><span class="prudhvi-badge">Created by Ƥ𝔯ü𝑑hѵ𝖎</span>', unsafe_allow_html=True)
        st.subheader("🔄 Alternative Solutions")
        st.markdown(alternatives)
        st.subheader("⏳ Alternative Solutions Complexity")
        st.markdown(alternatives_complexity or "N/A")
        st.markdown('</div>', unsafe_allow_html=True)

# --- Tips ---
with st.expander("💡 Tips for best results"):
    st.markdown("""
    - Ask clear, specific coding questions (e.g., 'Binary search in Java', 'Fibonacci using recursion').
    - Use the explanation toggle for a concise summary.
    - Always review generated code before using in production.
    """)
    st.markdown('<span class="prudhvi-badge">Created by Prudhvi</span>', unsafe_allow_html=True)

st.markdown("""<div class="footer">
</div>""", unsafe_allow_html=True)
