import os

from data_constants import PACKET_SIZES
from typing import List


def get_packet_files(folder: str) -> List[str]:
    """
        Utility function that lists all YAML files in the input folder.
    """
    files = []

    for filename in os.listdir(folder):
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            files.append(os.path.join(folder, filename))

    return files


def get_size(packet_type: str) -> int:
    """
        Gets a packet's byte size from a dictionary.
    """

    if packet_type not in PACKET_SIZES:
        raise ValueError(f"Packet type '{packet_type}' is not a valid packet type.")

    return PACKET_SIZES[packet_type.lower()]
