import json
from pprint import pprint
from src.html_template import html_template
import src.constants as constants
from src.utils import generate_nodes




def main():
    # nodes = generate_nodes(n=constants.N, layout='aandu pandu')
    nodes = generate_nodes(n=constants.N, layout='linear')

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
