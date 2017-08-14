import json
import logging
import os
from typing import Optional, Union

import jsonschema
import yaml

from rloopDefinitionApp.exporters import ALL_EXPORTERS
from rloopDefinitionApp.model.packet import Packet
from rloopDefinitionApp.model.schemas import PACKET_LIST_SCHEMA
from rloopDefinitionApp.utils import get_packet_files, md5

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class DefinitionGenerator:
    def __init__(self, input_folder: str="packets/", output_folder: str="output/"):
        # Data holding
        self.packets = []
        self.packet_ids = set()
        self.packet_names = set()
        self.sums = {}

        # State
        self.md5_ok = True
        self.already_warned = set()

        # Paths
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.file_sums_json = os.path.join(self.output_folder, "file_sums.json")

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

                # Verify schema before moving on to verification.
                jsonschema.validate(packets_data, PACKET_LIST_SCHEMA)

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
                            log.warning(
                                "Hash has changed for %s\nnew=%s, old=%s",
                                full_source_path,
                                filehash,
                                self.sums[full_source_path]
                            )
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
                        raise ValueError("Packet name '{packet_name}' is already in use.'".format(
                            packet_name=parsed_packet.name,
                        ))

                    # Duplicate ID warning
                    if parsed_packet.packet_type in self.packet_ids:
                        other_usages = [
                            _.name for _ in self.packets
                            if _.packet_type == parsed_packet.packet_type
                        ]
                        log.warning(
                            "'%s' is reusing %s. %s",
                            parsed_packet.name,
                            hex(parsed_packet.packet_type),
                            other_usages
                        )

                    # Append packet to lists.
                    self.packets.append(parsed_packet)
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

        for exporter in ALL_EXPORTERS:
            exporter(self.packets, self.output_folder, self).export()
