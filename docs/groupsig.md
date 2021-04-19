---
title: Group Signatures
toc: true
mathjax: true
---

## The Groupsig Project

Groupsig project offers interfaces and with that a structure to base new group signature implementations on.
These interfaces are based on [JonArrDia15] and meant to be flexible, i.e. enable implementation of different kinds of group signature schemes.
The project also provides generic tests for group signatures that use those existing interfaces.
Groupsig project builds on other Cryptimeleon libraries, Math for mathematical fundamentals and Craco for cryptographic building blocks and protocol facilities.
Very relevant here is the Schnorr protocol implementation in Craco that allows for quick implementation of PoK, such as the one used in the issue/join protocol in [CPY06].

## Interface Overview

Interfaces are found in the `org.cryptimeleon.groupsig.common` package.
Main point of interest is the `GroupSignatureScheme` interface.
It contains all of the group signature algorithms, except the setup algorithm.
The setup algorithm can be put where the user wants.
The [CPY06] implementation delegates setup to another class and then uses the generated public parameters to instantiate the `GroupSignatureScheme` object.

### Data Classes

The other interfaces are mostly for data modelling.
`GroupMembershipList` contains information about each group member in the form of `GMLEntry` instances. Entry usually generated when issuing protocol is done.
`RevocationList` contains information about the group members that had their membership revoked in the form of `RevocationListEntry` instances.

### Issuing Protocols

Usually, the issue/join protocol is interactive.
Craco and groupsig already offers facilities for implementing protocols.
The `IssuingProtocol` interface is used to instantiate `IssuingProtocolInstance` instances.
The joining member uses it to instantiate a user instance and the issuer uses it to instatiate an issuer instance.
In the case of the [CPY06] implementation, these are implemented the `CPY06IssuingProtocolIssuerInstance` and `CPY06IssuingProtocolUserInstance` classes.
The `nextMessage` method of `IssuingProtocolInstance` takes in the received message, and returns the message to respond with.
This is independent of how the messages are sent between member and issuer.
That can be implemented as desired.

[CPY06], in its join/issue protocol, also makes use of a Proof of Knowledge.
Craco provides Schnorr Proof of Knowledge classes which can be used to easily implement such a Proof of Knowledge. 
How to use those is covered in the [Protocols tutorial].

