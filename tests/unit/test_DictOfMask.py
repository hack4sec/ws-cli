#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

wrpath   = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/kernel')
sys.path.append(testpath + '/classes')

#from CommonTest import CommonTest
from classes.DictOfMask import DictOfMask
from libs.common import *
from classes.kernel.WSException import WSException


class Test_DictOfMask(object):
    model = None

    # Тест генерации словарей по маскам
    def test_gen_dict(self):
        test_data = {
            '?l': [
                'a', 'b', 'c', 'd', 'e', 'f',
                'g', 'h', 'i', 'j', 'k', 'l',
                'm', 'n', 'o', 'p', 'q', 'r',
                's', 't', 'u', 'v', 'w', 'x',
                'y', 'z'
            ],
            '?l?d,1,2': [
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'aa', 'ba', 'ca', 'da',
                'ea', 'fa', 'ga', 'ha', 'ia', 'ja', 'ka', 'la', 'ma', 'na', 'oa', 'pa', 'qa', 'ra', 'sa', 'ta', 'ua',
                'va', 'wa', 'xa', 'ya', 'za', '0a', '1a', '2a', '3a', '4a', '5a', '6a', '7a', '8a', '9a', 'ab', 'bb',
                'cb', 'db', 'eb', 'fb', 'gb', 'hb', 'ib', 'jb', 'kb', 'lb', 'mb', 'nb', 'ob', 'pb', 'qb', 'rb', 'sb',
                'tb', 'ub', 'vb', 'wb', 'xb', 'yb', 'zb', '0b', '1b', '2b', '3b', '4b', '5b', '6b', '7b', '8b', '9b',
                'ac', 'bc', 'cc', 'dc', 'ec', 'fc', 'gc', 'hc', 'ic', 'jc', 'kc', 'lc', 'mc', 'nc', 'oc', 'pc', 'qc',
                'rc', 'sc', 'tc', 'uc', 'vc', 'wc', 'xc', 'yc', 'zc', '0c', '1c', '2c', '3c', '4c', '5c', '6c', '7c',
                '8c', '9c', 'ad', 'bd', 'cd', 'dd', 'ed', 'fd', 'gd', 'hd', 'id', 'jd', 'kd', 'ld', 'md', 'nd', 'od',
                'pd', 'qd', 'rd', 'sd', 'td', 'ud', 'vd', 'wd', 'xd', 'yd', 'zd', '0d', '1d', '2d', '3d', '4d', '5d',
                '6d', '7d', '8d', '9d', 'ae', 'be', 'ce', 'de', 'ee', 'fe', 'ge', 'he', 'ie', 'je', 'ke', 'le', 'me',
                'ne', 'oe', 'pe', 'qe', 're', 'se', 'te', 'ue', 've', 'we', 'xe', 'ye', 'ze', '0e', '1e', '2e', '3e',
                '4e', '5e', '6e', '7e', '8e', '9e', 'af', 'bf', 'cf', 'df', 'ef', 'ff', 'gf', 'hf', 'if', 'jf', 'kf',
                'lf', 'mf', 'nf', 'of', 'pf', 'qf', 'rf', 'sf', 'tf', 'uf', 'vf', 'wf', 'xf', 'yf', 'zf', '0f', '1f',
                '2f', '3f', '4f', '5f', '6f', '7f', '8f', '9f', 'ag', 'bg', 'cg', 'dg', 'eg', 'fg', 'gg', 'hg', 'ig',
                'jg', 'kg', 'lg', 'mg', 'ng', 'og', 'pg', 'qg', 'rg', 'sg', 'tg', 'ug', 'vg', 'wg', 'xg', 'yg', 'zg',
                '0g', '1g', '2g', '3g', '4g', '5g', '6g', '7g', '8g', '9g', 'ah', 'bh', 'ch', 'dh', 'eh', 'fh', 'gh',
                'hh', 'ih', 'jh', 'kh', 'lh', 'mh', 'nh', 'oh', 'ph', 'qh', 'rh', 'sh', 'th', 'uh', 'vh', 'wh', 'xh',
                'yh', 'zh', '0h', '1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'ai', 'bi', 'ci', 'di', 'ei',
                'fi', 'gi', 'hi', 'ii', 'ji', 'ki', 'li', 'mi', 'ni', 'oi', 'pi', 'qi', 'ri', 'si', 'ti', 'ui', 'vi',
                'wi', 'xi', 'yi', 'zi', '0i', '1i', '2i', '3i', '4i', '5i', '6i', '7i', '8i', '9i', 'aj', 'bj', 'cj',
                'dj', 'ej', 'fj', 'gj', 'hj', 'ij', 'jj', 'kj', 'lj', 'mj', 'nj', 'oj', 'pj', 'qj', 'rj', 'sj', 'tj',
                'uj', 'vj', 'wj', 'xj', 'yj', 'zj', '0j', '1j', '2j', '3j', '4j', '5j', '6j', '7j', '8j', '9j', 'ak',
                'bk', 'ck', 'dk', 'ek', 'fk', 'gk', 'hk', 'ik', 'jk', 'kk', 'lk', 'mk', 'nk', 'ok', 'pk', 'qk', 'rk',
                'sk', 'tk', 'uk', 'vk', 'wk', 'xk', 'yk', 'zk', '0k', '1k', '2k', '3k', '4k', '5k', '6k', '7k', '8k',
                '9k', 'al', 'bl', 'cl', 'dl', 'el', 'fl', 'gl', 'hl', 'il', 'jl', 'kl', 'll', 'ml', 'nl', 'ol', 'pl',
                'ql', 'rl', 'sl', 'tl', 'ul', 'vl', 'wl', 'xl', 'yl', 'zl', '0l', '1l', '2l', '3l', '4l', '5l', '6l',
                '7l', '8l', '9l', 'am', 'bm', 'cm', 'dm', 'em', 'fm', 'gm', 'hm', 'im', 'jm', 'km', 'lm', 'mm', 'nm',
                'om', 'pm', 'qm', 'rm', 'sm', 'tm', 'um', 'vm', 'wm', 'xm', 'ym', 'zm', '0m', '1m', '2m', '3m', '4m',
                '5m', '6m', '7m', '8m', '9m', 'an', 'bn', 'cn', 'dn', 'en', 'fn', 'gn', 'hn', 'in', 'jn', 'kn', 'ln',
                'mn', 'nn', 'on', 'pn', 'qn', 'rn', 'sn', 'tn', 'un', 'vn', 'wn', 'xn', 'yn', 'zn', '0n', '1n', '2n',
                '3n', '4n', '5n', '6n', '7n', '8n', '9n', 'ao', 'bo', 'co', 'do', 'eo', 'fo', 'go', 'ho', 'io', 'jo',
                'ko', 'lo', 'mo', 'no', 'oo', 'po', 'qo', 'ro', 'so', 'to', 'uo', 'vo', 'wo', 'xo', 'yo', 'zo', '0o',
                '1o', '2o', '3o', '4o', '5o', '6o', '7o', '8o', '9o', 'ap', 'bp', 'cp', 'dp', 'ep', 'fp', 'gp', 'hp',
                'ip', 'jp', 'kp', 'lp', 'mp', 'np', 'op', 'pp', 'qp', 'rp', 'sp', 'tp', 'up', 'vp', 'wp', 'xp', 'yp',
                'zp', '0p', '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p', 'aq', 'bq', 'cq', 'dq', 'eq', 'fq',
                'gq', 'hq', 'iq', 'jq', 'kq', 'lq', 'mq', 'nq', 'oq', 'pq', 'qq', 'rq', 'sq', 'tq', 'uq', 'vq', 'wq',
                'xq', 'yq', 'zq', '0q', '1q', '2q', '3q', '4q', '5q', '6q', '7q', '8q', '9q', 'ar', 'br', 'cr', 'dr',
                'er', 'fr', 'gr', 'hr', 'ir', 'jr', 'kr', 'lr', 'mr', 'nr', 'or', 'pr', 'qr', 'rr', 'sr', 'tr', 'ur',
                'vr', 'wr', 'xr', 'yr', 'zr', '0r', '1r', '2r', '3r', '4r', '5r', '6r', '7r', '8r', '9r', 'as', 'bs',
                'cs', 'ds', 'es', 'fs', 'gs', 'hs', 'is', 'js', 'ks', 'ls', 'ms', 'ns', 'os', 'ps', 'qs', 'rs', 'ss',
                'ts', 'us', 'vs', 'ws', 'xs', 'ys', 'zs', '0s', '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
                'at', 'bt', 'ct', 'dt', 'et', 'ft', 'gt', 'ht', 'it', 'jt', 'kt', 'lt', 'mt', 'nt', 'ot', 'pt', 'qt', 'rt',
                'st', 'tt', 'ut', 'vt', 'wt', 'xt', 'yt', 'zt', '0t', '1t', '2t', '3t', '4t', '5t', '6t', '7t', '8t', '9t',
                'au', 'bu', 'cu', 'du', 'eu', 'fu', 'gu', 'hu', 'iu', 'ju', 'ku', 'lu', 'mu', 'nu', 'ou', 'pu', 'qu',
                'ru', 'su', 'tu', 'uu', 'vu', 'wu', 'xu', 'yu', 'zu', '0u', '1u', '2u', '3u', '4u', '5u', '6u', '7u',
                '8u', '9u', 'av', 'bv', 'cv', 'dv', 'ev', 'fv', 'gv', 'hv', 'iv', 'jv', 'kv', 'lv', 'mv', 'nv', 'ov',
                'pv', 'qv', 'rv', 'sv', 'tv', 'uv', 'vv', 'wv', 'xv', 'yv', 'zv', '0v', '1v', '2v', '3v', '4v', '5v',
                '6v', '7v', '8v', '9v', 'aw', 'bw', 'cw', 'dw', 'ew', 'fw', 'gw', 'hw', 'iw', 'jw', 'kw', 'lw', 'mw',
                'nw', 'ow', 'pw', 'qw', 'rw', 'sw', 'tw', 'uw', 'vw', 'ww', 'xw', 'yw', 'zw', '0w', '1w', '2w', '3w',
                '4w', '5w', '6w', '7w', '8w', '9w', 'ax', 'bx', 'cx', 'dx', 'ex', 'fx', 'gx', 'hx', 'ix', 'jx', 'kx',
                'lx', 'mx', 'nx', 'ox', 'px', 'qx', 'rx', 'sx', 'tx', 'ux', 'vx', 'wx', 'xx', 'yx', 'zx', '0x', '1x',
                '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x', 'ay', 'by', 'cy', 'dy', 'ey', 'fy', 'gy', 'hy', 'iy',
                'jy', 'ky', 'ly', 'my', 'ny', 'oy', 'py', 'qy', 'ry', 'sy', 'ty', 'uy', 'vy', 'wy', 'xy', 'yy', 'zy',
                '0y', '1y', '2y', '3y', '4y', '5y', '6y', '7y', '8y', '9y', 'az', 'bz', 'cz', 'dz', 'ez', 'fz', 'gz',
                'hz', 'iz', 'jz', 'kz', 'lz', 'mz', 'nz', 'oz', 'pz', 'qz', 'rz', 'sz', 'tz', 'uz', 'vz', 'wz', 'xz',
                'yz', 'zz', '0z', '1z', '2z', '3z', '4z', '5z', '6z', '7z', '8z', '9z', 'a0', 'b0', 'c0', 'd0', 'e0',
                'f0', 'g0', 'h0', 'i0', 'j0', 'k0', 'l0', 'm0', 'n0', 'o0', 'p0', 'q0', 'r0', 's0', 't0', 'u0', 'v0',
                'w0', 'x0', 'y0', 'z0', '00', '10', '20', '30', '40', '50', '60', '70', '80', '90', 'a1', 'b1', 'c1',
                'd1', 'e1', 'f1', 'g1', 'h1', 'i1', 'j1', 'k1', 'l1', 'm1', 'n1', 'o1', 'p1', 'q1', 'r1', 's1', 't1',
                'u1', 'v1', 'w1', 'x1', 'y1', 'z1', '01', '11', '21', '31', '41', '51', '61', '71', '81', '91', 'a2',
                'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2', 'i2', 'j2', 'k2', 'l2', 'm2', 'n2', 'o2', 'p2', 'q2', 'r2',
                's2', 't2', 'u2', 'v2', 'w2', 'x2', 'y2', 'z2', '02', '12', '22', '32', '42', '52', '62', '72', '82',
                '92', 'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3', 'i3', 'j3', 'k3', 'l3', 'm3', 'n3', 'o3', 'p3',
                'q3', 'r3', 's3', 't3', 'u3', 'v3', 'w3', 'x3', 'y3', 'z3', '03', '13', '23', '33', '43', '53', '63',
                '73', '83', '93', 'a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4', 'i4', 'j4', 'k4', 'l4', 'm4', 'n4',
                'o4', 'p4', 'q4', 'r4', 's4', 't4', 'u4', 'v4', 'w4', 'x4', 'y4', 'z4', '04', '14', '24', '34', '44',
                '54', '64', '74', '84', '94', 'a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5', 'i5', 'j5', 'k5', 'l5',
                'm5', 'n5', 'o5', 'p5', 'q5', 'r5', 's5', 't5', 'u5', 'v5', 'w5', 'x5', 'y5', 'z5', '05', '15', '25',
                '35', '45', '55', '65', '75', '85', '95', 'a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6', 'i6', 'j6',
                'k6', 'l6', 'm6', 'n6', 'o6', 'p6', 'q6', 'r6', 's6', 't6', 'u6', 'v6', 'w6', 'x6', 'y6', 'z6', '06',
                '16', '26', '36', '46', '56', '66', '76', '86', '96', 'a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7',
                'i7', 'j7', 'k7', 'l7', 'm7', 'n7', 'o7', 'p7', 'q7', 'r7', 's7', 't7', 'u7', 'v7', 'w7', 'x7', 'y7',
                'z7', '07', '17', '27', '37', '47', '57', '67', '77', '87', '97', 'a8', 'b8', 'c8', 'd8', 'e8', 'f8',
                'g8', 'h8', 'i8', 'j8', 'k8', 'l8', 'm8', 'n8', 'o8', 'p8', 'q8', 'r8', 's8', 't8', 'u8', 'v8', 'w8',
                'x8', 'y8', 'z8', '08', '18', '28', '38', '48', '58', '68', '78', '88', '98', 'a9', 'b9', 'c9', 'd9',
                'e9', 'f9', 'g9', 'h9', 'i9', 'j9', 'k9', 'l9', 'm9', 'n9', 'o9', 'p9', 'q9', 'r9', 's9', 't9', 'u9',
                'v9', 'w9', 'x9', 'y9', 'z9', '09', '19', '29', '39', '49', '59', '69', '79', '89', '99'],
            'abc,1,2': ['aa', 'ba', 'ca', 'ab', 'bb', 'cb', 'ac', 'bc', 'cc', 'a', 'b', 'c']
        }

        for mask in test_data:
            dom = DictOfMask(mask)
            assert dom.dict() == test_data[mask]
