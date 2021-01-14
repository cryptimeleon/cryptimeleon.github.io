---
title: Testing Schemes Using Craco
toc: true
mathjax: false
---

** This page is still work in progress **

Once you have implemented a scheme, you will probably want to write tests for it.
To speed up this process, Craco offers a number of generic test cases for classes that implement interfaces such as `SignatureScheme` or `EncryptionScheme`.
These test cases already include a number of test methods, and you just have to provide parameters for them.

There are some differences between implementing your scheme as part of Craco versus using Craco as a dependency.


# Supported Interfaces

<!-- List the scheme interfaces for which we have tests available, and match them to the tester classes. Also talk about parameter provider classes. -->

# Testing A Scheme Outside Of Craco

<!-- When you implement your scheme in a different project, you can use the test feature variant of Craco to get the test source set
of Craco. In Mclwrap the test class from math is extended such that the mclwrap parameters are given to it. We can use a similar approach to overwrite
the getParams() class. -->


# Testing a Scheme Inside Of Craco

<!-- When the scheme is implemented as part of craco, you can just implement the parameters in the right folder and they are collected automatically. -->
