#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# sfmt1_5_1.py
"""
乱数生成器 SFMT for Python
C言語で書かれているSFMT Version 1.5.1をPythonに移植
実行環境はLinux/Windowsを想定する。つまり：
* Little Endian
* Altivecというベクトル演算は使わない
OSXによる動作は確認していない。
Created on March 3 2017
"""

# 共通定数
SFMT_MEXP = 216091  # 既定は19937だがここでは最長の216091を使ってみる
SFMT_N = SFMT_MEXP // 128 + 1  # //は切り捨てなので、これは切り上げを意味する
SFMT_N32 = SFMT_N * 4
SFMT_N64 = SFMT_N * 2
# Intel x86 および AMD64 (x86-64) はリトルエンディアン

# 以降はMEXP=216091の固有定数
SFMT_POS1 = 627
SFMT_SL1 = 11
SFMT_SL2 = 3
SFMT_SR1 = 10
SFMT_SR2 = 1
SFMT_MSK1 = 0xbff7bff7
SFMT_MSK2 = 0xbfffffff
SFMT_MSK3 = 0xbffffa7f
SFMT_MSK4 = 0xffddfbfb
SFMT_PARITY1 = 0xf8000001
SFMT_PARITY2 = 0x89e80709
SFMT_PARITY3 = 0x3bd2b64b
SFMT_PARITY4 = 0x0c64b1e4
"""ALTI関連の定数は使わない
SFMT_ALTI_SL1 = (SFMT_SL1, SFMT_SL1, SFMT_SL1, SFMT_SL1)
SFMT_ALTI_SR1 = (SFMT_SR1, SFMT_SR1, SFMT_SR1, SFMT_SR1)
SFMT_ALTI_MSK = (SFMT_MSK1, SFMT_MSK2, SFMT_MSK3, SFMT_MSK4)
SFMT_ALTI_MSK64 = (SFMT_MSK2, SFMT_MSK1, SFMT_MSK4, SFMT_MSK3)
SFMT_ALTI_SL2_PERM = (3,21,21,21,7,0,1,2,11,4,5,6,15,8,9,10)
SFMT_ALTI_SL2_PERM64 = (3,4,5,6,7,29,29,29,11,12,13,14,15,0,1,2)
SFMT_ALTI_SR2_PERM = (7,0,1,2,11,4,5,6,15,8,9,10,17,12,13,14)
SFMT_ALTI_SR2_PERM64 = (15,0,1,2,3,4,5,6,17,8,9,10,11,12,13,14)
"""
SFMT_IDSTR = "SFMT-216091:627-11-3-10-1:bff7bff7-bfffffff-bffffa7f-ffddfbfb"


class Sfmt:
    def __init__(self, seed=None):
        self.state = [0] * SFMT_N32
        self.idx = 0
        self.sfmt_init_gen_rand(seed)

    def sfmt_init_gen_rand(self, x=None):
        if x is None:
            import time
            x = int(time.time() * 256)
        elif isinstance(x, (str, bytes, bytearray)):
            if isinstance(x, str):
                x = x.encode('utf8')
            import hashlib
            h = hashlib.sha512()
            h.update(x)
            x += h.digest()
            x = int.from_bytes(x, 'big')
        elif isinstance(x, int):
            pass
        else:
            raise TypeError
        self.state[idxof(0)] = _int32(x)
        for i in range(1, SFMT_N32):
            y = 1812433253 * (
                self.state[idxof(i - 1)] ^
                (self.state[idxof(i - 1)] >> 30)) + i
            self.state[idxof(i)] = _int32(y)
        self.idx = SFMT_N32
        self.period_certification()

    def sfmt_init_by_array(self, init_key, key_length):
        size = SFMT_N * 4
        if size >= 623:
            lag = 11
        elif size >= 68:
            lag = 7
        elif size >= 39:
            lag = 5
        else:
            lag = 3
        mid = (size - lag) // 2
        self.state = [0x8b8b8b8b] * SFMT_N32
        count = max([key_length + 1, SFMT_N32])
        r = func1(self.state[idxof(0)] ^ self.state[idxof(mid)] ^
                  self.state[idxof(SFMT_N32 - 1)])
        self.state[idxof(mid)] = _int32(self.state[idxof(mid)] + r)
        r = _int32(r + key_length)
        self.state[idxof(mid + lag)] = _int32(self.state[idxof(mid + lag)] + r)
        self.state[idxof(0)] = r
        count -= 1
        i = 1
        j = 0
        while (j < count) and (j < key_length):
            r = func1(self.state[idxof(i)] ^ self.state[idxof((i + mid) % SFMT_N32)] ^
                      self.state[idxof((i + SFMT_N32 - 1) % SFMT_N32)])
            self.state[idxof((i + mid) % SFMT_N32)] = _int32(self.state[idxof((i + mid) % SFMT_N32)] + r)
            r = _int32(r + init_key[j] + i)
            self.state[idxof((i + mid + lag) % SFMT_N32)] = _int32(
                self.state[idxof((i + mid + lag) % SFMT_N32)] + r)
            self.state[idxof(i)] = r
            i = (i + 1) % SFMT_N32
            j += 1
        while j < count:
            r = func1(self.state[idxof(i)] ^ self.state[idxof((i + mid) % SFMT_N32)] ^
                      self.state[idxof((i + SFMT_N32 - 1) % SFMT_N32)])
            self.state[idxof((i + mid) % SFMT_N32)] = _int32(self.state[idxof((i + mid) % SFMT_N32)] + r)
            r = _int32(r + i)
            self.state[idxof((i + mid + lag) % SFMT_N32)] = _int32(
                self.state[idxof((i + mid + lag) % SFMT_N32)] + r)
            self.state[idxof(i)] = r
            i = (i + 1) % SFMT_N32
            j += 1
        for j in range(0, SFMT_N32):
            r = func2(self.state[idxof(i)] + self.state[idxof((i + mid) % SFMT_N32)] +
                      self.state[idxof((i + SFMT_N32 - 1) % SFMT_N32)])
            self.state[idxof((i + mid) % SFMT_N32)] = _int32(self.state[idxof((i + mid) % SFMT_N32)] ^ r)
            r = _int32(r - i)
            self.state[idxof((i + mid + lag) % SFMT_N32)] = _int32(
                self.state[idxof((i + mid + lag) % SFMT_N32)] ^ r)
            self.state[idxof(i)] = r
            i = (i + 1) % SFMT_N32
        self.idx = SFMT_N32
        self.period_certification()

    def sfmt_genrand_uint32(self):
        """32bitの疑似乱数を、整数で返す"""
        if self.idx >= SFMT_N32:
            self.sfmt_gen_rand_all()
            self.idx = 0
        r = _int32(self.state[self.idx])
        self.idx += 1
        return r

    def sfmt_gen_rand_all(self):
        r1 = tuple(self.state[(SFMT_N - 2) * 4 + k] for k in range(0, 4))
        r2 = tuple(self.state[(SFMT_N - 1) * 4 + k] for k in range(0, 4))
        i = 0
        while i < SFMT_N - SFMT_POS1:
            a = tuple(self.state[i * 4 + k] for k in range(0, 4))
            b = tuple(self.state[(i + SFMT_POS1) * 4 + k] for k in range(0, 4))
            r = do_recursion(a, b, r1, r2)
            for jj in range(0, 4):
                self.state[i * 4 + jj] = r[jj]
            r1 = r2
            r2 = tuple(self.state[i * 4 + k] for k in range(0, 4))
            i += 1
        while i < SFMT_N:
            a = tuple(self.state[i * 4 + k] for k in range(0, 4))
            b = tuple(self.state[(i + SFMT_POS1 - SFMT_N) * 4 + k] for k in range(0, 4))
            r = do_recursion(a, b, r1, r2)
            for jj in range(0, 4):
                self.state[i * 4 + jj] = r[jj]
            r1 = r2
            r2 = tuple(self.state[i * 4 + k] for k in range(0, 4))
            i += 1

    def period_certification(self):
        inner = 0
        parity = (SFMT_PARITY1, SFMT_PARITY2, SFMT_PARITY3, SFMT_PARITY4)
        for i in range(0, 4):
            inner = _int32(inner ^ self.state[idxof(i)] & parity[i])
        for i in (16, 8, 4, 2, 1):
            inner = _int32(inner ^ (inner >> i))
        inner = _int32(inner & 1)
        if inner == 1:  # OK
            return
        for i in range(0, 4):
            work = 1
            for j in range(0, 32):
                if _int32(work & parity[i]) != 0:
                    self.state[idxof(i)] = _int32(self.state[idxof(i)] ^ work)
                    return
                work = _int32(work << 1)

    def sfmt_fill_array32(self, arr, size):
        assert self.idx == SFMT_N32
        assert size % 4 == 0
        assert size >= SFMT_N32

        self.gen_rand_array(arr, size)  # arrもsizeもどちらも32bitで考える
        self.idx = SFMT_N32

    def gen_rand_array(self, ar32, size32):
        r1 = tuple(self.state[(SFMT_N - 2) * 4 + k] for k in range(0, 4))
        r2 = tuple(self.state[(SFMT_N - 1) * 4 + k] for k in range(0, 4))
        i = 0
        while i < SFMT_N - SFMT_POS1:
            a = tuple(self.state[i * 4 + k] for k in range(0, 4))
            b = tuple(self.state[(i + SFMT_POS1) * 4 + k] for k in range(0, 4))
            r = do_recursion(a, b, r1, r2)
            for jj in range(0, 4):
                ar32[i * 4 + jj] = r[jj]
            r1 = r2
            r2 = tuple(ar32[i * 4 + k] for k in range(0, 4))
            i += 1
        while i < SFMT_N:
            a = tuple(self.state[i * 4 + k] for k in range(0, 4))
            b = tuple(ar32[(i + SFMT_POS1 - SFMT_N) * 4 + k] for k in range(0, 4))
            r = do_recursion(a, b, r1, r2)
            for jj in range(0, 4):
                ar32[i * 4 + jj] = r[jj]
            r1 = r2
            r2 = tuple(ar32[i * 4 + k] for k in range(0, 4))
            i += 1
        while i < size32 // 4 - SFMT_N:
            a = tuple(ar32[(i - SFMT_N) * 4 + k] for k in range(0, 4))
            b = tuple(ar32[(i + SFMT_POS1 - SFMT_N) * 4 + k] for k in range(0, 4))
            r = do_recursion(a, b, r1, r2)
            for jj in range(0, 4):
                ar32[i * 4 + jj] = r[jj]
            r1 = r2
            r2 = tuple(ar32[i * 4 + k] for k in range(0, 4))
            i += 1
        j = 0
        while j < 2 * SFMT_N - size32 // 4:
            for jj in range(0, 4):
                self.state[j * 4 + jj] = ar32[(j + size32 // 4 - SFMT_N) * 4 + jj]
            j += 1
        while i < size32 // 4 - SFMT_N:
            a = tuple(ar32[(i - SFMT_N) * 4 + k] for k in range(0, 4))
            b = tuple(ar32[(i + SFMT_POS1 - SFMT_N) * 4 + k] for k in range(0, 4))
            r = do_recursion(a, b, r1, r2)
            for jj in range(0, 4):
                ar32[i * 4 + jj] = r[jj]
            r1 = r2
            r2 = tuple(ar32[i * 4 + k] for k in range(0, 4))
            for jj in range(0, 4):
                self.state[j * 4 + jj] = ar32[i * 4 + jj]
            i += 1
            j += 1

    @staticmethod
    def sfmt_get_idstring():
        return SFMT_IDSTR

    def sfmt_genrand_real(self):
        """範囲[0,1)の疑似乱数を、浮動小数点で返す"""
        r = self.sfmt_genrand_uint32()
        return r * (1.0 / 4294967296.0)


def _int32(x):
    """32ビットだけを得る"""
    return int(0xFFFFFFFF & x)


def idxof(i):
    """iはlittle endianのときには何もせずそのまま返す"""
    return i


def func1(x):
    """sfmt_init_by_arrayで使われる"""
    x = _int32(x)
    return _int32((x ^ (x >> 27)) * 1664525)


def func2(x):
    """sfmt_init_by_arrayで使われる"""
    x = _int32(x)
    return _int32((x ^ (x >> 27)) * 1566083941)


def rshift128(ain, shift):
    th = (ain[3] << 32) | ain[2]
    tl = (ain[1] << 32) | ain[0]
    oh = th >> (shift * 8)
    ol = tl >> (shift * 8)
    ol |= th << (64 - shift * 8)
    r = [_int32(ol), _int32(ol >> 32), _int32(oh), _int32(oh >> 32)]
    return tuple(r)


def lshift128(ain, shift):
    th = (ain[3] << 32) | ain[2]
    tl = (ain[1] << 32) | ain[0]
    oh = th << (shift * 8)
    ol = tl << (shift * 8)
    oh |= tl >> (64 - shift * 8)
    r = [_int32(ol), _int32(ol >> 32), _int32(oh), _int32(oh >> 32)]
    return tuple(r)


def do_recursion(aa, bb, cc, dd):
    x = lshift128(aa, SFMT_SL2)
    y = rshift128(cc, SFMT_SR2)
    r = [0] * 4
    r[0] = _int32(aa[0] ^ x[0] ^
                               ((bb[0] >> SFMT_SR1) & SFMT_MSK1) ^ y[0] ^ (dd[0] << SFMT_SL1))
    r[1] = _int32(aa[1] ^ x[1] ^
                                   ((bb[1] >> SFMT_SR1) & SFMT_MSK2) ^ y[1] ^ (dd[1] << SFMT_SL1))
    r[2] = _int32(aa[2] ^ x[2] ^
                                   ((bb[2] >> SFMT_SR1) & SFMT_MSK3) ^ y[2] ^ (dd[2] << SFMT_SL1))
    r[3] = _int32(aa[3] ^ x[3] ^
                                   ((bb[3] >> SFMT_SR1) & SFMT_MSK4) ^ y[3] ^ (dd[3] << SFMT_SL1))
    return tuple(r)

_a = Sfmt()
seed = _a.sfmt_init_gen_rand
random = _a.sfmt_genrand_real
