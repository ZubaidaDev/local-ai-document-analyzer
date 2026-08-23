from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from local_ai_pipeline import (
    PipelineError,
    TEXT_MODEL,
    VISION_MODEL,
    analyze_long_text,
    extract_document_text,
)


MAX_FILE_SIZE_MB = 25

TASK_PROMPTS = {
    "General summary": (
        "Summarize the document clearly. Include the main points, "
        "important details and final conclusions."
    ),
    "Extract invoice or receipt details": (
        "Extract all invoice or receipt information. Include vendor, "
        "customer, invoice number, date, line items, quantities, prices, "
        "subtotal, tax, total amount, payment method and any missing fields."
    ),
    "Analyze a contract": (
        "Analyze this contract. Identify the parties, responsibilities, "
        "payment terms, dates, penalties, renewal and termination terms, "
        "risks, unusual clauses and required actions. Do not provide a "
        "definitive legal opinion."
    ),
    "Create study notes": (
        "Create concise exam study notes. Cover every question, show the "
        "correct formula and calculation, and finish with a short revision "
        "summary. Avoid repetition and unnecessary examples."
    ),
    "Key findings and action items": (
        "List the key findings and important details. Include significant "
        "names, dates, amounts, requirements, risks and action items."
    ),
}


def initialize_state() -> None:
    """Create Streamlit session variables when the app first starts."""

    defaults = {
        "analysis_result": None,
        "extracted_text": None,
        "report_content": None,
        "download_filename": None,
        "processed_filename": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_previous_result() -> None:
    """Remove the previous result before starting another analysis."""

    st.session_state.analysis_result = None
    st.session_state.extracted_text = None
    st.session_state.report_content = None
    st.session_state.download_filename = None
    st.session_state.processed_filename = None


def create_report(
    extracted_text: str,
    analysis_result: str,
) -> str:
    """Create the downloadable text report."""

    return (
        "EXTRACTED DOCUMENT TEXT\n"
        "=======================\n\n"
        f"{extracted_text}\n\n\n"
        "AI ANALYSIS\n"
        "===========\n\n"
        f"{analysis_result}\n"
    )


st.set_page_config(
    page_title="Local AI Document Analyzer",
    page_icon="📄",
    layout="wide",
)

initialize_state()

st.title("Local AI Document Analyzer")

st.caption(
    "Extract and analyze PDF, DOCX and image files locally using Ollama."
)

st.info(
    "Files are processed on this computer. "
    "Docker and Open WebUI are not required."
)

with st.sidebar:
    st.header("System information")

    st.write(f"**Text model:** `{TEXT_MODEL}`")
    st.write(f"**Vision model:** `{VISION_MODEL}`")

    st.write(
        "**Supported files:** PDF, DOCX, PNG, JPG, "
        "JPEG, WEBP, BMP and TIFF"
    )

    st.write(f"**Maximum UI file size:** {MAX_FILE_SIZE_MB} MB")

uploaded_file = st.file_uploader(
    "Upload a document",
    type=[
        "pdf",
        "docx",
        "png",
        "jpg",
        "jpeg",
        "webp",
        "bmp",
        "tiff",
    ],
)

task_name = st.selectbox(
    "Choose an analysis task",
    [
        "General summary",
        "Extract invoice or receipt details",
        "Analyze a contract",
        "Create study notes",
        "Key findings and action items",
        "Custom question",
    ],
)

custom_question = ""

if task_name == "Custom question":
    custom_question = st.text_area(
        "Enter your question or instructions",
        placeholder=(
            "Example: Identify all payment deadlines "
            "and responsible parties."
        ),
    )

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_size_mb = len(file_bytes) / (1024 * 1024)
    extension = Path(uploaded_file.name).suffix.lower()

    st.success(f"Selected file: {uploaded_file.name}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "File type",
            extension.upper(),
        )

    with col2:
        st.metric(
            "File size",
            f"{file_size_mb:.2f} MB",
        )

    with col3:
        st.metric(
            "Processing",
            "Local",
        )

    file_too_large = file_size_mb > MAX_FILE_SIZE_MB

    if file_too_large:
        st.error(
            f"The file is larger than {MAX_FILE_SIZE_MB} MB. "
            "Choose a smaller file for this prototype."
        )

    analyze_clicked = st.button(
        "Analyze document",
        type="primary",
        use_container_width=True,
        disabled=file_too_large,
    )

    if analyze_clicked:
        if (
            task_name == "Custom question"
            and not custom_question.strip()
        ):
            st.warning("Enter a custom question first.")

        else:
            clear_previous_result()

            if task_name == "Custom question":
                task_prompt = custom_question.strip()
            else:
                task_prompt = TASK_PROMPTS[task_name]

            temporary_path: Path | None = None

            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    suffix=extension,
                    delete=False,
                ) as temporary_file:
                    temporary_file.write(file_bytes)
                    temporary_path = Path(temporary_file.name)

                with st.status(
                    "Processing document...",
                    expanded=True,
                ) as status:
                    st.write(
                        "1. Reading the uploaded document..."
                    )

                    extracted_text = extract_document_text(
                        temporary_path
                    )

                    st.write(
                        "2. Text extraction completed: "
                        f"{len(extracted_text):,} characters."
                    )

                    st.write(
                        f"3. Analyzing with `{TEXT_MODEL}`..."
                    )

                    analysis_result = analyze_long_text(
                        extracted_text,
                        task_prompt,
                    )

                    report_content = create_report(
                        extracted_text,
                        analysis_result,
                    )

                    st.session_state.extracted_text = (
                        extracted_text
                    )
                    st.session_state.analysis_result = (
                        analysis_result
                    )
                    st.session_state.report_content = (
                        report_content
                    )
                    st.session_state.download_filename = (
                        f"{Path(uploaded_file.name).stem}"
                        "_analysis.txt"
                    )
                    st.session_state.processed_filename = (
                        uploaded_file.name
                    )

                    status.update(
                        label="Analysis completed",
                        state="complete",
                        expanded=False,
                    )

            except PipelineError as exc:
                st.error(f"Pipeline error: {exc}")

            except Exception as exc:
                st.error(
                    "An unexpected error occurred: "
                    f"{exc}"
                )

            finally:
                if temporary_path is not None:
                    try:
                        temporary_path.unlink(
                            missing_ok=True
                        )
                    except OSError:
                        pass

else:
    st.warning("Upload a document to continue.")

if st.session_state.analysis_result:
    st.divider()

    st.subheader(
        f"Result: {st.session_state.processed_filename}"
    )

    analysis_tab, extracted_tab = st.tabs(
        [
            "AI analysis",
            "Extracted document text",
        ]
    )

    with analysis_tab:
        st.markdown(
            st.session_state.analysis_result
        )

    with extracted_tab:
        st.text_area(
            "Extracted text",
            value=st.session_state.extracted_text,
            height=450,
            disabled=True,
        )

    st.download_button(
        label="Download complete report",
        data=st.session_state.report_content,
        file_name=st.session_state.download_filename,
        mime="text/plain",
        type="primary",
        use_container_width=True,
    )

    st.caption(
        "AI-generated results may contain mistakes. "
        "Verify important calculations, dates and legal information."
    )