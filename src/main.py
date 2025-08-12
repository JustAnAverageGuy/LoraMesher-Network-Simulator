import json
from pprint import pprint
from .html_template import html_template
from .constants import N, CONNECTION_RANGE_KM, SIZE_KM
from .utils import generate_nodes



def create_simulation(num_nodes=N, area_length=SIZE_KM, connection_range=CONNECTION_RANGE_KM, layout='aandu pandu'):
    nodes = generate_nodes(n=num_nodes, area_length=area_length, connection_range=connection_range, layout=layout)
    return nodes

def main():
    nodes = generate_nodes(n=N, area_length=SIZE_KM, connection_range=CONNECTION_RANGE_KM, layout='linear')

    pprint(nodes)
    return nodes


if __name__ == "__main__":
    nodes = main()
    html = html_template % (
        json.dumps([
            node.position for node in nodes
        ]),
        CONNECTION_RANGE_KM
    )
    with open("index.html", "w") as f:
        f.write(html)
