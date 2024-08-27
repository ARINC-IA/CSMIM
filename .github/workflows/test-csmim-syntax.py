import glob
import re
import pytest
import yaml
import yamale


# generate test cases for all files in the types folder
def pytest_generate_tests(metafunc):
    if "typeFile" in metafunc.fixturenames:
        filelist = glob.glob("types/*")
        metafunc.parametrize("typeFile", filelist)
    if "manufacturerFile" in metafunc.fixturenames:
        filelist = glob.glob("manufacturers/*")
        metafunc.parametrize("manufacturerFile", filelist)


# check the structure of manufacturer files matches the schema
def test_manufacturers_schema(manufacturerFile):
    schema = yamale.make_schema(".github/workflows/schema_manufacturers.yaml")
    data = yamale.make_data(manufacturerFile)
    yamale.validate(schema, data)


# check the structure of type files matches the CSMIM schema
def test_csmim_schema(typeFile):
    schema = yamale.make_schema(".github/workflows/schema_csmim.yaml")
    data = yamale.make_data(typeFile)
    yamale.validate(schema, data)


# check the id of all type files matches the filename
def test_id_matches(typeFile):
    fd = open(typeFile, "r")
    ty = yaml.safe_load(fd)
    assert typeFile == "types/" + ty["id"] + ".yaml"


# check the id of all manufacturer files matches the filename
def test_id_matches(manufacturerFile):
    fd = open(manufacturerFile, "r")
    my = yaml.safe_load(fd)
    assert manufacturerFile == "manufacturers/" + my["id"] + ".yaml"


# check referenced supertypes exist and are not empty
def test_supertypes_exist(typeFile):
    fd = open(typeFile, "r")
    ty = yaml.safe_load(fd)
    if "supertypes" in ty:
        for supertype in ty["supertypes"]:
            assert len(glob.glob("types/" + supertype + ".yaml")) == 1


# recursive helper function to go through the tree of referenced files and check
# each file is only visited once
def check_cycle(filename, visited=set()):
    try:
        visited.add(filename)
        fd = open(filename, "r")
        filecontent = yaml.safe_load(fd)
        if "supertypes" in filecontent:
            for next in filecontent["supertypes"]:
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
    assert check_cycle(typeFile, set()) is True
