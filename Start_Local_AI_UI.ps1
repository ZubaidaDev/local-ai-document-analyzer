Set-Location "C:\AI\local-document-pipeline"

& ".\.venv\Scripts\python.exe" `
    -m streamlit run app.py

Read-Host "Press Enter to close"