from typing import Type

from pydantic import BaseModel


def get_helper_output_parser(pydantic_object: Type[BaseModel]):
    """
    Fournit le début du JSON attendus par le parser.

    Args:
        pydantic_object (BaseModel): Modèle Pydantic attendu par le OutputParser

    Notes:
        Cela permet d'éviter les erreurs de génération avec les petits modèles
    """
    first_attr = list(pydantic_object.__dict__["model_fields"].keys())[0]
    return f"""```{{\"{first_attr}\": """
