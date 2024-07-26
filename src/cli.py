import logging
import tomllib
from enum import StrEnum
from types import SimpleNamespace

import typer
from pydantic import HttpUrl
from transformers.utils import logging as logging_hf
from typer import Typer

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
        quantization_int4: bool = typer.Option(True, help="Active the 4-bit quantization."),
        local: bool = typer.Option(False, help="Active the local mode to load the model."),
):
    """
    Generate tweet information from an article (url).

    Args:
        url_article (str): URL of the article to generate tweet information.
        model_id (str): Model ID huggingface to use.
        quantization_int4 (bool): Active the 4-bit quantization.
        local (bool): Active the local mode to load the model.

    Returns:
        None
    """
    # Validation of input parameters
    if HttpUrl(url_article) is None:
        typer.echo(f"Invalid URL: {url_article}")
        raise typer.Exit(1)

    # Print the parameters
    typer.echo(f"URL article: {url_article}")
    typer.echo(f"Model ID: {model_id}")
    typer.echo(f"Quantization int4: {quantization_int4}")
    typer.echo(f"Local: {local}")
    typer.echo()


if __name__ == "__main__":
    cli()
