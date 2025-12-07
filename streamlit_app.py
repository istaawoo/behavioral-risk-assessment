"""
Streamlit UI for Behavioral Risk Analysis.

Simple interface to load local files, run analysis, and download results.
"""
import streamlit as st
import json
from pathlib import Path
import sys

# Add behavioral module to path
sys.path.insert(0, str(Path(__file__).parent / "behavioral"))

from behavioral.behavioral_runner import run_analysis


st.set_page_config(
    page_title="Behavioral Risk Analysis",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Behavioral Risk Assessment")
st.markdown(
    "Analyze investment psychology and behavioral biases from local text data."
)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    input_dir = st.text_input(
        "Input directory (relative path)",
        value="behavioral_data",
        help="Directory containing .txt files to analyze",
    )
    
    output_file = st.text_input(
        "Output file",
        value="output/behavioral_profile.json",
        help="Where to save the analysis result",
    )
    
    llm_enabled = st.checkbox(
        "Enable LLM Analysis",
        value=False,
        help="Call LLM for qualitative insights (requires API key)",
    )
    
    if llm_enabled:
        st.info(
            "⚠️ LLM cost: ~$0.01-0.50 per analysis depending on model and text length. "
            "Set LLM_API_KEY environment variable to enable."
        )

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 Input Files")
    
    # Show available input files
    input_path = Path(input_dir)
    if input_path.exists():
        txt_files = list(input_path.glob("*.txt"))
        if txt_files:
            st.success(f"Found {len(txt_files)} file(s):")
            for f in txt_files:
                st.text(f"  • {f.name}")
        else:
            st.warning(f"No .txt files found in {input_dir}")
    else:
        st.error(f"Directory {input_dir} does not exist")

with col2:
    st.subheader("⚙️ Output Configuration")
    st.text(f"Output file: {output_file}")
    st.text(f"LLM enabled: {llm_enabled}")

# Run button
st.divider()

if st.button("🚀 Run Analysis", use_container_width=True, type="primary"):
    with st.spinner("Running analysis..."):
        try:
            profile = run_analysis(
                input_dir=input_dir,
                output_file=output_file,
                llm_enabled=llm_enabled,
            )
            
            st.success("✅ Analysis complete!")
            
            # Display results
            st.subheader("📊 Results Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Words Analyzed", profile.quantitative.word_count)
            with col2:
                st.metric("Sentences", profile.quantitative.sentence_count)
            with col3:
                st.metric("Sentiment Score", f"{profile.quantitative.sentiment:.3f}")
            with col4:
                st.metric("Risk Tolerance", profile.qualitative.risk_tolerance_label)
            
            st.divider()
            
            # Detailed metrics
            st.subheader("📈 Behavioral Scores")
            scores = profile.quantitative.scores
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Growth Focus", f"{scores.get('growth_focus', 0):.3f}")
                st.metric("Momentum Bias", f"{scores.get('momentum_bias', 0):.3f}")
            with col2:
                st.metric("Safety Focus", f"{scores.get('safety_focus', 0):.3f}")
                st.metric("Volatility Tolerance", f"{scores.get('volatility_tolerance', 0):.3f}")
            
            st.divider()
            
            # Keyword mentions
            st.subheader("🔤 Keyword Mentions")
            mentions = profile.quantitative.mentions
            col1, col2 = st.columns(2)
            with col1:
                for cat, count in list(mentions.items())[:3]:
                    st.text(f"{cat}: {count}")
            with col2:
                for cat, count in list(mentions.items())[3:]:
                    st.text(f"{cat}: {count}")
            
            st.divider()
            
            # Qualitative analysis
            if profile.qualitative.narrative:
                st.subheader("📝 Qualitative Analysis")
                st.markdown(f"**Risk Tolerance:** {profile.qualitative.risk_tolerance_label}")
                
                if profile.qualitative.traits:
                    st.markdown(f"**Traits:** {', '.join(profile.qualitative.traits)}")
                
                if profile.qualitative.biases:
                    st.markdown(f"**Biases:** {', '.join(profile.qualitative.biases)}")
                
                if profile.qualitative.narrative:
                    st.markdown(f"**Narrative:**\n{profile.qualitative.narrative}")
            
            st.divider()
            
            # Download JSON
            st.subheader("📥 Download Results")
            json_str = json.dumps(profile.to_dict(), indent=2)
            st.download_button(
                label="Download JSON Profile",
                data=json_str,
                file_name="behavioral_profile.json",
                mime="application/json",
                use_container_width=True,
            )
            
            # Show JSON preview
            with st.expander("View Raw JSON"):
                st.json(profile.to_dict())
        
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.info("Check the input directory and ensure .txt files are present.")

# Footer
st.divider()
st.markdown(
    """
    **About:**
    This tool analyzes behavioral patterns in text to assess investment psychology.
    It computes quantitative metrics and optionally uses LLM for qualitative insights.
    
    **Input:** Text files in the specified directory  
    **Output:** JSON profile with scores, sentiment, and recommendations
    """
)
