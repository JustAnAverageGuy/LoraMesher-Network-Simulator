# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time

# Import your simulation entrypoint or module that exposes the running nodes
# Adjust the import path if your main starts the sim directly. Ideally, refactor
# main.py to expose a function that creates/returns the node list without
# blocking. Example below assumes you can `from main import all_nodes`.

from src.node import Node
from src.constants import CONNECTION_RANGE_KM, SIZE_KM, N, SF, TX_POWER_DBM, Role
from src.main import Context, create_simulation
from src.utils import lora_max_range

context = Context()
all_nodes = create_simulation(context=context)
print("nodes created", flush=True)


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*", logger=True)

EMIT_INTERVAL = 1.0  # seconds between snapshot emits


def snapshot_nodes():
    """Return a list of node snapshots suitable for JSON serialization."""
    nodes = []
    if all_nodes is None:
        return nodes

    for node in all_nodes:
        # Build a list of routes from the node's routing table structure
        routes = []
        try:
            routing_table = node.routes.routing_table
        except Exception:
            # If your RoutingTable stores differently, adapt here
            routing_table = getattr(node.routes, "routing_table", {})

        for dst, info in routing_table.items():
            # `info` might be a dict or an object; handle both
            if isinstance(info, dict):
                via = info.get("via")
                metric = info.get("metric")
                rssi = info.get("rssi")
                snr = info.get("snr")
                role = info.get("role", Role.NORMAL)
            else:
                # try attribute access
                via = getattr(info, "via", None)
                metric = getattr(info, "metric", None)
                rssi = getattr(info, "rssi", None)
                snr = getattr(info, "snr", None)
                role = getattr(info, "role", Role.NORMAL)
            routes.append({"dst": dst, "via": via, "metric": metric, "rssi": rssi, "snr": snr, "role": getattr(role, "name", str(role))})

        nodes.append(
            {
                "name": node.name,
                "x": node.position[0],
                "y": node.position[1],
                "role": getattr(node.role, "name", str(node.role)),
                "routes": routes,
            }
        )
        # print(f'{nodes = }', flush=True)

    return nodes


def add_new_node(position=None):
    """Add a new node to the simulation."""
    global all_nodes
    all_nodes.append(
        Node(
            name=f"[node-{len(all_nodes)}]",
            position=position if position else (0, 0),
            connection_range=context.connection_range_km,
            size_km=context.size_km,
        )
    )
    for node in all_nodes:
        node.all_nodes = all_nodes

def background_emitter():
    """Background thread that emits snapshots via SocketIO periodically."""
    while True:
        nodes = snapshot_nodes()
        socketio.emit("snapshot", {"nodes": nodes})
        # print(f'snapshot {nodes = }')
        # print("EMITTED SNAPSHOT", flush=True)
        socketio.sleep(2)


@app.route("/")
def index():
    """Render the main index page."""

    context.connection_range_km = lora_max_range(tx_power_dbm=context.tx_power_dbm, sf=context.sf) / 1000
    return render_template("index.html", state=context)


@socketio.on("connect")
def on_connect():
    print("Client connected", flush=True)

@socketio.on('reset')
def on_reset():
    """Handle reset request from the client."""
    global all_nodes, context
    context = Context()
    all_nodes.clear()
    all_nodes = create_simulation(context=context)
    nodes = snapshot_nodes()
    socketio.emit("snapshot", {"nodes": nodes})
    # raise NotImplementedError('IMPLEMENT THIS')

@socketio.on("update")
def on_update(data):
    """Handle updates from the client."""
    print("Received update:", data, flush=True)
    global all_nodes
    num_nodes = data.get("num_nodes", len(all_nodes))
    area_length = data.get("area_length", SIZE_KM)
    sf = data.get("sf", SF)
    tx_power = data.get("tx_power", TX_POWER_DBM)
    if all_nodes is not None:
        # Clear existing nodes if any
        all_nodes.clear()
    context.n = num_nodes
    context.size_km = area_length
    context.sf = sf
    context.tx_power_dbm = tx_power
    context.connection_range_km = lora_max_range(tx_power_dbm=tx_power, sf=sf) / 1000
    all_nodes = create_simulation(
        context=context
    )
    print(f"Updated connection range: {context.connection_range_km} km", flush=True)
    socketio.emit("range_update", {
        "connection_range_km": context.connection_range_km,
    })

    nodes = snapshot_nodes()
    socketio.emit("snapshot", {"nodes": nodes})


    print("Updated nodes and emitted snapshot", flush=True)
    
@socketio.on("add_node")
def on_add_node(data):
    """Handle adding a new node."""
    print("Adding node:", data, flush=True)
    position = data.get("position", (0, 0))
    add_new_node(position)
    nodes = snapshot_nodes()
    socketio.emit("snapshot", {"nodes": nodes})
    print("Added new node and emitted snapshot", flush=True)


@socketio.on("disconnect")
def on_disconnect():
    print("Client disconnected", flush=True)


if __name__ == "__main__":
    # Start the simulation if main exposes a function to do so. If your
    # existing main.py already starts the simulation on import, ensure you
    # import after that.

    print("SERVER STARTING", flush=True)
    # Start background emitter thread
    emitter = threading.Thread(target=background_emitter, daemon=True)
    emitter.start()

    # Run SocketIO server
    print("SERVER STARTED", flush=True)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
