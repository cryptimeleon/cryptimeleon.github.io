---
title: Group Signatures
toc: true
mathjax: true
---

## The Groupsig Library

The [Groupsig](https://github.com/cryptimeleon/groupsig) library offers interfaces and tests useful for implementing group signatures.
These interfaces are based on the work of Diaz, Arroyo and Rodriguez [JAD15] and aim to be flexible to allow for implementing many different types of group signatures.
The groupsig library also provides an example implementation: the group signature of Choi, Park and Yung [CPY06].

Groupsig makes use of other Cryptimeleon libraries: Math for mathematical fundamentals and Craco for cryptographic building blocks and protocol facilities.
They are included in the Groupsig library and can be used without needing to include them as a dependency.
The protocol facilities of Craco are especially relevant, as they include a Schnorr protocol that enables quick and easy implementation of proof of knowledges.
These are for example useful in issue/join protocols.

## Implementing Your Group Signature

To implement a group signature, you will need to implement the `GroupSignatureScheme` interface found in the `org.cryptimeleon.groupsig.common` package.
That package contains all the relevant interfaces.
The `GroupSignatureScheme` interface contains methods for all the group signature algorithms except the setup algorithm.
Setup is usually delegated to another class, and then the generated public parameters are used to instantiate the `GroupSignatureScheme` class.

As the `GroupSignatureScheme` interface aims to accomodate many different kinds of group signature schemes, you might not want to implement all its methods.
For example, your scheme might not support the `trace` algorithm.
Then you would just have that method throw an `UnsupportedOperationException`.

### Join Protocol

Usually, the join protocol is given in the form of an interactive protocol.
The `GroupSignatureScheme` allows you to implement this via its `joinMember` and `joinIssuer` methods.
The networking is intended to be realized via the `BlockingQueue` parameters, aside from this you are free to implement the networking as you like.

To implement the protocol itself, you can make use of Craco's protocol facilities.
To get an idea of how these work, we recommend you take a look at our [protocol tutorial]({% link getting-started/protocols-tutorial.md %}) and then our [example implementation](https://github.com/cryptimeleon/groupsig/tree/develop/src/main/java/org/cryptimeleon/groupsig/cpy06) of [CPY06].

### Data Classes

The other interfaces are mostly for data modelling.
`GroupMembershipList` contains information about each group member in the form of `GMLEntry` instances. These entries are usually generated when the join protocol is complete. 
The issuer then updates the group membership list with the new entry.
`RevocationList` contains information about the group members that had their membership revoked in the form of `RevocationListEntry` instances.
Adding these entries is handled by the `reveal` method of the `GroupSignatureScheme` interface.

### Testing Your Scheme

Groupsig offers some generic testing classes useful for testing `GroupSignatureScheme` implementations.
To use them, you will need to include the `tests` feature variant of the Groupsig library.
In Gradle this can be done by including the following in the dependency section of your `build.gradle` file:

```groovy
testImplementation(group: 'org.cryptimeleon', name: 'groupsig', version: "insertGroupsigVersionHere") {
    capabilities {
        requireCapability("org.cryptimeleon:groupsig-tests")
    }
}
```

Included in this dependency is the `GroupSignatureTester` class which is responsible for running the tests.
To run your own test, you will need to create a subclass of `GroupSignatureTester`.
Then implement a method with the signature `public static Stream<GroupSignatureTestParam> getGroupSignatureTestParams()`.
This method collects the parameters used for the test and returns them in the form of a `Stream`.

You also need to implement a `GroupSignatureTestParam` subclass for your group signature implementation.
This contains the parameters used for the test.

For our [CPY06] group signature, the `GroupSignatureTester` subclass may look as follows:

```java
public class GroupSignatureTesterCPY06 extends GroupSignatureTester {

    public static Stream<GroupSignatureTestParam> getGroupSignatureTestParams() {
        List<GroupSignatureTestParam> params = new LinkedList<>();
        params.add(new CPY06TestParams().get());
        return params.stream();
    }
}
```

You can now run the tests.
Any methods of `GroupSignatureScheme` that throw `UnsupportedOperationException` will lead to the corresponding test being ignored.


## References
[DAR15] Jesus Diaz and David Arroyo and Francisco B. Rodriguez (2015). 
"libgroupsig: An extensible C library for group signatures". https://eprint.iacr.org/2015/1146

[CPY06] Seung Geol Choi, Kunsoo Park, and Moti Yung (2006). "Short Traceable Signatures Based on Bilinear Pairings". 
In Advances in Information and Computer Security (pp. 88–103). Springer Berlin Heidelberg.