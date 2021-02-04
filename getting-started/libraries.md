---
title: Libraries Overview
mathjax: true
---

The upb.crypto cryptography libraries are a family of libraries tailored towards fast prototyping of cryptographic constructions.

In this document, we give a short overview of each library.

# upb.crypto.math

The upb.crypto.math library provides the mathematical foundation for the other upb.crypto libraries.
It provides basics such as mathematical groups, rings and fields, e.g. \\(\mathbb{Z}_n\\), as well as implementations of cryptographic pairings.
Furthermore, it contains a serialization framework which acts as an intermediary between the cryptographic scheme and the low-level Java serialization. 
This allows for easy serialization of mathematical objects such as group elements.
Also noteworthy is the implementation of multi-exponentiation algorithms to allow for fast evaluation of multi-exponentiations.
To support better benchmarking, the math library allows for counting group operations via a special pairing group.

# upb.crypto.craco

Craco is an acronym for CRyptogrAphic COnstructions. 
It offers interfaces for implementing cryptographic schemes such as attribute-based encryption, signatures, and much more.
Aside from the interfaces used to implement new schemes, the library contains implementations of various existing constructions such as an implementation of the attribute-based encryption scheme from Waters [Wat11] and the signature scheme from Pointcheval and Sanders [PS16].

# upb.crypto.protocols

This library provides implementations and interfaces for cryptographic protocols.
This includes sigma protocols such as Schnorr, and the Fiat-Shamir Transformation [FS87].

# upb.crypto.mclwrap

Mclwrap provides a wrapper around the BN-254 bilinear group implemented in the [MCL library](https://github.com/herumi/mcl). As the bilinear groups implemented in the upb.crypto.math library are not particulary efficient, use of this wrapper is recommended for proper benchmarks.
Specifically, the mclwrap implementation's group operations are roughly 100 times as fast as our own implementation.

# upb.crypto.benchmark

Here, we store benchmarks for the implemented schemes.
The benchmarks are generally done via the [JMH micro-benchmarking library](https://github.com/openjdk/jmh).

# upb.crypto.clarc

CLARC: Cryptographic Library for Anonymous Reputation and Credentials.
This library provides an anonymous credential system.
It was developed as part of the ReACt project group at Paderborn University.

Documentation can be found [here](https://cs.uni-paderborn.de/fileadmin/informatik/fg/cuk/Lehre/Veranstaltungen/WS2016/ReACt/ReACt_documentation.pdf).

# References

[Wat11] Brent Waters. Ciphertext-policy attribute-based encryption: An
 expressive, efficient, and provably secure realization. In Public Key
 Cryptography, pages 53–70. Springer, 2011

[PS16] David Pointcheval and Olivier Sanders. 2016. Short Randomizable Signatures. In Proceedings of the RSA Conference on Topics in Cryptology - CT-RSA 2016 - Volume 9610. Springer-Verlag, Berlin, Heidelberg, 111–126. DOI:https://doi.org/10.1007/978-3-319-29485-8_7

[FS87] Amos Fiat and Adi Shamir. 1987. How To Prove Yourself: Practical Solutions to Identification and Signature Problems. In Advances in Cryptology — CRYPTO’ 86. Springer-Verlag, Berlin, Heidelberg, 186-194