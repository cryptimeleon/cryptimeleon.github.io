---
title: Representations
mathjax: true
toc: true
---

Eventually, when writing anything useful, you will be forced to convert Java objects (e.g., a public key) into a format that you can transmit over a network or store on a disk. 
What you need in these cases is *serialization*. 

# The Basic Serialization and Deserialization Processes

For serialization and deserialization, we introduce an intermediate format, the `Representation`.

```
Java object <-> Representation <-> Serialized format (String/byte[])
```

The intermediate format `Representation` makes it easier for classes to implement serialization.
The serialization formats in our libraries are generally not based on standards, but rather flexible ad hoc formats.

*Note: In this document we will sometimes refer to creating the representation of an object as serialization, not to be confused with java's inbuilt serialization.*

## Serialization
Because of the intermediate format, serialization is a two-step process.
1.  Any object in our library that implements the `Representable` interface, for example an encryption key, needs to be able to represent itself as a `Representation`.
2. A `Representation` can then be converted into a serialized format by a `Converter`.
  - The `JSONConverter` converts a `Representation` into a JSON `String`
  - The `BinaryFormatConverter` converts a `Representation` into a less readable but more compact `byte[]` format.

After step 2, you are responsible for how to send/store the resulting (`String`/`byte[]`) data.

## Deserialization
For deserialization, we invert the steps above.

1. Use the `Converter` to get back from the serialized format to a `Representation`.
2. Then use that `Representation` to instantiate the Java object (e.g., an encryption key).

The second step is non-generic and depends heavily on what kind of object you want to instantiate. For example, if you want to instantiate a encryption key, you would call `getEncryptionKey(representation)` on an `EncryptionScheme` object.

# Our Philosophy of Serialization
First of all, we distinguish two types of representable objects: 
1. `StandaloneRepresentable` and 
2. (just) `Representable`. 

Both implement a `getRepresentation()` method which returns a `Representation` object. 

A `StandaloneRepresentable`'s representation contains the complete set of data required to recreate the object from scratch. By contract, `StandaloneRepresentable` classes have a constructor with a single `Representation` parameter such that `foo.equals(new Foo(foo.getRepresentation()))`. 
For example, a `Group` is `StandaloneRepresentable`. Its `Representation` contains all necessary parameters to describe itself (e.g., elliptic curve parameters) and one can easily create a group from some `representation` using `new MyGroup(representation)`.

In contrast, a `Representable`'s representation is not necessarily complete and help may be needed to recreate such an object from `Representation`. 
For example, a `GroupElement` object's representation (e.g., coordinates of an elliptic curve point, but no description of the curve parameters) is usually insufficient to recreate the full object. As a result, a `GroupElement` needs help from its `Group` to be recreated from `Representation` (the pattern is `groupElement = group.getElement(representationOfGroupElement)`).

While it may seem at first like `StandaloneRepresentable` objects are strictly superior (and more convenient), normal `Representable` objects are actually more common because of (1) generally smaller size of representation and (2) security aspects (as described next).

## A Quick Journey into Use-Cases 
There are generally two use-cases for serialization:

1. Serialize trusted data that needs to survive JVM shutdown (but never really leaves a trust zone)
    - Public parameters (such as specific elliptic curve parameters or a hash function key) - usually hardcoded into an application or part of a config file.
    - Secret keys - usually stored on hard disk, ideally in a OS-protected key chain
2. Serialize data to send to or receive from other (untrusted) devices.
    - Public keys
    - Ciphertexts
    - Messages in the context of an interactive protocol

For the first use-case, external mechanisms must ensure that our serialized data is not manipulated. Otherwise, for example, someone could replace elliptic curve parameters with weak ones. Because of this, there is less burden on the serialization and deserialization processes - we can assume that deserialization is fed exactly the value that serialization generated. If the serialized value is changed, security is compromised anyway. 

As a rule of thumb, for the second use-case, you almost never want objects to be `StandaloneRepresentable`. See the next section for details. 

## The Security Pitfalls of Serialization
The idea of having a helper to recreate an object from representation actually serves a security purpose.

For example, suppose you have a `Group` object `group`, which you trust (e.g., something that is hardcoded into the program or was loaded from a trusted file). 
Now if someone sends you the representation `repr` of a group element, this is a value that you do not (and should not) trust. 

In this case, `group` acts as a trust anchor. The statement `g = group.getElement(repr)` should be read as "hey, trusted group, please interpret `repr` as a valid element". The resulting group element `g` can again be trusted (in the sense that it is a valid group element of `group` with all the expected properties that go along with that). 
This approach solves a big set of possible issues such as 
- subgroup attacks: someone may try to send a representation that syntactically looks like a valid group element but that actually has different mathematical properties (belonging to a different subgroup) than valid group elements.
- class substitution: someone may try to send a serialization of a completely different class that uses the wrong group operations (for example `g.pow(x)` may just return `x`, leaking a secret). This would potentially be possible with Java's inbuilt serialization (where deserialization generally reads what class to instantiate from the untrusted data).
- group substitution: someone may try to send a serialization that contains data for a different group parameterization than the trusted parameters. The resulting group element may then lie in a completely different (insecure) group.

For this reason, one should, in cases where a `Representation` may have been sent from an untrusted source, have some trusted object deserialize it. 
For example, this holds for group elements, ciphertexts, signatures, which are deserialized by a `Group`, an `EncryptionScheme`, or a `SignatureScheme`, respectively.

For classes whose `Representation`s will usually come from a trusted source (such as Use-Case 1 above), you can choose to make that class `StandaloneRepresentable` (usually things such as `Group`s, `EncryptionScheme`s, or `SignatureScheme`s, which encode trusted public parameters).


# Making a Class Representable
If you want a classes instances to be representable, you have to implement the `Representable` interface. Many interfaces in the Craco library already extend this interface, e.g. `SigningKey`.

The `Representable` interface requires the implementation of a `getRepresentation()` method. This method should return a representation of your object. Even though this can be done manually, we recommend using the `ReprUtil` class which has methods that make serializing to representation and deserializing back to the object easy.

To create a representation of your object, you can use the following code:

```java
@Override
public Representation getRepresentation() {
    return ReprUtil.serialize(this);
}
```

Now, there is some additional configuration required. Namely, you need to indicate to the serializer which attributes of your class you want to be serialized. This is done by adding the `@Represented` annotation to each attribute. This annotation takes a single string argument: the `restorer`. The restorer indicates to the `ReprUtil` class how to deserialize this attribute. The string is matched to some object implementing the `RepresentationRestorer` interface which can then recreate the object from its representation.

Let's look at an example, a signing key consisting of one exponent `x`:

```java
public class PS18SigningKey implements SigningKey {

    @Represented(restorer = "zp")
    private ZpElement exponentX;

    public PS18SigningKey(Representation repr, Zp zp) {
        new ReprUtil(this).register(zp, "zp").deserialize(repr);
    }

    @Override
    public Representation getRepresentation() {
        return ReprUtil.serialize(this);
    }
}
```
We already talked about the `getRepresentation()` method and `@Represented` annotation. 
Additionally, we have a constructor taking in a representation and the `Zp` field in which the exponents are contained.
This constructor is responsible for deserializing the given `Representation` object back to an instance of `PS18SigningKey`.
The `Zp` class implements the `RepresentationRestorer` object, it can therefore restore the `ZpElement` attributes from the representation. 

To perform the deserialization, we instantiate the `ReprUtil` object with `this` and then register the `Zp` instance as a `RepresentationRestorer` corresponding to the string `"zp"`. 
If you look towards the `@Represented` annotation, you can see that we used the `"zp"` restorer for the single Zp element. 
When we call `deserialize(repr)` on the `ReprUtil` object, it will use the registered `"zp"` restorer – the `Zp` object – and use it to restore `exponentX`.

## Standalone Representables

Alternatively to giving the object responsible for restoring in the constructor parameters, you can also add it as a class attribute so that it can be serialized together with the rest of the instance.
You then won't need to explicitly provide it during deserialization.

For example, your class might have the attribute `groupG` containg a `Group` and a `GroupElement` called `g` from that group. 
`ReprUtil` will first deserialize `groupG` and then use it to restore `g`.
This is possible since `Group` implements the `RepresentationRestorer` interface.
See the example below:

```java
public class SingleGroupElement implements Representable {

    @Represented(restorer = "groupG")
    private GroupElement g;

    @Represented()
    private Group groupG;

    public PS18SigningKey(Representation repr) {
        new ReprUtil(this).deserialize(repr);
    }

    @Override
    public Representation getRepresentation() {
        return ReprUtil.serialize(this);
    }
}
```

You might have noticed that the `Group` attribute has no value assigned to `restorer`.
This is because `Group` implements the `StandaloneRepresentable` interface.
Classes implementing this interface *must* provide a constructor with just a single argument of type `Representation` and the constructor should be able to deserialize the representation just from itself.
`ReprUtil` notices if an attribute implements this interface and automatically deserializes it using this constructor. 

## Restorer Notation: Composite Data Types
The restorer attribute of the `@Represented` annotation has some more syntax to make declaring restorers for composite data types such as arrays easier. Let's look at an example showcasing some of these:

```java
public class NotationExample implements Representable {

    @Represented(restorer = "[zp]")
    private Zp.ZpElement[] exponentsXi;

    @Represented(restorer = "zp -> G")
    private HashMap<Zp.ZpElement, GroupElement> exponentsToGs;

    public PS18SigningKey(Representation repr, Zp zp, Group groupG) {
        new ReprUtil(this).register(zp, "zp").register(groupG, "G").deserialize(repr);
    }

    @Override
    public Representation getRepresentation() {
        return ReprUtil.serialize(this);
    }
}
```

The `"[zp]"` notation is build into the `ReprUtil` class, it will automatically create a restorer for an array of `Zp` elements. 
The same notation works for lists and sets as well.
For maps, you can use the arrow notation `"->"`. 
For example, `"zp -> G"` for a map from Zp elements to group elements (given that you registered the `RepresentationRestorers` for `"zp"` and `"G"` before calling `deserialize()`). 
You can combine these, e.g. `"G1 -> [[G2]]"` for a map from elements of `G1` to lists of lists of elements of `G2`. 

Precedence is given by parentheses, for example, `"(G1 -> G2) -> G3"` is a map whose keys are themselves maps, while `"G1 -> (G2 -> G3)"` has maps as values.

## Restorer Notation: Wrapped Primitive Types

If the type of the attribute is one of `BigInteger`, `Integer`, `String`, `Boolean`, or `byte[]`, giving a specific restorer is not necessary as the framework knows how to deserialize these automatically. Non-wrapped primitive types such as `int` are not supported, however. 

If you want to mix these types with, for example, a map, you can use any non-empty string for the "simple" type. To represent a map from integers to group elements from `G2`, you might use the restorer string `"foo -> G2"`; the `foo` will then be ignored.

## Restorer Notation: Methods

The restorer string also supports a method notation. An example is given below:

```java
public class MethodNotationExample {

    @Represented
    protected BilinearGroup bilinearGroup;

    @Represented(restorer = "bilinearGroup::getG1")
    protected GroupElement g1; // in G_1

    @Represented(restorer = "bilinearGroup::getG2")
    protected GroupElement g2; // in G_2

    @Represented(restorer = "bilinearGroup::getGT")
    protected GroupElement gT; // in G_T
}
```

As you can see, we have one group element from each of the groups making up the bilinear group.
Therefore, each group element needs the corresponding group as a restorer.
In the previous examples, we stored the group directly and could therefore refer to it in the restorer string.
Here, the groups are stored within the bilinear group and accessible via the `getGX()` methods provided by the `BilinearGroup` interface.
To make it easier to access these, the restorer string supports a method notation which gives a method for the `ReprUtil` class to call during deserialization. 
In the above example, `ReprUtil` first deserializes the bilinear group and then uses its `getGX()` method to obtain the corresponding groups which can restore each group element.
