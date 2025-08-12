from src.node import Node
import src.constants as constants


def generate_nodes(n, area_length, connection_range, layout='linear'):
    if layout == 'linear':
        nodes = [Node(f"[node-{i}]", position=(i*connection_range*0.99+10, area_length//2), connection_range=connection_range) for i in range(n)]
    else: 
        nodes = [Node(f"[node-{i}]", connection_range=connection_range, size_km=area_length ) for i in range(n)]

    nodes[-1].role = constants.Role.GATEWAY

    for node in nodes:
        node.all_nodes = nodes

    return nodes

