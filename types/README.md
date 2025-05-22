# Object types

This folder contains all object type definitions, including deprecated versions.

In order to see type definitions currently being used, you can browse the 
[path](/path) folder. Type definitions are linked there according to where they are
located in the topic path.

**Example:** The `csmim.obj.registration.1.yaml` is linked in `path/core/csmim/registration`.
This reflects that you will reach the described `claim` interface at `v1/command/<username>/core/csmim/registration/claim`.

If you want to add your manufacturer-specific (non-standardized, non-public) type definitions,
you need to add your manufacturer code to the object type id. In case you want to standardize
your object type definition, please use our [issue template](https://github.com/ARINC-IA/CSMIM/issues/new?template=add_type.md).
