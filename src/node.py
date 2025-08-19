from random import random
import sys
from threading import Timer

from .packet import DataPacket, Packet, RouteInfo, Routes, RoutingPacket, RoutingTable
from .constants import CONNECTION_RANGE_KM, DEBUG, HELLO_TIME_SECS, SIZE_KM, PacketType, Role, DATA_TIME_SECS


class Node:
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
        self.all_nodes: None | list["Node"] = None
        self.connection_range = connection_range

        self.routes = RoutingTable(self.name)

        self.timer_handle = Timer(HELLO_TIME_SECS, self.broadcast_routing)
        self.timer_handle.daemon = True
        self.timer_handle.start()

        if self.role == Role.SENSOR:
            self.timer_handle_data = Timer(DATA_TIME_SECS, self.broadcast_data)
            self.timer_handle_data.daemon = True
            self.timer_handle_data.start()



    def process_route(self, src: str, routes: Routes, role: Role = Role.NORMAL):
        is_routing_table_updated = False
        src_position = None
        if self.all_nodes is not None:
            src_position = next(
                (node.position for node in self.all_nodes if node.name == src), None
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
                (n.position for n in self.all_nodes if n.name == src), None
            ) if self.all_nodes is not None else None
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
        # if is_routing_table_updated: self.broadcast_routing()

    def receive(self, message: Packet):
        if DEBUG: print(f"{self.name} received {message}")
        if message.type == PacketType.ROUTING:
            self.process_route(message.src, message.routes, message.role)  # pyright: ignore[reportAttributeAccessIssue]
        elif message.type == PacketType.DATA:
            self.process_data(message) # pyright: ignore[reportArgumentType]

    def process_data(self, message: DataPacket):
        if message.dst != self.name and message.via != self.name:
            print(f"{self.name} received data packet but not the destination or via, ignoring")
            return
        if message.dst != self.name and message.via == self.name:
            print(f"{self.name} received data packet, forwarding to {message.dst}")
            via = self.routes.routing_table.get(message.dst, {}).get("via", self.name)
            if via is None:
                print(f"{self.name} has no route to {message.dst}, dropping packet")
                return
            message.via = via
            self.broadcast(message)
            return
        print(f"{self.name} received data packet, processing content: {message.content}")

    def broadcast(self, message: Packet):
        if self.all_nodes is None:
            raise ValueError("All nodes is not initialized yet")
        for node in self.all_nodes:
            if not self.can_send(node):
                continue
            node.receive(message)
        return
    
    def broadcast_data(self, content: str = "Hello from Node"):
        closest_gateway_in_routing_table = None
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
            self.broadcast(
                DataPacket(
                    src=self.name,
                    dst=closest_gateway_in_routing_table,
                    via=via,
                    content=content,
                )
            )
        # if DEBUG: 
            print(f"{self}: Sent Data to {closest_gateway_in_routing_table} with content: {content}")

        if self.timer_handle_data is not None:
            self.timer_handle_data.cancel()
        self.timer_handle_data = Timer(DATA_TIME_SECS, self.broadcast_data, args=(content,))
        self.timer_handle_data.daemon = True
        self.timer_handle_data.start()

    def broadcast_routing(self):
        routing_packet = Routes(
            routes={
                neighbour: RouteInfo(metric=metric_via["metric"], role=metric_via["role"])
                for neighbour, metric_via in self.routes.routing_table.items()
            }
        )

        self.broadcast(RoutingPacket(src=self.name, routes=routing_packet, role=self.role))
        if DEBUG: print(f"{self}: Sent Routing Info")
        if self.timer_handle is not None: self.timer_handle.cancel()
        self.timer_handle = Timer(HELLO_TIME_SECS, self.broadcast_routing)
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
