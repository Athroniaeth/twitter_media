import typer
from pydantic import HttpUrl
from typer import Typer

from src.commands.callback import conf_callback
from src.commands.extract import get_content_url
from src.model import get_llm_model
from src.parser.task import summarize_text
from src.utils import valid_pydantic_type

cli = Typer(no_args_is_help=True)


@cli.command(name="create")
def create_from_article(
    config: str = typer.Option("", callback=conf_callback, is_eager=True),  # noqa
    url: str = typer.Option(..., help="URL of the article to generate tweet information."),
    model_id: str = typer.Option("mistralai/Mistral-7B-Instruct-v0.3", help="Model ID huggingface to use."),
):
    """
    Generate tweet information from an article (url).

    Args:
        url (str): URL of the article to generate tweet information.
        model_id (str): Model ID huggingface to use.
    """
    # Validation of input parameters
    valid_pydantic_type(url, HttpUrl)

    # Print the parameters
    text = get_content_url(url, 100)

    # Load the LLM for inference
    llm_model = get_llm_model(model_id)

    # Launch task summary
    summary_task = summarize_text(text, llm_model)

    # Print the summary
    typer.echo(summary_task.text_summary)
