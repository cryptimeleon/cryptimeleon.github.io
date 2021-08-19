---
title: How to contribute to the Cryptimeleon libraries
toc: true
---

We are glad you are interested in contributing to Cryptimeleon.
This page will give you an overview of our contribution/developer guidelines and will point you to further information.

## Overview

The Cryptimeleon libraries consist of a number of related cryptographic libraries united under the Cryptimeleon name.
If you want to contribute, you therefore first need to decide on a specific library.
Then you can check out that library's issue tracker (we use the Github issue tracker) to find something to work on.

Cryptimeleon's [Github page](https://github.com/cryptimeleon) contains a list of those libraries.

## Project setup

Once you have decided on a library, you will need to clone it and create a project in your favourite IDE.
All the Cryptimeleon libraries use the [Gradle](https://gradle.org/) build tool. 
In this guide, we show you how to set up a project in your integrated development environment of choice. 
This guide is intended for development of the library itself.

If you have problems with building any of the projects, make sure you use the newest version of the Java SDK 8.
Not all versions of Java 8 are supported.

### Forking the repo

If you don't have write access to the repository, you will need to [fork](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/working-with-forks) the repository of the library you want to modify.
Then you can apply your changes to that repository.

After this is done, we continue by creating a new project in your favorite IDE.

### Setting up a project in IntelliJ IDEA

*Note: This was written for IntelliJ IDEA Version 2019.2.4*

Start up IntelliJ IDEA such that the "Welcome to IntelliJ IDEA" appears. 
In case you already have another project open, clicking **File &rarr; Close Project** will take you to it.

Next, click **Import Project**. 
Now browse to the path where you cloned the library repository. 
The repository contains a ``build.gradle`` file. 
Select it and click **OK**. Once the import process is done, the project is ready for use.

### Setting up a project in Eclipse

*Note: This was written for Eclipse 2020-03 (4.15.0).*

Open up Eclipse. Select **File &rarr; Import...**. 
As import wizard select **Gradle &rarr; Existing Gradle Project**.
Click **Next** on the introductory information page that pops up.
A window will open up asking you to select the project root directory.
Browse to the location where you cloned the repository to and select the repository folder.
For example, ``/home/username/code/craco``. 
Click **Finish** to finish setup. You can also click **Next** if you want to, for example, select a specific Java SDK.

### Testing changes

Once you have done some changes to a library, you might want to test the effect of these changes on the other libraries.
For example, as Craco relies on Math, changes to the Math library should be followed by testing the craco library with the new changes.

To do this, there are two options: Local installation and composite builds.

#### Composite builds

Composite builds have the advantage of not requiring you to manually install the project each time you want to test its changes. 
Instead, the dependencies will automatically be newly built when required.
Furthermore, IDEs such as IntelliJ IDEA have special support for composite builds, allowing you to view the sources for any dependencies included in the composite build.

We recommend using composite builds over the local installation approach. More info on this [here]({% link contributors/composite-builds.md %}).

#### Local installation

For any of the libraries you can use the command ``publishToMavenLocal`` in the project root directory to install the library to the local repository (remember to build the newest version via ``gradle build`` before this). 
To make sure that other libraries actually use local builds and not remote, you need to make sure that local builds are preferred compared to remote builds.
Hence, `mavenLocal()` should be listed at the top of the `repositories` section in the `build.gradle` file.

## Making changes

When making changes to the code, remember the following things:
- Stick to the existing code style
- Add Javadoc whenever necessary
- Add your changes to the `CHANGELOG.md` file in the root directory

## Contributing your changes

Once you have tested your changes locally, you will want to integrate them into the upstream repository.
You can do this by [creating a pull request from your fork](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork).
