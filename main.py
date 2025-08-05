import json
from pprint import pprint
from src.node import Node
from src.html_template import html_template
import src.constants as constants


def generate_nodes(n, layout='linear'):
    if layout == 'linear':
        nodes = [Node(f"[node-{i}]", position=(i*constants.CONNECTION_RANGE_KM*0.99+10, constants.SIZE_KM//2)) for i in range(n)]
    else: 
        nodes = [Node(f"[node-{i}]") for i in range(n)]

    nodes[-1].role = constants.Role.GATEWAY

    return nodes


def main():
    # nodes = generate_nodes(n=constants.N, layout='aandu pandu')
    nodes = generate_nodes(n=constants.N, layout='linear')

    for node in nodes:
        node.all_nodes = nodes
    # for node in nodes: node.thread_handle.start()
    pprint(nodes)
    return nodes


if __name__ == "__main__":
    nodes = main()
    html = html_template % (
        json.dumps([
            node.position for node in nodes
        ]),
        constants.CONNECTION_RANGE_KM
    )
    with open("index.html", "w") as f:
        f.write(html)
