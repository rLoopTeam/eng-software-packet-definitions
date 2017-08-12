import os
import random
import pytest
import shutil
import json
import yaml
from rloopDefinitionApp import DefinitionGenerator
from rloopDefinitionApp.utils import md5

TEST_DIRECTORY = "/tmp/__rloop_pytest_"
TEST_OUTPUT_DIRECTORY = os.path.join(TEST_DIRECTORY, "output/")
TEST_FILE_1 = "/tmp/_rloop_pytest_fakesource1"
TEST_FILE_2 = "/tmp/_rloop_pytest_fakesource2"

@pytest.fixture(scope="module")
def clean_test_dir():
    dirs_to_clean = [
        TEST_DIRECTORY,
    ]

    files_to_clean = [
        TEST_FILE_1,
        TEST_FILE_2,
    ]

    for dirname in dirs_to_clean:
        try:
            shutil.rmtree(dirname)
        except FileNotFoundError:
            pass

    for filename in files_to_clean:
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

def create_test_file(filename: str) -> str:
    test_data = str(random.randint(0, 99999))
    with open(filename, "w") as f:
        f.write(test_data)
        return test_data

def verify_sums(hash1, hash2):
    with open(os.path.join(TEST_OUTPUT_DIRECTORY, "fileSums.json"), "r") as f:
        hashes = json.load(f)

    assert hashes[TEST_FILE_1] == hash1
    assert hashes[TEST_FILE_2] == hash2

def run_app():
    generator = DefinitionGenerator(
        "tests/full_app_test_sanity/",
        TEST_OUTPUT_DIRECTORY,
    )
    generator.load_all()
    generator.save()

def get_packet(defintions, packet_name):
    for packet in defintions["packetDefinitions"]:
        if packet["Name"].strip().lower() == packet_name.strip().lower():
            return packet
    
    raise ValueError("Packet '%s' does not exist in test defintions. (Possible breakage?)" % (packet_name))

def verify_all_data():
    packet_defs = None
    packet_defs_json = None
    packet_defs_human = None

    # Load all definitions.
    with open(os.path.join(TEST_OUTPUT_DIRECTORY, "packetDefinitions.yml")) as f:
        packet_defs = yaml.load(f)

    with open(os.path.join(TEST_OUTPUT_DIRECTORY, "packetDefinitions.json")) as f:
        packet_defs_json = json.load(f)

    with open(os.path.join(TEST_OUTPUT_DIRECTORY, "packetDefinitions_human.json")) as f:
        packet_defs_human = json.load(f)

    # If any this is inequal, something has gone wrong writing one of the files.
    assert packet_defs == packet_defs_human
    assert packet_defs == packet_defs_json
    assert packet_defs_human == packet_defs_json
    assert packet_defs == packet_defs_human == packet_defs_json

    # Verify Single Iterated Data
    iter_params = get_packet(packet_defs, "Single Iterated Data")["Parameters"]
    assert len(iter_params) == 10
    assert iter_params[0]["Name"] == "Faulty Flags"
    assert iter_params[1]["Name"] == "Fake Sensor 1"
    assert iter_params[2]["Name"] == "Fake Sensor 2"
    assert iter_params[3]["Name"] == "Fake Sensor 3"
    assert iter_params[4]["Name"] == "Fake Sensor 4"
    assert iter_params[5]["Name"] == "Fake Sensor 5"
    assert iter_params[6]["Name"] == "Fake Sensor 6"
    assert iter_params[7]["Name"] == "Fake Sensor 7"
    assert iter_params[8]["Name"] == "Fake Sensor 8"
    assert iter_params[9]["Name"] == "Flotation Device"

    # Verify Group Iterated Data
    iter_params = get_packet(packet_defs, "Group Iterated Data")["Parameters"]
    assert len(iter_params) == 8
    assert iter_params[0]["Name"] == "Snowglobes are my life"
    assert iter_params[1]["Name"] == "Group X 1"
    assert iter_params[2]["Name"] == "Group Y 1"
    assert iter_params[3]["Name"] == "Group Z 1"
    assert iter_params[4]["Name"] == "Group X 2"
    assert iter_params[5]["Name"] == "Group Y 2"
    assert iter_params[6]["Name"] == "Group Z 2"
    assert iter_params[7]["Name"] == "Placeholder, I swear"

def test_full_app(clean_test_dir, caplog):
    # Create initial hash files.
    hash_file_1 = md5(create_test_file(TEST_FILE_1))
    hash_file_2 = md5(create_test_file(TEST_FILE_2))

    # Set the seed to 0 and run the app. This should ensure I_REALLY_LOOKED=50494
    random.seed(0)
    run_app()

    # Actual tests
    verify_sums(hash_file_1, hash_file_2)
    verify_all_data()

    # Change a file hash and redo the run.
    hash_file_2 = md5(create_test_file(TEST_FILE_2))
    run_app()
    assert all([
        "for /tmp/_rloop_pytest_fakesource2" in caplog.text,
        "rerun this script with environment variable" in caplog.text
    ])

    """"
    TODO: How to set environ pytest
    # Redo the run again with the variable set.
    caplog.handler.records = []
    os.environ["I_REALLY_LOOKED"] = "50494"
    print(os.environ)
    run_app()
    assert breaker
    """
