import click

from network_analyzer.analyzer import Analyzer


@click.group()
def main():
    pass


@main.command(short_help="Analyze networks")
@click.option(
    "--jsonrpc",
    help="JsonRPC URL of the ethereum client",
    default="https://tlbc.rpc.anyblock.tools",
    show_default=True,
    metavar="URL",
)
@click.option(
    "--relay",
    "relay_api_url",
    help="Relay API URL",
    default="https://tlbc.relay.anyblock.tools/api/v1",
    show_default=True,
    metavar="URL",
)
@click.option(
    "--output",
    "output_path",
    help="Path of the directory to output the csv to",
    default=None,
    type=click.Path(dir_okay=True, writable=True),
)
def analyze(jsonrpc: str, relay_api_url: str, output_path: str):

    analyzer = Analyzer(jsonrpc, output_path, relay_api_url)
    analyzer.analyze_bridge_transfers()
    analyzer.analyze_networks()
