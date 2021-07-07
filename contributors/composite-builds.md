---
title: Composite Builds For Snapshot Versions
toc: true
---

This documents explains the composite build process for snapshot builds.
Snapshot builds are non-release builds that are still subject to change.

Read about composite builds [here](https://docs.gradle.org/current/userguide/composite_builds.html).
This document assumes you know the basics of how they work.

To make composite builds easier to use, we have implemented a Gradle build script to automate some steps of the process.

# Overview
The basic idea is to automatically download the required Cryptimeleon dependency (such as Math), and then use Gradle's composite builds feature to include it where required.
To do this, every library that depends on some other Cryptimeleon library includes a build script in its `settings.gradle` file.
This script clones the dependency to the same directory level as the library being built and includes it as a composite build if possible.
"If possible" means that the branches should follow some rules. Let `LB` be the name of the branch of the library being built and `DB` be the name of the branch of the dependency library. The composite build will only be enabled if either of the following hold:

- The dependency has no branch called `LB` and `DB == develop`. In this case, the `develop` branch of the dependency is used for the composite build.
- The dependency has a branch called `LB` and `DB = LB`. In this case, the `DB` branch of the dependency is used for the composite build.

To summarize, the build script will always try to use the branch with the same name as `LB` and use `develop` if no such branch exists.
Importantly, no automatic checkout of branches is done. 
This means that if the branches don't match, the build script will complain and fail. 
You can adjust this behaviour using the **useCurrentBranch** parameter as explained below.

Keep in mind that this does not include any version checking, i.e. the composite build will happily include the version of the dependency that is currently checked out, whether it matches the dependency version or not.
This means that you have to ensure that the version of the dependency being included by the composite build is the correct one.

## Customization
You can customize behaviour of the build script using certain properties.

These can either be set in the `gradle.properties` file in the top level folder of the project (on the same level as `build.gradle`), or be given as a parameter using the `-P` option for Gradle.
For examples of how this works see [the examples section](#examples).

- **useCurrentBranch**: If defined (any value) the branch selection checking will be skipped. 
    That means the composite build will be enabled no matter the dependency branches that are currently checked out.
    This can be useful for when you need a version that is not on `develop` but you also do not want to create a new branch.
- **checkoutIfCloned**: If defined (any value), will automatically check out the corresponding
    dependency branch (branch with same name) given that the dependency was freshly cloned.
    Used by the Travis CI to automatically switch to the right dependency branch for the build.

These properties only affect the project they are set for, not any of its composite build dependencies.
For example, the Predenc library depends on the Craco library which depends on the Math library.
If you enable `useCurrentBranch` only for Predenc, but not for Craco, the following will happen:
Predenc will happily include whatever Craco branch is currently checked out.
Craco, however, will then only include Math if the checked out branch names of Craco and Math match.

More information on Gradle properties can be found in the [official documentation](https://docs.gradle.org/current/userguide/build_environment.html#sec:gradle_configuration_properties).

### Examples

#### Customizing Settings Via `gradle.properties`
The `gradle.properties` file must be in the same directory as the project's `build.gradle` file.
Enabling `useCurrentBranch` then looks as follows:
```groovy
useCurrentBranch=""
```
We assign an empty string as any value suffices.

#### Customizing Settings Via Gradle's `-P` Parameter
When executing the Gradle wrapper, you can pass it properties via the `-P` parameter.
The property will then affect the project whose wrapper you executed.
The syntax is as follows:
```bash
./gradlew build -PuseCurrentBranch
```
After the `-P` the name of the property follows without spaces.
In this case `useCurrentBranch` does not need a value, but to set a value you would add an equals sign `=` followed by the property's desired value.
For each property a separate `-P` must be used.
