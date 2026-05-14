import os
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import streamlit as st
import requests
import json

from app.log_config import configure_global_logger

load_dotenv()
configure_global_logger()

logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Multi-Agent Report Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 Multi-Agent Content Synthesizer & Fact-Checker")
st.markdown("""
Generate comprehensive technical reports by synthesizing data from multiple sources 
with automatic fact verification across sources.
""")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    api_url = st.text_input("API URL", value=API_URL)
    
    st.markdown("---")
    st.subheader("About")
    st.markdown("""
    This tool orchestrates multiple AI agents to:
    1. **Ingest** data from PDFs, web links, and JSON logs
    2. **Deduplicate** semantically similar content
    3. **Extract** facts and entities
    4. **Verify** facts across sources
    5. **Synthesize** a final markdown report with citations
    """)

# Main content
st.header("Report Generation")

# Report topic
report_topic = st.text_input(
    "Report Topic",
    value="Technical Analysis Report",
    help="The main topic or title for your report"
)

# Sources section
st.subheader("Data Sources")
st.markdown("Add one or more sources to process (PDFs, web links, JSON files, or text files)")

num_sources = st.number_input("Number of sources", min_value=1, max_value=10, value=1)

sources = []
cols = st.columns([0.3, 0.3, 0.4])

with cols[0]:
    st.caption("Source Type")
with cols[1]:
    st.caption("Location (path or URL)")
with cols[2]:
    st.caption("")

for i in range(num_sources):
    col1, col2, col3 = st.columns([0.3, 0.3, 0.4])
    
    with col1:
        source_type = st.selectbox(
            f"Type {i+1}",
            options=["pdf", "web", "json", "text"],
            key=f"source_type_{i}",
            label_visibility="collapsed"
        )
    
    with col2:
        if source_type == "web":
            location = st.text_input(
                f"URL {i+1}",
                placeholder="https://example.com",
                key=f"source_url_{i}",
                label_visibility="collapsed"
            )
        else:
            location = st.text_input(
                f"Path {i+1}",
                placeholder=f"/path/to/file.{source_type}",
                key=f"source_path_{i}",
                label_visibility="collapsed"
            )
    
    with col3:
        st.empty()
    
    if location:
        sources.append({
            "type": source_type,
            "path": location if source_type != "web" else None,
            "url": location if source_type == "web" else None
        })

# Generate button
if st.button("🚀 Generate Report", type="primary", use_container_width=True):
    if not sources:
        st.error("Please provide at least one source")
    elif not report_topic:
        st.error("Please provide a report topic")
    else:
        try:
            with st.spinner("Processing sources and generating report..."):
                # Call API
                response = requests.post(
                    f"{api_url}/generate-report",
                    json={
                        "sources": sources,
                        "topic": report_topic
                    },
                    timeout=300
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info("Report generated successfully")
                
                # Display results
                st.success("✅ Report generated successfully!")
                
                # Tabs for different views
                tab1, tab2, tab3 = st.tabs(["📄 Report", "📊 Statistics", "🔍 Metadata"])
                
                with tab1:
                    st.markdown(result.get("report", ""))
                
                with tab2:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Facts", result.get("facts_count", 0))
                    with col2:
                        st.metric("Verified Facts", result.get("verified_count", 0))
                    with col3:
                        pipeline_stats = result.get("pipeline_stats", {})
                        dedup_ratio = (
                            pipeline_stats.get("input_chunks", 0) - 
                            pipeline_stats.get("deduplicated_chunks", 0)
                        )
                        st.metric("Duplicates Removed", dedup_ratio)
                    
                    st.subheader("Pipeline Statistics")
                    pipeline_stats = result.get("pipeline_stats", {})
                    for key, value in pipeline_stats.items():
                        st.write(f"- **{key.replace('_', ' ').title()}**: {value}")
                
                with tab3:
                    st.subheader("Report Metadata")
                    st.json({
                        "topic": result.get("topic"),
                        "generated_at": result.get("generated_at"),
                        "sources_processed": len(sources)
                    })
                
                # Download button
                report_text = result.get("report", "")
                st.download_button(
                    label="📥 Download Report (Markdown)",
                    data=report_text,
                    file_name=f"report_{report_topic.replace(' ', '_')}.md",
                    mime="text/markdown"
                )
        
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to API at {api_url}. Make sure the backend is running.")
            logger.error("Connection error to API")
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ API Error: {e.response.json().get('detail', str(e))}")
            logger.error("API error: %s", e)
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
            logger.error("Unexpected error: %s", e)

# Footer
st.markdown("---")
st.markdown("Multi-Agent Content Synthesizer v1.0 | Powered by LangChain & Google Gemini")
