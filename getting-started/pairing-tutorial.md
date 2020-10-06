---
title: Implementing a pairing-based signature scheme
mathjax: true
tpc: true
---

`upb.crypto.math` is a library supplying the mathematical basics for cryptography.

In this notebook, we'll take a look at how to implement a pairing-based scheme.

The (multi-message) [Pointcheval-Sanders signature scheme](https://eprint.iacr.org/2015/525) is a very useful digital signature scheme for advanced cryptographic constructions because of its elegant and simple algebraic structure. We'll use it as an example for implementing a cryptographic scheme.

We'll work alongside the scheme's definition in the paper:
![image.png](attachment:image.png)

... and show how to implement it. 

---
*Note:*
You can also check this page out in an interactive Jupyter notebook by clicking the badge below:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/upbcuk/upbcuk.github.io/gh-pages?filepath=getting-started%2Fpairing-tutorial.ipynb)

---

## Setting up the bilinear group

![image-2.png](attachment:image-2.png)
First, we need to set up the bilinear group setting required for the scheme. `upb.crypto` provides a nice way of defining requirements you have for the group:


```java
%maven de.upb.crypto:math:2.0.0-SNAPSHOT
```


```java
import de.upb.crypto.math.factory.BilinearGroupFactory;
import de.upb.crypto.math.factory.BilinearGroup;
import de.upb.crypto.math.interfaces.structures.*;
import de.upb.crypto.math.interfaces.mappings.*;
import de.upb.crypto.math.structures.zn.*;

//Choose number of messages r
var r = 3;

var fac = new BilinearGroupFactory(128); //set up a factory for a security parameter 128 curve
fac.setRequirements(BilinearGroup.Type.TYPE_3); //tell it we want a prime-order type 3 setting
BilinearGroup bilinearGroup = fac.createBilinearGroup(); //have the bilinear group generated

//Let's collect the values for our pp
Group groupG1 = bilinearGroup.getG1();
Group groupG2 = bilinearGroup.getG2();
Group groupGT = bilinearGroup.getGT();
BilinearMap e = bilinearGroup.getBilinearMap();
BigInteger p = groupG1.size();
Zn zp = bilinearGroup.getZn();
System.out.println("Generated bilinear group of order "+p);
```

    Generated bilinear group of order 66696243400694322499906033083377966773014133293855982130239936888504801018589797


## Generating a key pair

![image-2.png](attachment:image-2.png)

For a key pair, we need to generate random exponents \\(x\\) and \\(y_i\\) as the secret key. Because it's a group of order \\(p\\), we interpret the exponents as elements of \\(\mathbb{Z}_p\\). 


```java
//Generate secret key
//import de.upb.crypto.math.structures.zn.Zn.ZnElement;

var x = zp.getUniformlyRandomElement();
var y = zp.getUniformlyRandomElements(r); //computes a vector of r random numbers y_0, ..., y_(r-1)

System.out.println("x = " + x);
System.out.println("y = " + y);
```

    x = 29194185653301812958040709888436896895329104382064798546698833870275590673965350
    y = [53625046883063199261390587211645503506170419329125805045471693654277445529005099, 26461054318010074793075004741731802338825758453370563783037053741452260718536308, 4355162467228178687489472557065459517082113886310619174789038123862984715146084]


Then we can compute the corresponding public key easily and run precomputation on it to speed up later verifications:


```java
//Generate public key

var tildeg = groupG2.getUniformlyRandomElement();
var tildeX = tildeg.pow(x).precomputePow(); //this computes X = tildeg^x as above and runs precomputations to speed up later pow() calls on tildeX
var tildeY = tildeg.pow(y).precomputePow(); //because y is a vector, this yields a vector of values tildeg.pow(y_0), tildeg.pow(y_1), ...
```


```java
System.out.println("tildeg = "+tildeg);
System.out.println("tildeX = "+tildeX);
System.out.println("tildeY = "+tildeY);
```

    tildeg = ([33181815845555334358577068381664821343798875962465390910891008825471831131230775, 13759173252834472530665458094698752720169013464273477214357879193677067897449538],[48400772409451731070007287131869842588349583818819704262136088467120452819539790, 44820255457880940775530882633434781340728407777262826152054247968296341908849032])
    tildeX = ([13584324974435098549890062410017173982864337425102084138695982889809632998987227, 37806478085777905719833805458053259025691769182957631520297412772969962894315987],[9556023392299774324836660284943971141188359850226388327556342680813099235169562, 12449168755646069809305987791506076547553852538726873200836414950141408402510708])
    tildeY = [([55337354837484722135621859397626125663743792038086455035915008985484015380522545, 50084524730012055758423997005624960308057532992350373007013993736269501011244075],[6021534321662701332162195755881814874400021819392919300089708520959470560281539, 47791150474356654688646218835785397979091137815219476840640384828088242493694229]), ([26844438214517960332034541941765880301927382011492122251727159716864605853348952, 21130511824083624723348426626686684165530150433655563785330559369861070369165285],[50759885515800441502979572505052932992879684941980271554307220792597178636225556, 53926188088325355604522519840176925656714915494174927537394169524086412586147074]), ([58479031953533949415739523519554592646121535028651744504118684848124535149066759, 21805255030413712955238173382988055769933168125232231082573209007161504496688644],[16528999544906785429703634295889924046392982525938097630276058607995523619567788, 45126686982078300917610059149885829181704441858277624146073012111226899571457054])]





## Computing a signature

![image.png](attachment:image.png)

Computing a signature works as you'd expect now with what we've already seen. Messages for Pointcheval-Sanders lie in \\(\mathbb{Z}_p\\), but we can use a hash function \\(\mathcal{H}:\{0,1\}\rightarrow \mathbb{Z}_p\\) to sign arbitrary strings.


```java
import de.upb.crypto.math.structures.cartesian.RingElementVector;

//Preparing messages ("Hello PS sigs", 42, 0, 0, ...)
var m = new RingElementVector(bilinearGroup.getHashIntoZGroupExponent().hashIntoStructure("Hello PS sigs"), 
                              zp.valueOf(42)).pad(zp.getZeroElement(), r);

//Computing signature
var sigma1 = groupG1.getUniformlyRandomNonNeutral().compute(); //h
var sigma2 = sigma1.pow(x.add(y.innerProduct(m))).compute(); //h^{x + sum(y_i*m_i)}
//The compute() call is optional but will cause sigma1 and sigma2 to be computed concurrently in the background.
```


```java
System.out.println("sigma1 = " + sigma1);
System.out.println("sigma2 = " + sigma2);
```

    sigma1 = (12881395293820437412209221354171775162501313173950762334697141439549977730221868,43275778414801488770710658570270478043470714315195944264453702745904095124331885)
    sigma2 = (52682397122971136378482212917038482071576021326108349866017990788478610130228920,42718363354394888611417510515057317933591529131017082195256278823082542109388199)


## Verifying a signature

![image.png](attachment:image.png)

For this verification, we need to emply the pairing `e`.


```java
!sigma1.isNeutralElement() 
    && e.apply(sigma1, tildeX.op(tildeY.innerProduct(m))).equals(e.apply(sigma2, tildeg))
```




    true



If this pairing computation seems slow, check out the [mclwrap](https://github.com/upbcuk/upb.crypto.mclwrap) addon for a faster bilinear group.
