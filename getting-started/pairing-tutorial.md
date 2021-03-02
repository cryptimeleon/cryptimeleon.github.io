---
title: Implementing a pairing-based signature scheme
mathjax: true
toc: true
---

Cryptimeleon Math is a library supplying the mathematical basics for cryptography.

In this notebook, we'll take a look at how to implement a pairing-based scheme using Math.

The (multi-message) [Pointcheval-Sanders signature scheme](https://eprint.iacr.org/2015/525) is a very useful digital signature scheme for advanced cryptographic constructions because of its elegant and simple algebraic structure. We'll use it as an example for implementing a cryptographic scheme.

We'll work alongside the scheme's definition in the paper:
![image](/assets/images/ps16-algs-definition.png)

... and show how to implement it. 

---
*Note:*
You can also check this page out in an interactive Jupyter notebook by clicking the badge below:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/cryptimeleon/cryptimeleon.github.io/gh-pages?filepath=getting-started%2Fpairing-tutorial.ipynb)

---

## Setting up the bilinear group

![image](/assets/images/ps16-bil-group-setup.png)
First, we need to set up the bilinear group setting required for the scheme. We need to know the type of pairing and the desired security parameter. In this case we want a type 3 pairing and 100 bit security.


```java
%maven org.cryptimeleon:math:1.0.0
```


```java
import org.cryptimeleon.math.structures.groups.elliptic.*;
import org.cryptimeleon.math.structures.groups.elliptic.type3.bn.BarretoNaehrigBilinearGroup;
import org.cryptimeleon.math.structures.groups.*;
import org.cryptimeleon.math.structures.groups.mappings.*;
import org.cryptimeleon.math.structures.rings.zn.*;

// Choose number of messages r
var r = 3;

// BN pairing is type 3 and we specify a 100 bit security parameter
BilinearGroup bilinearGroup = new BarretoNaehrigBilinearGroup(100);

// Let's collect the values for our pp
Group groupG1 = bilinearGroup.getG1();
Group groupG2 = bilinearGroup.getG2();
Group groupGT = bilinearGroup.getGT();
BilinearMap e = bilinearGroup.getBilinearMap();
BigInteger p = groupG1.size();
Zn zp = bilinearGroup.getZn();
System.out.println("Generated bilinear group of order " + p);
```

    Generated bilinear group of order 66696243400694322499906033083377966773014133293855982130239936888504801018589797


## Generating a key pair

![image](/assets/images/ps16-keygen.png)

For a key pair, we need to generate random exponents $$x$$ and $$y_i$$ as the secret key. Because it's a group of order $$p$$, we interpret the exponents as elements of $$\mathbb{Z}_p$$. 


```java
// Generate secret key

var x = zp.getUniformlyRandomElement();
var y = zp.getUniformlyRandomElements(r); //computes a vector of r random numbers y_0, ..., y_(r-1)

System.out.println("x = " + x);
System.out.println("y = " + y);
```

    x = 41272235882270796841752239763215139690445139220052869021225648819351506091618015
    y = [49933786366933811269708582737180347035824715702155753800334860782944391506415324, 22205577332587401020809980693393162875499620926662659456444824904574515691060729, 1511944759078732359440695394869937420056759028079985561684540830828373717508784]


Then we can compute the corresponding public key easily and run precomputation on it to speed up later verifications:


```java
// Generate public key

var tildeg = groupG2.getUniformlyRandomElement();
var tildeX = tildeg.pow(x).precomputePow(); // this computes X = tildeg^x as above and runs precomputations to speed up later pow() calls on tildeX
var tildeY = tildeg.pow(y).precomputePow(); // because y is a vector, this yields a vector of values tildeg.pow(y_0), tildeg.pow(y_1), ...
```


```java
System.out.println("tildeg = " + tildeg);
System.out.println("tildeX = " + tildeX);
System.out.println("tildeY = " + tildeY);
```

    tildeg = ([5013151925304711734820736931754371120278297611382409653988297386220617843291669, 36426307630823641697822402577629725741773813862144395198532570591476558675458315],[13834308533358986060835197030129147549326283041946192902561764958320384755565843, 41548638325665820337031008242751701479292296351580034686096998863236974141440842])
    tildeX = ([34256840453143014654300481550789032328971237958761236090839037295780079096476572, 38214287811125631274876668325010848913745720736267995349757551432793335687490456],[57716250760473276923747729491086077587965753098484011422317592762331896894629583, 9942896045983436316810759478195526407146234250724861638953736145392844042588208])
    tildeY = [([48640119954767780514184820489977027921555499551804322492656156874754603520710026, 11972514378507745178545318760148141459312750478150838631028604463285404436010532],[48486731488504217889808029592004518602929464871620019708265770751243350628527030, 19638615755996694178150645081069312077342613959978082760489105122806806377844836]), ([52677957005026630601956943179426334605474081516291818272946844334195274801573237, 48392909378279145549483521095505991991304273543305139233638254662106700071221875],[37977188601087102876986000273364884866084864350833430024091208365273311072025379, 34993151244950477203687657050345923280810289397774573988305213076056238499392644]), ([5689691355483976331999929632748492893694622192089277754932940259569951150027676, 45259219041606711126290838675142723986040771579142817898581120168941194708434726],[51313171924877757082712949186705011889939198274781048585226537920543209064163213, 61928534808259309707079769370218177469052011390187128310048151336428814935913276])]





## Computing a signature

![image](/assets/images/ps16-sign.png)

Computing a signature works as you'd expect now with what we've already seen. Messages for Pointcheval-Sanders lie in $$\mathbb{Z}_p$$, but we can use a hash function $$\mathcal{H}:\{0,1\}\rightarrow \mathbb{Z}_p$$ to sign arbitrary strings.


```java
import org.cryptimeleon.math.structures.rings.cartesian.RingElementVector;

// Preparing messages ("Hello PS sigs", 42, 0, 0, ...)
var m = new RingElementVector(
    bilinearGroup.getHashIntoZGroupExponent().hash("Hello PS sigs"), 
    zp.valueOf(42)).pad(zp.getZeroElement(), r
);

// Computing signature
var sigma1 = groupG1.getUniformlyRandomNonNeutral().compute(); // h
var sigma2 = sigma1.pow(x.add(y.innerProduct(m))).compute(); // h^{x + sum(y_i*m_i)}
// The compute() call is optional but will cause sigma1 and sigma2 to be computed concurrently in the background.
```


```java
System.out.println("sigma1 = " + sigma1);
System.out.println("sigma2 = " + sigma2);
```

    sigma1 = (56006416618632332780583594200247128601628771395275437118740944541653305472682157,45304162972427873122256452890890278087417213543851782916398055111404720788154469)
    sigma2 = (7154264489482629758294497409626552359423101433383577228915125618291733406050945,9453029188618284870298649191542904068684443885115144905299453655872473622986862)


## Verifying a signature

![image](/assets/images/ps16-verify.png)

For this verification, we need to emply the pairing `e`.


```java
!sigma1.isNeutralElement() 
    && e.apply(sigma1, tildeX.op(tildeY.innerProduct(m))).equals(e.apply(sigma2, tildeg))
```




    true



If this pairing computation seems slow, check out the [mclwrap](https://github.com/cryptimeleon/mclwrap) addon for a faster bilinear group.
