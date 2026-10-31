from pypdf import PdfReader


def clean_extracted_text(text):

    lines = text.splitlines()

    cleaned = []
    buffer = ""

    for line in lines:

        line = line.strip()

        if not line:
            if buffer:
                cleaned.append(buffer)
                buffer = ""

            continue

        # Single character extraction
        if len(line) == 1:
            buffer += line

        else:

            if buffer:
                cleaned.append(buffer)
                buffer = ""

            cleaned.append(line)

    if buffer:
        cleaned.append(buffer)

    return "\n".join(cleaned)


def extract_resume_text(file_path):

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text)

    full_text = "\n".join(pages)

    return clean_extracted_text(full_text)