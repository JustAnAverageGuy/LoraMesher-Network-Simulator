from dataclasses import dataclass
from .constants import BROADCAST_ADDR, PacketType


class Packet:
    def __init__(self, src: str, dst: str, type: PacketType ) -> None:
        self.src = src
        self.dst = dst
        self.type = type
    def __str__(self) -> str:
        return f'Type: {self.type.name}, Src: {self.src}, Dst: {self.dst}'

class DataPacket(Packet):
    def __init__(self, src: str, dst: str, via: str, content: str) -> None:
        super().__init__(src, dst, PacketType.DATA)
        self.via = via
        self.content = content
    def __str__(self) -> str:
        base_info =  super().__str__()
        return f'{base_info} Content: {self.content}'

class RoutingPacket(Packet):
    def __init__(self, src: str, routes: 'Routes') -> None:
        super().__init__(src, BROADCAST_ADDR, PacketType.ROUTING)
        self.routes = routes
    def __str__(self) -> str:
        base_info =  super().__str__()
        return f'{base_info} Routes: {self.src} {str(self.routes)}'

@dataclass
class RouteInfo:
    metric: int

@dataclass
class Routes:
    routes: dict[str, RouteInfo]

class RoutingTable:
    def __init__(self, name: str) -> None:
        self.routing_table = {}
        self.name = name
    def add_route(self, dst: str, via: str, metric: int) -> bool:
        "return true if new route is added"
        if dst == self.name: return False
        if dst not in self.routing_table:
            self.routing_table[dst] = {
                "metric": metric,
                "via": via,
            }
        else:
            if (self.routing_table[dst]["metric"] < metric): return False # can be less than equal to or not
            self.routing_table[dst] = {
                "metric": metric,
                "via": via,
            }
        return True
    def remove_route(self, dst: str):
        raise NotImplementedError("TODO: node deletion, delete via fields as well")

    def __str__(self) -> str:
        return f"Routing Table for {self.name}\n" + "\n".join(
            sorted(
            f'{neighbour} -> Metric: {metric_via["metric"]}, Via: {metric_via["via"]}' for neighbour, metric_via in self.routing_table.items()
            )

        )
        
