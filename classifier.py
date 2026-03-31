import logging
from pathlib import Path
import pdfplumber

# Course patterns mapping
COURSE_PATTERNS = {
    "COS201": ["COS201", "COS 201", "Computer Architecture"],
    "SEN201": ["SEN201", "SEN 201", "Software Engineering"],
    "MTH201": ["MTH201", "MTH 201", "Mathematical Methods"],
    "IFT211": ["IFT211", "IFT 211", "Digital Logic"],
    "CSC201": ["CSC201", "CSC 201", "Computer Programming"],
    "GST212": ["GST212", "GST 212", "Philosophy"],
}

logger = logging.getLogger("classifier")

def detect_course_from_filename(filename: str) -> str | None:
    """Matches filename (case-insensitive) against COURSE_PATTERNS."""
    fn_lower = filename.lower()
    for course, patterns in COURSE_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in fn_lower:
                return course
    return None

def detect_course_from_pdf(file_path: str, max_pages: int = 3) -> str | None:
    """Extracts text from PDF and matches against patterns."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for i in range(min(max_pages, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + " "
            
            if not text:
                return None
            
            text_lower = text.lower()
            for course, patterns in COURSE_PATTERNS.items():
                for pattern in patterns:
                    if pattern.lower() in text_lower:
                        return course
    except Exception as e:
        logger.warning(f"PDF text extraction failed: {e}")
    return None

def classify(file_path: str) -> str:
    """Classifies file. Priority: Filename > PDF content > UNSORTED."""
    path_obj = Path(file_path)
    filename = path_obj.name

    course = detect_course_from_filename(filename)
    if course:
        logger.info(f"Classified {filename} via filename as {course}")
        return course

    if path_obj.suffix.lower() == ".pdf":
        course = detect_course_from_pdf(file_path)
        if course:
            logger.info(f"Classified {filename} via PDF content as {course}")
            return course

    logger.info(f"Classified {filename} as UNSORTED")
    return "UNSORTED"

# Assumptions:
# - Filename patterns are unique enough for basic classification.
# - pdfplumber handles standard text-based PDFs.
