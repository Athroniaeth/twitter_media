import logging
from typing import Any, Type


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
        text = text.replace("\n ", "\n")
        text = text.strip()

        if old_article_text == text:
            break
    else:
        logging.warning(f"The text could not be cleaned to the limit. ({limit_clean=})")

    return text


def valid_pydantic_type(value: Any, pydantic_type: Type) -> None:
    """
    Check if the value is a valid Pydantic type.

    Args:
        value (Any): Value to check.
        pydantic_type (Type[BaseModel]): Pydantic type to check.

    Returns:
        bool: True if the value is a valid Pydantic type.
    """
    # Valid value with Pydantic type
    if pydantic_type(value) is None:
        logging.error(f"Value '{value}' is not a valid Pydantic type '{pydantic_type}'.")
        raise ValueError(f"Value '{value}' is not a valid Pydantic type '{pydantic_type}'.")
