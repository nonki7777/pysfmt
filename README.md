### pysfmt

SFMT for Python
Implemented with Python 3.5.2 or greater

SFMT - SIMD oriented Fast Mersenne Twister
The original version: SFMT Version 1.5.1 written by C/C++
http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/SFMT/index.html

Environment: Linux/Windows
* Little Endian
* Altivec technique is not used
Volunteers for using on OSX will be welcome.
Created: March 2017

Usage:

    >>> import sfmt1_5_1 as sfmt
    >>> sfmt.seed(1234)  # If no arguments, the current time is used as a seed
    >>> sfmt.random()  # generates a pseudorandom floating point number in the range [0.0, 1.0)
    0.44362407620064914

main.py is optional.

Coded by nonki7777
