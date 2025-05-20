# Best Practices for CSMIM Definitions

This document collects best practices for defining CSMIM artifacts, in
particular object types, resource types, their paths etc. The document intends
to provide design guidance. Its rules are not mandatory to be followed.


## Object Type Definitions

Define object types to be abstracted from hardware layout and implementation
details whenever possible. <br />
*Rationale:* The CSMIM data model structure should be the same for all current
and future system instantiations, regardless of how a particular manufacturer
chooses to structure its hardware.

Define object types to capture one piece of functionality. <br />
*Rationale:* This promotes abstraction from hardware layout. And it avoids the
situation where the resources of one CSMIM object have to be provided by
multiple hardware devices - which is complicated to achieve.


## Resource Type Definitions

Restrict resource identifiers to use only lower-case characters and the
underscore. <br />
*Rationale:* This avoids lower-case/upper-case confusion.

Choose the identifier of a `bool` resource type (or parameter or `dict` item)
such that the meaning of the *true* and *false* value is immediately obvious.

Use the `enum` data type to capture a *finite* number of states that will be
processed by another device on the aircraft. Do not declare the enumeration to
be future-extensible if a processing device may come from a different
manufacturer. <br />
*Rationale:* This ensures future compatibility and clarity of software 
implementations.

Use the `string` data type to capture a potentially infinite number of states.
Values are typically not processed by another device on the aircraft (displaying
a string to a human does not constitute "processing").

Use an array or `dict` data type to group multiple data items that depend on
each other, that means, data items that must be transmitted atomically in order
to ensure validity of the combined value. <br />
*Rationale:* Data integrity. <br />
*Example:* Velocity or acceleration would use an array. A timestamp made of 
hour, minute and second would use a dict. On the other hand, flight phase and 
altitude would be separate resources.

Use a writable resource if the resource has a single "value" that can be
changed. Make sure that the operation is idempotent (multiple WRITE requests
have the same effect as a single one). If this is not the case, you must use an
executable resource instead.


## Paths and Data Model Structure

Choose CSMIM object paths such that the resulting object tree resembles the
structure of the aircraft and its subsystems, in particular the aircraft cabin
with its monuments and assemblies. The real-world equivalent of an object lower
in the tree should always be *contained in* its parent. <br />
*Rationale:* This ensures future extensibility of the object tree. <br />
*Example:* Galley inserts are part of a galley. A master galley control unit is
part of a galley. The object representing a galley insert cannot have its path
below an object representing the MGCU, because a galley insert is not contained
in an MGCU.

Choose object paths in such a way that MQTT topic name filters can be put to
good use.

Use the security domain as the first element of a CSMIM object path. 
Valid domain names are defined in the CSMIM repository. <br />
*Rationale:* Together with registration access rules configured in the CSMIM 
central services, this guarantees a certain authenticity of published data.

Use the system's ATA chapter name as the second element of a CSMIM object path. 
<br />
*Rationale:* Together with registration access rules configured in the CSMIM
central services, this guarantees a certain authenticity of published data.

Consider using the ATA subchapter name as the third element of a CSMIM 
object path. <br />
*Note:* CSMIM central services will typically not restrict registration access
on ATA subchapter granularity.

Restrict object paths to use only lower-case characters and the underscore,
except for equipment IDs (e.g. Airbus FIN). <br />
*Rationale:* This avoids lower-case/upper-case confusion.

Use `.../<collection-name>/<instance-id>` as an object path element to capture a
collection of similar objects. The collection name should be a plural noun.
The instance ID will be defined by the aircraft manufacturer in many cases.
<br />
*Example:* `.../galleys/M5/gains/208` (two nested collections)


## Message Payloads

Do not publish personal data, i.e. data that is subject to data privacy
protection legislations such as the European GDPR, on public resources. Use an
access-restricted topic instead, or publish anonymized data on a public topic
and a decoding table on an access-restricted topic. Use the MQTT message user
property `privacyData` as described in ARINC 853 §6.3.4.7.
