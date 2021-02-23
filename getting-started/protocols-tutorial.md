---
title: Implementing a verifiable oblivious pseudorandom function (VOPRF)
mathjax: true
toc: true
---

In this notebook, we'll take a look at how to implement a simple protocol: [VOPRFs](https://datatracker.ietf.org/doc/draft-irtf-cfrg-voprf/) (based on this [paper](https://eprint.iacr.org/2014/650)).

---
*Note:*
You can also check this page out in an interactive Jupyter notebook by clicking the badge below:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/cryptimeleon/cryptimeleon.github.io/gh-pages?filepath=getting-started%2Fprotocols-tutorial.ipynb)

---

## 🗒 The basic setup
A VOPRF is, first and foremost, a PRF. The secret key $$k$$ for the PRF is a random scalar and we'll call $$h = g^k$$ the "public key". 
The values of the $$\mathrm{PRF}_k: \{0,1\}^* \rightarrow \{0,1\}^n$$ are 

$$\mathrm{PRF}_k(x) = H_2(h, x, H_1(x)^k)$$

where $$H_1:\{0,1\}^*\rightarrow \mathbb{G}$$, $$H_2:\{0,1\}^* \rightarrow \{0,1\}^n$$ are hash functions modeled as random oracles.

This is a PRF because under appropriate (DDH-type) assumptions (essentially the only way to distinguish a PRF-value $$\mathrm{PRF}_k(x)$$ from random is to compute $$H_1(x)^k$$ without knowing $$k$$).

## 🥸 How to obliviously retrieve function values

Now in an *oblivious* PRF, there is a protocol between two parties: the *issuer* and the *user*. The issuer holds a PRF key $$k$$ and publishes the public key $$h = g^k$$. The user wants to retrieve $$\mathrm{PRF}(x)$$ for some bit string $$x \in \{0,1\}^*$$ from the issuer without revealing $$x$$. In our case, this protocol works as follows:

- The user chooses a random scalar $$r$$ and sends $$a = H_1(x)^r$$ to the issuer.
- The issuer replies with $$a^k$$ and a zero-knowledge proof that he has used the right $$k$$ to compute $$a^k$$.

Note that in this protocol, the user only sends a random value $$a$$ that holds no information about $$x$$, so the issuer cannot learn $$x$$. The zero-knowledge proof ensures that the issuer cannot send incorrect responses (which he might otherwise do to "tag" requests).

## 📡 Implementation - Setup

So let's implement this using our library. First, let's do the basic setup. 


```java
%maven org.cryptimeleon:math:1.0.0-SNAPSHOT
%maven org.cryptimeleon:craco:1.0.0-SNAPSHOT

import org.cryptimeleon.math.structures.groups.elliptic.nopairing.Secp256k1;
import org.cryptimeleon.math.structures.groups.lazy.*;
import org.cryptimeleon.math.hash.impl.SHA256HashFunction;
import org.cryptimeleon.math.structures.rings.zn.Zn;
import org.cryptimeleon.math.hash.impl.ByteArrayAccumulator;
import org.cryptimeleon.math.structures.groups.*;
import org.cryptimeleon.math.serialization.converter.JSONPrettyConverter;
import org.cryptimeleon.craco.protocols.arguments.sigma.schnorr.*;
import org.cryptimeleon.craco.protocols.*;
import org.cryptimeleon.craco.protocols.arguments.fiatshamir.FiatShamirProofSystem;

//Set up group and generate key
var group = new LazyGroup(new Secp256k1()); 
var H1 = new HashIntoLazyGroup(new Secp256k1.HashIntoSecp256k1(), group);
var H2 = new SHA256HashFunction();
var jsonConverter = new JSONPrettyConverter(); //for serialization later

var g = group.getGenerator();
var k = group.getUniformlyRandomNonzeroExponent(); //secret key
var h = g.pow(k).precomputePow(); //public key
```

With this setup, we can naively (without hiding x) evaluate $$\mathrm{PRF}_k(x) = H_2(h, x, H_1(x)^k)$$ as follows:


```java
byte[] evaluatePRF(Zn.ZnElement k, byte[] x) {
    var h2Preimage = new ByteArrayAccumulator();
    h2Preimage.escapeAndSeparate(h);
    h2Preimage.escapeAndSeparate(x);
    h2Preimage.escapeAndAppend(H1.hash(x).pow(k));
    
    return H2.hash(h2Preimage.extractBytes());
}
```


```java
var result = evaluatePRF(k, new byte[] {4, 8, 15, 16, 23, 42});
Arrays.toString(result)
```




    [106, 62, -26, 71, -118, 114, 53, -58, -27, 120, -6, 30, -102, 23, 64, -85, -90, 89, 35, 98, -20, -40, 109, -1, 55, 21, -50, 41, -95, -69, -86, 38]



## ↔️ Implementation - Zero-knowledge proof

To implement the oblivious evaluation protocol, we start with the subprotocol to prove that the issuer's response is valid. 
Specifically, when the issuer gets $$a$$ and replies with $$b = a^k$$, he needs to *prove knowledge of $$k$$ such that $$b = a^k \land h = g^k$$, i.e. $$a$$ was exponentiated with the correct secret key belonging to public key $$h$$. In Camenisch-Stadler notation:

$$\mathrm{ZKPoK}\{(k) :\ b = a^k \land h = g^k\}$$


For this, we implement our own Schnorr-style protocol. Within the protocol framework of our library, we think of Schnorr-style protocols as being composed of "fragments". In our case, the protocol will consist of two fragments, one that handes the $$b = a^k$$ part, one that handles the $$h = g^k$$ part (in general, fragments can also handle more complicated statements, such as "$$z \leq 100$$", but those are not needed in this example).

Essentially, what we want is a `DelegateProtocol`, i.e. one that delegates its functionality to two sub-"fragments". For this protocol, we need to define mostly two things:

1. which variables/witnesses are proven knowledge of and which subprotocols (fragments) shall be instantiated? (we call this the *subprotocol spec*)
2. which value(s) for the witness(es) shall the prover use? (we call this the *prover spec*)

With this defined, composing this into a Schnorr-style protocol is done automatically behind the scenes.


```java

class ProofCommonInput implements CommonInput {
    public final GroupElement a,b;
    
    public ProofCommonInput(GroupElement a, GroupElement b) {
        this.a = a;
        this.b = b;
    }
}

class ProofWitnessInput implements SecretInput {
    public final Zn.ZnElement k;
    
    public ProofWitnessInput(Zn.ZnElement k) {
        this.k = k;
    }
}

class ReplyCorrectnessProof extends DelegateProtocol {
    @Override
    protected SendThenDelegateFragment.SubprotocolSpec provideSubprotocolSpec(CommonInput commonInput, SendThenDelegateFragment.SubprotocolSpecBuilder builder) {
        //In this method, we define (for prover and verifier alike) what the proof parameters shall be.
        //We want to prove knowledge of a single variable, namely k. So we register "k" of type Zp with the builder.
        var kVar = builder.addZnVariable("k", group.getZn());
        //the result is a variable kVar that we will reference in the following.
        
        //Now we need to define what shall be proven. For this, we reference the knowledge variable created above.

        //statementToBeProven is an Expression "a^k = b" with variable k (not something that's computed here and now)
        var statementToBeProven = ((ProofCommonInput) commonInput).a.pow(kVar).isEqualTo(((ProofCommonInput) commonInput).b); 
        
        //With this expression format we tell the framework to add the fragment for "a^k = b" to the proof
        builder.addSubprotocol("replyCorrect", new LinearStatementFragment(statementToBeProven));

        //Similarly, we handle the other fragment
        builder.addSubprotocol("publicKeyCorrect", new LinearStatementFragment(g.pow(kVar).isEqualTo(h)));

        //Aaaand that's it :) - We have defined to prove knowledge of k such that a^k = b and g^k = h.
        return builder.build();
    }
    
    @Override
    protected SendThenDelegateFragment.ProverSpec provideProverSpecWithNoSendFirst(CommonInput commonInput, SecretInput secretInput, SendThenDelegateFragment.ProverSpecBuilder builder) {
        //Here, we need to set up which witnesses the issuer shall use, i.e. their secret key.
        //For every builder.addZnVariable() above, we must set the witness here (usually from secretInput)
        builder.putWitnessValue("k", ((ProofWitnessInput) secretInput).k);
        
        //That's it already, that's all the additional info the prover needs.
        return builder.build();
    }

    @Override
    public BigInteger getChallengeSpaceSize() {
        return group.size();
    }
}

//Wrap the sigma protocol into a Fiat-Shamir proof system
var fiatShamirProofSystem = new FiatShamirProofSystem(new ReplyCorrectnessProof());
```

## 🛠 Implementing the rest

We're now ready to implement the rest of the protocol. 

### 🙋 Client's request
Let's start with the user's first message $$a = H_1(x)^r$$.


```java
//User's perspective

byte[] x = new byte[] {4, 8, 15, 16, 23, 42}; //want PRF(x)

var r = group.getUniformlyRandomExponent();
GroupElement a = H1.hash(x).pow(r);

//Send (serialized) group element
String messageOverTheWire = jsonConverter.serialize(a.getRepresentation());
messageOverTheWire
```




    {
       "__type":"OBJ",
       "x":"INT:b3473a9f85c77f854dd63cf7fa1ccefea94d01e56ee5e48d4780fc10d739159a",
       "y":"INT:f2349fd03e28b5317d9b11b3c60dc18176ca5febf8a1a69b296fe769051f8962",
       "z":"INT:1"
    }



### 💁 Server's response

Now the server responds with $$b = a^k$$ as well as a proof of correctness.


```java
//Server's perspective

//Deserialize the request (also ensures the request is a valid group element)
GroupElement aServer = group.getElement(jsonConverter.deserialize(messageOverTheWire));

//Compute the response
var bServer = aServer.pow(k);

//Compute the proof
var proofServer = fiatShamirProofSystem.createProof(new ProofCommonInput(aServer,bServer), new ProofWitnessInput(k));

//Send response
var responseRepresentation = new org.cryptimeleon.math.serialization.ListRepresentation(bServer.getRepresentation(), proofServer.getRepresentation());
var responseOverTheWire = jsonConverter.serialize(responseRepresentation);
responseOverTheWire
```




    [
       {
          "__type":"OBJ",
          "x":"INT:228454d675943ced4b405f4985741b107ab870d2f23008894ce7d4fc2f10a821",
          "y":"INT:9bc38151c206651a1317419b7d95c63d149512d8c825b0da610c1504cdb06cb6",
          "z":"INT:1"
       },
       {
          "__type":"OBJ",
          "challenge":"INT:be1c5a94203dacdd7c472dd05e98eebd6f65619d465f66b7d4b2c2febf44f7",
          "transcript":[
             null,
             [
                "INT:cf50480a8e66ae729e060642faf973789406c8ce822bb4539cc26a9e1bed4ea1"
             ],
             null,
             null
          ]
       }
    ]



### 🧑‍🎓 Client unblinding and proof check

Now the client checks the proof and unblinds $$b$$ as $$b^{1/r}$$, getting $$H_1(x)^k$$ and computing the PRF value from that.


```java
//Deserialize stuff
var deserializedResponse = jsonConverter.deserialize(responseOverTheWire);
var b = group.getElement(deserializedResponse.list().get(0));

//Check proof
var commonInput = new ProofCommonInput(a,b); //set common input for proof
var proof = fiatShamirProofSystem.recreateProof(commonInput, deserializedResponse.list().get(1)); //deserialize proof
assert fiatShamirProofSystem.checkProof(commonInput, proof); //check proof

//Unblind b and compute PRF value
var h2Preimage = new ByteArrayAccumulator();
h2Preimage.escapeAndSeparate(h);
h2Preimage.escapeAndSeparate(x);
h2Preimage.escapeAndAppend(b.pow(r.inv()));

var result = H2.hash(h2Preimage.extractBytes());
Arrays.toString(result)
```




    [106, 62, -26, 71, -118, 114, 53, -58, -27, 120, -6, 30, -102, 23, 64, -85, -90, 89, 35, 98, -20, -40, 109, -1, 55, 21, -50, 41, -95, -69, -86, 38]



## ✅ Done.

Thanks for looking at this tutorial 🙂
