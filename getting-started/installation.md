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
For adding for example the newest version of Craco and Math to your project, add this dependency:

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

The `groupId` is common to all Cryptimeleon libraries.
Adjust the `artifactId` to the library you want to add as a dependency.
It generally corresponds to the library's name, i.e. the name of the repository.

If you want to use the mclwrap library, you also need to [install the MCL java bindings](#mclwrap-installation).

## Gradle

We assume you have set up a Gradle project with a `build.gradle` file.
The libraries are hosted on Maven Central.

Example gradle file:
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

If you want to use the mclwrap library, you also need to [install the MCL java bindings](#mclwrap-installation).

# Mclwrap Installation

For a much more efficient bilinear group implementation, use our wrapper around the [MCL library](https://github.com/herumi/mcl)'s BN254 curve. 

To use the MCL wrapper library in your project, you need to (1) compile and install MCL, and then (2) add the dependency to our the Java bindings.
This process is explained [here](https://github.com/cryptimeleon/mclwrap/blob/main/README.md).
