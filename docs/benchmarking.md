---
title: Benchmarking and Group Operation Counting
toc: true
mathjax: true
---

In this document we discuss your options when it comes to benchmarking code written using Cryptimeleon libraries as well as group operation counting provided by Cryptimeleon Math.

# Runtime Benchmarking

## Lazy Eval

While useful for automatic optimization, the [lazy evaluation]({% link docs/lazy-eval.md %}) features of Math can create some benchmarking problems if not handled correctly.

Let's take for example a signature scheme. 
During setup for your verification benchmark, you will probably execute the signing algorithm.
If evaluation is deferred until later, group operations done during signing will only be executed once the result is needed during verification of your signature.
This will obviously falsify your results for the verification benchmark.

Therefore, you should make sure to compute all group operations via any of the methods that force a blocking evaluation of the `LazyGroupElement` instance, for example using `computeSync()`.

## Micro-Benchmarking

If you care about accuracy, we recommend using a micro-benchmarking framework such as [JMH](https://openjdk.java.net/projects/code-tools/jmh/).
We also strongly recommend working through the [JMH Samples](https://hg.openjdk.java.net/code-tools/jmh/file/tip/jmh-samples/src/main/java/org/openjdk/jmh/samples/) to make sure you avoid any bad practices that could potentially invalidate your benchmarks.

[Our own benchmarks](https://github.com/cryptimeleon/benchmark) use JMH.
Since JMH is made to be used with Maven, you will probably want to add a Gradle task for executing your JMH tests (if you use Gradle).

```groovy
task jmh(type: JavaExec) {
    description = "This task runs JMH benchmarks"
    classpath = sourceSets.jmh.runtimeClasspath
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
Above is the script we use for our Cryptimeleon Benchmark project.
It allows us to use certain JMH parameters in addition to just running all tests contained in the `jmh` source set.

# Group Operation Counting

Cryptimeleon Math includes capabilities for group operation counting.
Specifically, it allows for tracking group inversions, squarings, operations, as well as (multi-)exponentiations for a specific group.

## CountingGroup

The functionality of group operation counting is provided by using a special group, the `CountingGroup`.

*Note: Keep in mind that `CountingGroup` uses \\(\mathbb{Z}_n\\) under the hood, and so is only to be used when testing and/or counting group operations, not for other performance benchmarks or even production code.*

```java
import org.cryptimeleon.math.pairings.debug.count.CountingGroup;

// instantiate the counting group with a name and its size
CountingGroup countingGroup = new CountingGroup("CG1", 1000000);

// Get a random non-neutral element and square it
GroupElement elem = countingGroup.getUniformlyRandomNonNeutral();
elem.op(elem).compute();

// Print number of squarings in group
System.out.println(countingGroup.getNumSquaringsTotal());
```
```
1
```

As seen above, `CountingGroup` provides the same interfaces as any other group in Math does, just with some additional features.

Whenever a group operation is performed, `CountingGroup` tracks it internally.
The user can access the data via a variety of methods.
These methods for data access can be separated in two categories:
Methods whose names end in `Total` and ones whose names end in `NoExpMultiExp`.
The former includes all group operations, even the ones done in (multi-)exponentiation algorithms while `NoExpMultiExp` methods only retrieve operation counts of operations done *not* in (multi-)exponentiations.
This is useful if you want to track (multi-)exponentiations only as a single unit and not the underlying group operations.
That data can be accessed via the `getNumExps()` and `getMultiExpTermNumbers()` methods, where the latter returns an array containing the number of bases in each multi-exponentiation done.

Additionally, `resetCounters()` can be used to reset all operation counters, and `formatCounterData()` provides a printable string that summarizes all collected data.

```java
CountingGroup countingGroup = new CountingGroup("CG1", 1000000);
GroupElement elem = countingGroup.getUniformlyRandomNonNeutral();
GroupElement elem2 = countingGroup.getUniformlyRandomNonNeutral();
GroupElement elem3 = countingGroup.getUniformlyRandomNonNeutral();
GroupElement elem4 = countingGroup.getUniformlyRandomNonNeutral();

// Perform a multi-exponentiation with 4 bases
elem.pow(10).op(elem2.pow(10)).op(elem3.pow(10)).op(elem4.pow(10)).compute();
// An exponentiation
elem.pow(10).compute();
// Squaring, group op and inversion
elem.op(elem).op(elem2).inv().compute();

System.out.println(countingGroup.formatCounterData());
```
```
------- Operation data for CountingGroup(Lazy CG1;Lazy CG1) -------
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

`CountingGroup` does use lazy evaluation, meaning that `compute()` calls are necessary before retrieving tracked operation data, else the operation might have not been executed yet.
However, `compute()` has been changed to behave like `computeSync()` in that it blocks until the computation is done.
This is because non-blocking computation can lead to race conditions when printing the result of tracking the group operations, i.e. the computation has not been performed yet when the data is printed.
So make sure to always call `compute()` on every `CountingGroupElement` before accessing any counter data.

### Serialization Tracking
`CountingGroup` not only allows for tracking group operations, it also counts how many calls of `getRepresentation()` have been called on elements of the group. This has the purpose of allowing you to track serializations.
The count is accessible via `getNumRetrievedRepresentations()`.

## CountingBilinearGroup

Cryptimeleon Math also provides a `BilinearGroup` implementation that can be used for counting, the `CountingBilinearGroup` class. 
It uses a simple (not secure) \\(\mathbb{Z}_n\\) pairing.

In addition to the usual group operation counting done by the three `CountingGroup` instances contained in the bilinear group, `CountingBilinearGroup` also allows you to track number of pairings performed.

```java
CountingBilinearGroup bilGroup = new CountingBilinearGroup(100);
// Get G1 and G2 of the bilinear group
CountingGroup groupG1 = (CountingGroup) bilGroup.getG1();
CountingGroup groupG2 = (CountingGroup) bilGroup.getG2();

GroupElement elemG1 = groupG1.getUniformlyRandomNonNeutral();
GroupElement elemG2 = groupG2.getUniformlyRandomNonNeutral();

// Compute a paring
bilGroup.getBilinearMap().apply(elemG1, elemG2).compute();

System.out.println(bilGroup.getNumPairings());
```
```
1
```