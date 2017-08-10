from typing import List, Optional, Union

from rloopDefinitionApp.data_constants import (KNOWN_DAQ_KEYS,
                                               KNOWN_PARAM_KEYS,
                                               KNOWN_ROOT_KEYS)
from rloopDefinitionApp.utils import get_size


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
        template = "<Packet '{packet_name}', type={packet_type}, prefix='{packet_prefix}', params={num_params}, daq={daq}"
        return template.format(
            packet_name=self.name or "",
            packet_type=hex(self.packet_type or 0),
            packet_prefix=self.prefix or "",
            num_params=len(self.parameters) or 0,
            daq=self.daq.get("type", "") if self.daq else "",
        )

    def to_gs_dict(self):
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
                "DAQ": True,
                "dataType": self.daq["type"],
                "dataSize": self.daq["size"],
            })

        if self.parameters:
            output.update({
                "Parameters": self.parameter_hack_for_ground_station(),
            })

        return output

    @classmethod
    def from_yaml(cls, node: str, yaml_blob: dict, file_vars: Optional[dict]=None):
        if not isinstance(yaml_blob, dict):
            raise TypeError("Packet YAML file is giving us a {yaml_type}, instead of a dict.".format(
                yaml_type=type(yaml_blob)
            ))

        # Do formatting of all variables if we have variables.
        if file_vars:
            node = node.format(**file_vars)

            if "packetName" in yaml_blob:
                yaml_blob["packetName"] = yaml_blob["packetName"].format(**file_vars)

            if "prefix" in yaml_blob:
                yaml_blob["prefix"] = yaml_blob["prefix"].format(**file_vars)

            # TODO: If we ever put variables in parameters, implement this.
            if "parameters" in yaml_blob:
                pass

        # Fail if we have templated strings without variables.
        if "{" in node or "}" in node:
            raise ValueError("Untemplated strings in node name. " + yaml_blob['packetName'])

        if "packetName" in yaml_blob and ("{" in yaml_blob["packetName"] or "}" in yaml_blob["packetName"]):
            raise ValueError("Untemplated strings in packet name. " + yaml_blob['packetName'])

        if "prefix" in yaml_blob and ("{" in yaml_blob["prefix"] or "}" in yaml_blob["prefix"]):
            raise ValueError("Untemplated strings in prefix. " + yaml_blob['prefix'])

        # Unknown packet root arguments
        unknown_root_keys = set()
        for key in yaml_blob.keys():
            if key not in KNOWN_ROOT_KEYS:
                unknown_root_keys.add(key)
        if unknown_root_keys:
            raise ValueError("'{packet_name}' has unknown keys. {unknown_keys}".format(
                packet_name=yaml_blob['packetName'],
                unknown_keys=unknown_root_keys
            ))

        # Unknown packet param arguments
        if "parameters" in yaml_blob:
            unknown_param_keys = set()
            for param in yaml_blob["parameters"]:
                for key in param.keys():
                    if key not in KNOWN_PARAM_KEYS:
                        unknown_param_keys.add(key)
            if unknown_param_keys:
                raise ValueError("'{packet_name}' has unknown param keys. {unknown_keys}".format(
                    packet_name=yaml_blob['packetName'],
                    unknown_keys=unknown_param_keys
                ))

        # Unknown packet param arguments
        if "daq" in yaml_blob and yaml_blob["daq"]:
            unknown_daq_keys = set()
            for key in yaml_blob["daq"].keys():
                if key not in KNOWN_DAQ_KEYS:
                    unknown_daq_keys.add(key)
            if unknown_daq_keys:
                raise ValueError("'{packet_name}' has unknown DAQ keys. {unknown_daq_keys}".format(
                    packet_name=yaml_blob['packetName'],
                    unknown_keys=unknown_daq_keys
                ))

        return cls(
            yaml_blob.get("packetName"),
            node,
            yaml_blob.get("packetType"),
            yaml_blob.get("prefix", ""),
            yaml_blob.get("parameters", []),
            yaml_blob.get("daq", False)
        )

    def parameter_hack_for_ground_station(self) -> List[dict]:
        """
            This is awful but a necessary evil for the current state of the ground station.
            Thing it does
                * Capitalize Name, beginLoop, endLoop
                * Decapitalizes type, units
        """

        parameters_copy = self.parameters.copy()
        for parameter in parameters_copy:
            for key in parameter.keys():
                if key == "name":
                    parameter["Name"] = parameter["name"]
                    del parameter["name"]
                elif key.lower() in ("beginloop", "endloop") and key not in ("beginLoop", "endLoop"):
                    # TODO: lol this is awful
                    realKey = "beginLoop" if key.lower() == "beginloop" else "endLoop"
                    parameter[realKey] = parameter[key]
                    try:
                        del parameter[key]
                    except KeyError:
                        pass

        return parameters_copy

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
            raise ValueError("Packet must have a name. " + str(self))

        # Node name
        if not self.node:
            raise ValueError("Packet must have a node. " + str(self))

        # Packet type
        if not self.packet_type:
            raise ValueError("Packet must have a type that is not blank or 0x00. " + str(self))

        # DAQ and parameters
        if self.daq and self.parameters:
            raise ValueError("DAQ and parameters cannot both be defined in packet. " + self.name)

        # Parameter validation
        if self.parameters:
            in_loop = False
            for parameter in self.parameters:
                # Loop validation
                if "beginLoop" in parameter:
                    if in_loop:
                        raise ValueError("'{self_name}' is beginning a loop while already in a loop.".format(
                            self_name=self.name,
                        ))
                    in_loop = True

                if "endLoop" in parameter:
                    if not in_loop:
                        raise ValueError("'{self_name}' is ending a loop while not in a loop.".format(
                            self_name=self.name,
                        ))
                    in_loop = False

            if in_loop:
                raise ValueError("Loop not closed in '{self_name}'".format(
                    self_name=self.name,
                ))
