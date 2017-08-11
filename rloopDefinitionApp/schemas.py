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

# I swear if someone puts in float8 or float16 :P
TYPES_REGEX = r"^u?(float|int)(8|16|32|64)$"

PACKET_LIST_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "description": "A list of packets.",
    "properties": {
        "node": {
            "type": "string",
            "minLength": 1,
        },
        "podSources": {"type": "array"},
        "vars": {"type": "object"},
        "packets": {"type": "array"},
    },
    "required": [
        "node",
        "podSources",
        "packets",
    ],
    "additionalProperties": False,
}

PACKET_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "description": "A safetyUDP packet that is sent through the pod network.",
    "properties": {
        "packetName": {
            "type": "string",
            "minLength": 1,
        },
        "packetType": {"type": "number"},
        "description": {"type": "string"},
        "friendlyName": {"type": "string"},
        "parameters": {"type": "array"},
        "prefix": {"type": "string"},
        "suffix": {"type": "string"},
        "senders": {"type": "array"},
        "receivers": {"type": "array"},
        "daq": {"type": "object"},
    },
    "required": [
        "packetName",
        "packetType",
    ],
    "additionalProperties": False,
}

PARAM_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "description": "A parameter of a packet.",
    "properties": {
        "name": {"type": "string"},
        "type": {
            "type": "string",
            "pattern": TYPES_REGEX,
        },
        "units": {"type": "string"},
        "size": {"type": "number"},
        "beginLoop": {"type": "boolean"},
        "endLoop": {"type": "boolean"},
        "iterate": {
            "type": "object",
            "properties": {
                "start": {
                    "type": "number",
                    "description": "Defaults to 0.",
                },
                "end": {"type": "number"},
                "inclusive": {
                    "type": "boolean",
                    "description": "Makes the range iterations include the end.",
                }
            },
            "description": "Does range(start, end) and sets variable i in parameter name.",
        },
    },
    "required": [
        "name",
        "type",
    ],
    "additionalProperties": False,
}

DAQ_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "description": "A DAQ parameter of a packet.",
    "properties": {
        "type": {
            "type": "string",
            "pattern": TYPES_REGEX,
        },
        "size": {
            "type": "number",
            "minimum": 0,
            "maximum": 8,  # Hopefully int128 will not be used in this case. :)
        },
    },
    "additionalProperties": False,
}
