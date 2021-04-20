---
title: Libraries Overview
mathjax: true
toc: true
---

The Cryptimeleon cryptography libraries are a family of libraries tailored towards fast prototyping of cryptographic constructions.

In this document, we give a short overview of each library.

# Math

The [Math library](https://github.com/cryptimeleon/math) provides the mathematical foundation for the other Cryptimeleon libraries.
It provides basics such as mathematical groups, rings and fields, e.g. \\(\mathbb{Z}_n\\), as well as implementations of cryptographic pairings.

Furthermore, it contains a serialization framework which acts as an intermediary between the cryptographic scheme and the low-level Java serialization. 
This allows for easy serialization of mathematical objects such as group elements.

Also noteworthy is the implementation of multi-exponentiation algorithms to allow for fast evaluation of multi-exponentiations.
To support better benchmarking, the math library allows for counting group operations via a special pairing group.

## Features

### Groups

Math offers the following algebraic groups:

* Bilinear groups:
    * Type 1 and type 3 pairings. For more details on this see [here]({% link docs/bilinear-groups.md %})
* Elliptic curves without pairings:
    * `Secp256k1`
* Permutation group \\(S_n\\)
* Cartesian product group

### Rings

Math offers the following algebraic rings and fields:

* Boolean ring
* Cartesian product ring
* Field extension class for polynomials of the form \\(x^d + c\\)
* Integer ring
* Polynomial ring
* \\(\mathbb{Z}_n\\) and \\(\mathbb{Z}_p\\) for prime \\(p\\)

### (Multi-)Exponentiation Algorithms

To speed up group operations, Math contains interleaved sliding window and interleaved WNAF (multi-)exponentiation algorithm implementations.

### Lazy Evaluation

The lazy evaluation feature allows deferred evaluation of group operations with the purpose of allowing for smart multi-exponentiation algorithm usage.
See [here]({% link docs/lazy-eval.md %}) for more information on this.

### Serialization

The representation framework contained in the Math library acts as an intermediate step between the actual Java objects and the Java serialization.
It aims to simplify serialization for the user.
For more information see [here]({% link docs/representations.md %}).

### Hashing

Math implements the SHA256 and SHA512 hash functions and offers annotations useful for enabling hashability of any Math structure.

### Random Number Generation

Math implements a random generator based on Java's `java.security.SecureRandom` random number generator.

### Counting Group Operations

Math allows counting of group operations via the debug group.
See [here]({% link docs/benchmarking.md %}) for information on this topic.

### Expression Framework

WIP

# Craco

[Craco](https://github.com/cryptimeleon/craco) (CRyptogrAphic COnstructions) is a Java library providing implementations of various cryptographic primitives and low-level constructions. This includes primitives such as commitment schemes, signature schemes, and much more.

The goal of Craco is to provide common cryptographic schemes for usage in more high-level protocols as well as to offer facilities for improving the process of implementing more low-level schemes such as signature and encryption schemes.

## Features

### Implemented Schemes
The constructions provided are:

* **Accumulators**:
    * Nguyen's dynamic accumulator [Ngu05]
* **Commitment schemes**:
    * Pedersen's commitment scheme [Ped92]
* **Digital signature schemes**:
    * Pointcheval & Sanders' short randomizable signature scheme [PS16]
    * An extension of Boneh, Boyen and Shacham's signature scheme from [Eid15]
    * Pointcheval & Sanders' modified short randomizable signature scheme (with and without ROM) [PS18]
    * Hanser and Slamanig's structure-preserving signature scheme on equivalence classes [HS14]
* **Encryption schemes**:
    * ElGamal
    * Streaming AES Encryption using CBC and GCM modes of operation
* **Key encapsulation mechanisms (KEM)**: 
    * ElGamal
* **Secret sharing schemes**:
    * Shamir's secret sharing scheme [Sha79] and its tree extension

# Mclwrap

Mclwrap provides a wrapper around the BN-254 bilinear group implemented in the [MCL library](https://github.com/herumi/mcl). As the bilinear groups implemented in the Cryptimeleon Math library are not particulary efficient, use of this wrapper is recommended for proper benchmarks.
Specifically, the mclwrap implementation's group operations are roughly 100 times as fast as our own implementation.

# Predenc

The Predenc project contains various predicate encryption implementations such as attribute-based encryption or identity-based encryption.
Furthermore, it contains key encapsulation mechanisms based on predicate encryption schemes.

## Features

### Implemented Schemes

* **Encryption schemes**:
    * Attribute-based:
        * Waters' ciphertext-policy attribute-based encryption scheme [Wat11]
        * Goyal et al.'s key-policy attribute-based encryption scheme [GPSW06]
    * Identity-based:
        * Fuzzy identity-based encryption [SW05]
        * Identity based encryption from the Weil pairing [BF01]
* **Key encapsulation mechanisms (KEM)**: We implement several KEMs based on the encryption schemes implemented in this library. Predenc provides KEMs for [Wat11], [GPSW06] and [SW05].

# Groupsig

*Work in progress*

The Groupsig project aims to offer group signature implementations as well as interfaces and tests to speed up implementation of group signature schemes.

## Features

### Implemented Schemes
*Work in progress*

* Choi, Park and Yung's short traceable group signature [CPY06]

# CLARC

CLARC: Cryptographic Library for Anonymous Reputation and Credentials.
This library provides an anonymous credential system.
It was developed as part of the ReACt project group at Paderborn University.

Documentation can be found [here](https://cs.uni-paderborn.de/fileadmin/informatik/fg/cuk/Lehre/Veranstaltungen/WS2016/ReACt/ReACt_documentation.pdf).

# References

[BF01] Dan Boneh and Matt Franklin. "Identity-Based Encryption from the Weil Pairing". In: Advances in Cryptology — CRYPTO 2001. CRYPTO 2001. Ed. by Joe Kilian. Vol. 2139. Lecture Notes in Computer Science.  Springer, Berlin, Heidelberg, August 2001, pp. 213-229.

[CPY06] Seung Geol Choi and Kunsoo Park and Moti Yung. "Short Traceable Signatures Based on Bilinear Pairings". 
In: Advances in Information and Computer Security – IWSEC 2006. Springer Berlin Heidelberg, 2006, pp 88–103.

[GPSW06] Vipul Goyal, Omkant Pandey, Amit Sahai, and Brent Waters. "Attribute-based encryption for fine-grained access control of encrypted data". In: ACM Conference on Computer and Communications Security. ACM, 2006, pages 89–98.

[HS14] Christian Hanser and Daniel Slamanig. "Structure-Preserving Signatures on Equivalence Classes and Their Application to Anonymous Credentials." 
In: Advances in Cryptology – ASIACRYPT 2014. Springer Berlin Heidelberg, pp 491–511.

[Ngu05] Lan Nguyen. “Accumulators from Bilinear Pairings and Applications”. In: Topics
in Cryptology – CT-RSA 2005. Ed. by Alfred Menezes. Vol. 3376. Lecture Notes in
Computer Science. Springer, Heidelberg, February 2005, pp. 275–292.

[Ped92] Torben P. Pedersen. “Non-Interactive and Information-Theoretic Secure Verifiable
        Secret Sharing”. In: Advances in Cryptology – CRYPTO’91. Ed. by Joan Feigenbaum.
        Vol. 576. Lecture Notes in Computer Science. Springer, Heidelberg, August
        1992, pp. 129–140.

[PS16] David Pointcheval and Olivier Sanders. “Short Randomizable Signatures”. In: Topics
in Cryptology – CT-RSA 2016. Ed. by Kazue Sako. Vol. 9610. Lecture Notes in
Computer Science. Springer, Heidelberg, February 2016, pp. 111–126.

[PS18] David Pointcheval and Olivier Sanders. "Reassessing Security of Randomizable Signatures". In: Topic in Cryptology - CT-RSA 2018. Ed. by Nigel P. Smart. Springer International Publishing, 2018, pp 319-338.

[Sha79] Adi Shamir. “How to Share a Secret”. In: Communications of the Association for
Computing Machinery 22.11 (November 1979), pp. 612–613.

[Wat11] Brent Waters. Ciphertext-policy attribute-based encryption: An
expressive, efficient, and provably secure realization. In Public Key
Cryptography. Springer, 2011, pp. 53–70.