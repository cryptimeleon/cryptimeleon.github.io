---
title: ElGamal Implementation Tutorial
mathjax: true
tpc: true
---

In this document, we show how to use the Cryptimeleon Craco and Cryptimeleon Math library to implement an example scheme, the Elgamal encryption scheme [Elg85].
Compared to the other tutorials, we also aim to showcase the class structure for a full implementation (as opposed to "just" a toy implementation).

First, let's review how ElGamal encryption works:

**\\(\\operatorname{Setup}\\)**: 
The public parameters for this scheme consist of (1) a cyclic group \\(G\\) of prime order \\(p\\), and (2) a random generator \\(g\\leftarrow G\\setminus\\{1\\}\\).

**\\(\\operatorname{KeyGen}\\)**: 

1. Choose a random secret key \\(sk \\leftarrow \\{0, 1, \dots, p-1\\}\\).
2. Compute the corresponding public key \\(pk = g^{sk}\\)

**\\(\\operatorname{Encryption}(pk, m)\\)**: 

1. Choose a random exponent \\(r \\leftarrow\\{0, 1, \dots, p-1\\}\\).
2. The ciphertext is \\(c = (c_1, c_2) = (g^r, {pk}^r\\cdot m)\\).

**\\(\\operatorname{Decryption}(sk, c=(c_1, c_2))\\)**:

1. Decryption computes \\(m = c_2 \\cdot c_1^{-sk}\\).

Decryption works because \\(c_1^{-sk} = (g^r)^{-sk} = (g^{sk})^{-r} = (pk)^{-r}\\) cancels out the \\(pk^r\\) term in \\(c_2\\).

## Basic implementation of ElGamal
The operations outlined above can be quite directly transferred into Cryptimeleon.

```java
public class ElGamalEncryptionScheme {
    protected Group group;
    protected GroupElement g;

    public ElGamalEncryptionScheme(Group group) {
        this.group = group;
        this.g = group.getUniformlyRandomNonNeutral();
    }

    public Zn.ZnElement generateSecretKey() {
        return group.getUniformlyRandomExponent();
    }

    public GroupElement computePublicKey(Zn.ZnElement secretKey) {
        return g.pow(secretKey);
    }

    public GroupElementVector encrypt(GroupElement plaintext, GroupElement publicKey) {
        var r = group.getUniformlyRandomExponent();
        return Vector.of(g.pow(r), publicKey.pow(r).op(plaintext));
    }

    public GroupElement decrypt(GroupElementVector ciphertext, Zn.ZnElement secretKey) {
        return ciphertext.get(0).pow(secretKey.neg()).op(ciphertext.get(1));
    }
}
```

The whole scheme can then be tested as follows:
```java
public static void main(String[] args) {
    Group group = new Secp256k1();
    var scheme = new ElGamalEncryptionScheme(group);
    var secretKey = scheme.generateSecretKey();
    var publicKey = scheme.computePublicKey(secretKey);
    var plaintext = group.getUniformlyRandomElement();
    var ciphertext = scheme.encrypt(plaintext, publicKey);
    var plaintextRestored = scheme.decrypt(ciphertext, secretKey);
    if (plaintextRestored.equals(plaintext))
        System.out.println("Correctly decrypted plaintext "+plaintext);
}
```

## Implementing the Scheme fully with data classes and interfaces
Even though the implementation above can be considered complete, you may want to properly encapsulate the artifacts (keys, ciphertexts, etc.) into corresponding data classes. 
For a simple construction such as ElGamal, this is a somewhat useless exercise. However, for larger constructions with more complicated key structures, this step makes a lot of sense.
For this reason, we showcase this step here.

To follow along, check out [our Java demo project](https://github.com/cryptimeleon/java-demo) and create a new class `ElGamalEncryptionScheme` as outlined above. 

To represent the different parts of the scheme, we start off by creating some classes.

The `ElgamalEncryptionScheme` class houses the different algorithms that are part of the scheme such as encryption and key generation. Let's have it implement the existing `AsymmetricEncryptionScheme` interface contained in the Craco library:

```java
public class ElgamalEncryptionScheme implements AsymmetricEncryptionScheme {
}
```

This interface – together with `EncryptionScheme` – contains the methods required for an asymmetric encryption scheme already: `generateKeyPair()`, `encrypt()` and `decrypt()`, as well as some methods for working with representations, more on those later.

Next, lets create classses for the secret and public key, `ElgamalSecretKey` and `ElgamalPublicKey`, implementing the `DecryptionKey` and `EncryptionKey` interfaces included in Craco, respectively.

```java
// ElgamalSecretKey.java
public class ElgamalSecretKey implements DecryptionKey {
}

// ElgamalPublicKey.java
public class ElgamalPublicKey implements EncryptionKey {
}
```

Lastly, some classes for the ciphertext and plaintext/message:

```java
// ElgamalPlainText.java
public class ElgamalPlainText implements PlainText {
}

// ElgamalCipherText.java
public class ElgamalCipherText implements CipherText {
}
```

The plaintext is a group element, so lets add that to the class.

```java
public class ElgamalPlainText implements PlainText {
    private GroupElement plaintext; // GroupElement class contained in the math library
    
    public ElGamalPlainText(GroupElement plaintext) {
        this.plaintext = plaintext;
    }
    
    public GroupElement getPlaintext() {
        return plaintext;
    }
}
```

The ciphertext consists of two group elements, \\(c_1\\) and \\(c_2\\):

```java
// ElgamalCipherText.java
public class ElgamalCipherText implements CipherText {
    private GroupElement c1;
    private GroupElement c2;

    public ElgamalCipherText(GroupElement c1, GroupElement c2) {
        this.c1 = c1;
        this.c2 = c2;
    }
    
    public GroupElement getC1() { return c1; }
    public GroupElement getC2() { return c2; }
}
```

Next, the public key, which consists of the group \\(G\\), the public group element \\(h = g^a\\), and the generator \\(g\\):

```java
public class ElgamalPublicKey implements EncryptionKey {
    private Group groupG;
    private GroupElement g;
    private GroupElement h;

    // Insert constructor and getters here.
}
```
(We leave out constructor and getters for succinctness.)

The secret key consists of the public key and the secret exponent \\(a\\):

```java
public class ElgamalSecretKey implements DecryptionKey {
    private ZnElement a;
    private ElgamalPublicKey publicKey;

    // Insert constructor and getters here.
}
```

With these classes, we can start to implement the algorithms in the `ElgamalEncryption` class. Its constructor takes in the group to use:

```java
public class ElgamalEncryptionScheme implements AsymmetricEncryptionScheme {
    private Group groupG; // Cyclic group with prime order q
    
    public ElgamalEncryption(Group groupG) { this.groupG = groupG; }
}
```


Key generation may then look like this:
```java
// ElgamalEncryptionScheme class
@Override
public KeyPair generateKeyPair() {
    Zn zn = new Zn(groupG.size()); // Zn = {0, 1, ..., groupG.size()-1}
    // Choose secret exponent a
    ZnElement a = zn.getUniformlyRandomElement()
    // Get a generator of the group, by prime order all non-neutral elements are generators
    GroupElement generator = groupG.getUniformlyRandomNonNeutral().compute();
    // Compute h = g^a, 
    GroupElement h = generator.pow(a).compute();
    
    // Create secret key
    ElgamalSecretKey secretKey = new ElgamalSecretKey(groupG, generator, a, g);
    // Get public key from secret key
    ElgamalPublicKey publicKey = secretKey.getPublicKey();

    return new KeyPair(publicKey, privateKey);
}
```
As you can see, we make use of a number of different classes provided by the Math library such
as `Group`, `GroupElement`, or `Zn` who provide many typical methods such as group operations or efficient exponentiation, meaning we only have to concern ourselves with the scheme itself.

Encryption is next:
```java
// ElgamalEncryptionScheme class
@Override
public CipherText encrypt(PlainText plainText, EncryptionKey publicKey) {
    if (!(publicKey instanceof ElgamalPublicKey))
        throw new IllegalArgumentException("The specified public key is not an Elgamal key.");
    if (!(plainText instanceof ElgamalPlainText))
        throw new IllegalArgumentException("The specified plaintext is not an Elgamal key.");

    GroupElement groupElementPlaintext = ((ElgamalPlainText) plainText).getPlaintext();
    GroupElement g = ((ElgamalPublicKey) publicKey).getG();
    GroupElement h = ((ElgamalPublicKey) publicKey).getH();

    Zn zn = new Zn(groupG.size());
    ZnElement r = zn.getUniformlyRandomElement();

    //c1 = g^r
    GroupElement c1 = g.pow(random);

    //c2 = h^r * plaintext
    GroupElement c2 = h.pow(random).op(groupElementPlaintext);

    return new ElgamalCipherText(c1.compute(), c2.compute());
}
```
There are a number of type checks and type casts in this method. This is because the `EncryptionScheme` interface we implement by implementing `AsymmetricEncryptionScheme` does not know about our specific classes, instead it uses the general `PlainText`, `CipherText`, and `EncryptionKey` classes.

Decryption works similarly:
```java
// ElgamalEncryptionScheme class
@Override
public PlainText decrypt(CipherText cipherText, DecryptionKey privateKey) {
    if (!(cipherText instanceof ElgamalCipherText))
        throw new IllegalArgumentException("The specified ciphertext is invalid.");
    if (!(privateKey instanceof ElgamalPrivateKey))
        throw new IllegalArgumentException("The specified private key is invalid.");

    ElgamalCipherText cpCipherText = (ElgamalCipherText) cipherText;
    ZnElement a = ((ElgamalPrivateKey) privateKey).getA();
    GroupElement u = cpCipherText.getC1().pow(a);
    GroupElement m = u.inv().op(cpCipherText.getC2()); // m = c_2 * c_1^a
    return new ElgamalPlainText(m.compute());
}
```

## Representation

You might have noticed that the `EncryptionScheme` requires more than just the methods implemented so far.
These methods, e.g. `restorePlainText()` all take a `Representation` object as argument. Representations act as an intermediate format between the actual object and java serialization. Once you have created a representation of an object, you can use one of the converter classes to serialize it to, for example, JSON or binary.

The `restorePlainText()` takes a representation of a plaintext and should return the corresponding plaintext. The other methods work similarly. Before we can implement these, however, we need to add representation support to the Elgamal classes created earlier.

We don't give a detailed walkthrough for that here, the [representations documentation]({% link docs/representations.md %}) should allow you to implement it on your own for the four classes that require it: `ElgamalPublicKey`, `ElgamalSecretKey`, `ElgamalPlainText`, and `ElgamalCipherText`.

For `ElgamalCipherText`, it may look as follows:

```java
public class ElgamalCipherText implements CipherText {
    @Represented(restorer = "G")
    private GroupElement c1;

    @Represented(restorer = "G")
    private GroupElement c2;

    public ElgamalCipherText(Representation representation, Group group) {
        new ReprUtil(this).register(group, "G"), deserialize(repr);
    }

    @Override
    public Representation getRepresentation() {
        return ReprUtil.serialize(this);
    }

    // other methods we added previously
}
```

With this, implementing e.g. the aforementioned `restoreCipherText` method is simple:

```java
// ElgamalEncryptionScheme class
@Override
public ElgamalCipherText restoreCipherText(Representation repr) {
    return new ElgamalCipherText(repr, groupG);
}
```

Now, only one thing is missing: The `ElgamalEncryptionScheme` class implements `AsymmetricEncryptionScheme` which indirectly extends the `StandaloneRepresentable` interface. So we need to add a constructor taking a `Representation` object and instantiates a `ElgamalEncryptionScheme` object with the correct group (more on `StandaloneRepresentable` in the [representations documentation]({% link docs/representations.md %}).

Thankfully, this is easy:

```java
public class ElgamalEncryptionScheme implements AsymmetricEncryptionScheme {
    @Represented
    private Group groupG;

    public ElgamalEncryptionScheme(Representation repr) {
        new ReprUtil(this).deserialize(repr);
    }

    @Override
    public Representation getRepresentation() {
        return ReprUtil.serialize(this);
    }

    // other methods we added previously
}
```
The `Group` class is itself a `StandaloneRepresentable`, so we just delegate the representation to it.

The only thing missing now is implementing `equals()` and `hashCode()` methods. We sketch our usual approach:

```java

public boolean equals(Object other) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;
    // Now convert "other" to the right type and check attribute equality via "Objects.equals()"
}

public int hashCode() {
    // Use "Objects.hash()" for simplicity
}
```

Using `Objects.equals()` and `Objects.hash()` is the easiest way to do this. The class check if-condition in the `equals()` method (instead of an `instanceof`) is important since it ensures symmetry of the equals relation in case you ever implement a subclass.

# References

[Elg85] T. Elgamal, "A public key cryptosystem and a signature scheme based on discrete logarithms," in *IEEE Transactions on Information Theory*, vol. 31, no. 4, pp. 469-472, July 1985.
