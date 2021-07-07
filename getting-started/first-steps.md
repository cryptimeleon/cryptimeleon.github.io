---
title: First Steps
toc: true
---

# Project structure overview
Cryptimeleon is composed of several libraries.
![Overview of Cryptimeleon libraries](/assets/cryptimeleon_overview_parts.png)

## Base libraries
### Math
The [Math](https://github.com/cryptimeleon/math) library contains all the basics like bilinear groups, hashing, randomness generation, and serialization. 
It is the basis for every other Cryptimeleon library.

### Craco
[Craco](https://github.com/cryptimeleon/craco) (the name has historical reasons) implements various cryptographic primitives and low-level constructions. This includes reusable primitives such as accumulators, commitment schemes, signature and encryption schemes, Sigma protocols, and many more.

The goal of Craco is to provide common cryptographic schemes for use in more high-level protocols.

### Mclwrap
[Mclwrap](https://github.com/cryptimeleon/mclwrap) provides an efficient BN-254 bilinear group implementation (powered by [MCL](https://github.com/herumi/mcl)). 
You should definitely use this if you want to run timing benchmarks.

### Predenc, Groupsig
Implementations of various [predicate encryption schemes](https://github.com/cryptimeleon/predenc) and [group signature schemes](https://github.com/cryptimeleon/groupsig).

# Starting from scratch
If you don't have anything right now, it's easiest to get started with our template projects.

- [Java](https://github.com/cryptimeleon/java-demo)
- [Android](https://github.com/cryptimeleon/android-demo)

If you want to use Zero-knowledge proofs, you can generate a basic project containing your protocol with [subzero](https://cptml.org/subzero).

# Including our libraries into your existing project
Our libraries are hosted on Maven Central. 
For the sake of this, we assume you want to import Math and Craco (which is usually what you need).

## Maven
Add these dependencies to your `pom.xml`:

```xml
<dependency>
    <groupId>org.cryptimeleon</groupId>
    <artifactId>math</artifactId>
    <version>{{site.mathversion}}</version>
</dependency>
<dependency>
    <groupId>org.cryptimeleon</groupId>
    <artifactId>craco</artifactId>
    <version>{{site.cracoversion}}</version>
</dependency>
```

## Gradle
Add these entries to your `build.gradle`.

```gradle
plugins {
  id 'java-library'
}

repositories {
  mavenCentral()
}

dependencies {
  implementation 'org.cryptimeleon:math:{{site.mathversion}}'
  implementation 'org.cryptimeleon:craco:{{site.cracoversion}}'
}
```

# Mclwrap Installation
Eventually, you should probably install [mclwrap](https://github.com/herumi/mcl) because it is a _much_ more efficient bilinear group than [what is available](/docs/bilinear-groups.html) in the Math library by default.

To use MCL in your project, you need to (1) compile and install MCL, and then (2) add the dependency to our the Java bindings.
This process is explained [here](https://github.com/cryptimeleon/mclwrap/blob/main/README.md).
