import hashlib
import os
from typing import List, Union

from rloopDefinitionApp.data_constants import PACKET_SIZES


def md5(content: str, filehash: bool=False) -> Union[str, None]:
    """
        Lazy man's md5 for files and strings.
        Saves us from doing this.
            with open(filename, "rb") as f:
                hash = hashlib.md5(f.read()).hexdigest()
        Or this.
            hashlib.md5("rLoop!".encode("utf8")).hexdigest()
    """
    if filehash:
        with open(content, "rb") as f:
            hashed = hashlib.md5(f.read()).hexdigest()
    else:
        try:
            hashed = hashlib.md5(content.encode("utf8")).hexdigest()
        except AttributeError:
            hashed = hashlib.md5(content).hexdigest()

    return hashed


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
        raise ValueError("Packet type '{packet_type}' is not a valid packet type.".format(
            packet_type=packet_type
        ))

    return PACKET_SIZES[packet_type.lower()]
