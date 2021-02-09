---
title: Setting Up The Project
toc: true
---

# Project Setup

All the upb.crypto libraries use the [Gradle](https://gradle.org/) build tool. 
In this guide, we show you how to set up a project in your integrated development environment of choice. 
This guide is intended for development of the library itself.

If you have problems with building any of the projects, make sure you use the newest version of the Java SDK 8.
Not all versions of Java 8 are supported.

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
For example, as Craco relies on Math, changes to the math library should be followed by testing the craco library with the new changes.

To do this, there are two options: Local installation and composite builds.

### Composite Builds

Composite builds have the advantage of not requiring you to manually install the project each time you want to test its changes. 
Instead, the dependencies will automatically be newly built when required.
Furthermore, IDEs such as IntelliJ IDEA have special support for composite builds, allowing you to view the sources for any dependencies included in the composite build.

We recommend using composite builds over the local installation approach. More info on this [here]({% link contributors/composite-builds.md %}).

### Local Installation

For any of the libraries you can use the command ``publishToMavenLocal`` in the project root directory to install the library to the local repository (remember to build the newest version via ``gradle build`` before this). 
To make sure that other libraries actually use local builds and not remote, you need to make sure that local builds are preferred compared to remote builds.
Hence, `mavenLocal()` should be listed at the top of the `repositories` section in the `build.gradle` file.
