# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time

# Import your simulation entrypoint or module that exposes the running nodes
# Adjust the import path if your main starts the sim directly. Ideally, refactor
# main.py to expose a function that creates/returns the node list without
# blocking. Example below assumes you can `from main import all_nodes`.

from src.main import create_simulation

all_nodes = create_simulation()
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
            else:
                # try attribute access
                via = getattr(info, "via", None)
                metric = getattr(info, "metric", None)
            routes.append({"dst": dst, "via": via, "metric": metric})

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


def background_emitter():
    """Background thread that emits snapshots via SocketIO periodically."""
    while True:
        nodes = snapshot_nodes()
        socketio.emit("snapshot", {"nodes": nodes})
        # print(f'snapshot {nodes = }')
        print("EMITTED SNAPSHOT", flush=True)
        socketio.sleep(2)


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def on_connect():
    print("Client connected", flush=True)

@socketio.on('restart')
def on_restart():
    global all_nodes
    all_nodes = create_simulation()
    nodes = snapshot_nodes()
    socketio.emit("snapshot", {"nodes": nodes})
    # raise NotImplementedError('IMPLEMENT THIS')


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
