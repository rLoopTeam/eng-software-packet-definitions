import yaml

from rloopDefinitionApp.exporters.base import Exporter


class GroundStation(Exporter):
    def create_gs_dict(self, packet):
        output = {
            "Name": packet.name,
            "PacketType": packet.packet_type,
            "Node": packet.node,
            "DAQ": False,
        }

        if packet.prefix:
            output.update({
                "ParameterPrefix": packet.prefix + " ",
            })

        if packet.daq:
            output.update({
                "DAQ": True,
                "dataType": packet.daq["type"],
                "dataSize": packet.daq["size"],
            })

        if packet.parameters:
            output.update({
                "Parameters": packet.parameter_hack_for_ground_station(),
            })

        return output

    def export(self):
        formatted_packets = [self.create_gs_dict(packet) for packet in self.packets]
        with self.yield_file("gs_definitions.yml") as f:
            yaml.dump({"packetDefinitions": formatted_packets}, f)