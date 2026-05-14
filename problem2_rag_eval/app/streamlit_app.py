import os
import logging
import sys

# Add the parent directory to sys.path to allow imports from app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.log_config import configure_global_logger
import streamlit as st
import requests

# Configure logging to console and shared file
configure_global_logger()

logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG Q&A", layout="centered")
st.title("RAG Q&A Chatbot")
st.markdown("Ask a question and get a self-corrected, evaluated answer.")

query = st.text_input("Enter your question", value="")

if st.button("Ask"):
    if not query.strip():
        logger.warning("Empty query submitted")
        st.warning("Please enter a question.")
    else:
        logger.info("Submitting question to API: '%s'", query.strip())
        with st.spinner("Generating response..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask", json={"query": query.strip()}, timeout=60
                )
                response.raise_for_status()
                data = response.json()
                logger.info("Received response from API")
                st.subheader("Answer")
                st.write(data["final_answer"])
                st.subheader("Evaluation Scores")
                st.json(data["scores"])
            except requests.RequestException as error:
                logger.error("API request failed: %s", error)
                st.error(f"Request failed: {error}")
