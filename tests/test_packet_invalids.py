import pytest

from rloopDefinitionApp.model.packet import Packet


# Blanks
def test_blank_name():
    with pytest.raises(ValueError) as excinfo:
        Packet("", "", 0x00, "", [], False)
    assert 'must have a name' in str(excinfo.value)

def test_blank_node():
    with pytest.raises(ValueError) as excinfo:
        Packet("Packet Name", "", 0x00, "", [], False)
    assert 'must have a node' in str(excinfo.value)

def test_blank_type_and_0x00():
    with pytest.raises(ValueError) as excblank:
        Packet("Packet Name", "Node", None, "", [], False)
    assert 'must have a type' in str(excblank.value)

    with pytest.raises(ValueError) as exczero:
        Packet("Packet Name", "Node", 0x00, "", [], False)
    assert 'must have a type' in str(exczero.value)

def test_blank_prefix():
    Packet("Packet Name", "Node", 0x1000, "")

def test_daq_and_param():
    with pytest.raises(ValueError) as excinfo:
        Packet("Packet Name", "Node", 0x1000, "", [
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
            Packet.from_yaml("node", test_input)
        assert str(type(test_input)) in str(excinfo.value)

def test_vars_missing():
    # Node name
    with pytest.raises(ValueError) as excinfo:
        Packet.from_yaml("node {testvar}", {
            "packetName": "Test Packet",
            "packetType": 0x1000
        }, file_vars={})

    assert "in node" in str(excinfo.value)

    Packet.from_yaml("node {testvar}", {
        "packetName": "Test Packet",
        "packetType": 0x1000
    }, file_vars={"testvar": "works"})

    # Packet name
    with pytest.raises(ValueError) as excinfo:
        Packet.from_yaml("node", {
            "packetName": "Test Packet {testvar}",
            "packetType": 0x1000
        }, file_vars={})

    assert "in packet" in str(excinfo.value)

    Packet.from_yaml("node", {
        "packetName": "Test Packet {testvar}",
        "packetType": 0x1000
    }, file_vars={"testvar": "works"})

    # Prefix
    with pytest.raises(ValueError) as excinfo:
        Packet.from_yaml("node", {
            "packetName": "Test Packet",
            "prefix": "{testvar}",
            "packetType": 0x1000
        }, file_vars={})

    assert "in prefix" in str(excinfo.value)

    Packet.from_yaml("node", {
        "packetName": "Test Packet",
        "prefix": "{testvar}",
        "packetType": 0x1000
    }, file_vars={"testvar": "works"})

def test_unclosed_loop():
    with pytest.raises(ValueError) as excinfo:
        Packet.from_yaml("node", {
            "packetName": "Test Packet",
            "prefix": "Test",
            "packetType": 0x1000,
            "parameters": [{
                "name": "Unclosed Loop 1",
                "type": "int8",
                "beginLoop": True,
            }]
        }, file_vars={})
    assert "Loop not closed" in str(excinfo.value)

def test_loop_end_not():
    with pytest.raises(ValueError) as excinfo:
        Packet.from_yaml("node", {
            "packetName": "Test Packet",
            "prefix": "Test",
            "packetType": 0x1000,
            "parameters": [{
                "name": "Closed Loop 1",
                "type": "int8",
                "endLoop": True,
            }]
        }, file_vars={})
    assert "not in a loop" in str(excinfo.value)

def test_loop_begin_twice():
    with pytest.raises(ValueError) as excinfo:
        Packet.from_yaml("node", {
            "packetName": "Test Packet",
            "prefix": "Test",
            "packetType": 0x1000,
            "parameters": [{
                "name": "Open Loop 1",
                "type": "int8",
                "beginLoop": True,
            }, {
                "name": "Open Loop 1",
                "type": "int8",
                "beginLoop": True,
            }]
        }, file_vars={})
    assert "already in a loop" in str(excinfo.value)

def test_unclosed_group():
    with pytest.raises(ValueError) as excinfo:
        Packet.from_yaml("node", {
            "packetName": "Test Packet",
            "prefix": "Test",
            "packetType": 0x1000,
            "parameters": [{
                "name": "Group Test {i}",
                "type": "int8",
                "iterate": {
                    "beginGroup": True,
                    "start": 1,
                    "end": 2,
                }
            }, {
                "name": "Unclosed Group {i}",
                "type": "int8"
            }]
        }, file_vars={})
    assert "unclosed iter" in str(excinfo.value)
