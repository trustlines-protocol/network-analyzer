import click
from web3 import Web3


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
    envvar="JSONRPC",
)
def analyze(jsonrpc: str,):
    web3 = Web3(Web3.HTTPProvider(jsonrpc, request_kwargs={"timeout": 180}))
    last_block_number = web3.eth.blockNumber
    click.echo("Successfully connected to web3")
    click.echo(f"Last block number fetched from web3: {last_block_number}")
