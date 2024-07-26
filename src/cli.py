from typer import Typer

cli = Typer()


@cli.command()
def hello(name: str):
    print(f"Hello {name}")


@cli.command()
def goodbye(name: str):
    print(f"Goodbye {name}")


if __name__ == "__main__":
    cli()
