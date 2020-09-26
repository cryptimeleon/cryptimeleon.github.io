---
title: Installation
toc: true
---

To make use of any of the **upb.crypto** libraries, you need at least Java SDK version 8.

# Library Installation

Here, we show you how to install any of the libraries for use in your own project. 
This process depends on your project structure and dependency management; therefore, we have manuals for each of the popular build tools such as Gradle and Maven. 

We assume that you are familiar with the dependency management of your build tool.

## Maven
Currently, the libraries are only available via the university nexus repository **outdated, not anymore**. 
This is a Maven repository available at `https://nexus.cs.upb.de/repository/sfb901-releases/`.

The group id of all the **upb.crypto** projects is `de.upb.crypto` and the artifact id corresponds to the name of the library you want to use. 
For example, `craco` for the **upb.crypto.craco** library.

If you want to use the mclwrap library, you also need to [install the MCL java bindings](#mclwrap-installation).

## Gradle

We asssume you have set up a Gradle project with a `build.gradle` file.
Currently, the libraries are only available via the university nexus repository **outdated, not anymore**. 
So, add `maven { url "https://nexus.cs.upb.de/repository/sfb901-releases/" }` to your list of
repositories in the `build.gradle` file.

Then, you need to decide which libraries you need. Once you have decided, you need to add the dependency.
For example, for `upb.crypto.craco` version 1.1.0, you would add `implementation group: 'de.upb.crypto', name: 'craco', version: '1.1.0'`
to the `dependencies` section in the `build.gradle` file.

If you want to use the mclwrap library, you also need to [install the MCL java bindings](#mclwrap-installation).

## Manual Installation

WIP

# Mclwrap Installation

For benchmarking you will probably want to use an efficient cryptographic pairing implementation. 
The **upb.crypto.math** library does provide a selection of pairings but these are orders of magnitude less efficient than other, more optimized implementations.

An efficient pairing implementation is provided by our wrapper around the [MCL library's](https://github.com/herumi/mcl) implementation of the BN254 curve. 
This wrapper is provided by the **upb.crypto.mclwrap** library. 

To use the MCL wrapper library in your project, you need to install the Java bindings for MCL.
To simplify this process, we have provided a [script in the **upb.crypto.mclwrap** repository](https://github.com/upbcuk/upb.crypto.mclwrap/blob/master/install_mcl.sh). 
Aside from Java, you need to have installed ``libgmp-dev`` via your package manager to execute it. 
It clones MCL, builds it and its Java bindings, and copies the resulting library to where the Java loader can find it.
