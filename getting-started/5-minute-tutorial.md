---
title: 5-Minute Tutorial For Cryptimeleon Math
mathjax: true
toc: true
---

Cryptimeleon Math is a library supplying the mathematical basics for cryptography (usually elliptic curve/pairing-based).

To give you some insight into the library, let's implement the well-known Pedersen commitment scheme over an elliptic curve as an example. 

---
*Note:*
You can also check this page out in an interactive Jupyter notebook by clicking the badge below:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/cryptimeleon/cryptimeleon.github.io/gh-pages?filepath=getting-started%2F5-minute-tutorial.ipynb)

---


## Setup 🔨

Let's include the Math library and set up the secp256k1 elliptic curve group. 


```java
%maven org.cryptimeleon:math:1.0.0-SNAPSHOT
```


```java
import org.cryptimeleon.math.structures.groups.elliptic.nopairing.Secp256k1;
import org.cryptimeleon.math.structures.groups.lazy.LazyGroup;
import org.cryptimeleon.math.structures.groups.*;

Group group = new LazyGroup(new Secp256k1()); //LazyGroup evaluates group operations lazily (see later)
```

A `Group` plays the role of the set $$\mathbb{G}$$. It has a `size()` and a bunch of useful methods to instantiate its `GroupElement`s.


```java
var n = group.size();
System.out.println("group size() = " + n);
```

    group size() = 115792089237316195423570985008687907852837564279074904382605163141518161494337


Now let's set up the public parameters for the Pedersen commitment: two random group elements $$g,h\in\mathbb{G}$$.


```java
var g = group.getUniformlyRandomNonNeutral(); 
var h = group.getUniformlyRandomNonNeutral(); 
```

`g` and `h` are `GroupElement`s. Their most important methods are `op(...)` (for the group operation) and `pow(...)` (for exponentiation/scalar multiplication). 

### `GroupElement`s are lazy 😴
Let's look at the group elements:


```java
System.out.println(g);
System.out.println(h);
```

    LazyGroupElement{computationState=NOTHING}
    LazyGroupElement{computationState=NOTHING}


Most operations concerning group elements in Math are lazy, i.e. they are only evaluated when necessary (and we consider `toString()` not to be necessary but rather a debugging tool). This has a bunch of advantages that we'll get to later. When working with `g` and `h`, this doesn't really change anything - though their values are not yet known, you can pretend that they are (when they are needed, they will be computed transparently). 

### Precomputation 🔮
`g` and `h` are fixed and publicly known and we'll later compute lots of expressions of the form $$C = g^m\cdot h^r$$. To speed that up, we can invest some time and memory to do some precomputation _now_. 
Thankfully, this is very easy to do: 


```java
g.precomputePow();
h.precomputePow();
System.out.println("Precomputation done.");
```

    Precomputation done.


Future computations `g.pow(...)` and `h.pow(...)` will benefit from precomputation.

<small>_As a side-effect, the values of `g` and `h` have been explicitly computed and can now be printed by `println()` above. You can now see that they indeed look like elliptic curve points._</small> 

## Committing 😱

### Choosing a message 📝
Now let's commit to a message $$m$$. For Pedersen commitments, $$m$$ lives in $$\mathbb{Z}_n$$ (because exponents are to be interpreted modulo the group order $$n$$). We can get the appropriate $$\mathbb{Z}_n$$ object from the group:


```java
var zn = group.getZn();
```

Similar to how a `Group` is a structure that has `GroupElement`s, `zp` is a structure that contains `ZnElement`s. 

We can now instantiate our message $$m$$, which will be a `ZnElement`, in any of the following ways:


```java
var m = zn.valueOf(23).mul(42); //simply the number 23*42 (mod p)
System.out.println(m);
```

    966



```java
var m = zn.getUniformlyRandomElement(); //a random number in Zn
System.out.println(m);
```

    92630712224131646301456420918815700255881880605567842301690225585365649881467



```java
import org.cryptimeleon.math.structures.rings.zn.HashIntoZn;

var m = new HashIntoZn(zn).hash("We attack at midnight! ⚔️"); //the hash of the given String into Zn
System.out.println(m);
```

    357739458326128062426942553905997083565071573036229449938149284158791503092


### Computing the commitment 🎲

Now that we have $$m$$, let's compute the Pedersen commitment, which is
$$C = g^m\cdot h^r$$
for a random $$r\in\mathbb{Z}_n$$.


```java
var r = zn.getUniformlyRandomElement();
var C = g.pow(m).op(h.pow(r));
System.out.println(C);
```

    LazyGroupElement{computationState=NOTHING}


### On automatic multiexponentiation 🤖

One advantage of the `LazyGroup` approach is that after calling `g.pow(m)`, that value is not immediately computed. This allows us to compute $$C$$ as a multiexponentiation behind the scenes, i.e. more efficiently than computing $$g^m$$ and $$h^r$$ separately and then multiplying them.

This is done automatically when the value of $$C$$ is needed. We can force computation of $$C$$ by calling `computeSync()` for the sake of illustration.


```java
C.computeSync() //computes the value of C and blocks the caller until it's done.
```




    (56771449235264302615258677380344060394745101305888541425349080151044428825409,88883184015215676917695009465406684554267011012005634798071713139170389707278)



The committer can now transmit $$C$$ to the verifier, who won't learn anything from it ($$C$$ is uniformly random in $$\mathbb{G}$$) but will be assured that we cannot later change our mind about $$m$$.

For this transmission, we'd have to talk about serialization. Very roughly: every `GroupElement` is able to represent itself as a `Representation`, which is safe to send, and its corresponding `Group` is able to undo this process.


```java
C.getRepresentation()
```




    {"__type":"OBJ","x":"INT:7d838066de6a5e807c8b35b1c49513175e1db3d7cd053e2e81490c674b828341","y":"INT:c48219706b509d790941ffacf9891718502f96b17da35b91f5240bb5b3faca0e","z":"INT:1"}




```java
group.getElement(C.getRepresentation()).equals(C)
```




    true



For more information on serialization, see [our documentation regarding `Representation`s](https://cryptimeleon.github.io/docs/representations.html).

## Verifying the commitment 🕵️

When we've additionally given $$m,r$$ to the verifier, they can now check whether $$m,r$$ is a valid opening for $$C$$ by checking the following equation:


```java
g.pow(m).op(h.pow(r)).equals(C)
```




    true



Note that here, $$g^m\cdot h^r$$ is also automatically computed as multiexponentiation.

... and that's already it for implementing the Pedersen commitment scheme.

## Bonus: Parallelizing 🦑

Another advantage of the `LazyGroup` approach is that it makes group computations easily parallelizable. Consider the following code snippet where we'll compute a whole bunch of commitments:


```java
List<GroupElement> commitments = new ArrayList<>();

for (int i=0;i<500;i++) {
    var commitment = g.pow(i).op(h.pow(zn.getUniformlyRandomElement())).compute();
        //compute() returns immediately but starts computing the concrete value on a background thread.
    commitments.add(commitment); //what we add to the list here could technically be compared to a Future<GroupElement>
}
```

As a result, the code above doesn't really run a any group computations itself and hence returns very quickly. 
All the commitments will be computed on other threads concurrently in the background, utilizing all your CPU cores. 

You can go on working with all the commitments as you wish (no need to consider whether they're done computing yet). Calls that require the result of the internal computations above may block until the result is there. 

Conceptually, calling `compute()` or `computeSync()` doesn't have any effect semantically, so for the sake of writing _correct_ code, you'll never have to use them (semantically they are `return this;` operations). But if you want to write _fast_ code, calling `compute()` on some values may enable concurrency and speed things up.

# ... what's next? 🎉

If you're still curious about the library, consider our 15 minute tutorial where we go through some advanced examples for the library.
