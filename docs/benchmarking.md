---
title: Benchmarking and Group Operation Counting
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

# Collecting Applied Metrics

Applied metrics, such as runtime or memory usage, can be collected using any existing Java benchmark framework.
An example of such a framework is the Java Microbenchmarking Harness (JMH). 
It allows for very accurate measurements and integrates with many existing profilers.
Due to these existing options, we have decided against implementing any such capabilities ourselves.
Therefore, you will need to use one of these existing benchmark frameworks.

## Problems That Can Falsify Your Benchmarks

We now want to look at some potential problems when creating a benchmark.
We will illustrate these problems using the example of benchmarking the verification algorithm of a signature scheme.

### Lazy Evaluation

While useful for automatic optimization, the [lazy evaluation]({% link docs/lazy-eval.md %}) features of Math can create some benchmarking problems if not handled correctly.
To benchmark your verification algorithm, you will need valid signatures, and these signatures will be provided by executing the signing algorithm.
Inside the signing algorithm group operations might be executed.
By default, group operations in Cryptimeleon Math are evaluated lazily, i.e. deferred until needed.
Therefore, group operations done during signing will only be executed once the result is needed during verification of your signature.
This will increase the runtime of your verification algorithm and therefore falsify the results.
By serializing the `Signature` object using the `getRepresentation()` method *before* running verification, you can force all remaining computations involving fields of the `Signature` object to be completed in a blocking manner.

### Mutability

Another problem is the mutability of the `Signature` object.
When repeatedly verifying the same `Signature` object, it may be possible that executing the verification algorithm leads to certain optimizations that change the runtime of the verification for the succeeding verification runs.
An example of this problem is the storing of *precomputations*.
The `Signature` object will most likely contain group elements.
Those group elements can store precomputations which help to make future exponentiations more efficient.
The first run of your verification may create such precomputations that can then be used in future invocations of the verification algorithm.
These latter runs will then run faster than the first one, leading to skewed results.

The underlying problem here is the mutability of the `Signature` object and the reuse of it for multiple runs of the verification algorithm.
Therefore, the solution is to recreate the `Signature` object for each invocation of the verification algorithm.
This can be done using our [representation framework]({% link docs/representations.md %}).
By serializing and then deserializing it for each invocation of the verification algorithm, you obtain a fresh `Signature` object each time with the same state as before serialization.

## JMH Example

As an example we look at how to use JMH to measure runtime for our implementation of the verification algorithm of the signature scheme from Section 4.2 of Pointcheval and Sanders [PS18].
Here we will also see how to implement the mitigations for the benchmarking problems discussed in the previous section.

Given the public key $$\textsf{pk} = (\tilde{g}, \tilde{X}, \tilde{Y}_1, \dots, \tilde{Y}_{r+1})$$, the message vector $$\textbf{m} = (m_1, \dots, m_r)$$, and the signature $$\sigma = (m', \sigma_1, \sigma_2)$$, the verification algorithm works as follows:
Check whether $$\sigma_1$$ is the multiplicative identity of $$\mathbb{G}_1$$ and output $$0$$ if yes.
Lastly, output $$1$$ if $$e(\sigma_1, \tilde{X} \cdot \prod_{j = 1}^r{\tilde{Y}_j^{m_j} \cdot \tilde{Y}_{r+1}^{m'}}) = e(\sigma_2, \tilde{g})$$ holds, and $$0$$ if not.
Here $$e$$ denotes the pairing operation.

We test the verification operation using messages of length one and of length 10.
```java
@State(Scope.Thread)
public class PS18VerifyBenchmark {
	
    // Test with one message and ten
    @Param({"1", "10"})
    int numMessages;
	
    PS18SignatureScheme scheme;
    PlainText plainText;
    Representation signatureRepr;
    Representation verifyKeyRepr;
	
    // The setup method that creates the signature and verification key 
    //  used by the verify benchmark
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
        // Computations in sign and/or key gen may be done non-blocking.
        // To make sure these are not done as part of the verification benchmark, 
        //  we force the remaining computations to be done blocking via getRepresentation()
        signatureRepr = signature.getRepresentation();
        verifyKeyRepr = verificationKey.getRepresentation();
    }
	
    // The benchmark method. Includes settings for JMH
    @Benchmark
    @BenchmarkMode(Mode.SingleShotTime)
    @Warmup(iterations = 3, batchSize = 1)
    @Measurement(iterations = 10, batchSize = 1)
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
}
```

JMH outputs the following results for the above benchmark (using an i5-4210m on Ubuntu 20.04):

|Benchmark           |               numMessages|  Mode|  Cnt | Score |  Error|  Units |
|-------------------|---------------------------|--------|----|-------|--------|-------|
|measureVerify     |         1 |   ss |  50 | 5.263 |$$\pm$$ 0.641 | ms/op |
|measureVerify     |        10 |   ss |  50|  8.157 |$$\pm$$ 1.506 | ms/op|

The above example is also part of our [Benchmark](https://github.com/cryptimeleon/benchmark) project.
There you can find more examples like it.

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

# Group Operation Counting

The collection of hardware-independent metrics such as group operations is implemented by the Cryptimeleon Math library.
The main points of interest here are the `DebugBilinearGroup` and `DebugGroup` classes.
The former allows for counting pairings, and the latter allows for counting group operations, group squarings (relevant for elliptic curves), group inversions, exponentiations, and multi-exponentiations.
It is also able to track the number of times group elements have been serialized.

## DebugGroup

The functionality of group operation counting is provided by using a special group, the `DebugGroup`.
By simply using the `DebugGroup` to perform the computations, it automatically counts the operations done within it.

*Note: Keep in mind that `DebugGroup` uses $$\mathbb{Z}_n$$ under the hood and is way faster than any secure group, and so is only to be used when testing and/or counting group operations, not for other performance benchmarks.*

```java
import org.cryptimeleon.math.structures.groups.debug.DebugGroup;

// Instantiate the debug group with a name and its size
DebugGroup debugGroup = new DebugGroup("DG1", 1000000);

// Get a random non-neutral element and square it
GroupElement elem = debugGroup.getUniformlyRandomNonNeutral();
elem.op(elem).compute();

// Print number of squarings in group
System.out.println(debugGroup.getNumSquaringsTotal());
```
```
1
```

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
Instead, it counts the group operations, inversions, and squarings that are part of evaluating the multi-exponentiation (using a wNAF-type algorithm).
Combining these metrics gives us therefore a more complete picture of the computational costs.

A more detailed (code) example is given below:

```java
DebugGroup debugGroup = new DebugGroup("DG1", 1000000);
GroupElement elem = debugGroup.getUniformlyRandomNonNeutral();
GroupElement elem2 = debugGroup.getUniformlyRandomNonNeutral();
GroupElement elem3 = debugGroup.getUniformlyRandomNonNeutral();
GroupElement elem4 = debugGroup.getUniformlyRandomNonNeutral();

// Perform a multi-exponentiation with 4 bases
elem.pow(10).op(elem2.pow(10)).op(elem3.pow(10)).op(elem4.pow(10)).compute();
// An exponentiation
elem.pow(10).compute();
// Squaring, group op and inversion
elem.op(elem).op(elem2).inv().compute();

// Print summary of all data
System.out.println(debugGroup.formatCounterData());
```
```
------- Operation data for DebugGroup(Lazy DG1;Lazy DG1) -------
----- Total group operation data: -----
    Number of Group Operations: 34
    Number of Group Inversions: 1
    Number of Group Squarings: 9
----- Group operation data without operations done in (multi-)exp algorithms: -----
    Number of Group Operations: 1
    Number of Group Inversions: 1
    Number of Group Squarings: 1
----- Other data: -----
    Number of exponentiations: 1
    Number of terms in each multi-exponentiation: [4]
    Number of retrieved representations (via getRepresentation()): 0
```

As you can see, the "Total group operation data" block has much higher numbers than the block below it, due to counting operations done during the multi-exponentiation and exponentiation.

### Lazy Evaluation

`DebugGroup` does use lazy evaluation, meaning that you need to ensure all lazy computations have finished before retrieving the tracked results.
One way to do this is to call `computeSync()` on all operations.
However, for your convenience, `DebugGroup` also overrides `compute()` to behave like `computeSync()` in that it blocks until the computation is done.
So make sure to always call `compute()` on every involved `DebugGroupElement` before accessing any counter data, or call `getRepresentation()` to serialize any involved objects as this also leads to a blocking computation.

### Configuring Used (Multi-)exponentiation Algorithm

`DebugGroup` makes use of efficient exponentiation and multi-exponentiation algorithms.
The exact algorithm used changes the resulting group operation counts.
To manually configure these algorithms, `DebugGroup` (and `DebugBilinearGroup`) offers setter and getter methods such as `getSelectedMultiExpAlgorithm` and `setSelectedMultiExpAlgorithm`.
Furthermore, you can configure the precomputation and exponentiation window sizes used for those algorithms.
These are the same methods as offered by `LazyGroup`.

### Serialization Tracking
`DebugGroup` not only allows for tracking group operations, it also counts how many calls of `getRepresentation()` have been called on elements of the group. This has the purpose of allowing you to track serializations.
The count is accessible via `getNumRetrievedRepresentations()`.

## DebugBilinearGroup

Cryptimeleon Math also provides a `BilinearGroup` implementation that can be used for counting, the `DebugBilinearGroup` class. 
It uses a simple (not secure) $$\mathbb{Z}_n$$ pairing.

In addition to the usual group operation counting done by the three `DebugGroup` instances contained in the bilinear group, `DebugBilinearGroup` also allows you to track number of pairings performed.

```java
DebugBilinearGroup bilGroup = new DebugBilinearGroup(100);
// Get G1 and G2 of the bilinear group
DebugGroup groupG1 = (DebugGroup) bilGroup.getG1();
DebugGroup groupG2 = (DebugGroup) bilGroup.getG2();

GroupElement elemG1 = groupG1.getUniformlyRandomNonNeutral();
GroupElement elemG2 = groupG2.getUniformlyRandomNonNeutral();

// Compute a paring
bilGroup.getBilinearMap().apply(elemG1, elemG2).compute();

System.out.println(bilGroup.getNumPairings());
```
```
1
```


# References

[PS18] David Pointcheval and Olivier Sanders. “Reassessing Security of Randomizable Signatures”. In: Topic in Cryptology - CT-RSA 2018. Ed. by Nigel P. Smart. Springer International Publishing, 2018, pp 319-338.