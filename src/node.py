from random import random
import sys
from threading import Timer

from .packet import Packet, RouteInfo, Routes, RoutingPacket, RoutingTable
from .constants import CONNECTION_RANGE_KM, DEBUG, HELLO_TIME_SECS, SIZE_KM, PacketType, Role


class Node:
    def __init__(
        self,
        name: str,
        role: Role = Role.NORMAL,
        position: tuple[float, float] | None = None,
    ):
        self.name = name
        self.role = role

        if position is None:
            position = (
                random() * SIZE_KM,
                random() * SIZE_KM,
            )

        self.position = position
        self.all_nodes: None | list["Node"] = None

        self.routes = RoutingTable(self.name)

        self.t = Timer(HELLO_TIME_SECS, self.broadcast_routing)

        self.t.start()

    def process_route(self, src: str, routes: Routes):
        is_routing_table_updated = False
        is_routing_table_updated |= self.routes.add_route(
            dst=src,
            via=src,
            metric=1,
        )
        for node, route_info in routes.routes.items():
            is_routing_table_updated |= self.routes.add_route(
                dst=node,
                via=src,
                metric=route_info.metric + 1,
            )

        print(self.routes)

        # TODO: alternate version here
        # if is_routing_table_updated: self.broadcast_routing()

    def receive(self, message: Packet):
        if DEBUG: print(f"{self.name} received {message}")
        if message.type == PacketType.ROUTING:
            self.process_route(message.src, message.routes)  # pyright: ignore[reportAttributeAccessIssue]
        elif message.type == PacketType.DATA:
            raise NotImplementedError("fu")

    def broadcast(self, message: Packet):
        if self.all_nodes is None:
            raise ValueError("All nodes is not initialized yet")
        for node in self.all_nodes:
            if not self.can_send(node):
                continue
            node.receive(message)
        return

    def broadcast_routing(self):
        routing_packet = Routes(
            routes={
                neighbour: RouteInfo(metric=metric_via["metric"])
                for neighbour, metric_via in self.routes.routing_table.items()
            }
        )

        self.broadcast(RoutingPacket(src=self.name, routes=routing_packet))
        if DEBUG: print(f"{self}: Sent Routing Info")
        if self.t is not None: self.t.cancel()
        self.t = Timer(HELLO_TIME_SECS, self.broadcast_routing)
        self.t.start()

    def can_send(self, other: "Node"):
        if other == self:
            return False
        return (
            sum((x - y) ** 2 for x, y in zip(self.position, other.position))
            <= CONNECTION_RANGE_KM**2
        )

    def __repr__(self):
        x, y = self.position
        return f"{self.name} | ({x:.2f},{y:.2f}) | Role: {self.role.name:8} |"

    def __str__(self) -> str:
        return f"Node[{self.name}]"


if __name__ == "__main__":
    sys.exit(1)
