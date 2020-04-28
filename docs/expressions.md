---
title: The Expression System
mathjax: true
toc: true
---

The expression system of the math library offers a way to do group and boolean algebra with the goal of allowing for optimizations such as the use of multi-exponentiation algorithms or rewriting algebraic terms to be more efficiently computable.

Expressions differ from the usual use of functions such as `pow()` or `op()` in that the result is not calculated immediately. Instead, an expression tree is built up which, when evaluated, will compute the result of the expression. This has several advantages:

* The whole expression is evaluated as a single entity. This allows for automatic detection of multi-exponentiations which enables the use of efficient multi-exponentiation algorithms. These can greatly improve performance compared to performing every exponentiation on its own.
* The expression can be precomputed. Since it may contain variables whose value may not be known at that point in time, this precomputation can optimize the expression to allow for more efficient evaluation later, e.g. by caching powers for exponentiation algorithms.

In this document we show how expressions work and what kind of optimizations are supported.

# Group Expressions
To showcase group expressions, we want to use them to implement a concrete cryptographic scheme. We have chosen
Pointcheval and Sanders multi-message signature scheme from [PS16](Section 4.2) for this. It is available in the **upb.crypto.craco** library already.

We start with the verification algorithm:
```java
    // Given signature sigma = (sigma1, sigma2), message m = (m_0, ..., m_{r-1}), and public key pk, public parameters pp
    // and message length r
    if (sigma1.isNeutralElement())
        return false;

    // construct left side of equality check: e(sigma_1, \tilde{X} \cdot \prod{\tilde{Y}_j^{m_j}}
    GroupElementExpression leftSideG2 = pp.getBilinearMap().getG2().expr(); // neutral element of G2
    leftSideG2 = leftSideG2.op(pk.getTildeX());
    for (int j = 0; j < r; ++I) {
        // equivalent to leftSideG2 = leftSideG2.op(pk.getTildeYi()[j].pow(m_j));
        leftSideG2 = leftSideG2.opPow(pk.getTildeYi()[j], m[j]);
    }
    GroupElementExpression leftSide = pp.getBilinearMap().expr(sigma1, leftSideG2);

    // construct right side of equality check: e(sigma2, \tilde{g})
    GroupElementExpression rightSide = pp.getBilinearMap().expr(sigma2, pk.getTildeG());
    
    return leftSide.evaluate().equals(rightSide.evaluate());
```
As you can see, only when we return the result of the two pairings are actually evaluated through the `evaluate()` call. Before that, the expression tree is built. It is barely more complex than directly computing each intermediary result. You simply need to call `expr()` on a group element to get it as a group expression and can then use all the usual methods such as `pow` or `op()` on it. There are even methods for usual combinations of operations such as `opPow()`. Calling `expr()` on a group itself will create an expression denoting the neutral element of that group.

Now, why are expressions useful here? As you can see in the code above, the for loop implements a multi-exponentiation. Without expressions, each exponentiation would be done as a single exponentiation. The expression evaluator, however, is able to automatically identify the multi-exponentiation and use an efficient multi-exponentiation algorithm to compute it. The evaluator chooses the specific algorithm to use depending on the number of different bases in the multi-exponentiation and cost of inversion in the group. 

We do not have to stop here, however. All implemented multi-exponentiation algorithms can make use of precomputed odd powers or power products (depending on the algorithm) of the bases within. We already know these bases during key generation, so it makes sense to do this precomputation there as verification will likely be executed more often than key generation.

The resulting key generation function may look as follows:
```java
    // given public parameter pp and message length r
    Group group2 = pp.getBilinearMap().getG2();
    Zp zp = new Zp(pp.getBilinearMap().getG1().size());
    GroupElement group2ElementTildeG = group2.getUniformlyRandomNonNeutral(); // \tilde{g} in paper
    ZpElement exponentX = zp.getUniformlyRandomNonNeutral(); // x in paper
    ZpElement[] exponentsYi = IntStream.range(0, r).mapToObj(a -> zp.getUniformlyRandomElement())
                .toArray(ZpElement[]::new); // r random elements from \mathbb{Z}_p, y_i in paper
    GroupElement group2ElementX = group2ElementTildeG.pow(exponentX); // \tilde{X} in paper
    // \tilde{Y_i} in paper
    GroupElement[] group2ElementsYi = 
                Arrays.stream(exponentsYi).map(group2ElementTildeG::pow).toArray(GroupElement[]::new);
  
    // Construct secret key
    PSSigningKey sk = new PSSigningKey(exponentX, exponentsYi);

    // Precompute odd powers/power products for multi-exponentiation
    leftSideG2 = leftSideG2.op(pk.getTildeX());
    for (int j = 0; j < r; ++I) {
        leftSideG2 = leftSideG2.opPow(pk.getTildeYi()[j], new ExponentVariableExpr("m_j");
    }
    leftSideG2.precompute();
    
    // Construct public key
    PSVerificationKey pk = new PSVerificationKey(group2ElementTildeG, group2ElementX, group2ElementsYi);
    
    return new SignatureKeyPair<>(pk, sk);
```
As you can see, the variables in the exponents of the multi-exponentiation are represented by a different type of expression, the exponent expression. Exponent expressions are not particularly interesting as computation is done in an integer ring which is very efficient already and does not need specific optimization as group algebra does (e.g. multi-exponentiations).

The `precompute()` call on `leftSideG2` will recognize the multiexponentiation and precompute odd powers/power products which are used by the `evaluate` call during verification. However, this is not the only thing it does. It also returns a new expression (which we ignore in the code above) which is additionally optimized by:

* Rewriting the expression tree to be more efficiently computable, e.g. move pairing exponents into the pairing since exponentiation in the source groups is usually more efficient. If you want to use this, you will of course need to supply the precomputed expression to the methods that need it, in this case the verification method.
* Evaluating as much of the expression as possible already. This could even mean completely evaluating the expression if the expression contains no variables.

## Variable Substitution using Value Bundles

Lets assume we have placed the precomputed expression in the public key and want to use it in the verification method. It contains variables in the exponents, so we will need to substitute those by the actual values before
evaluation. There exists a class that makes this very simple, the `ValueBundle` class. It allows associating variable names with values. Giving such a value bundle and an expression containing variables, we can easily obtain a new expression where the variables have been replaced by their values from the value bundle. Let's see how this is done in the verification method we showed previously:

```java
    // Given signature sigma = (sigma1, sigma2), message m = (m_0, ..., m_{r-1}), and public key pk, public parameters pp
    // and message length r. The public key contains our precomputed expression `leftSideG2Expr`
    if (sigma1.isNeutralElement())
        return false;

    // construct left side of equality check: e(sigma_1, \tilde{X} \cdot \prod{\tilde{Y}_j^{m_j}}
    ValueBundle valueBundle = new ValueBundle();
    for (int j = 0; j < r; ++j) {
        valueBundle.put("m_" + j, m[j]); // store messages in value bundle
    }
    GroupElementExpression leftSideG2 = pk.getLeftSideG2Expr().substitute(valueBundle); // substitute variables with values
    GroupElementExpression leftSide = pp.getBilinearMap().expr(sigma1, leftSideG2);

    // construct right side of equality check: e(sigma2, \tilde{g})
    GroupElementExpression rightSide = pp.getBilinearMap().expr(sigma2, pk.getTildeG());
    
    return leftSide.evaluate().equals(rightSide.evaluate());
```

In this case, using the precomputed expression is not useful as there are no opportunities for rewriting or preevaluation. An expression may be more easily understandable if it is written in a way that is not necessarily optimal for evaluation, however, in which case precomputation helps to still enable efficient evaluation.

# Boolean Expressions

Boolean expressions are similar to group or exponent expressions, just for boolean formulas. They support the usual boolean operations such as AND, OR and NOT, as well as some special equality expressions.

## Group Equality Expressions

In our implementation of the verification algorithm from [PS16], we used two `evaluate()` calls to evaluate both sides of the equality check. We can replace this by a `GroupEqualityExpr`:

```java
    // previously: return leftSide.evaluate().equals(rightSide.evaluate());
    // now:
    return new GroupEqualityExpr(leftSide, rightSide).evaluate();
```
This expression basically does the same thing as we did before; when evaluated, it evaluates both sides and compares them for equality. However, being an expression that is only evaluated when ``evaluate()`` is called, it can be precomputed and rewritten. Specifically, one can move the right side of the equality over to the left side, resulting in the equality \\(x \cdot y_{-1} = 1\\),
where \\(x\\) denotes the left side of the original equality and \\(y\\) the right side.

This is beneficial as it allows for the use of a multi-exponentiation algorithm to evaluate the left side of the equality. It can be done automatically using the ``precompute()`` method of the `BooleanExpression` class.

## Probabilistic AND Merging

Many cryptographic constructions, e.g. verification algorithms of SNARGs in the CRS model, make use of multiple equality checks to compare the results of pairing evaluations for equality. There is an optimization that can be done for these which we call "Probabilistic AND Merging". This requires multiple group equality expressions combined with Boolean ANDs and merges them into a single group equality expression with one multi-exponentiation.
This optimization is probabilistic as it is not guaranteed to work; hence, it is disabled by default when evaluating Boolean expressions.

We describe how this would work for \\(x_1 = 1 \wedge x_2 = 1\\).
Two random exponents are chosen, we call them \\(a_1\\) and \\(a_2\\). The new
expression is then \\(x_1^{a_1} \cdot x_2^{a_2} = 1\\).
If we are unlucky when choosing the exponents, this equality may be true even if the original equalities are not all true, but it can improve efficiency noticably if there are many equalities.

# Configuring the Expression Evaluator

The `OptGroupElementExpressionEvaluator` class is responsible for evaluating expressions when the `evaluate()` function is used (except for expressions over the group `LazyGroup`) and for precomputing when `precompute()` is used.

There are many ascepts of evaluation and precomputation that can be configured to your exact needs. The configuration of the evaluator is stored as an instance of the `OptGroupElementExpressionEvaluatorConfig` class inside the evaluator and can be retrieved using the `getConfig()` method. The config's setter and setter methods can then be used to change the config and with that the behaviour of the evaluator. The setters are generally named `setX`, where `X` is the name of the attribute to set, and the getters are either named `isX` or `getX`, depending on whether the attribute is a Boolean or not.

## Configuring the Multi-exponentiation Algorithms

The `OptGroupElementExpressionEvaluator` offers three different multi-exponentiation algorithms which are used automatically depending on the multi-exponentiation. These are an interleaved sliding algorithm, an interleaved WNAF algorithm, and a simultaneous algorithm. By setting the `forcedMultiExpAlgorithm` attribute you can force the evaluator to use a specific algorithm if you don't like the choice it makes for you.

By default, caching of odd powers (for the interleaved algorithms) and power products (for the simultaneous algorithm) is turned on. However, this can potentially reduce performance if you do not use the cached powers. This can happen if a base is only used in a single exponentiation. In that case you can either disable caching for each algorithm type individually by setting the `enableCachingInterleavedSliding`, `enableCachingInterleavedWnaf` and/or `enableCachingSimultaneous` attributes, or disable caching for all algorithms using the `enableCachingAllAlgs` attribute.
Even if you are not familiar with multi-exponentiation algorithms or even regular window-based single exponentiation algorithms, benchmarking your scheme with caching enabled and disabled can make a noticable difference in runtime.

```java
// let `expr` be some expression we want to evaluator without caching
OptGroupElementExpressionEvaluator evaluator = new OptGroupElementExpressionEvaluator();
evaluator.getConfig().setEnableCachingAllAlgs(false); // disable caching for this evaluator
expr.evaluate(evaluator); // evaluate with our configured evaluator
```

Furthermore, you can set the window size used for each algorithm depending on whether caching is turned on or not. For example, setting the window size of the interleaved sliding algorithm with caching enabled using the `windowSizeInterleavedSlidingCaching` attribute. Only use this if you are sure your computer can handle it, however, as increasing window size too much increases memory usage exponentially.

Once a multi-exponentiation contains too many bases, the simultaneous algorithm is not used anymore, instead an interleaved variant is used. This cutoff is set by the `simultaneousNumBasesCutoff` attribute. By default, it is set to `0` bases (0 means it is disabled currently, as interleaved sliding is actually faster). Above this threshold, the interleaved variants are used.
To decide whether to use the interleaved sliding or WNAF variant, the evaluator uses the `useWnafConstInversion` attribute. This is set to `0` by default, which means that if 100 inversions in the group cost as much as 0 group operations, the WNAF variant can be used (0 means it is disabled currently, as interleaved sliding is actually faster). A value of `50` would mean that inversions cost half as much as group operations.

## Configuring the Group Precomputation Phase

The `OptGroupElementExpressionEvaluator` does several things in its `precompute()` method for group expressions. First, it rewrites the expression to be more efficiently evaluatable. This phase can be disabled using the `enablePrecomputeRewriting` attribute. Then it evaluates as much of the expression as possible already, controlled by the `enablePrecomputeEvaluation` attribute. Lastly, it performs caching for the later application of a multi-exponentiation algorithm which can be disabled using the `enablePrecomputeCaching` attribute.

## Configuring the Boolean Precomputation Phase

In addition to precomputing group expressions, the evaluator also can precompute Boolean expressions. The exact optimizations that can be done are described [here](https://github.com/upbcuk/upb.crypto.math/wiki/Expressions#boolean-expressions). The rewriting can be disabled using `enablePrecomputeRewriting`, the Probabilistic AND Merging is controlled separately through the `enableProbabilisticAndMerging` attribute, it is disabled by default.

## A Note Regarding Efficient Caching
The standard way cached group elements are stored is via a hash map that maps the base to a list of cached powers for that base. This has the advantage that different `GroupElement` objects which represent the same underlying group element can always be mapped to their cached powers without having to always use the same `GroupElement` object. The disadvantage is that the computation of the hash code is computationally expensive and can, assuming you are using the efficient Mcl groups provided via *upb.crypto.mclwrap* take around 10% of the overall multi-exponentiation runtime. 

To fix this, the library also stores cached powers in the `GroupElement` objects themselves (as long as the implementing class extends `AbstractGroupElement`). This way, accessing the hash map can be avoided and with that the hash code computation. However, for this to work you need to reuse the same `GroupElement` object in your expressions.

# References

[PS16] David Pointcheval and Olivier Sanders. Short Randomizable Signatures. In Kazue Sako, editor, *Topics in Cryptology - CT-RSA 2016*, pages 111-126. Springer International Publishing, 2016.
