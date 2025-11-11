import streamlit as st
import pandas as pd

# Import the backend functions
try:
    from app_backend import run_comparison, auto_format_text, calculate_insights
except ImportError:
    st.error("FATAL: app_backend.py not found. Make sure it's in the same directory.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(page_title="Comparative Study", layout="wide")
st.title("🔍 Comparative Study: User Prompt vs System + User Prompt")

# --- Session State Initialization ---
if 'comparison_results' not in st.session_state:
    st.session_state.comparison_results = None
if 'run_comparison' not in st.session_state:
    st.session_state.run_comparison = False

# --- API Key ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Gemini API key not found. Please set `GEMINI_API_KEY` in st.secrets.")
    st.stop()

# --- Helper Functions (Frontend) ---
def clear_state_callback():
    """ Resets all relevant session state variables """
    st.session_state.comparison_results = None
    st.session_state.run_comparison = False
    # Clear text inputs by resetting their keys (if they are session state keys)
    st.session_state.user_prompt_input = "" 
    st.session_state.system_prompt_input = ""

def render_response(text: str, label: str):
    """ Pre-formats the text and renders it. """
    st.markdown(f"**{label}**")
    # Call the backend formatter
    formatted_text = auto_format_text(text)
    st.markdown(formatted_text, unsafe_allow_html=True)

def render_insights_from_dict(insights: dict):
    """ Renders the pre-calculated insights dictionary from the backend. """
    if not insights:
        st.info("Run a comparison with a system prompt to generate insights.")
        return

    st.subheader("🤖 Automated Insights & Comparison")
    
    # --- Key Metric Deltas ---
    st.markdown("##### Key Metric Changes")
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Total Tokens Change", insights["token_metric"][0], insights["token_metric"][1])
    col2.metric("Response Length Change", insights["length_metric"][0], insights["length_metric"][1])
    col3.metric("Completion Tokens Change", insights["completion_metric"][0], insights["completion_metric"][1])
    
    # --- Textual Summary ---
    st.markdown("##### Summary")
    st.write(insights["summary"])
    
    # --- Verdict ---
    st.markdown("##### Verdict")
    verdict_type = insights["verdict_type"]
    verdict_text = insights["verdict_text"]
    
    if verdict_type == "success":
        st.success(verdict_text)
    elif verdict_type == "warning":
        st.warning(verdict_text)
    else:
        st.info(verdict_text)

# --- UI Layout ---
# Input Area
user_prompt = st.text_area("✍️ Enter User Prompt", height=100, key="user_prompt_input")
system_prompt = st.text_area("⚙️ Enter System Prompt (optional)", height=100, key="system_prompt_input")

# Action Buttons
col1, col2, _ = st.columns([2, 2, 10])
if col1.button("Compare Responses", type="primary"):
    if not user_prompt.strip():
        st.warning("Please enter a User Prompt.")
    else:
        st.session_state.run_comparison = True

col2.button("Clear All", on_click=clear_state_callback)

# --- Processing and Display Logic ---
if st.session_state.run_comparison:
    with st.spinner("Calling Gemini API..."):
        try:
            # Call the single backend function to get all results
            st.session_state.comparison_results = run_comparison(
                GEMINI_API_KEY, 
                user_prompt, 
                system_prompt
            )
        except Exception as e:
            st.error(f"An unexpected error occurred in the backend: {e}")
            st.session_state.comparison_results = None

    # This ensures the spinner disappears and results are shown *after*
    # the backend call is complete.
    st.session_state.run_comparison = False 

# Display results *if* they exist in the session state
if st.session_state.comparison_results:
    results = st.session_state.comparison_results
    
    # --- Display Responses ---
    st.subheader("📌 Generated Responses")
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        render_response(results["text_a"], "A: Response (User Prompt Only)")
    with res_col2:
        render_response(results["text_b"], "B: Response (With System Prompt)")

    # --- Display Metrics Table ---
    st.subheader("📊 Key Metrics Comparison")
    metrics_a = results["metrics_a"]
    metrics_b = results["metrics_b"]
    
    if metrics_a:
        data = {
            "Metric": ["Prompt Tokens", "Completion Tokens", "Total Tokens", "Finish Reason", "Character Length"],
            "A: User-Only": [
                metrics_a.get("prompt_tokens", "-"),
                metrics_a.get("completion_tokens", "-"),
                metrics_a.get("total_tokens", "-"),
                metrics_a.get("finish_reason", "-"),
                metrics_a.get("character_length", "-"),
            ],
            "B: User+System": [
                metrics_b.get("prompt_tokens", "-"),
                metrics_b.get("completion_tokens", "-"),
                metrics_b.get("total_tokens", "-"),
                metrics_b.get("finish_reason", "-"),
                metrics_b.get("character_length", "-"),
            ],
        }
        df = pd.DataFrame(data).set_index("Metric")
        st.table(df)

    # --- Display Insights ---
    render_insights_from_dict(results["insights"])

    # --- Display Raw JSON ---
    with st.expander("Show Raw API Responses for Debugging"):
        st.json({
            "Response A (User Only)": results["json_a"],
            "Response B (User+System)": results["json_b"]
        })