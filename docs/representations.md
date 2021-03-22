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

The second step is non-generic and depends heavily on what kind of object you want to instantiate. For example, if you want to instantiate a encryption key, you would call `restoreEncryptionKey(representation)` on an `EncryptionScheme` object.

# Our Philosophy of Serialization
First of all, we distinguish two types of representable objects: 
1. `StandaloneRepresentable` and 
2. (just) `Representable`. 

Both implement a `getRepresentation()` method which returns a `Representation` object. 

A `StandaloneRepresentable`'s representation contains the complete set of data required to restore the object from scratch. By contract, `StandaloneRepresentable` classes have a constructor with a single `Representation` parameter such that `foo.equals(new Foo(foo.getRepresentation()))`. 
For example, a `Group` is `StandaloneRepresentable`. Its `Representation` contains all necessary parameters to describe itself (e.g., elliptic curve parameters) and one can easily create a group from some `representation` using `new MyGroup(representation)`.

In contrast, a `Representable`'s representation is not necessarily complete and help may be needed to restore such an object from `Representation`. 
For example, a `GroupElement` object's representation (e.g., coordinates of an elliptic curve point, but no description of the curve parameters) is usually insufficient to restore the full object. As a result, a `GroupElement` needs help from its `Group` to be restored from `Representation` (the pattern is `groupElement = group.restoreElement(representationOfGroupElement)`).

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
The idea of having a helper to restore an object from representation actually serves a security purpose.

For example, suppose you have a `Group` object `group`, which you trust (e.g., something that is hardcoded into the program or was loaded from a trusted file). 
Now if someone sends you the representation `repr` of a group element, this is a value that you do not (and should not) trust. 

In this case, `group` acts as a trust anchor. The statement `g = group.restoreElement(repr)` should be read as "hey, trusted group, please interpret `repr` as a valid element". The resulting group element `g` can again be trusted (in the sense that it is a valid group element of `group` with all the expected properties that go along with that). 
This approach solves a big set of possible issues such as 
- subgroup attacks: someone may try to send a representation that syntactically looks like a valid group element but that actually has different mathematical properties (belonging to a different subgroup) than valid group elements.
- class substitution: someone may try to send a serialization of a completely different class that uses the wrong group operations (for example `g.pow(x)` may just return `x`, leaking a secret). This would potentially be possible with Java's inbuilt serialization (where deserialization generally reads what class to instantiate from the untrusted data).
- group substitution: someone may try to send a serialization that contains data for a different group parameterization than the trusted parameters. The resulting group element may then lie in a completely different (insecure) group.

For this reason, one should, in cases where a `Representation` may have been sent from an untrusted source, have some trusted object deserialize it. 
For example, this holds for group elements, ciphertexts, signatures, which are deserialized by a `Group`, an `EncryptionScheme`, or a `SignatureScheme`, respectively.

For classes whose `Representation`s will usually come from a trusted source (such as Use-Case 1 above), you can choose to make that class `StandaloneRepresentable` (usually things such as `Group`s, `EncryptionScheme`s, or `SignatureScheme`s, which encode trusted public parameters).


# Tutorial: Making a Class Representable

Now we want to show you how to take a class you have created, and implement serialization and deserialization for it.

There are two options for converting your Java objects to and from their representation: via `ReprUtil` or manually without using `ReprUtil`.
The `ReprUtil` approach has the advantage of requiring less code.
Classes we have implemented, for example as part of Craco, usually use it for that reason.
However, the manual conversion may be easier to understand.
Therefore, we will present the manual approach first via a small toy example.
After that, we do the same for `ReprUtil`.

Both approaches are usable, but we generally recommend usage of `ReprUtil` over the manual approach.

You can skip to the `ReprUtil` tutorial via [this link](#serialization-and-deserialization-via-reprutil).

## Manual Serialization and Deserialization

We will now walk you through implementing manual serialization and deserialization for the following simple class:

```java
    class SomeClass {

        Integer someInt;

        ZpElement exponentX;

        public SomeClass(Integer someInt, ZpElement exponentX) {
            this.someInt = someInt;
            this.exponentX = exponentX;
        }
    }
```

### Manual Serialization

To implement serialization, we can either have `SomeClass` implement the `Representable` or the `StandaloneRepresentable` interface.
In this case, `Representable` is the only choice.
We will see why in the section on deserialization.

`Representable` (and `StandaloneRepresentable`) requires implementation of a `getRepresentation` method that returns a `Representation`:

```java
    class SomeClass implements Representable {

        Integer someInt;

        ZpElement exponentX;

        // insert regular constructor here

        @Override
        public Representation getRepresentation() {
            // empty body so far
        }
    }
```

To create a `Representation` object that can later be deserialized again, we now need to decide which fields of `SomeClass` are required to restore the original object.
In this case all fields are required.
Hence, we need to create a `Representation` object that contains the values of fields `someInt` and `exponentX`.

The `serialization` package in the Math library provides a number of different `Representation` subclasses that implement representations for different kind of values:

- `BigIntegerRepresentation` for storing all kinds of integers
- `ByteArrayRepresentation` for storing `byte[]` objects
- `ListRepresentation` for storing arrays, lists and sets cointaining `Representation` objects
- `MapRepresentation` for storing maps from `Representation` to `Representation`
- `ObjectRepresentation` for storing an arbitrary object via a map from `String` to `Representation`
- `StringRepresentation` for storing `String` objects

Using these classes, we can implement `getRepresentation` as follows:

```java
    class SomeClass implements Representable {

        Integer someInt;

        ZpElement exponentX;

        // insert regular constructor here

        @Override
        public Representation getRepresentation() {
            ObjectRepresentation objRepr = new ObjectRepresentation();
            objRepr.put("someInt", new BigIntegerRepresentation(someInt));
            objRepr.put("exponentX", exponentX.getRepresentation());
            return objRepr;
        }
    }
```

To represent a `SomeClass` object, we use a `ObjectRepresentation` in which we then store the fields `someInt` and `exponentX`.
The `put` method of `ObjectRepresentation` allows storing representations via a String identifier.
We have chosen to use each variable's name as the identifier in this example, but that is not strictly necessary.
Since `put` expects to be given a `Representation`, we need to wrap `someInt` into a `Representation` object. 
This can be done via `BigIntegerRepresentation`.
The `ZpElement` class already implements `Representable`.
Therefore, it already implements a `getRepresentation` method which we use to obtain a representation of `exponentX`.

Once we are done with constructing the `ObjectRepresentation`, we just return it.

You will not always need to use an `ObjectRepresentation` for serialization.
If your class only consists of a single field, or a single field suffices to restore the original object, you can just return a representation of that single field instead.
For example, if our class only consisted of `exponentX`, we could implement `getRepresentation` by just returning the return value of `exponentX.getRepresentation()`.
This would be enough for deserialization.

### Manual Deserialization

To deserialize a given `Representation`, we need to create a new `SomeClass` object, extract the field values from the `Representation`, and then fill the `SomeClass` object with the extracted values.

The standard approach in the Cryptimeleon libraries is via a new constructor that takes in at minimum a `Representation` object and restores the original object from that.

```java
    class SomeClass implements Representable {

        Integer someInt;

        ZpElement exponentX;

        // insert regular constructor here

        public SomeClass(Representation repr, Zp zp) {
            ObjectRepresentation objRepr = (ObjectRepresentation) repr;
            someInt = objRepr.get("someInt").bigInt().getInt();
            exponentX = zp.restoreElement(objRepr.get("exponentX"));
        }

        @Override
        public Representation getRepresentation() {
            ObjectRepresentation objRepr = new ObjectRepresentation();
            objRepr.put("someInt", new BigIntegerRepresentation(someInt));
            objRepr.put("exponentX", exponentX.getRepresentation());
            return objRepr;
        }
    }
```

As you can see, we have already implemented the new constructor.
In addition to the representation we want to deserialize, we have provided the `Zp` instance to which the `exponentX` element belongs.
This is necessary as `ZpElement` instances cannot be deserialized just from their representation alone; deserialization must be done using their `Zp` instance. 
This is the reason why we had `SomeClass` implement `Representable` and not `StandaloneRepresentable` as the latter requires the existence of a deserialization constructor with just a single `Representation` argument.
Hence, we also need to provide the `Zp` instance.

We first typecast the `repr` object to a `ObjectRepresentation` to gain access to the methods of `ObjectRepresentation`.

Next, we extract the `someInt` value.
We use `get` to obtain the `Representation` used to store `someInt`.
Remember to use the same String identifier as you used for `put` during serialization, otherwise this will not work.
Since `get` returns a `Representation` object, we use the `bigInt` method to typecast it to a `BigIntegerRepresentation`. The `Representation` object contains such typecasting methods for each of its subclasses.
Finally, we call `getInt` to retrieve the `Integer` object that was stored inside the `BigIntegerRepresentation`.

To complete deserialization, we need to restore `exponentX`.
To do this, we use the `restoreElement` method of `Zp`.
This method takes in a `Representation` and, if possible, restores the corresponding `ZpElement` from it.

`restoreElement` is a method specific to `Zp` used to deserialize `ZpElement` instances.
Other classes that can deserialize `Representation` objects usually have similarly named methods, for example `restoreEncryptionKey` for the `EncryptionScheme` interface that is part of Craco.

We have now completed the implementation of manual serialization and deserialization.
To actually send the object over the wire, you will need to convert the representation to some format that can be sent.
Refer to the [section on conversion to a sendable format](#conversion-to-a-sendable-format) for more information on this topic.

## Serialization And Deserialization Via ReprUtil

We will now look at how to implement support for conversion to and from representation via the `ReprUtil` class.
To illustrate this process, we create a small example class which we want to be able to serialize and deserialize:

```java
    class SomeClass {

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
It only overwrites the fields of `this` that have not been initialized yet, i.e. which are set to `null`.
In the above example, it will restore all fields since `this`'s fields have not been initialized at that point in the constructor.

The code above does not work as is, however.
As we discussed previously, `ZpElement` instances do require some additional information for deserialization; namely, the `Zp` instance which they belong to.
Therefore, we need to additionally provide `ReprUtil` with the `Zp` instance.
This is also the reason we cannot make `SomeClass` a `StandaloneRepresentable` as that requires the constructor to only take in a `Representation` and no extra information such as `Zp`.

To add such extra information, `ReprUtil` provides a `register` method that takes in a `RepresentationRestorer` instance and a String.
A `RepresentationRestorer` can be used to deserialize objects that require additional external information for deserialization.
An example of a representation restorer is the class `Zp`.
It can be used to deserialize a `ZpElement` that belongs to that `Zp` instance.
The String argument of `register` is an identifier used by `ReprUtil` to refer to that specific `RepresentationRestorer`.

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
The only thing left to do now is to indicate to `ReprUtil` which `RepresentationRestorer` it should be using for our `exponentX` field.
This is important since a class may have multiple `ZpElement` fields that belong to different `Zp` instances.
Therefore, we need to tell `ReprUtil` which `Zp` to use to restore which `ZpElement`.

This is where the `"zp"` restorer identifier that we passed to `register` comes in.
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
For more information on this topic, see the [restorer notation section](#reprutil-restorer-notation).

# Conversion To A Sendable Format

Implementing conversion to and from the representation format is not enough to actually send your object over a channel.
You also need to convert the representation to a format that can actually be sent, such as a String or a binary format.

To enable this, we have implemented some different `Converter` classes.
The `Converter` interface, part of the `serialization.converter` package in Math, enforces implementation of two methods: `serialize` and `deserialize`.
The `serialize` method is responsible for converting the given `Representation` object to some format that can then be sent over the channel.
The `deserialize` method does the opposite: It converts the received data back to a `Representation`.

As part of Math, we provide converters to two different channel formats: JSON and a binary format.
The JSON format is provided via the `JSONConverter` class and the binary format via the `BinaryFormatConverter` class.
The `JSONPrettyConverter` creates a JSON String better suited for reading by human eyes, but it also wastes a lot of space due to the inserted white spaces.
Of course you can also implement your own `Converter` if needed.

# Representation Restorers

Objects that implement `Representable` and not `StandaloneRepresentable` generally require external help to be deserialized correctly.
This help is given by a `RepresentationRestorer`.
`RepresentationRestorer` is an interface for classes that can deserialize representations containing specific types of objects back to the original object.
An example is the `Zp` class in Cryptimeleon Math.
It can deserialize `ZpElement` instances that belong to the corresponding $$\mathbb{Z}_p$$ field.

Generally, elements of some algebraic structure that are not `StandaloneRepresentable` can be restored by the class representing the structure itself.
For example, the `Group` class can restore `GroupElement` objects via its `restoreElement` method.

For cryptographic scheme such as an encryption scheme, usually the scheme itself acts as the restorer. 
It can restore ciphertexts, encryption keys, plaintexts, and ciphertexts.
This is because the scheme instance generally contains the public parameters which have information about the algebraic structures needed for restoration.
For example, the `EncryptionScheme` class offers methods `restorePlainText`, `restoreCipherText`, `restoreEncryptionKey`, and `restoreDecryptionKey` to restore the corresponding objects from their representation.
When implementing a new encryption scheme, you can implement those methods and then use the `EncryptionScheme` object as the restorer.

```java
    @Override
    public ElgamalCipherText restoreCipherText(Representation repr) {
        return new ElgamalCipherText(repr, groupG);
    }
```

The above is an example taken from our ElGamal encryption implementation.
The `restoreCipherText` method calls the deserialization constructor of `ElGamalCipherText` to restore the object from the given representation.
As an ElGamal ciphertext contains a group element, you also need to provide the group that contains that group element.
This is possible since the scheme has information about that group as given by the `groupG` field variable.

If you are ever unsure what types of object a `RepresentationRestorer` can restore, consult its `restoreFromRepresentable` method.
This method is used by `ReprUtil` to perform the restoration and usually contains a number of if-conditions which tell you which types are supported.
The `restoreFromRepresentable` in `EncryptionScheme` looks as follows:

```java
    default Object restoreFromRepresentation(Type type, Representation repr) {
        if (type instanceof Class) {
            if (EncryptionKey.class.isAssignableFrom((Class) type)) {
                return this.restoreEncryptionKey(repr);
            } else if (DecryptionKey.class.isAssignableFrom((Class) type)) {
                return this.restoreDecryptionKey(repr);
            } else if (CipherText.class.isAssignableFrom((Class) type)) {
                return this.restoreCipherText(repr);
            } else if (PlainText.class.isAssignableFrom((Class) type)) {
                return this.restorePlainText(repr);
            }
        }
        throw new IllegalArgumentException("Cannot restore object of type: " + type.getTypeName());
    }
```

From this method, you can see that `EncryptionScheme` can be used to restore objects of type `EncryptionKey`, `DecryptionKey`, `CipherText`, and `PlainText`.

The `restoreFromRepresentation` method is *not* meant to be used manually in your code.
It should be used as a reference for which kind of objects are supported, or, if you are manually serializing and deserializing, to find out which methods to use for deserialization.
For example, the `restoreFromRepresentation` method of `EncryptionScheme` indicates the use of `restoreEncryptionKey` for restoring `EncryptionKey` objects.

# ReprUtil: Restorer Notation

The `@Represented` annotation, used to indicate which fields should be serialized as part of the `Representation` by `ReprUtil`, takes a String argument: `restorer`.
This can be used to reference the `RepresentationRestorer` that should be used by `ReprUtil` to restore the field's value from its representation.

The annotation supports special syntax for enabling more use cases.
We explain these in this section.

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
This is because `StandaloneRepresentable` objects can always be restored without external information as they must implement a constructor that only takes in a `Representation`.

### Combination With Composite Types

For fields of some composite type, but where the entries of the data structure are of some primitive type or `StandaloneRepresentable` (such that usually no restorer would be necessary), you will need to give a restorer to indicate the composite type.

Let's look at, for example, an array of `Integer`s. The `Integer` entries do not require a restorer, but you need to use `[]` to indicate the array type.
In this case, you can use a placeholder restorer string to indicate the `Integer` entry. 
In the case of an array of `Integer`s, this may look like `@Represented(restorer = "[foo]")`.
You do not need to give a restorer corresponding to the `foo` identifier; `ReprUtil` will recognise that no restorer is necessary during deserialization and ignore the `foo`.

## Restorer Fields

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

In the example on restorer fields, we stored the group directly and could therefore refer to it in the restorer string.
Here, the groups are stored within the bilinear group and accessible via the `getGX()` methods provided by the `BilinearGroup` interface.
To make it easier to access these, the restorer string supports a method notation which gives a method for the `ReprUtil` class to call during deserialization.

In the example above, `ReprUtil` first deserializes the bilinear group and then uses its `getGX()` method to obtain the corresponding groups which can restore each group element.
