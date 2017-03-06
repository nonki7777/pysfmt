#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# index.py
"""
Created on Feb 28 2017
"""

import sfmt1_5_1 as sfmt


def main():
    sf = sfmt.Sfmt(1234)
    print("sfmt.SFMT_MEXP={}".format(sfmt.SFMT_MEXP))
    print("sfmt.SFMT_N={}".format(sfmt.SFMT_N))
    print("sfmt.SFMT_N32={}".format(sfmt.SFMT_N32))
    print("sfmt.SFMT_N64={}".format(sfmt.SFMT_N64))
    print("sfmt.SFMT_MSK1={:x}".format(sfmt.SFMT_MSK1))
    for i in range(0, 100):
        r = sf.sfmt_genrand_uint32()
        print(r)

    print()
    sf.sfmt_init_by_array([0x1234, 0x5678, 0x9abc, 0xdef0], 4)
    for i in range(0, 100):
        r = sf.sfmt_genrand_uint32()
        print(r)

    print()
    sf.sfmt_init_gen_rand()
    for i in range(0, 10):
        f = sf.sfmt_genrand_real()
        print(f)


if __name__ == "__main__":
    main()
