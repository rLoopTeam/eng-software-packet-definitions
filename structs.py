from typing import Union, Optional
from data_constants import KNOWN_DAQ_KEYS, KNOWN_PARAM_KEYS, KNOWN_ROOT_KEYS
from utils import get_size


class Packet:
    __slots__ = ["daq", "name", "packet_type", "parameters", "prefix", "node"]

    def __init__(
            self,
            name: str,
            node: str,
            packet_type: int,
            prefix: str,
            parameters: Optional[dict]=[],
            daq: Union[None, dict, bool]=False
    ):
        self.name = name
        self.node = node
        self.packet_type = packet_type
        self.prefix = prefix
        self.parameters = parameters
        self.daq = daq

        self.fill_defaults()
        self.validate()

    def __repr__(self):
        daq_text = f"{self.daq['type']} daq" if self.daq else "not daq"
        return f"<Packet '{self.name}', type={hex(self.packet_type)}, prefix='{self.prefix}', " \
               f"parameters={len(self.parameters)}, {daq_text}>"

    def to_dict(self):
        output = {
            "Name": self.name,
            "PacketType": self.packet_type,
            "Node": self.node,
            "DAQ": False,
        }

        if self.prefix:
            output.update({
                "ParameterPrefix": self.prefix + " ",
            })

        if self.daq:
            output.update({
                "dataType": self.daq["type"],
                "dataSize": self.daq["size"],
            })

        if self.parameters:
            output.update({
                "Parameters": self.parameters,
            })

        return output

    @classmethod
    def from_yaml(cls, node: str, yaml_blob: dict, file_vars: Optional[dict]=None):
        # Do formatting of all variables if we have variables.
        if file_vars:
            if "packetName" in yaml_blob:
                yaml_blob["packetName"] = yaml_blob["packetName"].format(**file_vars)

            if "prefix" in yaml_blob:
                yaml_blob["prefix"] = yaml_blob["prefix"].format(**file_vars)

            # TODO: If we ever put variables in parameters, implement this.
            if "parameters" in yaml_blob:
                pass

        # Unknown packet root arguments
        unknown_root_keys = set()
        for key in yaml_blob.keys():
            if key not in KNOWN_ROOT_KEYS:
                unknown_root_keys.add(key)
        if unknown_root_keys:
            raise ValueError(f"'{yaml_blob['packetName']}' has unkown keys. {unknown_root_keys}")

        # Unknown packet param arguments
        if "parameters" in yaml_blob:
            unknown_param_keys = set()
            for param in yaml_blob["parameters"]:
                for key in param.keys():
                    if key not in KNOWN_PARAM_KEYS:
                        unknown_param_keys.add(key)
            if unknown_param_keys:
                raise ValueError(f"'{yaml_blob['packetName']}' has unkown param keys. {unknown_param_keys}")

        # Unknown packet param arguments
        if "daq" in yaml_blob and yaml_blob["daq"]:
            unknown_daq_keys = set()
            for key in yaml_blob["daq"].keys():
                if key not in KNOWN_DAQ_KEYS:
                    unknown_daq_keys.add(key)
            if unknown_daq_keys:
                raise ValueError(f"'{yaml_blob['packetName']}' has unkown DAQ keys. {unknown_daq_keys}")

        return cls(
            yaml_blob.get("packetName"),
            node,
            yaml_blob.get("packetType"),
            yaml_blob.get("prefix", ""),
            yaml_blob.get("parameters", []),
            yaml_blob.get("daq", False)
        )

    def fill_defaults(self):
        """
            Fills in a packet's default values accordingly.
                * packet["daq"]["size"] = byte size [if DAQ]
                * packet["daq"] = False [if not DAQ]
                * packet["parameters"][param]["units"] = ""
                * packet["parameters"][param]["size"] = byte size
        """

        # Fill in DAQ sizes if we have a DAQ.
        if self.daq:
            self.daq["size"] = get_size(self.daq["type"])

        # Parameter defaults
        for parameter in self.parameters:
            # Units default to a blank string,
            if "units" not in parameter:
                parameter["units"] = ""

            # Fill in size
            if "size" not in parameter:
                parameter["size"] = get_size(parameter["type"])

    def validate(self):
        """
            Validates a packet's keys and raises exceptions and warnings if anything is wrong.
        """

        # Packet name
        if not self.name:
            raise ValueError(f"Packet must have a name. {str(self)}")

        # Packet name
        if not self.node:
            raise ValueError(f"Packet must have a node. {str(self)}")

        # DAQ and parameters
        if self.daq and self.parameters:
            raise ValueError(f"DAQ and parameters cannot both be defined in packet. [{self.name}]")

        # Parameter validation
        if self.parameters:
            in_loop = False
            for parameter in self.parameters:
                # Loop validation
                if "beginLoop" in parameter:
                    if in_loop:
                        raise ValueError(f"'{self.name}' is beginning a loop while already in a loop.")
                    in_loop = True

                if "endLoop" in parameter:
                    if not in_loop:
                        raise ValueError(f"'{self.name}' is ending a loop while not in a loop.")
                    in_loop = False

            if in_loop:
                raise ValueError(f"Loop not closed in '{self.name}'")
