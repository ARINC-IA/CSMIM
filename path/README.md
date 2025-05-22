# Topic paths

This folder collects well-known topic paths and links to type definitions at the respective locations.

Paths begin with a domain, which is also included in each client certificate.
These domains are related to ARINC 664, Part 5, which defines a set of domains within the aircraft.
Please note that the domain does not define a security level for the data itself, but indicates from which security level the information originated.

**v1/aircraft**
according to the A664P5 aircraft control domain.

_Example:_ An aircraft data recorder can publish flight deck data, and the cargo loading system or the cabin management system can communicate its status to this domain.

**v1/airline**
according to the A664P5 airline information services domain.

_Example:_ A container load, a galley insert sensor, passenger seats or cabin attendant seats can publish operational data to this domain.
The on-board airline application publishes the latest passenger list (received from ground) to this domain.

**v1/passenger**
according to the A664P5 passenger information and entertainment services domain.

_Example:_ The passenger flight information center can inform about connecting flights, meal and entertainment options.
Passengers can also communicate meal orders via the in-seat screen in this domain.

**v1/periphery**
according to the A664P5 passenger owned devices domain, but also for additional assets that are not covered by the previous domains.

_Example:_ A passenger mobile device publishes a gaming request or seat actuation request. A portable ground maintenance device collects data, a temporary sensor publishes humidity measurements or an airport finger collects information. A portable cabin crew device publishes a change of the passenger list.

**v1/core**
for CSMIM-internal usage.

_Example:_ The registration service can be reached to adapt permissions according to topic claims, or a directory service announces a list of failure reporting devices.
