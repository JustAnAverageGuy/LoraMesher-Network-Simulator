from src.node import Node
import src.constants as constants


def generate_nodes(n, layout='linear'):
    if layout == 'linear':
        nodes = [Node(f"[node-{i}]", position=(i*constants.CONNECTION_RANGE_KM*0.99+10, constants.SIZE_KM//2)) for i in range(n)]
    else: 
        nodes = [Node(f"[node-{i}]") for i in range(n)]

    nodes[-1].role = constants.Role.GATEWAY

    for node in nodes:
        node.all_nodes = nodes

    return nodes

