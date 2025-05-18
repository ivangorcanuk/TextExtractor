import pytesseract
from pdf2image import convert_from_path
import logging
import os

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path, output_file="extracted_text.txt", languages="osd+eng", poppler_path=None):
    """
    Извлекает текст из PDF с использованием OCR с обработкой ошибок

    :param pdf_path: Путь к PDF файлу
    :param output_file: Файл для сохранения результата
    :param languages: Языки для OCR (формат Tesseract)
    :param poppler_path: Путь к Poppler (для Windows)
    :return: True если успешно, False если были ошибки
    """
    success = True

    try:
        # Проверка существования файла
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF файл не найден: {pdf_path}")

        # Проверка поддержки языков в Tesseract
        try:
            supported_langs = pytesseract.get_languages()
            for lang in languages.split('+'):
                if lang not in supported_langs:
                    raise ValueError(f"Язык '{lang}' не поддерживается Tesseract. Доступные языки: {supported_langs}")
        except Exception as e:
            logger.error(f"Ошибка проверки языков: {e}")
            raise

        # Конвертация PDF в изображения
        try:
            logger.info(f"Конвертация PDF в изображения...")
            images = convert_from_path(
                pdf_path,
                dpi=300,
                poppler_path=poppler_path,
                strict=False  # Более мягкая обработка поврежденных PDF
            )
            if not images:
                raise ValueError("Не удалось получить изображения из PDF (файл может быть поврежден или пуст)")
        except Exception as e:
            logger.error(f"Ошибка конвертации PDF: {e}")
            raise

        # Обработка каждой страницы
        all_text = []
        for i, image in enumerate(images):
            try:
                logger.info(f"Обработка страницы {i + 1}...")
                text = pytesseract.image_to_string(image, lang=languages)
                all_text.append(text)
                logger.debug(f"Страница {i + 1}:\n{text}\n{'-' * 50}")
            except pytesseract.TesseractError as e:
                logger.error(f"Ошибка OCR на странице {i + 1}: {e}")
                all_text.append(f"\n[ОШИБКА OCR НА СТРАНИЦЕ {i + 1}]\n")
                success = False
            except Exception as e:
                logger.error(f"Неожиданная ошибка на странице {i + 1}: {e}")
                all_text.append(f"\n[НЕИЗВЕСТНАЯ ОШИБКА НА СТРАНИЦЕ {i + 1}]\n")
                success = False

        # Сохранение результата
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(all_text))
            logger.info(f"Результат сохранен в {output_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения результата: {e}")
            raise

    except FileNotFoundError as e:
        logger.error(e)
        success = False
    except ValueError as e:
        logger.error(e)
        success = False
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
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
        print("Обработка завершена успешно!")
    else:
        print("Обработка завершена с ошибками. Проверьте лог для деталей.")