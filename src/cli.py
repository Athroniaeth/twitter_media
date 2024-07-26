from typer import Typer

cli = Typer(no_args_is_help=True)


@cli.command()
def hello(name: str):
    """ Say hello to a name """
    print(f"Hello {name}")


@cli.command()
def goodbye(name: str):
    """ Say goodbye to a name """
    print(f"Goodbye {name}")


if __name__ == "__main__":
    cli()
