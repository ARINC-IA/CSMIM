import glob
import yaml
import yamale
import os.path
import re


# helper function: loads a yaml file
def load_object_type(yamlFile):
    fd = open(yamlFile, "r")
    return yaml.safe_load(fd)


# generate test cases for all files
def pytest_generate_tests(metafunc):
    if "typeFile" in metafunc.fixturenames:
        filelist = glob.glob("types/*")
        metafunc.parametrize("typeFile", filelist)
    if "manufacturerFile" in metafunc.fixturenames:
        filelist = glob.glob("manufacturers/*")
        metafunc.parametrize("manufacturerFile", filelist)
    if "pathFile" in metafunc.fixturenames:
        filelist = glob.glob("path/**/*", recursive=True)
        metafunc.parametrize("pathFile", filelist)


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
    content = load_object_type(manufacturerFile)
    assert manufacturerFile == "manufacturers/" + content["id"] + ".yaml"


# check referenced supertypes exist and are not empty
def test_supertypes_exist(typeFile):
    content = load_object_type(typeFile)
    if "supertypes" in content:
        for supertype in content["supertypes"]:
            assert len(glob.glob("types/" + supertype + ".yaml")) == 1


# check all files in the path folder are softlinks
def test_path_are_softlinks(pathFile):
    assert os.path.islink(pathFile) or os.path.isdir(pathFile)


# check all links in the path folder are valid
def test_path_links_valid(pathFile):
    if os.path.islink(pathFile):
        target = os.readlink(pathFile)
        # must be relative symlink
        assert not os.path.isabs(target)
        # Resolve relative path
        target = os.path.join(os.path.dirname(pathFile), target)
        assert os.path.exists(target)
        target = os.path.normpath(target)
        assert os.path.dirname(target) == "types"
        assert os.path.basename(target) == os.path.basename(pathFile)


# check that paths use only valid characters
def test_path_dirs_valid(pathFile):
    if os.path.isdir(pathFile):
        assert re.fullmatch("[A-Za-z0-9\\-._]+", os.path.basename(pathFile))


# recursive helper function: iterate the tree of referenced files and check that
# each file is only visited once
def has_supertypes_cycle(typeFile, visited):
    visited.add(typeFile)
    content = load_object_type(typeFile)
    if "supertypes" in content:
        for supertype in content["supertypes"]:
            supertypeFile = "types/" + supertype + ".yaml"
            if supertypeFile in visited:
                return True
            if has_supertypes_cycle(supertypeFile, visited):
                return True
    return False


# helper function: whether the resource is marked optional
def is_optional(resource):
    return ("optional" in resource) and (resource["optional"] is True)


# helper function: whether the resource is marked "restricted access"
def is_racc(resource):
    return ("racc" in resource) and (resource["racc"] is True)


# helper function: check that the resource overwrite is valid
# more checks would be possible, e.g. parameters are a subset
def check_resource_overwrite_valid(resource, overwrite):
    assert is_optional(resource) or not is_optional(overwrite)
    assert is_racc(resource) == is_racc(overwrite)
    assert overwrite["mode"].count(resource["mode"]) == 1
    assert overwrite["type"] == resource["type"]


# recursive helper function: iterate the tree of supertypes and check that
# resource overwrites are valid and that there are no conflicts
def has_resource_conflict(typeFile, resources):
    content = load_object_type(typeFile)
    myResources = {}
    if "supertypes" in content:
        for nextId in content["supertypes"]:
            if has_resource_conflict("types/" + nextId + ".yaml", myResources):
                return True
    for resource in content["resources"]:
        if resource["id"] in myResources:
            check_resource_overwrite_valid(myResources[resource["id"]], resource)
        myResources[resource["id"]] = resource
    conflict = resources.keys() & myResources.keys()
    if conflict:
        print("conflicting resource(s) ", conflict)
        return True
    resources |= myResources
    return False


# check there is no cyclic dependencies in referenced supertypes
def test_supertypes_valid(typeFile):
    assert not has_supertypes_cycle(typeFile, set())
    assert not has_resource_conflict(typeFile, {})


# check that 'enum-values' are defined for all resources of type 'enum'
def test_resource_enum_values(typeFile):
    content = load_object_type(typeFile)
    for resource in content["resources"]:
        if resource["type"] == "enum":
            assert "enum-values" in resource
        else:
            assert "enum-values" not in resource


# check that 'parameters' are defined for all executable resources
def test_resource_parameters(typeFile):
    content = load_object_type(typeFile)
    for resource in content["resources"]:
        if resource["mode"] == "x":
            assert "parameters" in resource
        else:
            assert "parameters" not in resource


# check that read- or writeable resources are not type void
def test_resource_type(typeFile):
    content = load_object_type(typeFile)
    for resource in content["resources"]:
        if resource["mode"] in {"r", "w", "rw"}:
            assert resource["type"] != "void"


# helper function: returns a dictionary containing all resource IDs of the given
# object type file, including those of all its supertypes
def load_object_type_resources(yamlFile, visited):
    visited.add(yamlFile)
    content = load_object_type(yamlFile)
    result = {}
    if "supertypes" in content:
        for supertype in content["supertypes"]:
            if not supertype in visited:
                result |= load_object_type_resources(
                    "types/" + supertype + ".yaml", visited
                )
    for resource in content["resources"]:
        result[resource["id"]] = content["id"]
    return result


# recursive helper function: checks that there is no subdirectory in the given
# path that has the same name as a resource of any of the linked object types in
# the given path
def has_path_conflict_in(path):
    resources = {}
    for entry in glob.glob(path + "/*"):
        if os.path.islink(entry):
            try:
                resources |= load_object_type_resources(entry, set())
            except:
                print("ignoring", entry)
    result = False
    for entry in glob.glob(path + "/*"):
        if os.path.isdir(entry):
            if os.path.basename(entry) in resources:
                print(
                    "conflict:",
                    entry,
                    "is a resource of",
                    resources[os.path.basename(entry)],
                )
                result = True
            result |= has_path_conflict_in(entry)
    return result


# check that no resource of any of the object types linked in the "path/"
# directory can conflict with another object's path
def test_path_conflicts():
    assert not has_path_conflict_in("path")
