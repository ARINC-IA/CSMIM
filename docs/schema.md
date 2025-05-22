# Schema for describing CSMIM payloads

The payload of a CSMIM message contains a CBOR-encoded resource value,
parameters for an EXECUTE request or a response to such a request. The
ARINC 853 standard defines in §6.2.7 facilities for specifying
valid payloads in an object type specification.

This document amends the ARINC 853 specification and provides a complete
Schema to specify formally how a CSMIM resource value, parameter or response
shall look like. It can be applied to nested elements, like dictionaries.


## General structure and syntax

CSMIM object type definitions are expressed using YAML in the CSMIM
Knowledge Base. The CSMIM Schema therefore uses YAML, too.

There are 3 places where a CSMIM Schema occurs in an object type definition.
Consider the following example:

```yaml
id: csmim.obj.something.1

resources:

  - id: value_resource
    mode: r
    type: int
    # Put schema for resource value here
    
  - id: command_resource
    mode: x
    parameters:
      - key: first_param
        type: int
        # Put schema for parameter value here
    
    type: string
    # Put schema for return value here
```

As you can see from the above example, the schema must be put wherever a
CSMIM data type is specified. It depends on the data type which schema
definitions are allowed or even required. The following sections list those
definitions for each of the data types of CSMIM.


## Schema for data type `bool`

There are no further definitions for boolean values:

    type: bool


## Schema for the data types `int`, `uint` and `float`

For integer and floating-point numbers, you can define a physical unit
for the value, which should be given as an SI unit.

    type: float
    unit: m/s


## Schema for the data types `string` and `bytes`

There are no further definitions for string values:

    type: string


## Schema for the data type `enum`

As defined in ARINC 853:

    type: enum
    enum-values:
      - name: identifier
        key: 3
        description: whatever


## Schema for the data type `utc`

There are no further definitions for time stamps:

    type: utc


## Schema for the data type array

For the items of the array, you can define descriptions:

    type: string[]
    array-items:
      description: If necessary

Note that the `type` of the array items is not specified again, because the
array type already does so. For multidimensional arrays, you can specify the
properties of the inner array in the first `array-items` definition, and the
properties of the items in the second:

    type: float[][]
    array-items:
      array-items:
        unit: m


## Schema for the data type `dict`

For a dictionary, you can specify the known dictionary keys:

    type: dict
    description: A description of the dictionary
    dict-items:
      - key: identifier
        optional: true
        description: A description of the dictionary item
        type: string

The `parameters` that describe the parameters of an EXECUTE request have the
same structure as these `dict-items`.

To ensure upwards compatibility, CSMIM dicts may always contain keys not
specified in the schema.
