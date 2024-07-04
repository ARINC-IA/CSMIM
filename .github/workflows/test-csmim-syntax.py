import glob
import re


def pytest_generate_tests(metafunc):
    filelist = glob.glob('types/*')
    metafunc.parametrize("fileName", filelist)


def test_filename_pattern(fileName):
    assert re.match(r'types/csmim\.obj\..*\d+\.yaml$', fileName) is not None
