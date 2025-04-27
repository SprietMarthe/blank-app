import streamlit as st
import datetime
import io
import PyPDF2
import os
try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False
    print("Warning: 'replicate' package not available. LLM analysis will be disabled.")
from compliance_analyzer import get_gdpr_analyzer


# TODO: Path to your file
api_token_file_path = 'replicate_api.txt'

# Read the API token from the file
try:
    with open(api_token_file_path, 'r') as file:
        api_token = file.read().strip()
    
    # Set the API token as an environment variable
    os.environ["REPLICATE_API_TOKEN"] = api_token
    print("API Token set successfully from replicate_api.txt.")
except FileNotFoundError:
    print(f"Error: The file '{api_token_file_path}' was not found.")
except Exception as e:
    print(f"Error reading or setting the API token: {e}")



# Initialize the GDPR compliance analyzer
@st.cache_resource
def load_analyzer():
    # Try to use Replicate API if available, otherwise use the fallback analyzer
    api_token = os.environ.get("REPLICATE_API_TOKEN", None)
    # If not in environment, check if it was stored in session state
    if api_token is None and "replicate_api_token" in st.session_state:
        api_token = st.session_state.replicate_api_token
    
    # Get the use_web_scraper setting from session state
    use_web_scraper = st.session_state.get("use_web_scraper", True)
        
    return get_gdpr_analyzer(use_replicate=True, api_token=api_token, use_web_scraper=use_web_scraper)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text





# Streamlit UI
def main():
    st.set_page_config(
        page_title="GDPR Compliance Analyzer",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📄 GDPR Compliance Analysis Tool")
    
    # Initialize session state for API token if not already set
    if "replicate_api_token" not in st.session_state:
        st.session_state.replicate_api_token = ""

    if "use_web_scraper" not in st.session_state:
        st.session_state.use_web_scraper = True
    
    if "gdpr_web_data" not in st.session_state:
        st.session_state.gdpr_web_data = None
    
    # Load the sidebar with information
    with st.sidebar:
        st.header("About this Tool")
        st.write("""
        This tool analyzes your GDPR compliance documents and provides 
        recommendations based on the latest regulations.
        
        Upload your privacy policy, data protection statement, or any 
        GDPR-related document to get started.
        """)
        
        # Check if API token file was found
        api_token_file_found = os.path.exists(api_token_file_path)
        
        # Only show API token input if file wasn't found and no token is in session state
        if not api_token_file_found and not os.environ.get("REPLICATE_API_TOKEN"):
            st.subheader("Replicate API")
            api_token_input = st.text_input(
                "Enter Replicate API Token",
                type="password",
                value=st.session_state.replicate_api_token,
                help="Get your API token from Replicate.com"
            )
            
            if api_token_input and api_token_input != st.session_state.replicate_api_token:
                st.session_state.replicate_api_token = api_token_input
                # Set environment variable
                os.environ["REPLICATE_API_TOKEN"] = api_token_input
                st.rerun()  # Reload the app to use the new API token
        
        st.header("Latest GDPR Updates")
        analyzer = load_analyzer()
        st.info(analyzer.gdpr_data["recent_changes"])
        
        # Show model information
        st.header("Technical Information")
        if hasattr(analyzer, 'model_loaded') and analyzer.model_loaded:
            st.success(f"✅ Using {analyzer.model_name} via Replicate for advanced analysis")
            st.write("The analyzer is using Replicate API to provide sophisticated analysis of your GDPR documents.")
        else:
            st.warning("⚠️ Using rule-based analysis (Replicate API not available)")
            
            with st.expander("How to enable Replicate API"):
                st.write("""
                To enable the Llama model for more sophisticated analysis:
                
                1. Sign up for Replicate at: https://replicate.com/
                2. Obtain an API token from your account settings
                3. Enter your API token in the text box above
                
                Alternatively, you can set the REPLICATE_API_TOKEN environment variable before starting the app.
                """)
                
                st.write("""
                You will also need to install the LangChain packages:
                ```
                pip install langchain langchain-community
                ```
                """)

    # Main content
    tab1, tab2 = st.tabs(["Document Analysis", "GDPR Requirements Reference"])
    
    with tab1:
        st.header("Document Analysis")
        
        # Input options
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Upload Document")
            uploaded_file = st.file_uploader(
                "Upload your GDPR compliance document", 
                type=["txt", "pdf", "docx"]
            )
            
        # with col2:
        #     st.subheader("Or Paste Text")
        #     sample_text = st.text_area(
        #         "Paste document text here:", 
        #         height=200
        #     )
        
        # Initialize the analyzer
        analyzer = load_analyzer()
        
        # Check if a file is uploaded or text is pasted
        document_text = None
        
        if uploaded_file is not None:
            st.success("File uploaded successfully!")
            # Process the file based on its type
            if uploaded_file.name.endswith('.pdf'):
                with st.spinner("Extracting text from PDF..."):
                    document_text = extract_text_from_pdf(uploaded_file)
                    st.info(f"Extracted {len(document_text)} characters from PDF.")
            else:  # Assume it's a text file
                document_text = uploaded_file.getvalue().decode("utf-8")
                
            # Show a preview of the document
            with st.expander("Document Preview"):
                st.text(document_text[:1000] + ("..." if len(document_text) > 1000 else ""))
        # elif sample_text:
        #     document_text = sample_text
        
        # Button to trigger analysis
        if document_text and st.button("Analyze GDPR Compliance", type="primary"):
            if not hasattr(analyzer, 'model_loaded') or not analyzer.model_loaded:
                st.warning("⚠️ LLM analysis not available. Using basic rule-based analysis instead.")
                
            with st.spinner("Analyzing your document..."):
                # Show a progress bar for visual feedback
                progress_bar = st.progress(0)
                for i in range(100):
                    # Update progress bar
                    progress_bar.progress(i + 1)
                
                # Analyze the document
                weak_points, action_plan = analyzer.analyze_document(document_text)
            
            # Display results
            st.header("Analysis Results")
            
            # Display document stats
            st.subheader("Document Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Document Length", f"{len(document_text)} characters")
            with col2:
                st.metric("Word Count", f"{len(document_text.split())} words")
            
            # Display compliance score # TODO 
            if weak_points:
                compliance_score = max(10, 100 - (len(weak_points) * 15))
            else:
                compliance_score = 100
                
            st.subheader("GDPR Compliance Score")
            score_color = "green" if compliance_score >= 80 else "orange" if compliance_score >= 50 else "red"
            st.markdown(
                f"""
                <div style="background-color: {score_color}; padding: 10px; border-radius: 5px; text-align: center;">
                    <h1 style="color: white;">{compliance_score}%</h1>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display weak points
            st.subheader("Identified Compliance Gaps:")
            if weak_points:
                for i, point in enumerate(weak_points):
                    if isinstance(point, dict):
                        # Extract formatted text from the dictionary
                        if 'area' in point and 'description' in point:
                            formatted_point = f"{point['area']}: {point['description']}"
                        else:
                            # Fallback for other dictionary formats
                            formatted_point = str(point)
                        st.warning(f"{i+1}. {formatted_point}")
                    else:
                        # Handle strings as before
                        st.warning(f"{i+1}. {point}")
            else:
                st.success("Your document appears to cover all major GDPR compliance areas!")
            
            # Display action plan
            st.subheader("Recommended Action Plan:")
            if action_plan:
                for i, action in enumerate(action_plan):
                    if isinstance(action, dict):
                        # Extract formatted text from the dictionary
                        if 'area' in action and 'action' in action:
                            formatted_action = f"{action['area']}: {action['action']}"
                        else:
                            # Fallback for other dictionary formats
                            formatted_action = str(action)
                            
                        if formatted_action.startswith("- "):
                            st.write(f"  {formatted_action}")
                        else:
                            st.write(f"{i+1}. {formatted_action}")
                    elif isinstance(action, str) and action.startswith("- "):
                        st.write(f"  {action}")
                    else:
                        st.write(f"{i+1}. {action}")
                
                # Add a download button for the action plan
                action_plan_text = "\n".join([f"{i+1}. {action}" for i, action in enumerate(action_plan)])
                st.download_button(
                    label="Download Action Plan",
                    data=action_plan_text,
                    file_name=f"gdpr_action_plan_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            else:
                st.info("No specific actions needed. Your document appears to be GDPR compliant.")
    
    with tab2:
        st.header("GDPR Requirements Reference")
        
        # Show key GDPR requirements
        st.subheader("Key GDPR Requirements")
        for req in analyzer.gdpr_data["key_requirements"]:
            st.write(f"• {req}")
        
        # Show common weak points
        st.subheader("Common GDPR Compliance Issues")
        for category, description in analyzer.gdpr_data["common_weak_points"].items():
            with st.expander(f"{description}"):
                st.write("Recommended actions:")
                for action in analyzer.gdpr_data["action_templates"][category]:
                    st.write(f"• {action}")
        
        # Show recent changes
        st.subheader("Recent GDPR Changes")
        st.info(analyzer.gdpr_data["recent_changes"])

if __name__ == "__main__":
    main()
