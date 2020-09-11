---
title: 5-minute tutorial
mathjax: true
tpc: true
---

# 5-minute-tutorial: `upb.crypto.math`

`upb.crypto.math` is a library supplying the mathematical basics for cryptography (usually elliptic curve/pairing-based).

To give you some insight into the library, let's implement the well-known Pedersen commitment scheme over an elliptic curve as an example. 

## Setup 🔨

Let's include the upb.crypto.math library and set up the secp256k1 elliptic curve group. 


```Java
%maven de.upb.crypto:math:2.0.0-SNAPSHOT
```


```Java
import de.upb.crypto.math.elliptic.Secp256k1;
import de.upb.crypto.math.structures.groups.lazy.LazyGroup;
import de.upb.crypto.math.interfaces.structures.*;

Group group = new LazyGroup(new Secp256k1()); //LazyGroup evaluates group operations lazily (see later)
```

A `Group` plays the role of the set $\mathbb{G}$. It has a `size()` and a bunch of useful methods to instantiate its `GroupElement`s.


```Java
var n = group.size();
System.out.println("group size() = " + n);
```

    group size() = 115792089237316195423570985008687907852837564279074904382605163141518161494337


Now let's set up the public parameters for the Pedersen commitment: two random group elements $g,h\in\mathbb{G}$.


```Java
var g = group.getUniformlyRandomNonNeutral(); 
var h = group.getUniformlyRandomNonNeutral(); 
```

`g` and `h` are `GroupElement`s. Their most important methods are `op(...)` (for the group operation) and `pow(...)` (for exponentiation/scalar multiplication). 

### `GroupElement`s are lazy 😴
Let's look at the group elements:


```Java
System.out.println(g);
System.out.println(h);
```

    LazyGroupElement{computationState=NOTHING}
    LazyGroupElement{computationState=NOTHING}


Most operations concerning group elements in upb.crypto are lazy, i.e. they are only evaluated when necessary (and we consider `toString()` not to be necessary but rather a debugging tool). This has a bunch of advantages that we'll get to later. When working with `g` and `h`, this doesn't really change anything - though their values are not yet known, you can pretend that they are (when they are needed, they will be computed transparently). 

### Precomputation 🔮
`g` and `h` are fixed and publicly known and we'll later compute lots of expressions of the form $C = g^m\cdot h^r$. To speed that up, we can invest some time and memory to do some precomputation _now_. 
Thankfully, this is very easy to do: 


```Java
g.precomputePow();
h.precomputePow();
System.out.println("Precomputation done.");
```

    Precomputation done.


Future computations `g.pow(...)` and `h.pow(...)` will benefit from precomputation.

<small>_As a side-effect, the values of `g` and `h` have been explicitly computed and can now be printed by `println()` above. You can now see that they indeed look like elliptic curve points._</small> 

## Committing 😱

### Choosing a message 📝
Now let's commit to a message $m$. For Pedersen commitments, $m$ lives in $\mathbb{Z}_n$ (because exponents are to be interpreted modulo the group order $n$). We can get the appropriate $\mathbb{Z}_n$ object from the group:


```Java
var zn = group.getZn();
```

Similar to how a `Group` is a structure that has `GroupElement`s, `zp` is a structure that contains `ZnElement`s. 

We can now instantiate our message $m$, which will be a `ZnElement`, in any of the following ways:


```Java
var m = zn.valueOf(23).mul(42); //simply the number 23*42 (mod p)
System.out.println(m);
```

    966



```Java
var m = zn.getUniformlyRandomElement(); //a random number in Zn
System.out.println(m);
```

    13992166359579056221313865179730665094231114406904438796802013373640178413481



```Java
import de.upb.crypto.math.structures.zn.HashIntoZn;

var m = new HashIntoZn(zn).hashIntoStructure("We attack at midnight! ⚔️"); //the hash of the given String into Zn
System.out.println(m);
```

    357739458326128062426942553905997083565071573036229449938149284158791503092


### Computing the commitment 🎲

Now that we have $m$, let's compute the Pedersen commitment, which is
$$ C = g^m\cdot h^r$$
for a random $r\in\mathbb{Z}_n$.


```Java
var r = zn.getUniformlyRandomElement();
var C = g.pow(m).op(h.pow(r));
System.out.println(C);
```

    LazyGroupElement{computationState=NOTHING}


### On automatic multiexponentiation 🤖

One advantage of the `LazyGroup` approach is that after calling `g.pow(m)`, that value is not immediately computed. This allows us to compute $C$ as a multiexponentiation behind the scenes, i.e. more efficiently than computing $g^m$ and $h^r$ separately and then multiplying them.

This is done automatically when the value of $C$ is needed. We can force computation of $C$ by calling `computeSync()` for the sake of illustration.


```Java
C.computeSync() //computes the value of C and blocks the caller until it's done.
```




    (58169634281804311752524932157207108266551368222203576391328166275732185654637,74943005388860664085553359509906579585955255204193574062154102519615359270473)



The committer can now transmit $C$ to the verifier, who won't learn anything from it ($C$ is uniformly random in $\mathbb{G}$) but will be assured that we cannot later change our mind about $m$.

For this transmission, we'd have to talk about serialization. Very roughly: every `GroupElement` is able to represent itself as a `Representation`, which is safe to send, and its corresponding `Group` is able to undo this process.


```Java
C.getRepresentation()
```




    {"__type":"OBJ","x":"INT:809ad8a49cf1c9553e41bd87adc50b3abd9e920459d5055e0ab4fd34f631a56d","y":"INT:a5b03ce564c4a295314b1376e5b8259d6a44514e0b25a7b777f49e958ae7be49","z":"INT:1"}




```Java
group.getElement(C.getRepresentation()).equals(C)
```




    true



For more information on serialization, see [our documentation regarding `Representation`s](https://upbcuk.github.io/upb.crypto.docs/docs/representations.html).

## Verifying the commitment 🕵️

When we've additionally given $m,r$ to the verifier, they can now check whether $m,r$ is a valid opening for $C$ by checking the following equation:


```Java
g.pow(m).op(h.pow(r)).equals(C)
```




    true



Note that here, $g^m\cdot h^r$ is also automatically computed as multiexponentiation.

... and that's already it for implementing the Pedersen commitment scheme.

## Bonus: Parallelizing 🦑

Another advantage of the `LazyGroup` approach is that it makes group computations easily parallelizable. Consider the following code snippet where we'll compute a whole bunch of commitments:


```Java
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
