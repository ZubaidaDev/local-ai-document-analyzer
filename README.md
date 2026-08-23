# Local AI Document Analyzer

Local document analysis using **Ollama, Qwen, and Streamlit**.

The application extracts text from documents, uses vision OCR when needed, and analyzes the content locally without relying on a cloud AI API.

## Features

* PDF and DOCX text extraction
* Scanned PDF and image OCR
* Automatic file-type processing
* Long-document chunking
* Document summaries
* Invoice and receipt extraction
* Contract analysis
* Study notes
* Key findings and action items
* Custom document questions
* Streamlit interface
* Downloadable reports

## Supported Files

`PDF` · `DOCX` · `PNG` · `JPG` · `JPEG` · `WEBP` · `BMP` · `TIFF`

## Models

* **Text:** `qwen3:8b`
* **Vision / OCR:** `qwen2.5vl:7b`

Models run locally through [Ollama](https://ollama.com/).

## Architecture

```text
Document
   │
   ▼
File Type Detection
   │
   ├── DOCX ─────────► Text Extraction
   ├── Typed PDF ────► Text Extraction
   └── Scan / Image ─► Vision OCR
                         │
                         ▼
                   Extracted Text
                         │
                         ▼
                      Chunking
                         │
                         ▼
                  Local LLM Analysis
                         │
                         ▼
                  Streamlit Output
```

## Quick Start

### 1. Install Ollama and models

```powershell
ollama pull qwen3:8b
ollama pull qwen2.5vl:7b
```

### 2. Clone the repository

```powershell
git clone https://github.com/ZubaidaDev/local-ai-document-analyzer.git
cd local-ai-document-analyzer
```

### 3. Create the environment

```powershell
python -m venv .venv-ui
.\.venv-ui\Scripts\Activate.ps1
pip install -r requirements-ui.txt
```

### 4. Run the application

```powershell
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Usage

1. Upload a supported document.
2. Select an analysis task.
3. Click **Analyze document**.
4. Review the extracted text and AI analysis.
5. Download the report if needed.

## Privacy

Document extraction and AI inference are performed locally.

The normal workflow does not require:

* Cloud AI APIs
* Docker
* Open WebUI
* External document uploads

## Project Structure

```text
app.py                         Streamlit interface
local_ai_pipeline.py           Document processing and AI pipeline
Start_Local_AI_UI.ps1          Streamlit launcher
Start_Local_AI_Pipeline.ps1    CLI launcher
requirements-ui.txt            UI dependencies
requirements-pipeline.txt      CLI dependencies
```

## Limitations

* AI-generated results may contain errors.
* Important calculations, dates, financial details, and legal information should be verified.
* Large scanned documents may take longer to process.
* Performance depends on available hardware.

This project is an applied local-AI prototype intended for experimentation and development.
