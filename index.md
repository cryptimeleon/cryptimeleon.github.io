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
  - Same abstraction as in conference papers. We're taking care of point-on-curve and subgroup checks.
- [Benchmark](docs/benchmarking.html) your construction (in milliseconds or count group operations)
  - Put convincing numbers into your paper.
  - Android support - benchmark modern crypto on a phone.
- Implement Schnorr-style zero-knowledge proofs.
  - Specify them using Camenisch-Stadler notation in [subzero](https://cptml.org/subzero) to generate code.
  - Supports AND/OR composition, range proofs, pairing support, Fiat-Shamir, etc.
- Use the basics you may expect: hash into groups or \\(\mathbb{Z}_p\\), use pseudorandom function and random oracles with arbitrary input/output length, ...
- No copyright issues: Open-source under Apache 2.0 license.

## ❌ What Cryptimeleon does _not_ offer

- Do *not* use Cryptimeleon for production code. It is a research tool only and may not offer the security level required in real applications.
- Do *not* use Cryptimeleon if you want to implement absurd levels of performance optimization.
  - We focus more on easy-to-read APIs than performance.
  - That said, benchmarks with Cryptimeleon are definitely competitive and we do automatically optimize some things in the background.

## Getting started
- 🙋 To read more, consider our paper [to be published].
- 🧑‍💻 To see example code, read the [5 minute tutorial](/getting-started/5-minute-tutorial.html) or generate a Sigma protocol with [subzero](https://cptml.org/subzero).
- 👷 To build your own application with Cryptimeleon, [import our projects](/getting-started/first-steps.html) via Maven or gradle. Check out our ["how do I ..."](/docs/how-do-I.html) page if you're stuck.
- 🧙 For everything else, consult this documentation page, follow our [Twitter](https://twitter.com/cryptimeleon), find the code on [GitHub](https://github.com/cryptimeleon), or [contact us](mailto:contactus@cryptimeleon.org).


## Publication
We have a paper on Cryptimeleon and its features published on [eprint](https://eprint.iacr.org/2021/961). The paper also highlights the benefits that Cryptimeleon provides for privacy-preserving cryptography researchers .

### How to cite
```
@article{EPRINT:BEHF21,
  author    = {Jan Bobolz and
               Fabian Eidens and
               Raphael Heitjohann and
               Jeremy Fell},
  title     = {Cryptimeleon: A Library for Fast Prototyping of Privacy-Preserving Cryptographic Schemes},
  journal   = { {IACR} Cryptol. ePrint Arch.},
  volume    = {2021},
  pages     = {961},
  year      = {2021},
  url       = {https://eprint.iacr.org/2021/961},
}
```


🏫 Cryptimeleon has been developed at Paderborn University (Germany) in the [Codes and Cryptography group](https://cs.uni-paderborn.de/en/cuk).
