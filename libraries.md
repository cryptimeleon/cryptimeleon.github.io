---
title: Libraries Overview
---

# **upb.crypto** Library Family Overview

The **upb.crypto** cryptography libraries are a family of libraries tailored towards fast prototyping and benchmarking of cryptographic constructions.

In this document, we give a short overview of each library.

## **upb.crypto.math**

The **upb.crypto.math** library provides the mathematical foundation for the other **upb.crypto** libraries.
It provides basics such as mathematical groups, rings and fields, e.g. Zn, as well as implementations of cryptographic pairings.
Furthermore, it contains a serialization framework which acts as an intermediary between the cryptographic scheme and the low-level Java serialization. 
This allows for easy serialization of mathematical objects such as group elements.
Also noteworthy is the expression framework which provides automatic optimization of boolean and group expressions.
The framework implements multi-exponentiation algorithms to allow for fast evaluation of the expressions.

## **upb.crypto.craco**

Craco is an acronym for CRyptogrAphic COnstructions. 
It offers interfaces for implementing cryptographic schemes such as attribute-based encryption, signatures, and much more.
Aside from the interfaces used to implement new schemes, the library contains implementations of various existing constructions such as an implementation of the attribute-based encryption scheme from Waters [Wat11], the signature scheme from Pointcheval and Sanders [PS16], and many more.

## **upb.crypto.benchmark**

Once you have implemented a scheme, you would probably like to benchmark it. This library provides benchmarks for
different types of schemes.

## **upb.crypto.protocols**

This library provides implementations and interfaces for cryptographic protocols.
This includes sigma protocols such as Schnorr, and the Fiat-Shamir Transformation [FS87].

## **upb.crypto.clarc**

CLARC: Cryptographic Library for Anonymous Reputation and Credentials.
As the name suggests, this library provides an anonymous credential system.

## **upb.crypto.mclwrap**

Mclwrap provides a wrapper around the efficient BN264 pairing implemented in the [MCL library](https://github.com/herumi/mcl). As the pairings implemented in the **upb.crypto.math** library are not particulary efficient, use of this wrapper is recommended for proper benchmarks.

## References

[Wat11] Brent Waters. Ciphertext-policy attribute-based encryption: An
 expressive, efficient, and provably secure realization. In Public Key
 Cryptography, pages 53–70. Springer, 2011

[PS16] David Pointcheval and Olivier Sanders. 2016. Short Randomizable Signatures. In Proceedings of the RSA Conference on Topics in Cryptology - CT-RSA 2016 - Volume 9610. Springer-Verlag, Berlin, Heidelberg, 111–126. DOI:https://doi.org/10.1007/978-3-319-29485-8_7

[FS87] Amos Fiat and Adi Shamir. 1987. How To Prove Yourself: Practical Solutions to Identification and Signature Problems. In Advances in Cryptology — CRYPTO’ 86. Springer-Verlag, Berlin, Heidelberg, 186-194