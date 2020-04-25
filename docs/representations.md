---
title: Representations
mathjax: true
---

Representations offer a way to convert objects to a representation which can then be converted into some kind of serialization, for example into a JSON object or binary data for transmission over a network.

This is useful if you want to, for example, transmit a public key over the internet. You can use the representation framework to convert your public key object into a representation, and then convert it to JSON using the `JSONConverter` class. Currently, this converter class is the only one that is supported, but you can add new ones using the `Converter` abstract class.

*Note: In this document we will refer to creating a representation of an object as serialization, not to be confused with java's inbuilt serialization.*

# Making a Class Representable
If you want a classes instances to be representable, you have to implement the `Representable` interface. Many interfaces in the **upb.de.craco** library already extend this interface, e.g. `SigningKey`.

The `Representable` interface requires the implementation of a `getRepresentation()` method. This method should return a representation of your object. This could be potentially quite cumbersome and require knowledge of the representation framework, but the `ReprUtil` class has some utility methods that make serializing to representation and deserializing back to the object easy.

To create a representation of your object, you can use the following code:

```java
@Override
public Representation getRepresentation() {
    return ReprUtil.serialize(this);
}
```

Now, there is some additional configuration required. Namely, you need to indicate to the serializer which attributes of your class you want to be serialized. This is done by adding the `@Represented` annotation to each attribute. This annotation takes a single string argument: the `restorer`. The restorer indicates to the `ReprUtil` class how to deserialize this attribute. The string is matched to some object implementing the `RepresentationRestorer` interface which can then recreate the object from its representation.

Let's look at an example, a signing key consisting of one exponent \\(x\\) and an array of exponents \\(y_i\\):

```java
public class PS18SigningKey implements SigningKey {

    @Represented(restorer = "zp")
    private ZpElement exponentX;

    @Represented(restorer = "[zp]")
    private ZpElement[] exponentsYi;

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
Additionally, we have a constructor taking in a representation and the Zp ring in which the exponents are contained. 
A `Zp` object can itself not be represented, so it must be given explicitly. 
The `Zp` class implements the `RepresentationRestorer` object, it can therefore restore the `ZpElement` attributes from the representation. 

To perform the deserialization, we instantiate the `ReprUtil` object with `this` and then register the class as a representation restorer corresponding to the string `"zp"`. 
If you look towards the `@Represented` annotation, you can see that we used the `"zp"` restorer for the single Zp element and the `"[zp]"` restorer for the array of Zp elements. 
When we call `deserialize(repr)` on the `ReprUtil` object, it will use the registered `"zp"` restorer–the `Zp` object–and use it to restore the attributes.

Alternatively to giving the object responsible for restoring in the constructor, you can also add it as a class attribute which can for example be useful for public parameters. 
In that case the `Zp` object would be an attribute of the class, and you will need to use a restorer string with the same value as the name of the attribute. 
For example, your class might have the attribute `groupG1` and a `GroupElement` called `g` from that group. 
`g` will then use the restorer `groupG1` and `ReprUtil` will automatically match the two. 
Keep in mind that `groupG1` must have access identifier public; otherwise, `ReprUtil` cannot access it to deserialize `g`.

The `"[zp]"` notation is build into the `ReprUtil` class, it will automatically create a restorer for an array of Zp elements. 
The same notation works for lists and sets as well.
For maps, you can use the arrow notation `"->"`. 
For example, `"zp -> g"` for a map from Zp elements to group elements (given that you registered the `RepresentationRestorers` for `"zp"` and `"g"` before calling `deserialize()`). 
You can combine these, e.g. `"G1 -> [[G2]]"` for a map from elements of \\(G_1)\\) to list of list of elements of \\(G_2\\). 
Precedence is given by parentheses, for example, `"(G1 -> G2) -> G3"` is a map whose keys are themselves maps, while `"G1 -> (G2 -> G3)"` has maps as values.

If the type of the attribute is one of `BigInteger`, `Integer`, `String`, `Boolean`, or `byte[]`, giving a specific restorer is not necessary as the framework knows how to deserialize these automatically (keep in mind primitives such as `int` don't work). If you want to mix such "simple" types with, for example, a map, you can use any non-empty string for the "simple" type. To represent a map from integers to group elements from \\(G_2\\), you might use the restorer string `"foo -> G2"`; the `foo` will then be ignored.

The same holds for classes that implement the `StandaloneRepresentable` interface. These *must* have a constructor with just a single argument of type `Representation` and the constructor should be able to deserialize the representation just from itself. `ReprUtil` will be able to reconstruct these without giving an explicit restorer.

TODO: talk about using a standalone representable group to restorer other group elements.