import time

import networkx


class CurrencyNetworkGraph(object):
    def __init__(
        self,
        capacity_imbalance_fee_divisor=0,
        default_interest_rate=0,
        prevent_mediator_interests=False,
    ):
        self.capacity_imbalance_fee_divisor = capacity_imbalance_fee_divisor
        self.default_interest_rate = default_interest_rate
        self.prevent_mediator_interests = prevent_mediator_interests
        self.graph = networkx.Graph()

    def generate_graph(self, trustlines):
        timestamp = int(time.time())
        self.graph.clear()
        for trustline in trustlines:
            if trustline["user"] < trustline["counterParty"]:
                self.graph.add_edge(
                    trustline["user"],
                    trustline["counterParty"],
                    creditline_given=trustline["given"],
                    creditline_received=trustline["received"],
                    interest_given=trustline["interestRateGiven"],
                    interest_received=trustline["interestRateReceived"],
                    is_frozen=trustline["isFrozen"],
                    m_time=timestamp,
                    balance_ab=trustline["balance"],
                )
            else:
                self.graph.add_edge(
                    trustline["counterParty"],
                    trustline["user"],
                    creditline_given=trustline["received"],
                    creditline_received=trustline["given"],
                    interest_given=trustline["interestRateReceived"],
                    interest_received=trustline["interestRateGiven"],
                    is_frozen=trustline["isFrozen"],
                    m_time=timestamp,
                    balance_ab=-int(trustline["balance"]),
                )

    def calculate_min_degree(self):
        vertex_degree_tuples = list(self.graph.degree)
        if len(vertex_degree_tuples) == 0:
            return 0
        min = vertex_degree_tuples[0][1]
        for vertex_degree_tuple in vertex_degree_tuples:
            if vertex_degree_tuple[1] < min:
                min = vertex_degree_tuple[1]
        return min

    def calculate_max_degree(self):
        vertex_degree_tuples = list(self.graph.degree)
        if len(vertex_degree_tuples) == 0:
            return 0
        max = vertex_degree_tuples[0][1]
        for vertex_degree_tuple in vertex_degree_tuples:
            if vertex_degree_tuple[1] > max:
                max = vertex_degree_tuple[1]
        return max

    def average_degree_of_power(self, k):
        power_graph = networkx.power(self.graph, k)
        vertex_degree_tuples = list(power_graph.degree)
        if len(vertex_degree_tuples) == 0:
            return 0
        return sum(
            [vertex_degree_tuple[1] for vertex_degree_tuple in vertex_degree_tuples]
        ) / len(vertex_degree_tuples)

    def number_of_vertex_of_degree_at_least(self, degree):
        vertex_degree_tuples = list(self.graph.degree)
        number = 0

        for vertex_degree_tuple in vertex_degree_tuples:
            if vertex_degree_tuple[1] >= degree:
                number += 1
        return number
