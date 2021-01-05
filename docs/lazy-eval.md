---
title: Lazy Evaluation
toc: true
---

To enable automatic use of multi-exponentiation algorithms, the upb.crypto.math library lazily evaluates group operations where relevant.
Lazy evaluation means that when you call, for example, `g.pow(x)`, the exponentiation represented by `pow()` will not immediately be executed.
Only once the result of the computation is actually needed will it be executed.

The way this functionality is realized in the class hierarchy is that a group implementation implements the `GroupImpl` interface. 
An instance of `GroupImpl` can then be wrapped in `LazyGroup` to enable lazy evaluation.
You can disable lazy evaluation by instead wrapping your desired `GroupImpl` in a `BasicGroup` instance which performs all operations naively.

## Affected Groups

Not all groups are affected as lazy evaluation only makes sense for groups where group operations are costly.
This is because in that case multi-exponentiation algorithms can potentially be used to speed up computation of larger terms compared to evaluating each group operation separately.

## Forcing Evaluation

There are a couple of ways you can force evaluation to be done.

Calling `compute()` on a `LazyGroupElement` instance will start the computation in a separate thread. 
This is a non-blocking operation.
You should use `compute()` whenever a term has been fully constructed as waiting any longer won't offer any additional benefits, and you might as well use your idle cores.

`computeSync()` is a blocking compute call, meaning that the current thread will block until computation is done.
`getRepresentation()`, `hashCode()`, and `equals()` will also force a blocking computation as they require the result of the computation to function correctly.
