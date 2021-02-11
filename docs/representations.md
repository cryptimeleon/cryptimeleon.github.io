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


# Tutorial: Making a Class Representable

Now we want to show you how to take a class you have created, and implement serialization and deserialization for it.

There are two options for converting your Java objects to and from their representation: via `ReprUtil` or manually.
We recommend using `ReprUtil` whenever possible as it substantially reduces the work required.

## Serialization And Deserialization Via ReprUtil

We will now look at how to implement support for conversion to and from representation via the `ReprUtil` class.
To illustrate this process, we create a small example class which we want to be able to serialize and deserialize:

```java
    class SomeClass{

        Integer someInt;

        ZpElement exponentX;

        public SomeClass(Integer someInt, ZpElement exponentX) {
            this.someInt = someInt;
            this.exponentX = exponentX;
        }
    }
```

Let's start with looking at how we can implement serialization.

### Implementing Serialization

As we discussed previously, there are two interfaces one can implement to enable serialization: `Representable` and `StandaloneRepresentable`.
In this case, `Representable` is the right choice due to the `ZpElement` fields of class `SomeClass`.
`ZpElement` objects do not contain enough information to be deserialized on their own; therefore, `StandaloneRepresentable` cannot be used.

We therefore make `SomeClass` implement the `Representable` interface which requires implementation of a `getRepresentation` method.
Let's add that:

```java
    class SomeClass implements Representable {

        Integer someInt;

        ZpElement exponentX;

        // insert constructor here

        @Override
        public Representation getRepresentation() {
            return ReprUtil.serialize(this);
        }
    }
```

As you can see, we have added a `getRepresentation` method that returns a `Representation` object.
We have also already implemented the method body by returning the result of `ReprUtil.serialize(this)`.
The static `ReprUtil.serialize` method takes in an `Object` as argument and creates a `Representation` object corresponding to the given argument.

However, if you actually execute `getRepresentation` on a `SomeClass` instance and convert the result to a String, you will get `{"__type":"OBJ"}`.
There is no information about the original object in the `Representation`!

The reason for this is that `ReprUtil` only serializes field values for fields that are marked with the annotation `@Represented`.
All fields that are not annotated this way are simply ignored by `ReprUtil`.
This server the purpose of allowing you to choose exactly which fields are necessary to fully represent your Object, i.e. what you actually need to later deserialize correctly.
Your class may have fields whose values are implied by other field values.
Serializing such fields would therefore not be strictly neccessary for correct deserialization.

Anyways, in this case we need all the field values, so let's add `@Represented`:

```java
    class SomeClass implements Representable {

        @Represented
        Integer someInt;

        @Represented
        ZpElement exponentX;

        // insert constructor here

        @Override
        public Representation getRepresentation() {
            return ReprUtil.serialize(this);
        }
    }
```

If you now convert the result of `getRepresentation` to a String, you will see that the `Representation` object contains the field values for every field that has been annotated using `@Represented`.

This concludes the process of adding serializability to class `SomeClass`. 
However, we are not done yet. 
We still need to add a way to deserialize the representation and get back our original `SomeClass` instance.

### Implementing Deserialization

The standard way of implementing deserialization is via a constructor that takes in a `Representation`, and then deserializes the represented object from that.
For a `StandaloneRepresentable` this constructor should take in exactly one `Representation` argument. For `Representable`, the constructor may also take in other arguments that help with deserialization.

To perform the deserialization, we can once again make use of `ReprUtil`, resulting in the following:

```java
    class SomeClass implements Representable {

        @Represented
        Integer someInt;

        @Represented
        ZpElement exponentX;

        // insert regular constructor here

        public SomeClass(Representation repr) {
            new ReprUtil(this).deserialize(repr);
        }

        @Override
        public Representation getRepresentation() {
            return ReprUtil.serialize(this);
        }
    }
```

The `new ReprUtil(this).deserialize(repr)` call does the following: It deserializes the field values stored within `repr` and stores them in the new `SomeClass` instance given by `this`. 
It only overwrites the values of `this` that have not been initialized yet, i.e. which are set to `null`.
In this case it will restore all fields, since `this`'s fields have not been initialized at that point in the constructor.

The code above does not work as is, however.
As we discussed previously, `ZpElement` instances do require some additional information for deserialization; namely, the `Zp` instance which they belong to.
Therefore, we need to additionally provide `ReprUtil` with the `Zp` instance.

For this purpose, `ReprUtil` provides a `register` method that takes in a `RepresentationRestorer` instance and a String.

A `RepresentationRestorer` is an interface that contains a `recreateFromRepresentation` method. 
This method can be used to deserialize objects that require additional external information for deserialization.
An example of such an object is the `ZpElement`. 
The `Zp` class implements the `RepresentationRestorer` interface and its `recreateFromRepresentation` method can be used to deserialize a `ZpElement` that belongs to that `Zp` instance.

The String argument is an identifier used by `ReprUtil` to refer to that specific `RepresentationRestorer`.

So let's register our `Zp` restorer. This needs to be done *before* calling `deserialize`:

```java
    class SomeClass implements Representable {

        @Represented
        Integer someInt;

        @Represented
        ZpElement exponentX;

        // insert regular constructor here

        public SomeClass(Representation repr, Zp zp) {
            new ReprUtil(this).register(Zp, "zp").deserialize(repr);
        }

        @Override
        public Representation getRepresentation() {
            return ReprUtil.serialize(this);
        }
    }
```

Now we are almost done.
The only thing left to do now is to indiciate to `ReprUtil` which `RepresentationRestorer` it should be using for our `exponentX` field.
This is important since a class may have multiple `ZpElement` fields that belong to different `Zp` instances.
Therefore, we need to tell `ReprUtil` which `Zp` to use to restore which `ZpElement`.

This is where the `"zp"` restorer identifier comes in.
The `@Represented` annotation takes in an optional argument, `restorer`.
This argument should be assigned the identifier used to register the `RepresentationRestorer`.

```java
    class SomeClass implements Representable {

        @Represented
        Integer someInt;

        @Represented(restorer = "zp")
        ZpElement exponentX;

        // insert regular constructor here

        public SomeClass(Representation repr, Zp zp) {
            new ReprUtil(this).register(Zp, "zp").deserialize(repr);
        }

        @Override
        public Representation getRepresentation() {
            return ReprUtil.serialize(this);
        }
    }
```

As you can see, we have provided the `"zp"` restorer to the annotation above `exponentX`.
`ReprUtil` can now use the `Zp` instance we registered to restore our `exponentX` field.

We now have successfully implemented serialization and deserialization for our `SomeClass` class.

This covers the very basics of implementing conversion from and to a `Representation` object via `ReprUtil`.
`ReprUtil` and `@Represented` also support more complex data types and method references. 
For more information on this topic, see the [restorer notation section](#restorer-notation).

## Manual Serialization and Deserialization

Instead of using `ReprUtil`, you can also manually implement serialization and deserialization.

Let us do this for a simple example class (the same as used for the `ReprUtil` tutorial):

```java
    class SomeClass{

        Integer someInt;

        ZpElement exponentX;

        public SomeClass(Integer someInt, ZpElement exponentX) {
            this.someInt = someInt;
            this.exponentX = exponentX;
        }
    }
```

# @Represented Restorers

The `@Represented` annotation, used to indicate which fields should be serialized as part of the `Representation` by `ReprUtil`, takes a String argument: `restorer`.
This can be used to reference the `RepresentationRestorer` that should be used by `ReprUtil` to restore the field's value from its representation.

## Composite Types

The restorer attribute of the `@Represented` annotation supports syntax to make declaring restorers for composite data types such as arrays easier. Let's look at an example showcasing some of these:

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

The square bracket notation (`[]`) is used to indicate arrays, lists and sets.
The entry type restorer string is written between the square brackets.
In our example, the entries are of type `ZpElement` which can be restored using the restorer registered under the `zp` identifier.
Therefore, to indicate an array of `ZpElement`s, we use a `"[zp]"` restorer string.

For maps, you can use the arrow notation `->`. 
For example, `"zp -> G"` for a map from `Zp` elements to group elements (given that you registered the `RepresentationRestorers` for `zp` and group `G` before calling `deserialize()`). 
You can combine these, e.g. `"G1 -> [[G2]]"` for a map from elements of `G1` to lists of lists of elements of `G2`. 

Precedence is given by parentheses, for example, `"(G1 -> G2) -> G3"` is a map whose keys are themselves maps, while `"G1 -> (G2 -> G3)"` has maps as values.

## Primitive Types and StandaloneRepresentable

For boxed types such as `BigInteger`, `Integer`, `String`, `Boolean`, or `byte[]`, you do not need to specify a restorer. 
These types contain enough information on their own to be serialized and deserialized.

However, the non-boxed primitive counterparts, for example `int`, `long` or `bool`, cannot be serialized or deserialized using `ReprUtil`.
This is due to implementation details of `ReprUtil` (primitive types cannot be assigned a `null` value).

For fields that are of a type that implements `StandaloneRepresentable`, you also do not need to give a restorer.
This is because `StandaloneRepresentable` objects can always be recreated without external information as they must implement a constructor that only takes in a `Representation`.

### Combination With Composite Types

For fields of some composite type, but where the entries of the data structure are of some primitive type or `StandaloneRepresentable` (such that usually no restorer would be necessary), you will need to give a restorer to indicate the composite type.

Let's look at, for example, an array of `Integer`s. The `Integer` entries do not require a restorer, but you need to use `[]` to indicate the array type.
In this case, you can use a placeholder restorer string to indicate the `Integer` entry. 
In the case of an array of `Integer`s, this may look like `@Represented(restorer = "[foo]")`.
You do not need to give a restorer corresponding to the `foo` identifier; `ReprUtil` will recognise that no restorer is necessary during deserialization and ignore the `foo`.

## Field Restorers

Alternatively to giving the object responsible for restoring in the constructor parameters, you can also add it as a class attribute so that it can be serialized together with the rest of the instance.
You then won't need to explicitly provide it during deserialization.

For example, you might have a class that contains a `GroupElement`.
Usually, you would need to supply the corresponding `Group` instance to allow for deserialization of the `GroupElement`.
If you want to avoid this, you can also add the `Group` itself to your class and then tell `ReprUtil` to use that group to restore your group element.

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

Here, the group element `g`'s `@Represented` annotation uses `groupG` as its restorer.
When deserializing, `ReprUtil` will look for a field with the name `groupG` and, if found, use it to restore `g`.

Keep in mind that `ReprUtil` first checks for restorers registered via the `register` method.
If you were to additionally register a `Group` with identifier `groupG`, that one would be prefered as a restorer over the `groupG` field.

### Methods

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

In the example on field restorers, we stored the group directly and could therefore refer to it in the restorer string.
Here, the groups are stored within the bilinear group and accessible via the `getGX()` methods provided by the `BilinearGroup` interface.
To make it easier to access these, the restorer string supports a method notation which gives a method for the `ReprUtil` class to call during deserialization.

In the example above, `ReprUtil` first deserializes the bilinear group and then uses its `getGX()` method to obtain the corresponding groups which can restore each group element.
