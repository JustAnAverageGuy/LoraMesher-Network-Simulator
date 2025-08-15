from enum import Enum
import sys

N                   = 10
SIZE_KM             = 10
CONNECTION_RANGE_KM = 3
HELLO_TIME_SECS     = 2
BROADCAST_ADDR      = 'FFFF'
SF                = 7
TX_POWER_DBM       = 14
FREQUENCY_MHZ      = 868.0
BANDWIDTH_HZ       = 125_000
NOISE_FIGURE_DB    = 6.0
PATH_LOSS_EXPONENT = 2.7

DEBUG = False

class PacketType(Enum):
    ROUTING = 1
    DATA  = 2

class Role(Enum):
    GATEWAY = 1
    NORMAL  = 2
    SENSOR = 3


if __name__ == "__main__":
    sys.exit(1)

