import os
import random
import pytest
import shutil
import json
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

def test_full_app(clean_test_dir, caplog):
    # Create initial hash files.
    hash_file_1 = md5(create_test_file(TEST_FILE_1))
    hash_file_2 = md5(create_test_file(TEST_FILE_2))

    # Set the seed to 0 and run the app. This should ensure I_REALLY_LOOKED=50494
    random.seed(0)
    run_app()

    # Actual tests
    verify_sums(hash_file_1, hash_file_2)

    # Change the file hashes and redo the run.
    hash_file_1 = md5(create_test_file(TEST_FILE_1))
    hash_file_2 = md5(create_test_file(TEST_FILE_2))
    run_app()
    assert all([
        "for /tmp/_rloop_pytest_fakesource1" in caplog.text,
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
