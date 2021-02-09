---
title: Dependencies
toc: true
---

### Math

Refer to the `dependencies` section in Math's Gradle [build configuration](https://github.com/upbcuk/upb.crypto.math/blob/master/build.gradle).

### Craco

Refer to the `dependencies` section in Craco's Gradle [build configuration](https://github.com/upbcuk/upb.crypto.craco/blob/master/build.gradle).

### Mclwrap

Refer to the `dependencies` section in Mclwrap's Gradle [build configuration](https://github.com/upbcuk/upb.crypto.mclwrap/blob/master/build.gradle).

Additionally, Mclwrap relies on the [Mcl library](https://github.com/herumi/mcl). The exact version can be found in the [readme](https://github.com/upbcuk/upb.crypto.mclwrap#readme).

### Predenc

Refer to the `dependencies` section in Predenc's Gradle [build configuration](https://github.com/upbcuk/upb.crypto.predenc/blob/master/build.gradle).

### Groupsig

Refer to the `dependencies` section in Groupsig's Gradle [build configuration](https://github.com/upbcuk/upb.crypto.groupsig/blob/master/build.gradle).

### CLARC

The only version of CLARC whose tests currently run correctly lies on the [fix-clarc-tests branch](https://github.com/upbcuk/upb.crypto.clarc/tree/fix-clarc-tests).
You will also need to use branch `fix-clarc-tests` of Math, Craco, and the [old Protocols project](https://github.com/upbcuk/upb.crypto.protocols/tree/fix-clarc-tests).

Compatibility of CLARC (aside from tests) with other versions is not tested. It definitely does not work with version 2.0.0 of our libraries as Math has undergone an API-breaking rewrite for version 2.0.0.