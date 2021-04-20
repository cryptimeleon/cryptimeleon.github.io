---
title: Bilinear Groups
toc: true
mathjax: true
---

In this document, we discuss the bilinear groups implemented in the Math library.

Recall that a bilinear group consists of three groups \\(\mathbb{G}_1\\), \\(\mathbb{G}_1\\) and \\(\mathbb{G}_T\\) as well as a bilinear pairing function \\(e\\).

To decide which bilinear group to use, you will need to know the desired type, to which of the groups you need to be able to hash, and the required security parameter. Furthermore, performance is also a concern.

# Bilinear Groups

The following bilinear groups are available in our libraries:

| Group  | [Type](#types)  | Has Hash to \\(\mathbb{G}_1\\)?  | Has Hash to \\(\mathbb{G}_2\\)?   | Has Hash to \\(\mathbb{G}_T\\)?  | Security | Library | Class Name |
|---|---|---|---|---|---|---|---|---|
| Barreto-Naehrig  |  3 | yes  | yes  | no  | 100, 128 | [Math](https://github.com/cryptimeleon/math) | `BarretoNaehrigBilinearGroup` |
| Mcl (BN-254) | 3 | yes | yes | no | 100 | [Mclwrap](https://github.com/cryptimeleon/mclwrap) | `MclBilinearGroup` |
| Supersingular  | 1  | yes  | yes  | no  | 48 - 256 | [Math](https://github.com/cryptimeleon/math) | `SupersingularBilinearGroup` |
| Debug Group  | any  | yes  | yes  | yes  | no security | [Math](https://github.com/cryptimeleon/math) | `DebugBilinearGroup` |

The security is given as the negated logarithm base 2 of the adversaries attacking chance, i.e. a security parameter of 100 means the adversary has no more than a \\(2^{-100}\\) chance of breaking security. Security parameter estimations are determined based on numbers from [BD19].

The "Has Hash to \\(\mathbb{G}_X\\)?" column tells you whether the implementation offers a hash function from byte arrays to the corresponding group \\(\mathbb{G}_X\\).

## Performance

The bilinear groups we implement are very slow when it comes to computing group operations and the pairing itself. This includes our Barreto-Naehrig and supersingular implementations. If you are looking for better performance, you should use [Mclwrap](https://github.com/cryptimeleon/mclwrap) (for type 3). For types other than 3 we do not currently offer an efficient implementation or wrapper.

## Debug Group

The debug group fulfills two main purposes: tests, and counting benchmarks.
It is based on an insecure \\(\mathbb{Z}_n\\) pairing which makes it very fast.
Therefore it is well suited for use in your tests as they will execute much faster than with a secure bilinear group.
Just replace the existing groups with their debug counterparts when running any tests.

It also has group operation and pairing counting capabilities built in. For more information see the [benchmarking page]({% link docs/benchmarking.md %}) 

## Types

In the Math library, we differentiate between three types:

- **Type 1**: \\(\mathbb{G}_1 = \mathbb{G}_2\\)
- **Type 2**: \\(\mathbb{G}_1 \ne \mathbb{G}_2\\) and there exists an efficiently computable homomorphism \\(\mathbb{G}_2 \rightarrow \mathbb{G}_1\\)
- **Type 3**: \\(\mathbb{G}_1 \ne \mathbb{G}_2\\) and there exists no efficiently computable homomorphism \\(\mathbb{G}_2 \rightarrow \mathbb{G}_1\\)


# References

[BD19] Barbulescu, R., Duquesne, S. Updating Key Size Estimations for Pairings. J Cryptol 32, 1298–1336 (2019). https://doi.org/10.1007/s00145-018-9280-5