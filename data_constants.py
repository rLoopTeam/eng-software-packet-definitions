PACKET_SIZES = {
    "uint8": 1,
    "int8": 1,

    "uint16": 2,
    "int16": 2,

    "uint32": 4,
    "int32": 4,
    "float32": 4,

    "uint64": 8,
    "int64": 8,
    "float64": 8,
}

KNOWN_ROOT_KEYS = [
    "daq",
    "packetName",
    "packetType",
    "parameters",
    "prefix",
]

KNOWN_PARAM_KEYS = [
    "name",
    "type",
    "units",
    "size",
    "beginLoop",
    "endLoop",
]

KNOWN_DAQ_KEYS = [
    "type",
    "size",
]
