import typer
from typing_extensions import Annotated
import os
import json

CONFIG_FILE = "healthcheck.json"

app = typer.Typer(add_completion=False)

def config_callback():
    endpoint = typer.prompt("enter the healthcheck endpoint (root url)")
    with open(CONFIG_FILE, "w") as f:
        json.dump({"endpoint": endpoint}, f, indent=2)
    raise typer.Exit()
    

@app.command()
def run(
    uuid: Annotated[str, typer.Argument(
        help="the uuid/slug of the healthcheck endpoint",
    )],
    command: Annotated[str, typer.Argument(
        help="the command to run",
    )],
    config: Annotated[bool, typer.Option(
        "--config",
        callback=config_callback,
        help="configure the healthcheck endpoint",
    )]
):
    try:
        if os.system(command) > 0:
            raise Exception("Command failed")
        typer.echo(f"Healthcheck {uuid} succeeded")
    except Exception as e:
        typer.echo(f"Healthcheck {uuid} failed: {e}")
