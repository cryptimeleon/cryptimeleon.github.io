---
title: Representations
mathjax: true
toc: true
---

Representations offer a way to convert objects to a representation which can then be converted into some kind of serialization, for example into a JSON object or binary data for transmission over a network.

This is useful if you want to, for example, transmit a public key over the internet. You can use the representation framework to convert your public key object into a representation, and then convert it to a JSON-encoded String using the `JSONConverter` class. A binary converter is provided by `BinaryFormatConverter`.

*Note: In this document we will refer to creating a representation of an object as serialization, not to be confused with java's inbuilt serialization.*

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
When we call `deserialize(repr)` on the `ReprUtil` object, it will use the registered `"zp"` restorer–the `Zp` object–and use it to restore `exponentX`.

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
You can combine these, e.g. `"G1 -> [[G2]]"` for a map from elements of `G1` to list of list of elements of `G2`. 

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