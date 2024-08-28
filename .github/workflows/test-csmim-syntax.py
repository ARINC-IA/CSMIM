import glob
import re
import pytest
import yaml
import yamale


# helper function: loads an object type file
def load_object_type(typeFile):
    fd = open(typeFile, "r")
    return yaml.safe_load(fd)



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
def test_object_type_schema(typeFile):
    schema = yamale.make_schema(".github/workflows/schema_csmim.yaml")
    data = yamale.make_data(typeFile)
    yamale.validate(schema, data)


# check the id of all type files matches the filename
def test_type_id_matches(typeFile):
    content = load_object_type(typeFile)
    assert typeFile == "types/" + content["id"] + ".yaml"


# check the id of all manufacturer files matches the filename
def test_manufacturer_id_matches(manufacturerFile):
    fd = open(manufacturerFile, "r")
    my = yaml.safe_load(fd)
    assert manufacturerFile == "manufacturers/" + my["id"] + ".yaml"


# check referenced supertypes exist and are not empty
def test_supertypes_exist(typeFile):
    content = load_object_type(typeFile)
    if "supertypes" in content:
        for supertype in content["supertypes"]:
            assert len(glob.glob("types/" + supertype + ".yaml")) == 1


# recursive helper function to go through the tree of referenced files and check
# each file is only visited once
def has_supertypes_cycle(typeFile, visited):
    visited.add(typeFile)
    content = load_object_type(typeFile)
    if "supertypes" in content:
        for nextId in content["supertypes"]:
            nextFile = "types/" + nextId + ".yaml"
            if nextFile in visited:
                return True
            if has_supertypes_cycle(nextFile, visited):
                return True
    return False


# check there is no cyclic dependencies in referenced supertypes
def test_supertypes_cycle(typeFile):
    assert not has_supertypes_cycle(typeFile, set())


# check that 'enum-values' are defined for all resources of type 'enum'
def test_resource_enum_values(typeFile):
    content = load_object_type(typeFile)
    for resource in content["resources"]:
        if resource["type"] == "enum":
            assert "enum-values" in resource          
    

# check that 'parameters' are defined for all executable resources
def test_resource_parameters(typeFile):
    content = load_object_type(typeFile)
    for resource in content["resources"]:
        if resource["mode"] == "x":
            assert "parameters" in resource          
