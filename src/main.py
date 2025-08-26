import json
from pprint import pprint
from .html_template import html_template
from .constants import N, CONNECTION_RANGE_KM, SIZE_KM, Role, TX_POWER_DBM, SF, PATH_LOSS_EXPONENT, HELLO_TIME_SECS, DATA_TIME_SECS
from .node import Node
from .utils import lora_max_range

def generate_nodes(n, area_length, connection_range, layout='linear'):
    """Generate a list of nodes with given parameters."""
    if layout == 'linear':
        nodes = [Node(f"[node-{i}]", position=(i*connection_range*0.99+10, area_length//2), connection_range=connection_range) for i in range(1, n)]
    else: 
        nodes = [Node(f"[node-{i}]", connection_range=connection_range, size_km=area_length, role=Role.SENSOR) if i == 0
                  else Node(f"[node-{i}]", connection_range=connection_range, size_km=area_length, role = Role.GATEWAY) if i == n-1
                    else Node(f"[node-{i}]", connection_range=connection_range, size_km=area_length) for i in range(n)]


    Node._all_nodes = nodes

    return nodes

def create_simulation(context:'Context', layout='aandu pandu', node_info=None):
    """Create a new simulation with given context parameters."""
    Node._reroute_on_new_node = context.reroute_on_new_node
    Node._data_interval = context.data_interval
    Node._routing_interval = context.routing_interval
    context.connection_range_km = lora_max_range(tx_power_dbm=context.tx_power_dbm, sf=context.sf, path_loss_exp=context.path_loss_exponent) / 1000

    if node_info is not None:
        context.n = len(node_info)
        nodes = []
        for i, info in enumerate(node_info):
            print(f"Creating node {i} with info: {info}", flush=True)
            position = (info.get("x", 0), info.get("y", 0))
            node = Node(f"[node-{i}]", position=position, connection_range=context.connection_range_km, size_km=context.size_km, role=Role[info.get("role", "NORMAL")])
            nodes.append(node)
        Node._all_nodes = nodes
        print(Node._all_nodes, flush=True)
        return nodes

    nodes = generate_nodes(n=context.n, area_length=context.size_km, connection_range=context.connection_range_km, layout=layout)
    return nodes


class Context:
    def __init__(self):
        self.n = N
        self.size_km = SIZE_KM
        self.connection_range_km: float = CONNECTION_RANGE_KM
        self.tx_power_dbm = TX_POWER_DBM
        self.sf = SF
        self.path_loss_exponent = PATH_LOSS_EXPONENT
        self.routing_interval = HELLO_TIME_SECS
        self.data_interval = DATA_TIME_SECS
        self.reroute_on_new_node = False

