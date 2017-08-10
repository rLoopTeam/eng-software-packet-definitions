import pytest
from rloopDefinitionApp.structs import Packet

# Blanks
def test_blank_name():
    with pytest.raises(ValueError) as excinfo:
        packet = Packet("", "", 0x00, "", [], False)
    assert 'must have a name' in str(excinfo.value)

def test_blank_node():
    with pytest.raises(ValueError) as excinfo:
        packet = Packet("Packet Name", "", 0x00, "", [], False)
    assert 'must have a node' in str(excinfo.value)

def test_blank_type_and_0x00():
    with pytest.raises(ValueError) as excblank:
        packet = Packet("Packet Name", "Node", None, "", [], False)
    assert 'must have a type' in str(excblank.value)

    with pytest.raises(ValueError) as exczero:
        packet = Packet("Packet Name", "Node", 0x00, "", [], False)
    assert 'must have a type' in str(exczero.value)

def test_blank_prefix():
    packet = Packet("Packet Name", "Node", 0x1000, "")

def test_daq_and_param():
    with pytest.raises(ValueError) as excinfo:
        packet = Packet("Packet Name", "Node", 0x1000, "", [
            {"name": "Test Packet", "type": "int32"}
        ], {"type": "int32"})
    assert 'cannot both be' in str(excinfo.value)

# YAML user error
def test_not_a_dict():
    TEST_INPUTS = [
        "string",
        1337,
        133.7,
        None,
        True,
        False
    ]
    for test_input in TEST_INPUTS:
        with pytest.raises(TypeError) as excinfo:
            packet = Packet.from_yaml("node", test_input)
        assert str(type(test_input)) in str(excinfo.value)

def test_vars_missing():
    # Node name
    with pytest.raises(ValueError) as excinfo:
        packet = Packet.from_yaml("node {testvar}", {
            "packetName": "Test Packet",
            "packetType": 0x1000
        }, file_vars={})

    assert "in node" in str(excinfo.value)

    packet = Packet.from_yaml("node {testvar}", {
        "packetName": "Test Packet",
        "packetType": 0x1000
    }, file_vars={"testvar": "works"})

    # Packet name
    with pytest.raises(ValueError) as excinfo:
        packet = Packet.from_yaml("node", {
            "packetName": "Test Packet {testvar}",
            "packetType": 0x1000
        }, file_vars={})

    assert "in packet" in str(excinfo.value)

    packet = Packet.from_yaml("node", {
        "packetName": "Test Packet {testvar}",
        "packetType": 0x1000
    }, file_vars={"testvar": "works"})

    # Prefix
    with pytest.raises(ValueError) as excinfo:
        packet = Packet.from_yaml("node", {
            "packetName": "Test Packet",
            "prefix": "{testvar}",
            "packetType": 0x1000
        }, file_vars={})

    assert "in prefix" in str(excinfo.value)

    packet = Packet.from_yaml("node", {
        "packetName": "Test Packet",
        "prefix": "{testvar}",
        "packetType": 0x1000
    }, file_vars={"testvar": "works"})
