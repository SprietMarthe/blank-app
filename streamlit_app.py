import streamlit as st
import datetime
import io
import PyPDF2
import os
from compliance_analyzer import get_gdpr_analyzer

# Initialize the GDPR compliance analyzer
@st.cache_resource
def load_analyzer():
    # Try to use Llama if available, otherwise use the fallback analyzer
    model_path = os.environ.get("LLAMA_MODEL_PATH", None)
    return get_gdpr_analyzer(use_llama=True, model_path=model_path)

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
    
    # Load the sidebar with information
    with st.sidebar:
        st.header("About this Tool")
        st.write("""
        This tool analyzes your GDPR compliance documents and provides 
        recommendations based on the latest regulations.
        
        Upload your privacy policy, data protection statement, or any 
        GDPR-related document to get started.
        """)
        
        st.header("Latest GDPR Updates")
        analyzer = load_analyzer()
        st.info(analyzer.gdpr_data["recent_changes"])
        
        # Show model information
        st.header("Technical Information")
        if hasattr(analyzer, 'model_loaded') and analyzer.model_loaded:
            st.success("✅ Using Llama model for advanced analysis")
        else:
            st.warning("⚠️ Using rule-based analysis (Llama not available)")
            
            with st.expander("How to enable Llama"):
                st.write("""
                To enable the Llama model for more sophisticated analysis:
                
                1. Install the llama-cpp-python package:
                   ```
                   pip install llama-cpp-python
                   ```
                
                2. Download a compatible Llama model and set the path:
                   ```
                   export LLAMA_MODEL_PATH=/path/to/your/llama-model.bin
                   ```
                
                3. Restart this application
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
            
        with col2:
            st.subheader("Or Paste Text")
            sample_text = st.text_area(
                "Paste document text here:", 
                height=200
            )
        
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
        elif sample_text:
            document_text = sample_text
        
        # Button to trigger analysis
        if document_text and st.button("Analyze GDPR Compliance", type="primary"):
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
            
            # Display compliance score
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
                    st.warning(f"{i+1}. {point}")
            else:
                st.success("Your document appears to cover all major GDPR compliance areas!")
                    
            # Display action plan
            st.subheader("Recommended Action Plan:")
            if action_plan:
                for i, action in enumerate(action_plan):
                    if action.startswith("- "):
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
