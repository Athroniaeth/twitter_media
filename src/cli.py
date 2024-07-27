from typer import Typer

from src.commands import extract, llm

cli = Typer(no_args_is_help=True)

cli.add_typer(extract.cli, name="extract")
cli.add_typer(llm.cli, name="generate")

if __name__ == "__main__":
    cli()
