import streamlit as st
from openai import OpenAI
from PIL import Image

# Set page
st.set_page_config(page_title="Doctor - Documentation Generator", layout="wide")

# Load and display logo (top-right)
logo = Image.open("logo.png")
col1, col2 = st.columns([8, 1])
with col2:
    st.image(logo, width=100)

# Sidebar tools
st.sidebar.title("🔧 Options")

# Language and depth
language = st.sidebar.selectbox(
    "💻 Language",
    options=["Python", "R", "Julia", "JavaScript"]
)

doc_depth = st.sidebar.selectbox(
    "📚 Documentation Style",
    options=["Simple", "Detailed", "Expert"],
    index=1
)

download_doc = st.sidebar.button("📥 Download .md")
generate_req = st.sidebar.button("📦 Generate requirements.txt")
remove_hardcoding = st.sidebar.button("🚫 Remove Hardcoding")
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

# Apply dark mode
if dark_mode:
    st.markdown(
        """
        <style>
        body {
            background-color: #0e1117;
            color: #f5f5f5;
        }
        .stTextArea textarea {
            background-color: #1c1f26;
            color: #f5f5f5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Code input section
st.title("🧠 Generate Code Documentation Here")
code = st.text_area(f"Paste your {language} code here:", height=300)

# Inline disclaimer
st.markdown(
    "*⚠️ AI can make mistakes. Please review all generated documentation before using it in production.*",
    unsafe_allow_html=True
)

# Generate button
generate_doc = st.button("📝 Generate Documentation")

# Output placeholders
doc_output = st.empty()
req_output = st.empty()
warning_placeholder = st.empty()

# OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Function to call OpenAI ---
def query_openai(prompt, system_msg="You are a helpful assistant."):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# --- Prompt templates by depth ---
def build_prompt(language, depth, code):
    if depth == "Simple":
        return f"Write a basic explanation of this {language} code:\n\n{code}"
    elif depth == "Detailed":
        return f"""
Generate well-structured, developer-friendly documentation for the following {language} code.

- Describe its purpose and major components
- Highlight logic, functions, or unique constructs
- Explain inputs and outputs
- Mention key libraries or dependencies
- Use Markdown formatting with bullet points and headers if helpful

Code:
{code}
"""
    elif depth == "Expert":
        return f"""
You are a senior software architect reviewing this {language} code.

Write highly technical documentation that explains:

- Architecture, structure, and data flow
- Performance considerations or edge cases
- Dependency choices and alternative approaches
- Input/output handling and configurability
- Potential enhancements or scalability concerns

Respond in well-formatted Markdown.

Code:
{code}
"""
    return code

# --- Main Logic ---

# Generate Documentation
if generate_doc and code.strip():
    with st.spinner("Generating documentation..."):
        prompt = build_prompt(language, doc_depth, code)
        result = query_openai(prompt, f"You are an expert {language} developer writing documentation.")
        st.session_state["doc"] = result
        doc_output.subheader("📄 Generated Documentation")
        doc_output.markdown(result)

# Download Markdown
if download_doc and "doc" in st.session_state:
    st.download_button("Download Markdown", st.session_state["doc"], file_name="documentation.md")

# Generate requirements.txt
if generate_req and code:
    with st.spinner("Generating dependency list..."):
        prompt = f"Generate a list of dependencies or packages used in this {language} code:\n\n{code}"
        result = query_openai(prompt, f"You are a {language} expert generating a dependency list.")
        req_output.subheader(f"📦 Dependencies ({language})")
        req_output.code(result, language="bash")
        st.download_button("Download", result, file_name="dependencies.txt")

# Remove Hardcoding
if remove_hardcoding and code:
    warning_placeholder.warning("⚠️ Removing hardcoded variables may change your code behavior. Review carefully!")
    with st.spinner("Removing hardcoded values..."):
        result = query_openai(
            f"Remove all hardcoded values from this {language} code and replace them with variables or configuration constants:\n\n{code}",
            f"You are a {language} developer refactoring code to remove hardcoded values."
        )
        st.subheader("🧹 Cleaned Code (No Hardcoding)")
        st.code(result, language=language.lower())
        st.download_button("Download Cleaned Code", result, file_name=f"cleaned_code.{language.lower()[:2]}")
