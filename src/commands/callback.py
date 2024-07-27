import logging
import tomllib
from enum import StrEnum
from types import SimpleNamespace

import typer
from transformers.utils import logging as logging_hf

cli = typer.Typer(
    no_args_is_help=True,
)


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
