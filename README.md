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

By default, you would need to run a relay server locally to run the network-analyzer. This is to prevent
flooding public servers apis, as the tool needs to make a lot of different queries.
The tool can take up to 10 minutes to run through.

```
Usage: network-analyzer analyze [OPTIONS]

Options:
  --jsonrpc URL  JsonRPC URL of the ethereum client  [default:
                 https://tlbc.rpc.anyblock.tools]

  --relay URL    Relay API URL  [default: http://localhost:5000/api/v1]
  --output PATH  Path of the directory to output the csv to
  --help         Show this message and exit.
```

## GUI version

You can generate a GUI executable for different OS (Windows, Mac) using Python lib `PyInstaller`. `./src/network_analyzer/app.py` is a sample script for generating a simple GUI that gives you the option to choose the RPC and Relay servers, and the folder you would like the analysis files to be generated. So, easily you can follow those steps to generate an executable:

```
$ pip install pyinstaller
$ cd src/network_analyzer
$ pyinstaller app.py -y
```

This should generate the executable with some other files by default at `./src/network_analyzer/dist/app`, and you need then to copy `contracts.json` to `dist/app/network_analyzer/contracts.json`

```
-- bash shell
$ mkdir ./dist/app/network_analyzer && \
  cp contracts.json ./dist/app/network_analyzer
```
