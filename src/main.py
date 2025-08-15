import json
from pprint import pprint
from .html_template import html_template
from .constants import N, CONNECTION_RANGE_KM, SIZE_KM, Role, TX_POWER_DBM, SF
from .node import Node
from .utils import lora_max_range

def generate_nodes(n, area_length, connection_range, layout='linear'):
    if layout == 'linear':
        nodes = [Node(f"[node-{i}]", position=(i*connection_range*0.99+10, area_length//2), connection_range=connection_range) for i in range(n)]
    else: 
        nodes = [Node(f"[node-{i}]", connection_range=connection_range, size_km=area_length ) for i in range(n)]

    nodes[-1].role = Role.GATEWAY

    for node in nodes:
        node.all_nodes = nodes

    return nodes

def create_simulation(context:'Context', layout='aandu pandu'):
    context.connection_range_km = lora_max_range(tx_power_dbm=context.tx_power_dbm, sf=context.sf) / 1000
    nodes = generate_nodes(n=context.n, area_length=context.size_km, connection_range=context.connection_range_km, layout=layout)
    return nodes


class Context:
    def __init__(self):
        self.n = N
        self.size_km = SIZE_KM
        self.connection_range_km: float = CONNECTION_RANGE_KM
        self.tx_power_dbm = TX_POWER_DBM
        self.sf = SF

