---
title: How do I ...?
mathjax: true
toc: true
---

This page addresses a bunch of questions of the form "how do I do xyz in Cryptimeleon?".
Consider it Stack-Overflow-style help.

# How do I do group operations and pairings?


# How do I hash into \\(\mathbb{Z}_n\\)?
You can use `HashIntoZn` for this.
```java
BigInteger n = BigInteger.valueOf(99991); //just for the sake of example
HashIntoZn hashFunction = new HashIntoZn(n);
Zn.ZnElement hashVal = hashFunction.hash("Preimage");
```

# How do I hash into a group \\(\mathbb{G}\\)?
Bilinear groups provide hash functions as follows:
```java
GroupElement hashValue = bilinearGroup.getHashIntoG1().hash("Preimage");
```

For other groups, there may be classes like named like `HashIntoSecp256k1`.

# How do I hash a list of group elements?


# How do I send or store a group element?


# My benchmark produces implausibly good numbers
