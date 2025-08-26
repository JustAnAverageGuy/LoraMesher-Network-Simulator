from random import random
import sys
from threading import Timer
from datetime import datetime

from .packet import DataPacket, Packet, RouteInfo, Routes, RoutingPacket, RoutingTable
from .constants import CONNECTION_RANGE_KM, DEBUG, HELLO_TIME_SECS, SIZE_KM, PacketType, Role, DATA_TIME_SECS, INITIAL_SETUP_TIME_SECS


class Node:
    _stopped = False
    _total_messages_sent = 0
    _total_messages_received = 0
    _average_time_to_deliver = 0.0
    _total_routes_broadcasted = 0
    _average_new_node_discovery_time = 0.0
    _new_nodes_added = 0    
    _reroute_on_new_node = False
    _data_interval = DATA_TIME_SECS
    _routing_interval = HELLO_TIME_SECS
    _initial_broadcast_messages_sent = 0
    _all_nodes: list["Node"] = []
    def __init__(
        self,
        name: str,
        role: Role = Role.NORMAL,
        position: tuple[float, float] | None = None,
        connection_range: float = CONNECTION_RANGE_KM,
        size_km: float = SIZE_KM,
    ):
        self.name = name
        self.role = role

        if position is None:
            position = (
                random() * size_km,
                random() * size_km,
            )

        self.position = position
        self.connection_range = connection_range

        self.routes = RoutingTable(self.name)

        self.stats = {
            "routing_sent": 0,
            "routing_received": 0,
            "data_sent": 0,
            "data_received": 0,
            "data_forwarded": 0,
            "dropped": 0,
        }
        self.timer_handle = Timer(INITIAL_SETUP_TIME_SECS + random(), self.broadcast_routing)
        self.timer_handle.daemon = True
        self.timer_handle.start()
        self.timer_handle_data = None
        if self.role == Role.SENSOR:
            self.timer_handle_data = Timer(INITIAL_SETUP_TIME_SECS + random(), self.broadcast_data)
            self.timer_handle_data.daemon = True
            self.timer_handle_data.start()
    def process_route(self, src: str, routes: Routes, role: Role = Role.NORMAL):
        self.stats["routing_received"] += 1
        is_routing_table_updated = False
        src_position = None
        if Node._all_nodes is not None:
            src_position = next(
                (node.position for node in Node._all_nodes if node.name == src), None
            )
        dist = 0.0
        if src_position is not None:
            dist = sum(
                (x - y) ** 2 for x, y in zip(self.position, src_position)
            ) ** 0.5
        is_routing_table_updated |= self.routes.add_route(
            dst=src,
            via=src,
            metric=1,
            dist=dist,
            role=role,
        )
        for node, route_info in routes.routes.items():
            node_position = next(
                (n.position for n in Node._all_nodes if n.name == src), None
            ) if Node._all_nodes is not None else None
            dist = sum(
                (x - y) ** 2 for x, y in zip(self.position, node_position)
            ) ** 0.5 if node_position is not None else 0.0
            is_routing_table_updated |= self.routes.add_route(
                dst=node,
                via=src,
                metric=route_info.metric + 1,
                dist=dist,
                role=route_info.role,
            )

        # print(self.routes)

        # TODO: alternate version here
        if Node._reroute_on_new_node and is_routing_table_updated:
            self.broadcast_routing()

    def receive(self, message: Packet):
        if DEBUG: print(f"{self.name} received {message}")
        if message.type == PacketType.ROUTING:
            self.process_route(message.src, message.routes, message.role)  # pyright: ignore[reportAttributeAccessIssue]
        elif message.type == PacketType.DATA:
            self.process_data(message) # pyright: ignore[reportArgumentType]

    def process_data(self, message: DataPacket):
        self.stats["data_received"] += 1
        receive_time = datetime.now()
        if message.dst != self.name and message.via != self.name:
            self.stats["dropped"] += 1
            print(f"{self.name} received data packet but not the destination or via, ignoring")
            return
        if message.dst != self.name and message.via == self.name:
            print(f"{self.name} received data packet, forwarding to {message.dst}")
            self.stats["data_forwarded"] += 1
            via = self.routes.routing_table.get(message.dst, {}).get("via", self.name)
            if via is None:
                print(f"{self.name} has no route to {message.dst}, dropping packet")
                return
            message.via = via
            self.broadcast(message)
            return
        Node._total_messages_received += 1
        Node._average_time_to_deliver += ((receive_time - message.timestamp).total_seconds() - Node._average_time_to_deliver) / Node._total_messages_received if message.timestamp is not None else 0.0
        print(f"{self.name} received data packet, processing content: {message.content}")

    def broadcast(self, message: Packet):
        if Node._all_nodes is None:
            print(f"{self.name} has no nodes to broadcast to")
            return
        for node in Node._all_nodes:
            if not self.can_send(node):
                continue
            node.receive(message)
        return
    
    def broadcast_data(self, content: str = "Hello from Node"):
        closest_gateway_in_routing_table = None
        Node._total_messages_sent += 1
        sorted_routes = sorted(
            self.routes.routing_table.items(),
            key=lambda item: (item[1]["metric"], -item[1]["snr"])
        )
        for node, route_info in sorted_routes:
            if route_info["role"] == Role.GATEWAY:
                closest_gateway_in_routing_table = node
                break
        if closest_gateway_in_routing_table is not None:
            via = self.routes.routing_table.get(closest_gateway_in_routing_table, {}).get("via", self.name)
            self.stats["data_sent"] += 1
            self.broadcast(
                DataPacket(
                    src=self.name,
                    dst=closest_gateway_in_routing_table,
                    via=via,
                    content=content,
                    timestamp=datetime.now()
                )
            )
        # if DEBUG: 
            print(f"Delay: {Node._data_interval} seconds")
            print(f"{self}: Sent Data to {closest_gateway_in_routing_table} with content: {content}")
        else:
            if DEBUG: print(f"{self}: No gateway found in routing table, broadcasting data to all nodes")
            Node._initial_broadcast_messages_sent += 1

        if self.timer_handle_data is not None:
            self.timer_handle_data.cancel()

        if not Node._stopped:
            self.timer_handle_data = Timer(Node._data_interval, self.broadcast_data, args=(content,))
            self.timer_handle_data.daemon = True
            self.timer_handle_data.start()

    def broadcast_routing(self):
        routing_packet = Routes(
            routes={
                neighbour: RouteInfo(metric=metric_via["metric"], role=metric_via["role"])
                for neighbour, metric_via in self.routes.routing_table.items()
            }
        )

        self.stats["routing_sent"] += 1
        self.broadcast(RoutingPacket(src=self.name, routes=routing_packet, role=self.role))
        if DEBUG: print(f"{self}: Sent Routing Info")
        Node._total_routes_broadcasted += 1
        if self.timer_handle is not None: self.timer_handle.cancel()
        if not Node._stopped:
            self.timer_handle = Timer(Node._routing_interval, self.broadcast_routing)
            self.timer_handle.daemon = True
            self.timer_handle.start()

    def can_send(self, other: "Node"):
        if other == self:
            return False
        return (
            sum((x - y) ** 2 for x, y in zip(self.position, other.position))
            <= self.connection_range**2
        )

    def __repr__(self):
        x, y = self.position
        return f"{self.name} | ({x:.2f},{y:.2f}) | Role: {self.role.name:8} |"

    def __str__(self) -> str:
        return f"Node[{self.name}]"


if __name__ == "__main__":
    sys.exit(1)
