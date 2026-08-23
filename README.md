# Local AI Document Analyzer

Offline document analysis using **Ollama, Qwen, and Streamlit**.

The application processes documents locally without requiring a cloud AI API. It automatically extracts text from supported files, uses vision OCR when necessary, and sends the extracted content to a local language model for analysis.

## Features

* Selectable PDF text extraction
* Scanned PDF OCR
* Image OCR
* DOCX paragraph and table extraction
* Automatic document-type routing
* Long-document chunking
* General summaries
* Invoice and receipt extraction
* Contract analysis
* Study notes
* Key findings and action items
* Custom document questions
* Streamlit web interface
* Downloadable analysis reports
* Local AI processing

## Supported Files

`PDF` · `DOCX` · `PNG` · `JPG` · `JPEG` · `WEBP` · `BMP` · `TIFF`

## Models

* **Text analysis:** `qwen3:8b`
* **Vision / OCR:** `qwen2.5vl:7b`

Models are served locally through [Ollama](https://ollama.com/).

## Architecture

```text
Document
   │
   ▼
File Type Detection
   │
   ├── DOCX ──────────► Text + Table Extraction
   ├── Typed PDF ─────► Embedded Text Extraction
   └── Scan / Image ──► Vision OCR
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
                 Streamlit Result + Report
```

## Quick Start

### 1. Install Ollama

Download and install Ollama, then pull the required models:

```powershell
ollama pull qwen3:8b
ollama pull qwen2.5vl:7b
```

### 2. Clone the repository

```powershell
git clone https://github.com/ZubaidaDev/local-ai-document-analyzer.git
cd local-ai-document-analyzer
```

### 3. Create the Python environment

```powershell
python -m venv .venv-ui
.\.venv-ui\Scripts\Activate.ps1
pip install -r requirements-ui.txt
```

### 4. Start the application

```powershell
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

The PowerShell launcher can also be used:

```powershell
.\Start_Local_AI_UI.ps1
```

## Usage

1. Upload a supported document.
2. Select an analysis task.
3. Click **Analyze document**.
4. Review the AI analysis or extracted text.
5. Download the complete report if required.

## Tested Environment

Development and testing were performed on:

* Windows 11 ARM64
* 16 GB RAM
* Ollama local inference
* Python 3.13 ARM64 for the original CLI pipeline
* Python 3.12 x64 for the Streamlit environment

Other compatible Python and Windows environments may also work.

## Privacy

Document extraction and AI inference are performed locally.

The normal workflow does not require:

* Cloud AI APIs
* Open WebUI
* Docker
* Uploading documents to an external AI service

## Project Structure

```text
app.py                         Streamlit interface
local_ai_pipeline.py           Extraction, OCR and AI pipeline
Start_Local_AI_UI.ps1          Streamlit launcher
Start_Local_AI_Pipeline.ps1    CLI launcher
requirements-ui.txt            UI environment dependencies
requirements-pipeline.txt      CLI environment dependencies
```

## Roadmap

* [x] Local Ollama inference
* [x] PDF text extraction
* [x] Scanned PDF OCR
* [x] Image OCR
* [x] DOCX extraction
* [x] Long-document processing
* [x] Streamlit interface
* [x] Downloadable reports
* [ ] Retrieval-Augmented Generation (RAG)
* [ ] Source/page citations
* [ ] Automated tests
* [ ] Improved configuration and logging

## Limitations

* AI-generated results may contain errors.
* Important calculations, dates, financial information, and legal terms should be independently verified.
* Large scanned documents may require significant processing time.
* Performance depends on available system memory and hardware.

This project is an applied local-AI prototype and is not a certified security or production system.
