import pytesseract
from pdf2image import convert_from_path
import logging
import os

# Configuring logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path, output_file="extracted_text.txt", languages="osd+eng", poppler_path=None):
    """
    Extracts text from PDF using OCR with error handling

    pdf_path: The path to the PDF file
    output_file: File to save the result
    languages: Languages for OCR (Tesseract format)
    poppler_path: The path to Poppler
    return: True if successful, False if there were errors
    """
    success = True

    try:
        # Checking the existence of a file
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"The PDF file was not found: {pdf_path}")

        # Checking language support in Tesseract
        try:
            supported_langs = pytesseract.get_languages()
            for lang in languages.split('+'):
                if lang not in supported_langs:
                    raise ValueError(f"The language '{lang}' is not supported by Tesseract. Available languages: {supported_langs}")
        except Exception as e:
            logger.error(f"Language verification error: {e}")
            raise

        # Converting PDF to Images
        try:
            logger.info(f"Convert PDF to images...")
            images = convert_from_path(
                pdf_path,
                dpi=300,
                poppler_path=poppler_path,
                strict=False  # Softer handling of corrupted PDFs
            )
            if not images:
                raise ValueError("Couldn't get images from PDF (file may be corrupted or empty)")
        except Exception as e:
            logger.error(f"PDF conversion error: {e}")
            raise

        # Processing of each page
        all_text = []
        for i, image in enumerate(images):
            try:
                logger.info(f"Page processing {i + 1}...")
                text = pytesseract.image_to_string(image, lang=languages)
                all_text.append(text)
                logger.debug(f"Page {i + 1}:\n{text}\n{'-' * 50}")
            except pytesseract.TesseractError as e:
                logger.error(f"OCR error on the page {i + 1}: {e}")
                all_text.append(f"\n[OCR ERROR ON THE PAGE {i + 1}]\n")
                success = False
            except Exception as e:
                logger.error(f"Unexpected error on the page {i + 1}: {e}")
                all_text.append(f"\n[UNKNOWN ERROR ON THE PAGE {i + 1}]\n")
                success = False

        # Saving the result
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(all_text))
            logger.info(f"The result is saved in {output_file}")
        except Exception as e:
            logger.error(f"Error saving the result: {e}")
            raise

    except FileNotFoundError as e:
        logger.error(e)
        success = False
    except ValueError as e:
        logger.error(e)
        success = False
    except Exception as e:
        logger.error(f"Critical error: {e}")
        success = False

    return success


if __name__ == "__main__":
    poppler_path = r"C:\Release-24.08.0-0\poppler-24.08.0\Library\bin"
    pdf_path = "docs\example.pdf"

    result = extract_text_from_pdf(
        pdf_path=pdf_path,
        poppler_path=poppler_path,
        languages="osd+eng"
    )

    if result:
        print("Processing completed successfully!")
    else:
        print("The processing was completed with errors. Check the log for details.")