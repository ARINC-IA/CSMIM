# Schema for describing CSMIM payloads

The payload of a CSMIM message contains a CBOR-encoded resource value,
parameters for an EXECUTE request or a response to such a request. The
ARINC 853 standard defines in §6.2.7 facilities for specifying
valid payloads in an object type specification.

This document amends the ARINC 853 specification and provides a
Schema to specify also for nested elements, like dictionaries.

CSMIM object type definitions are expressed using YAML in the CSMIM
Knowledge Base. The CSMIM Schema therefore uses YAML, too.


## Schema applicability

There are 3 places where a CSMIM Schema occurs in an object type definition.
Consider the following example:

```yaml
id: csmim.obj.something.1

resources:

  - id: value_resource
    mode: r
    type: int
    # Put resource schema here
    
  - id: command_resource
    mode: x
    parameters:
      - key: first_param
        type: int
        # Put resource schema here
    
    type: string
    # Put resource schema here
```

As you can see from the above example, the schema can be put wherever a
CSMIM data type is specified.


## Resource additions

This amendment allows for `description` tags to add human readable descriptions.

For integer and floating-point numbers, you can define a `unit` for the value,
which should be given as an SI unit.

```
type: float
unit: km/h
description: The speed of the device relative to the passenger
```

## Nested elements

ARINC 853 specifies `enum-values` for `enum`s. This amendment extends this pattern
also to arrays and dictionaries:

```
type: enum
description: The description of the enum
enum-values:
  - name: identifier
    key: 3
    description: Additional notes for that key
```

This can also be applied to nested elements, for example:

```
type: enum[]
description: If necessary
array-items:
  enum-values:
    - name: identifier
      key: 3
      description: Additional notes for that key 
```

Note that the `type` of the array items is not specified again, because the
array type already does so. For multidimensional arrays, you can specify the
properties of the inner array in the first `array-items` definition, and the
properties of the items in the second:

```
type: float[][]
array-items:
  array-items:
    unit: m
```

For a dictionary, you can specify the known dictionary keys:

```
type: dict
description: A description of the dictionary
dict-items:
  - key: identifier
    optional: true
    description: A description of the dictionary item
    type: string
```

The `parameters` that describe the parameters of an EXECUTE request have the
same structure as these `dict-items`.

To ensure upwards compatibility, CSMIM dicts may always contain keys not
specified in the schema.
