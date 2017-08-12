import logging
from typing import List, Optional, Union

import jsonschema

from rloopDefinitionApp.schemas import DAQ_SCHEMA, PACKET_SCHEMA, PARAM_SCHEMA
from rloopDefinitionApp.utils import get_size

log = logging.getLogger(__name__)


class Packet:
    __slots__ = ["daq", "name", "packet_type", "parameters", "prefix", "node"]

    def __init__(
            self,
            name: str,
            node: str,
            packet_type: int,
            prefix: str,
            parameters: Optional[List[dict]]=None,
            daq: Union[None, dict, bool]=False
    ):
        self.name = name
        self.node = node
        self.packet_type = packet_type
        self.prefix = prefix
        self.parameters = parameters or []
        self.daq = daq

        self.fill_defaults()
        self.validate()

    def __repr__(self):
        template = ("<Packet '{packet_name}', type={packet_type}, prefix='{packet_prefix}',"
                    "params={num_params}, daq={daq}")
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

        # Schema validation.
        jsonschema.validate(yaml_blob, PACKET_SCHEMA)

        return cls(
            yaml_blob.get("packetName"),
            node,
            yaml_blob.get("packetType"),
            yaml_blob.get("prefix", ""),
            yaml_blob.get("parameters", []),
            yaml_blob.get("daq", False)
        )

    def parameter_hack_for_ground_station(self) -> dict:
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
                    real_key = "beginLoop" if key.lower() == "beginloop" else "endLoop"
                    parameter[real_key] = parameter[key]
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
                * packet["parameters"][param_i] = param with `i + name` [if param.iterate]
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

        # Iteration fixing
        original_parameters = self.parameters.copy()
        self.parameters = []
        in_group = False
        group_params = []

        for parameter in original_parameters:
            if "iterate" not in parameter and not in_group:
                self.parameters.append(parameter)
                continue

            # Save meta and delete from parameter.
            iteration_meta = parameter.get("iterate", {})
            if "iterate" in parameter:
                del parameter["iterate"]

            # Put out a warning for names without templating braces.
            if "{" not in parameter["name"] or "}" not in parameter["name"]:
                log.warning("Parameter '%s' is missing template braces.", parameter["name"])

            # Set our group variables if we are in a group.
            if iteration_meta.get("beginGroup", False):
                group_params = []
                in_group = True
            elif iteration_meta.get("endGroup", False):
                in_group = False

            # Set our range start and end from the givens and implicits.
            range_start = iteration_meta.get("start", 0)
            range_end = iteration_meta.get("end", 1) + 1

            # Subtract the end by 1 if we do not want to include the end.
            if not iteration_meta.get("inclusive", True):
                range_end = range_end - 1

            # Do special group logic if we are in a group or the group params is filled.
            if in_group:
                group_params.append(parameter)
                continue
            elif group_params:
                group_params.append(parameter)
                for i in range(range_start, range_end):
                    for group_parameter in group_params:
                        self.append_parameter(group_parameter, i=i)
                continue

            # Iterate through our range and append the parameter copies to the list.
            for i in range(range_start, range_end):
                self.append_parameter(parameter, i=i)

        if in_group:
            raise ValueError("Packet {packet_name} has an unclosed iter group.".format(
                packet_name=self.name
            ))

    def append_parameter(self, parameter: dict, **kwargs):
        """
            Appends a parameter to the packet parameters list.
            Copying and formatting is for the group function and doesn't hurt general functionality
            if used elsewhere.
        """
        parameter = parameter.copy()
        parameter["name"] = parameter["name"].format(**kwargs)
        self.parameters.append(parameter)

    def validate(self):
        """
            Validates a packet's keys and raises exceptions and warnings if anything is wrong.
        """

        # Basic schema validation
        for param in self.parameters:
            jsonschema.validate(param, PARAM_SCHEMA)
        jsonschema.validate(self.daq or {}, DAQ_SCHEMA)

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


class Argument:
    def __init__(self, arg_type, optional=False):
        self.arg_type = arg_type
        self.optional = optional

    def __repr__(self):
        return "<Argument {arg_type}, optional={optional}>".format(
            arg_type=str(self.arg_type),
            optional=self.optional
        )
