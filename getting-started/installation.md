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
Currently, the libraries are only available via the university nexus repository. 
This is a Maven repository available at `https://nexus.cs.upb.de/repository/sfb901-releases/`.

The group id of all the **upb.crypto** projects is `de.upb.crypto` and the artifact id corresponds to the name of the library you want to use. 
For example, `craco` for the **upb.crypto.craco** library.

If you want to use the mclwrap library, you also need to [install the MCL java bindings](#mclwrap-installation).

## Gradle

We asssume you have set up a Gradle project with a `build.gradle` file.
Currently, the libraries are only available via the university nexus repository. 
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

# Installation for Contributors

All the **upb.crypo** libraries use the [Gradle](https://gradle.org/) build tool version 4.9. 
In this guide, we show you how to set up a project in your integrated development environment of choice. 
This guide is intended for development of the library itself.

## Cloning the Repo

Naturally, the first thing to do is to clone the repository containing the library you need. 
If you are reading this, you probably know how to do this.

After this is done, we continue by creating a new project in your favorite IDE.

## Setting up a project in IntelliJ IDEA

*Note: This was written for IntelliJ IDEA Version 2019.2.4*

Start up IntelliJ IDEA such that the "Welcome to IntelliJ IDEA" appears. 
In case you already have another project open, clicking **File &rarr; Close Project** will take you to it.

Next, click **Import Project**. 
Now browse to the path where you cloned the library repository. 
The repository contains a ``build.gradle`` file. 
Select it and click **OK**. Once the import process is done, the project is ready for use.

## Setting up a project in Eclipse

*Note: This was written for Eclipse 2020-03 (4.15.0).*

Open up Eclipse. Select **File &rarr; Import...**. 
As import wizard select **Gradle &rarr; Existing Gradle Project**.
Click **Next** on the introductory information page that pops up.
A window will open up asking you to select the project root directory.
Browse to the location where you cloned the repository to and select the repository folder.
For example, ``/home/username/code/upb.crypto.craco``. 
Click **Finish** to finish setup. You can also click **Next** if you want to, for example, select a specific Java SDK.

## Testing Changes

Once you have done some changes to a library, you might want to test the effect of these changes on the other libraries.
For example, as **upb.crypto.craco** relies on **upb.crypto.math**, changes to the math library should be followed by testing the craco library with the new changes.

To do this, there are two options: Local installation and composite builds.

### Local Installation

For any of the libraries you can use the command ``gradle install`` in the project root directory to build and install the library to the local repository. 
To make sure that other libraries actually preferentally use local builds, you need to make sure that local builds are preferred compared to remote builds. 
Hence, `mavenLocal()` should be listed at the top of the `repositories` section in the `build.gralde` file.

The process then goes as follows:

1. Update the version number in the ``build.gradle`` file of the changed library.

2. Execute ``gradle install`` to install the new library in the local repository.

3. Update the version number of the dependency in the ``build.gradle`` file of the library you want to test the new changes on.

### Composite Builds

Composite builds have the advantage of not requiring you to manually install the project each time you want to test its changes. 
Instead, the dependencies will automatically be newly built when required.
To enable composite builds, execute ``gradle enableCompositeBuild`` in the root folder of the project you would like to test. 
To disable, execute ``gradle disableCompositeBuild``.
