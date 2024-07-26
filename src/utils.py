import logging


def clean_extracted_text(text: str, limit_clean: int = 100) -> str:
    """
    Clean the extracted text.

    Notes:
        The text is cleaned by removing extra spaces and new lines.

    Args:
        text (str): Extracted text to clean.
        limit_clean (int): Number of try to clean the text extracted.

    Returns:
        str: Cleaned text.
    """
    for _ in range(limit_clean):
        old_article_text = text
        text = text.replace(" " * 2, " ")
        text = text.replace("\n" * 2, "\n")
        if old_article_text == text:
            break
    else:
        logging.warning(f"The text could not be cleaned to the limit. ({limit_clean=})")

    return text
