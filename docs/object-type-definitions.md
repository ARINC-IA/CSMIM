# Object type definition amendments

This document amends the ARINC 853 specification and provides
clarifications and further features for object type definitions.
CSMIM object type definitions are expressed using YAML in the CSMIM
Knowledge Base.


## Schema for describing CSMIM payloads

See the separate document [Schema for describing CSMIM payloads](schema.md).


## Error response definition

Resources may declare resource-specific error responses with an optional
`errors` entry. Each entry has a response `code`, and may have a
human-readable `description` and `dict-items`:

```yaml
resources:
  - id: motion
    mode: x
    type: void
    errors:
      - code: 409
        description: Motion is blocked by an active safety restriction.
        dict-items:
          - key: restriction
            type: enum
            enum-values:
              - name: obstruction
                key: 1
```

`errors` may be used with every resource mode. Its omission does not prohibit
error responses; clients must handle undeclared response codes as required by
ARINC 853. An error code must be in the 4xx or 5xx range and must occur only
once per resource.

ARINC 853 specifies that an error-response payload is either empty or a CBOR
dictionary. The optional `error` dictionary item is defined by the protocol
and must not be declared. Use `dict-items` only to describe additional,
resource-defined dictionary items. A resource without defined error-response
`dict-items` may still return an error-response payload.
