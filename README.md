# network-analyzer

Tool around fetching and computing information on the status of currency networks as a graph and their users.


## Installation

The network analyzer tool requires python 3.8 or up. You can install its requirements from this repository with
`pip install -r dev-requirements.txt`. You can then install the network analyzer with `pip install .`.
You can verify it was correctly installed by printing the help, e.g. `network-analyzer analyze --help`

## Usage

The network analyzer has currently one command `analyze` which requires a tlbc node RPC and relay RPC URL.
Sensible default are currently provided, and the tool can be directly ran with `network-analyzer analyze`.
Otherwise, you can see the help for providing these URLs, or the output path to export the csv to.

```
Usage: network-analyzer analyze [OPTIONS]

Options:
  --jsonrpc URL  JsonRPC URL of the ethereum client  [default:
                 https://tlbc.rpc.anyblock.tools]

  --relay URL    Relay API URL  [default:
                 https://tlbc.relay.anyblock.tools/api/v1]

  --output PATH  Path of the directory to output the csv to
  --help         Show this message and exit.
```
