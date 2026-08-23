LOCAL AI DOCUMENT ANALYZER
==========================

1. PROJECT OVERVIEW
-------------------
Local AI Document Analyzer is an offline document-processing prototype.

It extracts text from PDF, DOCX and image files and analyzes the
content using locally installed Ollama models.

The project does not require a cloud AI API, Open WebUI or Docker.

2. MAIN FEATURES
----------------
- Typed PDF text extraction
- Scanned PDF OCR
- Image OCR
- DOCX paragraph and table extraction
- General document summaries
- Invoice and receipt extraction
- Contract analysis
- Exam study notes
- Key findings and action items
- Custom questions
- Long-document chunking
- Downloadable analysis reports
- Local and offline AI processing

3. SUPPORTED FILE TYPES
-----------------------
- PDF
- DOCX
- PNG
- JPG
- JPEG
- WEBP
- BMP
- TIFF

4. AI MODELS
------------
Text model:
qwen3:8b

Vision and OCR model:
qwen2.5vl:7b

5. PROJECT STRUCTURE
--------------------
app.py
    Streamlit web interface.

local_ai_pipeline.py
    Document extraction, OCR, Ollama communication,
    chunking and terminal interface.

Start_Local_AI_UI.ps1
    Starts the Streamlit application.

Start_Local_AI_Pipeline.ps1
    Starts the terminal application.

requirements-ui.txt
    Packages required by the Streamlit environment.

requirements-pipeline.txt
    Packages required by the original terminal environment.

Local_AI_UI_Commands.txt
    Important Streamlit commands.

Local_AI_Pipeline_Commands.txt
    Important terminal pipeline commands.

6. SYSTEM REQUIREMENTS
----------------------
- Windows
- Ollama
- Python 3.13 ARM64 for the original pipeline
- Python 3.12 x64 for Streamlit
- At least 16 GB RAM recommended
- Required Ollama models downloaded locally

7. START THE STREAMLIT UI
-------------------------
Open PowerShell:

cd C:\AI\local-document-pipeline
.\.venv-ui\Scripts\Activate.ps1
python -m streamlit run app.py

Open:
http://localhost:8501

The launcher can also be used:

.\Start_Local_AI_UI.ps1

8. START THE TERMINAL VERSION
-----------------------------
cd C:\AI\local-document-pipeline
.\Start_Local_AI_Pipeline.ps1

9. CHECK OLLAMA
---------------
Check whether Ollama is running:

Invoke-RestMethod http://localhost:11434/api/version

Check loaded models:

ollama ps

10. APPLICATION WORKFLOW
------------------------
1. Upload a supported document.
2. Choose an analysis task.
3. Click Analyze document.
4. Review the AI analysis.
5. Review the extracted document text.
6. Download the complete report.

11. PROCESSING ARCHITECTURE
---------------------------
Uploaded document
        |
        v
File-type detection
        |
        +--> DOCX text extraction
        |
        +--> Typed PDF extraction
        |
        +--> Scanned PDF or image OCR
        |
        v
Text chunking
        |
        v
Local Ollama analysis
        |
        v
Displayed and downloadable report

12. PRIVACY
-----------
Files and AI requests are processed locally on the computer.

No cloud AI API is required for normal operation.

13. LIMITATIONS
---------------
- AI output may contain incorrect information.
- Important calculations, legal terms and dates must be verified.
- Large scanned documents may take considerable time.
- Performance depends on available RAM and CPU resources.
- The project is a hackathon prototype, not a certified
  security or defense production system.

14. CURRENT STATUS
------------------
- Terminal pipeline completed
- Streamlit interface completed
- PDF, DOCX and image processing working
- Local Ollama analysis working
- Report download working

15. FINAL TESTS TO COMPLETE
---------------------------
- Test a typed PDF
- Test a scanned PDF
- Test a DOCX file
- Test a photograph or screenshot
- Test custom questions
- Test after restarting Windows
- Confirm both PowerShell launchers work