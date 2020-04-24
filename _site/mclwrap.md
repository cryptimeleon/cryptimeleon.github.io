# The MCLWrap Efficient Pairing Wrapper
For benchmarking you will probably want to use an efficient cryptographic pairing implementation. 
The **upb.crypto.math** library does provide a selection of pairings but these are orders of magnitude less efficient than other, more optimized implementations.

To fix this, you can make use of our wrapper around the [MCL library's](https://github.com/herumi/mcl) implementation of the BN254 curve. 
This wrapper is provided by the **upb.crypto.mclwrap** library. 
On this page, we show you how to install and use it.



