from __future__ import annotations

import base64
import io
import sys
from pathlib import Path
from typing import Optional

import pypdfium2 as pdfium
import requests
from docx import Document
from docx.table import Table
from PIL import Image
from pypdf import PdfReader


OLLAMA_CHAT_API = "http://localhost:11434/api/chat"

TEXT_MODEL = "qwen3:8b"
VISION_MODEL = "qwen2.5vl:7b"

MIN_EXTRACTED_CHARACTERS = 100
PDF_RENDER_SCALE = 2.0
TEXT_CHUNK_SIZE = 8_000
REQUEST_TIMEOUT_SECONDS = 600


class PipelineError(RuntimeError):
    """Raised when local document processing fails."""


def call_ollama(
    model: str,
    prompt: str,
    image_bytes: Optional[bytes] = None,
) -> str:
    """Send a text or vision request to Ollama."""

    message: dict = {
        "role": "user",
        "content": prompt,
    }

    if image_bytes is not None:
        message["images"] = [
            base64.b64encode(image_bytes).decode("utf-8")
        ]

    try:
        response = requests.post(
            OLLAMA_CHAT_API,
            json={
                "model": model,
                "messages": [message],
                "stream": False,
                "keep_alive": "2m",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        raise PipelineError(
            f"Ollama request failed: {exc}"
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise PipelineError(
            "Ollama returned an invalid response."
        ) from exc

    try:
        return payload["message"]["content"].strip()
    except (KeyError, TypeError) as exc:
        raise PipelineError(
            f"Unexpected Ollama response: {payload}"
        ) from exc


def extract_selectable_pdf_text(
    pdf_path: Path,
) -> Optional[str]:
    """Extract embedded text from a normal typed PDF."""

    try:
        reader = PdfReader(str(pdf_path))
        pages: list[str] = []

        for page in reader.pages:
            page_text = page.extract_text() or ""

            if page_text.strip():
                pages.append(page_text.strip())

    except Exception as exc:
        raise PipelineError(
            f"Could not read PDF text: {exc}"
        ) from exc

    text = "\n\n".join(pages).strip()

    if len(text) >= MIN_EXTRACTED_CHARACTERS:
        return text

    return None


def extract_docx_text(docx_path: Path) -> str:
    """
    Extract paragraphs and tables from a DOCX file
    while preserving their document order.
    """

    try:
        document = Document(str(docx_path))
        extracted_parts: list[str] = []

        for block in document.iter_inner_content():
            if isinstance(block, Table):
                table_rows: list[str] = []

                for row in block.rows:
                    cells = [
                        cell.text.strip()
                        for cell in row.cells
                    ]

                    if any(cells):
                        table_rows.append(" | ".join(cells))

                if table_rows:
                    extracted_parts.append(
                        "\n".join(table_rows)
                    )

            else:
                paragraph_text = block.text.strip()

                if paragraph_text:
                    extracted_parts.append(paragraph_text)

    except Exception as exc:
        raise PipelineError(
            f"Could not read DOCX file: {exc}"
        ) from exc

    text = "\n\n".join(extracted_parts).strip()

    if not text:
        raise PipelineError(
            "No readable paragraphs or table text were found "
            "in the DOCX file."
        )

    return text


def render_pdf_page_as_png(
    pdf: pdfium.PdfDocument,
    page_index: int,
) -> bytes:
    """Render one PDF page into PNG bytes."""

    page = None
    bitmap = None

    try:
        page = pdf[page_index]
        bitmap = page.render(scale=PDF_RENDER_SCALE)
        image = bitmap.to_pil().convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        return buffer.getvalue()

    except Exception as exc:
        raise PipelineError(
            f"Could not render PDF page {page_index + 1}: {exc}"
        ) from exc

    finally:
        if bitmap is not None:
            bitmap.close()

        if page is not None:
            page.close()


def ocr_image_bytes(
    image_bytes: bytes,
    page_label: str,
) -> str:
    """Extract visible text using Qwen2.5-VL."""

    prompt = (
        f"Perform accurate OCR on {page_label}. "
        "Transcribe all visible text in reading order. "
        "Preserve headings, lists, tables, numbers and line structure. "
        "Do not summarize. Do not invent missing text."
    )

    return call_ollama(
        model=VISION_MODEL,
        prompt=prompt,
        image_bytes=image_bytes,
    )


def ocr_scanned_pdf(pdf_path: Path) -> str:
    """Render and OCR every page of a scanned PDF."""

    extracted_pages: list[str] = []
    pdf = None

    try:
        pdf = pdfium.PdfDocument(str(pdf_path))
        total_pages = len(pdf)

        for page_index in range(total_pages):
            page_number = page_index + 1

            print(
                f"OCR page {page_number} of {total_pages}...",
                flush=True,
            )

            image_bytes = render_pdf_page_as_png(
                pdf,
                page_index,
            )

            page_text = ocr_image_bytes(
                image_bytes,
                page_label=f"page {page_number}",
            )

            extracted_pages.append(
                f"--- Page {page_number} ---\n{page_text}"
            )

    except PipelineError:
        raise

    except Exception as exc:
        raise PipelineError(
            f"Scanned PDF OCR failed: {exc}"
        ) from exc

    finally:
        if pdf is not None:
            pdf.close()

    return "\n\n".join(extracted_pages)


def load_image_as_png(image_path: Path) -> bytes:
    """Convert a supported image into PNG bytes."""

    try:
        with Image.open(image_path) as image:
            image = image.convert("RGB")

            buffer = io.BytesIO()
            image.save(buffer, format="PNG")

            return buffer.getvalue()

    except Exception as exc:
        raise PipelineError(
            f"Could not open image: {exc}"
        ) from exc


def extract_document_text(file_path: Path) -> str:
    """
    Automatically choose DOCX extraction,
    PDF extraction, PDF OCR, or image OCR.
    """

    extension = file_path.suffix.lower()

    if extension == ".docx":
        print(
            "Word document detected. "
            "Extracting paragraphs and tables."
        )

        return extract_docx_text(file_path)

    if extension == ".pdf":
        selectable_text = extract_selectable_pdf_text(
            file_path
        )

        if selectable_text:
            print(
                "Selectable PDF detected. "
                "Extracting embedded text."
            )

            return selectable_text

        print(
            "Scanned PDF detected. "
            "Running page-by-page OCR."
        )

        return ocr_scanned_pdf(file_path)

    if extension in {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
        ".tiff",
    }:
        print("Image detected. Running vision OCR.")

        image_bytes = load_image_as_png(file_path)

        return ocr_image_bytes(
            image_bytes,
            page_label=file_path.name,
        )

    raise PipelineError(
        "Unsupported file type. Use DOCX, PDF, PNG, JPG, JPEG, "
        "WEBP, BMP or TIFF."
    )


def split_text(
    text: str,
    chunk_size: int = TEXT_CHUNK_SIZE,
) -> list[str]:
    """Divide long text without deleting later sections."""

    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # Handle an individual paragraph longer than the chunk size.
        while len(paragraph) > chunk_size:
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_length = 0

            chunks.append(paragraph[:chunk_size])
            paragraph = paragraph[chunk_size:].strip()

        if not paragraph:
            continue

        added_length = len(paragraph) + 2

        if (
            current
            and current_length + added_length > chunk_size
        ):
            chunks.append("\n\n".join(current))
            current = []
            current_length = 0

        current.append(paragraph)
        current_length += added_length

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def choose_task() -> str:
    """Let the user choose how the extracted document should be analyzed."""

    tasks = {
        "1": (
            "Summarize the document clearly. Include the main points, "
            "important details and final conclusions."
        ),
        "2": (
            "Extract all invoice or receipt information. Include vendor, "
            "customer, invoice number, date, line items, quantities, prices, "
            "subtotal, tax, total amount, payment method and any missing fields."
        ),
        "3": (
            "Analyze this contract. Identify the parties, responsibilities, "
            "payment terms, dates, penalties, renewal and termination terms, "
            "risks, unusual clauses and required actions. Do not provide a "
            "definitive legal opinion."
        ),
        "4": (
            "Create concise exam study notes. Cover every question, show the "
            "correct formula and calculation, and finish with a short revision "
            "summary. Avoid repetition and unnecessary examples."
        ),
        "5": (
            "List the key findings and important details. Include significant "
            "names, dates, amounts, requirements, risks and action items."
        ),
    }

    print("\nChoose an analysis task:")
    print("1. General summary")
    print("2. Extract invoice or receipt details")
    print("3. Analyze a contract")
    print("4. Create study notes")
    print("5. Key findings and action items")
    print("6. Ask a custom question")

    while True:
        choice = input("\nEnter choice 1-6: ").strip()

        if choice in tasks:
            return tasks[choice]

        if choice == "6":
            custom_task = input(
                "Enter your question or instructions: "
            ).strip()

            if custom_task:
                return custom_task

            print("The custom question cannot be empty.")
            continue

        print("Invalid choice. Enter a number from 1 to 6.")


def analyze_long_text(
    text: str,
    task: str,
) -> str:
    """Analyze all text chunks, then combine the findings."""

    chunks = split_text(text)

    if not chunks:
        raise PipelineError(
            "No usable text was available for analysis."
        )

    partial_results: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        print(
            f"Analyzing section {index} of {len(chunks)}...",
            flush=True,
        )

        prompt = (
            f"{task}\n\n"
            f"This is document section {index} of {len(chunks)}.\n"
            "Use only the supplied document text. "
            "Clearly identify uncertainty.\n\n"
            f"DOCUMENT TEXT:\n{chunk}"
        )

        result = call_ollama(
            model=TEXT_MODEL,
            prompt=prompt,
        )

        partial_results.append(result)

    if len(partial_results) == 1:
        return partial_results[0]

    combined = "\n\n".join(
        f"SECTION {index}\n{result}"
        for index, result
        in enumerate(partial_results, start=1)
    )

    final_prompt = (
        "Combine the following section-level findings into one accurate, "
        "non-repetitive final report. Preserve important names, numbers, "
        "dates, warnings and conclusions. Do not add unsupported facts.\n\n"
        f"{combined}"
    )

    return call_ollama(
        model=TEXT_MODEL,
        prompt=final_prompt,
    )


def main() -> int:
    raw_path = input(
        "Enter the DOCX, PDF or image path: "
    ).strip().strip('"')

    file_path = Path(raw_path).expanduser()

    if not file_path.is_file():
        print(f"File not found: {file_path}")
        return 1

    print("\nProcessing document...\n")

    try:
        text = extract_document_text(file_path)

        print("\nExtracted text preview:")
        print("-" * 60)
        print(text[:500])
        print("-" * 60)

        task = choose_task()

        result = analyze_long_text(
            text,
            task,
        )

    except PipelineError as exc:
        print(f"\nError: {exc}")
        return 1

    print("\nFINAL RESULT")
    print("=" * 60)
    print(result)

    output_path = file_path.with_name(
        f"{file_path.stem}_analysis.txt"
    )

    output_content = (
        "EXTRACTED DOCUMENT TEXT\n"
        "=======================\n\n"
        f"{text}\n\n\n"
        "AI ANALYSIS\n"
        "===========\n\n"
        f"{result}\n"
    )

    try:
        output_path.write_text(
            output_content,
            encoding="utf-8",
        )

    except OSError as exc:
        print(
            "\nThe analysis completed, but the result "
            f"could not be saved: {exc}"
        )
        return 1

    print(f"\nSaved result to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())