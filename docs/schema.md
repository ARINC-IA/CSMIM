# Schema for Describing CSMIM Payloads

The payload of a CSMIM message contains a CBOR-encoded resource value,
parameters for an EXECUTE request or a responses to such a request.  The
ARINC 853 standard already defines in §6.2.7 some facilities for specifying
valid payloads in an object type specification.  Some elements are missing
from the standard, though, for example a way to specify the items of a CBOR
dictionary.

This document amends the definitions of ARINC 853, thereby providing a
complete Schema to specify formally how a CSMIM resource value, parameter or
response may look like.

The CSMIM Schema definition is much inspired by
[JSON Schema](https://json-schema.org). It differs only slightly in
structure and naming, in order to stay consistent with the existing
definitions of ARINC 853.



## General Structure and Syntax

CSMIM object type definitions are expressed using YAML in the CSMIM
Knowledge Base. The CSMIM Schema therefore uses YAML, too.

There are 3 places where a CSMIM Schema occurs in an object type definition.
Consider the following example:

```yaml
id: csmim.obj.something.1
supertypes: []
attributes: []
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



# Schema for the data types `int`, `uint` and `float`

For integer and floating-point numbers, you can define the allowed range for
the value:

    type: int
    minimum: 3
    exclusive-minimum: 2
    maximum: 20
    exclusive-maximum: 21

There are two types of minimum and maximum: inclusive and exclusive. The
value must be >= the minimum respectively > the exclusive minimum. 

You can also define a physical unit for the value, which must always be
given as an SI unit.

    type: float
    unit: m/s



# Schema for the data types `string` and `bytes`

For human-readable strings and byte strings, you can define the allowed
range for the string length:

    type: string
    min-length: 2
    max-length: 3
    
**TODO:** Provide shortcut `length`?



# Schema for the data type `enum`

As defined in ARINC 853:

    type: enum
    enum-values:
      - name: identifier
        key: 3
        description: whatever



# Schema for the data type `utc`

There are no further definitions for time stamps:

    type: utc



# Schema for the data type array

You can define the allowed range for the number of items of an array:

    type: int[]
    min-items: 1
    max-items: 3

For the items of the array, you can define a schema that validates these:

    type: string[]
    array-items:
      description: If necessary
      max-length: 20

Note that the `type` of the array items is not specified again, because the
array type already does so. For multidimensional arrays, you can specify the
properties of the inner array in the first `array-items` definition, and the
properties of the items in the second:

    type: float[][]
    max-items: 3
    array-items:
      max-items: 3
      array-items:
        minimum: 0.0
        maximum: 10000.0
        unit: m



# Schema for the data type `dict`

For a dictionary, you can specify the known dictionary keys and a schema
that validates their value:

    type: dict
    dict-items:
      - key: identifier
        optional: true
        description: A description of the dictionary item
        type: string
        max-length: 8

The `parameters` that describe the parameters of an EXECUTE request have the
same structure as these `dict-items`.

To ensure upwards compatibility, CSMIM dicts may always contain keys not
specified in the schema.
