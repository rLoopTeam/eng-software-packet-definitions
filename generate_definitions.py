import json
import logging
import os
import sys

from typing import Union, Optional
import yaml

from utils import get_packet_files
from structs import Packet

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

    def load(self, file_name: str) -> None:
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

                for unparsed_packet in packets_data["packets"]:
                    # Fill blanks and validate.
                    parsed_packet = Packet.from_yaml(
                        packets_data["node"],
                        unparsed_packet,
                        packets_data.get("vars", {})
                    )

                    # Duplicate names
                    if parsed_packet.name in self.packet_names:
                        raise ValueError(f"Packet name '{parsed_packet.name}' is already in use.'")

                    # Duplicate ID warning
                    if parsed_packet.packet_type in self.packet_ids:
                        all_users = [_["Name"] for _ in self.packets if _["PacketType"] == parsed_packet.packet_type]
                        log.warning(f"'{parsed_packet.name}' is reusing {hex(parsed_packet.packet_type)}. {all_users}")

                    # Append packet to lists.
                    self.packets.append(parsed_packet.to_dict())
                    self.packet_names.add(parsed_packet.name)
                    self.packet_ids.add(parsed_packet.packet_type)

    def load_all(self) -> None:
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

    def save(self, with_sums: bool=True) -> None:
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
