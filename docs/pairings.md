---
title: Pairings
toc: true
mathjax: true
---

In this document, we discuss the pairings and bilinear groups implemented in the Math library.

# Bilinear Groups

The following bilinear groups are available in our libraries:

| Group  | Type  | Has Hash to G1?  | Has Hash to G2?   | Has Hash to GT?  | Security | Performance | Notes
|---|---|---|---|---|---|---|---|
| Barreto-Naehrig  |  3 | yes  | yes  | no  | 100, 128 | fast inversion, slow operation | |
| Mcl (BN-254) | 3 | yes | yes | no | 100 | fast | provided by mclwrap wrapper |
| Supersingular  | 1  | yes  | yes  | no  | 48 - 256 | fast inversion, slow operation |
| Counting Group  | any  | yes  | yes  | yes  | no security | very fast | insecure Zn pairing, allows counting |

## Detailed Speed Benchmarks

Additionally to the above rough performance guidelines, we provided more detailed benchmarks: