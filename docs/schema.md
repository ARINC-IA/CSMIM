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
    # Put schema here to specify resource value
    
  - id: command_resource
    mode: x
    parameters:
      - key: first_param
        type: int
        # Put schema here to specify command parameter
    
    type: string
    # Put schema here to specify response
```

As you can see from the above example, the schema can be put wherever a
CSMIM data type is defined.


## Schema definitions

The following sections list and explain all elements that you can use in
CSMIM Schema definitions. This includes the elements already specified in
ARINC 853 as well as the amendments by this document.


### Descriptions

You may add a `description` entry with a human-readable description at every
position in the Schema:

```yaml
type: float
description: The speed of the device relative to the passenger
```


### Physical units

For integer and floating-point numbers, you should define a `unit` for the 
value, if applicable. Units should belong to the SI system.

```yaml
type: float
unit: m/s
```


### Enumeration values

For `enum`-typed data items, you must add an `enum-values` entry to the Schema.
This is as specified by ARINC 853:

```yaml
type: enum
description: The description of the enum
enum-values:
  - name: identifier
    key: 3
    description: Additional notes for this enumeration value
```

The Schema for each enumeration value contains the following entries:

- `name` is a short human-readable identifier string.
- `key` is the unsigned integer that represents the enumeration value in CBOR.
- `description` is a longer, human-readable description (if necessary).


### Array items

For data items in an array, you may add an `array-items` entry to the Schema.
This element contains a nested Schema that describes the array items:

```yaml
type: enum[]
description: Description of the whole array # if necessary
array-items:
  enum-values:
    - name: identifier
      key: 3
      description: Additional notes for this enumeration value 
```

For multidimensional arrays, you must use nested `array-items` elements:

```yaml
type: float[][]
array-items:
  array-items:
    unit: m
```

Note that the `type` of the array items is not specified again, because the
array type already does so.


### Dictionary items

For a dictionary, you should specify the known dictionary keys with a
`dict-items` entry in the Schema:

```yaml
type: dict
description: A description of the dictionary
dict-items:
  - key: identifier
    optional: true
    type: string
    description: A description of this dictionary item
```

The nested Schema of a dictionary item contains the following entries:

- `key` is the name of the item, and represents it in CBOR.
- `optional` specifies whether the item may be omitted from the dictionary;
  if not present, then the item is mandatory.
- `type` is the CSMIM data type of the item.
- all other Schema elements as applicable for the `type`.

To ensure upwards compatibility, CSMIM dictionaries may always contain keys not
specified in the Schema.


### Parameters for commands

The `parameters` Schema entry which describes the parameters of an EXECUTE 
request has the same structure as a `dict-items` entry:

```yaml
resources:
  - id: reset
    mode: x
    type: void
    parameters:
      - key: wait_time
        optional: true
        type: uint
        unit: s
        description: How long to wait before resetting the LRU
```
