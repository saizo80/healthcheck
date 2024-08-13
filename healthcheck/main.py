import json
import logging as log
import os
import socket
import urllib.request
from os.path import dirname, expanduser, join

import typer
from typing_extensions import Annotated

CONFIG_FILE = join(expanduser("~"), ".config", "healthcheck-cli", "healthcheck.config")
log.basicConfig(level=log.WARN, format="[%(levelname)s] %(message)s")

app = typer.Typer(add_completion=False)

def config_callback(value: bool):
    if not value:
        return
    endpoint = None
    if os.path.exists(CONFIG_FILE) and os.path.isfile(CONFIG_FILE) and os.stat(CONFIG_FILE).st_size > 0:
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                endpoint = config["endpoint"]
        except:
            pass
    new_endpoint = typer.prompt(f"enter the healthcheck endpoint (root url)", default=endpoint)
    os.makedirs(dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"endpoint": new_endpoint}, f, indent=2)
    raise typer.Exit()

def send_ping(endpoint: str):
    log.debug(f"sending ping to {endpoint}")
    try:
        urllib.request.urlopen(endpoint, timeout=10)
    except socket.error as exc:
        log.error(f"Failed to connect to {endpoint}: {exc}")

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
    )] = False,
    debug: Annotated[bool, typer.Option(
        "--debug",
        help="enable debug logging",
        callback=lambda value: log.getLogger().setLevel(log.DEBUG) if value else None,
    )] = False,
):
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
            endpointBase = f"{config["endpoint"]}/ping/{uuid}"
    except FileNotFoundError:
        log.warn("no configuration found. please run the command with the --config flag")
        endpointBase = None
    except json.JSONDecodeError:
        log.error("failed to parse configuration file")
        endpointBase = None
    except PermissionError:
        log.error("failed to read configuration file")
        endpointBase = None

    try:
        if endpointBase:
            send_ping(f"{endpointBase}/start")
        status = os.system(command)
        status = status % 255
        if endpointBase:
            send_ping(f"{endpointBase}/{status}")
    except Exception as e:
        log.error(f"failed to run command: {e}")
