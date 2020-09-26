---
title: Composite Builds For Snapshot Versions
toc: true
---

Originally, the upb.crypto libraries were distributed via the universities own Nexus repository.
Since then, the Nexus has been restricted to the university network, necessitating a switch to a different host for our libraries.
Release versions are hosted on Maven Central, but snapshot builds are not appropriate to host there.

For example, upb.crypto.craco needs upb.crypto.math to work, but, unless you have installed the appropriate version of upb.crypto.math in your local maven repository, you will not be able to resolve the dependency since no snapshot builds are in any other repository.
Therefore we have implemented a different build process for snapshot versions of the upb.crypto dependencies.
This process is also used by our Continuous Integration system for the snapshot builds.

# Overview
The basic idea is to automatically download the required upb.crypto dependency (such as Math), and then use [Gradle's composite builds feature](https://docs.gradle.org/current/userguide/composite_builds.html) to include it where required.
To do this, every library that depends on some other upb.crypto library includes a build script in its `settings.gradle` file.
This script clones the dependency to the same directory level as the library being built and includes it as a composite build if possible.
"If possible" means that the branches should follow some rules. Let `LB` be the name of the branch of the library being built and `DB` be the name of the branch of the dependency library. The composite build will only be enabled, if the following holds:

- The dependency has no branch called `LB` and `DB == master`. In this case, the `master` branch of the dependency is used for the composite build.
- The dependency has a branch called `LB` and `DB = LB`. In this case, the `DB` branch of the dependency is used for the composite build.

To summarize, the build script will always try to use the branch with the same name as `LB` and use `master` if no such branch exists.
Importantly, no automatic checkout of branches is done. 
This is to reduce complexity and prevent potential problems potentially caused by automatically executing git checkout commands.

Keep in mind that this does not include any version checking!
This means that you have to ensure that the version of the dependency being included by the composite build is the correct one.
By this we don't mean the version string–this is not checked–, but the dependency's implementation itself.
If they are not compatible, it might only show up during testing when a function from the dependencies does not behave as expected.

## Customization
You can customize behaviour of the build script using certain properties.

These can either be set in the `gradle.properties` file in the top level folder of the project (on the same level as `build.gradle`), or be given as a parameter using the `-P` option for Gradle.

- **useCurrentBranch**: This skips the branch selection checking. 
That means the composite build will be enabled no matter the dependency branches that are currently checked out.
This can be useful for when you need a version that is not on `master` but you also do not want to create a new branch.
To set this, just give it any value; the script just checks for definition of the parameter.
