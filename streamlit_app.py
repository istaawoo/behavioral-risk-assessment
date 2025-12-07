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
    "Analyze investment psychology and behavioral patterns to assess risk tolerance and investment style."
)

# Fixed configuration (not user-editable)
input_dir = "behavioral_data"
output_file = "output/behavioral_profile.json"
llm_enabled = False  # LLM disabled - manual analysis recommended

# Sidebar - collapsed by default with advanced options only
with st.sidebar:
    with st.expander("⚙️ Advanced Settings", expanded=False):
        st.text_input(
            "Data source",
            value=input_dir,
            disabled=True,
            help="Source directory for text analysis (configured by system)",
        )
        
        st.text_input(
            "Output location",
            value=output_file,
            disabled=True,
            help="Analysis results are saved here automatically",
        )
        
        st.divider()
        
        st.markdown("""
        **About LLM Analysis:**
        
        LLM (AI) analysis is disabled to avoid costs. For qualitative insights:
        
        1. Run the analysis to get quantitative metrics
        2. Download the raw text corpus from the Results section
        3. Copy the text and use ChatGPT/Gemini with this prompt:
        
        ```
        Analyze this investment psychology corpus and provide:
        
        1. Risk Tolerance Label: [Conservative/Moderately Conservative/Moderate/Moderately Aggressive/Aggressive]
        2. Personality Traits: [list 3-5 traits]
        3. Behavioral Biases: [list 2-4 biases]
        4. Narrative: [2-3 paragraph analysis]
        5. Portfolio Recommendations: [sectors, allocation advice]
        
        Format response as JSON matching this structure:
        {
          "risk_tolerance_label": "...",
          "traits": [...],
          "biases": [...],
          "narrative": "...",
          "recommendations": {
            "portfolio_modifier": "...",
            "sector_pref": [...],
            "notes": "..."
          }
        }
        ```
        
        4. Paste the LLM's JSON response into `output/llm_qualitative.json`
        5. Re-run analysis to merge results
        """)

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
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Words Analyzed", 
                    f"{profile.quantitative.word_count:,}",
                    help="Total words processed from all input files"
                )
            with col2:
                st.metric(
                    "Sentiment Score", 
                    f"{profile.quantitative.sentiment:.2f}",
                    help="Overall sentiment: 0=negative, 0.5=neutral, 1=positive. Measures optimism vs pessimism in language."
                )
            with col3:
                risk_label = profile.qualitative.risk_tolerance_label
                st.metric(
                    "Risk Tolerance", 
                    risk_label if len(risk_label) <= 20 else risk_label.replace("Moderately ", "Mod. "),
                    help="Investment risk profile based on behavioral patterns: Conservative → Moderate → Aggressive"
                )
            
            st.divider()
            
            # Detailed metrics
            st.subheader("📈 Behavioral Scores")
            scores = profile.quantitative.scores
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Growth Focus", 
                    f"{scores.get('growth_focus', 0):.2f}",
                    help="Preference for high-growth opportunities and scaling businesses (0=low, 1=high)"
                )
                st.metric(
                    "Momentum Bias", 
                    f"{scores.get('momentum_bias', 0):.2f}",
                    help="Tendency to follow market trends and momentum signals (0=contrarian, 1=trend-follower)"
                )
            with col2:
                st.metric(
                    "Safety Focus", 
                    f"{scores.get('safety_focus', 0):.2f}",
                    help="Emphasis on stable, defensive investments with consistent returns (0=low, 1=high)"
                )
                st.metric(
                    "Volatility Tolerance", 
                    f"{scores.get('volatility_tolerance', 0):.2f}",
                    help="Comfort level with market swings and portfolio fluctuations (0=low tolerance, 1=high tolerance)"
                )
            with col3:
                st.metric(
                    "Risk Tolerance", 
                    f"{scores.get('risk_tolerance', 0):.2f}",
                    help="Overall risk appetite: weighted combination of growth focus, momentum, sentiment, and volatility comfort"
                )
            
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
            
            # Download options
            st.subheader("📥 Download & Export")
            
            col1, col2 = st.columns(2)
            
            with col1:
                json_str = json.dumps(profile.to_dict(), indent=2)
                st.download_button(
                    label="📄 Download Full JSON Profile",
                    data=json_str,
                    file_name="behavioral_profile.json",
                    mime="application/json",
                    use_container_width=True,
                )
            
            with col2:
                # Prepare text corpus for manual LLM analysis
                try:
                    from behavioral.utils import load_text_files
                    corpus_text = load_text_files(input_dir)
                    st.download_button(
                        label="📝 Download Text Corpus (for ChatGPT/Gemini)",
                        data=corpus_text,
                        file_name="analysis_corpus.txt",
                        mime="text/plain",
                        use_container_width=True,
                        help="Download all source text to paste into ChatGPT/Gemini for qualitative analysis"
                    )
                except:
                    pass
            
            # Show JSON preview
            with st.expander("🔍 View Raw JSON Output"):
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
