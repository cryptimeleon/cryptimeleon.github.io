---
mathjax: true
---

# Cryptimeleon - prototyping for advanced privacy-preserving constructions


Cryptimeleon (pronounced /krɪptimiːliən/, "cryp-tee-meleon") is an open-source Java library primarily aimed at cryptography researchers. 

> You want to prototype and benchmark your new kind of anonymous credentials, group signatures, attribute-based encryption, or other construction in the bilinear group setting? 
> 
> Try Cryptimeleon!

## ✅ What Cryptimeleon offers
Cryptimeleon supports the following features (plus others):
- Write equations in our simple algebraic ([bilinear groups](docs/bilinear-groups.html)) framework.
  - Easily readable, e.g., `g.pow(m).op(h.pow(r))`.
  - Easy parallelism and precomputation. Transparent multiexponentiation.
- [Benchmark](docs/benchmarking.html) your construction (in milliseconds or count group operations) and put convincing numbers into your paper
  - Android support - run modern crypto on a phone.
- Implement Schnorr-style zero-knowledge proofs.
  - Specify them using Camenisch-Stadler notation in [subzero](https://cptml.org/subzero) to generate code.
  - Supports AND/OR composition, range proofs, pairing support, Fiat-Shamir, etc.
- Use the basics you may expect: hash into groups or \\(\mathbb{Z}_p\\), use pseudorandom functions with arbitrary input/output length, ...

## ❌ What Cryptimeleon does _not_ offer

- Do *not* use Cryptimeleon for production code. It is a research tool only and may not offer the security level required in real applications.
- Do *not* use Cryptimeleon if you want to implement absurd levels of performance optimization.
  - We focus more on easy-to-read APIs than performance. 
  - That said, benchmarks with Cryptimeleon are definitely competitive and we do automatically optimize some things in the background.

## Getting started
- 🙋 To read more, consider our paper [to be published].
- 🧑‍💻 To see example code, read the [5 minute tutorial](/getting-started/5-minute-tutorial.html) or generate a Sigma protocol with [subzero](https://cptml.org/subzero).
- 👷 To build your own application with Cryptimeleon, [install](/getting-started/installation.html) it via Maven or Gradle.
- 🧙 For everything else, consult this documentation page, follow our [Twitter](https://twitter.com/cryptimeleon), find the code on [GitHub](https://github.com/cryptimeleon), or [contact us](mailto:contactus@cryptimeleon.org).


🏫 Cryptimeleon has been developed at Paderborn University (Germany) in the [Codes and Cryptography group](https://cs.uni-paderborn.de/en/cuk).
