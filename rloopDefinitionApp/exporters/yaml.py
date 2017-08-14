import datetime

import yaml

from rloopDefinitionApp.exporters.base import Exporter


class Yaml(Exporter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.out_version = 2

    def format_packet(self, packet):
        output = {
            "type": packet.packet_type,
            "node": packet.node,
            "prefix": packet.prefix,
            "parameters": packet.parameters
        }

        if packet.daq:
            output.update(
                {"daq": {
                    "type": packet.daq["type"]
                }}
            )

        return output


    def export(self):
        formatted_packets = {
            "_version": self.out_version,
            "_comment": self.autogen_comment,
            "_gentime": datetime.datetime.utcnow().isoformat(),  # https://xkcd.com/1179/
        }

        for packet in self.packets:
            formatted_packets[packet.name] = self.format_packet(packet)

        with self.yield_file("packet_defintions_v%s.yml" % (self.out_version)) as f:
            yaml.dump(formatted_packets, f)
