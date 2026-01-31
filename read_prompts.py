
import PyPDF2
import sys

def read_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    file_path = "trae_prompts_2.pdf"
    content = read_pdf(file_path)
    with open("prompts.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("Prompts written to prompts.txt")
