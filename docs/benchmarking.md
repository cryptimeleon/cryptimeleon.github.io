---
title: Benchmarking and group operation counting
toc: true
mathjax: true
---

In this document we discuss your options when it comes to benchmarking code written using Cryptimeleon libraries.

There are many different kinds of possible performance metrics.
These include runtime in the form of CPU cycles or CPU time, memory usage, and network usage.
Furthermore, one may want to collect hardware-independent information such as the number of group operations or pairings.
Both of these types of metrics have their use-cases.
Counting group operations and pairings has the advantage of being hardware-independent.
To the layperson and potential user, applied metrics such as CPU time or memory usage can be more meaningful as they demonstrate practicality better than the more abstract group operations metrics.

# Collecting applied metrics

Applied metrics, such as runtime or memory usage, can be collected using any existing Java benchmark framework.
An example of such a framework is the Java Microbenchmarking Harness (JMH). 
It allows for very accurate measurements and integrates with many existing profilers.
Due to these existing options, we have decided against implementing any such capabilities ourselves.
Therefore, you will need to use one of these existing benchmark frameworks.

## JMH example

As an example we look at how to use JMH to measure runtime for our implementation of the verification algorithm of the signature scheme from Section 4.2 of Pointcheval and Sanders [PS18].
Here we will also see how to implement the mitigations for the benchmarking problems discussed in the previous section.

Given the public key $$\textsf{pk} = (\tilde{g}, \tilde{X}, \tilde{Y}_1, \dots, \tilde{Y}_{r+1})$$, the message vector $$\textbf{m} = (m_1, \dots, m_r)$$, and the signature $$\sigma = (m', \sigma_1, \sigma_2)$$, the verification algorithm works as follows:
Check whether $$\sigma_1$$ is the multiplicative identity of $$\mathbb{G}_1$$ and output $$0$$ if yes.
Lastly, output $$1$$ if $$e(\sigma_1, \tilde{X} \cdot \prod_{j = 1}^r{\tilde{Y}_j^{m_j} \cdot \tilde{Y}_{r+1}^{m'}}) = e(\sigma_2, \tilde{g})$$ holds, and $$0$$ if not.
Here $$e$$ denotes the pairing operation.

We test the verification operation using messages of length one and of length 10.
The below code measures verification as follows:
For each iteration, a new signature and verification key are generated.
Then the verification of these is measured once.
This process makes up one iteration.
The results of all the iterations are then combined by JMH.
```java
@State(Scope.Thread)
public class PS18VerifyBenchmark {
	
    // Test with one message and ten
    @Param({"1", "10"})
    int numMessages;
	
    PS18SignatureScheme scheme;
    PlainText plainText;
    Signature signature;
    VerificationKey verificationKey;
	
    // The setup method that creates the signature and verification key 
    //  used by the verify benchmark.
    // Level.Iteration tells us that it is run before each new iteration 
    //  (an iteration consists of a sequence of invocations of the benchmark method; see sample 06 of the 
    //   JMH samples we link at the end of this section)
    @Setup(Level.Iteration)
    public void setup() {
        PSPublicParameters pp = new PSPublicParameters(new MclBilinearGroup());
        scheme = new PS18SignatureScheme(pp);
        SignatureKeyPair<? extends PS18VerificationKey, ? extends PS18SigningKey> keyPair =
                scheme.generateKeyPair(numMessages);
        RingElementPlainText[] messages = new RingElementPlainText[numMessages];
        for (int i = 0; i < messages.length; i++) {
            messages[i] = new RingElementPlainText(pp.getZp().getUniformlyRandomElement());
        }
        plainText = new MessageBlock(messages);
        signature = scheme.sign(plainText, keyPair.getSigningKey());
        verificationKey = keyPair.getVerificationKey();
    }
	
    // The benchmark method. Includes settings for JMH
    @Benchmark
    @BenchmarkMode(Mode.SingleShotTime) // method is called once per iteration
    @Warmup(iterations = 3, batchSize = 1)
    @Measurement(iterations = 10, batchSize = 1)
    @OutputTimeUnit(TimeUnit.MILLISECONDS)
    public Boolean measureVerify() {
        return scheme.verify(plainText, signature, verificationKey);
    }
}
```

If you want to use JMH, we strongly recommend working through the [JMH Samples](https://hg.openjdk.java.net/code-tools/jmh/file/tip/jmh-samples/src/main/java/org/openjdk/jmh/samples/) to make sure you avoid any bad practices that could potentially invalidate your benchmarks.

## Using JMH with Gradle

Since JMH is made to be used with Maven, you will probably want to add a Gradle task for executing your JMH tests (if you use Gradle).
To run the JMH tests, you need to run JMH's `Main` class with the classpath set to the folder where your tests lie.
The code below gives an example Gradle task that can run JMH tests inside the `jmh` source set.
It also enables support for certain JMH parameters.
For example, using the `include` parameter you can explicitly state the test classes you want to run.

```groovy
task jmh(type: JavaExec) {
    description = "This task runs JMH benchmarks"
    // Run tests inside jmh source path
    classpath = sourceSets.jmh.runtimeClasspath
    // Need to run the JMH main class which collects and runs the tests
    main = "org.openjdk.jmh.Main" 

    def include = project.properties.get('include', '');
    def exclude = project.properties.get('exclude');
    def prof = project.properties.get('prof'); // allow adding a profiler
    def format = project.properties.get('format', 'json');
    def resultFile = file("build/reports/jmh/result.${format}")
    resultFile.parentFile.mkdirs()

    args include
    if (exclude) {
        args '-e', exclude
    }
    if (prof) {
        args '-prof', prof
    }
    args '-rf', format
    args '-rff', resultFile
}
```

For example, to execute the previous JMH example (and only it), you would run 
```bash
./gradlew -q jmh -Pinclude="PS18VerifyBenchmark"
```
inside the folder of your Gradle project.

## Potential problems with benchmarks

While being the most obvious approach, the verification benchmark we presented previously has some problems.
We will now discuss these problems and show to apply fixes for them to the example.

### Lazy evaluation

While useful for automatic optimization, the [lazy evaluation]({% link docs/lazy-eval.md %}) features of Math can create some benchmarking problems if not handled correctly.
To benchmark your verification algorithm, you will need valid signatures, and these signatures will be provided by executing the signing algorithm.
Inside the signing algorithm group operations might be executed.
By default, group operations in Cryptimeleon Math are evaluated lazily, i.e. deferred until needed.
Therefore, group operations done during signing will only be executed once the result is needed during verification of your signature.
Hence, when measuring runtime of the verification algorithm, we are actually also potentially measuring the deferred operations from the signature algorithm.
This will increase the runtime of your verification algorithm and therefore falsify the results.
By serializing the `Signature` object using the `getRepresentation()` method *before* the benchmark method, you can force all remaining computations involving fields of the `Signature` object to be completed in a blocking manner.

See below for how to apply this to our verification example:
```java
    @Setup(Level.Iteration)
    public void setup() {
        PSPublicParameters pp = new PSPublicParameters(new MclBilinearGroup());
        scheme = new PS18SignatureScheme(pp);
        SignatureKeyPair<? extends PS18VerificationKey, ? extends PS18SigningKey> keyPair =
                scheme.generateKeyPair(numMessages);
        RingElementPlainText[] messages = new RingElementPlainText[numMessages];
        for (int i = 0; i < messages.length; i++) {
            messages[i] = new RingElementPlainText(pp.getZp().getUniformlyRandomElement());
        }
        plainText = new MessageBlock(messages);
        signature = scheme.sign(plainText, keyPair.getSigningKey());
        verificationKey = keyPair.getVerificationKey();
        // We force the group elements making up signature and verificationKey to be fully computed
        //  such that the computation does not spill over into the benchmark method
        signature.getRepresentation();
        verificationKey.getRepresentation();
    }
```

### Optimizations stored in objects

Another problem is the reuse of the `Signature` object.
When repeatedly verifying the same `Signature` object, it may be possible that executing the verification algorithm leads to certain optimizations that change the runtime of the verification for the succeeding verification runs.
An example of this problem is the storing of *precomputations*.
The `Signature` object will most likely contain group elements.
Those group elements can store precomputations which help to make future exponentiations more efficient.
The first run of your verification may create such precomputations that can then be used in future invocations of the verification algorithm.
These latter runs will then run faster than the first one, leading to skewed results.

We have slightly changed the benchmark method from the JMH example to showcase this problem:
```java
    // The benchmark method. Includes settings for JMH
    @Benchmark
    @BenchmarkMode(Mode.SingleShotTime) // method is called once per iteration
    @Warmup(iterations = 3, batchSize = 5)
    @Measurement(iterations = 10, batchSize = 5)
    @OutputTimeUnit(TimeUnit.MILLISECONDS)
    public Boolean measureVerify() {
        return scheme.verify(plainText, signature, verificationKey);
    }
```
The `batchSize` inside the `@Warmup` and `@Measurement` annotations has been increased to `5`, meaning that, per iteration, five invocations of `measureVerify` are done.
In the first iteration, precomputations may be stored inside `signature` which can make the subsequent invocations more efficient.

The underlying problem here is the reuse of the `Signature` object for multiple runs of the verification algorithm.
Therefore, the solution is to recreate the `Signature` object for each invocation of the verification algorithm.
This can be done using our [representation framework]({% link docs/representations.md %}).
By serializing and then deserializing it for each invocation of the verification algorithm, you obtain a fresh `Signature` object each time with the same state as before serialization.

The improved benchmark method then looks as follows:
```java
    // New fields
    Representation signatureRepr;
    Representation verifyKeyRepr;

    @Setup(Level.Iteration)
    public void setup() {
        // ...
        signatureRepr = signature.getRepresentation();
        verifyKeyRepr = verificationKey.getRepresentation();
    }

    // The benchmark method. Includes settings for JMH
    @Benchmark
    @BenchmarkMode(Mode.SingleShotTime)
    @Warmup(iterations = 3, batchSize = 5)
    @Measurement(iterations = 10, batchSize = 5)
    @OutputTimeUnit(TimeUnit.MILLISECONDS)
    public Boolean measureVerify() {
        // Running the signing or key gen algorithms may have done precomputations
        //  for the verification key and/or signature.
        // To reset these precomputation such that they do not make the verification
        //  algorithm faster than it would be without, we recreate the objects
        //  without precomputations.
        signature = scheme.restoreSignature(signatureRepr);
        verificationKey = scheme.restoreVerificationKey(verifyKeyRepr);
        return scheme.verify(plainText, signature, verificationKey);
    }
```

Notice that we are also serializing and deserializing the verification key in the above example.
This represents the scenario where we are using a different verification key for each verification.
In another scenario we may be reusing the verification key, meaning that serializing and deserializing it before every verification would not be representative.

Therefore, make sure that the way you design the benchmark matches the scenario that you actually want to benchmark.

# Group operation counting

The collection of hardware-independent metrics such as group operations is implemented by the Cryptimeleon Math library.
The main points of interest here are the `DebugBilinearGroup` and `DebugGroup` classes.
The former allows for counting pairings, and the latter allows for counting group operations, group squarings (relevant for elliptic curves), group inversions, exponentiations, multi-exponentiations, as well as serializations of group elements via `getRepresentation()`.
It is also able to track the number of times group elements have been serialized.

*Note: Keep in mind that `DebugGroup` and `DebugBilinearGroup` use $$\mathbb{Z}_n$$ under the hood and is way faster than any secure group, and so is only to be used when testing and/or counting group operations, not for other performance benchmarks.*

```java
import org.cryptimeleon.math.structures.groups.debug.DebugGroup;

// Instantiate the debug group with a name and its size
DebugGroup debugGroup = new DebugGroup("DG1", 1000000);

// Get a random non-neutral element and square it
GroupElement elem = debugGroup.getUniformlyRandomNonNeutral();
elem.op(elem).compute();

// Print number of squarings in group
System.out.println(debugGroup.getNumSquaringsTotalDefault());
```
```
1
```

In the above example, we instantiate a `DebugGroup`, compute a squaring within it, and then use the `getNumSquaringsTotalDefault()` method to obtain the number of squarings done from the `DebugGroup` object (in this case one).
In this case we selected an arbitrary size for the `DebugGroup`, but in practice you should use the same size as the group you are replacing with `DebugGroup`.
The reason for that is that the number of operations done in exponentiation algorithms depends on the group's size.
Therefore, if the sizes do not match, the number of counted operations can be incorrect.

`DebugGroup` has a multitude of such getter methods for retrieving various operation statistics.
Their names all are constructed to the following structure:
The first part denotes the type of count the getter retrieves, in this case `getNumSquarings` and number of squarings done.
The second part denotes the *counting mode* (here `Total`) and the third, if present, relates to the bucket system (here `Default`).
`DebugBilinearGroup` has similar methods for retrieving pairing data.

Instead of using the getter methods, you can also use the provided `formatCounterData` methods which automatically format the count data for printing.
The `formatCounterData` methods of `DebugBilinearGroup` summarize the pairing data as well as the data of \\(G_1\\), \\(G_2\\) and \\(G_T\\). 

As seen in the previous example, `DebugGroup` does use lazy evaluation, meaning that you need to ensure all lazy computations have finished before retrieving the tracked results.
So make sure to always call `compute()` on every involved `DebugGroupElement` before accessing any counter data, or call `getRepresentation()` to serialize any involved objects as this also leads to a blocking computation.
For your convenience, `DebugGroup` also overrides `compute()` to behave like `computeSync()` in that it blocks until the computation is done.

## Do I need to keep reading?

In the following section, we will explain some of the more advanced feature of the counting system.
If your benchmark uses only a single `DebugGroup` and/or `DebugBilinearGroup` instance (specifically no interactive protocols), you may not need to know about those features.
In that case you can just use `DebugGroup` and `DebugBilinearGroup`, and then retrieve the data using the `formatCounterDataDefault()` formatting method.
If you want to use the getter methods with suffix `Default`, you should read at least the following section about counting modes to understand the difference between `Total` and `NoExpMultiExp` getter methods.
If your application uses multiple `DebugGroup` instances and/or multiple parties, reading the sections about static counting and the bucket system is recommended.

## Counting modes

The counting is done in two modes: The `NoExpMultiExp` mode and the `Total` mode.
Group operations metrics from the `NoExpMultiExp` mode disregard operations done inside (multi-)exponentiations while the `Total` mode does account for operations inside (multi-)exponentiations.
`NoExpMultiExp` measurements are therefore independent of the actual (multi-)exponentiation algorithm while `Total` measurements are more expressive in regards to the actual runtime (since estimating group operation runtime is easier than that of a (multi-)exponentiation).
This is useful if you want to track (multi-)exponentiations only as a single unit and not the underlying group operations.

Exponentiation and multi-exponentiation data can be accessed via the `getNumExps()` and `getMultiExpTermNumbers()` methods, where the latter returns an array containing the number of bases in each multi-exponentiation done.
Additionally, `resetCounters()` can be used to reset all operation counters, and `formatCounterData()` provides a printable string that summarizes all collected data.

As an example we consider the computation of $$g^a \cdot h^b$$.
The `NoExpMultiExp` mode counts this as a single multi-exponentiation with two terms.
No group operations are counted since they are all part of the multi-exponentiation.
The `Total` mode does not consider the multi-exponentiation as its own unit.
Instead, it counts the group operations, inversions, and squarings that are part of evaluating the multi-exponentiation (using a wNAF-type algorithm by default, but the algorithm used can be configured).
Combining these metrics gives us therefore a more complete picture of the computational costs.

Let's see the difference in action by performing an exponentiation and examining the number of operations done in both counting modes:

```java
DebugGroup debugGroup = new DebugGroup("DG1", 1000000);
GroupElement elem = debugGroup.getUniformlyRandomNonNeutral();
GroupElement elem2 = debugGroup.getUniformlyRandomNonNeutral();
GroupElement elem3 = debugGroup.getUniformlyRandomNonNeutral();
GroupElement elem4 = debugGroup.getUniformlyRandomNonNeutral();

// An exponentiation
elem.pow(10).compute();

System.out.println("Total ops: " + debugGroup.getNumOpsTotalDefault());
System.out.println("Ops not done in exp: " + debugGroup.getNumOpsNoExpMultiExpDefault());
```
```
Total ops: 8
Ops not done in exp: 0
```

As you can see, `debugGroup.getNumOpsNoExpMultiExpDefault()` returns `0`, while `debugGroup.getNumOpsTotalDefault()` returns `8`.
This is because the only group operations done are inside the exponentiation.

## Static counting

Counting in `DebugGroup` and `DebugBilinearGroup` is done statically, meaning that different instances of `DebugGroup` share their counts.

This is illustrated by the following example:

```java
DebugGroup debugGroup1 = new DebugGroup("DG1", 1000000);
GroupElement elem1 = debugGroup1.getUniformlyRandomNonNeutral();
DebugGroup debugGroup2 = new DebugGroup("DG2", 1000000);

elem1.op(elem1).compute();

System.out.println("DG1: " + debugGroup1.getNumSquaringsTotalDefault());
System.out.println("DG2: " + debugGroup2.getNumSquaringsTotalDefault());
```
```
DG1: 1
DG2: 1
```

Technically, the only squaring that is done is the one on `elem1` which is an element of `debugGroup1`.
Due to static counting, however, the squaring is also counted by `debugGroup2`.
This has the advantage that count data of operations done inside internal `DebugGroup` instances (internal in the sense of hidden inside the application and not accessible to the benchmarker) can be retrieved via any other `DebugGroup` instance.

This sharing of data does *not* apply to the `DebugGroup` instances exposed by `DebugBilinearGroup`'s `getG1()`, `getG2()`, and `getGT()` methods.
These all have their own shared count data pools.
Specifically, all instances of `DebugGroup` obtained via `getG1()` share their count data, and similarly for `getG2()` and `getGT()`.

We illustrate this via the following example:

```java
DebugGroup debugGroup = new DebugGroup("DG1", 1000000);
GroupElement elem = debugGroup.getUniformlyRandomNonNeutral();
DebugBilinearGroup debugBilinearGroup = new DebugBilinearGroup(BigInteger.valueOf(1000000), BilinearGroup.Type.TYPE_3);
DebugGroup bilinearG1 = (DebugGroup) debugBilinearGroup.getG1();
GroupElement elemG1 = bilinearG1.getUniformlyRandomNonNeutral();
DebugGroup bilinearG2 = (DebugGroup) debugBilinearGroup.getG2();

elem.op(elem).compute();
elemG1.op(elemG1).compute();
elemG1.op(elemG1).compute();

System.out.println("DG1: " + debugGroup.getNumSquaringsTotalDefault());
System.out.println("Bilinear G1: " + bilinearG1.getNumSquaringsTotalDefault());
System.out.println("Bilinear G2: " + bilinearG2.getNumSquaringsTotalDefault());
```
```
DG1: 1
Bilinear G1: 2
Bilinear G2: 0
```

As you can see, the squaring computed inside `debugGroup` is not counted by `bilinearG1` or `bilinearG2`.
The two squarings are only counted by `bilinearG1` and not the others.
The reason for this is that \\(G_1\\), \\(G_2\\) and \\(G_T\\) can have different costs for operations, and so it makes sense to count them separately.

To summarize: All `DebugGroup` instances obtained by directly instantiating them via the constructors of `DebugGroup` share their count data.
The `DebugGroup` instances obtained via `getG1()`, `getG2()`, and `getGT()` each have their own count data pools.
Keep in mind that `DebugGroup` instances obtained via the `getG1()` (or `getG2()` and `getGT()`) methods of different `DebugBilinearGroup` instances also share their count data.

## The bucket system

All the count data getter methods we used so far had the suffix `Default`.
This is related to the bucket system of `DebugGroup` and `DebugBilinearGroup`.
Due to the static counting, `DebugGroup` instances share their count data.
The bucket system allows different `DebugGroup` instances to count separately by using what we call "buckets".
Each bucket has its own count data tracking.
Using the `setBucket(String bucketName)` method on a `DebugGroup` instance, one can tell that `DebugGroup` instance to use the bucket with name `bucketName` for counting.
Any operations done on elements of that `DebugGroup` instance are counted inside the currently activated bucket of that instance.
This allows different `DebugGroup` instances to track their count data separately. 
The data of a specific bucket can be obtained using the getter methods that take a `String` argument such as `getNumOpsTotal(String bucketName)`.

After initialization, and before any calls to `setBucket`, a default bucket is used, whose data as we saw already can be obtained using the getter methods ending with the suffix `Default`.
This default bucket has no name, so you don't need to worry about conflicting names.
The getter methods ending with the suffix `AllBuckets` summarize the data across all buckets, including the default bucket.

```java
DebugGroup debugGroup = new DebugGroup("DG1", 1000000);
GroupElement elem = debugGroup.getUniformlyRandomNonNeutral();

elem.op(elem).compute();
debugGroup.setBucket("bucket1");
elem.op(elem).compute();

System.out.println("Default bucket: " + debugGroup.getNumSquaringsTotalDefault());
System.out.println("bucket1 bucket: " + debugGroup.getNumSquaringsTotal("bucket1"));
```
```
Default bucket: 1
bucket1 bucket: 1
```
In the above example, we do a squaring before calling `setBucket`, meaning that the squaring is counted by the default bucket.
We then switch `debugGroup` to the bucket `bucket1` which then counts the second squaring.
The printed results confirm this view, each bucket has one squaring.
Keep in mind that static counting still holds, so if you use the same bucket name for different `DebugGroup` instances, they will share the count data.
The bucket system also applies to `DebugBilinearPairing` and its pairing counter.

An example application of the bucket system is benchmarking an interactive protocol.
By using separate buckets for each of the participating parties, you can count operations per party.

## Configuring used (multi-)exponentiation algorithms

`DebugGroup` makes use of efficient exponentiation and multi-exponentiation algorithms.
The exact algorithm used changes the resulting group operation counts.
To manually configure these algorithms, `DebugGroup` (and `DebugBilinearGroup`) offers setter and getter methods such as `getSelectedMultiExpAlgorithm` and `setSelectedMultiExpAlgorithm`.
Furthermore, you can configure the precomputation and exponentiation window sizes used for those algorithms.
These are the same methods as offered by `LazyGroup`.

# References

[PS18] David Pointcheval and Olivier Sanders. “Reassessing Security of Randomizable Signatures”. In: Topic in Cryptology - CT-RSA 2018. Ed. by Nigel P. Smart. Springer International Publishing, 2018, pp 319-338.