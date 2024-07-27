import logging

import requests
import typer
from bs4 import BeautifulSoup
from pydantic import HttpUrl
from typer import Typer

from src.utils import clean_extracted_text, valid_pydantic_type

cli = Typer(no_args_is_help=True)


@cli.command(name="get")
def get_content_url(
    url: str = typer.Option(..., help="URL of the article to extract the content."),
    limit_clean: int = typer.Option(100, help="Number of try to clean the text extracted."),
) -> str:
    """
    Get the content of an article from a URL.

    Args:
        url (str): URL of the article to extract the content.
        limit_clean (int): Number of try to clean the text extracted
    """
    # Validation of input parameters
    valid_pydantic_type(url, HttpUrl)

    # Send a request to the URL to get the content of the article
    response = requests.get(url)

    # Check if the request is successful
    if response.status_code == 200:
        # Parser le contenu HTML de la page
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract the text from the <p> tags
        article_text = soup.text

        # Clean the text extracted
        article_text = clean_extracted_text(article_text, limit_clean)

        # Return to console the content of the article (python src ... > file.txt)
        typer.echo(article_text)

        return article_text
    else:
        logging.error(f"Failing to fetch the content of the article. ({response.status_code=})")
        raise typer.Exit(1)
