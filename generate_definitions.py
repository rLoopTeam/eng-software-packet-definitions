import json
import logging
import os
import sys

import yaml

from data_constants import KNOWN_DAQ_KEYS, KNOWN_PARAM_KEYS, KNOWN_ROOT_KEYS
from utils import get_size, get_packet_files

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class DefinitionGenerator:
    def __init__(self, input_folder: str="packets/", output_folder: str="output/"):
        # Data holding
        self.packets = []
        self.packet_ids = set()
        self.packet_names = set()
        self.sums = {}

        # Paths
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.packet_definitions_yaml = os.path.join(self.output_folder, "packetDefinitions.yml")
        self.packet_definitions_json = os.path.join(self.output_folder, "packetDefinitions.json")
        self.packet_definitions_human_json = os.path.join(self.output_folder, "packetDefinitions_human.json")
        self.file_sums_json = os.path.join(self.output_folder, "fileSums.json")

    def fill_packet(self, packet):
        """
            Fills in a packet's default values accordingly.
                * packet["daq"]["size"] = byte size [if DAQ]
                * packet["daq"] = False [if not DAQ]
                * packet["parameters"][param]["units"] = ""
                * packet["parameters"][param]["size"] = byte size
        """

        # Fill in DAQ sizes if we have a DAQ.
        if "daq" in packet:
            packet["daq"]["size"] = get_size(packet["daq"]["type"])

        # Default DAQ to false if not appended.
        if "daq" not in packet:
            packet["daq"] = False

        # Parameter defaults
        if "parameters" in packet:
            for parameter in packet["parameters"]:
                # Units default to a blank string,
                if "units" not in parameter:
                    parameter["units"] = ""

                # Fill in size
                if "size" not in parameter:
                    parameter["size"] = get_size(parameter["type"])

    def validate_packet(self, packet: dict):
        """
            Validates a packet's keys and raises exceptions and warnings if anything is wrong.
        """

        # Packet name
        if "packetName" not in packet:
            raise ValueError(f"Packet must have a name. {str(packet)}")

        # Unknown packet root arguments
        unknown_root_keys = set()
        for key in packet.keys():
            if key not in KNOWN_ROOT_KEYS:
                unknown_root_keys.add(key)
        if unknown_root_keys:
            raise ValueError(f"'{packet['packetName']}' has unkown keys. {unknown_root_keys}")

        # Unknown packet param arguments
        if "parameters" in packet:
            unknown_param_keys = set()
            for param in packet["parameters"]:
                for key in param.keys():
                    if key not in KNOWN_PARAM_KEYS:
                        unknown_param_keys.add(key)
            if unknown_param_keys:
                raise ValueError(f"'{packet['packetName']}' has unkown param keys. {unknown_param_keys}")

        # Unknown packet param arguments
        if "daq" in packet and packet["daq"]:
            unknown_daq_keys = set()
            for key in packet["daq"].keys():
                if key not in KNOWN_DAQ_KEYS:
                    unknown_daq_keys.add(key)
            if unknown_daq_keys:
                raise ValueError(f"'{packet['packetName']}' has unkown DAQ keys. {unknown_daq_keys}")

        # DAQ and parameters
        if ("daq" in packet and "parameters" in packet) and packet["daq"]:
            raise ValueError(f"DAQ and parameters cannot both be defined in packet. [{packet['packetName']}]")

        # Duplicate names
        if packet["packetName"] in self.packet_names:
            raise ValueError(f"Packet name '{packet['packetName']}' is already in use.'")

        # Duplicate ID warning
        if packet["packetType"] in self.packet_ids:
            all_users = [_["packetName"] for _ in self.packets if _["packetType"] == packet["packetType"]]
            log.warning(f"'{packet['packetName']}' is reusing {hex(packet['packetType'])}. {all_users}")

        # Parameter validation
        if "parameters" in packet:
            in_loop = False
            for parameter in packet["parameters"]:
                # Loop validation
                if "beginLoop" in parameter:
                    if in_loop:
                        raise ValueError(f"'{packet['packetName']}' is beginning a loop while already in a loop.")
                    in_loop = True

                if "endLoop" in parameter:
                    if not in_loop:
                        raise ValueError(f"'{packet['packetName']}' is ending a loop while not in a loop.")
                    in_loop = False

            if in_loop:
                raise ValueError(f"Loop not closed in '{packet['packetName']}'")

    def load(self, file_name):
        """
            Loads a single defintion file.
            This method exists for testing and to drop exceptions when there is malformed data
            in the packet defintions.
        """
        is_sums = file_name == self.file_sums_json

        with open(file_name, "r") as f:
            if is_sums:
                self.sums = json.load(f)
            else:
                packets_data = yaml.load(f)
                packet_vars = packets_data.get("vars")

                for packet in packets_data["packets"]:
                    # Do formatting of all variables if we have variables.
                    if packet_vars:
                        if "packetName" in packet:
                            packet["packetName"] = packet["packetName"].format(**packet_vars)
                        if "prefix" in packet:
                            packet["prefix"] = packet["prefix"].format(**packet_vars)
                        # TODO: If we ever put variables in parameters, implement this.
                        if "parameters" in packet:
                            pass

                    # Fill blanks and validate.
                    self.fill_packet(packet)
                    self.validate_packet(packet)

                    # Append packet to lists.
                    self.packets.append(packet)
                    self.packet_names.add(packet["packetName"])
                    self.packet_ids.add(packet["packetType"])

    def load_all(self):
        """
            Loads all packet defintion files in the given input folder.
        """
        # Load the sums before the packets.
        try:
            self.load(self.file_sums_json)
        except FileNotFoundError:
            pass

        # Load the packets.
        packet_files = get_packet_files(self.input_folder)
        for filename in packet_files:
            self.load(filename)

    def save(self, with_sums=True):
        """
            Saves all the packets to their respective folders.
        """

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        with open(self.packet_definitions_yaml, "w") as f:
            yaml.dump(self.packets, f, explicit_start=True)

        with open(self.packet_definitions_json, "w") as f:
            json.dump(self.packets, f)

        with open(self.packet_definitions_human_json, "w") as f:
            json.dump(self.packets, f, indent=4)

        if with_sums:
            with open(self.file_sums_json, "w") as f:
                json.dump(self.sums, f)

if __name__ == "__main__":
    generator = DefinitionGenerator()
    generator.load_all()
    generator.save()
