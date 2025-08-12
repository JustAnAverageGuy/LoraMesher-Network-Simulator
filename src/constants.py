from enum import Enum
import sys

N                   = 10
SIZE_KM             = 1000
# CONNECTION_RANGE_KM = 100
CONNECTION_RANGE_KM = 300
HELLO_TIME_SECS     = 5
BROADCAST_ADDR      = 'FFFF'

DEBUG = False

class PacketType(Enum):
    ROUTING = 1
    DATA  = 2

class Role(Enum):
    GATEWAY = 1
    NORMAL  = 2


if __name__ == "__main__":
    sys.exit(1)

