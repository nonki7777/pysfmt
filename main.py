#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# index.py
"""
Created on Feb 28 2017
"""

import sfmt1_5_1 as sfmt


def main():
    array32 = [0] * 100000
    array32_2 = [0] * 10000
    sf = sfmt.Sfmt(1234)
    print(sf.sfmt_get_idstring())
    print("32 bit generated randoms")
    print("init_gen_rand__________")
    for i in range(0, 10000):
        r = sf.sfmt_genrand_uint32()
        if i >= 1000:
            continue
        print("{:10d} ".format(r), sep='', end='')
        if i % 5 == 4:
            print()

    print()
    print("init_by_array__________")
    sf.sfmt_init_by_array([0x1234, 0x5678, 0x9abc, 0xdef0], 4)
    sf.sfmt_fill_array32(array32, 10000)
    sf.sfmt_fill_array32(array32_2, 10000)
    for i in range(0, 10000):
        r = array32[i]
        if i >= 1000:
            continue
        print("{:10d} ".format(r), sep='', end='')
        if i % 5 == 4:
            print()

    print()
    sf.sfmt_init_gen_rand()
    for i in range(0, 10):
        f = sf.sfmt_genrand_real()
        print(f)

    sfmt.seed(1234)
    print("sfmt.random()=", sfmt.random())
    print("The above should be (1905350899 / 4294967296) = ", 1905350899.0 / 4294967296.0)

if __name__ == "__main__":
    main()
