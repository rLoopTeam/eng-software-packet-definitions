import json
import logging
import os
import random
import sys
from typing import Optional, Union

import yaml

from rloopDefinitionApp.structs import Packet
from rloopDefinitionApp.utils import get_packet_files, md5

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class DefinitionGenerator:
    def __init__(self, input_folder: str="packets/", output_folder: str="output/"):
        # Data holding
        self.packets = {"packetDefinitions": []}
        self.packet_ids = set()
        self.packet_names = set()
        self.sums = {}

        # State
        self.md5_ok = True
        self.already_warned = set()

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

                for source_path in packets_data["podSources"]:
                    full_source_path = os.path.join("../eng-software-pod", source_path)
                    filehash = md5(full_source_path, True)

                    if full_source_path not in self.sums:
                        self.sums[full_source_path] = filehash

                    if self.sums[full_source_path] != filehash:
                        looked_at_code = int(os.environ.get("I_REALLY_LOOKED", -1)) == self.sums["I_REALLY_LOOKED"]

                        if looked_at_code:
                            self.sums[full_source_path] = filehash
                        elif full_source_path not in self.already_warned:
                            log.warning(f"Hash has changed for {full_source_path}")
                            log.warning(f"new={filehash}, old={self.sums[full_source_path]}")
                            self.already_warned.add(full_source_path)
                            self.md5_ok = False

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
                        all_users = [_["Name"] for _ in self.packets["packetDefinitions"] if _["PacketType"] == parsed_packet.packet_type]
                        log.warning(f"'{parsed_packet.name}' is reusing {hex(parsed_packet.packet_type)}. {all_users}")

                    # Append packet to lists.
                    self.packets["packetDefinitions"].append(parsed_packet.to_gs_dict())
                    self.packet_names.add(parsed_packet.name)
                    self.packet_ids.add(parsed_packet.packet_type)

    def load_all(self) -> None:
        """
            Loads all packet defintion files in the given input folder.
        """
        # Load the sums before the packets.
        try:
            self.load(self.file_sums_json)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

        # Load the packets.
        packet_files = get_packet_files(self.input_folder)
        for filename in packet_files:
            self.load(filename)

    def save(self) -> None:
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

        if self.md5_ok:
            # Did you really look at the code or did you not? ;)
            self.sums.update({
                "I_REALLY_LOOKED": random.randint(0, 65535),
            })

            with open(self.file_sums_json, "w") as f:
                json.dump(self.sums, f, indent=4)
        else:
            log.warning("Not saving updated checksums to disk.")
            log.warning("Please review the recent changes for those files and rerun this script with environment variable " \
                        f"I_REALLY_LOOKED={self.sums['I_REALLY_LOOKED']} if you would like to save checksums to disk.")
