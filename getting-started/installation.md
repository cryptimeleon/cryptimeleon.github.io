---
title: Installation
toc: true
---

To make use of any of the Cryptimeleon libraries, you need at least Java SDK version 8.

# Library Installation

Here, we show you how to add any of the libraries as a dependency such that you can use them in your own project. 
This process depends on your project structure and dependency management; therefore, we have instructions for each of the popular build tools such as Gradle and Maven. 

We assume that you are familiar with the dependency management of your build tool.

## Maven
For adding for example Craco 1.0.0 to your project, add this dependency:

```xml
<dependency>
    <groupId>org.cryptimeleon</groupId>
    <artifactId>craco</artifactId>
    <version>1.0.0</version>
</dependency>
```

The `groupId` is common to all Cryptimeleon libraries.
Adjust the `artifactId` to the library you want to add as a dependency.
It generally corresponds to the library's name, i.e. the name of the repository.

If you want to use the mclwrap library, you also need to [install the MCL java bindings](#mclwrap-installation).

## Gradle

We asssume you have set up a Gradle project with a `build.gradle` file.
The libraries are hosted on Maven Central.
Therefore, you need to add `mavenCentral()` to the `repositories` section of your `build.gradle` file.

Then, you need to decide which library you want to use. Once you have decided, you need to add it as a dependency.
For example, for Craco version 1.0.0, you would add `implementation group: 'org.cryptimeleon', name: 'craco', version: '1.0.0'`
to the `dependencies` section in the `build.gradle` file.
The group id is common to all Cryptimeleon libraries.
The name of the library generally corresponds to the name of the repository.

If you want to use the mclwrap library, you also need to [install the MCL java bindings](#mclwrap-installation).

# Mclwrap Installation

For benchmarking you will probably want to use an efficient cryptographic pairing implementation. 
The Cryptimeleon Math library does provide a selection of pairings, but these are orders of magnitude less efficient than other, more optimized implementations.

An efficient pairing implementation is provided by our wrapper around the [MCL library's](https://github.com/herumi/mcl) implementation of the BN254 curve. 
This wrapper is provided by the Cryptimeleon Mclwrap library. 

To use the MCL wrapper library in your project, you need to install the Java bindings for MCL.
See [here](https://github.com/cryptimeleon/mclwrap/blob/master/README.md) for installation instructions.
