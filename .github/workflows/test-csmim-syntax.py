import glob
import re
import yaml


# generate test cases for all files in the types folder
def pytest_generate_tests(metafunc):
    filelist = glob.glob("types/*")
    metafunc.parametrize("typeFile", filelist)


# check that the filename of all type definitions is conform to the specification
def test_filename_pattern(typeFile):
    assert (
        re.match(r"types/csmim\.obj\..[a-z0-9_\-\.]+\.\d+\.yaml$", typeFile) is not None
    )


# check the id of all type files matches the filename
def test_id_matches(typeFile):
    fd = open(typeFile, "r")
    ty = yaml.safe_load(fd)
    assert "id" in ty
    assert isinstance(ty["id"], str)
    assert typeFile == "types/" + ty["id"] + ".yaml"


# check referenced supertypes exist and are not empty
def test_supertypes_exist(typeFile):
    fd = open(typeFile, "r")
    ty = yaml.safe_load(fd)
    if "supertypes" in ty:
        for supertype in ty["supertypes"]:
            assert len(glob.glob("types/" + supertype + ".yaml")) == 1


# recursive helper function to go through the tree of referenced files and check
# each file is only visited once
def check_cycle(filename, parameter, visited):
    try:
        visited.add(filename)
        fd = open(filename, "r")
        filecontent = yaml.safe_load(fd)
        if parameter in filecontent:
            for next in filecontent[parameter]:
                next = "types/" + next + ".yaml"
                if next in visited:
                    return False
                if not check_cycle(next, visited):
                    return False
        return True
    except Exception as e:
        print(e)
        return False


# check there is no cyclic dependencies in referenced supertypes
def test_supertype_cycles(typeFile):
    assert check_cycle(typeFile, "supertypes", set()) is True
