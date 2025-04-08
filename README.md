# GDPR Compliance Analyzer

A tool to analyze documents for GDPR compliance using Llama or rule-based analysis.

## Overview

This application helps you analyze your organization's documents for GDPR compliance. It can identify potential compliance gaps and provide recommendations based on the latest GDPR regulations.

The system can work in two modes:
1. **Llama-powered mode**: Uses the Llama language model for sophisticated analysis
2. **Fallback mode**: Uses rule-based keyword analysis when Llama isn't available

## Features

- Upload and analyze privacy policies, data protection statements, or any GDPR-related documents
- Support for various file formats: TXT, PDF
- Identify compliance gaps in key GDPR areas
- Generate actionable recommendations tailored to your document
- Score your document's GDPR compliance level
- Provide up-to-date information on GDPR requirements
- Export recommendations as a downloadable action plan

## Installation

### Basic Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/gdpr-compliance-analyzer.git
   cd gdpr-compliance-analyzer
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install streamlit PyPDF2
   ```

4. Run the application in fallback mode (no Llama required):
   ```
   streamlit run gdpr_llama_app.py
   ```

### Installing with Llama Support (Optional)

For more sophisticated analysis, you can enable Llama support:

1. Install the llama-cpp-python package:
   ```
   pip install llama-cpp-python
   ```

2. Download a compatible Llama model:
   - Option 1: Download from Hugging Face (requires account)
   - Option 2: Use a compatible quantized model

3. Set the environment variable to your model path:
   ```
   # Linux/Mac
   export LLAMA_MODEL_PATH=/path/to/your/llama-model.bin
   
   # Windows
   set LLAMA_MODEL_PATH=C:\path\to\your\llama-model.bin
   ```

4. Run the application:
   ```
   streamlit run gdpr_llama_app.py
   ```

## Using the Application

1. Open the application in your web
