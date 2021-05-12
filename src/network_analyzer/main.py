from network_analyzer.analyzer import Analyzer


def main():
    analyzer = Analyzer(
        "https://tlbc.rpc.anyblock.tools",
        None,
        "https://tlbc.relay.anyblock.tools/api/v1",
    )
    analyzer.analyze_bridge_transfers()
    analyzer.analyze_networks()
    analyzer.analyze_dead_identities()


if __name__ == "__main__":
    # execute only if run as a script
    main()
