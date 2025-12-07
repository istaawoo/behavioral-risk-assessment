#  Behavioral Risk Assessment

A Streamlit-based application for analyzing investment psychology and behavioral patterns from text data.

##  Quick Start

### Installation
\\\ash
pip install -r requirements.txt
\\\

### Run Analysis
\\\ash
# Interactive UI
streamlit run behavioral/streaming_ui.py

# Or command-line (offline)
python behavioral/behavioral_runner.py --input behavioral_data --output output/behavioral_profile.json --llm-on False
\\\

##  Project Structure

behavioral/                 # Core analysis module
behavioral_data/           # Input text files
output/                    # Generated profiles

##  Documentation

See **behavioral/README.md** for comprehensive usage guide, schema details, and troubleshooting.

See **IMPLEMENTATION_SUMMARY.md** for architecture and implementation details.

##  Status

 Complete and production-ready  
 All tests passing  
 All acceptance criteria met