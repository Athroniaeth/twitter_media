import logging
import tomllib
from enum import StrEnum
from types import SimpleNamespace

import requests
import typer
from bs4 import BeautifulSoup
from pydantic import HttpUrl
from transformers.utils import logging as logging_hf
from typer import Typer

from src.model import get_llm_model
from src.parser.task import summarize_text
from src.utils import clean_extracted_text, valid_pydantic_type

cli = Typer(no_args_is_help=True)


class Level(StrEnum):
    """Log levels for the application."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@cli.callback()
def callback(
    ctx: typer.Context,
    hf_token: str = typer.Option(None, envvar="HF_TOKEN", help="Access token for Hugging Face API."),
    logging_level: Level = typer.Option(Level.ERROR, help="Log level for application logs."),
    logging_level_hf: Level = typer.Option(Level.ERROR, help="Log level for Hugging Face logs."),
):
    """
    Initialize the CLI application context.

    Args:
        ctx (typer.Context): Command context.
        hf_token (str): Access token for Hugging Face API.
        logging_level (Level): Log level for application logs.
        logging_level_hf (Level): Log level for Hugging Face logs.

    Raises:
        typer.Exit: If Hugging Face token is missing.

    Returns:
        SimpleNamespace: Object containing application parameters.
    """
    logging_level = logging.getLevelName(logging_level)
    logging_level_hf = logging.getLevelName(logging_level_hf)

    logging.basicConfig(level=logging_level)
    logging_hf.get_logger().setLevel(logging_level_hf)

    if hf_token is None:
        logging.exception("Missing Hugging Face token; pass --hf-token or set env[HF_TOKEN]")
        raise typer.Exit(1)

    logging.debug(f"Evironment variable 'HF_TOKEN' : {hf_token}")

    ctx.obj = SimpleNamespace(hf_token=hf_token, logging_level=logging_level, logging_level_hf=logging_level_hf)


def conf_callback(ctx: typer.Context, param: typer.CallbackParam, filepath: str) -> str:
    """
    Load a configuration file and update the default map.

    References:
         https://github.com/tiangolo/typer/issues/86

    Args:
        ctx (typer.Context): Command context.
        param (typer.CallbackParam): Callback parameter.
        filepath (str): Path to the configuration file.

    Returns:
        str: Path to the configuration file.
    """
    if filepath:
        try:
            # Load the configuration file
            with open(filepath, "rb") as file:
                conf = tomllib.load(file)

            # Init the dictionary and update the default map
            ctx.default_map = ctx.default_map or {}
            ctx.default_map.update(conf)
        except Exception as ex:
            raise typer.BadParameter(str(ex))

    return filepath


@cli.command()
def create_from_article(
    config: str = typer.Option("", callback=conf_callback, is_eager=True),  # noqa: Parameter 'config' value is not used
    url_article: str = typer.Option(..., help="URL of the article to generate tweet information."),
    model_id: str = typer.Option("meta-llama/Meta-Llama-3-8B-Instruct", help="Model ID huggingface to use."),
):
    """
    Generate tweet information from an article (url).

    Args:
        url_article (str): URL of the article to generate tweet information.
        model_id (str): Model ID huggingface to use.

    Returns:
        None
    """
    # Validation of input parameters
    valid_pydantic_type(url_article, HttpUrl)

    # Print the parameters
    text = get_content_url(url_article, 100)

    # Load the LLM for inference
    llm_model = get_llm_model(model_id)

    # Launch task summary
    summary_task = summarize_text(text, llm_model)

    # Print the summary
    typer.echo(summary_task.text_summary)


@cli.command()
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
        list_text = (tag.get_text() for tag in soup.find_all("p"))
        article_text = "\n".join(list_text)

        # Clean the text extracted
        article_text = clean_extracted_text(article_text, limit_clean)

        # Return to console the content of the article (python src ... > file.txt)
        typer.echo(article_text)

        return article_text
    else:
        logging.error(f"Failing to fetch the content of the article. ({response.status_code=})")
        raise typer.Exit(1)


if __name__ == "__main__":
    cli()
