import os
import re
import shutil
from pypdf import PdfReader
from docx import Document

WORKSPACE_DIR = "C:/Users/Peter/agy-cli-projects"
DOCUMENTS_DIR = os.path.join(WORKSPACE_DIR, "Documents")
FINANCIAL_DIR = os.path.join(WORKSPACE_DIR, "Financial")
INVOICES_DIR = os.path.join(FINANCIAL_DIR, "Invoices")
RECEIPTS_DIR = os.path.join(FINANCIAL_DIR, "Receipts")
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "Reports")

# Ensure base directories exist
for folder in [DOCUMENTS_DIR, FINANCIAL_DIR, INVOICES_DIR, RECEIPTS_DIR, REPORTS_DIR]:
    os.makedirs(folder, exist_ok=True)

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return "\n".join(text).strip()
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading TXT {file_path}: {e}")
            return ""
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    return ""

def generate_summary(text):
    if not text:
        return "This document is empty. No main points could be extracted. Consequently, a summary is not available."
    
    # Split by sentence boundaries (crude regex split)
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= 3:
        return " ".join(sentences)
    
    # Select first three sentences as a heuristic summary
    return " ".join(sentences[:3])

def process_summarization():
    print("--- Running Summarization Step ---")
    if not os.path.exists(DOCUMENTS_DIR):
        return
        
    for item in os.listdir(DOCUMENTS_DIR):
        file_path = os.path.join(DOCUMENTS_DIR, item)
        if not os.path.isfile(file_path):
            continue
            
        # Ignore already generated summary files
        if item.startswith("summary_"):
            continue
            
        print(f"Summarizing: {item}")
        text = extract_text(file_path)
        summary = generate_summary(text)
        
        # summary_ORIGINAL_FILENAME.txt
        summary_filename = f"summary_{item}"
        if not summary_filename.endswith(".txt"):
            summary_filename += ".txt"
            
        summary_path = os.path.join(DOCUMENTS_DIR, summary_filename)
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Saved summary to {summary_filename}")

def parse_date(text):
    # Search for YYYY-MM-DD or YYYY/MM/DD
    match = re.search(r'\b(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b', text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        
    # Search for MM/DD/YYYY or DD/MM/YYYY (default to MM-DD-YYYY parser logic)
    match = re.search(r'\b(0[1-9]|[12]\d|3[01])[-/](0[1-9]|1[0-2])[-/](20\d{2})\b', text)
    if match:
        # We will assume DD-MM-YYYY or MM-DD-YYYY, convert to YYYY-MM-DD
        p1, p2, year = match.group(1), match.group(2), match.group(3)
        return f"{year}-{p2}-{p1}"
        
    # Search for word-based dates: e.g. July 26, 2025 or 26 July 2025
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    months_short = [m[:3] for m in months]
    
    text_lower = text.lower()
    for idx, month in enumerate(months):
        # Format: July 26, 2025 or Jul 26, 2025
        pattern = rf'\b({month}|{months_short[idx]})\s+(\d{{1,2}})[,\s]+(20\d{{2}})\b'
        match = re.search(pattern, text_lower)
        if match:
            day = int(match.group(2))
            year = match.group(3)
            return f"{year}-{idx+1:02d}-{day:02d}"
            
        # Format: 26 July 2025 or 26 Jul 2025
        pattern = rf'\b(\d{{1,2}})\s+({month}|{months_short[idx]})\s+(20\d{{2}})\b'
        match = re.search(pattern, text_lower)
        if match:
            day = int(match.group(1))
            year = match.group(3)
            return f"{year}-{idx+1:02d}-{day:02d}"
            
    return None

def process_categorization():
    print("\n--- Running Categorization Step ---")
    # Scan root directory for PDF/DOCX
    for item in os.listdir(WORKSPACE_DIR):
        file_path = os.path.join(WORKSPACE_DIR, item)
        if not os.path.isfile(file_path):
            continue
            
        ext = os.path.splitext(item)[1].lower()
        if ext not in ['.pdf', '.docx']:
            continue
            
        print(f"Scanning document: {item}")
        text = extract_text(file_path)
        content_and_name = (item + " " + text).lower()
        
        target_dir = None
        if "invoice" in content_and_name:
            target_dir = INVOICES_DIR
            print(f"-> Categorized as Invoice")
        elif "receipt" in content_and_name:
            target_dir = RECEIPTS_DIR
            print(f"-> Categorized as Receipt")
        elif ext == '.docx':
            target_dir = REPORTS_DIR
            print(f"-> Categorized as Report")
            
        if target_dir:
            dest_path = os.path.join(target_dir, item)
            shutil.move(file_path, dest_path)
            print(f"Moved {item} to {os.path.basename(target_dir)}")

def process_renaming():
    print("\n--- Running Invoice Renaming Step ---")
    if not os.path.exists(INVOICES_DIR):
        return
        
    for item in os.listdir(INVOICES_DIR):
        file_path = os.path.join(INVOICES_DIR, item)
        if not os.path.isfile(file_path) or not item.lower().endswith(".pdf"):
            continue
            
        # If it already matches the date pattern, skip
        if re.match(r'^invoice_\d{4}-\d{2}-\d{2}_', item):
            continue
            
        text = extract_text(file_path)
        date_str = parse_date(text)
        
        if date_str:
            new_name = f"invoice_{date_str}_{item}"
            new_path = os.path.join(INVOICES_DIR, new_name)
            os.rename(file_path, new_path)
            print(f"Renamed {item} to {new_name}")
        else:
            print(f"No date found in invoice: {item}")

if __name__ == "__main__":
    process_summarization()
    process_categorization()
    process_renaming()
    print("\nProcessing complete!")
