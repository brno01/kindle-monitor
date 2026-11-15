"""Glifos DejaVu pre-rasterizados (GERADO por tools/gerar_fonte.py: nao edite a mao).

Licenca das fontes: DejaVu Fonts (baseadas em Bitstream Vera), https://dejavu-fonts.github.io/License.html
  Fonts are (c) Bitstream (see below). DejaVu changes are in public domain.
  Copyright (c) 2003 by Bitstream, Inc. All Rights Reserved. Bitstream Vera is a trademark of Bitstream, Inc.
  Copyright (c) 2006 by Tavmjong Bah. All Rights Reserved.
A licenca permite usar, copiar, embutir e redistribuir as fontes (e derivados como estes bitmaps) sem custo,
desde que o aviso de copyright acima seja mantido. Estes dados sao bitmaps de cobertura 8-bit (0-255)
renderizados com FreeType/Pillow a partir de DejaVu Sans, DejaVu Sans Bold e DejaVu Sans Mono.

Formato: FONTES[nome][tamanho_px] = {
    "ascent": int, "descent": int,          # metricas da fonte (px)
    "glifos": {codigo: (avanco, xoff, yoff, largura, altura, deslocamento)},
        # avanco em px (float); xoff/yoff = canto superior esquerdo do bitmap relativo a origem na linha de base
        # (yoff negativo = acima da base); deslocamento = posicao dos bytes no blob descomprimido.
    "dados": "<base64 de zlib de todos os bitmaps concatenados, linha a linha>",
}
"""
FONTES = {
    'sans-bold': {
        26: {
            "ascent": 25,
            "descent": 7,
            "glifos": {
                32: (9.047, 0, 0, 0, 0, 0),
                33: (11.859, 3, -19, 6, 19, 0),
                34: (13.547, 2, -19, 10, 7, 114),
                35: (21.781, 1, -19, 20, 19, 184),
                36: (18.094, 2, -20, 15, 24, 564),
                37: (26.047, 0, -19, 26, 19, 924),
                38: (22.672, 1, -19, 21, 19, 1418),
                39: (7.953, 2, -19, 4, 7, 1817),
                40: (11.891, 2, -20, 8, 23, 1845),
                41: (11.891, 2, -20, 8, 23, 2029),
                42: (13.594, 0, -19, 14, 12, 2213),
                43: (21.781, 2, -17, 18, 17, 2381),
                44: (9.875, 1, -5, 7, 9, 2687),
                45: (10.797, 1, -10, 9, 4, 2750),
                46: (9.875, 2, -5, 6, 5, 2786),
                47: (9.5, 0, -19, 10, 21, 2816),
                48: (18.094, 1, -19, 16, 19, 3026),
                49: (18.094, 2, -19, 15, 19, 3330),
                50: (18.094, 2, -19, 14, 19, 3615),
                51: (18.094, 1, -19, 15, 19, 3881),
                52: (18.094, 1, -19, 16, 19, 4166),
                53: (18.094, 2, -19, 15, 19, 4470),
                54: (18.094, 1, -19, 16, 19, 4755),
                55: (18.094, 1, -19, 16, 19, 5059),
                56: (18.094, 1, -19, 16, 19, 5363),
                57: (18.094, 1, -19, 16, 19, 5667),
                58: (10.391, 2, -14, 6, 14, 5971),
                59: (10.391, 1, -14, 7, 18, 6055),
                60: (21.781, 2, -16, 18, 15, 6181),
                61: (21.781, 2, -13, 18, 9, 6451),
                62: (21.781, 2, -16, 18, 15, 6613),
                63: (15.078, 1, -19, 13, 19, 6883),
                64: (26.0, 1, -19, 24, 23, 7130),
                65: (20.125, 0, -19, 20, 19, 7682),
                66: (19.812, 2, -19, 16, 19, 8062),
                67: (19.078, 1, -19, 17, 19, 8366),
                68: (21.578, 2, -19, 19, 19, 8689),
                69: (17.766, 2, -19, 14, 19, 9050),
                70: (17.766, 2, -19, 14, 19, 9316),
                71: (21.344, 1, -19, 19, 19, 9582),
                72: (21.766, 2, -19, 18, 19, 9943),
                73: (9.672, 2, -19, 6, 19, 10285),
                74: (9.672, -2, -19, 10, 24, 10399),
                75: (20.141, 2, -19, 19, 19, 10639),
                76: (16.562, 2, -19, 14, 19, 11000),
                77: (25.875, 2, -19, 22, 19, 11266),
                78: (21.766, 2, -19, 18, 19, 11684),
                79: (22.109, 1, -19, 20, 19, 12026),
                80: (19.062, 2, -19, 16, 19, 12406),
                81: (22.109, 1, -19, 20, 23, 12710),
                82: (20.016, 2, -19, 18, 19, 13170),
                83: (18.719, 1, -19, 16, 19, 13512),
                84: (17.734, 0, -19, 18, 19, 13816),
                85: (21.109, 2, -19, 17, 19, 14158),
                86: (20.125, 0, -19, 20, 19, 14481),
                87: (28.672, 0, -19, 28, 19, 14861),
                88: (20.047, 0, -19, 20, 19, 15393),
                89: (18.828, -1, -19, 21, 19, 15773),
                90: (18.859, 1, -19, 17, 19, 16172),
                91: (11.891, 2, -20, 9, 23, 16495),
                92: (9.5, 0, -19, 10, 21, 16702),
                93: (11.891, 1, -20, 9, 23, 16912),
                94: (21.781, 2, -19, 18, 7, 17119),
                95: (13.0, 0, 4, 13, 2, 17245),
                96: (13.0, 1, -21, 8, 5, 17271),
                97: (17.547, 1, -14, 15, 14, 17311),
                98: (18.609, 2, -20, 16, 20, 17521),
                99: (15.406, 1, -14, 13, 14, 17841),
                100: (18.609, 1, -20, 16, 20, 18023),
                101: (17.641, 1, -14, 16, 14, 18343),
                102: (11.312, 0, -20, 12, 20, 18567),
                103: (18.609, 1, -14, 16, 19, 18807),
                104: (18.516, 2, -20, 15, 20, 19111),
                105: (8.906, 2, -20, 5, 20, 19411),
                106: (8.906, -1, -20, 8, 25, 19511),
                107: (17.297, 2, -20, 16, 20, 19711),
                108: (8.906, 2, -20, 5, 20, 20031),
                109: (27.094, 2, -14, 24, 14, 20131),
                110: (18.516, 2, -14, 15, 14, 20467),
                111: (17.859, 1, -14, 16, 14, 20677),
                112: (18.609, 2, -14, 16, 19, 20901),
                113: (18.609, 1, -14, 16, 19, 21205),
                114: (12.828, 2, -14, 11, 14, 21509),
                115: (15.469, 1, -14, 14, 14, 21663),
                116: (12.422, 0, -18, 12, 18, 21859),
                117: (18.516, 2, -14, 15, 14, 22075),
                118: (16.953, 0, -14, 17, 14, 22285),
                119: (24.016, 0, -14, 24, 14, 22523),
                120: (16.766, 0, -14, 17, 14, 22859),
                121: (16.953, 0, -14, 17, 19, 23097),
                122: (15.141, 1, -14, 13, 14, 23420),
                123: (18.516, 3, -20, 13, 24, 23602),
                124: (9.5, 3, -20, 4, 26, 23914),
                125: (18.516, 3, -20, 13, 24, 24018),
                126: (21.781, 2, -12, 18, 6, 24330),
                176: (13.0, 2, -19, 9, 8, 24438),
                183: (9.875, 2, -11, 6, 5, 24510),
            },
            "dados": (
                'eNrtPAd4FFW3dzdlQzppIBLpAoJ0QaVJkS4oAipgpSgYFEVREJCuCCoICqJAKKKgAoIIShWkFyO9hhYgIRXSk929755z62xC8bf+'
                '7735vt2Zc2bm1nPPPXV6U3bc2/uG/73gv1F7+K9cjf25fP3clJ4n5BKlPxOyjdJYYh43Lu1dSkcQkkFpxB+5ElX1pXQwIXUo/UxX'
                'v4DSeoS8TGlvjTtLM+yELKM0WqHuoHQ1IbZkGq8fe5LSNwipSek8Du+kHof3rePY8RilYwi5k9JluoqFlN5DyBBK+yiUPZkm2gjZ'
                'SGkZhJt4ljb11nFwxNECf0IWUVpTVRHqotvZ6RxNsSlcJ0rfIaQ8pct16yZT2p6Qpyl9ReN2UWcwIXMorW+Z5Txa+tbAsm9vOkdp'
                'xt7FL9ZglT+To9tbhzR3URNcxf6XVsqjle/qMCmuFklk4B26qKsMfEqDv8E72120SxCCw2Ux7t2DAwhxrNMFn6pEiFffXxW8A1+4'
                'vXshTUO4imrz/dcY2EF34WcGtj0wr3ftSFserdAxm5VeJgNeKRRFLSUZRg9+Cia395y55UQmpVcPzm37+8fKAwwedyQ3a/eLXhyy'
                'baFXOYWQsCO8wpVechnEiFc+p3RTmbvZgA8EKDKV7rLzG96sUY0IGSS6v5A66+iVQNmIPUBpGoNaUjpF1l+O3QkkpAWlqWxEj9Nz'
                'AfKOKO0lCnQ1ltKHdPs/gxbUZC0YQKrm02+NnoUdVa3eRK/dbnY6ePzRvOw9MV7kGUoHEXv/HZl5x94LM58IT6Z77PaveQlnbjPu'
                'zKPOuqQPpZfrl2aT/o2+0ZzSDwjZTOkwQuqyOQuUN3yP0vMMuExpJ0J8GDOrJe+MorQzQc7Wkd+5W9yoksfXySZkEbUpLZBjsZ5e'
                'Kwvn5yhNqFtqDaVLNDd5mS/wb3irT4uJLXmF7hVzan9+Z1be8UklxSu3Tdx/Le/M1gmNvXQvWikKe1jhSl2lRZGvAPhGcGjnzQZy'
                'BsNl4tVzbRTyDXiyBrEeNWEtbvayIv33waOxdhNXVUzjXOAlHdjFQkIqX2HnXMB+bkOyAEYNS/DX0j8AdraNrGan1qQGbibEbyOc'
                'Z9Zhdab7kJ6woth7gdsBC2twHCH94DoKmNd+Xl9CCCHN4GIGtCLiMFwW3AODeBoulzUIqDTwEj45AGc/z8odXY8i9pxC7IKBzWuO'
                '3eyz8kJeftIvk+8lLQsYNqM2bDXX+3HSou+zJbmXlVAGp5rOZOhjFGmpFTsdYiBQ63BGbjnYZ9KYnfIdhLzJznvY7U/ZeQU7L2fn'
                'OZy2kIcDPJedZ4v7w8XzTaG9vqI86Pi37PwmO7dm5wPAIaD+mpz06CdEtO820d4PWLmFMOv1GbAeur0Wp4SQLjDzsC6AH9bma5h+'
                'yM6PA/dk5wowXkDlyezcSzBfGAeYxmnsvIKdF4gufMTOB8T9FIr7cEWKrJw8wU6w387hPfVN5/U9LOr/kZ1bEdKAndbxcShUVNqO'
                'Jhg0qKHVr/hyqNLSp0kbxhp6tqcJEdMK6Ckb6cKamUTzrlLX/PIwGo8fR0K5i7PTxxD6tjoAndmTCTQ3lTpjy0Mpp7qzMku+nw+l'
                'rB4saqi49Jkbt4UfsZS+QP5+zAOe4oDfrWD+2TYjgdF7iz8NZf+MTTOOyrYX2HC+JuR+tjYZPb/Fi5glevHMDS54Ydf7560YSWkP'
                'frWf5nFxgslFqxRbfY5fbaFOLnhGuegmjuoH2xUeP0jhMjif7uaoJ3DngWMppVXxwi+THuGohygdz6/mStHKK5me46gWSpj7iNJm'
                '/Oo8vcKZ8z1K3J2ohJWj9KqvHuEmn53IzD69UAggvgvkbK/EHfA7Pf2/MEG1D1xMiwwdTZFb2YCZ7gPWDuw71QFMC5kM6Q9XXV+D'
                '/44AN4Kr92Lhv66UI+gP3ymJKhyudq6H/wo4MHB1CO/fqe/j+/WktEHXYPmdAL4PriY35s1ix/NYP7bvV2jfBmwfb/9HEaFj5YNG'
                '/7aBIO67UIKr+NySpnNOZmXHL2rHZ7rnjP1OdtPJJWX5bLFgyNnFMfW+VCAei/7LwCxz/Xe6MRjVZdKGM1nOjEOfAxEm6Dvf+psQ'
                '06QS6Lre0X7V5yH44BKhK3xjqCWczWv5rAVAn0poIkDPSmELWpFUQoin8dD29kL2OA8SvtCd6oLQ4RQ8uSmIRLldONABdsirzcUy'
                'hB09qS4HXgAp5+ydoiJTeKeHbgQR3+ZjNxxLL8w4suRJWGmv6Xuna1lAeiGIvPh9n7pRflUmugF+Ws3CdAAnmeompW9ZRDXaUshd'
                '1fBdFDm9RbkXR3iZ4N7+dhNkS0cwc98KfS9YS64CnT6qqQFu5yuoElB/UotdY1vdGexXYQAKSAtam71PK2+Ce6sRe/2h3x9MKsy5'
                '9Mu0VrrYj4UaJ4621AKHXbTCS6gFZlYG9woNl2WiwcwYBdsYG4kP1DBT790PEAVXz0WxQ8I+TOw56a/hcUz6a0I0fAgVAwtsHgk3'
                'g2UPYyz9vXXY3IYTbwX8SpdxczDpdG7O+eVP+VplgqM1PUqOJk03D2lSzq/yK0jpC1UZ9wC15JZQ8CbFoaV9RZGpvFvH8u41x5k5'
                'vevd5qg0OIOL6+bgHS1pgmuYSlSu96c7TmUUpsXNaqZKrff+/iv5F/d+2sEBUNBit3zhNaCkOF3Aa0L4LPygrn9gjccXDQR5jHIt'
                'jqidmX6nQV9QU15+c09m/vkvgUM0hMfzRXGzvFAY1sd7YA0B8bpBUNvLUE8lFBxQ/H4WLoZiddfUBhaLsjIalQIoTk6i5f5U8qHl'
                '/UdJhWwov35gGyj/POvwC7r6QlTaXpBGk9SOvA/RE/enFSZvHhoqhH/T9HRj2KUVvCdQGNYDg1as+xV4L26g+jau10cUWBZMICe0'
                'YjgJbmtJzz+VgcmaiAbA7dEKtIEOmROpYLQuztSVgSbgqqLA6ooZ8uNTa1PDYAS369vDUFJQoDfwu5OGDlth7JakvPzk7ZNQ9ieD'
                '89UuP0ZoQ+pgW81WOE+MCnsdzkx6Y5IojYP3NgPCQUCJWSJb5fRB9K/yPlPL2kDjx0Xy97vDwKutJbMfX7WXxfSiNBe6Ule/kSnA'
                'oDin9wwP6QJP7bTVBvwgZWhtBcozlxHxzks94P9FdX8AUl3aY2H8fbaQF5n9W0NIiaUaXBuCkte0XckFBan7ZollHjxkQ1JByt4J'
                'wnra5op4Oud5bH2+fp8RgA8IaKldgurCKs2pCHZG1ir2XC0U1Mh7cEIVDBZGqm2+1PPJQRQNP7Xcp10Gy/7WxBqeLgfbecpDQXXQ'
                'NEH7c9FBHT2I/WNxifaIpuzNZovP52ftHQ4CJJhGTYpeb+hxbtQ0yJOrnqwR5FdrEtSz2obWNXkcjCAmvBRHy7fdrH2XClLiPmyA'
                'xZSGOyOu90+uc9zkrVs43ei40XvA/1z3oE3oQ1x45wKJTxbK+I21MUsfUS/vcxigo/uqQq1Hsnc+TTc1y4pvn+JW2W0xILOH9N3C'
                'WfmBYeVA4+nwVS6XoSbUMLXYxI/us2xpzrHexLrJMU45We9J3h2X8HKOj66qkCH9tvJp2v/6HQpZcbRoz9aB2hTeZLalzbxfPb4v'
                'tGKg74P3O/6Qnv07j/+sriY/9vIvUs61eQ/YipR8dvydClPy7WP8/Z0DteG13hQUJWn+sod9FO9uPisFkSkz7lEP+nT8IrNIT0t+'
                'acF4tZ5jjrPt/umJvJyPGyL7evcsr2v5I1BXyVHCzrjrxTCzzecmVLX0K7aF2a+mP/X26HsDXmjSz2+GSQArvd8A6EVHvd0jG0c7'
                'qqPbQFpK0doo3UijjT0HtYj9vF6w5tFLfK96EY3TlfG6MrDF+LKGxbUxUTo9pfabTj7qA38EQNHp8cWH0wpTdk1tbmJLDE1VXd/f'
                'SKHLMZb92yv1Qn3LtZmdQV1SU6l6hWb0VEvgS24aZPvUcXrxbqPQd8S29BnNs9qWF9HMUswPVojWkJJTzuSfn9IRtoqwTDqKkA/o'
                'JTbdEZz4zuAWMhf21xPoh/iCcdno6C/51vIUdZcohdaBcCe9wqjI9xLimSpZri5aFdoKaXgu4ploVqYlGi6ZK266aOMLYMko8KmL'
                'ltp2lufXMCvkbVh+hIsmq/Lvc8O2fRa7/RW0p+xi1p4hT6fRZYwEZtLzTNSOOsH5GP7HgtxTx4126LAPzhVceJ/1Nz5W8LTF9Kpa'
                'db7hmrFFnaPHyxVHCLXTaWIXJevMGawt8WzQdgyqEeKIfuSzbJqv/X1B4zK1evqMSWoRfb89fjU/cfsHllVDwvgeXtXEDeTvTzBx'
                'uzjuvFFkVVmRoQnCllwAtuL5WuIDvXIV0GeW8sOAnZz2amJRkkEcyAm0gZ6/UaACwBzAjH9TgG8LVv4Ul535GhaaLhiErgFvOQk7'
                'AReUXVK1GQ8P3mfxFPJjJrefWY40hzBvmUd3ruG6hQ/OBwwO3xPfVGGdxwMs/oWlusLjoyQOFYhXvrNoUZHQrrjPRcl5yfvmdLGh'
                '804fOyKtMBPVEWZWq5IxsIk6S0pYyKi1PeBoCYcMgOd3WcuLr2yBMzt61E8nq/qCHkTq7qjLR6XpBw3bYIouGDBI5Fkez59W5bXG'
                '8mZb68upZIETW6j2uLPiVw4IFkMX2GfR0ZTCrPjVw1B69xqert9htqDgzWYhMcQHOXr2hFr+gXcNOsIQ6CZLqS2osu+TjmRBSvJo'
                'Q63WEjKBUsnzpMeRWq3ay82NotgnipRRpBY/z3aQVy0t7dOb+KDXLHv83SUC7hp0GHy+oVutvWXjMSrDMh7ADfotPp7qzI7/YXh1'
                'MaQFWRfjlr1VVbmM1eH+qbonis3j4xLVjpSo9Cw63gtbKxRUiub2xAADRbx2cP3cQJHOVNOhQAWAHukKMFEETVCVLCg0wdQr+lRF'
                'S1nOImWhzXGnpV27PNvlDY42mqRa71fxOeyj88Hrj4Q81hnj5cy5/NuKkdWKjiqdcVNIdor8TkgeETeF/tMabqX2U7cM/W8diVuC'
                'uGLxxOzfEvPzUg8se5OLz7bBSUYTlwKL+9FCdWsZia7BZTureZhPVPPR8YACJztNl0YQW7fphHOyx8zKHgTMMctWP96TE5ncqo7k'
                'JJqjKVQxTyFXe98UtGPaUOH81ijO2R4yUZy3JdUyUYK7vXdPsG/0CMHOrPytGA5HDzYzeVzirgUDq1uHHfv7zN+OMY9bx/yzbb4l'
                'zN/5b11C//areUp3RKcnmINKg1xUGEL879/DV7JwFOXUEVcXmdT8mjvz9PJ+QVZ20fgaFyI1qlmm8HAqVItsDPkxXmyNluIhRrva'
                'omFksMGNOuQpC6JAzQDp3z3Qk5u6+3syWLeOWpQo13NFUMZjiMKN2t3PRHVeZVbA2+XLcc+bjNMXxWb3AHOgfdBNhM1VI+GzXLIH'
                'PV4+31LeUWNUvXko1sv/7D7wN0G/Y3c+YBFC6ZvimZYqzNbECmfKQSvWVZEY3giJ5TvN9xYsEwyvMmqvwpSS7Rr7GCdK0BB7aKyD'
                'WQRO2EIY6W+prLHeQ0AdgRXU1cTCYxuYEemMl4nlRhFYFRZsFTREZoZYsbypzFZgxUK33FU8sTAEECXigRXHn4rNxxAKPrxi81hQ'
                'BOOq6Ynhc2XBoBJsxWyyYiAsrK0FU8+NMSEGxvsLtLWbmIrMYH7c28SQT9h/PwumNGNZFzqZGDQWrLFgQtMsm6K3NKBZMCUuemKk'
                '48zAeJ/0xPDoIqEZ3Tlqw/nsnAtbJygHZthiHZL8PQ9RrXLGXDBJENoQgtaqXW1DApsjq794G8ZOsyg2jMKxI+eZT4KB+7sqC/MO'
                'AM470LskLRsEDaT90Xc2TuIGoQkJ3SJ9Je4hnBdkcr0s1pMdxT1XXHnF1RucbbQvEttXrmg/GJ2For6+s01QQDNUpy+BDaTqOXNc'
                'krkwG75Ej98aFW1fdfSmhJzci9veqWvdOzKOLOhk9+BW26M9lK6TSqGLfBolvxGa12FM0n4Nl4erjOvD1ucjeHkjrfWdDrTAu8rp'
                '7e/asUVd7EWl+r8a1rSam/DLO/WLo9W1dxRDqykQ3xZ81Eqrl28XzlpzjhcWR6vlOhelmX7F0Na82KI0+MMt0upGdAeOsZQ3/xGh'
                '9Rj1xoSCZFMQbdCqqyyzHYOPzkv3YxEbFXTwbGopafUKxL9Wv2COSwY3eUd8pcdvW2UVLDNy3XmMgtpps05A+VQhbJlHO1aEq6MH'
                '8m2IPqpmxdnAjXsiVNFSXtK292oU2atdY4uaX57UFOGohZrhPpNGIlB48zapBpleqImBMcky34oq4M5fXTIMVuH9HrVnPOzRntPV'
                'irQ5o5WmWVs0zmdGObMuDHtaYWKCk0X0pW4hMvifTEzAFe40MVYDutA3mBh/1J3BuRH+2vrLebmXjqyf2gecMR1TDMMCi3nOpxYY'
                'NpysAdGO8KYTLzLYN19GObI9o/8IUhYe62k4/pAgSmkERr/lrhraOtRw8OAM7h8G7ir7Al1dOqq+D21WQSx5PAI5stuUbTyR5GOd'
                '5vAZtcYyeOegfXl9W0GNwYU4mHk0fmK7Mr6hzbdwd78l2D2+BEkxVWSW/+LbYsSy31LynRmHF3f3BmeGxzHrVjCGj+nhIp6q/8eY'
                'dFkNWdh/D2K2RlRH/j1ZW6PRPrP4JarYH4pQk9AKtFu5PVjAAFpW51TyLoshGWe8Sf1sg3ycUHxTLTQk8xgtv95fnchwXju97PlA'
                'GbyrnP9l0U3S1bJEhqI7Bd0uyVJW/g3dLjwAsZNIZ0EJTrhxvuS4d2UEDkYfBSm3VLpDuoWeEnlDwi2E7qOfRFaTbBe4mZylRfbC'
                'CcMdxZLmuhruKHRb7eVZGtJthe4tWi00z9xYcXMc19fiBrODAyx+s8VdpiNd5t/Y/Vacm65Yd57V7VeGimwOFhMqtxmeDMV4Lng2'
                '92t/ljNIPTYGO+UKVsPEbSDPYCQw1x3baR8bbnCQ/+EM5G2HBkUw1pglRuQEHzUC3H+LsOCzfT7bR3BhCCdeBszXgR7B+IY8ueZR'
                'uNdNpkE1xnC2Bd5ZaAyZCqjSPHQe2HwJtvn1AyMNCynbJ1JcCDzLApkhLLk67ODJJAjcCfOINOhk2FmeAEugbAkz2FYEh4ndnsLG'
                'zLY4f1Zy33F6TFti8NNVHqfIWhQLM3pFhMgBJz/GWw9S97kcI8hNzGCOj/SasONVcW+K1tpImNhUGpox1mKURVxrtlwlEW49O8xt'
                'bRHuyBE9q5iPJcoIhHkvFCJnQxiQM0GkKSyLQxgF5Aez6m7Brt7n4ZLyCunID0p1MaGiCbxxnIcDNsDIQX9/kEmcIgODYPT+dGSm'
                '76iYEkj8ckOjD+rkhppipyuoa9Cx2H1HmbRdwVXEpW0TSaFbjHXxIvUYXUbVQAnJIKLkSiHOjnbo7t1QlBYhlEMEZ1mkMhQwDple'
                'DmcKE8gH+WDe9tqtjN9IM3FsRtG6LXKMZ3J5ujbIYxdCBOeAoSm8J/CsSmYT2WB0o42b9K9y1bQZDE52RbGiOPE4UDfFzMOQBBkI'
                'iSS5zS4Tf5kGF0JqQpW5cny+wHB8+w5qCrnhIF25UZTZowNHu8khKzDDP0SSI33bnIRSPM7kgE/RDHGnNZ+Y+FG5Ev+lyCke4lDf'
                'myO07oDyWFpFVTIGL7o6mElRFgLmZLlSqSD3FaAqHKIi+tD6kaVCPrxRDjScPxhkpHwzGF8PPENZl2rh1nwhSsVqYehKvgoGsv8g'
                'wivlMQbhOXp0PKLi6YqbI34RF+WLv8DE43/jxXXarLOudCaWzs6CjC27ZxaXzuzS2V46A8zICtOZYjp7zMgo01lmOvPMyEbTGWo6'
                'a83IZNPZbTrjDbLgHpPfFPiq6IVc4/+6i5u0mU0J23+PRhnruhZypd9KaiFKeGB3yyCTCoxzOsdBgPAWHk5YlmUhXWBz2Jctm3Ww'
                '85VibHYFBiZWY1FzK31I2AGaK7PwHWzCl3jR6x49XTS3hgiLP+AnoginSRm1vdgYkkqRoPaTfk7ILUw/ENtBpnHJbw0EWkAIcpq+'
                'oOvdUT7hLbdw44gyHAldtuHUXVekmviababZnrefszRvNHhi8weW9iLRCIJI9otKwRsN9J/T1b/0IGQhowdb3/VZK8T9YTzk32vQ'
                'nuzcM/PvjkAwzhpzTf4auNva5Pxzn1UU8C/fCmGqA4d1xFF1Die0ddz+CSYIchjtOcCh3VEAX0EujPpP5zil86BU1l/DXRTs+Twv'
                'b48qjya0cZSZzvUTS3ty77K0N/ch2Z/uPyYXXJhTSXCGp5eevpZ7au3zTM5oo7LwviEPO1VB34RjUNTCuo7IhsOnDjWTK36CZsgv'
                'TEAO/UVTAlSA5bGhpgIWgUXH1vENrz9mOnnUqJTl3V0yAFLi2W/is/JOr30hwsOlEfMXwN02pOWemllRwF7zhaVlGIfHW6MIMHnl'
                'ag//SL6pxQxTpaL+GYMZGMgLUKGLgblL4wHRCk5FuH6xzw9TORhoBo2JhvrSu5WIGCXclO94RDV4L7K2l5AeGzPyTs+qqPoXNGh1'
                'Qk72ybkiiLirCuCNBW70uNuIE7SRSHAepz8TXmY8T6t8UypHqKkfw9lNtSstrfxhK3tqf8QK917nEasArUwJMMQ8qG9Pl1I+Jas+'
                '8MZqZoTtZbQHtHDyaLIVJoHPrzibXZB46Kfx7TjTrf75qVyx5zblwfx4LbyMcI0JxsvD8en7pSov48I7qRhtkVZ4vWvz+X/umjyy'
                'Li33tKJX+xzr/I+x0sftIP1l9vQvNYnDbwpzA0+UEvSHlsjuHvRa34NeG+jng/TzqD8N1OVhfYxeo94V9Dnag1695or2DpeU3nV9'
                'OtDrvR6G0+l8zEvtH3FfWZ+gRpjcc1AkpIgju5EFPowqYa23Np7Myk/Z9/lD3kW5/J8Otl2eWJC4tA4Ht4p88dxWVu581gvB1K7+'
                'tZEom8VJFwemAA4EMN1L8qThcdKCcjv6rFS9pf8O0OPPo79/+M8Yx+udPY9bfe+Png9wv4YtBWWiMFxPL/Gcn+xIPBc+wdwhzstf'
                'N/qrpI9iYDSJfO0rYTRIzbaL+zY0e7wrn7dhMO3r8v0NYFNzPqfKA7NGXlddPhwfECvsekrDcfCZE1cv3Z5oMCs4n9Dtqwy7trOH'
                'bm8NGLzCR3X760Ose+Ejuj9NQPQr6PznUNON/8Ccsd7eZ9vVzD3sS1jeA3dczfltuB//1s4vq3l/f4zczS9+9iHHLIH88mIwx59o'
                '6M8V4bT2Jdrkoex2TAa6HJNhUSB+5SKYJEUhGkaEh9/3mIz3B1EhQ8V2+x2TYwPhSWeVuflfh//fx/EgF+nVtRdZ1vvKF7hQ8riK'
                'EL3cRlrnpc3qQVIKAukyeweWHARi2QW/4TJDladm91yndkd0Isw+rGy2mNG9+ogV/t7zec/ySoE98VqvgNAYXp9IKRftgQY+ob7n'
                'lcitsyVf/ZE5MxO+HxDwf0Cn+bO5Log1G0zpynuhVbrykL7v8NAGhntoA6v+am1g4u/WBv5U7YmPX8XPzznX4WWDFMl8d8Wjwx0n'
                '1D0uOrD1pDjtXYDLglB1eUBPxqYi8/IfXjIFd8GRa4XJB1aOvM9LGLmp+FJNZ2pCQOo/VnOEVGszcXd7dEgpNwLXfs6tnjawEZih'
                'IxPlW6nvsm2kwhIVGbAYl3TLmKlrspGu5fs4q/cN2Dis+Z2hPndgzEl10+hxmBhQwt3Et/Ew/DrK2R9iAlX4ZGUjlPKG11/psg5d'
                '7/r3lnn966eNTwF2RLcu18aiCtXGKYR4cW0fsD0DlLvBsHt+rj4U0Q3Az6zgbCv4qRWcaQU/toIzrOAnRHxrkHYDL1msYkbdEoVt'
                'yoY7VDdw1LlfC43m+n+3PpaV1c1L2KZSh3GF2GfI/uycwxPDeUXwjQo3z8DEzxT2xpioEcp1nOaHFIiZhfYL3BXZUH5GrJX8bEGc'
                'aC60YKt0vKb6Ev9MEcvDQ626ohckjadCz8GYjh/1x5IaoXfFKb+EIIo9LO1whj+XF4nFcmd7ms7A5kraNL3eeU4jn26vdBEp7mAD'
                'DJ94xeCrHAc6V1dKdbWjkIfW8grT7ULJnixEbObXrEL5F8A2i3gA/M5DbcKDTAYTRy7NvgqexZflNsJ7y7zs61eD2Xy5XHpP4Pcg'
                'mDt1BIvzmWRLlV+EigR6q72JfcuBjfYuDDuIVmPyei7N8fW6RgtHoWVDeWoSwGkNtvEUSU3qi0SjlMNQZNX6c7NoMzlAzhDz4zbg'
                'aPbOtITlDFf+17WKH0aBFL0TtNWyIHVusJPmTv7NEzuYUy9D8BA4/gobYe2uFkhGMOcnmoK6PVKEtl0Un5ddJ52UzbiJ7VKUJb7M'
                '/AaPjYvB4zz9oa7W8gMHhTy3mibxD6dGgNlwZQRUtRGqsUE3LkeSli4RjPcWLIW2IuTA1ZJ3BUO5veEzMYmlgafmR+rvFbctCUQ9'
                'VIXExNswGuMUzLc9kQdXYcR1a7FWCmA8VvHEXvRtLpEfBSsoTXxg0lqoOR6OS/+45lhn7PO1x9YXvmvyMJP4cuV3C0ZCE81vGkUI'
                'g1JjNUKzqbBEyOMut8feiFObHWIghkiOJ+ywTS8JQjeD5JcSK+JkpInIOTI+1JKIJXeN6wMi63U7FZ/WZHZVTJSKRYnMF910S/iX'
                'wVDGWom+VjuKED+hj96GURnCkTENVyl3+Ywz3SCHrvfFKyvAuz50J2wCSF6+2/md1sYgcOBr9BOIEdxmfqhqr9B3FTBeAvtM4JTx'
                'zaDbXGp6HPU2qWRqke2Lyf0CmO5nAHQr93g66qIaJx2u4YWKWoXmN7bY5gAw0fxA0jwJoPbXJtAIW5Xd9o8zABIwcu81GCqWV1Dn'
                '7/ixbuedXSw+zMHHwPmIOSAXOF/xrozUcrfpJGovAy8sUW5FAPURKKcKpGdHktzx5egUDIzi7uvqieaANDqngU4Fxh0IecnrH8nf'
                'yVTULirtXVxz7CYQrdQS4lUOc7HqG92+4qMBd285IPkXvm5a/Nc3AtgwlZ8RnxcfK76cUW6/Hxks/GcHX63mV2VUJvVr6uHYc7PP'
                'w8T1Kh3Q4F3hCbnSjjR+g4+4T49Vl3MOjoH1X2LimfyTIx3EsV145V+kSQ8GtEmmfZaj4vgyXbIcNYZBdOlL9FIL/1ZJ9Fm/PTzj'
                '2EYCJ58viB/rR278bdP/AeG8JNI='
            ),
        },
        34: {
            "ascent": 32,
            "descent": 9,
            "glifos": {
                32: (11.844, 0, 0, 0, 0, 0),
                33: (15.5, 4, -25, 7, 25, 0),
                34: (17.719, 3, -25, 12, 9, 175),
                35: (28.484, 2, -25, 25, 25, 283),
                36: (23.656, 2, -26, 20, 31, 908),
                37: (34.062, 1, -25, 32, 25, 1528),
                38: (29.656, 2, -25, 27, 25, 2328),
                39: (10.406, 3, -25, 5, 9, 3003),
                40: (15.547, 2, -26, 11, 30, 3048),
                41: (15.547, 2, -26, 11, 30, 3378),
                42: (17.781, 0, -25, 18, 16, 3708),
                43: (28.484, 3, -22, 22, 22, 3996),
                44: (12.922, 1, -6, 9, 11, 4480),
                45: (14.109, 1, -13, 12, 5, 4579),
                46: (12.922, 3, -6, 7, 6, 4639),
                47: (12.422, 0, -25, 13, 28, 4681),
                48: (23.656, 1, -25, 22, 25, 5045),
                49: (23.656, 3, -25, 19, 25, 5595),
                50: (23.656, 2, -25, 19, 25, 6070),
                51: (23.656, 2, -25, 19, 25, 6545),
                52: (23.656, 1, -25, 22, 25, 7020),
                53: (23.656, 2, -25, 20, 25, 7570),
                54: (23.656, 2, -25, 20, 25, 8070),
                55: (23.656, 2, -25, 19, 25, 8570),
                56: (23.656, 2, -25, 20, 25, 9045),
                57: (23.656, 1, -25, 21, 25, 9545),
                58: (13.594, 3, -19, 7, 19, 10070),
                59: (13.594, 2, -19, 8, 24, 10203),
                60: (28.484, 3, -20, 22, 19, 10395),
                61: (28.484, 3, -17, 22, 12, 10813),
                62: (28.484, 3, -20, 22, 19, 11077),
                63: (19.719, 2, -25, 16, 25, 11495),
                64: (34.0, 2, -25, 30, 30, 11895),
                65: (26.312, 0, -25, 27, 25, 12795),
                66: (25.922, 3, -25, 21, 25, 13470),
                67: (24.953, 1, -25, 22, 25, 13995),
                68: (28.219, 3, -25, 24, 25, 14545),
                69: (23.219, 3, -25, 18, 25, 15145),
                70: (23.219, 3, -25, 18, 25, 15595),
                71: (27.906, 1, -25, 25, 25, 16045),
                72: (28.453, 3, -25, 23, 25, 16670),
                73: (12.656, 3, -25, 7, 25, 17245),
                74: (12.656, -2, -25, 12, 32, 17420),
                75: (26.344, 3, -25, 25, 25, 17804),
                76: (21.672, 3, -25, 18, 25, 18429),
                77: (33.828, 3, -25, 28, 25, 18879),
                78: (28.453, 3, -25, 23, 25, 19579),
                79: (28.906, 1, -25, 27, 25, 20154),
                80: (24.922, 3, -25, 21, 25, 20829),
                81: (28.906, 1, -25, 27, 30, 21354),
                82: (26.188, 3, -25, 23, 25, 22164),
                83: (24.484, 2, -25, 20, 25, 22739),
                84: (23.188, 0, -25, 24, 25, 23239),
                85: (27.609, 3, -25, 22, 25, 23839),
                86: (26.312, 0, -25, 27, 25, 24389),
                87: (37.5, 1, -25, 36, 25, 25064),
                88: (26.219, 0, -25, 26, 25, 25964),
                89: (24.625, -1, -25, 26, 25, 26614),
                90: (24.656, 1, -25, 23, 25, 27264),
                91: (15.547, 2, -26, 12, 30, 27839),
                92: (12.422, 0, -25, 13, 28, 28199),
                93: (15.547, 2, -26, 11, 30, 28563),
                94: (28.484, 3, -25, 22, 9, 28893),
                95: (17.0, 0, 5, 17, 3, 29091),
                96: (17.0, 1, -27, 10, 6, 29142),
                97: (22.938, 1, -19, 20, 19, 29202),
                98: (24.344, 2, -26, 21, 26, 29582),
                99: (20.156, 1, -19, 17, 19, 30128),
                100: (24.344, 1, -26, 21, 26, 30451),
                101: (23.062, 1, -19, 21, 19, 30997),
                102: (14.797, 0, -26, 16, 26, 31396),
                103: (24.344, 1, -19, 21, 26, 31812),
                104: (24.203, 2, -26, 20, 26, 32358),
                105: (11.656, 2, -26, 7, 26, 32878),
                106: (11.656, -2, -26, 11, 33, 33060),
                107: (22.609, 2, -26, 22, 26, 33423),
                108: (11.656, 2, -26, 7, 26, 33995),
                109: (35.422, 2, -19, 31, 19, 34177),
                110: (24.203, 2, -19, 20, 19, 34766),
                111: (23.359, 1, -19, 21, 19, 35146),
                112: (24.344, 2, -19, 21, 26, 35545),
                113: (24.344, 1, -19, 21, 26, 36091),
                114: (16.766, 2, -19, 15, 19, 36637),
                115: (20.234, 1, -19, 18, 19, 36922),
                116: (16.25, 0, -24, 16, 24, 37264),
                117: (24.203, 2, -19, 20, 19, 37648),
                118: (22.156, 0, -19, 22, 19, 38028),
                119: (31.406, 1, -19, 30, 19, 38446),
                120: (21.938, 0, -19, 22, 19, 39016),
                121: (22.156, 0, -19, 22, 26, 39434),
                122: (19.797, 1, -19, 18, 19, 40006),
                123: (24.203, 4, -26, 16, 31, 40348),
                124: (12.422, 4, -26, 5, 34, 40844),
                125: (24.203, 4, -26, 16, 31, 41014),
                126: (28.484, 3, -15, 22, 8, 41510),
                176: (17.0, 2, -25, 12, 11, 41686),
                183: (12.922, 3, -15, 7, 6, 41818),
            },
            "dados": (
                'eNrtXXdgFjX/v6dP26d0l9IFyCyjDMtyvSJbUHCgIFRkuBAQnCCKDFFwsAVlKcoQlSGgbGRvBURAEBmFMkoLLd10P80vyTfJJbkr'
                'gi/81Ffvj97dJ0/vklzyzXenKSLHhqZ/8HQ3Pa2vTU9f+9LTGCOVnPob+8npQeNbcoo1ppBTiDEQ/8021OPa37cD/6lnGIPwadjN'
                'vhbVW4NQrgufP0WoOFiqtlcOQuvIRQJCP8jtaY7//TV8ronPo+SCURhoiM/98bm5XLAboRQHPuO+yvGW8MAihBbis2cmQqsZ9gOy'
                'Oxrc0AJyNMaXb+PzLfg8Ta7sSxi4F58fx+fucsFi3EEB+PwxLqgqF1xA6Cdy/hmhJBmvhn84GZ8DihFawrBvbevU5oYWyM0rj88T'
                '5Eq9joF78LkXPt8vF6zHI9cLn79AqNBPwl25CK0iF4kIbZX/oTV+wiv4XBefh8sF72GgPj6/iM93GfoxHKEm14KNsMHe0rCoFxfs'
                'SUMoY/v7rTwBCZhWZPZFypRaZJTtU3voJMamIgvml0cujrQfi1CzmO6fpRGsGS2sYgyD93p3W2oYjxIo38ExetxLf/eogoWXEKz4'
                'Kzy/bhMVXi7eWPDTp48FUqxSolyT7PG08yMXuWX0SFn60+ih23JNcC5/quc4hDYnUKwogIOkLh5DKNhcxgwnbeij7b9obGJkiCLU'
                'uiNCx8c+UtWFsaYNVtP6h3ZkbysU711odNRH3ckowytuW4mElCyIoI+PfPqTH5NwW9J+WTKoivztRl7D9y1tHNiNl2Eq1mFJYkH6'
                'nuESRXsS16oju/ZZyKp58U5eXDYFoe/4zWeiHZcrmVAOv25EGjigzK3HzK/QFDd+EP/3yRhfgc/tyVBxUWp6GKGDnoZE5J7GZ48r'
                '+OIOgryBHyiqYpzGcDtycRJfPITPVfAPpxtK+X3kIp6uQYaxCqHkYIXgomf48283jM741E3qnEmsfvfhc57LCDiPVzm5LxuS9vUv'
                'U+8oPs+hzcmvoXT2LLl/GuHBMwJPvdd3pxUmLe/s0PrXYy9Cv7mMBucYtIYO0Q5LEwsz9o7AlX4BYy2NqGTxyGXKq6Lw4jDPMGbi'
                'goQmPs+6GXkWxyI8tsIMz2yMdwUqjeZLxaSJz7IW+eD7J/DFCbO4DO7BnbjG7Qi54KtblkLLivCSSctTCdASX2SK4hg8Kz4gF7Hy'
                '84+L8q0InfYlF84sjHdh9RMT9yl80wEup+PLU418nnTT3oAjFLMa37DrSLN/OGR8jqtaQXyz86x4lT9D7sFD8iWzKQFv7E7H36eT'
                'gwMe7eccySi69OumCZ0rqnOp1o/STPaUS6qnoNKK1qDSisIoLSt5Pcr7lse/dStFd9Afb4SbmiucUtGttOiAYXM4oRad7coG0aLM'
                '+jZF91Iqh5Ki9QLHKE66ztwCNJlcu/HM9ZhrNuk4pWh3kcvTQMDwcQy+y6GybMFDazGZpmvQ8dCGmbTsxwDWOW8axjiKtMDjKJ9e'
                'bSlTg3YOru5PtG7kFZ2A9q/+nvz9FQOU5dxPa9ZX6uPH8X0SXeg8OPlkxwEC7KWXjORNYyVZNcndu/Q6uSaMgwNQ9CG9q0qXB5Qx'
                'uKpXuQc3sP8qotSGsreWI7uh4P4sxwWgmPfHm1DejPvSYU0LZqNw+v5LhXnJu2d2xf3UCpaZLd6UV73WP2bPUF6nLOmvnHBO6dAk'
                'clWRtKu4igBXUA6UTEv0CLnsQ9tCprCxk1wuIlcRdFz0IZc9aMViRF/mOjmlRT/T918ST/WkP/2MXAbRy4+1S+kH8G2X08s95sM+'
                'oa/w4EQCodoG4+YQ6m3+eAG9HEBHPOWsQ3LI9cMUnmI++RYy2oorC+KPJgKBuUw6KkzqvnKkQy4AE/EOQcbB4kgWkgJYvynvNJte'
                '1qNjo5JZnwnmFEyl9akujUHKocyhl/Po8KOXr9JfVOW0GqFO4slUzDDCkaiwP72cSakZvfzE/MEk898G0zFnkgggCdUN4G7xokRf'
                'fEbwUDUY+4aP1+iaRqu+V7yWUiLovWmiDaFml4wSHRUqdR8co02m45qQuJUNTOSBPTUM12lUsrAWIC3wyFxqhM3HdKx4NqZM7xAK'
                'kfMBHiY15xXzCZYzFj6oET2XYlfGhYnl6mtKWfInR8J97S8Fl5k7Ac+XsPn4vmgmZnWGr4Ink7d/HQ1vb7qdvN3oujLWrGH7PTX+'
                'aEv5QWjMncbfFH3Wjuqd/+/R/43eMYwPaHMGXcPFQMNYRklwVcOZQS6eMwyqgFmDH/M2PqdXYPSWSOXBxXQs4iEsib7Xe81qcA0n'
                '3hxCaVtLTU3jvEwwXvK/4AXdORUjxzd4yePytCubrRDkeIAx6fTA2hd3OOfLMEuxnRfcDV0DxzhOxshxHKFf+HVdWRczFN805jeY'
                'LJ/l1xXwavYRv3lebsr3UlOCCqWmdJObskhqineW1JT75abMlJriuCA15S65KWPkpvwmNYWTqmHbz+RlHF/2tCTWhH4qyFVqXw6W'
                'PypPnOnA3fr8qs6ndyn6Pr0+28E/4g1KGYsI51KugEq3dZgMiUDb8aokiQRRVq24AmMMsO6PHtvpzQDDeYVeNDP5eLJC1IEXRwuB'
                'FR8HjVaAhgDaD7gw4xFAywD6NL3Jp6MIH16A9mBsNfutL6DPsN+2Vp7bH0QvOirwUcOQuMNDhjOX86CC0SDLILTtBVkLN4D3AzAR'
                'oZStdWNZIYxyaUV1BZcA6juYLGfb+4W/ST9UcSO7b/HeVb4bfsksm29MxsPw7WfzM08se4aPh1vaD573c74sENWTnvffQnXPrRnb'
                's1FfVd7iWoR/OuRpWa863kjIUfXBIV/uTsgsLEw9PP9pqiRroUocgz11CM9VbwuERhPoxPsdKroCW65leregpouFUnI+YF1ldQNI'
                'gm/IjQdpc6SEeIOWsZcEwQQtijSRChdNdhWOisdAkAwUSG3KhaLEagK5MxUEUVNIbQ8E5kB5gfSE1683Gc1BUO2vhHrdMR7aNkmI'
                '+15fgGJusPgnPxDZi3qaNbRo9tDKGwkZC7gUmHJwwfPQoAXyL4qmB+oQbnmwBUKfYtK1blibuhHeFe/fDFB+oPQ5oLGolUxCTKmZ'
                'H2DTYfKS8itZww86gC1C+xB+P9WNojQqlBHdHT+2A2JC7qlBhqH/KusNDx3iEhWZXaF3jLiETFGID0zQ76yRByaI8Rd0Iwym/dP7'
                '+nAkAhRve9aizNlP1Ar0CGz0ehI8fuha/QOdLatDZxsYKpQ7pRyWvpq9Mn/3bxcLCtMTNk3tHKSs3K6jsjpBraqGxhbZoE6hr5fR'
                'wcgGjSZLWYKGOshw2DVCQ4l4n1d7mIpWyKTSooYSJf0ep4bGEdpR11DRUPKdhhoaSqjKfk8NJSxSYayhogFnBF2RUGKBOuSlo2/Y'
                'yQmRNwtVFeuWr/nHUV3cGXazsJVqHa4LS9yVWph1ZtWblWyEvOLPA23acSLKpi4/4UHQa9f7XZpU9vFrOLYAwD6KbRiUbfuVKowB'
                'Oh0qY3fBPzfU7YsaieO/a2B9njuk66z62nu3k3X90NvtKrh8G4xh9evM1nrp+M6wYGt9dOzSALLSOGPi3lu570RKYV7SvhmPycZe'
                '30c/+TmRGZHAUON87oL0/xTzW6U8k2A+PyILBua7nIn3hHhFxD783r5G3MqeoJgpqIXUrfRFRbfVwvAE/ddnYsb/lFF4cec7lUx1'
                '6VbOixa+5wTRVmU5PEBpqxwjjVPMAjYyyrsJCAm5UccBo9JXAKiMX9gjf6vJwGDBilziKY27XfD98qCyXenN3s7W360KzrU87wPQ'
                'tCnvvceonc/r1xjqt1MhsNC59DFjFag9VKFXkoB2xvBO9O+1+Djuvn2T7qG3lpUF5fxRKNUKyQQmmKpwi2XbIpC0BTK/BiPtNgkC'
                'MUu2aDtAUHlQgh6kyG8OCdqGmHJCs2Fc9JGgbyg0QkKi6VDKLSdBICpOlw0l9Au65UH8tsUk5gsMYlMJogpgxUvDGW+xkHShSLxs'
                'Ytkry3yGyWhflh0AVkkSND9qDll+Ir0oL2X/Fz3Y4h+xUPo+6QNJj5U/pX41ou9epn/KzkZ5mGR7mwdE9ckCvtboAHxShCklp7Fp'
                'upm+rQqQNCZPA2dWlWnOfDPM/32evxgsF3ubBUTCO7IIf/eubLBGSXeD58TXQgBNeguETf9hZ8Sv3Fuowa621rbZnkbQWXq1qElA'
                '1KMnmM56KKefxKZEX1x0yy6KgUHFgF7rDS4AdQCDSTc63vq7YcDpLgVSBp3VA7Tb6KvGAREdQb5whwcn6/08A5ucclRoF1nIbt0q'
                'IQXj2Ydv8PaqUxlF+amHvuoTZooLvReezChI3DtG0u/1vyz+eQWTYTzmK8sCkKMJ6qsvk+UylnZ/yVtRrjt+FP30pTnBg1PZpPW4'
                'bNpeGGX+FEx0qMAhWcUuUbcXPPxkuo4qxVp/iR4EowF7JnMHeYooorjSP4hZOl9hH7FkeKT37btY/V8z/M9YqBI2M9+aoYPEqlBD'
                'cLSJQGLoOuzoMOd4VmHyur7+tPXpHqrZm47Cb1XmBNreVsFeYKolfIxfM7hZdID3LV02QosptzBDrU8/wwIW9jAs4NpYQwGz47cM'
                '58xHE4rsu4aTcb3HdTz6es9/9Li25+9lo20ACIsbHMQrDGVWMuqT2yeBAJHxvQ5bayPs31Rz5GYdinhpj2wMoMSox7pi1URgeD3w'
                'da5uOPjPtFQx6CbDhI0ZLYhW8tRmdLiVH7hfOEvNbAUjsOEGTgAvf9bWUzN0ZMxt76VzyyUf+9nw0OSJreXFpuFG/tyL01tKg738'
                'oJ8Fwf24mVRQ593Two48pam5Bjvuni7adm7SHVI/PLjA0g/g+tDz+2IrSrwqXt5rg5Jv8fbmm27aucHHzapv96WdXLZvy5jV0sO2'
                'DufHNbCv2eEhlSXGrfcGbrMs2d5XknbC+20RfPfyLmUkmvjCDr5iZ825VxpbFV8Rvp5Jo+U3V35tn32vNz9lQcu/yJ5uopEDtrm1'
                '54b328yhrLltaR3K9dnIG1K4oiutb9Cz33PVRsmOfqF6Pxx5s4qlz8Y3tPTvZ630/u2xrLOP9Vv4txm64Mf4zKK0X77o4tLUZ6db'
                'a7qzgtaaLu2U5wKUPL5dhCv6IwBajnvWS5iFkOxD9J4QseFYzdc9ONpC/3Fd5m2ZEreCFZuwNiZFMR86KL1cj/UrsEDJt5q+TaS0'
                'LnfYA96lg9CbQtU1HnzHNU+WO7Xf3+h7ToVHbzybW5R2ZMlLFp8jj+7HpY+wqZXqM35Ym4VLpPnRh0jROXN6xIR4BjXovYoMx3N1'
                '5U+UM8Jf/LjGeiJCMTGtJ1FKKL7LxlP4YfGUzW2IpcLNGiU3OhczJ4tNWAwKtHQjtjSVNKLecW6Q6VsvS84/NSmMjOlyhmMbtSxt'
                'Zh4Tjg+ZSnE4LSVMfp5PeTxmbjVNZKT2UEqYvhbYBvYb5e3xbCp+JST4JTqriBC1EqFXJ7K6Ebve+8xXFEoxo/Q+FjVeZhbQEqrP'
                'CilgpdhONQW3h6q907gfCrGn0lLs3z1yE7NnFgnD5A5WiqfEc99SVy7DSOeuJNRPE5f6Y019zGRWK7yylNCxHsre+xrxM8bePAmc'
                'yf9ACHjljDtyiTmhKmMOo4mHx6shQS/Q9sa+iQvXOGlT5iu+VplcDg8EG42bdKUH49kS3oT+HE0XcS8sG/xKv2C75RfzT31Y7lmU'
                'd2bJC8xkaLTC32GVROc9VZpPrHw/RClr6teSGyZ5Y8or4l+cPeLRKV/JJ4/Qx6SZHWsFuSrfO4Gu6m9Jj2qrCVPuj2QPGsOrv+Qh'
                'nff5rfog9Gw7YduF/ILE/Z90C7XOdG5mrGkpuc00E+nHR7wowaGVeJkOkC20oofNWn6uFS2RlP9llJIQqovJAoVBN6UIBN/5DyHm'
                'VqhGVBAhxkW/f7H8XcCXKcObGUAGWUwDc7hW45Ck+QBGC8cDeGdo+kNwgb/sJcwgEzQn4FnUmxdIO1+SfeApdIB4pfNnCz06HivA'
                'V86GyBplNVGNDUByIoptGJNnJPcx7QCtzgG7ohKy8ta3DZ2gUQxgNks3P9LXYLLDg/qCqUozIyBojAM4rqFYqUfjmXIH5Nk98seD'
                'aZnmnWAO6tSjy0c2MZ3kpGNnrA2IMhvbgMR1MEEM6JAHTnGdcYI0ymGhQn0V0MhiC7sCZtOb5xXwdvj3uyUw+P6ToO22qdLFaCu4'
                'KsKmRSVLo+xadLa89KIyMaPymDuCUk8m0kcroAuGzLMKaMAnHKmAPsDPDVFAkKpRDxP0qT0a3l4SZa0n9lC3ggdDLWDx9GClmcQM'
                '2l8hq7c8NXv/mZyCS/s/6ynMao0XSeO/YA61MTrfK1EfTbR/Ppv0OmDUsRjZoC/x1fbD1uFegdU7T0nGaACzO+4UVXJ2m2O8wprj'
                'a3H0QnocRpl8Oz6oJvz0bRWF6DrUU0U7INlr+eq/rWX7XN8CW15so119OfnQ2hbAiPwOsx8ex3TzZd5nk1qFewZU70T7zPBYYte/'
                'RpmtdqjhOdbmu5GJtUQK+CmYW5u/uNIzcw+cu1KY8vPnPc2hU5yXeebAig+7C+d/bZy517eyxYmaMNAeR4fC7XG0w1siK/6VH56W'
                'zQomG+o8DP2OCUFVVdzwYKFq0zXcKAdc/Vkdp9EeZM3WcbB+oA46Duw/elLHmTH/RR1nZrJeOt6tlOd/zjypNDwy17b+zjW27Q1b'
                'be0fv0oPT8/R+7O0/r+W7zXf7vu61zVXxoM7P/PMzysmdYssZfyInrxRiMxh/TeIpKC8wciNquH1tQJtuGnIv1/wb4YIothlyu6T'
                'aUWZ53fN6ldN0obOypdb/csAYI09hhQhGxcIw3uVlWSQAsd8ZF/Qj3tgLYirHuhVrk7chGO0wJ+Zkg7UNutSb9pLLNoJy5RBegNA'
                'a2T1DfeBBuyytLiG7TpO1CdIdrP7UNS3b3uFS5AKVEZBKmC8wluWAsYuSIbgBYxD3qj7UvACxjT8VEYv4HzD9vJagWAdcqd1KO/j'
                'imy3nxfYcA9QYMNAsAIrD4HdBZvasBGoaEM3M9iOcRKpJ9eNiwu2GYLBzCD794Yt9uWbD/+P9eB1wn+Xk4Xq/pOvwXj9jiT7vyqx'
                'y5TeguIC62ZdjZi9IMWRLHk5ieuEYHGdgnWXcF3yLRGdkt3pp1YMjbZZ8HyZpDrHQy3w28L8KTzU//BjxPAzD/VR/uDAhGY51HcE'
                '7AD8E4f68kAIc0AzHeoyHLhbi0NgBUHMsDTNoS7cHzPnrY/1Fb0E6VoihWGZbNgXKClI5IKfQkopUEsUAiWXQMGqdEsJa2ATSwnv'
                'EkuJ6MTGWonZ7VqJ9KEap8kl8qdVSpTB0EgqUYePVKJRJ7Pkf4Mr/LsgN1OmGWxx60creVmCMANHFOhlphZpBLKUbeIK/QvWMhZR'
                'TnMAWcpmyCp4qYy8/kqwcBkpkMvmIx77Rv0xv5DLWpLwjlOYroUT/vjE43JZg5nMI5Fax16KU8rqga+cF7GOZAeqZQalrzGPA43S'
                'ymgM2VTiy1RSSy9zJvC6rzX0MtNHtIO1rCxzvTjhsJaR8EZuSbaUQZ6H7EC7MmOLILLWsk7QANsy8/hTy3iwG3eI5YzklUhbWCwn'
                'Gswi73WYJxLRYXcdW5hZ4hWYLle3W+BFdP5Z4LuTucO5Ajd4gSsyVdj7NJuEKkxzT6HDHjrscYSq3HUYMi6d8tJhyDjwvAWmyZiS'
                'tukwzIgSC3ynhZ+HD/qdPVzPbQsLwqTB1QptYZGOQ4OjcpHit+ts9c6m45cLU35bN/Q/qs3z2RMSpTzQxTRTRm3XvdS52b7aBYsE'
                '8yvklfL/xUa6We+ULaHLO4R7R3Vm3BnN+1UexPmS5ww5xhUll+ExoZCSQY7xeppHluaaUb1VWeSa4V9kCTvcyeKbYizrAGSxQMgF'
                'fv+K5ZQ5xFboYA3uYqaiOveU+l8VS3+XD2TJsqlhkmiXqQypUsKNm8xaP9GmNyqwPuytRMqgZF+WZ472fPtyXpGP8p6nfHrAYZvv'
                'tcH5O18Zj40dpY0NvA4+d1IeUV0Vw7ez9egtWCeVeuz74XfbrPvZ57dNauGwYwZ+bW7HIZT0tVNdl7Sy03MflLn6BlPZ9Kuj8CGQ'
                '5gz1VsDKTLf1++CbSLcVBsR+rL7Itkq/V3m7Zh5toXbIlQs7PmzpKFUj+HcBNXp1bP2I5o7S6dXRJ52l06sNYaXTqzPlS6dXP/qU'
                'Tq/eKp1epQeWTq+e52yelV59Uzq9SrkKvSpTOr26pXR6Vbd0elWFJRoYaH2Xf2Cx4l9h1vA0WzxRlq9Or74UoZoj9d7AaZIqAVdb'
                '9JhKr056Su7jC9qGSvSKxlYHHbX5Xox5ibaEKqAVPG6swk5tQo3xlOiV7D+3pZHqXNdi5IbjqdD8nd52I3UIjyK2ORbw7AfWw5c6'
                'lRS1sCurTLW/KVXsylrQwXLAT577+ZePrXirYSlS1Ppq9sJVchV7++1ye7i4nDxjneGdz5m+S/JEbmtGK8hwJMCtNRj8XYrKyrBH'
                '+KPn2UpuV5P4CDt4SYRNK9Pus++TwqdKETg7KXTJVecjGMqpZTVyxcSXsRrsAcr4nFCtleAmRaO4ZJiFiV0qo5HCpwXNUGDvRB53'
                'pRLOwXx+qHBQJnOm0cjsOCm9a/hL3xxPK8pLPbJmUs9a4HcxtlDukETseeW3TTfkmSyFhIUXW7Fe0N1jbgtyBtXoMimeYCM1itZk'
                'ThwLLL1PGehg6FgqBwlwd6tzkx+r5dTCyug82P9RR/BqDlNShWSNo+58/pMLlLaBB0fEy+uvSLOCO/551u32ISc278h1aJZoE2kL'
                'slrmw+8FqrkvcZ3i0KWh4ar64DyNAf/2hUYRXuFNZ8EYWxtnJWzPW7EEHwuW1sjwf3K9Yrz7HgL//O9/d9mRlPyi9PgVb1FJ7rC9'
                'u5rnzcYNJQbIGkLzL/73xjUSk2zDGv+Lami8Gg0LKV6G7FfDksGjp99GJf4hFGZVHIj+Fz2UhCsNusnZATyB68xylgUaV/R2Da+A'
                'lsxkMt+GjlMNQki8DtKVrp4Wqfgl0ODQedKScd6MZ67w8uJjKYVXEvd+3AmI+FciRNxQk3Gked9nzZVygHk+MW/ZoWZJXe4ty3xs'
                'fzW0uJLj5lLRSPNMHm4+eoKaV5/68zKLfKKHol3ZKvsOs7zoXqmS7zDzOJ5t5mMTHsd8afCRfIA5H+0DSzTlgf2vKN7NzCf6OzMh'
                'kPCJZp7UhWVFqtwJuv81/vjhRbpOEbQH27hL6iGL30RJZaZ8GGT1EB8C+TcVD3Hm6XF4hI1feQgstZdtvNGv4sN+Nc/3q/jLX8XL'
                '/mq++QZnEmoJBDydWyo+nen8mSBfPjJPCclfisxAXMyjgWdv+HOwDCtzm0XMMhfU40y2y3bKnq1EajJYcn3aBdDoxjJfiM7Ab1Zy'
                '3c93UnDV57y5NP2wI41HLICQt1jEp2wXCYzqsYhnrsCkiYPDyNVTF7kiuZ/IHeCVK7LRUeV/jSU8tfKXpvS4mbOJNFr7IvX7dQcK'
                'a/Ed5mgkkfwkaHkJmDrug20U8OShFKMdvT6GhaVCqip0ZsN37CYF8DNVWjjNp03yMmyAOH6YuSyV4X4mkxBJPccTMtjhV/wis51T'
                'mG5tHUsjTX3y7wym3JmbzeXH6G/2eGQyJyM/MskGdlDyS0cBob1bxC0QAXnZB6qRFwgsyWFAd4Kg/XQJdGpx/DdzhF6dbgoB/Q3M'
                'YkVrqCbYg8NMBYehRrgJQmOw2HRzsBk85zA5orS87P3M3/CUC/Hsvhf/jZQie6C2pUB1dp8uTUzm+o96G4ozPWwOIejDRZHhwgvo'
                '9RGXEQ7VXKSStCLCyEMeE5oZnZiCi6TPD0Q3lUqILmBRD8CKVDbJTIoBX6gwVknYQVKE3lGsBSvCh0kr7wMduddUJQSBULxyIrD+'
                'dSRa005eOV9TyNBMs2CXGqfpf5oX5NbQaFdL7rn1ok7VAhi5Kamtl3xaymvkyg1WCoLOmSX5MYYllVk6qHr3OPVMJ6jXXW5t3Wad'
                'vYLnESqor0bGkFQO7PPsZ1JfJ0lb1ahIUiaFXZI5IhApCxuaCVNSmMTlCWl1DnkLE2wX4XqYzxiwyMvqoOLUt/i2MKC+ScFarhe8'
                '0HdDqtonHB6ShB0MVkDvszSejOuhqcErQDTTUZfc6fDe3pLnoi989dRwOd6gIEbEFKEnuF4TeIbtDqNhMVJTUDE3wT4sB1qmmZff'
                'A1JPZIzVJiHx2pEdQzcqS+lQSdFcTTUgiaB7iJKUjoZFpYw3zqhpYwribWDNmmKj+zpvSZ/4TymJtBOrt9wIeJMtrOslp1kWA0mp'
                'PNVOQ4k2KXs6GNWAXz5ZVqVVMN+z6qhKV5hC7gfUB39gRzx5cpZ5Kno7MGI/qMGnFWClOR+pxhpB9qLcxuojvrbm9DQnwiiNbwVq'
                'vExlP+tDgMtBf9Ut+7Tdd6gy2FZ1UuWNGwGXM6+bXvs1SKH/Xl97vynpp5XE1ErKakeSlMxaSXOtJsBWUmMrSbPVdNpKom0lBbea'
                'nFtJ260k9FZTfStJwJX04GricCWluJJsXElDriYoV1KXK0nN1XTnSiJ0JUU6JE83dy2b87uXVNj+R11eb++Q4yEiZa3X0oLcB4L8'
                'asX21TqP/e93knq+ualGXyw+1X8oCVzSg7JHXzE24HYiP+XgbB8VqCZqDqWaDYnH5z4aXO/xeiHzuK2PVw33GP6SJsfoahODGdzz'
                'UpoLPyKsTETXf0Qe4VYmI+yQYKVDMUNTCE4yIZh7SgTLEvHf3QLNCsSC2nj8uzavfbU3Mac4N/mnzx73kXV77EjtbsWYckXD3PUp'
                'tnVAkzBPn+pPnRAr2kKRoyAi29xwRBwgaJM8k94PTd16LtM0wWC916Nntea2NLpbwj3a+FkSjaE2wHa736sXKIJw2gwxt0nh+t42'
                'b0mSZ3/2vz2Br+sT7ttwNntbm7Bc6zu4rwRVCW7jmrUxvILfBq8V2rbbZsfnZZ/84n7u/tUm2k4t/RcB7/rkWE7mofcrSaDrE9Yo'
                'MuQZeHC5ZObhoGKjjBXghtt9Il64wva3YuBuOiceZa4lDGR5NEDmeRnAfE85bfJX0VylIokzG6ORuV+QSAx6lV/aPpMrRpW3o52e'
                'NvVE625zhQ/IYfynTdsb8F5aYdNL+1yzrP2Je77pZyeuZP0yppKpDG03fufZnLyz++b2oFqNzpKdPwFTmU8Vw5q+l2OC0YbZ14bE'
                '+ATdOSEngWlHk9j6Fzmzgp5cG2TMFA9NHbJeV8J+Y5T+C8szLG/R6hHyEds2EqW9UdsV0GhkWoLpFmi2dpYGYG3WCQ0wHPdN3HX+'
                'Sv65n+b2LK+O75GaDuRPA737bbqYf3ZlNw8JrM81Wj9UF2AdU118di4DvayJPIZxIWZeHe/Ko90c/IXtTyk5dQ0rL6d/cUF8wrCH'
                'pd7jO6kO6yPvRccyVg4bhMS2XmIc2P+yo90zbd/O6rlAqScPwJwX411plGiRt13bjToi/x06N9fan/ui5Z5/fsulgvOrezqVb+TV'
                '9ZODyQWZp5b2Nz0WnzHT7GS8DiKR51c2jjmf2jjyQEBm7ugY34pPg8KoHfcxgqzBDQohKUMFJQaU/sId+rjNKt/WbrO5Hna7zPW3'
                '++WAJ+wcfEBNfd5LRYH2jTftKhPf4OYgtKZDmDOw2sOjD0K6ptn6ez6w9hJL7GT0OmMDGs6HpvyYmFuYcnLf6rE9Yjl/1m7ukUy3'
                'yLzuMtm8SFPJLe4DC9V7oCPJd7qUrShmGKq6ebzJrSOJi7zee/15/4B7w6v3xuSCc6uUOVSb+yDuNWdbzWTrvPTcZzODmd7wm/qu'
                'qhMEeBDU6Q5zqyI0LIpH4VGOOVumNOcM2aDEaNImxQVw2EBp+x5BvcDKtYGBwIEPe0hJqAcL+DCmY6quvN0AzeEXhlxPthMR+ry2'
                't9Qiz7121EvupTlmf3IvlL3V3zU5bq/nNjHqNdcmA4zrArdMNZgRrno/XvIgcTh5cztVcvlU6cq8EYeIfK7msd9lBX8qZ+hg6hAg'
                'Go6YZ2f/cCKtOPPstimPeJfKWf7pWL1Jv2blHJ1cycScY5ickfuQYGcXifYV1LHh6JbbYMVhHNt6l09FxrB0YNiPlARBNueB0abz'
                'IE9q/Q5gV5ySG8E4wI4YYvt1PPeUtg34W2FXO9lKH3/uSRtJ13Npf/z3z/0rXEK+iN1mhBDdeOdFHtzr1x7MdV2rCALhIy57sPz0'
                'yD0IUtVnH50aU2rX/dXQoD18AyoJDQB/kpOV5d/6g+n7aHn5Cb4QqX0wXH5uGbCG7QmR3+YDOortgXIdDoFPzgZfpWZwrPQxrOgW'
                'L8MGzW1uh6KsO1T0CFjV0mLVfgiBtehibbV3KoAC5XxVtc9qglXzVAW1JxtDYP3RcLV/W4G17kCI2utsz+cfAtQv9BxrZJm/BK24'
                '7lM93pb2y87lnfySBhr6PLM1Oe/0nMbCiWWfP1+GsHdOLcYGuAfz4oPfm0x9lVTJ6buevjRlSWEhCR71rqpEbMmLZ1bzu59vYjC1'
                'iv8j4Nw1lBUvNPfgAJUjKM++qCdlfHxEcqcAP/rlUJwh+aldlnwo1kPxYcnTab+U72ZDPWkENJGS2TX9Zxf/y9v8eRhYXHvOPnyp'
                'MPP06jeFL4Hj5UumOnwBRG65ViidmthQMsuK40JFoV9cGOuKfPkK17AdkFzeQNApqVdJ2UwV9GhDnhBOo6aL/upBiksSuHvsHyU9'
                'kjsrnrL95ROK9pQ9s7IsBXHHSlbPBbLzTD3u+fL1rd4RL4KidAnuo0V6DA8ZuT5rFCwJwhocA00K514sNorw7TX3SEpRVsJalkzl'
                'X731X0pv/Re0bHClq662EEpCSW0hKV2F2sJW8djPTul62EbpWsFO7dnxmpWuA+2Urs/Z/dJWkRtlq3Q9ZKd07WundPW6SUrXv5Za'
                'XgybiLd/Tkdf89sOlAFawG7vAjvyQrg9zCIMFqqTaBG/TRlQyVWrz1h2m1ZDYcBfVPnxUOX2rDqYD5Qytv/fbun+JIsPpxXknju4'
                '/qM+Dcii3isdqeF0nZEeYHdSR2BTsjV3BXuFN3v9B4IAC8hjnKNndGWiZjvZk4pOSPfmcX3b3MKg18ynXlrSlSieHO/LoXvH6A4Q'
                '1UftKZSCzpirX612fWdlWPa+vYMFIazvwN2fqrD9inPQ+cldagZ7hrbdw9hybecwnFNcQ2YaKpI3iiS0afval7BL7JFv+kfKMUhx'
                'WkzSH7wfr1bijeu9v9H1+QP307RQi/FaNDck3z4e66VmLqbrEQV+0e5jL6r3RvjwHamFcB/HA4ikmsRJ2lwVm2eDzbXBPrfBPrXB'
                'ZtpgM64RYx4MEMQR11WuH8R3xHWUwlnKAdWKg90M0/3Nje5RHNNp76zlHcOjLuIMS+QUxkbYYAGmc8bP3/AvWZfbzZaGmF83cNje'
                'jPzTX7YV7eigeu2AY8abzkQlnoZ+zOIKTK3eRd6efiWP92F7wr0vArapG0ZBiBlIdMlL7Nje2wxdoTy8X5bYMHGqtOcgNemVYJbc'
                '85JQe/Gx9hq4t5n7/Bxh7BtNeZMToOQjiCmTpUQBQTzT6C7alpU0JuEUXa5/033QSzR/dqdIAyFvrs7dSvnuioaSah6hh5Qlj+U9'
                'SVKdW58CdIyyaSfYEc7xzuVw+edNc34VKVtEMrShtul+2JPvhsBjOHBuv0QBgfGUho88x1P9zBcQ7N9IY1vm802An+bLA9uykAYf'
                'nuGrZGUeJUVEj/V0T19Wv4kiMmorbAfbGa8q+S5WvwdEuEieiwbaRJBv0gyg4kBTJrqbZJE4RunQUBqDxEYHMFlD7qdbgJB9F9dG'
                'yqGRNAh79XvUZOPEYyLrcUlghrGXsQtiB4l7EJWq8n2U+AHYiUu4sPPN8cpyZyMSj3cPkvbuoMfPUgSMi3vGi6Q1E+QEbyxCPttL'
                '23wgzSHtWG5uuB5QJFnT2slezZ67hXnJ4MmFVzuMqplmwEQLWuukMFPWxG8NoNO15F4pNGMkD+IZy2JJqLdHUUOo2l5e1dsoRT9M'
                'Te3Z0Ta7pKMe5jh3rOfgfHn4RzG2P17ZbcdYjGRqbcibx+K6ymxKZcEQJZtbGjqlHENrHOo2ttNXi+xR5LiHMjAn/SJTzO0qjRBK'
                'Yt3/4Xq13/zMSfi+uWnMLDGBDlIrXMApFisVQ0XXAuaB15Qy9emVe6oRl2Aj7Oa6JMilwSdVug/78p1kNgk7y1cslobDeBHgR8Oe'
                '3MCmnRZbcbYwB+VtEvdL6ftpB9+UuyBUcshvw/aRYqKU4ZfOBnkjhT+kVc8vC6EYZ7m/UXQJvOS4mviA9vdBugFqiRmlC84aq2Vx'
                'iowS06/oCekjvyJ8QuSgz+Ac28SlM5DdLhtMWXrIsHODfElDe0sdowWfLlAjSyuPtmyELLYw3WBXq5xaNmhWW0sLcg9PqCi3VecD'
                'av8xRDywAeiYz4uUqywHzmURTxEFozlH5FAPAem1UEy/MjDNSgRH78kSaoi0NTzTuxmOMlkP/GApkBZ4aKEh64TbcDsQin/00zbX'
                'ltv1xxBOLh5bfDKrRDCrZXeqzOtylZmN0ZhdcF8990i4p7x1cjdti+3q2jcvq90Hl3oPWf0CNRc+wUXUpL2TyFoS2TVeis/cIqwS'
                'deT7wvlsIzJefryzeo9K2CaHnlFxp5WFDxtH6PuydZdCc2LCJw+65vZNN4OOpeXxYW3yH7sv1ENOjiJ9nw3afcR+9d7w6r70NKHI'
                'OYTZK/e3+EO+RO65Nf15/A//MqfraV/qlLd6j7oz8T24+Q9aMHwtpFHbDNg1WBynNfXDyd+5P66lUKAqq1yTv12uhk2yoPiMAVXY'
                'Yhd4QvtyoRPTlPsmO5Ty6tnq7yEfUdaL1bzlTolTg/Sl+pzU6qu3J167v6T2T0Vpo3fDEXDnBomdMfu/t3qf6KvcJzY2q5p/4ftX'
                'go2rHNiY6/HQvPjcjF8+eYQTP++Bx432x0Q/LH4K++3Gvn4Gne+Crnk73V8xurF7Je/w1u8eEXLNjLLPJrYXYTyvbzxXkLrrHTwr'
                'G4WVUruYuYkFZ6ZXoZwZ8LjZ2M8+lidKyokmXNzmxn5NtpJg/Ux0njTBPxFd8Oby0nLkxpnfzxLS4XsOZw/A3P/3DXwbbiAifmOu'
                'Q8rFC2Z3uMl5kPzXrV8lFZ6dWY1LX4Ou4fR/eydE8Q=='
            ),
        },
        48: {
            "ascent": 45,
            "descent": 12,
            "glifos": {
                32: (16.719, 0, 0, 0, 0, 0),
                33: (21.891, 6, -35, 10, 35, 0),
                34: (25.016, 4, -35, 17, 13, 350),
                35: (40.219, 3, -34, 34, 34, 571),
                36: (33.406, 3, -36, 28, 43, 1727),
                37: (48.094, 1, -36, 46, 37, 2931),
                38: (41.859, 2, -36, 38, 37, 4633),
                39: (14.703, 4, -35, 7, 13, 6039),
                40: (21.938, 4, -36, 15, 43, 6130),
                41: (21.938, 3, -36, 15, 43, 6775),
                42: (25.109, 1, -36, 24, 22, 7420),
                43: (40.219, 5, -30, 31, 30, 7948),
                44: (18.234, 2, -9, 12, 16, 8878),
                45: (19.922, 2, -17, 16, 7, 9070),
                46: (18.234, 4, -9, 10, 9, 9182),
                47: (17.531, 0, -35, 18, 39, 9272),
                48: (33.406, 2, -36, 30, 37, 9974),
                49: (33.406, 5, -35, 26, 35, 11084),
                50: (33.406, 3, -36, 27, 36, 11994),
                51: (33.406, 3, -36, 27, 37, 12966),
                52: (33.406, 2, -35, 30, 35, 13965),
                53: (33.406, 3, -35, 28, 36, 15015),
                54: (33.406, 2, -36, 29, 37, 16023),
                55: (33.406, 3, -35, 27, 35, 17096),
                56: (33.406, 2, -36, 29, 37, 18041),
                57: (33.406, 2, -36, 29, 37, 19114),
                58: (19.203, 5, -26, 9, 26, 20187),
                59: (19.203, 3, -26, 11, 33, 20421),
                60: (40.219, 5, -29, 31, 27, 20784),
                61: (40.219, 5, -23, 31, 17, 21621),
                62: (40.219, 5, -29, 31, 27, 22148),
                63: (27.844, 3, -35, 22, 35, 22985),
                64: (48.0, 3, -34, 42, 42, 23755),
                65: (37.156, 0, -35, 37, 35, 25519),
                66: (36.594, 4, -35, 30, 35, 26814),
                67: (35.234, 2, -36, 31, 37, 27864),
                68: (39.844, 4, -35, 34, 35, 29011),
                69: (32.797, 4, -35, 26, 35, 30201),
                70: (32.797, 4, -35, 25, 35, 31111),
                71: (39.406, 2, -36, 34, 37, 31986),
                72: (40.172, 4, -35, 32, 35, 33244),
                73: (17.859, 4, -35, 10, 35, 34364),
                74: (17.859, -3, -35, 17, 45, 34714),
                75: (37.203, 4, -35, 35, 35, 35479),
                76: (30.594, 4, -35, 26, 35, 36704),
                77: (47.766, 4, -35, 40, 35, 37614),
                78: (40.172, 4, -35, 32, 35, 39014),
                79: (40.812, 2, -36, 37, 37, 40134),
                80: (35.188, 4, -35, 30, 35, 41503),
                81: (40.812, 2, -36, 37, 43, 42553),
                82: (36.969, 4, -35, 32, 35, 44144),
                83: (34.578, 3, -36, 29, 37, 45264),
                84: (32.75, 0, -35, 33, 35, 46337),
                85: (38.984, 4, -35, 31, 36, 47492),
                86: (37.156, 0, -35, 37, 35, 48608),
                87: (52.953, 1, -35, 51, 35, 49903),
                88: (37.016, 0, -35, 36, 35, 51688),
                89: (34.766, -1, -35, 37, 35, 52948),
                90: (34.812, 2, -35, 31, 35, 54243),
                91: (21.938, 4, -36, 15, 43, 55328),
                92: (17.531, 0, -35, 18, 39, 55973),
                93: (21.938, 3, -36, 15, 43, 56675),
                94: (40.219, 4, -35, 32, 13, 57320),
                95: (24.0, 0, 7, 24, 4, 57736),
                96: (24.0, 2, -38, 14, 9, 57832),
                97: (32.391, 2, -27, 27, 28, 57958),
                98: (34.359, 4, -36, 29, 37, 58714),
                99: (28.453, 2, -27, 24, 28, 59787),
                100: (34.359, 2, -36, 29, 37, 60459),
                101: (32.562, 2, -27, 29, 28, 61532),
                102: (20.891, 0, -36, 22, 36, 62344),
                103: (34.359, 2, -27, 29, 37, 63136),
                104: (34.172, 4, -36, 27, 36, 64209),
                105: (16.453, 4, -36, 9, 36, 65181),
                106: (16.453, -2, -36, 15, 46, 65505),
                107: (31.922, 4, -36, 29, 36, 66195),
                108: (16.453, 4, -36, 9, 36, 67239),
                109: (50.016, 3, -27, 44, 27, 67563),
                110: (34.172, 4, -27, 27, 27, 68751),
                111: (32.984, 2, -27, 29, 28, 69480),
                112: (34.359, 4, -27, 29, 37, 70292),
                113: (34.359, 2, -27, 29, 37, 71365),
                114: (23.672, 4, -27, 20, 27, 72438),
                115: (28.578, 2, -27, 25, 28, 72978),
                116: (22.953, 0, -34, 22, 34, 73678),
                117: (34.172, 3, -26, 28, 27, 74426),
                118: (31.297, 0, -26, 31, 26, 75182),
                119: (44.344, 1, -26, 42, 26, 75988),
                120: (30.969, 0, -26, 31, 26, 77080),
                121: (31.297, 0, -26, 31, 36, 77886),
                122: (27.938, 2, -26, 24, 26, 79002),
                123: (34.172, 6, -36, 23, 44, 79626),
                124: (17.531, 6, -37, 6, 48, 80638),
                125: (34.172, 6, -36, 23, 44, 80926),
                126: (40.219, 5, -20, 31, 11, 81938),
                176: (24.0, 4, -36, 16, 16, 82279),
                183: (18.234, 4, -21, 10, 9, 82535),
            },
            "dados": (
                'eNrtXQd4FNXant30XoGEmtBL6L13UJqIoUoRkCoICIKIolJUQEARkQ5yAZEmvUjvRWroPfQASUjPJpvs/NNOP2fC78UrauZ5xNnz'
                'ftmdOfXrXzPZuCKa/UV3TcFduSrgLiTYuLFZpFT97oYkXdXv9kjSb/rdEklaqN99Lknj9bs+kvSOftdUkprodyUkqZh243CXzK+X'
                '/W5DtP+FKd9cULsb/k9qwDvO3aY21dXuvzPGhrwaq62pLtr9efW+J03xhdq6S7sNcqj3hWiKA2rrOO22g3p7kybAH2OWervA7DEu'
                'qPfdTB4jWHuM/CaPEaneXqUJ3LDHmK3ezgWIt2x62V4dCuP6Rv24VrvV11Ao/bJRamt/7XawenuBJgiBE0eSNqi3M2iKnmrrde3W'
                'OVG9f42mWK62ztZu66m3GZ4UgSVGbW6HRnAvhHabv2uzV4dCvzqqnx7r94+NnYy8flBbf9Zuy2i94UFTXFKbB2i3g9TbQzRBHm1q'
                'l9Luf1FvJ9IUr8hjROb4GMalPsJyAVbOBIswwSqYYBX5mOtrE7eefaoeNvE3jm1Z+HHnaoEG4vvVU3bU9ROp8X3ejNCwpumyCPN/'
                'KguxL4373yNbKP+uCC7bZszPjw3shnGQOkul0TuU/STKDaxVWW4j4Zh+VTawFhystoEt5GAlwXP9GMZgrinwqeOV/3bkxcGN1Hvd'
                'Wz88nP5B/DrV1UkHp/J65UxJfaOYkMUBE8rqf1ltg4MFrzsbP1rkg/1pNNgHPa9z5bEkth1/G/Xdt705O8nAkmlM6Zeizw3Ql8Wk'
                'zw2sMAeLNDC/ymuq0lgvHUqVqimbYh9/HLPu1bGtKqas310TWhfzUrEV/k23G1/ZU8f0i5yLZ604RlyPFZ5LgJ1Qx8FSY+IpZhxO'
                'v+sEHt6r0Yg5uy7HZCitmbcOLOlf5v+3bsv9QazsH8TM9p7SXCzs030P0lOiNw8LoFmYO2pXtCaafsgEXZQ4kqT+TG3cgrf4ncS7'
                'dLkFg4qok9dWHD81N5Mj8DmGrVMbJuNf/Za+Trt55/k4W72zF4VQc/XzfS+c+rgMX+Qr7fZ7gLhcVj92wol1hi9Kuw+wq/e3ADRS'
                '/bSPeOtW2vd9q3/Q39fYOEJU9sEeQVD31giGSeiQkQ2CZdjXgGuYjPgZaYmMGLk66iM+8ZM43z2c+W7rafW2NzW2r2sE3+HPnUe9'
                'HaDeHbdQ1IFYn/hnQn43MFa5y67GzKijqL8narez1Ns5XC5Ykt4EYxk8RluHdnVnraTexgez1PQ8+UxtPKTeDeFNec4c7K7enXfi'
                'rhD3OXY4v0dpXPIj9b6BSEoLH7//oS317hZj7Wi7/Qp92xiw9lZixqMjkyNEf1tK7chkjaXv9wz8quNnfz71DhUdDXkdeCAU5hG3'
                'V6FrrsrdB9S5xBE73W+rSEvlLlTfVKfk93xD42/kD1hqTbjdgJbSXHQEPrLSxNoyTw+HvLkcjqQWuTJNrS3zL7Re1+bbHb1ZP20G'
                '8eTjaI3NC5exdfkOs3uox6G2zDtAZkk5/nSgs8yRAkYisUsKw7+7N5pxSKRQl3lmaf2Dp7YZRePPPYCg/klt+gZ8Oov1yX7tvjzB'
                'yai98NgHfJyI+ruG1j938WVqPaU29YCf8+rswVehHm0eyszy0Jb5Eezvh5Lz5JgrRhygLXNiuL7Dia/kZ1jxOWSP9oXsYfZyYtuq'
                'qC7zuEBqbL36r72dlPH4yKSy9BTx6rngzON029Mbp3fNeb9FYQtv8ntOSRKIM/gxeVso9GDs4hM5ZyrLYfkFqF6XX4RqEYB2NM7j'
                'kqdK3yXPeFTHDaLjgBm0ttjQiKG6ZVBNMFUznTOo/mNKtQwI42FmVG+Ap9/vbEJlOQ+ZcLMvqwW7aYyYqOhxSOXoJtSkJWB9ntEE'
                'yntGi77kuthJJrw8Jlqp364J+a3s1Ag+KKhTtdU/PlTvC8cbYEocILugz/lJRu+o978aUGz1OpCT3astun36h+nqIQjeTdmc38wG'
                'ZCuVWV/I+NQE6EWUa7X610Pgs00FO4ac5AL3GqDPQGLJkMKG3LNGaXYC3J2uWrGshMs2CvvzQNBqbBKu+6huuaCuS6A4hbozvwsk'
                'VVvtJ0CX9gLjUvABTrRRb7yL+HzjKp+Isfgh1PL5Ag5+E8ivyg2NptawZZLxbdYPMmDbaoMxsJ6FTRf7hbv5Vhh+DX+uxcbWU99c'
                'kzLL+M0PzMm+NMg+4Yh88jl495FB9tojRi58TZoGP7wH9u1PCLr9b6vj9T1cMLDHXZpP2H091p4U/fv83kWZ5WMoW/+M/xlSkD4F'
                'LhqDsUt/vI4YJ2PMKGV+XgGSoHYZ8uQjfR46GTvepzrYyZi5xhI9ZmyshnBtdEJ3CWlGlWNc571cYvWPBgvQ0qAdpX/81vhosL2G'
                'KSBZnzZgaRwl/3Se/nG08dFg0ucaHyP1j0DMra1//N34aMibl42PYeTunp+LniL/dif5zfNloouBpmAELtHAZ85rfDxCHitJTthp'
                'r1xV9I9tyO9ye070ujTP2IR9Sc1JV4l45a3Gx276xyzjHZ2NI3scIfDID3UNuuR0jRhSXS2vMPoWUvfaUaJmnau+t9iAPqe/Trce'
                'LI470IaDCWXyKaBFNw6XN43P0/WPURYkqeNa5BNkfxi7taOksfWBfYnsj2jjyyYbcA1M0EX8qJehxDhm/LGxVDLd9I+rDerqmGlB'
                'ufoRLw02IjAHdFFGqmN83Elq3w6T73ha/1iFnDB1jY+/kZvvzxgfqlxf6x8nGB8NpnmN8bEmsdQydRnG23jfE+RSM7b+L8k/NRaE'
                'wTEXMsDJJO9bCpeGwcuWI0dwBjG+Psbotyfmxmly5jTjzSt61uG77bccJua/bZ+8sDDVnme6IouH2+SM70Owdv+JybKjht7zadOC'
                'jXavsfH6kPbX3ylpwjiVfxuu88dPRztLLn1vUkfSk1G6YcSp51WsNWYkMpdYu14CB/gIXF/v3MtQC8vPxiA9jnNv/BcA4vKuvitk'
                'G/+pT6Mg/aN1pcJYdcud3f8BeE7tvVIm+xnv5T4yVt+tlX6wfZsX6wefz5PUfpAmLSxE9Vvw9AX/g/HCrrVavwl54Fz4JcExpixa'
                '8VcYzh3QvwIGBiq5y8u7Lw/EVEWhNMK4/0T5ra2G+KMI1i7J2q29EpI+JqCz84IrVMBmaUe9rx2dr+00FwH9+HyXnEORf/Zn9JYv'
                '+46x8uLuHCW0vsIVTBoTvhv/o2O40KReoaoY5iiItQzCOA39+g0XyJBevDTWoimaL0tmhgyPFEyUQEqU+/gfLcUFSe1E1Q6txrQr'
                'SSyudZnFeL7cQ14JmAyUgh+8k5GHhYTJFW/jSmtMTtKvjzBmCWNyB2INBbT+xN013sOEJIw9/xDXOtrpva0H49OxnlZweaTSmuX2'
                'mEYW08HOxPmNOFrHrzmCPcVNBLMNkzJSY92njWM1NM7IDWvRNOS/4L99lZmxaKaO2ng1MSvt4aGZrzG2iVq4w8ajYa6EbnsGpTQ4'
                'h81B9+3MaRFfC77CWs5hEmdwwdL73LPmrP7b+VOBFmFOBc/879wldXU/go+60r7APePjc1XuCwB/CtxiOgHq9zGBAAjFkhNQHZ/B'
                'RGQ7ZCKXyNAW7ZQM9DXw9eE79NT8J2RyPBqDpjlSF3A7g5zpuvJ/HKuKDICeAPpSw2Qp9QJDkiGtkGkFlyTZQJv3OpkSgZULaq+D'
                'N9KdoVxQqRgKlXOY+RJY7WUfoFzAVy/o+WzLFPaZLeCZE6BGQLc36bsbaIo27HW4HQP5VeyQisi4OpJ0ZVSkS6AcPU/pl3TJfAsY'
                'Xy9a8+xQ2PCugLI9mBtAP6+qVD2AmvcAvl1A2+dsqPDULVOPwXLQ7CtB0AD3Y3mP/H2gCrI/oWqgrqOWF1lHkvsOdg3WRoPiMpNa'
                'v+dLk2t/D772R7gy+8aHm64nZaU/PvxtK1Lt7t5w/B7oIwIV955NJxyw4T8XRmxx/yPEdnBi85EMMmXP+IYqdzKQQcCVi+QifOQd'
                'kXQU8tcj2jFdqd/MjVGPErNSHl5cPaYO8gEatYdyq7s20pXQBhLXpVpCSE5rJoTktAghJB8E0JPZ7Qq7elf4CBM3G2nQ1XfA1hJ8'
                'CELfKdDTXpjN3x+aG85IBRaTRt0Poa2GYXyAOlHOZKD8cMMU/9VJBhrAHlDgOgOgysI/2sL8EuArkmhlXSnAmzg60gwbNHh/SCEd'
                '0lgjlX6NyOb5Pql6MmSzGUqZuiGHkNGVRPL9DruuIWX5vgOQW6VIpCE4nOXjeUjkbWgfW0c51o6Dh9cM0vvDeSEAsgZTL1pNqMmo'
                '9+pDkqVgo3e/Xnck6vazdHvCgwvrvnwDMqOvsctudYQIUtiw75xEkDINnYSQPFYM2fw0KHnTqNfC/Z19yg86jzCFA222qS1iIKxf'
                'Q2ges1KgTXcTA/UF0B4GasVyf+DqB6CPGWgvgGh/D+skgBBSqUtg9RHAIC3fyEv7RUCDZ36JC2UfiLRIfCh6fCFJAClrbKa7CFIE'
                'oyAhJJ/AGTP3PDXf24uw0XRnNIK77yMXGqsKHRDqMp24SSati7RrpuYNxECfAmgaAwEXBfmDJZ1IR5uK0Kje8bh8fiCmDaj1EG7m'
                'gWo/pG8a0yDM29mvYu8tiMvdwukio4fLC6HRkgByjJIE0MWWmjJnyH7KbcO+uyeUsD0bf/zTkXvPMzPj755fN7FTIFc0r4ycCFhn'
                'RzfMrYFFp8kmaP1sE9T7lmyCzpdNUMrZiEQD9VP6Lh9dpS+D3lxUl5IdTSJ5aGic4fHARbfpa9WTi+pnb3YdiYcWTQbuLBzUelDn'
                'ity4qM502KtJPDTChp3CNOqiMwpnXbjoJDBZeWjNLLhHc1DdDeG4Ex/V1EPppSQTVHRVezVRiRNCw18pfx+Ub42Z9HfEXuO98F+E'
                'LVtzNdb+/PaJOT1CTYxymT9XNTHYZU92MRmjPW4m/fKLxcQI+LaB3fyxT/UQN49C7VeiI+GOylEd/AzTVFdGzqXtWJfxRKR2ZC6o'
                'abwgcaM3dNs3i7mA0zXb6f+Fwe98wn7nJ0iaa7GktOAdvlFcfhyb3nLjvXt93R0oYfXw2oU83Ik+O2mBrkLMeV5TEmIfSkJsnCTC'
                '7ugOGE4Np1+jGYRhWJhInrZfLD98JzY963n0mZ+GVOFN1Lx9lhyPSctKuLvvh54hlMC3iYghOjkAxU0FLmMe6Wso/d+WhWBErCwE'
                '8z6QxeBO9BjDKgY7B5TuPPMGALsBKBHTKVf4QTutnAHHkVSefffOHE21RAQnIM8X4vK1y4TTHnG1A4OehwMC5v+K4ik29cgjW/Kd'
                'Q5MbWaiIvM11fkcdEGW8FBB6YrKJ/vlJE14FoYryYXUSZ4hOMsUVyiI+55QgRWz8L0bmcS0yFA6f4oIWj+QEb10KB0oFuZIUDUFg'
                '0/sceXxC+e2pBYvw0q5VKCwR2jOt6dC68jkriz2GK7otaw55DKW6EIfwa38GkQq8B/ocumRyXkVZ1l4Jgk7QIkfeg933VrBLYdR9'
                'mvrAepTb71f17b5UvJkGvu5zBnuO5KeyUbS0hmsbXT94jGvfelMimXOr747E2DKfXtk+trZFKP+Ba/arAfUVQjFu9BqMcAildrCt'
                'pdBxg1LBTKgipK8ZQCnEqHT9k0jXQOz6GDxfVUb4ekwZE9EFXBrl12nEek14yHbgWOskwoEY+puiq4FQlocGrSQ/GinrECoplwJW'
                'h8k6USBTGK4BogDkijTil0i6b9K2e24oiivQ5Z5l/uhdjmXRMIRdAUZRZ25EGuYZjF1HgN3Rh0bqMuclo+3IYFJilAYdu1gShdc4'
                'yvFOd2u98avOPUjISntyY8eMbsSA+U4k+cKMX9EJ2fIZy4UCXWhHO2+VrdN2ikKJ/DX4PiveoytR0UC5QBPww36FXfyabINoB8xq'
                'HVNAfwRof1bcThrRKrjCoGGJ4fOgXs3Bm4GDchm2xbcA4DM0NJZY6muL4CEeYGLGhJIPpK2jQDDN7vct6OzbeCtp8K4UK9J+arsM'
                '69twry0aszr/IeyqZ/tgltPQGSQTkLkZKcnfT2N/8tdA0mOfvG6EECEe1/soo9IQWudPKlx3CLC8H/EhPIU1DwnA82eF0/pQxXcI'
                'BJftkogMJepVREpGoT5kuJIsv+EmY+5jEhbLqFx9XMHdFCK/hGEtT2D2C2hKby0Bl117YSapSSUUXLLfE/Pz0ZyTrFIL2GFXehV0'
                '8a2/HH5WJphFdCbZVZ1wzUw+qHtrRHJXGQjkaXGHgTK/gnu45zjSbzl1ORmvW2vU8rP3lD0h5tqOrzt6UztGsf4rzt1Py4g9vbQX'
                'vb/X24zNvvQ5uLTgNof2BkCseMBpVh4CQbiu+3mvaRxUM7n9k6wNUjhgah1zq3r61AGRAPJmYqcZRoa3qCvdAk7XcwZv4x6DWMpK'
                '9HqEbj8ZQcifphVjX+uHvHJqSEQ4v6yGh49nQKh/OS0NZ850+LUZrt2YB0IdXSRCps4zN8TXVZCAg5I8lDpMVYPPl3Ak5lT28Kq1'
                'Cuvf1lLAcyGb9YbhAci9WmIxGMyleYcMILw0kL62iL5cf0Xz68G7fcDEBvO61AdbrsfbYy8seMsZPn8U79A7jLKlMFdQFs/FUsLi'
                'wNW57cdiBeLJ+BH88jqCtgv1Pba1QbxCqTNItJH0+Me4ZX2r5nHxDu+yEspX8aEA5CgPDIc8LghCyDmgDfJ7LHgecZ2WlusIATGq'
                'F8noeLWdtu1mnGJMuLj+wwocju7iy7qRXtL1JzzY/+D2z7pe6kNuhWyo4bEtPw6A4aJvwNW/AnLATxQLoo8dsj/tkOyueRg+ywsd'
                'crvk9CJBg44UE2HunTZmUjEDiAVuuljnSnlwxWlQ6cTAhT+6KAsCEiT/fvsJTsyGpaxw67CO2Obs29FJamkwn9hcs3b3C0JuM1/d'
                'Jdb9wffyIa+RUeeIBXx8RAHMlWE3oRM6MyZMGARy8dMSAlW14qQzoZxYkx0viEWHf33+4+JmsHKdGs0IyN33ZJNvVZDedj88T/TJ'
                'oSEhtDT/NdFr2XsHUBlWLA0XEH1u39mHku7d3lpPjFjm1p6+lCDf/4BwvI3ZMlY8W4xd+JuHZrAyU5stSTSBVX/QzpsyTWB1lQw+'
                'WuyfEfTzil1/3049ML5YDi927L1g8/e2b+niYd4tST81t5r32qPprP3hOvGklz+m9geX1ssSydU/gF657VelEEqMDZGUus+z0zrC'
                'FzFhYWPqQX26byYYoPtTKtBqvN47CXEsajTdG8ED9mabT+SQoYcd5vO86kUxHNRvd5bor/3f2W4X/bZP900kczcGPblX5/VEz9yf'
                'itRs7h1+SSV6bVET2Gtu7VYkE32+sSP0IXJ5fWkCMWKHBwaKx3tcmHi2zKgqnEzJy1o4CWfq1q7imXp8iHieE8ZO/ubb9PO1F57a'
                'Mp5e3zzJMNkE9d1BdO+996wgCyupfs/Da1VzqHBaFQ0zrzUrr9r6ZEGnEt4B1RbA2dBng3yyG1ADQUvFnBld6DApVUlHvM8hMh2J'
                'cVg+5BlyW9NpOLR5Fw2fDJtwUOexEnPPOQFVJki1mRf6GGUiTW3QJfi6ndEiPwan2lvoS6FeJhVT9JYAq9DWmOcr1k9i3HcUKZTY'
                'D87ynPOgm8rSl3yq8L/31W3F7KtDl5+ISc1KuH9syYjy4hcsOJHURT2YHManW8yqw7KXFmJ5pNEp3FMufQSVNyvUcPbM3j+pTck8'
                'Ll4FGg/bZmx3OwjxvrQ+jZ98jP9Y4Ch9szmbD/OM1tTDGV/70k5tU7RJdxG2h2gM6Z2qnNdspH3HTpCPR1OKngni9kjpB5irteb1'
                'FRUg6OSK6n6cpqW5KaDexhcVjkc3mK9hHiF11Zx1MT7txsrm+jaaBew8WYpmJsSG2aICoA74F29IWcZQu47BvDjzYXz7fyCl5oJ7'
                'TTdmnyDc3cCYQ0rNtzY0PzQfSIam7EZ7P5/XDftmFrLVduyKQidctK67pW323mcxSos6eT74GgU+twWWbu0Axig1A/aX65CWWlOf'
                'PQCT7BRGqSp45qib6U+YphuaoGdilOqO9/UZFPkaRdiBhmKU6guMOoOsjXeIJH19EaWfettd/fVF6DeQCvx9RKk5UIatR2lL9hF2'
                '9O8Q5X9kNRfmNC0QEL3DQwu+Q2qUJe2a/60WJFIQM4m1wYJHNUpXVRuQGCQVVxve1TW/j7ExOgcofbeAEOTbaNLpKYZuvunn3dKY'
                'VFlFh2tDvMYCIlL1Lcj5GHFiottdGlNQyoGSleS/jNAFkPHIGm/FHIVbGswdjIVb6WVQ2pbAPS9C7YRHgLGoM/tSQtrNlS3UdZQd'
                'd35uDzzlspZI5zDDn+TxY3L+eWhTY6fXCxwhJTXT2alwjjw5lrLD1tT4toSBNKdeep/soCIqaum2sIu98KetrSlob1NPVcJYjEmr'
                'BtUJcXfyLRs5E+Q6GU/raWZm8XX6o13YBMTbWLq0xQW4fRAxh7R9XRoeIOwv53pj15x7lp6deu/wggEmPJ8HJnoUM91OZX7sC7x2'
                '4o5bFj5NAUIP0pBPNIZ4ycV8oksEUZInj6Y61a/deUR0tONvHBqQVkwGdpzsgpIgGa5ylYilkr5h1waYZWwecpGipaxMaNJozJhU'
                '6PjorBDJCpjZH2ii05gJEliH4lzZTNYwB3lNzB6NXyDpYIYWMHCbx1JLTsAgvAFF0KuiCuEfBmNfOpOmy2E40c/APcWTHOszuGtE'
                'GmWogOEQ5TmBK23wnBKU6wawo8TDxQlysD2G8lcxE83D60TND8G1Cgget02I0o1wjIammg4jsHmxKZGewsszSc5ZE9Vd5nr5wUCq'
                'CTBnBp2PA5O51ERncHHvpqbh9ygkEfmtvEcRNcEcGsCh5aD3QWfgQJHsVQNKncwC+glAPX6QhUsRurXsJl0DMuLvX/h1ajf4nlzH'
                'gay9zczcCpTQK28zVD7pYYZqwT5iNDMQQ7WQIWvI20j+6EGj6pbyAAsXY1C0427goc2xaFMWhb4B23joaMzez6CB9zAnJuqN8nWF'
                'WpQzFpPeSKlg0lf3apmMwjpf0xE828x0BB2fmY6Rao6m3terzBDoz5BWhNNX3lCpMJ2DorDZuzwUaZWCeSg8LiN4KGQrKnJQdIqG'
                'sKgPdOFNc6JQzzJDkXvsr2Z9Jb9lhu4y6+drBU3QXXmEY5R9oDVv9LOTY65vn9GL59IcEDl1++W49KyEe6eWjalPGo+d3tpFOrIk'
                'rnkdcZ/teHE2tw2fKr+V/GfXvfYLX5RN4Px3ZBPYHTOlxS1sV9LXLX/57rOvABh5WGTPxtjIWgsyVLg61OJmUVxT+MqSeBWivpyu'
                'Ki8LI7IlPLDOweVLr5txYjCpKc/Pk4ifK8WDoVNTIpdBhf4iV7g8JzzHjnPh+TLj8cX962Nc+Cvz34a5VhK4Tw6jd+WSPDifLJu4'
                '8sNiPjxHU8KpxlFMVMQI80uShEHC3Nki1URzjfJLDV9eEqWeVWfq99hMrT5Pm6mSBxbFGTe/bXEft5ByXWZehKuk4F2zVaL41l0x'
                'hSX/1aaw4nl83WR9q0xLp92kPJi0rhUpmwZ2+mbn1ee2rMQHp1eMa+xCbkwOe2rc3fN7l0/qEUEMPXdji13QIAcKdQI2yYlClud7'
                '5UQhnw7NicLwryQOBr/wBuP24mZ8d4nHOFTEjAOzuRRK2gXYrWolEx4FcjtTUxNzKVCwtKOEgKI8FqrEp0Ab4kERBWR805wFFPXg'
                'zxQVUKA0IA0FFJ6Qoq2AAkW7dBRQeOX4Heg5GggoGqDkQQIKGC+XKuqPAzJMC8WnqII5FvMptmJHDZdiDH5U8ShGQ41FdlUeReUt'
                'JvPUN6zBuH3CuZ7zemGvUzmsOcc8T/N1e6iB6dqPmVuHt39k25Lj7pzZvfSzbuSRLfqVw68SwmRV+Jsj5HX1lUL+aX39oqOgxEe/'
                'usjhVwMY/qKd/IoD9Ox/NYB/Su/+PQD8cm368eqTj5KzbLF3z679uk9pxhr+czI1bE/XdsEMFvX4AbLJwOnd43uHYG3NNqQ7k1hS'
                '3fR2RTancD2B6UB+G1WjsIdH/rLtJ2xJgRRYlMpW3BHCo/1/bBpFZWTaGc+In5M+l1CoORbmITBFyHsE9iOU9qqcYDCuyQIlNF08'
                'ii2syOYCKy2geM9cGMel+auiWcNRJpC5y25y9AkUBUelQFFwtAoUBVQsPBdRtGKd7iiKfLIgsBQIcTeRhmGLiAIqGbLDBBRIz7BW'
                'QIGpGnoJKJC2wd6DT4EpHBzzQrgUuM4hZWXPcnmcA4q/9s0TjMJE7QBrzoddyYlCqHxQZQVT/YOi/J4QLlZByI7z05tRBnKghUh6'
                'eO3gwg/b5jHbAhvlcLzn4q8c/v/k2145PHd8/+F47t3LvxPxsbkNuQ1YwzwihQXmggPtRUepsHBfGFRRhdKkJupeM43S8UKgfnVm'
                'I8/n9tIW0htCIhuSq5ANmS0koiGqMp6gRT4zSHdp2iJnxt4+uXBwBVPprTRMde0YzCcpC03pjv78bymPiiL35f8Qyn+R3Yv/LFXj'
                'aKsXTVIDxvPZu/DfqDZ03rNH8l+6HvQAynyTL9U2hJ7mGW35gm8TGCNja8WXjVvAxBvpLfni8+s2ItU5h2Q7DDFJaZST4iW5fk66'
                'maS6OSnuEmpJOZF0kHIkuV0kRxL5TljOSsTo8Jy1TfeKSjl1nXy/mEB/0RqFfj4oIVBxtEI0D0sKtCAtUTDVo1ICRUkLRPO4jECX'
                '0gzlaokpK1iwaOLJT8oJ1nQjFCjxtLxg2TdANM8qCHaG+khHE1tJsHnURe50cZUF+wtaknJ8VcEWVBMFjz2vJhCwqqNg3oQa/0L1'
                'ei6Si7z6ZpYsKkC+C0bXZS4vbSjFTdF0cR7CcgsEnRFeYlz/EdPhqWNCMsR0Mnboko7MFN16pPeOMaPLKsKkveLSoRRYpwR0mXqQ'
                'RrwnkVruIUNnm0w4SBuas09YugJ2LIdgQf3DzSosnZFSXW6CaXSHVeLQ1UGO7x4645fky6MzykJnh8NUfLMkLl0P6KUeBVxTuHR6'
                'eJH83KsJdHLh0oFcngM3wBxGfDpjitzVlflXLSI6csoNloR0+BRO8BLT4UtiumRCh5ZYdrgZnfMDmYhHENEhR5Qm5nTB6UTqSSEd'
                '8MzvlxNdRWLFi+nIK5dOresnsaU+cE1iyxzw0xZzXO6cA37d2RwHm5AQf+BhjqOMpAI83t8cBwXhhXhqiAC3HSbCiVjcSIWUWVSA'
                'A7erFSK8om6DcVQU4NJKuJ3x8WKZIE85HwcJ7Q6L8NBUGBjExcF2H2UV4P7xIKaMjwN/v9suAtzD0EMMEeB64VpFOrogwJ1vCDTl'
                'YB11zQG3nDXHMadiPi4dzAGvmwMubc4BL59tjkvLc8DDM81xLPzvMB7w1+yzjedjlejJx7+vGlWda+QtOy+BDPmfGMqYvZewhvu0'
                'Ce4ETfMnXCYzCjc997QLWNE4pMPokC00oSQA2bkckrmfTKsd4la45WLUclvPb+qEJsVaELFfCnFmC8i4OnkV6htfGAqfrQrZ1jvQ'
                'BI7nqimchuc2by3ThUElIn+8nBmCMrMhi6d+BcFuUSoWP6G3PSYsdaMUDn+tAUU0DNW4g3FhMh1cC9Psyvkg/SOxp3116KxwniZy'
                'gkRvfM+bfhJR81XuZhJZAFMY936hb3qhZ4JO0w/Fb1cDhrvK/qJIPjmkqIwqSgh6PAYLP5os8YsTqJXMYFDfdcpqbceSROY4n+zK'
                'IrVG82cm7KU1wjnuA2NqsitSq2UNiBgs9Tu1WqRySB/2ZGqtfK6Fmi9i1p2SLNWR8wo22QvicX1mC/6ucoF0aMn3E2d/mujOuOXM'
                'p3a6SaFcN6jmX2y6EGfLTntyevXoGhaxMJ8Vf+fU4sFlzUX9Yz0tpoqAgyVM1QTPK5n6UT8tauplvYlWTTjlbbtLxnYPVnExAaI/'
                '8NQah1ERZg6KJGQvDorcosI5KPLFr8JBI0z/9h2z37XALBN3OM88Wfi+1rztsJrn9c36eaPpGIX/0fE9ZDI3jhtlT+nAv+d3Ty95'
                'r+yL+f3loi8L5bFcMadWj65t5bJcc8mNKGYKk58y72KWD8qYRmb/bsrPJHgNL7/wtmibTUJ6svZilisFJAEsk2rCcj3QOQynU6Ys'
                'l14woo85y+VQ0zBZb+fAcv1KREiKjkgledmSHFmuQVjEsZDl2vQiLFfMC7FceV8ay9XuRRilrvPFUagcluuQ+Js6TwF358TP9PoI'
                'aOQTv11NWOLE4S1kufyLy6KcIbAH70uWOFFJ1x2Yi+UKmV8cCrFc3bG0JxSLB+dThjKozlBbe9zKZbkWwNRQMlV9BrFcWZr7qQvK'
                'aDTXm2W5ZhjWdST33Z9YPS/Jcl1xp4sjsNczVNB2oGidJ+C5z9o849JcJOOQQ5exLFfmd0wCpLJzqLJI90vwNkTnRuPWnnmS5sjB'
                'rxpPiyTDTPn8q6HRTY4+ZlSvG5aE7M5mVB0Mn1N7OzOq7sbj25qZUYFqAan1mMNbreW8dmIbtxysR0lLi+RgXUofnpP1aVwOeHbV'
                'HEJid7OHonOeZisQbxzIPTSHkz4JDG69STjwsIcu3M4m8vHPZDy9E4t/QZRZYPFFxDbPPh8QueLdufgomcjLQ+BOwc1gjoQHfqb9'
                'G1vBdHyOhJmMr2NPB9P54zjZLSfr5HqPHObPJivLFPlX/OQpHRhB9U8wlDJtJblMVcHnZAA+078DZaL6NIM7k2ET7Pj2wKpq8HCn'
                'a3hlcQ7T1wM/Jjg48QU8prGHqfiFf8FePtPZI4fgafQFwLxQ8N25J+88z0qLv//7xtlDm+PJiOpupFO8PVzfC2R/c3DjUbXDa5ss'
                'C8FFshisKZuAsJpS1NAqgS5ehWsMXnYfgN7A5jsHHbyWOjPjNLAVv1y559CfkP6ZirWg9gsuCI7+OF8OCIstHeTk8nsDbeob+9Dp'
                'PQOIc/jp1s9a4OfmRuZYPToGjlg1TkK+7I3l6SRFBDzVyP71EVcvs9HozobneOhEsO+9sY1lHtJDsKQycy9RX/8J+c5tpuEpYNha'
                'eRHIEBvH6W3IUjk4EpUF1innJZMG6SDTpbrzmXR3YB4/UDy506eR+iC/JMg6q27e9vVYLhyPTaggrOEDHrfhg/ol/J38q42BETOO'
                '0shBXOaU8xSC8eFiMFWNbK/I59Ki9HPbWufLE3QZ0fNDscXhVuu9mRvO3Y/PsMdH/754aCVGvSO4PvlbEGBjCKWIBwJ+LJcglyCX'
                '4BUi4PI0kK+enQvnwv8r+EdT+PupvKScMH3rZJgoaRIGQyXayAFY6Ul4wcp+vZvwdFYwWreeJ9ALORATVghKV26oAvSXTN1jNf0l'
                'rH+Y8ZqBtoO6sAEK4wy5i+xFjYOcg5suhdzfYzdCjJe5Be5+EaBGynXPXVx0K9B8WMexWuvMDzFLXLEZZM3DuGlUaIJn0483Rt1N'
                'zEq4e37D2CaQK4RpVD9lNqNOUHCECVmvSaKSv0puUqi9q07RBGXC1K4oVxZdhXoQliQWppt94syvSqy5tP7GryUN9dJq4lqUApes'
                'evgJkQIXJtNNJbSvV8jg+MVYGlbWj/cIleAXT7c3k3Idg6mCs9BUdXpMpQpGihlUnbklnXQYpS8+zZQAx/oF8ocgZsMzmUmEjMzi'
                'k+nc4FhKZb90vHclLA9XeU6aZ0NxnMfOSfOMkjHMI+WZYdzU0/GuuMcYmXoaJrGW38QP0Y2CHBTrkNcsGwkEEmvb/FHuRDqxNtos'
                '+iHx/Qdhsu8DKCNEDWHacEexp+IskVATf0Cc9VhypQsz81KZv1BS9BdLr/5CidpfLOX7CyWPf6E09C+W0F6YGh+qMCpj/Qqm/HNM'
                '0IbrvGN1OsCS8I6rwEmLF+qcgruj0P00mDXZKCkjdiGnGomqYy/LP6P1kojK3kDNL7QwWJDt4b7E5Np7F7M29WHdDECVW9zepJhA'
                '4Lm7hNnK8ZkDdA5P8WUMbZArsD+ZCxofY7ZNlFo2lMhPrnvDXJKoJPAfECqnjgQ3MFZfb4ZTTx9iaQYBlc0sfDbFBzpg5XQJmVBT'
                'nYllcBYvuLzZcO83QiBuYipUjKPP9sOYmDHGYXxUNydRk/htYlcPcBgq3846z+JBHNjNqULy2obeRj9dXKX82CqbBQ4ibyrr+0EJ'
                '5uRRb28hGwnQWJ+ix87mBk/oybBu6w7Vlg1W97cSrbRWVM5uNvhaffUoYytmyn6L2b0VRXp91HklZVC2GGb4hRWPoClUyV/+MWan'
                'jQHmjkOsKRzwMwlWQxGmp1laI+s1cdxs7Eb2IfjhitYEzMP8fcPPrh6zpJRUzKBtiJH4pgCeB7zoWJnN+OsCDKq/6CmKbhuMof6T'
                'PYHW7gm+m+0DSuBVBFut0y5K4BVVg85OKUS9sbFYG8GR4EnkSRajHtlcDf8Tb4KbjQV7uRtRxDSFZP5+x7ENfEdlKjMUUX99lMQ6'
                'OMlYTSLDsIljNVnGS72aSoK0U8qWgDSKPphi2u4lKJtGKX5PE5Hz5LUAYROw5m9l2kAucZzP1MLxElPYHed+YLL/DLIYWn2weLMb'
                'oGLy8hncrOB1E38Cr1u8x5xDWujrgW+1I0N7U7D32mtQuakvATHI9y6thneDTMg0iaqecRY+Y1Uw3bLrktUA8XeF7PYNlZEJfMTj'
                'tFxO47nVoO3yGFHNsRyYxY6mqKtTqeTd0DBxt/hTWWC9t0JxJ0mcPa04XU4usYhJVjN2K0ImA1IE5ef7LoS7acWG8Lmrd2RutA1x'
                'VUW2kawIPokbbh454yKZJpxnJhzixUgzjb0aS+JJxVvIlxhPWSQoyxypiJrAGYPhoqlHkqAJPA4pPm6SuwP00DrpJLlB/QZRzrIN'
                'NDipbr+VoOajOSZ0PyZ4IcR93kPFA6FS4qDO2TpBHclSRgmQAvjkktDbxvD9CIklVR2EMBcTRKoJMHHDskfG4gWk3tD3phB3wimJ'
                'MgpBtv0dosd6Qa1HKJrFm6jRgcnAN5eDhqAdlBkS+r3d8kQdRsj72P7iUJQQznBDeIZXZm0sE1JhReiytByTQeCki/amYnNfY5Vj'
                'gKdziYJ/BWZNJTvllK6sLnj2zJQoR8QHfmwmw2xdYzMS/lhrbBVCtc559TwOT6U0VwZDk417nUFB7THp9TcdTtsS2NnUnpLNYM67'
                'fXljWQEHHEtw/4CHz9NgcSZGeHViV78XXbhpHW8baUIac+PycfejeS8gNku+93LcZ4lclXJCAaHz1BLTPZ0Wi2JM3LDCcjJO5BL9'
                'M4namJqOC76ycGaQqbZpAIu2RKzAfBYthpQjR10Z1BtxI4/YIBnLWuSTzmYfQupmKruDfrVCjzWHRUsilusQywT5IJ/ZB+yWZEGl'
                'Nmys6hEpQekDVffYQTve9yxaGmXMOeDMoH7XUG6jvAxqRZqrdE6RYUw+68FxPUWPNZNFI1Cyn73sYwWgWmrR7GlhRWmM0yqzX43O'
                'Yrkbi3Y2YQyVaogoWGAXp/T7CdNlsOrqqwtHEx83vIyPIah+ce7Hf/7HlzBzrhKVwCFr+wveotkwk/DgGct9itU1jCMLmTCVp1am'
                'UGUDpirlTKYEZTTB1qZSZgVJWs/IrD2wLCTGjmUnsnNLoCDRh4x4f5QwqKibpCOU2WMGSnTdIqIsWCntXCWifi8zub8nM96hmhE0'
                'xZ2pHkoEB8wibARQSorFt0MnjeFvjBMtxbTxmCcpEUzjkcJoGNcxQceaJfgy3uKfyVST+42xrQ1iCpHm1/qWsK0dY8qejmbUkSXY'
                'IqsaS9FrNzGZz/03H42jOffjv+PjS585hkLfZhpyVC/VNNqoGlTScAONIjArNSfGqMRjgsVvS8GFqdT7NlIXH2LoVNLfa2bob1Pq'
                '4I4oBg9/RbHK5jVc6xOqILncUJIs0TQrlpG61uYZiND31L0okiDzV03nJh/pmjE3XfN0CturfXTTWLSq0HLWvNgdM0jJore2c13P'
                'J1k1l4lnrej+KKWZ26IC5T/56qhpjOy1wUGkiSTR/oRryDrS/DuIOEfSyxMmpMuehIp2EalH7QrPYFWblqh3oFOlwT/8duNZuuKA'
                'fXb5h2jc/Luvp6qs3PzIjckRg3S3VYSQHF9KCMnXXISQpltRoIszetUq4Ofklrf6MBgboJ7W0yfjOnfrj4wlEuma0mm7psRU6hyj'
                'f6w8esnR6Nh04jnUXIPuo+7xHlFxoikvqEuxVIp4Lhj2pdZjohmxFNq8Mr5vEOyEW62WAvt1Fiw3eR9AJ2m9lhdQTy69iyeBI2Sm'
                'pTGUX5Mn9L1aCuTuNH1huaNokKXQN/DJkOJuIT0wUWWpOP5zqWs01XL8Juyo1qSxICbsKlKID8axRxUkDJKaIR3ilgISAUnOXZff'
                'SLLHn5xJ+sUBK9EQ3ib6bwRDB2+/mpB6fWtvPwb0nwcV2gl9KZCc9WuccXAeFWv7sxUDmWuUGahOPwxcXMvbpyY0Bah6fQg6jMTq'
                '0KBhC0bgYsbj5X0EFmecblZDEAt7vwkDym206w3wVFAuDxtr4Ybmsvw2wjikXeMBCA2YI9ioMASafq3pA51n9zz0Ksgfi9MJqPuW'
                'c7oPdDy0P2bkIYasprd3jUV4sJFwsNNLInAl7Xk7Gp99g0hsjRMxb4fjRoN1LtSMbw43jYT+rDubS9c1t22pN7b1pZMwudQe9evZ'
                'u8mZz278vmniW8WMv/Qf80DmZH3tlki/m9ruwglIbERYE4j2j2RueyHUf5eHRvi75q01bF+20r4QDsgnUHAOW1TXN5OfmQDmiDhr'
                '5VtcqXLge2hPMOM6j3uYYdcjQb0uUbvoe0S/K3pO+F5nyMH1tQsyNKB+Gwd7It8PdaXCqJ8vDSnr6xJcud+GTHVcxvLHRTiOksti'
                'frviXpbEb5cCxj6U+dmEXeqM3nj+fkpm7M1Tmyd3LMFzyIQZjCL/XaC18fxzz9Kjj31VlQUrIEemo5UpsHsmLvz0I8BOVKDr1xhY'
                'Ik20k0VKlgOyGERZ1S50zudWdEQcDkIt/W+60FIEzYTIvIAZSgR6dJR9JrK9THN6EuSXI79m08ZAO0TkenDnywYOR+5jo2Fh3bhI'
                '8AN3EVjUDCz2Yl9r+kCmr9KeNQecZbsvIZgx90Yin/qdescXxjoeM9dFdcrrGj6cGDLLIZPBlkqlm4BSVyqeeSoxNYnsdPbB1KSu'
                'hJIananJLoemC8/H2u6f+KYO12vbt/XUA1efZsZd2z+pEWXhKjIrFfvZewMw2DKaPpivQB8r743sKyY0Z2xiuLNhBOsaiK5bKkta'
                'DP7eznb5XPJ2PIP7oi2jAqNcgbtJYoAUAFYu1Cz7xkKPGeAh5ghn4v3WQq+5SxKT6icOK4jIXn5RJmCxRyZgTTOwntnX1tuL3G3Z'
                'CwjFT3j5v97ih/IYJxDovotkhIHljcM4H70Xk7aLfaRIYKo2CQ7Z8+lN87l4Fqzca5Y+bIT/C31pc/ZXE1Dy/NUEVHx/Wc7Svgp6'
                'k+b/Mg5HHCc+IpTJ7o0/3X7hYVrG0+u/TevGeH7kH7nmamwm6TnjuwA/G4zWADI8oz0ZbkK0VpV5rZO5rWC3zBqQz0pZCRg/nUdc'
                'H9sYOig9mGdY/B+38p8st/Vv0So5NV94/ln63eNTOE4ONVAaj5PVqaNpEH7k2QcRICXZEcdhNbv4IHW9bHIEI9fYiyy/BX0Jd+rq'
                'zcJI0RdZEjqeBTI+hpF92Lha6DocCfNDVWUDdiMBp2F3ZRPzRR5jYwpgFEbkBZhBFB3WEDzK+puVZX4zw5nzm/PYKtDQLTHyHSaD'
                'PopsjIRhf9HAENkA69uT0G1RZ0EKRmMgUhYeaRfsGj4slhjPi2YsVRW7GUs1gMoAM4WYfUT2OfuAQqRTPj5vq0kVZDI4zqnFIiUj'
                '773jU2vix2cZzvEJOJMslYP9gnS2hH6iB3VT607M9NrkKcrnYthhoyY3LeLhGlR94B7kAx4AjbTsNUASgz9ZxeAyqyQCY6DpIGjY'
                'WSqdyweEpqRgn3kH7iVkpcVcPzS7b7kXUUf+GyDft9deirc9OPRZSQpy/QwaWew/uOFQ2Hm8l/d5ImhODFNwXqRSUwpCCLVtc3Fo'
                'bQM/n9eh1/tTDNIDeHyhe3ARG+2wC8McUE3Ccrj7h2Z6AtBFRngfyAR3+QFoCIDGQ58DBoIpEVwZCA6Kcy70Z0B/7MbEV9b2kn7i'
                '1b/h7h5/3sf/1/VXPeS/9aPhwQSYlt66YUHGcitgoe11CV1FluIz4VH+WweMhSYSZQ4nPir1jfCPXYismp/hCY/udQG/4Yi/uryH'
                'W67h9I+BMF+F7U0GhJlrkpsxfwlZ77iazNfCCMZHEcxvQsPEraLMA0Ff+AuhzNNCE+SxAOZVYHjULi/mPWFG6nWuTCdAT/TFTmwP'
                'QUW1RRKCn3L7VqZC2rlf+40ZSFSOBOCGDDrCFX/PDlDP8zlnsHs6mHx/WN+iGNAxnGmCTEkjOXMIacqGcSYYSinyHgtaYHUXxwB2'
                'ajqtg2hfdt667sBKbTOT2hPqurO7/3vO6z+bEzCu6rPOJdnjjk0CLgk+Azfft6Xc2TYsiOLBpHww9CVrtqqgtb4PnY0S3idpq+EZ'
                'ak74SV5b8eXwHU47l0xms9F1H7l2emC09EW7NCnlRZ1f2BGuL06b8mER1+K4rTx+cAG3ijDx1FaMNk3z7rGgSI4ErSKPezSUZBDt'
                'eDo57RAqBD0PpAUOw7BgG3CzbgcaSjjTpQqq0CGwMEVNNWc60KgErToqDxpqOVOp0VEA2QD6hxDtMFqo6kKnvKjlTL01a1rNpc2l'
                '5dMSZsNcVUauKuOfAkGtZodvD1+LtcddPzorMg8VCLoQT2CduQSr+OY0mc5Fnv0V4HYD9nDm6R6dv3bezZ3FuzXN/HeCOa4GOpWD'
                'v3e9VwHX/D0gk51dGpbnVhaYnmbSA3qgrJSCoeMDeLt8YLFmB8JkE1MkJkVnh7lsDj0oi86GVkkU4OUFuOHfLjApz5Ah6QywUV7m'
                'eGLfe8za3yF41/RrTR9ontmrmHZCMOM3gnUf6vi9bMdLEVA6uNazgGsoNmRlOWkBZTwPmss+LmYE2Abu52D7gZnKaQqdZN8xDRPE'
                'yizBXZ7sy8qScz44ctbRG3H2+JvHZnfKyxN1c52Gc52GX0GnYebCnYbnPzdzGq5AhHfQTsMBi7Jpp2H8VCn4/s7rSbjTcK4+DMXl'
                'aE6ZfCeBiqfETgKk5xvpJNDFxGfOzNvOctjEqNzOzClzu4lTZj4zp8w3zZwyp5p5Mv5q5gO5/w87ZZ79c5wyvzJ7lTfMnDLzZJk5'
                'ZW42c8psZeqUaeaBa+q7y3r9ThX7CzNOmRXNnTKbLEBOmf9WR+0XAL36bbyTlhHdF9thehjJ4CehNpjaajJsQ0lfYNsvaLv4knNU'
                '4G1xn1by8yzV9sePUNvxYEaVjGXzsnFypoC2BHe2bTtn95zKafsoh13239amT4qOs3bdjrVlxt3a9UO/MtB4kGc2uec/+6mDZqyo'
                'yqlNpO5AhRNlPrBO5gNBWQKgI+CJBpX1dvLJX+udb07YNcAw72RhJbm8I1d9BpmzJMYlG3gYj6SRtuD3bi8Z3SECm1J+hBOU48bq'
                '4eXo4oHwujRI42hCotnXuKBF0Rb/nUWuapXUnXudZBBgnCnUZ8ERgq26gz95YNWus+AQFKKXfRxPuyRh6bdbFDgxAv+rQFCDvYq6'
                'ZdxaOqxVqbyeVq8yAwGTnR1UkL+lH5QEQAcBsELiA/NVkaXSpyep+XAIRud4Nxm79NDd55mZ8fcOLRiEORhX4mbkfTVbu/Ne/er/'
                'tvXv1mcvp7U0XhQSOZ/LvNQProALedIxLyban6F6MkziOd3rreGZvFYsIyXeKg1I5rVKPgNWXgau8XIYLBYHS7nBluIvhFU0wSr8'
                'Qay8CVbOBCtjgpUywUqYYMX/TKwZi5VmqllwxgFWyy5eX6aLT8N8y8WhKAASE3nA8MXihemCHLD+kFzcCsiSdIVBS6RRLQ4jG+SH'
                '3QI8Kn6L7azFkQMFcxWX/JLFGO1Fnv4V3lMLcehxHbIXP4SvlL04WKJ6OHjE9rupqTd3DSNLfOTLJFPz6idBKkw9uJatOwGT5yZ5'
                'wxzgNn8q25SeXwKWreknMYU7qmIphg9KdJZrrThNfoNLcMAFG0XYEzdQzgtgkFN8iKTdoAbRN2RQlfUeoVOFdWNqUDLg90S2c5j3'
                'ppDxIs807uQ/TCkOYKlWE9J4GSm3U/0Y8XM1dmhhJQJAkfR0P5QctxanrOq7UmgWSisCrzAHKCQzkpt6ZyfoWEPeTvPnRlet4mXu'
                'VbS7lOmrLsUFfU3ybzSTVNxBenpJorBp9f0DGbgLBi9nZTJXjHNuwJHZpqPoP57Op5QsszpL4Euf5ES6QJ2VqCy+0y0xVEkrQxWS'
                'DdyTrsG4tZVkmQFLLJUkG2gXvWDFkc3k04D0/V1lMNiwfFmClUyqfYZ8TJUHvk7UrYHiQ7Y/8Zi1sXB1baQsqHvb4lVHEpywffpX'
                'qg7MN/hjapUY/I1ZG2cBpkvHOVgjZB4hRJ3ATkLNXnFR25+z/LDHLE3Enw0BdpUf6oPk1KFkJtvGaFsro910ck0zSgJ0JROau6bC'
                'kJZBRjLCvUa1hXnUkbIDHr2rDD5Qk5iyfOBjhlDhNAP1gLd5oDpQq1CZWsyA1/q5FEgj6qYJjFO60hlNLUb0xaP+MqgPomnaTsxj'
                'UnSDZX0SljLR9jq7YeLIRDXN3sVX6kIyiAjzH8FDeaBCwR3XV4zn2MPUq7BEl+SowwkBRdLZBNSS5MyvULGUihCiErtjlaN7G6wA'
                'OtPfl/gFRIoytX1Js9OXTJEk6GD4UKIz3A9nkw/3xZZgOmDrKmfgu5z/HZmoUuEBosau6sNVA5zkX0l4jon0ChSfpFW0eF1mDmaQ'
                'cP+2j5QnBhkBoQQL7F+LIOU1vPZdbSDRg0pu6RUlbvkKfrJlyzZeeCVm1sNzldzwYbbt+oj5slU2LfvwOQf1u0UGblPXGuy3V0vm'
                'pTIGUWhlUmtnq0QGsoO1ALRA14l6gmCh3i0XyylKOAjVWWnPJouulI5VrwSm8DRQOcMHbP+/u+Bz6bIXyTin6J4yFW3E2upPz57h'
                'eEKT8un4KUAMbkoZyQtkunqE0innA9qRKI9KnDJoqD5fLekAp3beOLRpggMoAQv8jkIckPUWufIlsP0bHBBYI8cZQ4DGAfkm0Q93'
                'heCAvsNKveAHtcEBFcsmH24y5QG3kXy4GxQHBHbeY0QE9nLGNlMer2+IOKDeODsbzXBAbsYYJHgg7ymMA4Kehu/AAkI2PJt6PmOv'
                'OipZHjJ7h2QkvFUfrgGdFAavYyV/b2xb16lVZAz78ydYfKHEqXYI7LGUHY+o1/ALs4JHyOJaTfiwK9dNTj4KzO1lDGdzKQYPnEyu'
                'QwLMPLGGa4RsTNXzkPiFoW7zyxv6JXETB1HMcCanNoXFp+o8UY9VorzbzGCWRcfhR0FmcGJNyQSOqiiJ4KRry99gsqY34svcy/+i'
                '9kXEw0FP3qsheDP0sr9ZgFt1Mrow9yi6XxRv7gcErscl8Gbo/f+UiAKGWV3iKhAyITjgn1chVPyA7Ugixuo1cGKkEMJhE3A2pBHr'
                'vz5QONjwqmNSbaAnySByblcD9Q3sZGyyINXI8qt/UTu+Pb7/88Wn+ruj2lU+szGNEWz2JqwZEUw5NKI5NJPbDEvlnO9R0stCJtRW'
                'hSCCyYCHPVWFAJive5LNW9iKP3hzs/+meTe/+RRXnLeCOmbEfETFBYlyDb6sY4HFt8Kw24zrHNGftwI5zdmr0DaOSSPDMHEE/44b'
                'VbjNchyyD1n9q34UI1PMg6EFuMPxGcSEafItJQ87W41WwrKt1Oceq/SZt/VljOUWTh1BrLk9/xCk2Oef+MVXAHcTF8xnA268Wxqb'
                '9n5J3EWCRDSy2WU3t1ly+yqD16yIRoNWXHym73cR2jAOyf1X9K/ObsRe3/AJcRRhHb6xIH8dPQrjr6Mj/Ga5CbYqirTfyS+1YtmP'
                'dGcSXVaB1V1W4C/GgvwyScEvs5nKLQlibDPI5FgujBlHIvIqjeJv8bHh3LeX4z+vGYDYKKd9/AXjMT2Nu2CkN+9ymkP3874ElS0k'
                'mmGF+dRv6gc5MxsUVXTnISdMUlGlO5h0NtqJALZzsnJjEOBy+MPw8L8Zy7z85jB+cx3A4vHVDefIfEZn2AKFHmEdjzBFa8lFUpnb'
                'vIl/kAVzmh0rgqjlmhl3Y/2YItKLXuGaYrzY8G23km33doyjijt1T1CsVxU2IIPBrfGIs62khNUV9/qOcmg4NalFfpegisO1s634'
                'adnsKh7zX8CJISocPa1+QZfgeqN+o9L67CyiqKAf9YCrJ7A/FmR47g1VQ72CVDWFDV17PTXj/uGJup2na859F/H9leTkqCnGxug0'
                '3WDcbZ9YyAJjmqgxjtRS5VO5p0ttvb3bqTqMZ96qvfKCplfzU9PAdVc9Jlsin8YlihbeYYRKuyrDsUvRHTuMBemifN69EZVhUS25'
                'P6l2p1NaUIG3ynr1KqgekGdf9/Jura70536kkUjRNDjvJHxYlJ9ZYAx75iTjLK82/0Zq0oVviuHmEbnLy777P+aD1EM='
            ),
        },
        72: {
            "ascent": 67,
            "descent": 17,
            "glifos": {
                32: (25.062, 0, 0, 0, 0, 0),
                33: (32.844, 10, -52, 13, 52, 0),
                34: (37.516, 6, -52, 25, 20, 676),
                35: (60.328, 4, -52, 52, 52, 1176),
                36: (50.094, 5, -55, 41, 66, 3880),
                37: (72.141, 2, -53, 68, 54, 6586),
                38: (62.797, 4, -53, 56, 54, 10258),
                39: (22.047, 6, -52, 10, 20, 13282),
                40: (32.906, 6, -55, 22, 64, 13482),
                41: (32.906, 5, -55, 22, 64, 14890),
                42: (37.656, 1, -53, 36, 33, 16298),
                43: (60.328, 7, -46, 46, 46, 17486),
                44: (27.359, 3, -14, 17, 24, 19602),
                45: (29.891, 3, -26, 23, 10, 20010),
                46: (27.359, 7, -14, 13, 14, 20240),
                47: (26.297, 0, -52, 27, 59, 20422),
                48: (50.094, 3, -53, 44, 54, 22015),
                49: (50.094, 8, -52, 38, 52, 24391),
                50: (50.094, 5, -53, 39, 53, 26367),
                51: (50.094, 4, -53, 41, 54, 28434),
                52: (50.094, 3, -52, 44, 52, 30648),
                53: (50.094, 5, -52, 41, 53, 32936),
                54: (50.094, 4, -53, 43, 54, 35109),
                55: (50.094, 4, -52, 41, 52, 37431),
                56: (50.094, 4, -53, 42, 54, 39563),
                57: (50.094, 3, -53, 43, 54, 41831),
                58: (28.797, 8, -39, 13, 39, 44153),
                59: (28.797, 4, -39, 17, 49, 44660),
                60: (60.328, 7, -43, 46, 41, 45493),
                61: (60.328, 7, -35, 46, 24, 47379),
                62: (60.328, 7, -43, 46, 41, 48483),
                63: (41.766, 4, -52, 34, 52, 50369),
                64: (72.0, 4, -51, 63, 63, 52137),
                65: (55.719, 0, -52, 56, 52, 56106),
                66: (54.875, 6, -52, 44, 52, 59018),
                67: (52.844, 3, -53, 46, 54, 61306),
                68: (59.766, 6, -52, 50, 52, 63790),
                69: (49.188, 6, -52, 38, 52, 66390),
                70: (49.188, 6, -52, 38, 52, 68366),
                71: (59.094, 3, -53, 51, 54, 70342),
                72: (60.266, 6, -52, 48, 52, 73096),
                73: (26.797, 6, -52, 15, 52, 75592),
                74: (26.797, -5, -52, 26, 66, 76372),
                75: (55.797, 6, -52, 52, 52, 78088),
                76: (45.875, 6, -52, 38, 52, 80792),
                77: (71.656, 6, -52, 59, 52, 82768),
                78: (60.266, 6, -52, 48, 52, 85836),
                79: (61.203, 3, -53, 55, 54, 88332),
                80: (52.766, 6, -52, 44, 52, 91302),
                81: (61.203, 3, -53, 55, 64, 93590),
                82: (55.438, 6, -52, 48, 52, 97110),
                83: (51.859, 5, -53, 42, 54, 99606),
                84: (49.109, 0, -52, 49, 52, 101874),
                85: (58.469, 6, -52, 46, 53, 104422),
                86: (55.719, 0, -52, 56, 52, 106860),
                87: (79.422, 2, -52, 76, 52, 109772),
                88: (55.516, 1, -52, 54, 52, 113724),
                89: (52.141, -1, -52, 54, 52, 116532),
                90: (52.203, 3, -52, 46, 52, 119340),
                91: (32.906, 6, -55, 23, 64, 121732),
                92: (26.297, 0, -52, 27, 59, 123204),
                93: (32.906, 4, -55, 23, 64, 124797),
                94: (60.328, 7, -52, 46, 20, 126269),
                95: (36.0, 0, 10, 36, 7, 127189),
                96: (36.0, 3, -58, 21, 13, 127441),
                97: (48.594, 3, -40, 40, 41, 127714),
                98: (51.547, 6, -55, 43, 56, 129354),
                99: (42.688, 3, -40, 35, 41, 131762),
                100: (51.547, 3, -55, 43, 56, 133197),
                101: (48.828, 3, -40, 43, 41, 135605),
                102: (31.328, 1, -55, 31, 55, 137368),
                103: (51.547, 3, -40, 43, 56, 139073),
                104: (51.266, 6, -55, 40, 55, 141481),
                105: (24.688, 6, -55, 13, 55, 143681),
                106: (24.688, -3, -55, 22, 71, 144396),
                107: (47.891, 6, -55, 44, 55, 145958),
                108: (24.688, 6, -55, 13, 55, 148378),
                109: (75.031, 5, -40, 65, 40, 149093),
                110: (51.266, 6, -40, 40, 40, 151693),
                111: (49.469, 3, -40, 44, 41, 153293),
                112: (51.547, 6, -40, 43, 55, 155097),
                113: (51.547, 3, -40, 43, 55, 157462),
                114: (35.516, 6, -40, 30, 40, 159827),
                115: (42.859, 3, -40, 37, 41, 161027),
                116: (34.422, 0, -51, 33, 51, 162544),
                117: (51.266, 5, -39, 41, 40, 164227),
                118: (46.938, 1, -39, 45, 39, 165867),
                119: (66.516, 2, -39, 62, 39, 167622),
                120: (46.438, 1, -39, 45, 39, 170040),
                121: (46.938, 0, -39, 46, 55, 171795),
                122: (41.906, 3, -39, 36, 39, 174325),
                123: (51.266, 9, -55, 34, 66, 175729),
                124: (26.297, 9, -55, 9, 72, 177973),
                125: (51.266, 9, -55, 34, 66, 178621),
                126: (60.328, 7, -30, 46, 15, 180865),
                176: (36.0, 6, -54, 24, 23, 181555),
                183: (27.359, 7, -32, 13, 14, 182107),
            },
            "dados": (
                'eNrtXWeYFMXW7tmcWcKSc84gSE6C5JyTgCQDBgQEUUAJooIgICI5SxABQYLkICASlZxzXtjAsnl3Zvqb3enprlN1qrqGq1f97tQP'
                'Hqb6Pb3d1RVOPo9Uo+1/9D/z4wHxY89J4seK9cSPiV8RPwa+S/xo3Ib4UbyC8X+bX4jx456iROs/DimK8YdWKIrxhyYqivGHBiqK'
                '8YcaK4rxh4orSnnjzyj/cfvXfKzirv9Vdj74Ou3n954L/28vIPPVK9Z57YHec8zZkeDLneMvGuvN2cKtzo6f+eviA42mn6ujvdbx'
                'Pp9mhwYp5Or4Br4X0vwSnYhres8FZ0eUhUtTX7vrfFdHHq3jB/6jjdMg3VwdvbSON/g0B50Ie05XxxJjD+K04FQn4ozec8fZcZv/'
                'Z5prd53h6iihdSzm03ypQdq4Ot7UOl7h02j7rjXM1bFWo8nDJclqcyKOujosUc6O8xAXrrrVhnho/rs0RntJ657r6iikdWznT5xP'
                'NEgPV0cfrWMUn2aPBsnn6likddTlbwVJTsRVveeasyPZn0tTR7vrQldHPtdxyX+0URqkj6ujp9YxgU+znd7Z5hq8Caf5xDsRt/Se'
                'i86O9GAuTXXtrstcHTm1jiP8RxuhQQa4OrpoHV9CXH735s2bHpr/Lo3RBmvdr7s6OmodH/BnwUb6aJqldbzIJXFxErfpozfGi0tT'
                'TbvrEvro3cB/tJEapJer4xWt4x0+zU4NktfVsVjrKGvKSVzUe245Ox7y/0wD7a7fujqKaR0r+TTjNUhHV8drWkd/Ps0hTV7J5ur4'
                'XqMpzOck0pyIk3pPpLPjOv/PtNDuOsXV4RLJFvBppmiQFq6O9+jdXtR+yeQ8/0zgAVngQVngIVngr7LAw7LA38yBWVtNWLL9tJNt'
                'jL9xZOPMYZ0qBjCoiA/P2JGNw3Z98/i2+QxY7qUpon0mRD/xosUbkga0zDTbuTTgZFUO2EqVA/relAT2Jnt29KvkHPDQYrU6jFp1'
                'Jp0A7jBgCa0dv/eTXyakxZTfNaBfsgHsrtDAjFb0o1MZB3hFA/fIggK1RuhInGw0D/iKAbwlBHYj3vlFEfBlAng2QgCsSA7jw/dy'
                'c4GuTVZr9htxvBm+Hftm9iNz36pJKW1e437hlF9GlSeA4klx7l19ditdxTPnyXveLuQEk0n2Wz5a4uK1W7lcyFa3TO6pL2//d64J'
                'kR8Sh3WjBQ8FbxRCjqil8nurr9hx5ADmQ4UeQ4HICZg5KZK7fLLHSgIfcIAZk6LQTyQykA9UvHYSwPwCoM7yZ7RKIqAPMQSVRUAl'
                'yQAWbbamHheYndRwtlbV069nw4HvEOtOaZ0pde8bUoQF1npqAKc7gZka083j25fL6a0BAwq0XkaOeFUDqD3Lk2TsC+5UaCBnmZWR'
                'BGYITBJAWyY7aw6881LmaHjXn3JJuFrHBBljXLz//LM2DPVsY09meoVW6zn2uz1/3NYEsfuntsx8o5qP6DA+8ice7G6yCof/dC7l'
                '0J/OSR3805k4abZwvwkwpOW0Q1di0iLP7xhV3ctMQZlUCLmWbeIzYj5d7eON36KLQPfRMY6alaeLos96z3n1EmK+GMPu21H1kXtM'
                '1S6+zF56B1sf8aUZXHmNP1rN3qJGGroUL4SgH1pV4xAV4ikX1eM38gaUm66v2vEU7lWt/z32Fi11lqQgUNSoMfBBwjXR6JQ3Xyet'
                'ttM6Vqio+Dlb41Bqsbfwd22vumipW6B+InFVbZQyCpE01Um0dguI217aYRydHbnH+yoteiqrXV0lDJhLFfwaNvcmuQgqKgwPVNsQ'
                'N2I0VgVVws93ERRkH01XSLuU5dYX0GWkP7iuXFfeVmkddh1tMczEl+I8ldbKKcNdXa1dWrjT2gzKgt/jC5aVmOjqck2FYdrvnpxd'
                'xXVd7ax3rVGhPiavtrfs5e1M9VRGa3dd64m2gHumlTFToKqXLZT871LPNNZ+fsHfSH+mJ9l3ro5Bzj+iHda3g/j3aKpLRgXBnqlG'
                'OVWfo7Wf7UU7/klj/8jjX3qqvn98knm1sPauW4SnRrVUdB8763z2TZp6uYj46BmE3SKuJBDuPjY7vz5i9/UnTlV4oCbWXNG13OWH'
                '/HT6fmrc9aNzu8BtoP1T6hantEf/TPvdRAO2PkGA0uaD4y4rOOeu9NZ2n5LaUK3RdoC91J9Kg3a/4FbTf70am/b4ws7RNbworV28'
                'U2iqgMhBS80s9i7Zdphz2aAyz1zxLULvaza4TFbP91ecrXxVeI9p2mlQF+5M6spqQRE9b7h+xYYJblEhnVSV+uiD4Zwq2S4jQh7d'
                'LJoFMiYCyv2HtfVdE2og0NYX6phdelS1A3WEkycCraJ67AQc0z606/1TgpjtfzDvHnM02aCqxmy5CH5nT8hlvMWsbQGztN+lXARr'
                'FNr6wzNsex13Xo4M1zpqq7QtWQmG2hqmvaVd7u3qaOYiMI4pb51jQm+RU9O8/6L31GSfQ/eg+Q29xzJtWZbTe0qqjBlcHw90m6zL'
                'GorCBd8FM0f7nHVeu0vatK4w82MYx9IBJk8n9GxvBySAjMZysko+TcTbBno7uCgOUtYL1Br/g3YaFAO93lddNCMzf2e5IJjqTbRL'
                'Y6n+gfr+saxKYI5u+i2fsGeonzZ412gdsPdefB/rxD7Gx9ql5uzEu4fd4iv2FkW043UdMlBlEKXVbESs3qypWwtgcy/7LloLgVmD'
                '2mkXR3C2hJak7ip1Tn4EEqRtvOf47jHlh2w68yD12Y2j87pk4wuYTT5a/8fNWGtS1O3jG2YOeTmnlHdZrUUJ9FA92vh+dR8xVaEt'
                'coZCmlFJVJ+H7gtpwyRo76nPRVcu7fnoNqvPRVcE8F03h1QM8c1TqcPXmjXlTbm3226olgp+fF9It5Kc0hHkFd/+twR0JJdygJY/'
                'P+J79ZwiXTgV+fYLOSO95OlWk+PSSp7ubZLumPwfhN9vsPwfJD1Y1eSq0nQV04FWP0KacCyYkSfDZOkoY8X+ACmq0MX0GvjJW4Ks'
                '9FWEJ4fMI3FjXT5r9hRbddN4Bh/XaHdMx5fraJLujNGvDXbrNJl1Hqv3xjo7yibyVdJddbJSxFA7D4jzJHLLOkCY2pQ9w9WvFdKj'
                '0Hn+WfzggZbgUh4sN/oyHyJnPIHKUL2FHAWEMU6TV4ghpNkjSK+lzFmZqf7KfgEQ3i9CcqeO9odCOB2RHk/5bwPCaw7LlRcxCJma'
                'zaIE4KlLaCv1GEqfWZQhxM+itG3SUI5VfQYID5YmTsV9UOkC+dGG0J5NGGo0Dc8comccyftZOVPhgnO2ryK6viWn4wAOXStKe+g0'
                'sCBuLowRhlQvOidVGOrLCdQLhSg33Mw2HC7mRSxdb0Z1mvkBc0NWcgNNNsPYV8CSPQ5d1fz3QbI9Xjx778FcgHdaCumeEna7jvDS'
                '/a76buTbmzH4PjSYc6/TtAH445p5fMOLd/ga43GvGyPwkt0d16zT4YynjFw7qPMM3pvcItysM4cB7hEu00fOZ5oQuO9dK4//b3OH'
                'S3XF4Q7xOtc+HfwJ7lJyrLc36UKq6uEdxuTov48+Ji5PeoHSG2jN2gHMx7A249afeJBgtSY8OLnx8255BQef4WL/7/6f8UZzjclt'
                'iBOVbZiC66Axst6Yu4mh2A64a1jAjMU91IC+bXw34zCIMbaJ0Qb0c2NTMc5qqyGjEWeHoa7xvmH0dtF7OxPWMD/ktYgtvDgxXV5W'
                'ED+PGH20LMT+sozRisAnmET05sR4l/Os0iWDL2D0cNBJn5zeFfReQnubpout/oQu2wgvqEzc4Ad0U53G2ilUMoqD9PHqRmtDqGHc'
                'SvTWVhjNjKMZ1p7jRG8ptLc0Ko28wJoiwF9biz7ZLJXy24LmIHB4ErPJ4XWh8yhE71q9NzCddOXAxC7jCykL0K85EP3yhdBZolzA'
                'ZpRu7SWYZMKXH5qevO5gs1r53OiN9sG4YbUhKo3ORCWVx8ZLexNqfsMwSe4ZhPKR3AmI7ZrYNSYq2A4TFaRg03iQgu1cl71Qp7ru'
                'CrYjXiLEJmL37MPqrjN32jDjmPuEgHxosKgFiUPxMTKjCG05GPOgKIPpICSyidjqVHKnoi+wxAD3M3pfIBQgBPgPbJ/Tnc+h4jkb'
                'wYfXNLp/hKKMAkOrMgRvg30KJ6S61xXG01vNjA1FnoLwkSbdFA11ocUYOHWrcQuCyU0KQHeEJqzB0tHGGIOMyjIKIQQ9ZDwhMlsu'
                'VF1SE13O3bHzkOCseqFseieid4GCMf2r0G3CeI2GRO8m9A6r0Q3TcG4gfW+/Rg+ZUbQ9jeI21qAbPKkKM/xKCPbyMXrUbmXc4KFM'
                'SMpnurO7QrDYKcF0ZESmUzG2jIioqqFkCLTeSyjrjdCdbMRZ8hbj/5IhGBrq55+wYz0HsYTqYE9wFFWrdGMCQTN2AuMQWI7tGnlS'
                'Mabxc2ziBkVjO9cIbJfDd8SPsN0z1FjWY8Vc/Tmhyuvfgql0pBkXEzjcKWo7ptWB+ijG7+0HTo8fZ5juzuoMxrtf5kEdGab4upSA'
                'P1UEGEu3y7qTUhdD/fR9KQPT1pC6Y0OV2obQb13i9C0519hQZyVNz5S6qxvWDDvxbyZimi6XV9mIyuWJXwFNQqV1DCpxai7GxvA9'
                '8BFNmIIaa7oSyzGqEoaovB78teSvGTe3KhuZJ6ZQ1XDDRfIMHVXT4HPTiX8JFDHOqTOd/s/nauwBKON7WRcXNL5XoyPE9/LTvrt9'
                'TSk4N9qdMZzTnPNna2Vm/ni9ck2bP5nzcH9tdB76vnlP8zyrdKQpdz4HDN/j9f95LTNmcowH9aA9aA/6P0L3dUc/usWD/k/Rnjno'
                'QXvQ/y309+Ta+0d3kIK8NaODjOiaTCVEuJShjelHGOfrUI4zTmWC4fp7Ixj4sqv2RpTcO5fSF98JdfKiuqm9OUwcpC6lzAIPsypE'
                'FBbh+RCWTmViyo1ujNb/Z93gA/9rfrAryDUvizFX/OIYnT6tPprAjzipwlyxPOR6ltZmdGSM6b8he0kTxaNYr55y1CRWWD16O/aS'
                'ZnhJZINw89u5KTzeQbThWtutSaysx2TWdK47mktl+C7fX4v1Fg3QnEVOKNzY+jHsJZcbUznmitdjOs+QQmcWm6LwIgIIPaXebnDd'
                '6CppRPP47mItuD59z9hYicL8xHBD+GfJftTtJNOFyIr5TWe2fqyqntJN2nMzV4I0B53DLFFHvivvcjaGzXVCaprFc/zcBhPZS9/w'
                'U99otrE77BWX+e8b9pLLBNOIvXSOtikrdCaZ5SzRcDoEgzG8JbGO4Tk1ldZGlsiVQaGvwovmsrLhhKEppPsV6pGIRGSuYiLudG+d'
                'p3TggEIHSHyi8MJCCGupvqHe56a7cQVLTFW44Y1IljGNJYk09z0tNmDenhvRqWmxtw8sfrscP7RGiRh5Hh6ctyYUwpFhnyewx2zq'
                't5hestFtXPh60pld8zauqDaJeuzPRXId9AAdKhYCyWiBl818qXobW819M+kyrgju9PNobJXsoRUHw6gDl8mqLHBl2q1tcT7LAbgR'
                '67unHtF3Vwtw+XRGaOYhXVCthNdNXhDiXRHafumdGaTF+QYENTLu0yAFywMLdBBQU+GxDcayNrAhMXFLwBHaYZFbqKK2Q9aH2eGU'
                'c1rgfdgdTE7FC+Sg6KKgafqcLUcR8LMOfsY5W72XwE8q9icMXHylG/hJmwXATBn6LsCGUth4sJZGASzNkUWSF78dr4pYUvDhFk5S'
                'abmJbGAf+A7MJRvnXHO2FROEz/AAPMNogKWDZIDD77eDAZaOqAbu15Pgt6Bc8yxg4xoGvzHFsWWF37go+Fmf4+XnvAjnZA88E6bL'
                'q+Y0x7NRIRJeOllyyvN2iWCn3UbpKKnTcSu1NsHcTwdJDryiqTVP+m9QodS1gM+sF+U9rq4nsd+SVzJDK/OCvY+INs8NvnBlxo9a'
                '/VWfPhaQ+Ge/s7M8WIE/aWvOD2xIekLN+aD33vtlA/yKvXEJV0fmeGh2tsQbEmBTszOrL5Jck9NmmDpyG4uSOpCH8x/jK4blaHIX'
                'R0Z3QxiILJORQIi0ublxziTnRxch8vZnhQW8UcnX5u+7GZuW/vTuoSXvVuTwRlnbTD1uZecK0XJ0mPEHw7wAVO6u355FhwiguKm2'
                '/mdRT7eOrLlUiIraOLRKxp6wkIs68sPbFVyfdqHwOyoelAflQXlQ/zFqhowBsrgH9VegdK6tVPuhM7f8ce3hM2tq3O1jayd0ZBQU'
                'Wdp9vhsJBj05kpC2Kn34Szrvb6UucIkCpcUPlTBICuaQuP2lYOoOXylYpkgsAcvguGVg13wJWNSqgTUifEOLdJzDqIO6u2C2ja0N'
                'KSzbAgq2zQlLX1hMEF/tUCD6Z8A2shrV6RBXrbR6rRmyTkNhpGfPEl/j6Z6+VqXCs1urAuGKVZer4vTgUH3Ay8oFAjqwVKEKEvCZ'
                '6GOWYJ1bmMX5aGDit+bBfgBhtBapyHBesH1FEFu7iqfTBJqHy5zo9DIgdjKmJI56ORZMtdqccQVR3ClNUJAFJp9Ibo6iAn6Awlwj'
                'XJI5AlBR1VBU2ZsAdbMU/opwjzuBC08D4Tb3I7pGLJPgkpuKKqAD1wJQOpq8T8kFX/EpXn2iHHzFG3jCuCbwFX/FMx28Bl9xNZqd'
                'wELl//4UndGB6+FJ0Ftmr+C1Sx7YXwrT9d2N3pqyYvf5e9GJtvTEqKtH1055tRI9gXO3n7Q/DrtL7PpuQG/9VPAXo8aFyAEd2vHW'
                'kkDVPkoSaGi3TYHW2pJAV+kGc6Bm/3cCzy0b0aJsvhDvLEVaTbhAA2drwJR1A/KBb9CBsho5E48dHMKa53NDm1U6Py9SBRgmLsh4'
                'tA0AC/GBHwNgVj7wLTDkXpJpV04KNFcgP8fXfFw5q5Qko0QAhfEuHszSAezGCUiySUtQROWu06F9KxUe95V5M+dxU0UGaF1JW0NQ'
                '4O0ZLMeIAWMnIOPC+dPH21vkgI7YlsKSQDWuqSRQTW4sCVRj2CTG3mG5q3SbeJzWVG7ifeyi8ygol+tUGscA4Hz+hGwO1KC3BFMc'
                'mBPUfHxgH5ERhW+4E+RrrQ2tNHxgL9k7wuQXdSr8WBPHNYFDns3xiQ+0Qza1BlEAd9E5F2IWN4csf96ZlOz6pT5pEg7N6FWzZIRP'
                'QPaSrT/aT4u49uLC2WW05Yoc8HEuOWDaS4oUMKW1IgW88aIiA0ybqhlwLLWn3ebDYqcXJIe3+qitMdjGs7gDW+TNUq776MW/XLob'
                'm2ZLibt7eteCUW3zm3vVFnqmyk4xy25VGjtIlcYWiZfGWvaq0th3VGls0QRprOUXVRr7niqNLZ4ojfU6qEpj9ehi+24zbEk9WdTM'
                'MSZYLz3k+EqQGVa3CNpqKybY0smEC7QY660Lduf8zbB6IHN6Rp41IbZsCoiDFmG99VSav/uaYXVrcqozWZkAWz6V0vrwsT562pPf'
                'vM2wOh+Z5NJRcLEVdT2E7s/Gw/rqJvX9FjOsnv4t3uDoONjKaUjeAxzrqycWIetx4thP9S02nxm2SjrrkMXD6rGm0NMQxR5yuf/k'
                'ksdKtBMe7D8Hyzlixkiemx7sn4o1j9dr7gH+3cB3hF/2fx44+ZVpe88/Sk19evvImjEtQ2RjetN29wmUDf6NHO4nGyV8sZbs4kob'
                'JL0KP5Rerq/KApPLyoY8HySAthPzBzcqmcs/MO+Lb69nrLItNWDMom4gQiDvHAqY6RXdY0NHNiSlZRIA2vhJGFtBQf01/lyBiU2X'
                '8oEFVFnt3+9A0yMALhD6+ipoYi5HC/sTgPBPC3Sef1DuqLwGXamPKP1HBSqiYhK6knmIeu9trOh6O+iR1zUz6ujBaMZ01Aam7U0M'
                '0cKTUtZ3IDPK5p1HTbPFRBaslF0T2pUL9wnIU/UtZuKmF4fpslRRsIIM8FyAHPBRYUUKeNdpczMFHtIUGibAhI9cE9G/5dx7XFji'
                'N0DnZ6k6fC3iOJq65w1M8Z635TtT1x27ct+hbUmKurRv8fBGgSaalrBm41cfvedwBn0WeePwD9MG1Q7BceGv7WV8Pe2X5nTJwajU'
                'v3jGebMjlNLiDb5RBUJz7BEMK4BWEJZtJaEVo1RJaLEnqiQ0+IwqC11CXTn8ecvSOX1DC1TuNdXpd6NDG8Mh/w5U+AnvuTZVh/qA'
                'vPBPWiBuwq50cP3BehDVzvIiTRrJNURTqZnKyeOtCCsQRIaIkP6kDupT4U3BSL0ghJK27sw4wkJ95h+78dQaf/fwkkHFAXQfsBl4'
                'td4JvseZt4i9kPTu/7LSCdbm2VdBct6pJ1BHqy3ZkDgATrtclEkoyG038yGuRjy50Z/OXs5vU5nyCdyWXs6odma0318vERJUpM8+'
                '2LsKqe881nWsDgRbkjWXMppCfqOgSSMzUve9D5HRxJnuDbzpN5B5DjLaHHJ6fADLKLcQ6D8rwtLnlG4eVBn1BX43pUPgke3PD0d6'
                'EUYRpcFpD96rJizHIoJWoCaB4AEKKNUFr0WW8kv1Urweyg3WWSo5sOATzIMZEkUftjOVf5o/XeID6ZSU3En4NVWx1Dm1XysRHFi4'
                'N5zayZpNpVSi6YL5GEtDjLajfgoegMluRkSQvtcaoQ2rLDgQvuYjz9OlcnvFcJDzQpk9Oc9CbB88WAc3z3xBJbmPXlyLbyKqPHjZ'
                'obtx6enP7hxe8X4db1mzM2h9PUBR6ywJjAyQBI7mn94lyBUXL3BAAfFn0/m4XKSok16QDwRxgd/xcSGxTISxIi47q+IZHPSd8w4S'
                'C23qFXBcwAKdgUIgt4EiJNe9Tap7s6lxmQbOh8eBktWfPpGcDonZ+UAgqc7k43KSIafWwnzgZzJeuxnTIUaSNR0q5Y7kYPWBsb4J'
                'H9hbELjKnw49JKfDTdnp8C4fVw3oQQQFiUGE/3g+rjg5HZIEtb/mqrz6QaLpUFRSSbSGjwuOhiwbtw1hkxpITIfmktPhtGA6AL+4'
                'Xnwc4IluC0oiAt5nCB8HeLcYgWgIfK0n8nHFyOmQLPB/nCNZnjiCnA62EmauLLnbjv3u0OWoJKstOebake8ndsY9K4uOO43IdVPK'
                'M56N63kxxzuAcO79aTr/bLV/a3DwQTvE5/Axl/ep9w6zI/t4AFZFD23O+r8Fk82RtoqmYdkqGcQP+UL7T10KBfnnb7cGKq/ifIzk'
                'PhoboUfQ1IM8a3UjQ5VKF2ttSsecv8ZVZQM5YyTlCPQp12g4ljrRX+Oe9Y411Zz8DXI+varCYJsI7uIBzr0lqIMBHCCHSVUp49vU'
                'iXNkZLJ1IXfQkW9Ack2Ps7GR/vaNnQsF+uejvqYrBdObZvNjmCGXxItwif3J42QrH7iDCjypuQqV5ZK+Z4WYCtOR4na2byoxnscn'
                'eX/8VBfSJ7f0cdEb/W7k4+idZGKicpUP6G9aY83unI21wddInNO2QHBA3mZfAe2uLcM/NeAKYG90f5NwUMvuehC1jvYSjqBemyku'
                'k5yeaYBzz5UEYiHyCWK/QB3Oot14Vc7oA7TPGAFTTpagUidME5z4FcDGOFdwT+DJuxTEhfaHyFeALQgs6pUCO93EHuSvFGCJyAnm'
                'dj8YN7mD4AQtGyn3aZg1aqtuMsgC63Q+sdDl+eJntcoX6J+7yZRYRq1XNE3mRLCVIVLJCduiTMbsqjnwjrMaTsnHZsCnrnxoZW6I'
                'gfcMP/xsK0XAjcBDq/4+rpmBiQYtO/kiC7s+owrKiuTtOH7Vr1djkm22lNjrR9Z81o0vAfnUG77qsEOzkhpza9/CN0rzuaC631HG'
                'nquf4Ebml35DCy2wITBZlnDe/iGdOLPkFf6QQjNFxWjR8JMJIItGir+pUTcv4HdT1YlUfrfMFqsp7YqlQst+7yKBYaXfPqciAggQ'
                'eq2ubcJnCpu+KzSJEwe8hEnYA7aXU4SVOxsZQ2YvBQvTUO4li+gBA9EzIDYaWDauOaxC5JHzzMJPH1VOKQEDBsgWSJkEgGbiGJxE'
                'YLtZDRNPUdB0GMNVX/YB0nyrAB7VgqWi1FqpnHwtO1WNtYESx9XMUJHpXWGA1e/EE4RT63cQVSv3be5NHWwXzPeV7spE681Urf8I'
                'Fgx0tN2vFAoIKTXoLKYTryVZBXYEfcTzW8YEDb0iBc3kk0pFykCdEnmFexJQTVeYD/WnTzmCRd55vcduW7+U+opmz7Vt8/3L4IDc'
                '1BgOOSwPUG7wd8ceJtqe3jg655V8RIZkM5UcbbesJYSSwl2ssAJ6eAxaxczMxKvWESHrkZvpGRGyRBSWH3HNB6zOsR0QIvWKWifU'
                '5FVdgOnjhVWQYakF6oem7p7cvWL+YN+IUi2/oA9GQ4F5wswo5C8LvU/E5oihD8i8AkLoFZCBQATdDLMR8qFPXqWGmweNHs9YB3L2'
                'WHyTtUhv78tRNWVrNPSbDcdvP0mwpj29d2TVx41ZHBmns/9f80P5Z7V/7yD+b3X8i9u/Z5BJSXs3zdO2oAIZl1C2sgcZAqoXcf60'
                'pcwsKxRYr/GR8/jaQ1UADkyhJAld2/kkgjq3u1EOuj9qv7NrDFp0biobTq/n+HxVpy+UhRb86AJa6AhpWQbss3PKIjHCbus1yfwi'
                'SpSRc+ZjYckl0pVhDODIROjw1w/QLC8P7dtuXYoqU/wpg1X7FneGRExYxcbiKpLHcxrQGQKyDfoV14ssbU7bifw7bkhFFbFrmIhi'
                'S925qE9J6uaewfTDlpyAal6suwcwXEGOd46gGs5f32UKUwZ02YTqnn7/oKBpgh6XFDi2pFl8hW5inVRZIhrDqfiYWUsudsOxIBc0'
                'EqfQJ9DWL/zMZju49+0pVd1AZzCIn5ZzA+1o58YU56Hx8T4xvAAOD+i6GTOT2Q+9k4tj/Hv3KD6lBmbDCUp+ehMjSNvSKxT3Vao3'
                'LxZVy6/vgrtK+HfaiE7H+JVt8O+W/a3D6LqMWdQEl72Kj7uGu/J8Ww/PelZ7Nq5H42Vc82u/XnqvymxZ3zhol0dn7LEfX3YD7Wg1'
                'vnniBtqx3bb5IVkenXHuDNxvl0dneCiPuugGOsOSPmORp/yh+jeXVvS0v7J55uB/F93jxw5+bn2dmDl13PuW18eXcO/L//Z2Drfm'
                'SdpPnf3dmlWx8+tb3JqDtyaWcm/GHhvM80rqgn6G9C3dcFag6Cg8ACluUUP8Fcp+iqu673xRliODTb2DEpwciifXtNSdhSrIrdt6'
                '4p5+3k0WoexP/NLGOMPq13ZVAmpU/bIC/gpB3TakoO4UwzlRr2Gvbsd4RNtU3jfO8eYvNrfOhrxDj7p3klAf2vzcaXpPGp3zLSBj'
                'itBZB+yySj53aK/NaZJjEth5HeYWZvsK+fhtVqKOPKdH5JWdWPenMN7ZlvqzUeN+/LImzBysMQ016li3v8LM70pf4H4Avw9j1k7p'
                'sRfxdTmJkZSKfHgKX/OLEQmPs59s7R4ou1cdfy+n9D74WWnZffDpggaye2zapi4Bsvv3kXekz4YbE6TPnZi5dWXPNDTY3qx5vzhg'
                '6tZzd+OsKXE3j676uBklJ5Z5fwudpzV1WxfdRarC+PP44X1N8/EPERzwa4PNEOrxMDOEut1ihlDfNEU88jdDOKzVLkTatuH18/gH'
                'FGj3vZ3K0udEnBtkKHzqAw3BlUzEH9BlpC1YHd4hauRAL7yyq7NlCV6ZXRjiqqJBCQCBzhNyad9XzJKto9vpBrOoDOBql4gE07QB'
                'p99kZJaDnf0WYyCzjAVfJa06o8KA4Wd2JvNk1gOqOEd9Dug8bXuTEbchII5JxO4F43qvlBbHZqiHs5u49R9EDIrAs/AWFrgEKnkN'
                'UMzS9IZjCHKwnqJbzCG51BP/imb+Lh7EPxPBHHzV3v1m+6UH8db4B1eOLB/TpbAbsyB8wFYm7cS1OW19pYgb/JiCnzCRX5Y0Je5w'
                'THBE2VcXExJX2m9yxqV9G84l9ptiNZfZb7/E82U5oco022RU7moMeJDkfV/0qlko1Ncve6G6A6YcBY+1DhG3exLWntQNnShElq7b'
                'CPlpfxamqrVxnDweiqrd888wJIj91MnaTn+6hE9DeUObz0imsxJwpjX0G+/JK/qwre5hkWpZXelJrB+bVDDO5ZIIbQ0UpnxJagfT'
                'WRnowt7W5RCXa3diU4kl4edyBPxM6wjRnLjt7aSWVIhmCk7RRukLLKo3qMfSU7Hp8VdWdWbWaWHNyDfNubqfsRxO0DiDkbvaXOf6'
                'rUAGeBZMRNQkEPa5KsCkYX+fIlc0a2DfDLOvpsF4n7Ay0WEer1DkLfTqu67olwfGJH+BicCIHQ7JLU5JMTlIr8050nhvRDS8QVWf'
                '1aqVvKT4OsXjhCw4g0EJrQqsqjrC5cO31lgXOqsXM6ZiSEj5kZEIeYhN80v4iC7uo/vkHdU8CMJ3IaVzb2jhjs4pbNc3QIvLJHMz'
                'C+tcbaXYn/NaBourChNm0QoJ/rdS+ddvejm3qHUKXZzpKrkf7GHInQ99Lx8d2LUQqzY6hCHf5/wbZZz9Q5ml3xsLMbFSScX+qEbH'
                'hLhYwqaYp7RO7u3UpG2uB706jFxlQJmbmyYvr/klvgiS4hF/HYQllKDJtYQsfcvQDsUbVfqGjlaPJtec30sV4I38TIyZt8IYtauK'
                'TzplqnTVmL5hQYKbNXL/q/pm6fzfKXaGtebOOotW0zwtv8sV16ZPcN2Px5jz/scBuc8souaZlk64jcKUCjuirbjQrWDFlXX5aMRG'
                'GB4+i41tWD8sYz6pFBpUehgRymMt1GuT3ah8lrHwnWMXF8BJAqiKcgc52k562oYhGrMHTM88C9jzLxtHay3GqyRxFM2hjdH/WDIz'
                'zdrSfOEblJbr+ssKnV0gkmDYat2hgk0A+ZMPSbVbMStbiTp0kqHevN2e1INZ9/UNwrUJYJWE9Pnu7FNr4rU1PfxdA5R07edJHbKw'
                '5mXtSEuqyT3TQ4sXzsPNfOga15iKzyXF+bm2mCc1n4u+uIsfTeosBmbdhAY9ddZn8jxBCgKl/nX1rJ84ccONjjzi3PPsIDKIbJ8S'
                'ioM2mC600BTnB7JWV8xq8lwZS1lvwntt0RnqC7j2tB9Q8txe9V6rMjkCvYJzV+859XAaE/XAtnp3ZNZ5Kre4YNZ15tSnqgi+TBuT'
                '0L34D3zEE3CYIDojeVqEuQfIqxxB8M6YXJJzeMwx2tB0f3ZjbzdWQXDjDxfuv/440Zb4+PzmGX2Ky1PSiaXshd3XvqhawLrMqzKj'
                'dN0iQ/cpO7z1JcgsSFrIxRJ0L2MTKdicbjk2D3qbC02oJXOPKV1/XPdQ0IzuF3zCjjEhK8oJu7pqQjeet7zE9hQLyQScTaGqvPIb'
                'CNF7j4xJjhMmRSULr9vydJcsiaQEx4NvFpQgl8kHpmYYCK0CtvxyCVXSHKrkduR9RnHJCpMfb3PGxkeaRS9z6T5R6XKti6UCvK7B'
                'FMIZwjMvphYctKzfoDfpSfA0QCLrdHtE5O2OOwWQysOn/kgE/3bFNJ+Oa0exkGehDa3gtQdN3zSFyhHCtAKkX0GkN1ok94JiUodg'
                'ltEPvD+Q3K5XODF0E7i5GBUmTcFtYmMvA/xN/YW5sydz0xHRycoC47jF/j4ir/xMayFVrFgmW53YStWU2ynrLzUCKiVtsnTnFO47'
                'iBtILHFJnm4WL27TpEX7cZKrmTUjO0xArDt0m3W67u6Qqek6C7bdLTpd6ZfX6h7dGbrOE/9EBtNQ1XhcUDR0N67ifcZGg1aX4TjA'
                'xv0kU/U6W4bDAQdqZtYd/xgm/ZIp9/UT44fyklR6vbQIqjbiLS7HWEqFiZFyg483gX+mAjesU1TKYAE3DbMpV0aztFqT4+6c3rlw'
                'VJv8Qsab5qlm1ZPGZrBHPeWxjhKL+eWxamQFeaz6KK881skdSWIzo99ksT8zWO0bWsIqDKa2R2s4B5spHFIpDVoLsIoXdFYYKcLC'
                'nOkZlYEF2IA0KvuoAKs8oFJTSmPnCrH+aVQyLwG2Mf3h+FgLYIjigwRYn1lM3h4cG1rubegKlVJIfu4Mkp+Tk6XXRcIbsustZV4h'
                '6XVs3dbD2411fKGZG+vYPsHixnqb7gY2Iz8d/t18s1fuR0VlPc0lmmcVoG/P18K5ng0Y/mICRFgqoX4LIdYPeKKOE2IVkNRtrRgL'
                'lsYeMRbkGjouxAYAK+QhIbYHrJwswuaEZWS/EmBfoDwVu3HmQ7bK/bdS7Fd6Dul55ghGlsbaq8pjZ8nP9UP+0th9YbJrKG2ij+Q6'
                'tq4sLbc/pB18P48J/+Ao4nvnj59nD2kQYqLsiWg2avGuiw/j0qwJD09vm/HGC1z1q6X+lAvM33m2pjtmasg2gqfmTd3UkFbIjI4T'
                'vezJHuQTNTfNzWMoqfznmo+5js4hU6bRhc57VZVH57igyqN9D6tuoKexFy5P61Ipu79PWKF6A2afB2hWSboO2igKjryoo33oh77O'
                '6m8trQ5p6HdpVSie673D1Qy0N6Xk3cPzEw/4ogbliul4jKzC2QyTUtnFOufwNKmoV3RvVcuL0ZD5OWyyCE+gsixvHUJjZwUxOh/M'
                'cGpipYCV5f8weez2HJlfZgCXmqAHqJJpnhH0HBN0T7eeBL7lJhN0HVU2k3umrsmtr+OV6s4UhMwLkVQXb9Dh6Fe3hlAtZ2LMhStt'
                'tcnNt8FVXE+MpnaIa+IdAqZgF+0+n2coWgdTO9tu3M2z3ZXMfdCX9vm6hjx7i4OuHbkxw9f8UA3uyB9cIHb76exuf+mrzhWy+nmH'
                'FKzb/9uz1EnymzsniRLhzinl2FauuYNWIn51B634z3cH7fAKuu8OWgn+WMxx9KR4oOwjeW+btuVllFOayjr/JazvxXcRztli9NI9'
                'lyOfpac+vnri5y97VfDl8Hf29NT4J3cvHt2+YtrQThUDZUzEkMc8t7BnmFsUmXb1dW0t7lFk6Li6eblJ4TgoS7tLoaYMc5fCYQHy'
                'dZdC3R3oLoX6s5+7FI5AKAXXk/iEFqjRe8pxGyqfizQ2eT5gqlImF1fEeib/EbTn61YTCofJiGaJm5hRKDnOM/pFEwqlAJWwpIIp'
                'hdIZUnxmTkHZ269IULSGf6SgOYXXIxmZWlCpd6oEBYRskKCoBhlACYpcAPJAgsILQOIkKBTA8qbLUABWKU2CwhtqsiQo8gDIfQmK'
                'GvCckaCAtRLWS1BAn5YvzSm8YVKxLuYU1JLKb0phgXHzl8xXVB/4JyaaUhSLozlSE4o81Jm+02z3qXjLvR0ucHSKW7tovo8eyO7U'
                '3sH5q/eaetIudRq4f+II2za/v/rkXOjm6Zz0npscwC8l3OMyTnawuMPJJKxu7gZ/lXZ6TucgM47MlpYYncH1fTd1SIdyfm5zffrk'
                '8aD+elRxKddND+qvQOFqfQ/qv4HyzML/x2vI4SriQf1tKM9Z6zm3Pee2B+U5tz0oD+ofgcKa3wv9p6074qhBY0tLeHL58A+TX68p'
                'DEIrNmQHktDGdmJSY9wo6dtzL7+SVvK2roxiwPtVk5KG6pOpMIHWC6ckDs5rpDJ3bLrqHknIT3JqHYMk6++qmyRhx1Q3Sbyko0V0'
                'EiTIMXXX2LYVsgd6BeWo0GLYkks0SR3m811+i7LG5X51UzJB4k1/j/i3MQet8HdO6yRvUBQXuVO4+X4niRelCj2VTTBpm65hPS7V'
                'B3nNV8dmVZWsfu5qWaC/wwaJJUg5A1SSIIFlR3+TWejQX2e4BIV7TjvP4bmDuO+cknmVdiIfntbY9D8hdOTBSYTePDIkc2RIeqqC'
                'MBecBDr3/CRDAj18TsqQQDefBC8JEsrXp7QECeXw8w76vUMgCfT62StDAkfZXlyChPL/WSxBQjkBWatJkFCL/0KoOQntDrTd35RE'
                'wieIIWEcg241MSNhvYPU7c3AzAllSDAXoUeLX6+dP9jLN7RInTcWR7Iksn5CBImssxBJIukxBEjk3IYgiZTvUGY77pYDUcYW/G1R'
                'N7yIMibg+0zyUb4rkaPdnFqD43k9Fcsz/WjjYKHfne5UZEuKvXV86+xhrfO5x+cCX+vvPXgP3oP/p+JNmwf/r8Z75r8H78F78Fy8'
                '56fn5//sTymxxnPFc8VzxXPln3qFLEHxHrhCVkUeq/IKFq0CelkyVf9NYKtR2OzcumuA3naoMFeH3j6AYoqefDxwCryQlpm72D9v'
                'o88eUZLNT9yiUi/zruzjFbNKqcC7MohXImsyp7yWbRSn8JaePJq68uCDAEx7+2x9F3+o102Lf3h6x7dvV/dxy86clbJhHs9qSpOd'
                'MpQezmL6d3KehSQHQkyfLQ+ljNwTZPo+BajosO0BpmNQmDJdb/Y3HbfiVHLj9b6mY12aUvx+72P6fcpT83m5t+k3rfwEkiz0Mp0H'
                'L8ZAktkW07lTi6qpPsPcr6E+VZbxS3NfiJcT6dAcU5rmVJ3Ij819LtpSGeE/MPfT6EQVrhxi7tvRA/ou2N8y9wf5FIZg2ga67d1m'
                '7eO2R1x6d7e96NK46c25NCltFHdpkgVWfB6NKL8yj+Z6Qfdp1JuF3adRbxdzn0a9W+I5vBwflH4Oz8hHZSVoKJum+riCOc2LtMdM'
                'VGXz9ZOFth1GVzFfp6EHKaLY6ub7QTBdgCuulvm+E7SbInpW13x/C9xBESU0MN9H/bdSRImNzM96P9oRKqmpOX/gu55etS3MeQqf'
                'NRRRahtzPsR7Bb2ltDfnXbyW0ltXZ3N+x2shb78T8AcWOruT9RVzvsryDc309ZXgxWirun2gBP/2JU30pgTP9xm93t+RsNOOo4mG'
                'SNh2R9NEIzy+nR6UB+VBeVAelOKJIPz3olI4RZDeZGgHytaUOS9Beh8t4ttElSDFq31sliLFcisWs0mRwjoMzjZDlSNdzlCGxkmS'
                'pjJ1pt5VJUnVT2jXwCvSpA+o79NSlSYlSoMiymEx6RFAWdruBqkKBMPZqjukK8joiAQJUiPxampug/R9vTfmApd0+B2idKAu1Bj6'
                'yy9PcEmHGFVDHvqxGSethQSk2Y0sXb0UptrQekVAqhgS11GFKruqqg2EpASwJqzcmRlyICIlHm+VU2FtvEJ/E1JjUNLywHIrTwJM'
                'SL1ugqISPneIbGAmpERtiUeO79PVEFHzmZIS064PWYHte8WUVJlDuClXMa7VliAtYyyxWssob2cTUqJkzq4USmFnRtoKO5v8pEgt'
                'SDrlcYoUKeOMbyxfU9JQphL9d4okqTKTJq0mTVrCzjnAzEmVrZxjU4K0KaC85+MGqeUCVUxCnlQZRGqLI9wiDY5FQ0ZkSJWpKlZo'
                'Soq0sM48/KK4SapsUJnCSbKk5oFmHlIPqYjUwaOwuY8rC32QJ7mJT8rnHl6d7ybeWso9PFH4XQ6vVncTv9dNPKyeLoH/3eIeXu3h'
                'Jv6ar3t49S038Y+C3cOTUqYUPi6HDJ4we02TwX9k2P5TCkrgh7yuslGvIrzPZcPOUF4CTybW3CSDV44xZR/F+EYq7ewjxpOSXhsZ'
                'fBWDuTnrJYEny6j2kcEXM6z8t/wl8GSE6xAZfC6Da38SJoEn0wBMkMGHGc4gCbkk8ETNckcxGwm8v7EQ0opJ4MnStqtk8F6Gz5C9'
                'rwReacOxTfPwyiGZmJghvKoL5nhlk5v48jb38MpSN/EFU9zDY7VfhPjsce7hYTFaCXzwQ/fwyltu4n2vuYdna4+a4C0n3cNTMpU5'
                'XqEcErCSM/k7TFx16OaTRFty9N1j677qVcq84LqlwXQ2z8uTJR38REQhgy9zNMqRE/PwiLwHPhSoohPH49Wmih8x0WHfaYBQdY83'
                '1X3bxjODM9wuozRfRulCx6pybQPIwvG6KtvI9BW13ShR+6ZOFcZ84eg5nUuHegcXafXlTeZDlMaTmzh8bYYYvqmWLjfY3GCZrRSV'
                '0+cEdL8KXUvRab5mlJfJb3T+Ba8lEHAx8+vlg3/sYU5mJvj+inDYE2AfVvK9fDpbuucy41fMtq8AJi2MrlTLyV2TB37YrrQX9wNO'
                'CpftdHKMlaDjK0WmBM85qgq4ynPmywtXULAvPNm4lewjYfnjInCz4W4z0FTQvr5kXSw4b9/tAH5uU6QqEavj4BCt4ZJBn/bJMPXM'
                'Ai4ZNKjNHCiWfPUGEzR984pkFTLqIWWHZCIckgaqXJkn+AEGFwU/H3PJ4FxuT02ufDwy6FJdVblKl/FVzAsw2EJgBIQ6lUMG2YLz'
                'ijJEapn+TGcXKgM3haYoVS4ro7GF63QPSjaFjaX41NxkWi6NzeaUHz7AgxwMlc9BtnSzolB7/K/00W6hnPYuO4/i0tTRcQxuKCHf'
                'U0dHZ7T8mEOV9S5xUHW6zjP6ZqGLMqhR33YsGewVWLjFJObETDKcZ+u5cQi/LeRZeQ1uGxMkqTZRk+8jKaqVDKfXK9GUyP45wlmW'
                'PG5Cda8Rzhi++UhAlPRZKJcNHXKFQ/T4C2FSOUvDrxm+R41a1tHflF1WCnb6/PvDt6OTbCmx9078OK1PGS9pjxZr4pML+xYMrevv'
                'hvdL8uZeAW54yjweHeiGV82dZm544Ng/daeuxlx3qnaMcQNrq+1GNRCHGkk+c0YXXh35op3m0+LEboFvUwTlZW2LEHkiU47SHUU+'
                'U6GQj/pM6F812Y2MIC0gYyvEVoRbtBALFELqUSEWupTsFWLhCbdahM3yRHrMvFbDb9GBj825kfrGOTj16Yt0WpBgMnfcmZOCdk5+'
                'rtvqyK+hT+TX5gL5veQLiyz2XivZPSpqbLDc3pey9dVAsz3VlhR9af+i4Q0Cnje7rwfrwf6vYE00kcd/nN63vPfzaSKffv9KyPNp'
                'IuNmFn8+TWT6rIjn00TGdHk+TaRRtMxNTeTO0OfTRB4GtV9fkz6NSAGjlhtC0HiDg7nuhibSWlvheEyJNZHntccskeaeJvJ1Z/9q'
                'NzWRTneovG5rIrsg8VcSmshMn4KLbmsibQ7ZveRzaCJfpd3k5DSRDhfaFc+hibysKJeeQxNpD3s+TeSLz6eJ7PB8msjB/481kTOe'
                'TxM5oaNKF7mU0UQObwh+HpT8AK8VBz/vS2oi2/rD3TiHnCayiHKdTlAioYl8ZlF+EHrt45rIX0lv40z7iCKjiZxCy3NqFRlNZE06'
                'LwwS0sDKaXctTGirvY65JjIzFUVRuL5P+5tpIq3FsDiQ771NNJGab05lymT/UxahJtJagmO5v93TS6CJ1D2NIhh+5O5XbYtzNJFn'
                'jHdvapc+g1MqcBehSFLsYeo3gIl3r1Kj/KkMlZVNh9E/yVw+rIvMoDInTai24mvY500RY3iuLXfDCH73PG8sXvcScr21v7yI0i02'
                '5Zdzt/p4+b4rj+Ph0hwtz6OTq9PeXZrMQuq3UupI0wWShZyfFJOmy0Wq6S9nk6YrR6a0+cVPmq5JOuLVL9FeQ0IQZNpk2QQn1GdY'
                'R5ClNpD/DKQYE1OKqwOxp8TfP7trwQdNs7kZsWk7PrqQmxGetjWl3YwITR1lcTOCdJW3m5WeZ7uJN3hVSfxlb/fw+h+Qxa8SyPIB'
                'EdVe30EdHw/MZP96jyFBLjNdQU07wzeIdQtbMAlFgIfRj+1N8S0xlkyAr0cZl83woLqKPaspfih55Yq57mUXeWWeKf4lcKWGGb5R'
                'tIql9EOz1uSo/ib0SEuv6N78H+ze+hrr1np/1sWd/cS6KJ8b+8/dz4q5tb89ml3czf3QOtHHzf3w5yA3I+o3e7u5f34h0g0G5Gk8'
                'JZLa018y0SWGzqO2Qz8z3SOV4Wakqa4SWuJis5rhc0SiES789QV1Z4mm+6HXWSzLnmC9Q5VBSn5T3ewJpFqWCA83xLQiprrfwypT'
                'KEuIfxnO7JKmuuV90Lhniq8Lp115U901lO5/NMVXU6lDwEw3DnNz/WyKrwRPydqmuvcfuFFGPtXfm7f3YlSSLTX2/tXjP349oltF'
                'jPO1NFvxjF3iaWdXjagJddEdzvN3hMQ9Y3XdfM5tJtuH6y0qPFDlkOViVDlk+A1VErlIlUSWt8sil6iSyEA43nErBtbNH+bjG1as'
                'bv+pvySQSJD1wvY5VD/7NJx2RUd+onI8jVyt1GcPncgV0NsTa75d92Yca/uhdkjQTopTbHKQ3wiRJHvzMEyEBBqYHeEC5ETKQ4br'
                'SEhtVQ7+7fiX7XA/ogBMMfFw64R2rOJ5NldzsXYQ5CMKpgnm0NmPSevFJ2Jxan1VY6WbVEy1L9fTQIfsNZnHD2q6oH7TTVZIslGN'
                'rM4JMfQhMWZt9ojVNuRwFR11xMaHUjX/srWdfIDj1oYo1H1eGLQM2VWiOaqc/K9vp5+kCneSFYObt9pXMHU/B8j3BUif6xxejW3A'
                'mDZdhAR5/j7vNqeo3D2H91Wt6xpxTK8ghqtLZgTY5TFFEORU8O7lXLFiJ8bVgKmw80HH3adeRFRZ4t7pAxqWzOrvFZynzpsbqLTA'
                'q5W+0nK3JPKilyyynSKJzMhFI4X8LVASuSfzRMn5gZm3Zto4XUQoPPww39ybvhpyKCFNP92fjGw0Rz7E9lLfUq2Hzt5x4vL9OFt6'
                '4uML+xd/2Axs5itU99puD8G/lICZGi+qmLO3oHkIPAQeAg+Bh8BD4CH49xKY6b/WgQw1HrQH7UF70B70X4eGeoXSYovHxR6qOFEy'
                'UPL90Q6gWUcW4HZ/uLYqDmQGMb0bC6lCp5wgoMX81jdVlB2OsgONUE4BhT5tZhmvwgBvaHygXMkswMxij6C8O09Dt8U+4OIfDu2m'
                'lZ+ZrxS0aX7O2KfUuYbCpSUViVuaCQ50aEG/bl0k1C931WF0oqX9mbc4KinvO83D9eQ8GDdxqqmgLcqVgsZ/nzk4tbH+8mGmj55G'
                'ehUErReDoxvCbzzgqQC8kUmbk/3zOA52P6pbDeq9lU1VfWFSGS4X5lf3nXk7z0bGp9uSY278+sO4TpR6bgS4E1/3q7wNgJVyW2Xc'
                'lx0NFIA6RSWovcolK05XauuiIj5GirjUTbojxscfWBi/5dFdo+pPUiadKF+OYyd4qg4ZXdVpFTDWsJtfEO5Lzq8JXHdmOjtHAucB'
                '1EjWHjNb5AWf8DWMDpwPZ1DT+gGELDwFtWiA7c5emKUD6ZLS9ST4AbGquADBASanhbPNo6JOqFYYbEtEQt5aqiAfKJX3LJo8EkBY'
                'C2MEBVdnKbwkDo99RCcSOGjz2wRZUGaqfHvwTr5tzCcSHoAKN5AnGfjLg/TeVmqnCwTb3ACujfdneswWsGeP5liURKVSgg3k+7MT'
                'rqr9gLMQG2EAkk2MMvr38rJ1YZPiAucL1WDpCtoR30NqUaNhHnvQSp5nUd8psvUmEZE+SAy/DTWeBwHfhpYKG362Hd/rFtGePg4D'
                '4QPT2h6O0qMkJimUSaf3NIDjMw328n4ZXd+piEMl0z6hs+4Eg7O2Fo8O7CM2h6G7l3jfwZ2gRlIBaKP4dK/ClQ3OYlsBPl0wCFN9'
                'YRj5a5dIlwMiXqb9oZoEM+KeqWD+xAWK6Cw3VamkOUwbz6OrK6YryuFQr5ppuX5RzfIX460/7qdRyIwuBK1UssdcHbdcdbPSKsdd'
                'JqPFB5vTWW6rzxHuoqBhRPVl6IozZNctMnRsKtmxUmSMQ60dc3DYK3wPSzQ3bTezm9uyjBOGAJVT8bgGrWW1Az4cfNYdijBa9Cx9'
                'uS1kc4JIl6ZndPAdzFVozyaKHuxKKQKqUuA7qjBuGNDmocIQh0JsIVVY2Bq80zWYoTjTnZRsvWgvDcESWkJ/CyoeeR4tjQbxN7j+'
                'GT1nyB4oCF6gZ3ZD/tzMDG6cpbKR8s6Wwy4sNOVLul09yuzqxiu2REkjzOEDuO+1ChM9e1vhxr9ntAQfXgzkYETUI/3t9FzpMaiD'
                'GYgyfcHZt4Ts60WctHp4mfHBhhHrPgZZMf04TEpjwz9Kz3q4QcFTNW3HNsOLyPSJtuhs2RNjm3wH3WEAsxbBTp+fCI8kYwKuQXe+'
                'NYy8DKfPcKUoMgHJJ0gNQFUSuo9bTZLbvqvSIX7F0eAXOIonGO1IokNE113QbqGyxBf417WG0gnF94CiNy52bTHCXTOzrhl9bIwD'
                'G39PRJlhC+coeyY6+8qrZJyU5Qkl4uSh1DcKO8yGEkB/q/RgUOtGEz678aRjsHuk+MNjw1l+bBh1gMziSn97WLbvDkz4+SJ1gJwm'
                'KfJytUmj4LHh1Ox4PwMHSDgp7l0Hu20jlU4LoR8b9uxUAorfmCizpfzTKc6bPDbOK5RbZ+YB8iVX/KY0dFXIY2OuQsfHNaTxJRV+'
                'Tev3yGPDJSf4pxAHSCD5HpHUaQ7efz15bBRkFD+7qPGl1Wfgu0QSx8Zt1oPccYCMpV4DNjBfShnHxgok7Xs1mNGd8RgG8/g149h4'
                'w+D49b5hPgkiRouoPedoy41jw0hqqujuoBtqiCV3sO5v6cdGlAU5ep98YBKbDpL16qmcNhKIduxlDuO/GBWcSK/p7Kgsl4poC/qp'
                'pjUlz2EILClyMQwIeBE8SGASJlrcN3Wd7I7dq5ViFkOBSjh5EYQt3NwI4GyUneI6iziNik8VEMsL5HWxuJtZuLAZY1JVFBW4u+Fy'
                'HVv5Y4qpqKlyMtGOYIBtTb/1dY68WYPRFmQz/dZLOffyodUI58y/9QCeILxbUMuA861L8u41VhXWlWVkZubYmCX8cs72AojBiXZI'
                'ikFg27HVQ4j8z7KTpwYwodxAkth9qbLaTypYiVVp1QVK4/taRKvv7yqHR3SKHNfxvF/lgDHmYXZINZenNYCJhn4ARM2hjozQBnn9'
                'wv16WcFEtwJtahGgG4whFtMqxq7N1cAYhxi0FZ7yE5aNHqT15o7iZtJxXgc5ZhOKY/cawU6ATvDkyAwugkm7DmIBR9Cx/sMMzhOM'
                'UTxqqg2/C468iooFGsdfwxddE3BinvYD+QrULby1CpfaShAOEpWbRxV0WRVkwuW2GlZR8IwiFxdotLuiYEJ6qekbbhOxRrAcVqKJ'
                'c2QpvKWmsUFBZlRerOrZWsNca1mECQn+VEbZOZciSskiQcSOxzfmRL5sWid74+fRGqt3zZ6xOjqnlouJAi/hM6qjIh2PR2r/cgmI'
                'GnH9Zn7iE4Xd5q+vfnIWHnU5MK7G8awSUJF3yvcdmLASV79HAPtyagXFslM1r2/6o0obNvMDr4BkzAUGulD96s2mojzuwxAVAB48'
                'icWxykWMhcCyG62PmQ2oztJpdTbMa7NTwTO1X4CSS0kQ4RpLxNXOUdG8c5lqCpjWthfJNwDpzP4St8DbevAYMDXsLSOAvTJgriIj'
                'RFkvF3GYq3bi/bgNylwtMdl/HuVAmKs7yB7xvsqoEiBzZceyPHrtZ4YY6vJnohO7UBz1OZtLnQPQV3On5VWVW6CVaDARp6MaJczE'
                '9Ay1HYfDdHln/JR8seYMAvSETK/Cits9kA0PIiYiySwfZ2cYCsj4nnWye/mfooXbFTzy2OpyqxkgzJ77opXDjsLEGLeBIOB7Gkpa'
                'hs9J/jj+4QjXnrUal+211TaulE5R+RHiML3tBf0xLIc4F5zbYRw1ZVDx0Fpd5MqlpmncdAHIfExmJgA8Co56ITXtL7KKnILwtkPZ'
                'fd5a0zS5baLDfJvjicgmiIq7u2gL5yXcLaUQTBHeD6bksfGcSwYBWMwdqfpVikWQYeEy3/OicLyoIIsi5xrKO4KYZ+QkorgSKOZf'
                'E3jFLoTtHYxquqkTw37EJcSUM1eKMkko7PUk2OXBNNXXMpy5hZIDrgXJUCnFwDPapVwsFCp13yXFQ+Wh8lB5qP4+qgRVvpX3oP+b'
                '6DNBbqAfC10fC8CQpVThcR/8hyqdfEmx/KhK8Hyc5JSbhWm/e1LJvUJF4Bowm86TwiJwfiiSpQq5iyBKmdlfOuG0iMVUkKKVW4XD'
                '0Y2yOAkzv1WDudeiiorA+aANLU2YJzuQylQ2UDgca9zgaOk6L9uE5ZC6QOXeBeFwVIUcZZQwsXqee3A4XhKBA46pKtfrj2lU2ZwZ'
                'QvDHELxdOByd4HBcFOpuX4DDES2sXJX7LlRFNBQOxxFefXXF1ErD0fC42igI3ikcjg5wOC4JzRWV4DYbU0IEzgX1w+kvi8D+h6X0'
                'SorAx5zTUkao7qAPedD/VfQptNvnX9VN7Aqebk+3p9vT/R91/5v2Qc1IHYlw5JNUbkhcTT7Xb7lvxMLQzWV4rMBeaqZyMwT4ahaa'
                '35E7utx+EKGwK88t1xETnMIvlahZkazZFW5NH0ROzGVjfVVdTav0mBTE9+jooHDD1DAvA83ZNNqH78eCZIWoKvCt0OwFdxR+1bwX'
                '+TF/E9lLPtH8/OLLyVAi3PCIOEgFJfELLGo5TOy5+b67iLySw8qvvagp9FMRaWuIyg1HLqzyKx5qC/CZH9+ZsQXCsqv8YGQtKfUj'
                'ZO26arPV5odLIy6P3o/50awuf+py7KU2/GDWgAQqUkZh63EU4Meev8teyprOD2XVLG7p2fh2nT6IksTOxEoplB98YiA/HzaSuaOc'
                'wKtWyxsQ5c33AW3Izx+CWHosD5FwNwUGCSIJyFvQhlqj+T3jxHMqhudwsfzoebL9H9+toKVCPN2ebk+3p9v97n//PshETF3JZW5x'
                'I9yi/jB18QUazYNivw0qp4C61VdoK6BLbawSmBaasyVVuHm+lDpYgZCJHHDFWHSQh+IeFZyysnbM/pSXrDyycQSRk9DangFnI6LQ'
                '0hxh5NVuEpo6WiIIITTYtzIdwsM3EC5+sGSKH1GLZ5OLvRpijGcU6VbrbdiG0ocbzr3Vjae5S8hrRs3lO8C5iXiaKznZMJktNJM3'
                'VH+a37NQ2bLSR7IuxsbTHAgEjmh3UZth1o36H3ZIXV1d0+7n7JwZoT/NSksz7aNZP+LnGdGfZpb6P9zqxWOxGvUSMCOL3ptCMrf1'
                'Xb03wrFeIJ43SNBzCZC92rpPr4v13gNuyi9pvbu8sN5x4As3dPbammC9j2EmrUbO3kMZ8r1XRPnGrwybvHTb4TM3nzxLSrOnJzy5'
                'eGDZ6FbZzYNDNNnro7xSOMeesTSfFM4R1tRPDmfYyc1w6keSOGttOZx6wmLg7q37rE+NknlCvYOyV2j3xSkkHNaBOzicVky9dIXJ'
                'GDhoHqK9UrKQwUopAs+6JgKvYbJ5RUuW8f4dKfGrmGQvInIxRrQcuWjX2XvPUrDqWa6UZKXGnxFmZnWqjSptNUvf+jjjcJhoNf1y'
                'UQ790TqJ/SLK0E6Z4Bqqcjhoxnw6v2PJLN7s+EWVB7AfsnMqYkaBgPetFl6SxyjwskDDYiHd06NIh5V7qJ7IiSPOffUkP2426jYv'
                'hVkwCHKMIkOt7DkVnvd+1M+ciPUh1DiDKCybi+8JnEp/j5oUL9ghn1945dFM4FKU1w3J79uDd+nUSYCzHMRhMcUPwfkXcQ2DxddU'
                'KJxSHAE+qqkwOCVsLQ3bkV9BcI7sEcAz+khHdp66xr/MO+vOPkhNjT6z9v2yZs5xK8TsuQfqgf73oOU/2nglNj3x3t4pL3sLoR1J'
                '96Q7w/250AI7qNV1sz4HWjeSWbC2YSi0IVYA1KVZBdAqHEfHdxjodl54ZnpNeXfW6wHynq9jMei+ASVDQksO2Ad7n4Uz0Gd6lFb3'
                'eDokHUJJQbRJKsVuQOjHfJfKFyD0PlAqhDyBQaAJglQPc2FJ0QRB9nDAu90DUCuVIDgbeFiQjPMCPe9B7GepBFG6TuChWY+EbhQm'
                'HG2WwCaXUPCgtDbPeVc3ntWNEXBjXOmkyYKvRTvvzhHMgXsgTCtYNLMgnz5BNF/VZML3tFGKcBWocXresi7PxGvL0fb2KxESUqLf'
                'HtMV69Y+ILe77ODuWbWYnbBqouxOuEJphO6vn+K79mN2136fcxYU3EmfBQ34J0wnskTq3REBwrOswqifrj61Jt3fP7UJ333Tr97g'
                'RXsuRiVaU6LvHFs7pXdpSj8U0GMz8yHiNr5myOjh4zhl0XXni37RvI+nQbJs5n9fJ6TAJdUEku+aagLxF5eXvcYkCcEg1WkR9dKU'
                'FiWy+uYo0XTM5mQnhA5x60qMaFj/Iw4IlRyJqRXeei2hkMyUlREnCx8gHT3Jg/mlq6qZAA/C+JJQx90F4pqoClUknVNf46x5EvUb'
                'sDyNYpZrrObz3kXiWXZxWQB8XPCM5O+Zjy6swIHmUfeJNv3SEvNFoeTY7fTj1F/NzN2rnYm569fx54zpXYNeARcnNyuWxSdbsQbD'
                'Vkdr6+hb03WkBJwwhSj5r5tCJHYGx/6yxRTiCKaPMYUoWSfEmkEcGoSeW5hj5dmm16k6BX71hyzedzk6yZYac/f42il9yniZGbBK'
                'q6LCUR6oB/qnQ3MPWHkqOi350W/zu4QKoWV/IMya8TPycKF+UynN69OBHGgu5Lhe6IdB86JH/wYfFhp2Bl++y1no97zdYB4N7SnH'
                '0jqgoQ+loR9S+8c3DfP55a49+TEL9YXRhvtd+Wazr2egsK7db4aFwHsDDQWp7JILE3MiDGokxlke8wVbmMhgXFmVq2JWsgK7+Lie'
                'oqokQHsyDsg4tPXhCwBdJDprwZ8ct1mUigqkfhm3W1Q7FvBg4w6IMqCWe967uvGsboyAG+PaUxT6vEMwB6AiODxVMLOguPyWcL6S'
                'ifJDHwlXwSFDaeO1zmRt7XXlr8r2g/mK/bpBHr9cNb+I/M/2AeUVeSiV94to86V3wpXI/poPZcM2+6K7NsLWfeePnwX+06izIP5t'
                '/glTbm06wUrPKSA+t15bfSY2PSXy2KIe4eZuRPm7Td70x6Nn6WlPb+5f+EY5Pu4TetCuT0SrTxVfhZkX0+flZITvT9M5XyyOKlVU'
                '4HfBx59PivcVxJNrk+HKVPKRyaRa5eL+Qy6ZTsAP0bDKp9Oa5/XPUv69y0x+LYc7A0Auczm5+4xns1cfRbM60Qb4tiD7O6yup8B0'
                'TRlBF8tIFV9RfkG2wopvrCCBGLnAh0Ehq58gl+tmKByWE2QOf0xJd6KWfbc0tOo5aWiLm9LQTg+koa/I37WX/LP22iMPJU/DdD/h'
                'JgHy7FUUQkGdzXeFUD8yYdlRRT5+m+e1ETjybbqIz3XUPSx4yD1nrATYWE7mYD0FJ0e5wiqaQUeKXkDLUOjdg3YiAoM6IR9M61Iy'
                'u49feOmmQ5ZeoyqPhV+T+FZaXEe5J9JQpeIjaaiS/7g0VPEdkyILdah35/LBN2e1hBrcbO8cYA8E+8Vlb6EG89DmH648eD0m2ZYc'
                'dfvCge8m9G/ATcuQr8eU3RfuG0axBPJiu59plQ5xOd829rmNy2Ux1a5+OfctVXR5pSq6XNomvDxDFV4+A4uFF4YmHFB14REz519U'
                'uXkJmcKObNRcd3Epv75iFebzXl4qmpAp/7OX/9Ix91z2XPZc/lMuZ7Y8r63KUDdGHl3YXRzOUXE9KQzO5guDgd/YJEXM/IhAvBwV'
                'XIvelRWHIzj2ixUM1GuXtOg+RFohkPuZNHQ6dYrOapjXL3edKVEsNAzaNg64gigiNjJQmFb3V6Pyhs9GGgps4Imk+iYLpb4JTOaX'
                'A4B/cBysdw8LnoaC1xgH1EknqdkGlKPjvhKVQwFZpMZ9L6rMBfLRj9vOy3jOFJcet19UoacyH0oXIK3IfwC6kA2QqseBvFpvU1Cg'
                'XRs3VVRbAmSNHgdCrg4KPwEQstMh+xYCP2xAEuvXoVCpFFyTEHC6D0leOstDCgoLNH1v2O58GE16CHRF+z4bf8Eok2HPk0l1cvnm'
                'qv0lsgyViFh5xeBb8lDLVmm7h5Ltsuz25pAOb+PKqNJIpYK8f7DIZX566giVCNRQAmZgG/zL+MIrv47VIYKSN2Rgfu7XV1E6xLGq'
                'dJnnnyXKbTlb0FOuO70iCkpcLbzpVaRQzcYKprU0nmomoQTbKkbi9PsWTdee4Ry0sxvp+WhpCWXp2JzAnSnpl89aV8znH5i3XLcZ'
                'tFrxDelEqeststDjIbLpVw9nkc3UOs9fMqnrtVaS+V+vvEE5GRZ8dRmmHrs1uz4awJf1pcEz1/928/GzdFtSzI3Dayd0K/ScTtAe'
                'nAf3n+Ice+fZ6PTkR0fn9wzl4yqtIcwkSTMjcFzgDMqYEtUawxVhDw3bABZXFrOO2BrRuBKP0VV6Iwjitl3hLOcpku6rcbJZh/tI'
                '4naxuJODy2YJKT8W8gvPLBQufbDGxOSH1W1KQpzNcJcrCjjxHgncagDfkReGA1xUGK/ExacJ3OICgBudyXeWL0leWUri0vy55WNX'
                'kLgz0DzNxUHvvyAuDlYl8ufi4Hrzk8T5eHAe3L8b9/f/UP7TlvAPfjnPj//O3Pnf6/3vNs+oe3o9vX9er1FwkPTCna+7B6uYH2Yu'
                'TB8HnV9eR/20XFmdLGS6g2RfNE9XpqtKkW47qToHA1nJJyYY6/1MQXpPByC9iRkaL7o3PjMNJtX7e2mF6T0/QBOftN602PMbRr3w'
                'XJumB+vB/nuwA0C+nfhGAuzrABpVXXDfQQB6v6zgGWBBx6uFBc8Laxaezi14N1hV/tdwwTjAJFDbgwRjNhJA1/gJxhcWYJnnJfgW'
                'H/PrlNJYYMJQPxB9Y+D+b3tNNB9AVoTUrqK5Mwlsuc1E8wzYzWJrSxdTe1hRuvDazWLSRdou5ZUv6BZdSR6rPinvRqG4yDJuFJV7'
                'WEqIhTW87hcXYVcuA+C7RUXf2BtGHt0uJJo7fjAVyo2CojkZBDMiXcsnmuthJ6GFJY9oP8txAYAv5hLtfXlhpqdzEaJ9siis93Um'
                'u2hPLQPdW//IKtp/q8BqxyfCRXt1Xei3cTRMtK83TYWGsVDRGdAR6ucPBovOiz4wPdv+INHZQtXq3RMoOrM+guAdAR6NhOfH/zfF'
                'EunA333Zmej0p9fWD6USAuR+94crsdaEW3u+eMkLV7lm+skQBiHrasI5qjRplbv5uhfnBvXgHpjsYhC8P6E82H/Lj96gTxpegDuU'
                '9YR7UAK5QR87njUmDMsrcDOUuUEjLPLK1kDx2YGepd/SN9iJh1ld9v4CP4zttakb8NpcG+fCD5I34LbUHP/hDRwV9ZgbxE2pkSOg'
                '2HtIHMBP7fL75epyGvR9x9zguMYdlKD9mZI6aVYykJPiAn2D6/rhO5Ya8E6uC6XIEbUFUzcweNAX4IU1Cpq3VC0Ob/CrAfOFc6q0'
                'gucNq+qj8pzSQMDEKZ77bCN4g8IE7hgvU3gb8kJ7cIM4XpScy3NIUWifqs7gBsfIG2xSOfG9Dfk3AIngQY1bMtVxK/4N1pI3AGG8'
                'ZFRXZ/4NVvBuYFU8N/DcwHMDzw3+BTfA+ESPL5bHF8vji+XxxfLgPDgzHDw5SvX9etvZxwm21Kd3flszunkI1zpU5is69X3q7lfR'
                'CkvVcOk6ZlQwjQxbwN1X71HJD8rfFO3CX5KJ9RrEibfsdUZKg2qm0XMrXZ74EfdV6fwoWyQOjvQX2VAqh4plYcvCAdkqDKMKh/xm'
                'IaqxuhS2rqqmXkOgSNqeyeJwhPisvYFO5ReFyoKWBHTzi6joOv9n/MC8nED5/D4oXgblV/pvboGJN45Rs6QTrOyxSFRWqyD4ozn2'
                'oIEnrgZO6BfPiULulIvk1VZgMr5EY4F83vWBIHW0ouwjr/YW3xdkyOnqzvO6Mw7ujK/wu3UEFjA4H+yUvWg1nA/+8bxkQI6FSM0z'
                'OJcS8yu89K0Z0aHN4RIidqSezLqwnAfgQy47ote77Hpj1vGCFgX9s5YbQmV0OmJxd39Qcj6Q33eU6vHS+5ljn3wmvU86Mk4J99+p'
                'MLFpGD+X0T229HB1PC46dkwwdrqUnUY/Sdqefvw6SGX6zdx+/kmiLe3Z3SNrxrQMNfc79FSC8FSC8FSCUDyVIDyVIBRPJQj1H1kJ'
                'ApP1OJUgPOWePNC/BkrqnweulEvqU36tZFIf+byxuU+qkkl98t2QTeqT5Zx01ot10kl9+qiyGTrCIqWhY6RziPs9ls4h3lE+h/ga'
                '6RziXlHSOcTLy+cQf0U+h/in8rmuF/8lOcT3/N05xDfJP+tC+REYLz+uPeRziJdR5XOIR8rnEF8pn0O8rRs5xB/K5xAf6UYO8QfS'
                '+4AbFQo8OcQFOcQ9hUI80L8J6l3/85+vx6YnPzhemeHCAobf0Tsa01frkFbxJtTVV8FeSV19FTpYNgVXX6ZWHZC9GdfIZkIBrrnw'
                'agt3rx4fVT2/X5ayAzamqS3pq3eMMzD3N02oq5fyCcIqYvOJgi76i0IybnmJro4VhnNUEV1N9RNdPSXk3/cIr/7oJu/vufq/fFVv'
                'gY2GL9l36XGS1Z6a+PT+5RN7186dOKRb3aKGcsK7y2ZeOnR9vnYS1FHXQH7CrM9OkNcG1Rz0kWoOypMoARqrSoBIy+29z5sXC/EO'
                'zFWiRp/P1t80QMHEtvsjtF0U7L3ggRNUgdgEsjGfwave11uga85N7icjKl2kRsgcTwcKcEBAF5q+c3TrMv4I6iqjDbuxfebb9aBm'
                'gFOG035+XifDSPOCnTvYyWt0I8oq0UfZq4kOVPAX1ZJaOlH5hKhETd8bNElUHOCSS/2Wa6yg6EFfQiny/oZ7OOgXavjr9Jmw4gjt'
                'RJ+KemEUeRVqGutwPimQGzryZgeZOfY1HmgSSMj59QdopQJSxBjg0J7ETWHjM4HqoLFTxXLqExhDmXMvOWty6nqYyB2Te9QsnTvQ'
                'J6x0p3ngnD0hUNbobZAE6Lq/OSi9rmIKsvZUTEGPmyhmoORvtO0huN7QFRewkBf78eG5oEdQydZDp63ac+5+dKLVlhJ97deVY9uy'
                'VUFOwMFTPIC/ARBiMtEOeQBOgGfCeABII01ov2OAX8md3ezss2Fn2nI0SQ7RxgFmaF6j3P4iVynSBUd3erKbAOiqziygqxnA6zcT'
                'gFIk0gSgFD9rAlB8B98QAzK01iPX/P4w2UYC+vILY8GqE38xsNmfDmz6pwObyAIbywIbyQIbygIbyALrywLrygJrywJryQJr/n1A'
                '+IyD+MB6APih7KT4ig+EPqfADFWzt8ordeENSrDXBH6Tw0lgS7BF1HxJ5ZXk2ASBIMKX3NCh76daMyf42cPYwyirS00FSGcJrhnZ'
                '4I5KA3+C/P3cOtkCCndez+zdNWkjEK/VVArYJIHKNllgU54cMY+egd+hOFsXZqpmw5zj03sgBYEqsLX9YpqjlYOK0Bai3UU4JYa8'
                '3yKdgE50EtQi8mo4ee/tRFv8rZ8/qayYFXW4jOjoSbX3uvZC127ohN/M54GgTAqs/HjTC7geRvlSWFD/xOEBVsQucAUn3Q7S81LR'
                '3/TJu4v2xCNjD1Ngnd285NTM1J/4RmJ5ATPbCFJD71SWT+bWgjnD6s5LEK9oJ8v8VCIXnMvuSuoGPiHAU7HCsaRR+iqhYbuP1dXx'
                'j0J3adLz757hfjVNxVzpl+O+7aWxTx5MuLbaSKf5A7QHuqP1Ivp+Jge0NxITt4NX4DCA2KFTncmJ8hCmoAegIqgyU6UjC96HqRmB'
                '+w8jsJ3ifNaMRvKjxSjqnfT66UfNmcmimNmgOPDJvYgN/pEvszRng/OWzJEwid0hyOJMs8nKK/biYukkOvyZyHSjwNJXa4n/d8PA'
                'IXgowBO8Au58FDwV1/NVQ8GlOFpBpNCPup+nQsSqGPXkgcNYpX20P1cLvoQBT+dbOWox4LIC0y4t9BwU2YEHq3SksaBlhQncYgOF'
                'JmZ4Xs+krpIC4B3yQn4Vd9Qmi5zeBuVUyZVKeGA94Hm5LwKu2X05E68k0X8JsGZfEr+WEKgr+HmTG6qGSYbnhoKHIa/EX/u0w+BF'
                '6voL4BVg7+Ov/RV1FPXC3b/VEuhrt6AyRC7Ag7vUgdhrp2UEz1QnOq7oinM4/XRTXzfa7uAVg9S36gKp72Iv5IyhIN0Ku3OMPsWQ'
                'F6rFSDJzNBTtlDmAzVEc5zycSqiM638O1/x1WXiWs6/9k8Jm6MkJFDQxrnR1t9nXfhcJmnSePF+77l8WLiDytcsg3Mg3mT2n9cLz'
                'kaTrXi5s/uW0U8H0WV0dVRXXkbGUfu1l+sQiEjnZsxNRbXHeep6+W/SJ2BuVFdsT3M9W4ujO8BC9gNZNa07tzL8bCUwtLqHhVTh9'
                'zxMneipQ82Vx8abViZm4BO6BZI4DooiiLVxprf033ofYr2/A127DKXLYWpmiEgmP9AKMBcnXTifj0GoCt9jjpB7R4kq51Scnno3K'
                'IZEQteWOhlqBjsNVfXAR+drjwaFAFChMd6ESnSyQqwjp9dlcNQLpt+s653dTibYIt8p4X75HFIy/8kIqH26lzjOkRGt9VCWQ2Yaa'
                'sgPJLt7hfZaaLqv3CoPY57pUlbn0iD6nc6moWyb9OZmTicNuEFo3JrK0H0M9nW8+HkFTs34ArfisTnXqEiI+h1AJAYnkZd7P2GR8'
                'dIOZYYGek9J+dECooftGOhldCtUx1nCEGhaa/U3hLGDHIjQu+J9Eo3Q19oOUJO2Ow744OQJpQD1hAb7Rk+gNXD1HRoyB4sGHfNiQ'
                'Q4LvLU/yl1Ga+BxA+rDYdd2vP5nmz647pZckBY074Zje8EvOwtGm9sska3mYFC+BF3qmmJON1MVFg2QFgeS6iMnw5SO9r+2t4fCX'
                'IYWHXRaoL5oqrGw9uAj5pX5jBUYykXISOZgxhdiJFcxzOWmLBtCgcWlaXk2mDcSwR3054sNKFhtbmCdrhLCFYdvzJZNKyRR2hiJb'
                'BNWRWMBPBO4Gwb/7C7DF6dQgs/hYfzauqBMX/C07dE+LcLCdsY/CeceiT9HPjUqufsfdmEgzgdRMTtGCDLYD2Jfr23irNaMVJg/u'
                'C4HKRJWXtt6hLiQTWqQ6Njyf36gtkXdsZRoKipIf8wnpuwsiN3ZbGN2YesBQ0RUkpZzofIg21jilwPMZsyGMjHuwNUZ0jQ4B2Dgt'
                'SA+dR876BK3IHfBqCK9+9p4MxWkB8txIrw6cAn+hvI59QFLTMXD4C5BvbnsJuG+pB71Fs/ZBTp97MGst3QqT8GHKaPJoy8mgR8LL'
                'OZJBxLMiCPPeQLFy1+jKuSXolVCZb+yCw/3Ih9az/iBgxL5kRol6TxDQ5JT2vO9w33M8wmyQRrur4D0vIe552cmT4mWOxjwxDEuV'
                'Qr7n50T/cr23Auc9r+H5a/apWEGKF0lDnQXfb4z3nMLJ0uB1E3lPC2ERsgEudjiS/bcWV7Ecnsj6zs5AFBuI8ucDxooQEwDRZZn3'
                'rC9igHfTBnny0KlKo9tQ7+kdyUuzl/mY1+B7Niaoh7Crm6ycMgLMnTTWjVDJQnCIVyw+Ubz8fMhZ2qiFyo+DzGyliK3ze0Ld/sDb'
                'zJE1NU6oyGdt0GaqbssVkWOaqSKY1GmxLRTJ1pPAT9f2NYteIuCL7FxRGmtbafBVEYPWjEaPFqEtFylrc36hypsyGGwTgpVgyE51'
                'FaOB+U5kWtB4NZtA+S62NL9giiasKH+YgoshWkl+I+Kik7OZgXPHcrww0Dl7gBvGTdvVs1b78K5A14M7/Lnk9XLuoOcobqCvhbmB'
                'TqmiyKMTmyry6Bu1FWl05ASxkciFtj29vX9qW18+7p5qnnfMgxG1t7FhHQ8LEGDHFKwLtsEHgUAd5RZMeoRJFXZi2xes1rYXmzh9'
                '7UzhH7r1BD5KR7Aca51BLOkJLElIO6AbPIXtRC1TOSWZjNYEKBou5UYgDZL49aW0VgcYz28VRCDVgSrhLibsV4llK5xQrWK0WeUv'
                'pSzI2xFVAYGUBMG4MdhpUhTM1rhqCKQQSKUUj205+UGEf2IDbH5L+KF9eMiDkcrnaLSI7tO3X4xKtnPkVqXpdipam0Lk2Mz8FYjI'
                'zurzIMIPe/DGglJeLMLvrhmilWqG+BJcOTG8YYEwb77bEHQpVZDkb7vQsy/ZzEEj0FQeILOXW33MEHGKGeKhKeLe34jIbYoowXM/'
                'QU0sl00VwzgbvELkI8Y4DaG84EJYDYlpAd+AKQjdunyyleg0I4ovAGLT21rPBGGFvpQs4BS1E1OX7cteptVi9B1SN9c1QWTofwLN'
                'EOoubzMEvST9Isq8shBaNR4iXGl2aNOti3w4r13cTJ66ZGRHK2IrnHyTuOxOBpSfRRFtzWKKgC/jXRRR2HRFZf+HrH0SEWmKiDdF'
                '2FBJ2181FSaTMK8orkzzC4oAmbdGWxAEzAr7xweNCoR6C/KAoqeY93UzBG67AwifPWYIJfy8GULJ9qMZwpEb7GerCcLBYXSbseNS'
                'TKrOobg0ioU9//H852/8j37CPb1+YMEbJZEFTc3+M6/7KmZn4cWqpqdlci3T8/RJUdPzdL0pwl7R9MSlvAMswblqDNgEhPaTipmg'
                'bEVTp4/m1EJEnYvp0DtXuw/c57C216wAFigo2NnUORpHLP0HIl5RzHzZ30ARc8w4IeCh8wOKIK2y97xMXRmaYAhQE+oserADtcMv'
                '+UxVZqmr+1aMoO6U9b7paVn1ielpmf9Hu+lZWGb8UzGiwKwo8T0GpZg8xwdm71LJZoaAKXHsWwe9mAfy7r7AnHQZ0SoBr7ZIxKyn'
                'vKoK0qMpdOB7EmqsmmEqis839RpaAvLOmK2o/qaIrn/j2l9lithoijhg6rIUSUfuMepClV+TAFmT2KnamJzmaTDLlSUoZ42BW+1c'
                'j0r0FJtkhrCVNEOsMjtNHxYwQSS8aHKqn6so5gxODfDhcRfpz24cXPhGCeU/a4G6virPwOUnolKT7x/6tmd2DrjQiS3OD9JyJ7Gn'
                '2A70xxZrt6dqJroB42iWMI8WyApsyCzko2Rfhn7LY28RTiOFpic7y/40ecjTiNqOTGhTONg3os6w3dpzbmluV+Xblr7qX4Ze4EKf'
                '/qx5oWC/vPWHbeTms7RN8M5E29cQDGRAm3WpGPh8Tafj6WE6VDnb8Js0NuZ9v0w31ZQhiMhqabySNGjcHOm0v/S9VpEzLfwaf7bt'
                '5jPrsytbxuhhzRWyPsdkLDNyz/WE+Cub3wCGmFJr9W+X8rUxEboDLdCTRojHTiYn6pzgnZjvn5qhFMrlfNP02TVCQmvOc4qt94Nc'
                'sRvRWhq0l55qQRYhKXpB0szmnFWRXh3oPIjOKlO1p9JpLpzhoB869Y7BdN6mmZlW/lTy5TM/9UrnPh9AF7GcNZ1O1ubMezDKGW42'
                'X6GCiOuFZ3oTpulf6aXMN4721nyQH2q2oJpRrvoVhZzbcsr0qsEh1b9JM6qCsvoGa3M2hXfGYA1y6ftBrrGnhntOFcPLJn0+YOhe'
                'GHvwdlL81a3vFMAKwf1rfvwf7pBwBA=='
            ),
        },
        140: {
            "ascent": 130,
            "descent": 34,
            "glifos": {
                32: (48.734, 0, 0, 0, 0, 0),
                33: (63.844, 19, -102, 26, 102, 0),
                34: (72.938, 13, -102, 47, 38, 2652),
                35: (117.312, 9, -100, 99, 100, 4438),
                36: (97.406, 10, -107, 78, 128, 14338),
                37: (140.281, 4, -104, 132, 106, 24322),
                38: (122.094, 8, -104, 109, 106, 38314),
                39: (42.859, 13, -102, 17, 38, 49868),
                40: (63.984, 12, -106, 41, 125, 50514),
                41: (63.984, 11, -106, 41, 125, 55639),
                42: (73.219, 2, -104, 69, 65, 60764),
                43: (117.312, 14, -88, 89, 88, 65249),
                44: (53.188, 7, -26, 32, 46, 73081),
                45: (58.109, 7, -50, 44, 20, 74553),
                46: (53.188, 14, -26, 25, 26, 75433),
                47: (51.141, 0, -102, 52, 115, 76083),
                48: (97.406, 6, -104, 85, 106, 82063),
                49: (97.406, 15, -102, 73, 102, 91073),
                50: (97.406, 11, -104, 75, 104, 98519),
                51: (97.406, 9, -104, 78, 106, 106319),
                52: (97.406, 6, -102, 85, 102, 114587),
                53: (97.406, 10, -102, 78, 104, 123257),
                54: (97.406, 8, -104, 82, 106, 131369),
                55: (97.406, 9, -102, 78, 102, 140061),
                56: (97.406, 8, -104, 81, 106, 148017),
                57: (97.406, 7, -104, 82, 106, 156603),
                58: (55.984, 15, -77, 26, 77, 165295),
                59: (55.984, 8, -77, 33, 97, 167297),
                60: (117.312, 14, -84, 89, 79, 170498),
                61: (117.312, 14, -67, 89, 47, 177529),
                62: (117.312, 14, -84, 89, 79, 181712),
                63: (81.219, 9, -102, 64, 102, 188743),
                64: (140.0, 9, -98, 122, 123, 195271),
                65: (108.344, 0, -102, 108, 102, 210277),
                66: (106.703, 12, -102, 85, 102, 221293),
                67: (102.75, 6, -104, 88, 106, 229963),
                68: (116.219, 12, -102, 97, 102, 239291),
                69: (95.641, 12, -102, 74, 102, 249185),
                70: (95.641, 12, -102, 72, 102, 256733),
                71: (114.906, 6, -104, 99, 106, 264077),
                72: (117.172, 12, -102, 93, 102, 274571),
                73: (52.094, 12, -102, 28, 102, 284057),
                74: (52.094, -8, -102, 48, 130, 286913),
                75: (108.484, 12, -102, 101, 102, 293153),
                76: (89.203, 12, -102, 74, 102, 303455),
                77: (139.312, 12, -102, 115, 102, 311003),
                78: (117.172, 12, -102, 93, 102, 322733),
                79: (119.016, 6, -104, 106, 106, 332219),
                80: (102.609, 12, -102, 85, 102, 343455),
                81: (119.016, 6, -104, 106, 124, 352125),
                82: (107.797, 12, -102, 93, 102, 365269),
                83: (100.828, 10, -104, 81, 106, 374755),
                84: (95.5, 0, -102, 95, 102, 383341),
                85: (113.688, 12, -102, 89, 104, 393031),
                86: (108.344, 0, -102, 108, 102, 402287),
                87: (154.422, 4, -102, 147, 102, 413303),
                88: (107.938, 2, -102, 104, 102, 428297),
                89: (101.375, -2, -102, 105, 102, 438905),
                90: (101.516, 6, -102, 90, 102, 449615),
                91: (63.984, 12, -106, 43, 125, 458795),
                92: (51.141, 0, -102, 52, 115, 464170),
                93: (63.984, 9, -106, 43, 125, 470150),
                94: (117.312, 14, -102, 90, 38, 475525),
                95: (70.0, 0, 20, 70, 13, 478945),
                96: (70.0, 6, -112, 39, 26, 479855),
                97: (94.469, 6, -79, 78, 81, 480869),
                98: (100.219, 11, -106, 83, 108, 487187),
                99: (82.984, 6, -79, 68, 81, 496151),
                100: (100.219, 6, -106, 83, 108, 501659),
                101: (94.953, 6, -79, 83, 81, 510623),
                102: (60.906, 2, -106, 61, 106, 517346),
                103: (100.219, 6, -79, 83, 109, 523812),
                104: (99.672, 11, -106, 78, 106, 532859),
                105: (47.984, 11, -106, 26, 106, 541127),
                106: (47.984, -5, -106, 42, 136, 543883),
                107: (93.109, 11, -106, 85, 106, 549595),
                108: (47.984, 11, -106, 26, 106, 558605),
                109: (145.875, 11, -79, 124, 79, 561361),
                110: (99.672, 11, -79, 78, 79, 571157),
                111: (96.188, 6, -79, 85, 81, 577319),
                112: (100.219, 11, -79, 83, 108, 584204),
                113: (100.219, 6, -79, 83, 108, 593168),
                114: (69.047, 11, -79, 58, 79, 602132),
                115: (83.328, 7, -79, 70, 81, 606714),
                116: (66.922, 1, -98, 63, 98, 612384),
                117: (99.672, 10, -77, 78, 79, 618558),
                118: (91.266, 2, -77, 88, 77, 624720),
                119: (129.344, 4, -77, 121, 77, 631496),
                120: (90.297, 2, -77, 87, 77, 640813),
                121: (91.266, 1, -77, 88, 107, 647512),
                122: (81.484, 6, -77, 69, 77, 656928),
                123: (99.672, 17, -106, 66, 129, 662241),
                124: (51.141, 17, -107, 17, 140, 670755),
                125: (99.672, 17, -106, 66, 129, 673135),
                126: (117.312, 14, -59, 89, 29, 681649),
                176: (70.0, 12, -105, 46, 46, 684230),
                183: (53.188, 14, -62, 25, 26, 686346),
            },
            "dados": (
                'eNrsXWVgFUfX3nvjShIsOMGd4hQoDi0Ul+JWoEVbKFBKCy1SrMUpUgrF3d3drbi7BgIhIa53v5sEubs7Z2xnefu+355fLTv7PJu7'
                'OzNnjnaWAanS2bxiXjGv/E9eaQ1dKVsZupIpO3AhRrImoK9cl6S76Cs7JWk/+socSVqAvvKTJI1AX2kvSV2AP1SSaqKv5JCkvMgL'
                'iU6S5GpDXbkn2eUJ6sqBlCvHUFcWplxZjroyMuXKONSVrilXeqKu1E65Uh91JX/KlaKICza3lCteiCtPpVR5qb1yPO3KWe2VFWlX'
                '1mmvjE+7Mll7pVfalX7aK5+nXWmqvVIs7Upp7RWftCvpNRdeSW8kUn3lnGRKqpgrn3nlQ15Zo/qHcYqvcbbq6lxzuDncHG4ON4eb'
                'w//Lh1OpY1lROrxC9ikHdGDW+DooAR5qBnjEKUdkZaZQndbmawbUVQ64yq63PtIc91Tym3LANGaGgjLpZ/hHOaARM0UvJcAVzYD0'
                'ykNnoi8zxVrSz9BSOeAYM4M1VInQWDPiT+WAUcwUZZQASek0I+4oR1RjphisBDipGZBbOSDalZlilxJhtGZAd+WA7cwMrjFKhJqa'
                'ESuVAwYwU1RXAsS6qwdYQpQjSjJTjFIC7NEM+Eg5IMTCTHFciTBEM2Ag0sbBIL6JSoRymhE7lAO6MVM0VAKEOWk+h2jliNzMFFOU'
                'AOtJn8Nt9oX8khKhD+lzmM3MkFm1kBcmfQ4tmSnaKgGeaD+HJMWA5PTMFPOUFIs0AxorB5xlfxX3lQidNAOmI+17DKI2r2bXjLim'
                'HFCHmeIrJcANkooV5wFjLZGNkjMmhUlhUpgUJsWHokBIX+XQSySlX86l9/w1XTNA5aW8z8xgeaFEaKYZsVA5YAEzRQmV/1CrvTxQ'
                'jujCTPGNEuCCZkAe1asIYqZYrwSYqhnQlWQZIb4K1VG4qWbEYpIWR5KSqlcRQLKMfMlMofLKntcMyKd6FXmZKTYoASZrBnRTDnjE'
                'bpV4RbJKLFUOWMJMUUoJkOyvGfFY7xHvOyXAP5oBBYj2QpJsUgJMIinUT9hfRZgSoaFmxDLlgKV6DUTJWgPRU+WIr5gpBpC2FbW9'
                'sAAzxRYlwATNgB7IaA0GcQpXIjTQjFihHLAcAzbcsD073KQwKUwKk8Kk+FAUCJlIMv7WUQ64xm5xVIUTfqMZMFo5YCYzg1+yEqGE'
                'ZoQqRvMLZopGSoCXGneElyoWNhMzhSqEco1mwKfKAZfZX8V5kh1eFZf6BzNDgOpVFNWMOKEc0JyZoinJM+StdMvYMjBTTFVSrNIM'
                'qKcccJH9VVxUIvQk+banMjNksJFcIqdJJ1mSNFcCPCO5RBAnWZL8QdJVG8h6g36vKBG+Ji2Sk5kZMhGPDWf1hhl8QTo2qBbJZD9m'
                'ipmkE1wj3d6pa6TD9GTS8YkkgapXkY+0SDZgpmhNsmuoFklEqANJVNEWi0mL5Gn2V3GDZGJSLZK/MTNkJVr7VItkPWaKdkqAB6RF'
                'MtGHmeIvkuFVtUieYH8Vt5UInUmL5DhJiOx9j9j634a2TyjafqFoB4SiHRSKdkgo2mGhaEeEoh0VinZMKNpxoWgnhKKdFIp2Sija'
                'aTFoAWWa9/91xnIHO2n8vcMrJvRrUZZx+Q9oPm7nC8zJ+8meP/rUpjsJFh55KpnqNP9gzeCaeIXBs9cZJvuA7cbctlkArHQ/v+Ax'
                'OVyb0VzrP7R8+ZzbhnFEDZbrqA6LiBqtWZgsDq2fTRaHNkKn7ecIxrWgD612kkA0vyeyQLQFskC0kjaRaBtkgWh54Sl9cWrXug4r'
                'ebsM+cs37jNu+T9RMBr0qcVNSz2u7kGsvZYcjYZvfo5Eu40GO/XGCrEHXMkLfbUkRI2WGw2221MioaU8ZLlhZxVonZBg970lGrQU'
                'CRp06j3aDCTae7PWHoo9q/C4Fej48TQJdWFCk6CI+TTZJXGiRaPQFnGiWZDTah0nmhf6YxOKlpSeD82K/ngHcL6FWCRaWFY+tHvo'
                'h7ucgQvtAKQH1eNBmwcub8da+TCj9cSsqAn7J3Y9x4RWin65pkCzBlOj7RtYJzOjoY4gIXsmtcbFvH3MvkM9XdMjiDItg1JuTaqI'
                'RGvAu4neH4P6m7dyb8rJG6tq94lwHbv8bs0f3FiXJjLXD5/+wijB6ryj73XBJX6rgmsZpQvvZxVckZO64PqpJ2w/PSeGJM2n4j9W'
                'x5/7RGvK9x90jxsO5d6wfrookg8tIR9y3no0ncul8sMeyRJ9VwezokViD9K5m4/ezgRJztPNfIoebQ1539hDjxZhZUEb22PiDuwL'
                'L8qClrIDOlecDq+GnVjRUqwcYxMBtLEcaJJUNRqNtpQLDVXcKEUO8aFJu5FoFzjR0A93ixPNF/kiHnOiqWOb5fc1uHjQziHVW6Fo'
                'J6WdXzjxoD1Foa23V+a63cOTGS0j0nw4MbXOV9i0ooxo6LpqPd9WDTvSzZ8BzeUKEq3M+xpkCZvbpqNFG41e35wUFc0SDwwuQYHm'
                'hAaTN2nro73YOLiKFw7Nqf4F+ATwEmWkubtpbJfaBTxUaG39clXu+RdoKo3wQKO9i/Z6cPFwKPW28LuER2OSqIwi0VJVOFFo510E'
                'okWlfVpi0JLeBBgIQUt+GzEhAi2uhSQO7X4lSRzaMofFIt+Qf/R9GdVVy0Te/rvjOLHOtEFpWV4Np5xPZoWKWISpb+HfaPSuV/Tn'
                'g0UtPYgbXt6mQ5dfIBxC4s7M6VGEJeypQqvvflu088zNZ441K56e2DJ/XI+6+Zz5HXhn/o1eRUM8nif/xWgn/sU+8WP/YrSj/+Ko'
                'icP/YrRD/+K4mgP/YrT98r838kpsVNgenWi+NX/4e+/N55FJcWFP/lk/pUtRKw+KVaWQtKW/Nd/3xzWaQtjSFp7Mz9BHibGf+sbP'
                'dgBW5tBx2dkeIZPSRJpYlPK+crjIjrhxPjqK1FGGC7vPIFjagz+lf4RKSqzH3lR3FbxIVOtsvzlRPoKTKqS5FdVd5an09HVuEk/u'
                '/16qmz6hNDrvpXqIzEoDZEIhmpsKUevZK2hKlC2S2SN1/e7SHxtGkOGqKO945EXzDMtYTrSViR+kylLSguYRWmiZYufUC3TxKtYb'
                'YZa748FWAWEXzSO4ar0qe3O8vfil1oD8Ax4u8LVidHwBjsoNKR+ew0mqkuYIF44vQ7aEVLAQ9fo0JtpTrvg39SMOrppy7ANPjiww'
                'u+mjKLYoix0Xs1w6X+JJhdqipliFL+Rhl88k2uIDdJUhvTSmio+ITwknWGaNUG62+aieoYmaQFvjtI16CFx3ZTmiXYbEmrGH2uoD'
                'NAGLUE2TGirfg4fEeq6T37ftwCaignux2mROmRBm1axBGSjCQ4DUnUHKUVsotY3sYIcO3Cq2DomVTakAxOahfAZNzAoq60bTUAWd'
                'JaUqp/oLreLXUg2/llx1CZVDaZdaqr3NnfYZumPC9cCCjXIc6oO8huzhQiHfquFnUaTlybKVWL93A70S/gN5eZAkH80zaFWj7Mr9'
                'NSa3xFt9OMU3p5V0mmfQ7oaqmuRDJe4KXOhKq1k1z2AhVAW45cbwDJpvcjFiUH6NqqfRxW5Q76wUuuR6xKCPgM5J7+VH8gSHpQJN'
                'FbtGWmezUnIqV/zonJKeFEz5NVkx0UamrCNVWsaKRXPIC9QOmk0I8lDVRrjuym9blKFcU00ImfLY4nZT1lfWdqIaX5vzn15jHVIu'
                'QENJhQtIoomnvCkR6iCrYzNyKeuTR2VnfgaPGDVDOaJOOw1Xeu57DiPeBpKCUlyzStbCKBdXXTieQfMybCWwqoldM3Bcqd1ukyrF'
                '02iU99UcZ90wFantMsjx8i8ydakxjPTWkKx2OPOWi9DYKh0jIoOUEfMRWfmeweWW5iH2vVtsO0Ri4vvtsllvSX7w17bbQD7L7OxZ'
                'pMdp7aWbbvDHdJnf/bqQxRZUwdGuqruDw3tL/S36ZxiKSahbIumQAtSRDAqaPMoP8nWgLp9HpQi6R9jlillAv9XpeClLlSW62hXz'
                'LV9w0vkMUv7zZJv5OMWxwkNpz7NVQZ5nm49Zfuz+y5jk6Jf3jy4f0zwH3ncwneA7eFpXwrU+WKjVj6pN0Zod702phjM3l8X6UMaq'
                'fBD5lEakMHXGsnefmwDUzT44d8anDL6k7TKuNJW1Oy51+Fk3nJ8u3+ATKJ+a1qjTTDnmnPKDLHiWFPyDN9/61hoyf9+tkKjk+PAn'
                '5zZM/bIY6pk9lTWWbR8rrnYiJwlEdtA7i6QxSsS/Jcx+TrPi8iys8UoDUkasqQ+QCfqeYSemQNeP1HvPd3oeQXVKPeP4xbSkTway'
                'NeB/BK+HSijH7Tw7Sw5MSGbuZxin6RQt4eLig0d+7OfsX3l0iPbSBt5HKKj8IEPT43WyqW8XF++/tBdrcD7Dbri6sdM1Dcu32El7'
                'hu8RVEXGTlnhMkeyOldH60HkOo94K31PyWUluG+e3c2gXOX9w2hsskT5DWPP1Obk91Xd/atGR2YvUCgVVpabfBGANdiEqDe7DJoj'
                'dkdJT+yO/LZ9uQSmAv+puX+jRj9kfgSVX+m4QidyjVcTNJEI1bbtPxXrI/go89iSSyuullPjIyqMaasb5JR0WY7+IPyNNxAQr9WD'
                'GKtBFlUmAT33I9i2NkvYsN40GSjxhs3JiDppq2kM8MvIRjiJvuDcEQsp+7k/AuR3OucYpGgq04qSNM35rqrhv6Ip/L5X4q9lO5Vc'
                'd6Ad2QHJ1riymPKDfKbNL3pGXh4QZQPO8VuVEbp5MM2066UxwUm8nWAPShRVQtrTvIsj1I+QTvlDJxZDjLlM801q9Jjd1M8wTSZ0'
                'wED5AL4j7/0MbSNLKuMPniIDGZdyrVG/07pajijva0Ojb6dmw0mE2sGout5o6UwVmdpZDY8qPB7GEF3jKH5KY0ICkNOisfAnaI0d'
                'OWWKgAuJXNcYeoNOmoCORmSH6n26R/goiTIyVVMVY4ZE8EnL8jy6D5K6MLtGiQlW+5z9ImnWc618KRNa0b73liaTVqmh6gHRVNGV'
                '/iH0kamb1BS3lb5Ob8259y+Jo7ozNjL1M81XPw5XE9cupWgeobTy932I/e0s2iKHjjWK+2uuUgXUWdjK09dEWJjffpceWkNVckmO'
                'AImdElvPs9Sg3mHlfZ38Ko5AlK+YQ/MIAS8ZI1MzsZR2vOvDUeOaIjK1Pn2WZXwlKreGEvA+TWRqX+pnaE/lfz3Fs6aNpnyEQVRo'
                'Xytv2ka501NVBEruQYWVXpnSHkfdjq4V2T0W2oir0vcIiVryniA8wsEcdEDllVbfu+4SQ5xNl6eYJ3hEm6VkPUPq9Cbhi9NeB57g'
                '8lfUf01Psi2B8Ft8MlnrU7s9oRI9QgZlXkgse6vKFMnRfMyK4w9CY22xoQ+OLR/dLBuvgTpdpe6TVh26+Tw8Ljn6xYOrZw6umtiv'
                'efksVkm0eDSZdgFwPcSemfdt9QBhTJb6y4jpP482fFfWST+Ve88blAtmxPYfKrno4mp9X5Z1VB5jkdwHZflDkbV/LX8oMss4Wf5Q'
                'ZE4r5A9GZlkofziysfKHI/vM9uHI/DlrjHORTZY/HFlQwgck+13+cGRuuCiqy782L5TJ3Tldlo8a9ZlzOk43WX2Yal9Z1XPVGH1G'
                'HxkYqWBDBgAGfX9BBxlUfEoeDN1R8e9oTjInqEDOWYzCkWFEKBcZWOUcf3LwGviSg+wTiIx04PAd2ZWZrB5E5iGJlxYQmasBZE0g'
                'svwGkNWCyLoaQFYQItttAJkrVOLSVsQANjDAbYUBZFPAdbiqeLIaINlVd+FkTo9lltK6OmUoHPbVSDhZAKzkh+UVzvYTvFdfSyea'
                'zOM2zLbb9YMtWSmzTfihfZLMU1CZU3xxxSd/EctV7ipWGe0pclYPTyQYMlsK48pGPrfH1xLEVZsmhyGyrERXEeq9DEcM/I6uZVBI'
                'AVY1V7vRO8+lPbHcx9jckCu5Jq/Pi6FrwGV/iamxh9oT6HOE5TR2FHJYZEYOV432ZWzVsBVIKaqENLqrDlv7WU+ai9D5D+1RY5Vx'
                'Q5Y17OfaSfRulln6G3gNoQhIR5yBGvDZWVBqMnJVcMxGyBQC4q3eiyFLakLO9U7VXrzhBGMHtEGSDy4vI7YaoTCarKl8/imElZCy'
                'wGe6iWELV9de2Ywa9Rc2bvtNjFSa7pYb1yMhWKlxeSKTQ9qAoYnvpdebAcVwpa7uBGLCHN9IZkw8l+aPrxyDYTufjvThX5Kg+kHv'
                '4wcc3Myf43bvg+8PAUHILWrKe6DFAIbis+6Am4gb3jks0K3D3ucHuALq9nnlV9YfN7nfxuFkRP7cT61EY0Q7FsPxOGRwk/b0MwF9'
                'e4wXweeKiM8rilYqKmDy9qFkEKd1GDKbPXrTgl7Z7jjoHfHouxGVwLBbXuLn2lodsjqZvRBwMyoMzhdXJTumK7qrWKRDFHdD4F6k'
                'JSLzLfZtaCoccfBO0Lpa0FNWruQ8FDltQOG04qytf1Y63g18+WDIf5UYJq54Rcmu6cCo0pAO2iCRhUwZmzqduf9ZJwZ95aUfPkZV'
                'Jib9DaAn60tnY/kHc04ZT8t1zIlQLumt4E5Ff9NxRebFp7zKpJJgacskXRPT7ur7ioGPhYuZdadxYmsjlN3AWLBZ2DiKc0SuG4gQ'
                'h2vgrlEdxxZ4hxSahLKXz4BVQmxtizz4ZlbxyHIMzeAbzvnj2Epim9/1RztvMcvPqfTcDstLfhJl3OQ7uQk7KrwJk+0gshjW59io'
                'ks4AV9NHpK9xLcpa6PQQe8/eEoh76hyjmGczJMbOmilTYGt9ZcRM0IDrMncauctt0l2hK7+pmdvHydUvT42v5lyhX/S/lCRy3UpR'
                'koiqn7fZKLZoRPPMwJdGsb1EhK83tRnFdj8rRbk/YXIhHTEuVKDs1y4lzksNY1ulXUqsswxjm46YAKN0fCXhc1gtao2527OuyiL9'
                'jLuOWs7znuWiup26UOCs2Yn1EWzOA9j7dT7tmWbAdd6OW0rKo7aAHKvZ3lzw4HchDt643+UFWuktsYo+0v90B0fvXeA9zNB7QCWm'
                'wtOoyhs9n/mxxFA8/pwvsOm7NFtD+DLv/1UXEfVaBde2ai/sw3SuMmo/+kybeHVpd/F+Xbtds/GgqWtO3HkaFmuvhvPs3j+bZw/r'
                'UMqNG05tzx9n/oP5Dx/8Hyj6HKTKrxJNUX971aN0xI4BcJeBJahFF+ENrCzTBXFaUI2LnyHi1DqiABF1HDxRvtUXiIw/5Eb7EyK8'
                'EJXoE+lPGXmEiMzJhVpOE3NSGl+WITQA5Om2IiUgojh5UCJlF2qkavRSu+AGxpHNfBjzm1bv90FuZIgiBN/JdH2hrUiLSbQ2obAh'
                'bTPnnZQm9HxIDeeFM2VkvTbt0gltta5DLgOb9vqcyUnYMrqioC/a2t+CbjLLCVrFBa0x7qE18HxPqqMCG65XoX8cTXAA4EtbRRsr'
                '+A2pTp78rquxBHeEdJAozfvzQyu1+yk/CITtG3jENqTKOW+lILkcQdr805wci6IBz5KrSctAXVbAoP4T5beIKC0AGF81xaZdgbCl'
                'jOqBgD8uSqLMQrhBLu0gA13kh6MHrqHbClCGPcA6+ivtt6Od0+dpw/jv0XmiERV8oIUslMJpnyrAqflzumgt1L4BIGprMgJnRW1B'
                'ICDDSRt/+ECmzDu/JGMDQyRUQ08Zm2ICmDJH03qutE6aXwH7N605+gi5t4KsCQaCSr2nSqxmk/EArCBauwJg169IKrIng07VKZgu'
                '6grpgh6oLc1eGrBbaH1t6KCHGCuuZbCjFJYoM+vakbvsQHthoEy5uwKxS9HOtD95WdoNW6tTeKGXldUUvccAvQfaQrQFWQLR6sdA'
                'iXLF30VRtCfN0agtNJQBrRc2k8i1iGSg2hD6wwjR2s1c0ca9mrRx9Ih2akWQA59Zsb15ZWzjsGaUur3khFz1Iz0pGhJBhfj8kDU0'
                'UAUBkdEtNkQbuWzIJWM8AnIe0tTqQnu8bkPuCpsmxxED8yVRKYgQJKrZVm7UHx6fjTZDClUnLCPq9USgMmR+pgxNQ1tnnqPSEjvS'
                'eveRFqSnqPSryhQhObCV66mHRGk3GyxRWuJC01Hb9sbQJsX6hVEpXBK62PirjIiBXih1+G8UJCpi1IZy7HiidM2jEk19SCj0ywu1'
                '3N53p83/Qn2t/qjQ5zB/2jmFWnVyoRaTmGzkfpUy2FYNmQYRn5OmtiIUtoScfPE5aHPsZ9DmisUgPrdC1P2HkYeGl4gNCa2Z9tYO'
                '9EEGRV6z0PYtrkObi70R4S1D/pTJOWnjAhApcOiUg3vaP8c5lFZdWERpVVGXdH+rLmgXUd8EylOntAc5cB2tAhKndQKUkSnVQ2so'
                'rZqEtpW+dCK3r5Q1uTBpUhY9cJj2LUZRGnUA7RBRhnSiTPlhtKM9JRZGD9yh/cnRAcrh2q/3HG1lBaDZuLYW4zD0wFGUXzlieldA'
                'D7xGmUEnx2s/ICCAW1swDIiZ12Z6AjmA2hL+a2XKYJiZMmVyMFBYcBVtCNYucnHrNDklUWX2oYymwMt+SO4hDrXgBXIfQmkrekTQ'
                'Ir6ijb99rhnYCj3wMaVTR74tUaXKoWz4Q9AD99IWnVpLqv0Jq1UbaNez47S5j3fRAzX9QC1xlD6TbOhxSa5U5x5FdhHeZ6Jdm0fK'
                'lMH9q2nNbUBeX1HNHgeYBDVGtJJowIPkiuAyqg+spCn1LoN1KtE90pI14f1u6Dd9RqJ8gWPpDkuolX4TejnReO6dab2blWhdAuit'
                'NTGA0iWgLbYckETp4kev87G+pMbs4GLi9prSA4N2CDxxotSux2hNi+GU9rAmlD8isKNr3VP+yG/2tpXSRIuIAEJ6scO0qmhJSscP'
                'Okk0TtsmzCOM8oTdDaks55Loakgg6mJXRwLmpnwrCMA8qDkQm50yxQeRk5UBpVyGB1C0zgCCor1RB6gH7pQh9gh7j2cIsR6DBKbn'
                'oWxSXs8prVwo81FYRh2WOJTu+w9rsZ5i/O2NTBAT5F8PUmfXR1wgWf96b9m1nJVti3Mxg/iMipZfZ1AoyXET/JlAXHqHONZ7cH0T'
                'IvRqkBs9SIs3JULi32wU7/P4H3S00oFUeX9aWZz2pzmuouc/pQAptEHTd0J1GthdmgASODtJo44Eqm1XtiW5MSDeI6IQ5S0QSUVx'
                'EwMAEOeeCLfGSckb6bUN+94dBdIUWd47oZTkPwZpi3vYyaoGqYQ8LSQvSS0kkGky0m9/4TMFSAF0eYmN7/phZZuNtLFedDREIZ2c'
                'eysotIyFdHW2lL+oxlZYaBVjNtZlZG+Kj7YwQNzpAO2nFfdSQjzthavPXuMoBUTo96QCrPVJyVyRoygqFFqa49JT4yZnpFugre2h'
                'nNjEuTno13lfdJ2U5Nb0EK69oEoctlUF6CCcOt3D/CZJf2Wn+FlbXiO8ndiJpC5d9f+h+E4ifsE1sql+lPKLfdEfSn0qv5th7jzs'
                'iuqEUHwD40JwvaXacp9/GUda5tlPFfmBf6HWrSTHYJ4jyPjHA+9acmSeijzSbimiWGP9JyENT5uKpx6K0av9mRqaLSNoJXq1zwvs'
                'O/fbW1D7ToXDwL4zC7V1uUHbKGr7OoXYi+OnpMfsxc59QlClplRawaq8BK3Ad2ys1kih0E8OV6DQT3Issmn6Yr3XlG40pVS3Su1R'
                'aUrvdLaQ3s70Olv9y0qdLU17jBntw6Q9OnV/qqgWZvlHTp6fjVmP9Roe5aDHSnV2luDSqAP/GmIeVUwQE0SiLp59QpKMqcptApvA'
                'JrAJbAKbwCawCWwCm8Am8P88cDHZGPnBBDaBTWAT2ARmAja3JhPYBDaBTWAT2AQ2gU1gE9gENoH/A8A7ZHy+pnndvG7kdSiy8Ba2'
                'kMK7FJ9ywOV1mKI1dnmZGVvZ4F0CkWc8voZEPTw6UKmrNT6N9X2Fiix4dHQKdWt8k0jH+hfBWHRkvcHW+GLJ6/AVUB3RJddofOJW'
                'DULtjjFYdET5GmUEcUAyvjJISzy6poJpa3z1UHXdkXx4dHX5yDZ0CZNI+dUca441x+obC25k5gXzwge9QKHVq9SiSJqeNqOJtV61'
                'coVYs1Mjqn0vwY/inkHECq8SqapGL4pbMik1Als2inu6k8oFScTasT9S3OIdR6pULJEqz96gebSl5JKEanEJI1Uk00od5S3BFop7'
                'ZpBLG6rF8ojckJowdV67sk+dFRxTpzX71In3ZZ862zmmztcUt2RWTZ1A9qlzjGPqfM8xdQqwT52rHFNnDMfUKUdxT13VbkAzdWZS'
                'dE9VT53HxFKVGimvvCXMheKeMcTKkFq5KhPaLGglv/KWOG+Ke75X3rOF5tFUzWu7sU+d5EwU93ylpDlM82jblPcMoLjFJ45UIlEi'
                'Vb27RPNoqkKLI2mmTjhlK3l46jyQ2KfONI6pU4N96oQ6s0+dhRxTpyn71InxZJ86GzimTmf2qZOUnn3qHOCYOv04pk5uintakRpc'
                'SMSyz79wTJ2SFPeoSgPfpXk0VXLxJJqp80R5T1WKe1SlUl84UdwzlqI4uVpUyfyNKG4poLwlyoPinsGkMnIIOU7svKeRQGUufaI/'
                'xT1fy4S2aghR2YD70EwdldE9B/vUOcMxdYZyTJ2i7FPnFsfU+Z1j6lRmnzrPrOxTZw7H1KnPPnUi3NinziqOqdOW4pYsyqmTQFFh'
                'RW2t38nhmu1JcYuvcurYslLc01pWlTSikBXsAa3qxoeFKO75THnLdZpHmy0T2+Fqpo6qWkwFinsqKm95QnMMG0fupKCR68p7PqW4'
                'pSCHBeMHYtdYidRE6wv2qRPnwz51tnFMna/Yp05yIPvUOcoxdQZxTJ387FPnCsfU+ZVj6pRlnzqPJPap8wfH1KktCRBr0SYDZu06'
                'd/Pp66TYF/cvH1/xa+cqAboAyw7cjKrOa7swtSkncMGxjzGOrMRNzVyZH7LNcaKD7OWkQCbMJhep/G7R4+l/hVKnqN15rwfSFUx1'
                '+ilBZpDDeWjMuCdkNokkm5EqvZSZZTJhz2oSI3PIKqym1j1Z5pKDXjBmc05M+14CmlmqxMrcMh/ALPRK1iGjkJjul/RgyjakPjFF'
                '1ifBiKp2dW06QeX12oPiU1m3dKTsVf3GLvdn+6IZXLyz1x58EjfsieprzYGZScE9HMzkRTdiUFW2ncXwyM2q03ybKHBoVBbHgcXh'
                'tzRPs1qUjwAHzyJ2TkyVTYhFuBY4m6MddoIM4Px8kp7i1Ip2If0IDmqDnHxuD6DxD94ZoZzAvfgcsPx2AZ/iXZ+pWuCQTpAKGSIT'
                'IiVRtQDf+HFAs9UE6JaYNxPAGgyNWEjrgJU1Pb4+IQ1A6anPoHtWYDtX2Q8CmOP9QnDHTpvTYHXWi/TnHVnVldkbLKqLM8V8BIIO'
                'RHhGKI9OTnHQXRswXV/sUgWnIoA72gsJbOqWIljj/yrwtgJw/3a7UotVkEbhZmo68OI/LP4JZZxIRfDiRixoffC+xWBHG6KjuDh4'
                '32nNgU3GNaJzlIzgfRFAj0uK8B5nG+ar2QdeI8RkvAZvLCzBBZUJjvS74I3VJVjHJ1isLoA3foH5aYozWU4dpG8WWDUhuJDh6tqj'
                'CsCghJPnJvDGKZgUf0JgGryizCoDg/owuSQcXVSVYFCCR3YJeOPSGjAoweC+ALxxzWcwKMGtDWuKm+vBoIQwk7/BG7fUhEHd8aCL'
                'wBvXVoZBvSSWCCLHF1UWBvVlsjc6flLwAi4TjC5r4I8fM02zM3nZHacpZkEhhHMdAG/8FbP0lcKDwnamb6RQ8BrBIwef5FupwzZk'
                'XMsthcCWwBpQ7hPZgQyfZosAzdBS5Fsspjv8hjNI48Fr+FChbLBJzSJ9CV6cyxKqo/Q6fwxe3IEFbQbeZ4+I8wcv4s3634D3pfi6'
                'n4O/DRYUPCil9sXdyzf5t4K3pbgJfwWv1uZSpUItYLPrtDkMiydondiUapFKwrxGUOADbZp3COwBgYslGAiCpgVoTwavZ4ZB14Nm'
                'pDSfQjVmw4TdNAGakd448K3PCAMQUhvWeNHOLgczUzpmTSLWGx3XTuG994ki2judn0BDbjhRBX3LqFjZoeCYrkjMdODG9vC9VpcR'
                'tAi8CGRT+BxDCuaDo3Y5S7QNiFOsUo4mghLw7r9EY5asGw8O/pNShZN3qgwUPWHMaGXcRi6MM+J5bwdvXpk9GPPxCLxLVSmv5rQt'
                'HODsla32EGyHoWB1HLVvsH6TfBeJsp01g2xGfHzTdWI+Q0Vqe1zRB4qOjSoargcTSkWoHsePuQh0Hn7B7enZhTnJ9eR08h3Bnrhb'
                'cLn51hEOh1U4HH3Tif7oAqcZIaN6UDijnX9JZME8lo/OFV/mDDVkxGAniVaaXaaCjJmQQWIQa9uTRMiXk7MwB2IUHv8Eg5i4pQVz'
                'IEba45b/fivK9mi7NL15ekmHOBVrNujPPedvB0ckxb18cPXkqjFfVuWJQbEU7DD9JLi2jKMDydJ49O4w7CshA/nUGLz2EflzwQK5'
                'lOk5/wrl4gMBWfK3m3qcZamBgMqyLismkAlkAv0PA91bNbBqV51AL7YN/zwjIp6VBSjq0IRWQVBgLCVQ4j9/di3uhIuwJQOVvrX0'
                '20ruxFBd5u3IBDKBTCATyAQygUwgE8gEMoFMIBPIBDKBTCAT6L8CaLYsRE6YQCaQCWQCmUAgEErci3zadfjcdfsvPHzxOjY5MSr0'
                'ye1j62cPb1vai2HVdynVdfK2u6BD0nZ3SY+iFMVIgjrMPkMT/vH0j+q4yITcX614wvC7BI9Ap2q41Z9+k/lHjl+sCUbwb7c6ku+N'
                'JUwJoI2bJ8urVsKg7BlavsKg5Gu5hUHJwaWFQckRpYRByc/yCIOSb/oIg3pbZE4E1Ju6jUKgHroLg0qrKSoG6qUXBBV9YHLvTwtl'
                '9bF6Zvqo6aj9FPU5OqOgkg4MKKeKHvXtQaymcEgDlbS1AzJGxtKaVJ0gtxLq+mA4wshvHR6quyPUTnyRKMt4LNTyd1CJf5PL203E'
                '7h1voJIW0hSOte7EYaVLgbItL0C3SWZ/jYEqa4c6VoF6w/0FA9VGGteaYe/2w8QAfcN4+oNTsKgKyktwIW6ZsYq1RJUTLE9ghPKE'
                '40hHs0akwZUqhrBCBWOXGUFPxVqryhn+2VnDFguCSCGsf19bEGotK9SfIFRv1p/qBag6Z2eEagw+1GHWv+8kR+KMxJjq/9yDcQLe'
                '1dfB3EEmwXuEF+NvDq8KX7IhFYD3iAMWJqQs8A8VlZcJyR9TFK0dE1IGTN7Gn0xI2eDkU/mACwtSoXsw0m2myOXKoRj9n+knx2UA'
                'vC7FgtQPEyQcXZUByDoJo3HE1GRAcl+NQYqty4AUcASDFF2LASn3Ndw5sAoDUplnuPNDeQakelEYpEeFGZC647IpbuRkQBqJ04aP'
                'M+Q3uCzAIW1k2BR8d+GQZtKncUhZz2OAbCy7S9GHGKS4NgxI1XHZBq9YJnCbeAzSPZbP6XtcLtWZzAxrygzcq9vCsAl74krUybMZ'
                'PoKMuDqYNhbFPN9tnJmQ5SOoEIJBCqvGoqjgqmfeZ/kIeuGyT84wVF3Fn/xZPgLXZaI+Ar/9oj6CnLjcsPi2DEglcSbtsOoMSHUi'
                'cB9BEQakTjg711mm0rscpWIBqW5CmVAmlAllQv1LoABjwMdtBkxasfv0rZDXMYnJcZGhwbdP71ox84c2lbKybBxSQI1+80/h1OSw'
                'A1M705RAt5TosegW3Z90f14L7BEl6KuVL9h8jYuBg6+10liu4g2Xu7gyVaAhyb3mItFkeW8ekWhyeDORaJo2EzrRVG3G9KIpXQ26'
                '0WxNRaLJETlFojmWUxKA5tD3UATaDqFotvwi0d67ydRor47OH9K6ZrFAP3erT9YC5duP2/ycjHYOgWa7OLk1ovaGU40ZpNXvXS/e'
                't2gRK9rAPUZ9RkTJFKEHb9Bil9Un1AkNxNqM3rnf7Ghnv6ZopGWdh0Nb8NaUs/oTyhPxJgzaHolVAjA7+UlmNEwJN7qOxCrfAmya'
                'vM2OJsEG4cscaDNE/m6Y2mYbONAGgGjTOdB+kXlKrUMyF0Qrx4EG1jUNc2IHywiarVZyPNpg8A9twA4WAK6Z952ZwSxrOKuSI8H+'
                'AMGuuTC/gS0gWHJ1RiyfAa+oVTiSV6rOHFx4zlqqzkxWt3S5SjXsPfMoPoh1G7w95WPe5Rdg3gArWgy2OBcj2m68y5MJ7XQ9krGd'
                'Gip2FdlrQokWtrozTZtNSrRHsxu6ikNLUfNmlxGIZpeD9USi2R31ZUSiyUm/ewhEk+XzeUWiyWFVRaLJMfVEoskxlUSiyS9zikST'
                'jxJ3QIurd6aCH7f87s/j0WS4gQyO6kojrhLQItnsVeWX4Qu3TWPcBEscwr7XjIxw1mE49+53zMpDJwzcBXYt6SfMw+VkRrMekxkr'
                'DmMFrpktz+NQL8/jirozywgQLZoDrT53jxKU5JUx1fuZJYMs8gASAKNVZUcLEooGt8iSSwmdW/nY0TDlSzMxg5XDVJS1MKPtw3it'
                'pQk/sy2Z32JWpKX2Pjexc0vTgzVLwi6+qV1zzvWlrH/aBwdmn1hvevDEbe5EnrK5NuITdhw7+iTsHIBt0xQ0lVB2dLq6P1DwqgFV'
                'kA2F8vTYRyyDWgTVbSjp9tZJvZtXzpvJ19Xi6pWlaPXOIzc+ovFbSLjeRaxSTyTaVkkgWnx+kWhp/SwFob2J0xeDdtlHINrlt8Fv'
                'ItAuvAunFIC27v1BVTdaoqP6rBftpOIMqA/t5VdKK40etODB6hZWfm2WhfFhnf0KafBxrjriSAIj1IOxOH3Iu87P20IpkaK39y9G'
                'YfoLajJs1SXskSri5MxupVnMgJasn7QbOGn5rpPXg8OjE2xJMeEvntw8sXXR5B9alc8gCZKS2F+2Dxem6wVZPOivsnjQconiQd1I'
                'YQg8oL/J4kE/ThYP6kEuBMAOOlUWD1rNJh7U+64sHnSWLB60jiwe1PehAaDzZPGg9WXxoP5PDACl3pUZQJvI4kEzPDMAdJUsHhTR'
                'W+qlXtDMWoQbw/SCahu1JVUcqBO0g/bOsZJO0KxaPe+Sq15QbSPRhFKSTtBu2vt+lnSC5tS6QU876wS17NbcFVdE0gnaC7Lr6wDN'
                'o40zOmzVCWo5CCbg8oP2g/363KAFtMlBeyw6QZ20BvbXOSWdoINx7dk4QYvE4dqz8YE6a5tjvQzUCzoM1YpXJyjisLRS0gnqovVe'
                'PEuvF3SUdnQjSSdo2UQwZI8bFHFYepROL6j2sGSrI+kERRyWZko6QT1uaEbe9tILOkUzMLmKpBO0qvawNFHSCep1RzPuqrte0Jla'
                'G1w5SSdobe0fP0rSCer7QDPqnIteUO1hKb6EpBO0HnXNHXpQP+1h6YSTXtDFWod+QUknKKJCTD9JJ2j6Zwz1SmhBtXUvI4MkvaBb'
                'WEJcuUG3S+JBw7IZACpCkkxQE9QENUFN0P9voJKQ1CE+z5kJaoKaoCaoCfo/BVpMFllwwkQz0Uw0E81E+59Eu8y7I5loJpqJ9t+L'
                'Zsnd8Md5O68Eh8cnRb18fOvo6infN81r4UJ70H89Ml4q4uiEuu7MaDiJ3fWltzg0u0QtqCgQzS47K4lEs/tB8ohEk2MGOQk9L5zM'
                'LvT08ayy0LNMQnuhJ6PkdkLPWUmthZ7a4isI1RweZRKJ9j4QSgiaQ1cWEWghASLR3hcQ0qA93jW9T5OKudN72Qud5Kz4xaitERRr'
                'XmYEWvzhkQ20hcKdq8+NpC199w7t3rS6nmD88s8EvDAvR7Sbw0vgt4/sm/BwX7xDezmZJtN4IDZVYc2byLQ9rV3p9sq2uLSPGC/W'
                'rbeHTMhcZJP5GLRRzGh+wSJrpOGSeCPY84vdw8S1PrLLHBitEjsaJla+LTtaehhtMIe6FyKonJNESEGfxIG2WxbTuyZNNoNoC4U+'
                '22yhv9tEDjS4FuQISWRth4HsaM1gtJbsaPNEVmPwxJQj8/3oz0zCqjY+lcrKrwe5MoAFYPpRrLSjyfKddlZqtKWYfaFXKpq9zFxr'
                'Srz+uD2r6Bs0+wGyI83f2wW3PdvLU5Z99z/Bw0g1Iyw/YjPzfnFEsytNy+vhihvm3IbXQ/Io0VJe8sRPAMCAkYSCSbslDZpdQpd2'
                'zK/R32rOI+pvVZBoKfJy62896hTM6uvk4pOjwhcjt1DolimPBqBxHI8qiESbIglEu+UpEC3+jc4gBq2jJBDtnRooAm2aRSCaw06l'
                'Gy3R0empF+2BQgPUibZeWVjG+umaBG6sO421a02mQZe4sF4PBexwhYdfZcV6PMgXs7IW+m53HP2L3N6OuI141R97KIYMFb2rJ23p'
                'A5fyPWYeCYf/vh3DqriyKhuBFVsPmbFy7/mHL17HJSdFhT65c2rjnyO6VeYo5aUVt+KN+0/fevrK/RcxydEvH944f3zn3yO6f1Ys'
                'HReaf4NxR8BWZiE7x7cuZGXSJ3seJqfMRx8bXcONCs6p5dZE2s8neseAEqSzpcuXNxm/74/wz9fzAfPswyJ+dIZjPmMQPX9LlIUi'
                'FrnJt36BiI0iZKGIlmE2WSiiZR7/DoBEtMyWBSP+IQtG/E0WjNhGFoxYIlowot9tkuX12NSudQpk9La6+WUt/XmPaXteEBDX4H1N'
                'fzfS1tct0GnhcxixMQ4v+Dtod7GUHXMHjeiNqcYRP9obu/SVmxmOQJwCA94g1+3z7HxGjVgcLrq3w5tqD6m+SWmGhvvlrnTh2kKL'
                'gAvObj5ACey8eN2XD7AAdPROLMuphUwWaIRKO+1CTVMee3IiNoIesQuv6rUWAHzC+Z4lf0j1+on3EVtBx/EsvIjQ9neQW4OFVp3e'
                'vIAFoTddgBexD2jd45XFFI0yAusNWbD72vOIhMTXwXePr/y9VwWcmnyR0G/Hud60Gwgv+JnxlQCV3iUB236j8BS4r9Hz6chutyWh'
                '8SmJpx9vJGhqez+TaArUpH3fLlIQTTWgvZoi+WOhV239nu7sapvlRfeq7x+lN1EpA1H2CjDgJHZ3RLwmxFz1m8OB67UY49yCd5Be'
                'gmyH8oy3iLlEIb4zrRUShmh7U3mjlDBEOSwtWuhjcYjy4dS3U0MgotxJQlcQ4Jfnfrjd31GO/1wnj4+TR2DFnqvw54mU/fgzMt4K'
                'x3KiPoPDcQ/pQfE7hn2uWqyy4boT9CC/65dFtfakzZjfR5JK4wGTqiCWfY9z8A25pKJ4xLHokDnYjjFIyo0FDPFBb3d/gndslzyx'
                'iCOBHTk/uKGFWyWsLyc3tMkfBG8pLuFOrOc5fHrtJNwGNRlEhJesYdI6DGJr2K4G2nj/libxWcIuwuEt3TGIPhJD/b03ckKqgjEj'
                'YDQ68Iu8hAsMeYJBHAPddFeSYG3ursTR2+4uLmziBgbxR/ivxnTS43rGE5JUU+zvaC9g75Eg9F0vt188JvR7TAnyGyl0zqQ0cykh'
                'dF5XT7l8nX3t+Qi6JdkXqHBGWh/7ydiWrcXZ1/ADMj409Li4faZJ2oAvhO2Fr9+cQJ0eEPviUu7X898OGSRKp3hXts3nOYPe4wpH'
                'n156f6z5ikE3O0gVCuiEKXu+3PEU7fM9Ju7xtmP8SS2canFsaJ0gL6t75go9VmJ1XKWD+W/9avh6lbH5pl7AyByqX7xMgk7EL5ja'
                'z1DIBBZTKY3sRsUZWZbyAx5Em1NdtvECHoHM8C7z+QA3Y/a4n3kAx2Nd2K3CWfHC2xBsfdl3MP7F2cj2w69e0eM9aEdlkkw3nNJm'
                'E9yXOgTCfxRFne9T3TyYXAOfr8R2OLo9pSS7Pda34YTTSN/S4439C3JbeX2qdBq17PjVB/bYjJhQex7dignffpZRTP12Gqltoplo'
                'JpqJpkNqikR74SESbbjI1dLeylUg2kyRK3kyR39IabuMT3xjEviUW5EDbRHoTuAAywEq/Y040EBr4nX2PDXJD4xl68bxaEMgsGdu'
                '7GBuwbLAUINuEFhUADuYBfRFTuV4NDBIKik3B9pRnJWOVSqBk6oMB9oGCGwfTwSFTVxmqiT9hbHoMktgHNZzyCigIfcxRwyPdxi+'
                'QyebfAeBRXCEdjs/ZDFRSOxtgdIkITsHGmgAW8QBBntlS3Cgga2Md3KAlYE1Ng60lXi7NJsEJQlMWobjjx84s4OlB62U/TgeDXQF'
                'hXmzg3m8YHNa46U3BBbPEavndAdCm8fxaKD/wMbRP146DaFt4QCDYyaqiVSaT0mCiivJnNnPsNJ8x4kdLDuoNPMEXU4E3SyeIpXm'
                'kRyP9gPoi83EDub2VBZYBgBUmpMLiFSa14lUmnkqYkhHILCjHGBwRFMTkUrzDaskUGn+SqTS/NydHSxzHBySI1Bpjk7PoTS/IlZK'
                'YhAwmikpD4fS/ECmiNKmlfbgl1tOEqg0HxCqNH/OgQZGJ1+xiFSau4hUmp+6SgKV5h9EKs2RfiKV5kkilebEnBxKM1jeZAnHo/WS'
                '+TJ10UrzbWwpDEZpCT5aXQ60UxDYBaFKc3sONDBU4KGLSKX5O45HWwj67H1EKs3jRSrN8VnZwdJFEMOrRCjNtqLsYK6g0rxN0i+W'
                '7FU7j5y7/tCVJy8i4pITo8Oe3zuzY+mUbxsW4dCSMn7x2z44+iPp0vw+HzHsYKVGnaZIPQ9e0ILKfJ++/wVqf1HYLKJGETghis0H'
                'tbcGDs59VCy7W2tfIRCv1m2ZR+JHuQBFAJJ5fW/HULPRY6MOb16wNsfWfacu/2CY2l/gtFWnx/GVyq7zq24f5jWFfe1Tm25Ahbrg'
                'dkeEn7UGtgk2h1x4Z5rxeCUEUG7+FvBLQb7lPeSqhKmL394RdQtlcvHNXbbHkhDsSNsbZ3Vm3CuOne54HHPvcReH+C3B6WCX2+oK'
                'gD4rMaO3po2ZC484j3Cx/A4Pj0zbFuAw/ZBciFXEiukZlxbaGsqop2WOwQdFpwMv33SibQz9VlLTR3OAlwcAK3sh/B2FZeYaj08x'
                'Vf8wyUjhVuZDYqqaB6arXWFX9VItmkHQ1UMSc4pMalFYD3b7el+8T/UFc7zGUPwaux+4elViLjCRFk45Abj6GnzLUDmWBwSTCFS2'
                'xPIc73DxiATzFRlPQs0kfMnnW8BcnglZ6d/aPspDjB2QeFnjiMehXZANE2U4cIJGx7wvZl4yiWHFnkZj9JwA5tyrLQi+YPLiFUcV'
                '3hX0b8VOc2yw7dELNC/GFFMePB9h9uXhdQpmdPHJVabH0pdwAFlT1Z9ShCIqGxeQ9qXmt85/Vwde3BeIzyGAXyl+gC5jY+nLWSVq'
                'PhhxkXMZhyZ7piruLPXRSsbDyulmpFNpzpEPqdEi//6Y6uDdmu4TShhNFdufdfA56id8PJVYOqrapiS23/B8J5ytqvoJjo/mydeQ'
                'YzbHJt5DFNqn3T2Ce6bYZmpfj8dCXYvDObWnxe+IzjPKc6Xul+6crFfCHRcIt/24k/DG/lWLZHbxDSrb8o9LmLn+PB95o7XLpbaK'
                'j6LgQriOwaV3b6YpOCa6o2bq5zlNLFbv8wQacRcVJOUOfg+2SviaOXIIEA8GluY5m7b0Q7pSUk1gSvmAucINsLGzE9gdzakOthsc'
                'sTqHoV8xD8bN9RdmWWoI3fSjJP1EzI5FiEsMXNwL8uolYgOnoFznBHfpFVeoDZjBXS67zBVG2BG67cvKMrb6OCQNoNtGgB6hn7GA'
                '4HPM7c4XGgeeLFZ/wxcmAEYyb+nHnsKP/Q13fA1dWSBxRayubc8XnTIC/NrA1TregyvUdFZFGoOldi6Duu7PGUHAP3jeib1QDJg4'
                'Go2pu30Ik1RykqOZEfw72QLgY54cD6WweMNF0S5hFl+7gpqZ0bCUWpPMD1Oa+VpBpn3ZLi3sA3Bq5mttDGLQKdz4lI+3OVapOttC'
                'YWwpOB9bazrVLOIaQsgXW/tNZbvZ2Sd36RbTLxJOWpVJrVgY5U3ehMdTUYCVBJvu10rkbkcsEvI+JDLwhQhAR6tD5VhZQL6fozRJ'
                '0oun1q1axenDm6s58FV5qQdvKGLS5z3GDfeiGXJVoq1rqZGNmaGVOO9SDqvIpYa47bHEGsbK9Zc7kEI4s/5MbxWJW1aVxoxhrTia'
                'pgfHq6WtGCo3Z23++2G4WlzyzcW9y3CEgGep2nX0X+uPXE8JnLDZAyee3f9n55LJAxoV5sgmfGOwq913/LJDNx69jE6ODrl3+djS'
                'ER0r+fKCSUG9195HHgFPT2jIkQBVaDy2xGncqgZMuSmu7Q5S2C3GUMfDOnW+R/chRoyiCwf8nKGia1gvcliL/yK26beHFBr4aTDr'
                'AhHREQv4Hc9+MBr+y105ax4thUJJndfzrtx70XPSaRX/3rLOibWLKFHmsDgW6UR77Kyks8ZTstqE6v1Q1imP/AUWeFKrdqk+bNyX'
                'nbRzYLUcXk5eOat/vwfnOGhJddi023OmOVYfyjET5r7n8FVWgAHvqq31FeBffMj7UXCI1RVt6k7WW+CiEfhOKQF1klDUWpUHjAT8'
                '/e2QYeAjtkLO186gOfqtDe0KozHCcha6oS8pnBaqjtAauuG2FV8PMRhSQlzA2KdPJWwHjj/Zk+Hm4UNCWoGI4LsJTXEMZZPh+sUS'
                'c6RLSg59NdBiAu9IzolwGVx7P03o4kXMpgnGWT7C2Vp385RISCnyP4cnoWYTrlb4Uh6r72qcVWIDT+bsMjiyCo6C4HxGmydcWZfv'
                'd7QHtWwU+67tAWrLeb7HW7je9GBKXBRGscboC+sw9YRzgIgFMJvsOUyUYkt2F4Sc0mGkCq7IkMTeDT7J6g/uhI+hxccZaxDKCG9c'
                'YMEQvC2xGKYt+34AEe+kr4lrOobOHW2LV9IaSt5wvOVzVNx4LkIUcEtsl7AL2tNkJtIprz2+TdhNtb+3DPEYaq/1bL2BuZ4wydEF'
                'mm0a2WzTG5cM/aYV6HefZPOwemavNnAXzSmvf8rxTUhI+FtJbSr7uUjEbvgEZA5Jq/KZ5Zk4xDfR5tWThCHWlyTBZvqapMY9zFKC'
                'HEDIKBkocimZJE6xTMUJQLynPHFepr7x/AG6I4vb73RhbQkjXbbTKjfFtlAAbsgHn6t+0a7RVbfhbde2LSmOJksky06S57fHsFV+'
                'WlpSXR4ZbjePbuM46gTixd+e8fnbSLYm0JEYY+1zKd19/PKjd569TkiKenFz/+JhDRytAcMFFnKQsIHgk3gB3WMFFi5LM1QCgPGe'
                'olvo7eMFdAkl21PYpC3cZoZTTgosV5W2K8n4fCFmsUDNlhMyciJ2pqyFTy05w0WWEEv5cg5iej1xyQJZFjoDLXCDn9Oq+LrmVEVb'
                'XOAnVJe7SJLv9CNXsMyDSZ3bIKkR7WkAi2tgH9R1ACaeNyI7AjHlnDi5CmR/8+iOzab9RkIjpvgpl3crrNksXGpND8XukCetMGKq'
                'RW3fH70alMmWzs3qmT5P9Y7j95HCl1/mlvCIzE4ARAUGfYiohVYX4gqLYMT1SP+mDsRN6Ih5fsStgOOMG3EGFNPPiRgPl+3lQ3yK'
                'SbXgQbTN9ZeEIl7DRz0wIz4bRIguYER82JeYXZKn53rqVqRJezrSlSxx/mTUUYpcopP9Alm2OmvhdhP2gmtrwsmJTfkUkfQlG/QY'
                'vXDPiYu3HofGJMe+fHjt7PaZA5t9RNd1A3QItTCvmFf+HVckU0z5V4g5G80r/yWrpTnAHGAOMGKAKaaYIlR7MgeYA/4zA9qRnAVQ'
                'jbSjb+3gV9HXY97W+c+GCWPB+ZEOvzO0o6Mgo/MRilN9S+ibfui9ERrZnTsqr4Qv9dTHwTGLipXa72Dlro0icCyY9BtiQC/H1QNR'
                'F2Svoxk9o9azH6lwLSAixHoQ4upU4ZGaSk0Rytjywug6eu/lG1KnIXWu52tVpKJLpDZgSxngoLq+XcKXWAjPTgi066y+7peEKrdo'
                'tDjXX9bXANgK00L4CrpjJe8vae3PxQJn6H1c1lGCHvIfttrsEEQrCthaa77S7ycGuOTvmlAbAcA5BqPSOvUCp+u6Hx1rpAvYtfFq'
                'MNdaB3DlWTivLy9wwVGEunFcwJn7nSb6ZtiBvdrvoHFPMQI7fbaEshQ3E3DZKfRxoPTAQUOvs7jnKIEDehxhyRePXduSxnPl3mJD'
                'PANqwpb2ND0BLNXnhjOgJu3u6k/zExQbx5KGaDvUi6p9VbaB51le18n+2WhQfTvvYalQeP6H3FRhOQ1XxjCgXv2lINW39fEMllIW'
                'd8bQdYnMP4KlQP2jiXQdfjL2PcniS/+jClU3As82WxlKJ4T+VYuqmIC1zsJIetTXi+rTOdZLTWQotxK9sildl4ecQ67Qo8ZtaO1F'
                'uc0cpF+2Erd3SiegCYpKkvd9xdRyiw7YdrRvoCSqbct7OTMwhySwH8wbufRTXi7NAw98Y2QRTo0GB3xvfGmJXyDgJ1M+lnQJGji8'
                's1WSjACW5RP9shkDnLI19s5sCHBqeFD39IYAp64Pnf0MAbZL/Ma23oYApxix1rT0NAQ4xfqzrDFTMZrAQ/Tr8euF9Vm6U+X68QrL'
                'HlqbpSBP6UkMe97zmdUYpqVT3UUMu7R9IWHob+TZdhuDXvHg97IMP0mmb04xaEK3R7P09i4wkiUz8NrwwgzYlWayFPy68CPD1uXS'
                'aBVLCbUzg3LRY/t22cug0duOfcvQoizboAsMj518sBdDY95i4x8xncW6BVBDW2rMYznnJWxjUO/cW25kqWITt6EN/fId0PMoy5Ev'
                'ZnULD2rsoGFGnP7TpNzUZ8YA2xfBekujDAFOsQl12JlkCHDKdtb/jDHAdin0611jgO0zp8rsUEOAU2ybTdbEGQKcYo3tdsBmCHCK'
                '/fiHS8YAp7juJjwxBth+yK+9IMIQ4BSvQustiYYAp/hB+pwwBtgu+YbfMgbYLhWnhxgDbPeOfb68bzHZGPnBBDaBTWAT2AQ2TD82'
                'xRRTTDFFMncQE9gENoFN4H8HcJFDX/kbtdDHrWvmZtQOEjanqkUyaGu6P6aIYXveP99lMWozTdrV0duoXTp6WX1no7b/kGnlDdMr'
                'bvyc1zCF5XjvDEZpQgmbW3kYpWK9nl/LapTu9vj3koYphZcG5zBK27Tt75rOKDU2dnVjF6P049BZlek9O5WnMzVtuTuqIDW2teaf'
                'TL2yTn9LH+bj/NkCppjd7e29qLHdGi+PYsCOWvIZfWiI5xdrWVz+z6YwhFj4tN/C4oO+NjSIHtu/626GOk62Iz3o3fJSxl4HGUIV'
                '4je0YFAfsvVj6fMdPrc6g/qQezBL1+qH44qxRLT8fIUlHnsgQ/SGVPzXWwzRG3s6+zBgl/39AUOkwooGDIugpdI0hqCqFzNYIiit'
                'NWYzxJTf/pTJTffZ/DCj7MeujZZFGmWY9mi5JsYoi7dP+83xRpnS/b/EF5TXY6PP2BOzVOk0/mftd9wwr0KRE0YAuzWBNko9wC6f'
                'L3ot/jd2rjvvlfivwlp91gvx37Gl8rRgA2Ze+YmPDFgrSo27Z8DqVnTUTYb1+DNK1ILDGHbVlzMr0aHm+YFBD4hZ2ZBuz8sxgCFe'
                'NnlvF7q2nFm+OcqQl3dhEF1Qf8YeBxg0uIfj6TShgK67GHTO8Hk1qHS3dB23MmjJ8RtbUuUjebfZwNKy4WhPKv3Yo8VqlgS668Oo'
                'NHq3RksjWc4gU6lS3VzqMZ3IopbWozk1OdX+K5TlnLejA805z1ptZgjLyfRMv8xUCupUpsbid38taMTpf3YV6jMMPXDcmiauBlhY'
                'DnQzwsJy6QcjbEJPJnxkgBUrYkFtA+xuCVtaG2EpPNHHCNvmzV+MsMaGTK9ghMV7+ecGWLyTd3cywkZ/boARXoUHY43wg4T9Vc0A'
                'z038+uYG+JqKHP7aGO+YVnwrtv9l4Y6zD0OjkhKjXwXfOLJ+zpAWJajmttsnQ9bcQSt7iWf+aItNe7RW+OUwQZ9JOtAPKF3u/cUy'
                'uj07fqnWRuPTcROLgXRrSWXBgRUs+lLqFvSHg8LQnsdZeruivvvluNb67pdt/fXdL9s66btfTqyp7375sb++++XFOu+3ldZ3v7xD'
                '5/1yIZ33j9N5/2PU/VH7xnWtGpTB1T2wUNNfj5L+ANX9534pp9wsC/2JO3z2UNx/+0dUtmMljLHh7/f3J6+pCewmOeEkqcNv74/7'
                'Kz/Geg5myAan3Z80F39ohnvJW1PuX09KToWbUHu3l69TNI0CW31mbvYTjZK/GbqfsgIA2AaWzoQB9gy2USrSUNPkV5R78lN97bVK'
                'yRzNqB1kukzb9QltZga3V7rTKNid+w7V7c3Ar/c3KgseaBpOzk1xe6abmM7RZPGDDX1JFIfDDGfhxWsG+fbsV+HbQ8j2pJKPMbsf'
                'uZFbXVxLL/K764IrLHCQeKb6BbfxXCVp49aZuNufktLqnZdh7cSk4BaXdVhHJanQgfNa3O3PSbZUy2KsDaoQ6ZefhLv9BDGzvyfu'
                '9jXEg8zHOFvt78QToy9GXbB9o2Ottau87ci3B8H260SawvJTYYN/K4rb3WEz7wCaxRZujr2Uaq0HZ90zP139RemeHm7om0hX8icD'
                'RH+EbqPOq2Otl8ACznYZThmLodMP95++3xRT/pPy3z5/zPvN+837zfvN+w3UP7J/1vu3lQcuPgmPSUqKCXt249imeT93qJLJ2J0p'
                'feOxB6Bgi+Ad4xoa452yVBx9mhTmY7vwe1Unwbzlp9KWhAtdUMsqjNZvIEsItj2saXQOMV/UxEiZVRJXVdLNW3RBgswl+z7RxZt7'
                'tU3mlt0luXk9RsTKeiR5FmcwRIsHsl551YGDN8suWYRsYg4q+DxEFiMv6zHxuk62yaLENpphWct3Fuv2vrjs5+6fl8qZycfZ2dM/'
                'qFy9HuPX3cE96Q7qDIyP4YSr4JW9iiPNrD61Rx0C7VQXKde0RpDf/epI/AwNaL8eWHaeUFVp/Rr96KETaYJU0vdBm9SfFyffOwJ5'
                '57lO7rTvqs4+LmuyNAx12/mmTNEzn6IcGcF58Dd9hdr0vmCN2rG0RdTqvYVVmJpptY74cV4cK6DbBC3SSUyAUHVtDMzZwpzbTXXt'
                'qr8AHJxf4+ZKHufCvdOlWyLDbeJUv5Dmwwirp2t376de2BJKURqLr+TTqdC0UqcYXUHOzeYa865+9bmm+v1NRXkH1Cr8Zg9Jv3yk'
                'SjazIbSz/SriLa6SCKmu+sHPaZRxdTe+3e6SGGljw/X4s8ekqQqqXvCRRMkPqgVc9fWoWhw+zS7wZDRPiT1ScbGQcl9NqIgB8m82'
                'du3FpxFJEQ/PLx1YiWJJ91CejV4pfs6NtN4a/94nlQvyo0m5JWTkbW6Hc4pS1fje8Qij/Aq2QX9IlhkI1T9hVhYCs+pVP3OYNUon'
                '62vgJbsMB9Skl40JzC5Xga7UuZR+9a/QxMXOYePGcMxSDaDzo9I3ehL9WzfGZtJPxjNLCg0p6W2Ocwblj4g++fYhWCoG4plrqAan'
                'yXeKf12FVkhJJ4mEslhmZSvOg2/+UVFr2lYURdyanIJ1oTiWuZvCpJAOYURD/sklaWJuR2KZfRSfSUvEwlkGpddQ5bG/xjJLCt1o'
                'buo/3SFGdc3hOUKqmdsqDlop/1JCMR4VYFDZJoI5veOnkpSidXzvODwCoYdYUCvIhWFVA13dMlcZfIKWWTqjnrp7HP9hEeJPbqJF'
                'vVzn/eVyhyiZZzte7W23Dij2gPoI5n80oLMVhwXL4GQq5u6OVyfY+886/n8MQgWqpMEcqx7SLpmGuaxq8vaTcV2C7TJXDblcO2YQ'
                'DbMieOKEKmzwO8TBQx1eFoKIEbEcpmCWHJejJ5Kk6FWCUILqqhG7SHRhv1pmx+jCaMnJ8fSY4EYOrbpgoQyj0TI75grbpHyOg/9B'
                'QF6gOw6WomA+4HjZo5bj/y1DvGbVz5gIHfwvkJm3O15O/yUhQqYsoQn3OxlMZlZEEAcoDDLttYBdZJya7nh+IjMrTLjuiviw2uSo'
                'yaYQs6+NyHxQ8YUp9N0S5Bjt3OAZ4CZx5GXFrFL89oiyN1upg8J3E5kdazs8k3Y6DkbYCFQbUQR8elpDYnZ3fB+nled1RG82VWvk'
                'R9QnRi2zQgVZo/ybEFaCyyoLi0QdR6phbuV4daJS909HZL4uUUdR5sZmZPRVvmdEToOqhc9TmHkBiVlR4uET5bddQIun2v6iYeZ1'
                'BOaMjmbzRA/lfEZ0tNyuwoMDtvcSmBWHjLOSNM3x/2uQv1g4S+EhgXmfKgZzuOP/d9XiqY4scivqQNHcuIydz1VnxLFawG6IIzra'
                'h0BgVizDr+0qSD3Hf1itBayowjsg0QbkK5nzJarDhRWH3nNaQE+VQpucjTZ9KTcmuyfFruLhiByN+HLVfv5BaOKKeG2olTIbxqo5'
                'SVYgx5dftVKt2krmPEqLb1/tz4D4gxrIMt5imiqlk3HMvspW5K+8tI6xzVpML7W5IBQRjm05jtP0PVVb7feIePUwxE+p8YOstpDM'
                'uUrmzKqQ9OsuqBUAYXGvpcGcwHSi03iP6r69TWEYnI34Ja9pQOcpj5wDMafYTDPVmuH7I7pi5X6JcE8h0lGvfe5gN9oLn9wLTNIE'
                'wVx57/FrqLjQUMvshMpxvDqiZlY35/QV+h2ErBVl6oxAeO6jHFx+njEkc9hnwkIO5MQm4JaehKr0s0IUcXIb5ZepuDgTwZzpCQ0s'
                'uT6QTXX29lJ8BbGoKjyVaTrWjiANiNIcjebLhE2akNv0xqxXnDDgvvbw9IlSycuJov6JaGUuRyg8swlVvUG5oK9FbkbDCcyD8SVv'
                'XrRBoqoOyegKm52wRSNnYGviJMwBwrXclLX2bqJ9oRUx9eim4IrmJP4NF+Xqr8VB+domAREy4a0wVXWejsOFc3ioWrM2BsYFzUdw'
                'Jy3IAZbdCV/VgBAo1VsVygZmX2YaeE65+QRPzw/U5Yk5NrIyOT7LWRXtcwLj9s7Y6rcNl4MjkyIfX1g++BOrtgxO/P2jq8e2LkwZ'
                'FabeFVazx6l6Va9ereJHBXOlZ4y4Wa22YUsfSgLVdW9//WDUndTf5bAPRr1KTT3L6QMx+6tPwPJGfRElmXfQdhwvp4mUOqEnGrr0'
                'Q3kX7diumjXoVXNu4g4p+t2XtKMRudFzPPmmyvq0QwttHW/Lai31TZ5IrXZvSzVtpL3DHRW3uCU/I29lB1tWG+olEOXri58QyMBb'
                'VBGc8iIj7X0+h1GbbNw8ylpolrqbVaesFdSP7LkdrStvbUqubRbQB9HfvQk1tetyyKm+qD4uHjFD951ItfypHzW1ZSSob0XsGFod'
                'tbD51R9zGIxkns/wkbSNxmnWF9b93qPOR/mz+Dq5pc9VtHq3cWsuY0MvprNs2MVuCDs+vmjINiV9Fgoi3pOVeRlq9kIAb0Q/nhKC'
                'GfX/2Suycm43NS7p4r1Wi3+Lder2lJv3QQ/+YOTU00e/J5y8+gNV3b6+zMx7rpuLJERqrWKpEh01r4IkTvx7HaQrp52w62tfSbBk'
                '7Lqa1AsofHlr4bRpYi3Ve9E19N9uu76gZymD9XO3Eq1+mLHp+PXnkXHJCWGPb/yze86QVuX9DGLbgv+V4wTmhmYimd56iuPqT/pq'
                'T4jjOi9T1GoUIyXJ03GMKK5JZK5HgtJnnZ9RrDO1xXA1kGnLgxpwtkdJtJDcAj+6naKLCK4edPvRARFcx+m4bLn1UxWg3WgFGIdG'
                '03Ld1k1loc8frqyXqya9tjJHLxeDHh6uM2/Im6XBX2vBpkicbNfHtY+FK0lXdficbJHog/RwDWVT1y/p4WI9f5fmp/oYwoTcXFP5'
                'uWZDRoIJ0AXuI48b1O5uJljRrjEv1xcQ4ifSVR2FXpGyFVKaLNLP0ItMz0eVGdKsf7fnBkN/ch8+rgG4LxsqZHCaj+sCAHcj5eJA'
                '6EG4+k3gqyfmsGGy4ZhlMr6k8mHg6hMObdv5OQD2Jsy/F/Qoddm5GhIW84yJusqDSriQ6Hd64Nvwhx3AgBhmo4F/HFgA/o10hv7w'
                'rqxcYIhIr7cj0kFPc4iVC0rCSswIhgW/+5XzsFEVlDFdEEhL83A2rjEQTicHgyJUMukuk0XY+hCAifXFRRFi4v5gqQ2hrKUqwTuX'
                'hQssAa0oQuwCdW157SFAs1YlFYIZlG3pucBpqkojrAGN20nPtR/CUDldrZBVPTkbLVUuaG96oY5dngLHYFHKMAhhlnpkBWjkVVou'
                'MFu3qmboHWhoOTqqyjKsq1GvL39I+tpZTNCOBaMBX1I5NtzBRtKo9GjQz9GUhqsVdPdNphPaBhqubWDcpsRSVzuBwpsfmMRm0z2l'
                'o9sGqNCeY7RxnyVzXYTu/R49PivosiY2Zy0tk3Q1CZcjqjrO4GUKcw12sP7CU4KbxxmsUtcbuiV9IuWuoJZGoE0mE/skIUSSrOXY'
                '/TpA98Ri+3UGgPG5neGbfMAyjN0l+jBSvYKt6X9KLJecj6e7E6eMhLnGiua6D2rb1keiueTqEm1SnH4Bg4eWiOeKBCrb+USL55KB'
                'OqJfGkAl72bcHPRIMjL6NLfNCC55CIrrZ0Oo0HnOt43hQmUsVjGICpVW9JdRXK80gZMe4UZxyS1IRfAEymZS3rZAUZfuyJJkHJfc'
                'TyKWoGE8+QYkUGrncIheELX1ANTdlLUzysgColtgf+NEx2HTwGH96bnSgQrfMwdbhQsY3GnLRs8F9m1MTal/K43BQUz21HYgzCqJ'
                'aE11sO7SCKwAvw/WSh/PcWKQKApDyNoE8D6sOzizCeF9UbXTsiBTuxesHb0ppFEEHJAQwMYlrQSh3mQ4jQcHbGG16jcHoR6katvW'
                'x6zKHSwecOeBmshSWe/PhewxT2AjUXkh/vJadu9SIzjG1ttexwAuYPgFh/sbViU6obKV3j2Jp9CYmX2agkQytqobWeqDcLZcQbBm'
                'zeXbd4E7yA/NR6kz2OKjwkIeXzm6bdm0Qa0r58R7gvLx6SWRJ+f1K+8sGDQNeef3eYWDphoTB2cUD2pfAf4qIh7UfpD7M6N4UHui'
                'XScDQO1eOXcDQOUj3gaAyoe9DQB1sPcLBH2vkooETShgAOi7H0Ao6NtATrGgy40AjQswAFT+mgSq8lp4ZyvW6rczBNBVjKBpUhIf'
                'pxpi4QG161bBRIsxO6hUFJd1U48TFKMHvvGL8YCC8XXyG1cqF2g9GR+wzAXqEYvvjMwFijkLbeAH3Yaf/XygsG4+24gnHWfEb/ot'
                'N6gbfNT8hBsUnlLJ3tyg6wgh0jygn8iENAoO0HyYtS+IE7QKJktiv8QFWng2zn/wMSuoZ5bCLcacwG4mKw1QJl7mFA+aVNsABa2f'
                'eFUyuad4TVpROkwQ6K4g4aeTOx2Fn6NOtnQSf+J7NLmUZMSJ72gjQ058J8oaceJLnuhqxDnqRDYjzlEPDDlHBQcZcTq5ZcjpZKvF'
                'ANC0Qq7024nFJ1uRat8sIDStjczBtZuWmPoKh7qAU5nIsAy3qRTk1fpaJ2H9zHygUmd494/05gWFc0dSCk7zggaEYVQKXlBMSEMI'
                'PygmA74QN6gFzj9vxQ0qbQBvHMEPCgc5LOAHBWOa5Z38oEPAG0/zg/4OH1H4QeeDN97gB4XPp+e5QZ3geXqUG7QiRq/kBv0NvnEp'
                'L2ggJqJtJC8orjVXJ07QPri9rwIfaFfcWTLahQf0TRFBGfTes4OWmfkar0/8wALqnbVw9X6LblDUfhCtS6X6Q8WDtjYA9JLVANBG'
                'Buin2wxQekMyiwdNrm+Azt/NgNPJAPHnqNh24k98jyoIP5vaZvkKP0UfrSL8vH+4jmjLRMjkEoK95tcm13UR6d8P3/97q5wCwhsS'
                'o8Oe3z+3d9WsYe0/ziwJEWve6h1+nLXl5KXbT8LikmPCnt07vXX+uK+qZ9UBWbjDlMNgcZjIQxNb5WYH9W+z7BX5B7o7u2k6BtAM'
                '/Q8k0v72CVs7UkJXWhzH9nnEra1DTLF27nqBy1YzAF+rrjl3qdSI8fAXWO2ErvX2FzSq32KdC8UZJGxt3Wk1KFzP6frzJBC4Wc4K'
                'WIK1uCUeykbg1ouQjcBtKyhKXoXbMFE2Ard6rGwEbrkI2QjcwGeyEbjWvZTr1YIfWpXLldHT6pUpd4kGvcdvfIrHHU6zvG5sg1iq'
                'sjb+4x6IW4PcB/xBH3g7KPLjTSSuB7Hq3JMuhJJRVRfGaXFHkrT3PygKvGSZEKnCzU34ckOqU6aJjIpW4K4jfDb0XQ+yL7W9x/0E'
                'D3vIm0XfqHj2He5m2hBAKnH+KT4NtyB2g7jOXse36ExslbK0XZu76moGbIf6ltzaYj8c7Dp+LfQIBvY1v3abBbcy/MT/uLhU7Fe+'
                'xlQz/Jkf1hOzVyYG8uNWkxkS8xhkMAa3uQ5cjLUw3ksH7lNi4A2XZJUZM3ApBbf0VtGB2x6Dm04ypBjmPT2n6bnGfL2aNtsyvpWg'
                'pLeWoL61DJtMravYMmZaNNSDG2ZQhe14Y6aFE2ZalDUIt4ye3yHBmN9BCjfovWG+swYGzYtOBs3jH/Xg7sV2iuSXeTDuRj24w2Dc'
                'O3pwO2LM7noq1VeVjak7nh2D+72eHwJjHdirB3cj5vjuqQN3COaHaKoDt4ZszBfslURfLIJJDmIeeKgO3L4Y3FAdUyOrzSBV9RjO'
                'T5PFoOYqa/hxM2KNMM34gedgPVYFuHELYe0aV9m/iSIziblNdjnAuEw4//jGDoM9c6act5iAK5x5b+fagAc+SV+4I9tiBzuXFESw'
                'yz2j1Kn8RyrtctIogh0xaQqFsSvz+Ai1fdKT6F541NGZ4FSbF4uw09Yi22nv9YatJ/kHXQPsysRm5ykb07pWiCzwzJ9PvoWxg1N2'
                'l7gx//uWZXKm97B6ZshZvH7Psesf/Wfs9pJUPtIYXKmGMX4Rw/w4hvmdDPOT2QODHxmDK2X9xxhcyXOGIX5Tu9R9bAyu5LfEGFy7'
                '6/CkLj/6cHg5bXmTFzXyd6x517nbRR7U24PI9YMqL2GOq/jUQhkHcpB6aidu78RieQxotzyMIm7lz+bsvQydinaadhQM/406Mql1'
                'EL926JSvZqehf247fflOcHh8cmz48/tnti0Y93WN7BbWIKbkxLiYyLBn929cPLln/cLpv/Zr/2mZLIxdO9hDrxLuHVr4Y4viLoYR'
                'vP3GTs/unMtIgjdxTXWcDSVI8TLNLmcsgV0udHE1lsDuQe/vZiyBLD/sYjGWwF7craTBBHLiaBdjCewpLQUMJpBfNzSYQLYNNZjA'
                '3ibCajCBvMrZYAJ5kcVgAnm60QTyKKMJHH1fxhBEF6UheJ9S4u4XGPRx874TdlGfHq96MRG8l0xf/HWf7lPiJEg9rM58RZnIwV0P'
                'xL0P+Rxxx10Hgb04yrcRlN1WuVPRshNaXMsxOfURSNI3BJV6nl4CqS5es44L1EtACrL8VTeB9Am2In2op24CqS32T/hKPwEu6iE1'
                'Z0w3gcddnFEyo34CqRnuT+gugABufiWndhHRT1AbdxpyF0AAN0NK9VYKIOiBTewSQJAJYy9eLYIAF3b4WAgBLpItQAQBziddSgSB'
                'F+YlNBVBgPtQ+wshwIT9TRVCMA3jSxRCMBAG2S6EABO6d1AIAWbJPi2EAFP28IoQguoYr5UQAkzn+TtCCBrIRpSecLRTwyAnhRB0'
                'hkEOCCH4EQbZJoQAE++/UggBrqaoEII7MEhfEQQBmB2toQiCTzEEJUQQ4BJ8fEUQYAII74pQW3Jj/oBlIghwatG3AgicHmB7POkn'
                'aI47ybrqJ7DiPLZbBBxAuhEsX3oJ/HE2qsQA/QTYtLRd+o+xfbEH8a66CfBxDy889BLUwrtfR+g1hrTEN+eLy6SPwPILIbLgL30G'
                'qfykJnzROfQQeP0YQzIK/qTDKOg1KIRo1rztxk1QZR5NiEsDPsNsYJv5jw0wLbv5ZspdsVmfibufCzWOG27e1yGd/8tdLNP/y91c'
                'RjvqZhrrakweYqyzNKy+se7eY3kMdVgn/OxkqMt9f2FDgwZutTI0ruLu14b0gHorx79wMjD05OnEIgYGz1yZUJkUyMZNEHlkaiua'
                'xBJ2gtjb+/4a1KgAbagXlsCWlBAbHf78wU17ENm6hdNHfdu2zkcZJaODyJBy30QykUwkE8lE+tchFRO2I5hIJpKJZCKZSEZo0RVN'
                'JBPJRDKRTKR/IZK535lIJpKJZCKZSP8Lp40U6WwimUgmkolkIv0XI903cUwcE8fEMXE+GE6x/4Tmb+KYOCaOifM/jMNkrzdxTBwT'
                'x8QxcT4Yjrl/mTgmjolj4pg4Jo6JY+KYOCbO/xMcialVQo0OQ2ZsPHHh5qOXUcmJUa+ePbh4YO1f43o3KOatH921dLeZx3GVUV7s'
                'n9a9In+v4Xx9t9M14kk8PbkFR2fnclMYW41cGl/VmQHft+c5nrNf+LIGlL0hCv0dzX3CfDmLootj7vk6+wpd6oH/zrLMSNB/WH49'
                'AiawfC2mgdFlkCHXHjGOLpjia2F9rgAKt8WybCxFpqOywRTF78sGU3wcIRtMUTpcNpii2EvZYIr8wbLBFN7XZKMpVlDeF3V4av8W'
                '5XNn9nV2TZclT6lGvcYsvZRIRdGHal870L8YqkaFW6kuCx6QKMrFkwmu98H2tsrXfUs8hsL5CpHgeF1ym6t0HTfHQxQDSAT3W1Nu'
                'xpl+uIOkyEKa1fMZFBjLp5ttWoqleILI1ox6S4kVySqKsniGFxyd1wvMT1ZQrMIyPCrEpeEV3+5AEYTVNcKL8qqRdRa/+8/p2NlW'
                'R4DGHRAlG9Xg+q30wjEcs4qg2I9hiC0ggiET7mVPEnL4wZXsj8wohAKn+o0RwuCO0Y+TcwmhqIL5I3aIOYcOwlB8IYYCUyI10VcM'
                'xVOY4oAYhqyY3+kHyfC3XV0MBaa+vuwnhmIozHBPkO0E0zpmsyAKzPIxSxDFeZhiKO6+PrSq82zplkxTtFMXxRP4YkNBFJiGTXUE'
                'UWAU8ipiKJwwF8saT1FG0A+VgGvmI4YCc9KuJYjiKbmasF6K2/DFDoIoLnDuSAwUe+GL0wRRzIMvrhNEMQy+eE0QRUeMLughhgLX'
                'Yqm8GIrsmKt9xVBIz8Rs3u0xFBsxpwtXMRRDMH9kbTEUNTAUi8VQeGGOejG+Qiikg5g/o5cYClyPhIeuQiiy4toA9BRCIR3DUDxJ'
                'J4SiP25yzhFCkRHnGLTVFEEhzcH9GcE5RFAUwvZ9+MdTAAWuR5JdtrkLoKiGX4/3eumnkDbgOU7l1E8RRPA2h36um0IaRdi7bIuy'
                '6KXwfEjaICOG+OmjkGolE3fhyGkYm/CXZAppBM1ef2VkeYSz3FKg/6FkCgrrPjqNIu749H5NS+fM4GV19c2cu0KzvpP2vyZoIO8k'
                'kLqBNZPMVjSXjjScQqoRazgFoU+QEAqpbZLhFFK9CMMppJKPDKeQsv5jOIXkOcNmNIW9H/djcQwv26HXNL8lgghu9oQPc9VP6se3'
                '7W+M9xK1vKmP4NHovMTd2LnbRW78iOX1KN1clZfEceC/+LuBG8MpMUP/g0xrSsLRX6s5sXsW2y0Po4J/fXD8Z9xBd05FO007iokq'
                'i7u+dVyr/BZJ0h2ZWLPT0D+3nb58Jzg83hb3OuTR7bM7l0z+qWuNnFZjoyhhgCYmuAlugpvgJrgJboKb4Ca4CW6Cm+Am+P8YuG4x'
                'wU1wE9wEN8FN8P+n4KZqYYKb4Ca4CW6Cm+AmuAlugpvgJrgJboKb4P95cPOaec28Zl4zr5nXzGvmNfOaee3/6zURmQTmeHO8Od4c'
                'b443x5vjzfHmeHO8Od4cb443x5vjzfH/w+ORpfcLw+ORFeI/gscja6lhKlFmQI1vDY9HVsMYDA63IStQwNVdniHdtnBZ5NOo4blk'
                'tgql38tMRVMtmKYpPRDjW8DD5XLa4Z534eEJiFoqf2Lg/9EO/w4zXJ6g+Vt/xg2Xq6qG592JHR6qLNVSfDahoszCNwOtnlkrdJx+'
                'QyZJSkXj2zK1pP46DOO7sI2/68Y2vrnENP6AxDQ+pgjb+C8lpvHvCpzSjT/gwTT+2PvWZzTjjzgU36QYP8ex5ChxfKxyjpPG78on'
                'MYx/qCmIhRt//UttwT5wfNy6JqjFGD0+YmtXoK6hZrzt/pYhFeFefmnj4+1ViW4cXTtjWKfy3sb2dvwaWwItvKIIkj5YjrByIv6S'
                'fviVtLSIn2sQluPFRyLeyY9YjpDiIl48fpN6VkTE14WvNvq0kIhPeCyW43F+EfNkAn79yStiMk7BctwLEjDjLTOwHHdyClhWLNiy'
                'xfKt7ALWLuvfWI7rWQUskNaFWI6rgQJWYadlWI5LmQQs9c74xmnnMwjYT1zW4VXGAAGblutGLMdpfwE7oxu+VvWJdAK2Xw+8tn/E'
                'R8Ae74lvCXvIW4Ai4XUAy7HPS4C24nMYy7HbQ4BK5HsMy7HDXYDe5XcKy7HFTYByF3AGy7HRVYAGmQHfT3qti4AW5JnwZVlXOQvo'
                'cx6Ibxy6zElAM/Ws17Eci5wEdGzPfgvL8bdVQFv4nHfwx0CLgN7zQfjeyTMtAhrc58VXpZ8mSfpJCuCrPFO3lcSRFH6K5fhNEkDS'
                '6jmWY7QkggRvxhohCSHBylDJeBK2rol8JAMk40n6SYaT2HpLhpPYvpYMJ0nuKhlOktxJMpwkqZ1kOEliK8l4khOuH4BE3uz6AUjk'
                'rW4fgETe7v4BSAi6tahlZZfHByCR93h8ABJ5r+cHIJEPeH0AEvmg9wcgkQ97fwASzKldIIl8zFcECalVxHFfASRfhhNYTqYToAuX'
                'JTWkOO0nQKsv84rAcsZfwPmkVCjJ8Rog4KRV8iWB5Vx6AWfGEi8ILBcyCDj9FntOYLmYUcA5viiJBWmlZbVIFA4msFzJLMC2UvAp'
                'gQVl1Wa2EhV4QmC5lkWAvSsfqaPSjawCLHd5Sb3sbmYTYIPM84DAovWacFhTc98nsNzJIcAunOsugeVuTgEWboJVyu4vyyXAVp+d'
                'FKdwP0iA1yEbqdvVgzwC/CdZSZFAD/MK8ARluUZgeZxPgE8r8CqB5UkBAd65TJcJLE8LCvAzZrxEYAkuJMBjmuECgcXR38/t+01/'
                'jsDyvKgAL3YAqSmgQ3wEvz/e/wyB5UUJAU5/gmfI3uyvpIDwhXQnCCyhpQQEYvgeJ7C8Ki0gpMTnKImlrIDgGO/DBJa38Uq6wny8'
                'DxFYwisICFgieGrtDfs+FhB65bmXwBJRSUAQmcceAktkFQHhcB67SCyfCOgE6L6DwBJVTUC7QbdtBJboGvpJxHVHNJFMJBPJRDKR'
                'TCQTyUQykUwkE8lEMpFMJBPJRDKRTCQTyUQykUwkE0mAdDaRTCQTyUQykf6dSJOY9oXqRLxuZMpwpgSAdSIo5Z4MjDmThFBeZaD8'
                'TRZCKdemZvQIFUS5iZryK1kQZXIeWspLoijliZSMtWRhlGGU82SjOEpksTytBCULpLxCRTlRFkgp16Jg9AoTSrmRgrKnLJQyOYhM'
                'eVUspbZcoUbqyoIpw4hpa1tEU8qkRN+8ycIpLxMop8jCKeWaWEbv1wZQbsBS9pENoEzOjWG0XDeCUv4dQ1lPNoTyFWaebDeGUv4K'
                'ZCxgM4jyEkg5XTaIUq4BMPpGGEa5HqD8VhZC+RShBCehs14sqDoxD9kpz6yVaSuONEAdK8ZyUFZD/GMoMtkaFbQ7aSgHpXQe8a/d'
                'EYyFbCjVl4uyK+JfLyIoZyIVfC5Kd1QuaHUNY7oo5DGGixJZrHGtRFNu2a6E8lFmT0TME3UOmvUOWtXmo5RWI/59vIqyMXCg4KT8'
                'hGKe7AXUQU5KCZWI003BWBRSenkpuyAuXJBIpb1TVRZeSrcQxJVqDoz+0ZBixkspjUZcWSPhi9CmbavclNnw88TpHqg8cFNKKxGX'
                'xr6jbAarSPyUlRGXXr4rRHIA3uD4KSVUKtnbIkHFZXgb10HZCXHt/Jtrc2W4xr8OSrfnYLH79DGYrUYHJbLA8OrUKz/gNlQ9lFkT'
                'tBcTUzKnnR7ilkM9lNJyxNUx9n9vifqYPYRQfoy4+sI+T1CJceMkIZTSKWT/AFTjDoeFSR9lB8Tlc9J8/PKrj9L1GeJ601h8pwh9'
                'lNIIxPUozBIhgDIwQWbqmSCAUlpKxfjCXSBlBSrKMZJASukkBWNidqGU7SgoV0lCKV2CyZRVxFJKv8hU/U9EUmaOJ1F2Fk0pLSYw'
                'hrgJpyxLoPxVEk4p4RPSE7MZQNkGS7lCMoDSBVtvp5IRlNIwDKN2tBDKTJiCsR2NoZTgHgDP3QyiLANSjpQMopSgkgoJWQyjbAWM'
                'XSYZRukMVIyqaByl9BNy6CnJQMqMyHnS3khKpL78zNVQylKIkcMlQykRZ5+EQIMptSe8JZLBlM6ac2x5oympxaQ0KU1Kk9KkNClN'
                'SpPyv4kyVUbRgIOtnpvgwaMyGwguTzcSPD7IQPD3jXaNAE8uZiA4RfS2DnCtdUgk+EEjweX6RoKftxgILrcxEvy2i4HghDQNneBP'
                'PQ0Ex7di0gse5m8guIOD1QDwmCwGgsuzjQRPzGcguLzcSHDbRwaCy9uNBFcEPwkHP2YkuNzISPBLVgPBEU4OgeD3XA0El/saCf7c'
                'Wwz4dVScnzxMDPgZZNT36/RiwF3vU2bE8YAjY8nk2OxiwK3IKvtzxYBLTVD/nlRIDDjav7xGEHg15JWyYsAlZO3pPYLAS9koUvp4'
                'waUVFC41bvB8iahrzcWAI2OT5WtOYsCzooIs5a5iwKXxqIsP3cSA+yMzOb8TAy4NQV194SsG3PMpwVevBxydbxqZSQy4C7K9zVQx'
                '4FJbpJknlxhwCypFR14oBlyqjzTzFBUDLh2UMcnHesEryZgQB73g0ibUkAOCwIshM3I/EwP+f+ydd3xURffw76aHVEoglNA7SO8g'
                'XXpHBQso0gRULCggiiCIIFJUunQRASnSBJQuIEV6B+kloSeE9GzmDT27e8+ZM2V5nvf53flHP+zMdza7e2dOP+Yhb/tseuAFTGP4'
                'OuqBm2dFnvbSA88ey4DsaQ1w0/h8dsVfDzzYtJlhfz1w4yOzabdD9cD9LjHTKGEtcKOb2by4cD1wT9N060l64MaLZhOT/9YDN/YI'
                'KZaC8IbuhBvr3Qmv7E64scSd8OKpboQbM9wJj0hwI5xYj0USnjXGjXA0ulgZHnjNjXDjPXfCfc65EW50difc47Ab4UYrd8KNHe6E'
                '13YnnFQ1RBpeLs2NcNOcR23wQsluhBuT3QnPGedGuDHSnfDQ226Em2b8aoP7X3Ej3HjbnXCv026EGx1xODmgKqh863dHL9x24OSl'
                'm/H2uJsXT+7/65dRfVqWEypFyRu+VfrMPgoV/rIfntmrko+ObcK6LI/nHgH3lr6RVW2b0Pf/ohYxS93ybrD0PqWnxDGRETuxuNQ+'
                'DTYy8fFHbeF9iq9kcmNpEaF9sk1IYbIjeVxm+kbNrjGVcZValNTve6Y40kaTHrCSh5j62Ev4tupEMx3jZlXeRu0TmZ4Rx4l7621n'
                'ukbKG4aWQn+U8Sa8UTu71p1SGkMb1UxgekdsefONit1iukekaeU3n4NM/9juabLTt4SFUfP6tSyeM9AzKGfJVh/Pp5xZJsEX9blK'
                'x43RZR2X2MqNucn9VVR2uV0v8f6cHr5mIkbPKM66U85RjmPx+fZvAiFTxmjOhzGY4qZ4+hvC7oGG+J8V6xh6vgCdfCICPcIiTqKr'
                'J2ecWwX9BA5l5xzL2dGLJiWjHIP20b6Si3vV5EI1iAx5z4WwPym+IuH6rIRJn0k5aA/tuySRALV3fUaqZb7VRtrJthVhXHp8JnXB'
                'hGCqWIralNs9mvQnMmcGWXTDDMy/PnJzIbaKpLzknfIiD/9dHzQpn8Fpx2IxiemjkcEr1FNLYKdajJOv4nlbta7543EEBp2HEtIf'
                'j6FCOw1FSPev+e7I6xWEdsLec3soXunhuCyodF2EUfcr/u1lEmHY5gP5bf2ZLhIhj8F7gjshIvBtwyiDfLiVBXeqiLAijJaIwuUv'
                'uJMfIm3XNPrAL14Q1sPPMyRDZiT6LQqOP2DYJ9jvZYrwTpOw82irrhPCwEtVLceaBrwjvFNvGLbNQFxSLwvv9CKizRuIANpYeKeG'
                'WFsYxLlZV3in57F7A7naqwvvhJSiu+aJHCAVhXcqh4gSntpup/ujLKJyGCk6P70qMOy6cfeZ/SKieKKTpl/5cezJfUl4p/YMqZiH'
                'nEZ9hHfqhZ1G257RCbsCc09OFt5pIgybaB55/cj4LbzTWhjWH5NnzgvvdBaGvYo57O1+ok4dO6ZLlNN48FVAWHkN32RVZfrpQOSs'
                'O+nq8n6SIUFVV9uQ/vKPiM4tuNMFGHW/Nn5P5MMtr+t2enCyYcL0EKGdhiCk+wUNvO7IdwsyqH3SLnLDJWoKbFSTYWeRwSlx+ZPA'
                'TlgR0ocCXQjyRCVGkDeKQHwvsb788Mrp5J2mI5THeWFdMYNjMeJGxVI4mvv9kQnrj7aFaHXbgjAue5FM2BosiU8dAYWVraMVMeto'
                'xoJ+aPDU5Zx8i+9lRswux4tIH+RasVE3T2qJjHMX4pb5POhGeU4I5PoX5HgbsBZ/DfDaz7FOZRfHcTwoo0APyii7kAfFCL3Mc8R1'
                'N/Nw+/YQ9goZDbieruvfPOe0pszoG1xPVxW5WOGrP33YvFiOAI/A8OItPvo5irBisNkH4Q6P5A5PUyv+be0bReUHzNDaPccV/uPe'
                '8Gfo4dcbtfDms4rEaM67AOrqiS65VY0QMXNYw0b7ipIsxBNU90kbQw2za35daaNIAZNJtkkK0VrfZRGS5kusltzot6KG6Gi4SWKf'
                '9XXkIgWnCkYKTiopHZWY+f3t5OjHre+GqIVaZu+6gh/RGfdbl2w6wkf9qr079zh0+duPzu5TxdfQOIIqtu075tfth05fvp2QlnDr'
                '8qmD2xaOfrd1hUAqQKhcS2LMtYvHNv0yvn+74l7aoBkfxaMz38ivG/rQwfVddZt26H3uVzn1Q9NDA2aV1g9N//1Nz64fmt4btK9N'
                'P5SxddndAGWRddwAZYlt3ABlqZ3dAGX21m6Asnvl3ABll7K6AfrI0qUZypq6A3rO2w3QBw1xtUPPeqFQpxMtKG/ZJl+sucOldhCB'
                'Poqc7bSHX5hVFJo+WuICbXIWGagR/gdK7SoFNbxX4A+AFNQIPIb9VCWhRnXMWJJHEmoswx5VWWg9BNpHFuqB/K7GyEKxv3+JNHQw'
                'vPBPaSiSvLxDGop4KQ9KQxvBC09KQ1vDCw9IQ9+EF26Xhg5xx7ePHFSLZaFeSMzyt7JQ5MtnvWWhqxBoE0no89jRn1sOGoTF9Z+V'
                'O/l90LD8uVLQnBsY3rBUAtrqhu5736fTPxwJZbmIhBIY8Vzjz9fwDZYvP3upT250c4N8et4dknRzN8j889ygnVx2gx4VV0G/xpfW'
                'zg1a9Fv6teikF/Xr+9fq67dMbAjXbkO5289Dt7UnbXa4brtU8k9ldVvQLo3Mo9nWd/GHWlqtkinHZ3cppMV+mnT3xuXjWxZ+P/DF'
                'Ut6Sll5+ZxULakEtqAW1oBbUglpQC2pBLahOqFwFt/ibl04d2L7o275tK4Xq3MSncm+4glva6fkf1g7UsU22N5fxI5mS17+XX22b'
                'kPe2kssXHxqSR3qfEpPuiSmBi+tK7VP3TwmN83Anm+g+RX6T1G731hPaJ8v4ZCY9VhSjb9QoUsmskEDNL/MZk8YUx+rslI2K7tNh'
                'zSKEb9a4pdnAB42W8UzT+BTf6K1Upm384IFs1F2reXgCEsWbqnWn9JoNwKgcp3cjlga0ai14nekeSaaFLL33MP3jslltya+YOyq4'
                'LXDdqGaqWyq4sdddBJKzbqrgFp1HrGqyQgW3OYZIywCVCm52x898DnNfBbe1GeeWs7uxghvL+IH85tYKbpufTsxnd2sFN/Y0aP5r'
                '5t68yyeHuu91N1dwi3n8iLzu9gpuPQx+fqeeCm6PKhUFJrq9gltS0IMp7Z5BBbeHbsvZzP0V3GbzItu0VXC7fv8XXOaZVHC7rxW8'
                'xZ5FBbdXDbQelcYKbmPTX97NnkUFty3pIlHiM6ngdtdmlGbPpoJbAaP5M6rgVhtrNaC1gttrxohnVMFtAFZJQmsFtwnGlmdWwe0o'
                'e1YV3M4+swpukc+sglv0M6rXdc5IekYV3KKeXQU3r2dVwe3eM6vgdgur4FZH5y/iqoGoxS/o/JWfw47fdobGCm5HsQpuPQ2NFdw2'
                'Y822Buk8YX/FKqF8Z2it4IbU2f7N0FjB7XOjry5Z2cAruL1itIVfTPQw9FVwq4RKToUNfRXcQowAOybPGLoquF1Nf/kop261Hl1t'
                'OW7I+cfQVsHt/rP5LiLE5tBWwe3+GVqdYeH5hp4Kbin3Oyb5xeGfrqGjgttD09Fy5K2EG3oquPU3eCXIBhp6KriVeWidQ56oc16G'
                'jgpuJx7N+Ztg8TGUKrg9bmfwATLnkq+GCm5pBR5NyoyZAYcZ6hXcNpL+8JTy6pbEliSTBTsapFrB7WQGY+R2bKtVHooV3DJKPk1Q'
                'K/RUm1IFt38d4qdxH/s8L5UKbh0dRXe8wMrmPPIV3PY6fSKzcTfIrVdtkhXc7M7lznLxyoLtNi1Mx6/gNt5lzctcn9WxDyPEK7id'
                'N+mJOIfgizs19d3GRbILVHBLqWEW5nPGDR7Jj56NO5exZZB3X7OLmu3OBD0Z3fRudDrMkEm1Fh8XChrGM9nq33z4Ydk1RdNGR7k+'
                'v2b3tGz0O6H8VMXTGjYaTVK9An5U3ecGubFra7VIiVUCikP2yfI/jCuC+l0xyQi0pG/E4xNrrRMP2kqamk8qgq/IWMGqmbvzGrLD'
                'v8takVqMKS1VQi0D282m/xLjn1eL6/Qo2em7bbSjI7qserSqZ5GGXQb/uHbvsXNRMUjAYmQhQ/NoBu12Jlz3Vq9Cz8DBUN1bgaab'
                'v/x1bwXemiu9dG81Htpqrk3zTra5mJ9Y6/BarsOOQXOrbmZIJSytIxjqhmZvr3urMEgfTKyve6sIKIDgbiXdWxWHdKgbxXRvVRFy'
                'LF3Io3urulDw39EsurdqDalDOwN0b/UGdLCv89G91fvQE7zAQ/dWw/AeGoZALr094e7NyFM71/z83UftKxK/acns/6u/j2if1V3w'
                'B5bNvaNquA3+QPD4soD74OkBiD+Xdh88/eOZG+Y+eLoVrYsb4YxN83EjnG0LdiOcbfF3I5yttLkRzj50JzyxjBvhroFgWqsL1Xcn'
                'fJM74WkF3AhnX7gTvt+QyEm1+WUuVKvzmO08K6w9VCHhNUsfjomthVI2rVf/ZFoLI7lU3ZfsvEhplTxgxHfP/lKFexzBophUM5iR'
                'wKUbynB/2EIVr557vRleZFOGw30j7ervvB+4Jk4d3gUNnVGEv4QEqCrDuxODRaTg/RnWQV0RPhZNI1CE72Jw20xVeBB4Z5xRr44A'
                '/xJHK8O9z1KjbCXgsDvub0MV3o3felAW7jsMvuV22ZTgYR8gCSypVQ0puM0ntNDzb4zdicYgjHCjfL7J233wE1ncpxMdD3efNvdX'
                'mPv00Ak+btOgLzRxm+4f96W/u6wW0SPD3GVv2dk9wF2WovO8yhJq7/zIe35utHGxq31sbrRxsY0R7rRx3anjRjhLaO1OA1pqe3ca'
                '0BJruNM6F5nbnda5zZ5S9ahsQXme6zByS5pExRTy7Z93EF47Iqm0UiWtLJPQd7/Dplamq10Cr8i5ilDUEOvRey1YscAY1imcjVSt'
                'Xob1nI7PrQj3wQJyp6qK0OURO1dyPlX5fDz9rYvDQ5F6S0kRqmrL++QCQxJwPySaOyGnqqqIJPywMapwv6uIcBemqp5/iLz1r1Xh'
                'mZB45rtZVIsXDmSkjGw5eDASC3cnRLXsIlYkYpAqPDOS73ozULVgJFbv6GNVeBgS9R3lr1rqEmsV31cVnguJZ7ziq1qkczLy1nup'
                'wvMlc9qeKJUXncl4CXsK8MLIbfqvp2ph1J95JcdU4CUR2fG4h2pJ1yUML+2gBMfSuA7ZVIvRYj2t2qjCqzGsSoVqGV0sP6uZKrwO'
                'Av9buQAwVqCroSoc6322BV7mWbTNgO8Xbjlx6cbdZHvSvTtRp/duWj59+Lsv1cwtHrga1v77/VgxrtN/fN+7Xk5yRGM/YnXGm+tH'
                'v1aS92492mwRi/OPXjekCZxY4tnjlIwib//n2xam0HqH5a0DZ01kq59VzA3nXeMw/2Vaga8lMa3At+1MK/A9ZZONI7C5XS+w1F2m'
                'Feh1gOkFfsr0AgskaAb+yPQCI5I0A0czvUCPK7jx9cD0j9pVLZTN38sjIFtE2aZdP5+3Lw4F1kdoKUtfNgsotBV6bcLeFAiI1Aab'
                'heVBBbaefNYUCAbGRDfhB7l/ftgFmBm6Qe7RSkSVGHLeEdhMucyGR+PFyRmAH0Eio8g1nn3ItSfACUyl+ulTC0u3VY/+D+ooWkI2'
                'Fnw/8Av0lAWehopcyY4rlFAekQH1ZA/WDWwqC7xKK7hMH5D8kVpREggWNDmRUw4IF7w6XUoK+A0iSX+bQwL4Oura+6mB8BNTjHP3'
                'XJv5cpgQ0MavQ552fFavyr5k4lzaLZm8b1qPCqSMmHYCd2/SnsndyvCSX/xuCt7od9cPb4K67kdJiAlJmwaVgzUxSeHrzDdVNL7F'
                'h+Poh6Y/qRCFFh9J04uaEJuqSF32hYXEPEeU3HaX491zpaJs6NIUIdNWNaJ9mLMe7r9KUYBd6Bzs4fWdInG9y4Pe7o4acbHLQx7+'
                'ixpxsIk3WalZRapZ2fC2Kn1kjpkmUddeLF8moo/5YZGjr+xfHgke6YX6/iGlsGGFLAIbf7U1URS4jXM9+FT/8NfLIsA0SnGAvB2+'
                '201uvkTNwPar1X8F6UFaICASeFT6bCfXcPevoOAS8fFJDjGzqCxka/EPCqwsLq95vIP9mqSS1Vsk8/1zhq5ys4OlgB77iIH45NFd'
                'oKgYaeRkpFAEgQGGfXwpCTwG13OXG+C38l7IH3VkgGC8eIfQ9CDjJsK8LOCXUjX0geupk68YsDMIzBH6SL8ZllvkhNgLxlPZQp/2'
                'BmxBrk3yLpJTFppRDRtPqyveNBnJxwh10pJH1eRm9fdOxipoh7r82/VZr2JVHepjpTZTs5kAHzhHZnWrYlYsLu/bOxgndzYUFnNP'
                'Lx3zwcs1CufO7OcRkL1AufYDZx0l3KKhTONIyKoZeL92gk5gSgHNwAddgzQCb2TTDOxs6AUuMvQC92bSC7z4+HHVBDz1xMqvB7j3'
                'aXuzgEgNvAkZVVGPBtNvq+EiW7gI+y1nXmPyaSimxe88qn11SAYXPQ6p35jjlWmCHuEDvbi1bfK8NHpLLM3MsL0ftdqaR6kOQ389'
                'igZir/viBWHLuUfu6h0+Hjd31Y4TV27eTbTb46OvXzqyadGEz1+rglajbMPcOTZbeAtv4S28hbfw/+fx/FscbtcXZWgYFt7CW3gL'
                'b+EtvIW38Bbewlt4C2/hLbyFt/AW3sJbeAtv4S28hbfwFt7CW3gLb+H/P8SrFfD5DFx8xAJbYAtsgS2wBbbAFtgCW2ALbIEtsAW2'
                'wBbYAltgC2yB3Qgu5Cbw4bwwuBwfDPf4+Cc7U6nE8zW4eFswDK7JB38LLl7vzZC69twxHVy8ykjFOyzgYym4+FfjpkotIbiaxzTj'
                'oEqBnfMM7sy+BnxtCZfrmYLU9pgBPzyGQhnN5saX4Gup/jxwR+zpQqqB1pD/GacFGs8xYpd2kwF/8afTC//BWfzbOdxcacjPGKwh'
                'fP/vKYiDP4b/2M/SX4Z/FuwrlGs7hh8HSPO36FAM/BJSYfJ+/YisSKX6cQjXH+mHsNHA21QzO1JB6nt4Gev/YMYQZMbNYoZ44TLG'
                'yj6YUhSbcr26OXcgVq3usMFvBcKSh5n0Ny2wFlvy5MDtzPCSI/2dinpUmomXAUx83EPMn1fsxL7jm5crhQd4eIcUqNtj5nnObDbP'
                '0Noq4Omp+LSQeECUTvAsg1J5S3wkZexI6HNYH9ixMXa5ZF3cA05FNQfp+iCec75wN+kBv+fyMIVq+ZjHmjz9uS+qcxeY9rIpfkGV'
                'uxSohhr+jxp3HFgJLmC5AjblHewe6yndAeUwp2R8vvVyb/crfv3wVvuFsfb5RSmhK7YXD4odk4tKksNiqkyJpmKP9xernu/30sxL'
                'hKZJI6rJhPOUeHfuAVBkvLX5uw5ZFWKFvEq//MHonzcePRd5O96eEnvj8r/7Vv/45dtN8vAWFoTlg7Yyb8TnDiKBwnLGUpm94OL3'
                'afmMrrAQkVlir6WYOBkcD77aQ3yrULjO7hsG1qNwq/hePUDYvUC0jVtaPuG94G//QR8Oj8tCLcHxQxP+Vdc38Ir/R0X3grvSXnx4'
                'E5WEz5IKgnuBLYTY8Ecz9gjJB4ZUy8fHV8A74IyrYs07xjC4zeGjkRXWthuJbIX0nXqb8LDPFdnrBcoR1BqcFJtJYK85jFO28/7w'
                'htszv0rfyv8uYiCiaMq/0/eCbUZRGQsTV4TloOzkvVYRzXxHBER7YGRL4ej6fIPObupe8FO633FizlTuE88bO0HC+04zYdMnscZ4'
                'YfpXDlunztD2gk06K10ejmh5O6aB9PtKHy+6zIW7Bk6ibFUVXH7btTh5Ldio5U3Y6wehtwpXc21FkIWvg6urmkwfTDk5odEcXHzC'
                'bHp+UC5J4Nd8hXu4DDSdv5lJ9/MLBNuy2yNMF7zFsbYi4w2GFD03G0Hwm+OpO3+Ae3UCVswDV3yCbxUOnqaxAcLyAqdh4ockM6Gj'
                'HAQrumUMqc4LrK6EA/MbVGMGl52H+ysXBxddxloEjJC6j3aDqxogxhHYGl0Y2auP+Jec3v9IrtNPFlDajoHdfFMlW/bAnes7gFYG'
                '0PyfEIKbvOg3+ePRVrZxkDd4DyVnE/4oeL0vx4u2sYKtDJE85a0CX10ziC1vRnNvPdg2XkjQkc+PDemH+OpNRgR4m+/lSw7w/XDK'
                'bPoAJaXjdyGJCPzIkyn9MzuAe/3gOrkcOPk3ksEWlLavewmECdAsndNIai/HynCT1NbTqAnu9Yvz1Ibg1AmGoaZyxAc5zZzNVBuK'
                'fY7aNklWhmPqVsA/qT/Z/mTrAegdtDv6uMEmmXZ696Y3wff7kYOVAXSyrqNbYALvkcwHfXRYloyfQEopSrPkGH+BvRpSGrvBoYbT'
                'hayOoB/2go2giD4vZE2FRdmncS1gw8GzNkNPz+Ufn/jrwClDBK3foHXpji/P5sgLnBKIx3nU6dDrmjY3TGZQ2l72cEIz8M10FfbC'
                'LAYDHh7apOeDl4F4P/eW4PvuiVsZfpbwgF6D28+lj0563AePxjjwd5Y//dV10KtXPCT2gkWkQZgUOVLKjwy67Y8bxgfgGykptddH'
                'IK+SATYn3CPnH4c/p/GwweAdSWf8atBnMRKUrGWd/y/DPiatvvb7w1e8L3Vr6YiGKaJb3fCW3qu66F7fKYRqnBTcq4LCXp8JxiIp'
                'bGXkTRPa62OVvYyNQtFFOZX2ekNkrzVKWyHStsnoqLYX4jN2GdF+invVp+81TXErw0aPeqypupfxFXWrf5W3wiPAmUhmA2H8Tdvq'
                'gcRjuK3UFRPsoUSQthNJe3XRsZexiLJVXJCWvVpQ9vpJy1aGFyWYvaGevYyx/K0ueWjaqywTjGRXGQe4exXXttcHvK12atvKyJ7C'
                '2auXvr1gg9ojtTYLiQJayIfy104G9+bfmmBm6E3bQGmXOuY1qc1d2x5auhwOAonnCt+Z0xTCO0HvVj/DFzzOqykcmHwxbi+y7VZp'
                'oXckIoLxjrigVOTLAcWUFby3tJ3JZ0U3hhZuSn+xCRh9xLFB+mE3OE9pHw4tHJb+YrBd0nlYGzuCFhqSuceN0IALziGKJrJdwdf6'
                'JECq1ANR5TsIO1/WDXl/FJDziO0z0ETSS7hhHs8l6YwuHoCbB8JBbH4FCWSanOnpJY6rr5MhFUL62DaIfMKg0eiRVj5T6i9dwJEw'
                'ssl8wo9VtC5SrsfLnLfUxpAI7plt8MJdkb+0AE/m+1bmE37ic4iU+Es7897SLuQtgV71Ylx9a4yMX/+xcRYOxC8Ixh8Y3OxcJIL7'
                'GFcxqCdurlrKdymkQKGJRla+dW+wIVwO5MOnx0SMsBbZmq+q/SFuha1MiFEfKl6J4smI9RTVBO55ES71jeIh+U9HRVFNYH2GSc+L'
                '6gT+lNzv90U1gYzOZGGdoJ6JEOryL4tFNQGHX+5fgjqBa6DMv/OoheBBTSAlkBQosIIaPT27p+viImKagKNDryk07ZapTuDpGiTU'
                'tSTVljeMkQqLhNgpMSkGkopUzOaadzXTEArZb+c4bz8/hy3D6Osy7ZphLGOkuEMfMLU1OzHB42daFMJS0zD2HCZra0A7naT6Ri+a'
                'vSVXaeYDw6gMxn84jP7QTjOcJuYEDzyTfNoipreTV6yrD9sQyGbrQk62ManH1cX8dvrT5Z//EdEEXMLeZ0Ezp7piZ5jfTq7nZ2qg'
                'y9oy9A4bbwnoBKfM44frui5+ga4J/Er5fUA6QXYgQ8E/iSDcLBCoq0bXCdpD0ucOgnBzWUCU+ZWsE4yDZHTXdPE4b6omYCbwvUfW'
                'Cf6B8rhb8GO53xARiytQdYKAFCh+OtSOx6MaSMaimcfSM4aYXWMSyhkGBjQtc9rlhJCKtZYYzDgUTgic4Bq6QtQEzBVRsOLRBsd5'
                'GxgYw9qB53lqJ+Y1As2hjo+NVxwcBZ6LcdKIxokZNfySSCkQVbA8kzPMtHIF8rAyNAxqG+zWMLA4uavYTXnWIZ4kVdBs9DXs/Mkw'
                'lmG5siY3ZcYQ+EaiZsRmJJ3gOpYYUwTPLRsmaoIk6QQmgYXl0ZvyB4om0Fk4dDODTtDN5cW7nuhNuZ+iCYCG+wkEncA1CGmtgda2'
                'swfzNYEr4tlJGXSCM6bFMzHrWRO+JgA7gXKBYlxeRG2ow3FjfMV3kCOusjPQmtdg5SrZn+Ps2fIkQOu2hEMRzD2aAqugOwxOqZ6E'
                'x+lYYJnYGMTt2pVbRGg/L+O5FlwnoreMcxoMEUt7FGEc7HojtOQ6/z7hlSAYhDlGojjXoqsjOC0L10W6kqcJ1JbKgvgW8hIf5TuS'
                'H/mtC8iFg/TleES2wD98xMhWGve67EC9iRVxncDkRnidYIp8G9cERqFvyfMuqhPUoBhW9gL3EagJtMTd2utQneATikvaVZi9cP+f'
                'w8CnOYtk4PcG8xthPqm6Xl5ME+BVFq8D6gTpFiTbLZd/7u2KCDPPLhzHvRmgQBJQJ6hiGKVc//U5E8YJ04I2e7j3p3C4zUdmYbJ3'
                'zMziP5oF9sOaQD7poKTfzOqjrDJDuKZfpWWG651cNKTr7ty0Ga6VaQeYIfK7Lm4B17efz31LoaBOUDLC9d9qmTIumaRxbYKwvflh'
                'gIegtT1fdfmnRF9ThGs+4HZvUBN4jv+WJkJr501ippl7BiE3M6keRL1jUygyd+EwNfi3tOviVXALDP7IzegD6MdhcqSCYwAlRPYs'
                'GWeHav4LFGCuZWjNYDloCNf8ID4gTqMbmTdBvC4b8QExyB09GDGjyCuOiviaFrV9jcqDS3ptUHxADHLxHcdxDkZ8ofqAGIJB+4yb'
                '1VFf9QFxGpWIPKTwcSZi8f+JxLfkGUvjlZSqXOkwXiG+JaTSnJO0Ao/Rqg8IufQKaOc1yAn9Gcd56jsy84jyrOEGPa9AKu3JP4nC'
                'qyaZfeFcAoE2dhBwnAyMSZS3VIr+lkYRcJtwxCsExC2b3vw3TnHZPATECkMg15Dw42ykLnYJ5VLzf5ypQepiV3WRt8T/ce5VF7sS'
                'fETe0ivqNQCKac5n5f84X1QXu4YLvSXjHI8Xri52NRZ7S3M5uNN8RF+e+CZYCqc7ozdzMkRrLprW8uaO4hzeW3yEJ6fnzfeCb8m4'
                'jvMoRcjxtmTsZUNb2w/2MIySPzgNqXJJHbOHfel/Q8UUTrZcCFIvYRR5G1+4Lj7b8PAafwG+Du3kC+MbeJuYvDwjU3qUK7GrQg07'
                'oTZAAFyt3azapZkudIokadSE301aA0Op/jq7mYP26V4gnHr10ogPny8ihszkbhOENPRzKpBZAVE2WxjSfWzZ1SzkOvIskuOtaSpi'
                'vPDawyQrEmeGe588Ldf3dJRIYOKVmQ20QxE7HyRUCIzdROSHtkhRkrpmCzy2yEj1Yci1NN58ScFYiboiiBx0Aqpr2ZNwFjqN1xC5'
                'vyr4IcDtOth6UxUt522pXrO57whmdq9m5M6Q1I8hrrCQepFURq7eYrojxSW0JB8iUg3Ez5AwRLR3blVgQ0ynO3nVv5G0u8TS5Lzh'
                '+KIqxv29DsaOwnFMpTp2CNLzL2MwvMc2eN5Gip0CEX9SKpKaON/Np6pPH30Sg1ISqaJALCuKiT/fEq6rVQZxIOKPvRb3+r1Fr/+G'
                'iD//BvAa13agy+SY+HM/fsDnEJMuJ0EVf9JewDpzsEixkpTI538ppGqqghBGF3/mn4BfmyGq+mHij5qQTBd/4O+uvvA2qPijTYfn'
                'iT9qShld/DEXcKobcmOt2D5fS26Dij+u45CP7D6Y+OMykssZ8mMxfZ9BCtug4o/j2OWpsg+l6sBDAaf4s6nO+b7iNqj4k8FUbVPd'
                'BxN/ngo4+Q31QfB1ddewjRHwL2+b3w0tAxF/HozbufTsw3PvxhfVsk02bvHIvz2NZ1N881MN21D8mBwlkTJykuK5Dnir7rOKdu4M'
                'V9ymK/XOrqK0Td4Y6r1wXKXEsW0D/Z4bq7DPuwL3tr229DZF4kTkkDOBktt47hCTq6ZI7jNAVB5tLLVN6UTRfS6HSmzjvU9cjpcp'
                '+/uljP7TVnibiiky+1wLE9zG9yiiUSNOmMWC+yAloK5krobowa8JbVMLEQmaolXJhYQFTMS5nxzrc0CP8IOIbOceuAyeS9IhzL2A'
                'aNT1OAmc6ZUcqMIp5lB9HDbisV1d2EZUhJNPXAaF76kqD62Q2zlDIFxvRHAspigWfk3KtyJYr3Gx8LAPVRv/VEUsTC7vOPV1BcER'
                'EwsHC2jjPMEREQv/8RL5KofLioWJJcV+mpjgiDlaTKPpZkoJjphYuM00sTj4ArxiHLjPe2LeLI6nPq2OhFjYB3pv38FrzgYKi4Xr'
                'waPRHzH+ThUVCyHv6f1RJVVMcCydJBlmNUxIcMTEwpXSAuVPImIhz9FSKpEuOFZKUWh88zFZcPRDSq3+yjep/wWvXuIwcww8MSqb'
                'mkn9daJY2FrRpH4nN0ksnEOTXdZQiu9PRpxKRNUp121+jsoLOlRB5L6PLcC1tAqotgt5guMc4RPXdGSNxAXHVrpMD81RwRGTJQRN'
                'KdMxwTE3Vgp+rdA+vTHNtQ9u+uok4i7CjFtbbKikzG4KaNBY3uYDASMvFgv8s4ZuhuxBOU4Da8zKMtbhwUco8tNmOx4KZjasx9z5'
                'ANpGMxBGwmMPUUHM2jaetE897FP5hBTYbqcYWv2RiA+225MUK8MOEWzUIzFjesYwo6IJSi7Fcpj16TOqUMESeQqu5z/I6v2OCpTn'
                'Ls5jjQ0snznF2ZOLxQBxEtQKxAmlWWHdSKJzyWZSHnb1gHvtReYvlWzzmFrJZEEZLI21HeypvoksM+/aOwRZcTUE2ugXcWeH90Em'
                'qkRh3amRsP4KyHOXZi49BF6QcqqMQFadNE2j+B5ZcRqOVPHFujaYxbxWswt/Bg9HVWRhsmsNDu/DMlUIuA0NdnmIZBifwyVP/1MC'
                'MQ7FsGOLlw5RCwlDuOcYX2nbKvE40H5Ha4jd5tMVHX5EWcAZRvMr5MIExqaGWn7HjWxYgVAmku2Gq34ZjBIvYicjTUMMukDQ/lCB'
                'sRVR6myMPR4BnALJQnL0DO5JWRf5Iq/RIz9DkJSS1PutVPxOKeWrGqTs7oNeaCQrwZCTcfzEsCD8MsjFdTO70EZZojDlYDfTUIbC'
                '4KbKsJuyxSBEjRPIuCPeoTvshsxGb0j4wTtK7CPXBnyZ8D4xEVIbhd8W3Ug2YK6T4D7r3R239Pimzy+9Ue5okY36PIMYKYpeaMiV'
                'sCT7k6jxWHepG31gqI1exH12qLaOtm0i7ZOg3su5ICksq7+hPvoS9tmjI0gTNRSZmHvkR1FuPsdnhp7xMWef/V6aNkINRSbmHvmB'
                'Gop4VXWExqdi5h75gRiKTM098gP2M58wrI2sjayNrI2sjayNrI2sjayNrI2sjayNrI2sjayNrI2sjRQ3KszcMRZYZItskS2yRVYY'
                '891FjivvJnJae3fdKYPddVstVLh/O2Pgf/zlwdUxf9LV3PLgCKy2TIJCLZGA/dhn8ao82IYWwB+h8O0Nw8C/KcQLdMDAhwLlwRXj'
                'EfD1fPLgnJcxB3MtebAf6oLtovDt/YyBxyiA0YL0vys49dtgBb6OBcuDy2AFBW8pBKSEncfc5/XlwT5oWEMvhW9vJtPQMcsQLUO5'
                'XiFkoWkqFk+fRR5cAotmjlYIt8mCZTmlNpEHe21wVyk/tObddAVwHwy8VSEgowGWeXUuTB5cGCuUFvucPDjkOAK2t5IHe65hqs05'
                'gTGOaS4K9Xi8hYF3KpRSq4X1X7sULg/Oh7WXiasgDw48hCkMLylIhr9hH/IQhW8PC5ZnixQkQ7Su7N5M8uAqWPReZB55cO6rmMJQ'
                'VR7sj2V8Clb7Mugx9l8rgL/AwMsV4mTbp7lJYSiPRcRezy8PznERUxielwf7/o19yF0Vvj208dk4BXB/DLxGQWFoidW1PR4iDy51'
                '100KQ7azblIYvDdjH3JvhW9vGgaeZLgpRnyDgsLQCFMY/lVQGIph5dVjSsiDQ09ikmFTebAn2kf4Q4Vv7wcMPFMB3AMDb1NQGOpg'
                '+fbnFRSGglgKXKxC5eagI5hk2EYe7CGW7EQd1chNp8XJbzA3kasnuou8grmLvMoiW2SLbJEtsgKZfvB/Zk21pj7TqWZOAmuqNdWa'
                'ak21plpTranWVGuqNdWaak21plpTran/A1Mts4c19dlNPSFW99gwKas/gbKmmuOaS6TQNaeoKlJBrSlMvMNsE8c1RylrfJzihotQ'
                'Fi1g/CZhBl45dDtlTbBj/KM9hyHen74HZc3bTLxbY07HOK7EIMqinY4bvWyIJ/7OJ0V3OK6JIYUanJDo9uP0EE2WeIiu2CQeoqoS'
                'D9FIiYfohMxDVFziIRog8RDtkniI0nJJPES9JB6idRIPUTIpzu1viXwzp7i9RRIP0V1fyiKnuPhmhngI8jTKmqqOa6IoEak2pwrl'
                'NQ3x4vOjDfHq7qdJUX9OpYRLURb9IlG11Clj7x9S9JJTJH6ERFu3dwzxnnOkEtDhjg9RSmaJh6iTxEO0hLKmqOOae34SD1EriYdo'
                'psRDdMNT4iGqLfEQjZV4iM7KPERlJR6iLyQeov2kh8hJoM9PWfQ7E88Lcwq73Ex6iBzjr1NJfR+cmrO+SVnzieOa3yhrijiuiScl'
                'jxyT6EY/QqJ/ZRXHNbco0c42pxzkeoZ4Xt/3lDWNHNdckHmISPlQ85l4GWinFn+HZR6iQhIP0UcSD9FflDU5HB8ie3aJh6ibxEO0'
                'SuIhSgiUeIhelHiI5kk8RHe8JR6iFyQeookSD9FlisLm7ZRfUNkQz/MnFXx4yXHNMcqaQKeHqChl0WoGdJJERnfHNTskHqI0Up7n'
                'dibQr9Awrc2/RqKEWBKpksFRJtay+v74irkU3uGOyhJWD9slibapE5l4w2KnxsqRMg9RdYmHaJTEQ3RS5iEqIfEQfSrxEO2mrMnu'
                '9BDllniIeks8RH9IPETJoRIP0WsSDxGp91clxzWxfkPIZvh71lRrqnum8i211lRrqjXVmmpNtaZaU62p1lRrqjXVmmpNtaZaU/+/'
                'nGqZPayp/42WJ+dR36UgIynUkD+qx7qpM3M50+pffdXBxc0ri6Z1VQUXgKqW2zuqgXPDZexSWqqAw44hP6vEBvLg0P34L7aGLDhw'
                'B+dhiC4vB/bbwH3ObpSUAXuvJDzCVwqKgz0Wkk6Hc8LVVm0ziQfPieyC5O/JZ9rBzELgEYw+dooUMB3IRMYmeo+Nd5jYWO1NBL8J'
                'FW/9Faqy+SutJuhLQJ3H222NwnsA9GyKC7k5UClwe970F33GAH8PIRmmnnkVYvuIR/FfzYAa09yrsZp5h4PIpydmTuA4GYSDy5qX'
                'vFyb8UHzGGReiv098Usv+ROn76fmBdOr8S0YnN/00jvr2rols2njFHsHCJzrjNn8habh973NvujklgKXXjyUhPPcMfLVGLrPZOoR'
                'OEg803Ti1RhgdulNQ8+ajjGUq9Hs0ovmlUAvYNJD5UYJ/qW3swD/rvwmjXM1eixw/XV+QzoaG19Dr0bbDJeXrzUmHrnhf2BX43cu'
                'L66n18W3DXB52A9kNg+dSBcGBwkV/a52zhnwd6B5H8cLovJayCJnxEY/s+4USzIbwqNHvOvV+IbT7yahj5QQWMq5AuwiT2YNa1jj'
                'v2SUvuF6c5c2eZDL33aZd9QsI6FKDK2Yds17LvNeN5tX16UjWqxp4G4jl8TxA6apey2SaT2j2rncEu1N573iXMI/2vxSdj5P2S7z'
                'O7Z7Gq3T2bvOd3YL83n9nObdBJTXz5zmbQVUmOGMlqTuVEfb3pCmwEYB6d42pyr+fwL3sm0OzXDm6Zj/lAo1tPBylLEvQRlC3o5V'
                'XldCWprvOkZKyvDf5CB4g30bAxz6rJ0FU2mDHUTMxaYfSUSNVm9+9NWURRv2Hj19Ier2vWR7Qsz1Sye3L5s2vHvtHNQbP6JRj+E/'
                'bTmfwjEqbRvVEs22suVv1m/mzhj6QZa279Mi1ARv2jjQ3U8jLb0dyxchGmnpynEnnbT0Rz5CJ41dr6eTxlK76aSxtE46aSy1tU4a'
                'i86vk8Z2eOmksX5aaXcy66Sxb2Ha5U0zP+vcrEqhsBB/D0+/0HzlWvT6flMcSkvIbEaLWdW/kXm/De96P2A9Vvq60A59UQU1Fmb6'
                'GOYdc6SdHURo7JNnO4ir8pSWtqwRrQma/0bGa8/WYA69sUyWK5CJWUr77AS5j7LK0LwiAZxcf5vpTGe7w54Mbl4uPl4AaMelaFUB'
                'WrwUrRL0i8uslVYa/MmXbt5r5JwVWw9fuh4dl0I8lRqZyYJ1By06YZc541xMvPn7b0yQPjHfcJQoe/+tdP5mzEIMG35L8TR/emB6'
                '9Y1WvhuepG8WP6hBdX78oL4Uy/TReutR6x/SeqRppNVNZfpoYVeZRtpPTCOtfJpO2mqmkZYPPy0i5w5s+1zerL6k822AMRRBJf5Q'
                '1SZyWg4wDsOw+RGCZ++AMPA7SBsIncu1QNrL4DsbIa4xDhgGvXLIh5rNmoG2AHoFKYkA9igbAHmNsWzTv0DaOeAFpLRTCNi9eMAN'
                '4IUtiOcdfhbigReQhPa9MA26PPeCsBbIcwpdercgZ5L/KYR2AXqlhkQr9AGg+D9NTK58SAMP3lTTroGd0CtkwKfgS6dczU+2gfg5'
                'PaAO/NpR57ijfL/zzl4/pDBp4hcZlcF84+L5Jzna2Tpp6Qc18wZ7BuRvOGhLGuVeeJnpvGV8I3XSnJPlFWmBV0QXTcUkh5cEYZMr'
                'oTLSEiHYNm+cFnxSAHYsu4HToDBNU1gOg0czylBl++PhBp9mlD5Pgq0ONSg0I/tfBBvglzaDRjM8ByRxYEfq8mWkp6PYUtT894GX'
                'IUJLV7EXQM1hj/QOIslvjiPHu+tdgPY9I2pJx68G1P5oxvpTN+LsiTfPH1k/6f2mAm2MQclO/u1YSAtpIS2khbSQFtJC/rcgQxq/'
                'P23rscsxqbFXT2yc+M7z3orIYv23OLsoYpa9FSCNtDVdB4is3xeVQzY8CsvBqZPCxJF5FuGCenRvUWQrvudheRYRpMdwio35Ujk6'
                '0ncFTReLqUNF+q2lKosJLWlI//V0bTahFgVpWyyibt8uQUAOF7MHnM/MRU4UNVgs5iLFRw/9yPj82pFsqX7kowq5WpFHbURk8poP'
                '60cEeQZF1P/w92R8alsSMnZwxsSl7INR1+NOCnK1s2k1fA02vQ4fOcLVc2T7Bpn/Exc5XMwNkp7zE8BBLjEPb/FA7MCdcOQ1yKAR'
                'DgfwrMSRnUGB4j34B+KFIU/AsUZ+sGG1JoZ8G5F7BoOrvkCQcVh94QjQBboOQS5DxbNdoEMVQeIly+G/PAxG4hWp64PrGoDIO3gU'
                'VzAohvQEkVs5si5oxh0KInltO8BE8h9B5OeSwVdsdS1KYIvB74r1dOwCke05yH7QwkMgklfKuhfoYgOR9TnIrqAACyKf5yA7g6fs'
                's3yXbvgs3fCNu+F3+Zns0/P7s3zG3XAS3dZ/XrrhVHfH3eOGG9IN9zgqbXwuJW2w43CKry8sE9VCJbdOMpKbN4qM0i9fglLwamkp'
                'mLFhpkhE/r8XyNUovjLRKEYh8+cR9J5VznpPDjRUry5FO7vroJ2FfX4Xm7yLqEMmrf6gbp5Az8A8dd9flaRDhxTSdD20Ixtp18eX'
                '6bdtFNCO7MmzwEwSJS75T1izatmWaLe5GZk2MM2WwfSYunVUYmIrspV1JY0YU5duC/b8mmILvlxeyGLdhp84uSKroF0971LOH/2O'
                'hPW/yQnE+j85TMpH4dEK+DnF/EDq+WQ+Sny6zTl68e7yroGG2ght8uH0bSeu3E29F3lq8+T3anvLgrye6/DR2IXbT5y/FpNsj79z'
                'af+fc77oXJlePSui24y95iGOqcdmdeE3nLPVG3uM84s7830j7M+L+Pws6eG6OQXqvll2mUA2zcmPsrkSSi8WDP6f7UwI/F44o8eZ'
                '8cI58dvFkeH1ncwN5cDIsoGpMor/y1QZxWRDUZ8yCl9hqozcF5kqw3s7U2Z8x5QZ7ZkyI/iqOmM833GydczrtfJm9vUMDi/X+oN5'
                'p9KcGc/xMu/+fMU52z5nt+XJDoxlOGG5eaGxsI9OP2UURZ/2y3B3Rs9XDj9mTEX/jGzYqevR7doDRlYs+28RryVe8IS0dEY3BLGG'
                '0N+17mDDQGSu40G0iygL/MWmVDbU8n7TxzjqhTgF1vKyURlwluFYKiIQTpkoTmXUBhH7yPLBW4IKv9n4EmTUIzPgVL9QMmMrqP/Q'
                '5S0wamULnQHe8z/TGdcgxgQ6I5ZQS4E3ksVT7NzyPnR8Hjq+Fx2/Dx2/Ux3Pi47nVsf5oeMcC7Srn6c6znXk1o8h3y+dmfobyYrc'
                'txWpEOTeP0pVkTH5YxWhoHKl9ErAWZEsPfYLT7n2/CT5vjw2DZPH1uJ5KzUPPpTpiqF65EXEWVl+Wdpj+XQ5x/5nXlfFu+2aDDJu'
                'WV7W/rqOzm4a/xZTrjnK6/wq40lbRr9aIyLE2zMwe8mmb0/ak+Qi84coZRXONm1ZLKdH/aCB4fO3OsPIc1mdYRSNVGcYJa6pM4xS'
                '59QZRrbN6gzDe5I6wzCaXlRnGEGT0pQZ6U/xb+oMw6iwQsA2dfpj4BrKN4SWqXn7x3qIN93WYPwJDuDcxKb8Zu75eszanwTYLWe/'
                'VYR8HXuXfeXj8b/+ffLijdgUe0L0pQPrZwvZT9FRnBEqqVlIC2khLaSFtJAW0kI+S2TZrt/+fvRSdOq9qyd3zunfMoci0rPVLGcv'
                'UdqeIeXlkdkGAbL49pc8pZC+/ZEIiXPtJJCNONrPmiKCSO9RXM0hvpMQMmwnRW6f6ENH5jtFUya2BFKRJcju2h3BNGQuATVuVygF'
                'GSxUPXK9Fx9pW8uExiQ+8hNRtXMiD1k5mekaj5A+J5lu5ACmG5k7VjtyNtONzMdxh+8e1rxIqFem8BrdF0QTkaiZLG1uxvq4mbpd'
                'oiCzYrW2z1R1OlAzfUdAvou8/pdJuf3XUrjI3fDLf5smzndM4yCLwq9ezWmQ2mw4IwfBr7aBIsQO4Mgt4Iu/g3JDDRQZkMSvNe46'
                '/sCQTeHrAJGImmHIL6XSLDwvI0jQcG9HXTsTEeQ5JlUZHf7L+wWlyblbQ8B1/cqDu72Mi6zgPdCvOYjk9I4FSwP0A4uxpvnhSDDl'
                'oN8XDMyPwcfbIBI8fg9xkC+CSDBtayMvtAdEzgM9dhxkZRC5mFMcAFZiQCRYHGMhB1nyWb5LN3yWbvjG3fC7HKL/6XHDM+6Gk8gN'
                '56UbTnU33D3uuCHhexzrQ+9xWUra2I4gm0rKRJWl4ivcIrlh8mVrSL7c/8ylYFRWN+tOaHTgyepIgmZ6xrGJRvFqiqLe4ywK+49X'
                '187mlHLQzi5q0SF3DW1aKNjTP0e1bvOpOqQxh+nXx+9pRwo2pafZNk5pRxpVtFtgDKO/djuRsDVrGsXmdkiEuMWbYhkUyevYn1W3'
                '/XJfFqqVNT/xp7QnM90WnJ1kC56XSchiPZprsU7pK2pXb8yxq++sIGH9H4BY/290t8n5KD4Dfk6Hu/vLe1Jaz3GJ7zo6mlc+hTds'
                '5bqPXXs8vcpkXNTp3T9/1j7C0DV8K3f+dPLKfacv34q3x924cHzT7KFdqvpI43J2nXHA9MxL3Dm+ha84r+yXe9Gf6N0FLwplYPq/'
                'SXmMrgwi95sLGnKHeHzEjyUFcPu+f0Pg3LzRix9oW0s0rW9fMc5bHC3eBO1eF4xY4LDUnTgH/u6ryQZI/gGFP78k37Btt3nvyRdV'
                'GnTtM0vPapTEVMYfrp9n1ThFueUnl/j1S0x1OBWVsa1SF6/iHWOzP0Qnnxj3SoUwP8+goi2+Por1I854jkYgH2TKTIfKsdWQooYf'
                'Z5i3AFF8XB7htrehudFhhIQN9qVJ1Z0C4MkyyeB2q2Lvmz4UuaD2Sal5eT0xwByKslCWwahHE36BiGvBWkOQu/b2QzU2F6SbJcEh'
                'rt5ngDXdH7zcF3qTow3xNqMbDCxhKRFrzRkI/JJT7mda5ICuhl/RK2UFUlETLATXEkV+AKxalP7aTEic8JIysl4y4PyxTZxwaOiP'
                'y2kEQx/lN5zrmYGOxnqS5ksDuqm+RLOAJC+M4bqRWzQ2nGSPM/q26kameBzVjWSB57Qjs1/Tjswfqx1ZMlk7sqz+d1lO/2dZTv83'
                'Xk7/77LcX/qRP+tHfgXZa+XzTHpIOqWQ0ZBJFi+FR5Y0jsQkMU5KBIJwxlwAaQ+TRoIuyl7SyAjowzwg/5eDBT6bSyPBvo8HvQRJ'
                'gf0HPTKEpslWrHUG3mDjH/0/6IlMaUAH5hp+M33FeK7ac6cSEVhp3sML5zHS2AMyYxoReNn6PvHOPUHCDm1m/4rjJg/usCzDjfgE'
                'aWCq85lXYeNSwd7rHG0NT5GFElHBaahJFrRv2Z4/u/p1x1NKxT6SwOd90qJceKCXZ2BY3vIt3h628Ki5/pUB6bFezyUxPqOR/op2'
                'pFEzQTvSaJakHWm0TdGONNrFa0caFS9pRxrhO7QjDa+BibqR6d6M7dqRhq3DMUle7KKOUJEpj9eOi/POTWmJH4O1Z4v4om+t6FuM'
                '4gJ4YwGls679+E9vl7KRbyiPqoOWIaL8lY2T36kZIHHLh9TuOnjqqn3/XrkVZ7cnxNy8eGjLbzOHv92ibJCk2GAr0W7AjNW7z924'
                'a3aoFEZWFuu/Bo9LABeHfshXSYDFod9SfgLmi9+6SfrdmC0OWkD80ZkszvoPk14s4IZ3WWxbweQXf8DkFwtlcDgvnsHkF4cnKiz+'
                'jCksPqiwuCBTWPwmPDHxtx41cwV7IE8wXLZjdR7uwbGNgQlY/FMHigJMIxSF8oIMq38Rjrvs0LseSVicj9fuTSpNtANhcWnR7JP/'
                'i4tflJaMqlmLrcXWYmvxo8XW0WstthZbi63F1mJrsbXYWmwtthZbi63F/+cXO+X1jPn92MM6brt++rRtHkNteLWdG+X8ng6NrCEP'
                'DB8KeLQPdPGVypEK+AJxv0R1kcjkasOpp729nCAy01Suhp/cRwiZjxRAN9efjixLbOq0m5xhWDOGEcfezDRkaWpmFHuQW0lA5hMK'
                'r9hMyCn1P6w983UGExyTeMjXGdOcRZwjWjtyHtONrMu0I/doRzbh/bC/alEkxDNTeM2ei2KJSDw0dlHGqpxBfSIpyKrYhIt1nIPt'
                'phGQU5DXd5lkT3ZJ5SF9kePiH9OkvNd4SKT7RGQuQ7B1zkPkXPhVKB3FczeOjJTo8V4hDUOWhQtNIFHGizDk++BraxDxoTqGhD/K'
                'dphIchhBgl70ODRgeyiM9ElGerVj8aAwsgT40gBcuAMzCPs1YlgbdEOiY1W/LiAyHEeCp0c/MEDiLkcK7QciwZKTJzlI8Ozo9yOT'
                'jA54AUT+JFsorMr/50XXfmW8VujC79INnyX4i93MQTYAkWBJoCMc5Ksg8lPolescJJjL3O8N8BkPkuy12Q/8SFgFHAnWxOpXjMnU'
                '+0y/d0FNs58XGOc1HUVWRO6evdBLF1DkFwgSViXKYshDCLIPk2lAVw27x4vDnb+RANWFqEx0QeKOLI/KRAZ4rrNoyOziuQuX3FrA'
                'r67zkJMvva6JtsJ9lVshbSzy+jibjKxuPIdN+DO3s9FnCkXvQYtQ3RuRUWAP7H2VpErVwuekrh/QMH+gh3+O6j0WUrUzQ67fGYqs'
                'bNdfzmyKfmSW6/orpLXWjyR0K2eiFdJ8dosRpxKsWTnP6rZmGUYRga8o3Y5HsgxWukUl7slMtV+WuEAj7gzB5MsPHKPGD1CIs/3Q'
                'i9wpENeP33syqfcjAyo04XXn87U5JwNpW5lHE1tCM9q6nNn+g+6S7OpgeqtZUmL2wcA7PfBWhjybr8Qymj1bu/ooDo+qaVDKgbBM'
                'sCelx7i1x6/cfVghbVA7lyv9omTJYngUZNoTmt8BTyhpJBhl/4osEXwcWV5ZJJi6f1GWWBGUir6XJPodAf/u6hndUeOyk5GzQOLZ'
                'jNM6pks/xIT2MfAhMMQRyVjCVEJ2mz+St3QvqzMy3cD4RwdOmb96WHFMx1JGHR//860pjeGahDXQ8l/xOcyR9+X+X/uUdhV/bWUG'
                'cdx1nxgg8gH2r8nvtqkckdnf5hOUvVT9N0at4qaN7fXEkeIjpZyhG9nb0I2cYOhGrvXSjVxpklGqhvzZLL1JBZn2tamyqYC8BpQo'
                'kEeugqzGssgTzcADQQ55uS9SSVQGua8TWprU6/kR+4RaTUdOrEW4AbK0HrOLlMWYduT7uh7kq8q7Ys+JmzHlInLjmDZZJK7V4JKN'
                '3kpPSN6x/8SF67GpqXG3I88f27zw+0/frM4vlwqq97VkLniLZtEsmkWzaBbNolm0R6NM51GrDp+/nZJ469LeJd92LiJP8241zSWA'
                '8cbMJl4ytLBBQCzk1Y+DRGlBo5ESU7d72URots6ciLQdhei0rKu5UuythlRaTUrdp9RXaLRutGJXKW0pNHLn36SKfNpIukJxJoRH'
                'Gyain8zh0HqLKbU1Udo4QZfZXoI7UGA01UrboJXGimulDdVKO0GjHfy6ZZFQz6AiL83E/bKFCLRlGfq0ZR6JPbhvcWmRToaRalHY'
                '88Ch7XOxiZSAXW3HObT9JiXbW8IHkzdKu2baYGYZOL8USmsu1rGStcFov5hf6B6gjbUXQksuCMgHK0ErOkKbBUkbYEHzyQgN7Lj8'
                'BrRiXi3k1wON+tCSxTANLgIMxoWshGn1QVoeaMkfIC01EKSFQGvW15KI1vMSp2FBjynCNKzeVJwwrS9CuyNMw3yLN4RpTRFapDCt'
                'gURVMZiGdfa6KEzDdJkLWmnnLZpFs2gWzaJZNItm0SyaRbNoZjTrlf+9VwxrGNbvwHrFesV6xXrFesV65X9RqrFmWjOtmZbM/7+o'
                'o1gzrZnWTGumNdOaac20ZlozrZnWTGum1EyXCvn1oJkVnWc2hmaWMqjdJQs5z+wGzczmPPNzYGKyS12LH8kVVqBe5jtdQmDvUQOh'
                'a9IqOKUPsKBrQ6eJoVC9+tQQp5nTIeTfjvNscBng4Q4TK61n3CqXPllKthmBFaQ6nD5pAbmuGWlmTCh15oO/hzLzVhbqzC4GceZ6'
                'gzjzUg7izIRKBm1m/AsGbebdugZt5uEMJXSwmfaJGStXITO3ONZtgWamLnY+skxnxv3e3bUaUcaZafHpWY1Lx/co5+n+nEsLakEt'
                'qAW1oBbUglpQC/ofgZZFqhEmtZODlkGY8Y3l3mmZG4im87zcn/8cwrxZUe4zxZhXS8l9UaWRSmvnCsl9+xjzeB65n1QphLk/TO53'
                'WgqpgL89VO7HXxJh/hkg90RhzN985R7TElH0spFUKMac4iF3oBSPpJZwpUMx5mDJo68YzEzrK3meFoNbD9jfkjyki8LM5JclT/6i'
                'cLPEhGaS1wnCzGAyEYMWgZm3qkhefIUvg8zI5yRvU4R5oYjkFY0wT+WVvPcLwXWODuaQFCYQ5s7MkhJKwYsgc2OgpNjT+aJQHV8a'
                'FK6musBbWkADx48ehnboWBVRkoFlgbRDPzS0Q+3dDe3QlI6Gfugqww1QNsYdUPaVO6Bml7yG3+nH7oCyd90BTevhBihL6+wGKEvt'
                'KA1NI9TLE4YOiEe02uayWnSzZMTr1FBWNe+I1K6Lqy2r7/dCvq3Y6rJGhEEINbqirGXiW8zlWEbW3IF13r5eQhLquRihXi0sKfT6'
                '/IlQL+aXFM8D/kaoZ/NIKhKZsR7pp8IlVZ6cZxDq0TBJ5awg1hfuQBZJNbL0bYS6J1hS4a12D6FuD5S09b2QhFA3+0saENtjLQH/'
                '8JW0SnZFBSJvSVNnP4y6xEvSfjoCo873kDTKTsaos2xyUI9fMOoUSfOxN1qMd7ykTdof7XY/UtLQHbKforqIWnqzY52LHjcmFbZJ'
                '50PrEr8vaecvfgOj9pJ0HlS8iwmaXSQ9EnUTMAXuVUnfSSus0mtqe0mHTCesZUtySysL1XrFesV6xXrFesV6xXrFesV6hf2v1kbL'
                '3e7L5QcvRKfcOXdg7ciXC3PnZ23Uf8Ge0zeSE29f3rd0bJfiNtmwp7z9/nYSw09/WRyZn6P3ZmeT6605zZ2dd28SPpFS80wNIdvr'
                'ATuXXmBu6702MERw7/AFoObxZwWTnUsshjWV6Hc9RPbugpm/Uj51dlh6DsT7T+4uRt47YAnDx4acjn/0Hs58Ft2MuHfEfsbtn5Mv'
                'o90thvGdkW+R9i4RyUexc0+NxN1JzYjuK9LcvQteoaDY+ceJaNTWRSnPc/fOfY7IWm3Dk+RcxpUwzt5+e5mQO7FtKnk++42z93Q6'
                'KiX9jCubwJhYmyJ47+kiqGVGwAmR+eyUJ7a32Kg5W3BBR317XxVdsFff3uKj+n9w7+//g3tHehD2Tlndq2o2n6AiDcaeJ2IPfPFC'
                'ngDffDWGHMFmVeHunTb1aTiX12dJhJ131Xl6t3SLwQ4kzt7XHD3KjblnV9pnDjd6iWgGx6zge19wdmQO4N1RrzktaAi6yq/je0cX'
                'dfFfcPr/ve8iQs0F52ZD9zaJ2PyGcEfQGimx2tjeK00kwTrY1vdymaw4CM3uhuxtL2rm3sFEkyFmEvPX0OzPkL0Xmwrfx+EF8dnM'
                'FjSHpk9A9jYX/ZfCC2abu4Gg6b/Ce182jxUcB+/dyHSBDRLY18J7TzZXeGDn610v8xVQHMBmeO/25qTO4IIVgHq2C5j/N7x3uDmp'
                'BbigP7D3H8D8feDekcLhW1CI0grougP3/gMgVQD3hmKNlwjvPQ3ycUILYg1tew8CSPmhBYegvZcJ7w2FA+YFDQHQ3quF934RsvlA'
                'C+ZDe28R3rsJQAqHFkyC9t4jvHd90b3B2Op/hPd+XnTvEfr2riW693Brb2tva29rb2tva29rb2tva29rb2tva29rb2tva29rb2vv'
                '/8N7CwRzlek8atXh87dTEtMrkS75tnMRQ3p4t5rmEr5yY2YTL5mct7BBQCTM1Y+DRGlBo5Ggjdu9bCI0W2dOcNCOQnRa1tWMWwC4'
                'IZVW8xLjj9RXaLRuKbSImLYUGjVIiSURSoCNZORxJoRHG8YExhwOrTcTKgtQE6WNszPhoBeZOgIMDlzSR9uglcaKa6UN1Uo7QaMd'
                '/LplkVDPoCIvzYxF5xUi0JZVfnriZB6JPbhvcWmRTg7qalHY88Ch7XPx1Za4BU4+zqHtN6lz1BI+mLxR2rUIEQ9hei8BlGZe3qIu'
                'OL8NRvvF/G71ACs89kJoyQWBq3oltGIIQpsFXfzDoRWTa2FBW8B4A1oxrxby64EG2EliMUwbBdLAsKCVMK0+SMsDLfkDpKXCpblC'
                'oDXrQdoRWJjzEqctQWTDFGHaSIQWJ0zri9DuCNNeQWg3hGlNEVqkMK0BQrssTHseoV0UpmG5LRe00s5bNItm0SyaRbNoFs2iWTSL'
                '9n+ZxrHdZ67fY9isP4+cjYxOSo29fuHkjkVjPmhXSN4XYDz3yeKz5m/lzsbRjX3FgR5NJl/E7U33lncPFULm+vwixaYXN7MKGVnw'
                'J5rl/P7Y/QIJmWNCspAJcn0lPrPbXVHDZppDBz2TkXM1kxinscqoRv1bclbY1E9gZpdkJjumAik0Yn4E57EmQD8z3YTkY8L8QNW8'
                'vcg14+m1NGWj+URnZsk4DaZ4JyON/2Ed9v2YQvT6kfSxJ2P7x0ppeqCsdwbodnzqucmvVgzz9wot2vzLv/GZN58esa/ix1CDjI7V'
                'YlPQc3Hc43m2k8is662dfyilsBaviTl4eYX3PTE5XR8T34XIgi8eTUIqCB8w7cngibQdjfLBM6rSXRZAPwo/pOTGw2zewfCEdtAh'
                'WSyBkyy7XzjXL30MARfFZ8JyulhaWRgafAv9894FX12L3TxgGiybmf7qfPFP9P4olIb5L/4F5Q+8dQZYPCMt2MgKvtHl+G0Of1UN'
                'jEaM3E7a6ToHF35ivM3IzcEdR5AdTpGFv0VOhxP4y/gd/vIjeVLXWtgPsw16aQcPOomBWZjHBBLeHQfcitsLLN0wnQd9B4QGX+PX'
                'NYbEORAaDrrWv+FBXwOhBZOlm3K8DEJLuOWduuUzdcu375bfKfhEbVd4otzy7LvllOrljvO0sezJXw85+bO5444Cyxqwe7K3aYj0'
                'vV8QvfclJZQRaJxGAViWKiMtSxkH9Ep9CQEc+bSthHz68EdTQkKS3g2vef3hlPWIzG9qesJaAUT58kpXpFPNtJMFhJouNqxW/rWW'
                'Lgo3Vm0vKZx/29wff9bPqPEVnYxqfN89mWjjaJxnJ3Ysn83XM6RwsyE78Jm3MuhdVXRp0e9k/Jym6mHudTAkZTqqgxnrFLldOl4D'
                '9HWDXOOFPKa4/qQ/VmUu9RTS4Uhjg6+gZkgYf0I3evcUaeYMuAtioztySPun2M2TZ50M88zzHGHm7XviBlmegJRulp4i9sluqkoy'
                'yheeT69B+U8Tsvsg9xeUKH4WP7uakKPDs9lUDjduZY/MEl6esgOWAhpB9OZvm/oZ0iNrw7e/mrPh6PlrMcn2uJuXTu9cPO6j9kVs'
                'hq4R0vj9aVuPXY5Jjb16YuPEd573VuQV67/F+XcWs+ytAOmu8bamwEMW/X1ROWRD5JZJnRQmjsyzCP9JRfcWRbaK5v7yl2cRQXoM'
                'p0gBl8rRkb4riH6COlSk31rqOZLQkob0X08/7hJqUZC2xSJH6O0SBORwsZP+fGYucqLo7bHYkO+/yTg1wzQi4/NrR7Kl+pHsBf3I'
                'ozYiMnnNh/UjgjyDIup/+DvHv9uWhIwdnD3Dw5Z9MJqms5OCXO1ckC98DTa9Dh85wvU6tGGFTn/iIs0TTUfDC+4FcJBLzK9sj9/h'
                'JZ1w5LUswBUcfgcry4oh4Q6978E/EC8MecITRPrBJd5rYsi3EeljMOKthJFxwQgyAjQDrkOQy1AhaRdsPYWR3VAk/JeHwciikl6q'
                'BiDyDi6ZBoNiSE8QuZUjcYKW+KG1MNclNjZAC38EkZ9zkGCN+9UgsicHCWYA76olWLDW4FbNPVRLtEjm4wHa30/VEk8UM/B2rZek'
                '0ndQc861Z/ku3fBZuuEbd8Pv8jPZp+f3Z/mMu+Ekuq3/vHTDqe6Ou8cNN6Qb7nFU2vhcStpgxz1Aoi8sE9VCJbdOMpKbN4qM0i9f'
                'glLwamkpmLFhpkhE/r8XyNUovjLRKEYh8+cR9J5VznpPDjRQuC5FO7vroJ2FfY5GM+8i6pBJqz+omyfQMzBP3fdXJenQIYU0XQ/t'
                'yEba9fFl+m0bBbQje/IsMJNEiUv+E9asWrYlTLfNzci0QbdlMD2umuwNSmxFtrKuJFpZ69JtwZ5fU2zBl8sLWazb8LvOrcgqaFfP'
                'u5TzR78jYf1vgjQPS50cJuWj8GgF/JxifpD0UTyI3Ph0m7Nr7e7yroHSnpSHI7TJh9O3nbhyN/Ve5KnNk9+rDfp7NPTltJAW0kJa'
                'SAtpIS2khXy2SGjYynUb8/vRS9Gp966e3PXTp23zKPI8W892KU51aGQNeWD2z4EYpQNdfAlNx/q5eto+RewCUV1s4shmF3DRfHs5'
                'QaTPOK5SktxHCJmT1Et5rj8dWfgsTRnbnZmKLHONqjLuzUxD5hPoErwvCwWZ5biI+r3Zm4/03CRmJJjGRw4RNWVM4iGfT2W6xiOk'
                '/zmmG/kl040skKAduZDpRhbh1ATePax5kVCvTOE1ui+IJiJ/xGakzS2dMUq92yUKMjwRmXDGObg203cEZD/k9b9CXC+S11K4SCRt'
                '/G/ToM2OaRxkafjVqzkNsbKpj5BwchtrA9yhXgdwJJxA8Tt4L9dAkcEp4hVe4earD5BwWV8sGbYZhhwh5eLzvIwgV0Ev2bNhUs5E'
                'BHkRDTCT+Mv7hYIvfYuHR4M/934VmUDf7YwDrOzQD/7CS+JIMCy1X0/wUOMEpYPurn5DZXM/wdT2fj8w0S62j8aLIBIMGdjIQYL1'
                'qvvNg/vP46MyiFzCCUyFEw5AJBiYvZCDLAkiF+t/lz/p/yx/1P+Nf6//dzlY/9PTTf8z3kz/SVRW/3kZmKb9VIfzpaXvHrievvwN'
                'CSs8XRGiB3aPw9VMsEIBTTFpwx+WgSvDyHWo5LZRu+RmDIBfbQ3Jl/txZEH9UjAis7K/TWvSdeDJ6gbWqmWriUbxKl+jyIxlL55x'
                'FoX9x1O0s3GodjanlIN2dpGk8OXhZEfsGtq0ULCnf45q3eZTdUg4SlFeeQ6/qx2pnmTsivQ+rh1pVEzSjjQ+El05kYu0rdZuzTKC'
                '9osQt3hTLIM5L9CJ+7PS7JfFLwvYGolW1nwnacQ9mem24LC/KcR5mUQs1t6juBbrlL6idvUXOCbmnRXErf++/ZHYnBvdJaz/6SPb'
                'IOCYPdzdX8pH8cDM0MrVk3J0tGPoviDygb+n+9i1x9MznOOiTu/++bP2Li2PxJHcYSEtpIW0kBbSQlpIC/nfj8zW6P0f/zp68U5K'
                'wq3zOxePrkdcVmrgdidn7ARSVZfmm010LcLKxqbFW/grs8w2f30Sb2WtKOGWjg9XdkxkcisHwHrFFHTlu4jiMBVb+TLmT5+GrHwe'
                'VdGRlVlxxRFOway1DFeQpoMr5zHZlbwxQ3rlTOmVs/4DK2dLr5xDW3liapfaESHpgRvF6vedfpC88u7o0o6HUu4eq+1sLndl6liz'
                'DMd8X4/hrbxQRTiM8eHYncOQW3kwsyG38kZuQ3JlM0Ny5SJDcmVyPtmVcwzZlRVlV56UDWgFastQVtaXXZnsL7vyiHTg7iLplSOk'
                'V74nvfJl6ZXNpFc2cF9QtLXSWmmttFZaK62V1sr/9ZXmsT5FmvYePX/dP2evR8en3m9leWL/jjUzhvduWzUvscZvSLvvtiHlHlPP'
                'rP2hT52sKCL7+9toeRRX1wxvGwF8LsvFCldHLfvkeWd5t/omGbV1ggMjeJJcJX0HSukzkip0RkqzWKZOaZDI1Cll7jF1ir9K2f8n'
                'lLFMAyV/kg7KLKaBEhKvg/I200GBKzPfWTXw5WoRWTN5+IXmLNWw08A5u6Ihihf0q13TwqQgVqFXx+9MNaEA4b+3X4SPsTYTzjhT'
                'zMv9JXFO2nJfHnagmKdfjeKfrGXGRD2lmP9aClJOaK/m6YauCXDcbSz1sij47ZcP/mtaifec6NVjWg0lTpSyWqqQo0GKR97oIUYB'
                '2p38KFYtfxDwAOxtKlLPH+49c/H71mFUSin0ub+0bsJHrUr48IWMGEIPjbPrJvRtVgj7E5eTD6R7O6f2rgDUFH5D7Gy7t3FoDRNS'
                'qPiVdnthe5dA+x9kjtuYmRUcKfkl0zG3OlYS/UL2/F+bMdrfd58sJiFjB4T8N6Wvo+kZHtvy8pg5OgQyxvpnvGQWyVJSHZwJzU5J'
                'Yv5xONG835QMyO3o+PuzNfpF5he42/USfvUX8RY85cyuvGofr7guRBkKnTp5Wgyat5v6rv7huM+rdvz0x/Vn7byIUH/K2exbpvNE'
                'tEl3dfJlkXfgFYlq764j0zzZ0r209KDJQpRwQKmcK3arA0rhr2KU6ZItO0kSxs/GsGE56JS1UKexKSxxZkUiJCQW8stMeeCLfD+b'
                'irDz5kPK/VYVPbLzIC+kgE/AlKcCxl9fPI+IKrZ+kFKXHJiB8kBGXT/yJVPBO7j3MTj83nCiPHRK7//167fbPV88PHMmT8+g7IXq'
                'dx29GzOFDDSliN4lEToo93+5ypS0qjoo9zt1KFNu5NJAsT/s6qJI+dDQQPnYUKckPkkTVKCcfXqiSFOSRmRIXZOkpMx1KLPpX6Pv'
                'vFOitrqob826oYY2HLj0FNX8eGVWE7jbieFdvPUnM7bdQB/fIz+9W4p0RAcUqvniO8Onr9q29+iZK7fj7akJMTfP71u/8LsP2pYj'
                'iRipare5tdxabi23lv+PLi+udD+vtZZby63l1nLicuugtpZby63l1nJrubX8f3w5ZIv+krYcKgc0jrYcMj8RHSeXJKvhPRpQTdbU'
                'LKTlYK3Uj0jLwYqDt0ixNnCt5TN1CctfRSTAQ1+3L5vDDw1JKS8mU05xNj7GKS03Nqgt/0xteQm15cYhteV91Jb7X1NabvRVW+65'
                'R2m5USJaabnRKEVpudH4rtJy47kDSssNrwG3VZanF/Ma8K/K8vRRddTuVIXl999Dre5jF/916vrdxDRgeahMJU2oeF+URfs/RBv9'
                'X0z7Ritt1H8xbaRW2tdaaSO00r7SShumlfalVtoQrbTBWmmfaaUN0kobqJXWXyvtY620j7TSPtRKe18rra9W2rtaae9opfXRSuul'
                'lfa2RfsvoPWSqBov9+udrvWpn6/1tPxT6y1zUJiGFXKJFaaNgWG5mTANUQhbgLQQ6JVfYNpXIC2A5vB0GGCd5igv6JX9ICwnGAMY'
                'ZUCB+ndA2ocMpoEpQ1A6lu0UQjsHvfQCQOvAENpOQVHV5xRGWy5YKGgEw2hgexXz2jgNU1Ea3MzgmElM5HOoWSfKqAe/uNDFVFsV'
                'T0aKMsKQVxc5Nm/w6MtJQo5CWqKkj1MZKhJ5tj3IszxFcZrfscOD6+bw8c5c9pWpV/h2rCjc0i040mkhSTppxgqttI5aad6XdNL0'
                'tXl4QAuKElt04VeMZnQRgt0qPh6l2XYIwOKrGzjNyE9PVYttYPBoRhtqLPqtKgafhvZsyTAulTQoNNrPZF2YQaMZHbhlC1I/9zCo'
                'NKP8YRy2sxJXinbwgw1Csnsj37IZQjTDyDoMuEX2v+lLkfCd7xG/dotcMqqPjqKn+7kMjzI9v195+Gp0cvKtc/sXD30pH33pMolu'
                'UHx36b2g5tDnT3LDQr6UGYYndHx+TsBWZ3Cq5TDgpRME7gREXMoPnQuVuFiv65j2BSlG47lc6LtJzIrJmVGePC6k+C14KHJCYQlN'
                'ONhAyK3d8OHr47C0MmR0AtadteGdEu8FGDLpmU/1Ukj/eQ3F5gDk4tRcj2d0BbhrUC7keV75ZEYA4JxNRTM79/Cbrf0oUeGzKLDm'
                'qlcGQZ1RM9afjqEUrwYUY1AU5p42X5FWiPIdwI6GaozSBTMLUP7pjPBR9qrjtF8Ec9aho+y2U0mNBgB3oiHWkPE7Z1UcKABxw1vs'
                'KHvOICZAtzDFBgBH2S6XmblSsbOUepR1d526EpCXgwSOsnsmk1szKBPcdWQH/rjpZr+cq+Zz1wscZdXM/ravzefac7lO3S1iDSmU'
                'RnXiFBUzrm6imsaGYte7QS41VIp4lEF2Q7/bND9xNdHKyUDVnfM20rQzYI2iMsAbqU06ygYJX4XTKEdZai6YC7T9vp1RKzF+Np+0'
                'AgskAvSnthmPMmBOK0wmmGW+ZkmGKa8D1zsqfdYEfvGh3KOMU4b8GO9cBY4yx+vddQAtKjc/mfCe+YQNHJk2m7khLS0v5yh7hSfb'
                'A4aeAY9eLgLYOnx53Mb40TqUdr2bqMTnzVeWRY+y5/i63hcMCWiqKtNU+uGIMHdWXPZAjrJuFF16DXy6epkHrcYGUrjtzbmz4KNs'
                'Osmm4G3+pmL8wKOsKs3UMZoBTQGAo+ww0YRSDDpgXxePcXAYf5kuT85q/o0mZqFy3zB/X0PMY3jnk21J/uZBxClyfS4yjMkCht8z'
                'AlUWKwhwPxUxyNFr6GHXu6EQpL5cyIAYSi5D21LMMvkTEXvFU4xbh8j9StSUSutLnFZQlNufxF0vbPrNkSJR8E/FMJxx3PQV5zYn'
                'cMeLY2HDcIZRWsa4PoyL/VvKaJ+f6zDqKucN+JPnzQqU43bgcH+U9F743MC5VSW5oGGYiaSzmYySKPc9aa6BNTCnX++uoyvCnS+P'
                'BQ3DhOvdE/C+HgNXmNWmTA2GZr/PIEVnmWAUj3HBbHZTaPZSAJ/DeAd4pR10QDCRDAAb8BQdhjProGO2s9ApVxqhA7Ek+wDUDHOB'
                'N5OYMNQSljvsIUJG+obms4EqwA9+jG8ykQZiOZlQukIUcv9EMJGMkY5wmUuDXinpYWwkEEq2wxQ1CTre/AQMXKwephaY98E7Ah1U'
                'dQTs//EPBZ4XBc68rOA1b+qxBlqm/onDhpiQ2gpJmYUYbuDZR3E38a7dOBNvy1vA3Mq41h7vLaR1mfil5pjPvPNYE2kCoGq4kIKR'
                'gtADXDcGLFPLntyqSVRUM+Red3X65mO8yPAt5hN+d0GNQja+60m7Txgr/mTGYPMJMR4iEpJrRMUMQNnkGo5ZeSdSpmRs44+I8SsZ'
                'CjB4x9KMQw2FtPxcwLw3DF7HDQcbPF4J4YGLwembeQWYF8GPrb7utPFmXBso6zh7CqFxa1kAVcKB5Mupge+UTASU3p/kIJMBrqKe'
                'DqTnOXrVYkffKTCrvcOshQwoNI75rneh38xLgEjlqJf0MJ91ycBqfHSIw74ZICRhL+0CK5DRdef80IWtZ0gGz2FatvF5/jNXxUXL'
                '+RxxokK3fGPa8TYjw5SPXSrw14EPQ0hkSMpEK3NyGgkzeMXwc45FKcwVGVyk0RzAl5zzqd/H2emc3hp7K2xX2UdNogV+Cx2eTChn'
                'EmIzDGxJEmKnChfjeQEx75k4YF5wdo0bnLygWC+XjVsyjlfEuctDl/uyi7M5Mh/H+7LKVT4KBlyqTw6aa2Yhpc4ZMJ04Hs8P6PaX'
                '1kCFmssP/vUbwMsVBAS5lDHZeDhDs8V6mtpsmgOPHyC4XjdzjNTDA+V+Nj0eXX68udCIGtOQJV9zj0NKoHkNqpLmj+sju/YOcvQT'
                'bB5t9ODFgsAVON60kwkkFZp7BwZgSvSbgDjmfCQfxcLkgB5uQDe9raYhGX2hSygMkQoBz66HuZEv8YEWfQYSuY+YSTZbxOIWlsGR'
                'PM55ltEekG3ifpSBbyJkzjMf78B1FF4Fjz5ny/oB2MMFOqUBI98fJjLyJ08WhTsLc5lBXQz2yVwBb5RjcBzeKVej3QZRj+Nc8wVV'
                'XPLwMtodprtUyQHKpqUEizrQ+7nERKxHYjT3QMrnDthqngcKNfgOEWDyOtspgwaKF0kx94veth3ArGnOknETIAirLrIxYDCsbcfs'
                'h86/jNGxmDlPKL7F+U/4C/W03IafSnBk4fUXM3NtF2HC3excx14SozHl8RfLdvmGgkhx8lsuoCy64yETfoanDfSiLFqK+78yUTJe'
                'vxVq58n4hUWQm5RhQZy2G4RFxTkbD+Yj0jJT3WmABisSHZpxHDQkCjJy66l68asa/mBIFAF9g+uZXcVlvESV1jKOPNyNP+Aycki8'
                'W0ISXhke46TJIm5a7ET+xrbrEnERVXkbtyO433kH4OtmP0lOV3k7JcygO2fjvEKFfRml9aZhqp6BZg5Kig4jd/JOH+ckTgKOYbeR'
                'odB4kmERwLgpOykTaeNX0I2LmC9CjfebiSFtGCPSEEvfI+cGI0a+B2MhsKYBtnEN4sbjJe5zzCV114u4cUtkYzAYHqnDsIoaOhQM'
                'xy3eAiN4v4Y3/sD8UgAfhD9sktfYB3h1BlT6KgW+nZUP384S6PW4IjDVG/R7X36U8ZX5PDRjBxx3C37YqU90vBopwrUZa9oJhSs/'
                'BY+usubUQLC/96YM8r8HGBl5yEfs7L3hELUdfk2oXGsrUPp1ChJqDIWO2Gu6UrNfI9cBBrWtf10z28FSULtdAjC8wSJULn2fu0Ez'
                'Y0xMpwWiiZpoQVC2ednse3gZfGwctBCPbdC8qeY/xmmMEmo5EJp1BGjt6X+EIMqXg9TKuJLgoQTF/t8MfzzF74hEiHIP7h0xTqIS'
                'HejafiIL1Yeemn+DMWzIWeguzX//5dCL0JHEqeNRFbqmt3jAyZnQfZZhfMLgYJSXONcMps1A1SsSSua6xblmsJE9EpL710HXTG2K'
                'HNGAZiyj1Uc2aCXtONcMahHYzoR7WlNG3tt0alozeoR3Wzr2W5HI8YlU6m5vEawfsQ1EjGD+TvF7JOzLogH0pAJpU8UD8+fxqYf9'
                'xbFBp3lU+JrBRsUk92TCcIxRvxiSA7VX4dcMNnJiuVxvyVKNb7F3e1E2raQpnr70m+RHwDOmvSND9djI+90mlpXAEgzaJwKEqc+n'
                'Es6EWaLULLSyk68JYpfTztu7hYWo5GZI//gIUCvQi4yOpVMDTwncvM0N3YmzYnJCF7dINcXuCcpgnyvd5UkxkMRYi4CFElBYv9cU'
                'zsh2yEcI1ZJ6GvEPjXyQVBedbmEPuSB5RnrtQJ/+2na5MxK0Fy3gSNToGflCGkdJ9/5H4ozMAdW5TXuS8lUsTviMtIEujnH8lCb4'
                'jAQtBUf9KCcxcEZWh4SNpHIZp2WLFDojQ88TIw+apIloJ6BddKvzCQUWG7/uekaCVtyY/C6HEWgB2ehBtjl3NjFQJxLPyIDj0MRf'
                'DZE69k5n5CzQqW565tlAC+rFzISKYiytsflPHDQtZDwjC4Pe9O+Fj+WndnqfvSL15A008j7DGfkdNCO5AiJLgPrV8QCOu2YgaoMC'
                'FYuZD6LKwLr2f+ECwOfg20kvF+m5FTzpCuAXlCdocb1bCMlL6sK7TgtAggPb45MrWZb64Lm4Anamg5z0O0i6AANjbcCgllIE7g/I'
                'm9orX5TD4ypimoUyo/k1wozaDKlD6XudVrLUoBc7nW1gTU82cj+GSLSQYB7gaUwrLFn05jReow1tGogZ4z7l/AqjvKU+htTcj2fs'
                'ZzLBL1DPjt+5OcVrpDSDF59KAcBBac+LnWaArHkjg1w2kom3BqxPeE7zAraEi8i5DmRUOuatLBEqc/DgY7hGifupK6wqQfEXvQ1K'
                'd+iUcIg7FXCDhNJCoQZAH8N1WhkWf0Ai+hfw4DSkFlH9RqxeC+DMPOfyNvKlihhZvYCA0i8MaiqHeTXbRsDRmo/+/JhW3/0RLctA'
                'iiI6avYx3BRIa+lJDzICwprvmBbZyHSHrD/PEIqSBAzPcS4Gci/gx14RkOPsxIZ5TajBvo/GClKmsWHMZGKFHaGH00kV8DY39yRl'
                'FS1P6xRv0VRAcUQ145hMFOWxKcwNiCYI2cDHcNlTvNTXdkK1DLREYCE7X8iebT6lsIwLKYOhyOeOQIUe3pOfoVJfC6mYctsJ3kll'
                'Xk/lLi/Y9B2OkO0TTaidbearjMGF7JYCpeIdxnd4L+2fBMuaPRlFzC1ikQ9DOX1jgJQzQ7YAcFskGC0lB8UDiInh8+S9gkDbRHsE'
                '/DG0Ivkp3oNljtZAP0oSN9g87uyCBxTf8w3RXTMBOmD97kpl4DyxbacBKUtt5U0VD8Y64Nc0X758NXZmDYmldqeAVFTzQj3JiFVA'
                'S+QB0l4AHyF0V9tpIZfrJOaWQshg7UHEKmBoqXIKF6/CRysit71oDMJZmivXR5ALtRKABQviCI2jcJ8T5kKatVNytPigZEf2kgkf'
                '4UaPuFgFaKMNl/uzVBCN53ket4FcdM4nHOw5mxw3C6f8+BeyoU94z9u0fLJcPNnwT+lQLTx/6hV5bnsEa24VIP7ULjCV3El4DIC5'
                'FVW4WRPoKcBCA3QJ9lXjloPc9FnVuEB3CbZIEQulVTRR5Zr7jy55qHJXIlV5FEaWJJm+QPzRWyW1ElG6DpBTiDX8GmQaBzhq9/+q'
                'x6Ab5OQSu+K35j1X2AJHkSjbHNFcMd8va/76b88CE8n+EOWl0kTpKu7hLjPcwk0s5B6uxIlD4R7zcws3pbLhFm4/wy3cBYZbuBv9'
                '3ML9S7JDB4e7SFbQQ7kJfW2GG7iri8mfjCA3bVVtlRPXnJu6q38+tfvBkWuPv3Vqy9z+TSXzSJjy2GlBLIgFsSD/RZC0N6kW8n9g'
                'SG8iI2C7QK1/YPhvVK9H47MGZowgMryWqfdZ8/iFKWen2mbCjLk2dS/FImoHwTEwYwU12Xg4zFhHVW0HwowtmYiM92HG31QvWE+Y'
                'sY9q1u4MJ4MeyUa1FMDS4MlwqvMGzqA9l4fIaASmZLBLBYiMOrBBO6ookVENrtR2k9rIsAJYOoVFVyAySt+EOwlWJzKKRoGM+DpE'
                'RgE4gzWxMZGR5xys0LYiMnLALUJTqQUAssKVxtI6U/1zSLXWnkRGINJP533qRbdZ3Vfsuw5mDKMa2VbAjDFUd8YimDGJetHNgRmz'
                'qBfdFJjxi4d6Ubll1PpwSBmUNVRP9eeI/cRf3cm9PVDJcv5g/BNCZHSBL7pD1EoKHeGSNSeyExmtU5i6WL6KWRALYkEsyH8RhHrb'
                'V3jli7lr9168GZss0eTbVu3rv+AauXxCvm/wqvc8QoEFPBcATvD6MpEpNTvPQ6lDhhEKXWRqhDy0gjQwwZtYSq20Qmd3DqFAoirh'
                'Z6ZIyJmsSvicqRIOqBLyYmuSt4zpUr94jkyobaYzvP5IV5IlBEzYTxvsqRRQQy45CLfSOEa1bXmmCtUJNxm5IfU4WDXidzvZg1Ve'
                '0VyZXtyEqdaRq8WEWoILEEooE8KVCZmUCd7KBJsywbAI/ycJ9ZQJjZUJbZQJQA1sO50AeBASDdX46Lt0wiZzwmUywBZDT5c2H88B'
                'X8UmMgGqNz+PTDisGtTVgElXMXnkowPNwSVVnVq3iEd1P9A4RgsqzvkrLMV1IKyvMhHpe3ID88t5B+Qq1/Lj+VekqhYOoUq/5zMp'
                'EpJrGmqEVPhjpBHuIMndJMKqCEOFkLamLvoT4BCStvbPz/kRcQhXf2zupUZIH9eHZVckpPveBnopEtIbvudVJbArJVUJ7GK4KoGt'
                'UybgNYd8gvNUbDPw12tMrIecyW1Xa2aycr+g/GvU8/yGCfVJMx1gqUVG9WJ4g0UNmyuna/ZTzAEWqbsO1aRbTSZUgiIwyAQvIF3z'
                'LF2WAwxqt+iEWeaEODoBsEYl0wk9lSXz9sqEJsqE+pauZxGeCcFDmeCjTAhSJkQoE8ooE+h9VaoxtQBVwygLEKaQCcWUr5zskJAe'
                'Rlb+oZL875HfxDmAcNZHrWgJo3YGNeDyjelVgYh20pdgie5kT1IUZlbMo5iybexb9Yplz+Ql58Age4LeUybQC5yUFq3qSidkj1El'
                'YJG5RIJttSrByHJClWCEn1AlGFnXqBIM28exioT0GuMzkxUJ6RaqYecVCfdl/S83x6sR7qtO5dPjH9btv3Q7zjkSrLTz5dLC+gfr'
                'H6x/sP7B+gfrH6x/sP7B+gfyPzj5D9ISYq6f3rF88octqJlgiAfi2m/vRagR7o/d3fwVCen5ZAN9lX1a55qoEljaSE9VrxhbqO4V'
                'm69MwJKEiYSUcsp+tS3KhP/X3tkHRVHGcXwP7oADzniREGIojiArqbQZZ7DzDdFEsEmmbDKDsiRiOBywAUdzHCcZhZoYX0Kx0NQa'
                'RycsDscxIukFh5dmxFCOVGBIUGJAAo3kOLjNSfGefXaf3d/yG/zr9q+b273P3Ow+z7O/5/t745ejCT/iPXPT0QTZNDSNpyHsmSRz'
                'qVWOUAua68Z8tnAwBuwEGszOG38BuOR4/sYimKGr1kwHuo5oJY8tepXK88h6xCEMwgW4bM6ICWmFExgd1a/BCYwmHH/BCVvQhCw0'
                '4S00YRWa8Cqa8IqL4CIoE3rRhEE0QYXTnNUoEV6DitWaMBIdlAsPuZ/DY6s+P8UgfAEmBDEILWCCZhh9K1klCj4EE1hVY7o8ka8c'
                'dmssDto2h78NLQGsZ9Yw75kJRJSxK1dkw5x7CTJ2ZUdO6MSLs45vm37fk75weqBedvO00IH2ihWiCW5fo71iboVorxi3+Arap6V7'
                'r4VHe6RiP72IJPitOTGEIcQcxuWRPvylA3cn43uQT/MNO3I8JNiRYzKkDzsvDvFIQuSY7K+s+zLjnw7ykVsf5GbV9Y2Q8pZsx+jI'
                'ZlDd0RlMwN8m2FKdzhRT5mGLuIPzOOoZgF4fKKGfxxV847x5RGfgu+OJpfFx2HjWIxw2IQZeTj+RV92fjoMleT2BDiX1x9r2oxos'
                'QUWSF4PQ59rruQgTI7yGJqxGE95BE9ajCdvQBEb3yW4O23PmKpzAsIAugwFGHtuTJV21E4Q+anhkD6Y52DhS7yYeV75BpqoLaLsb'
                'XcCOvhyW2+xqPHwfiUnMOnBJzgytRPtxzFjCaBiWUIb2Z83FEr7F+vWGIrGEFKx/cyfWx1qswRHsuRqcr9lqwvm7r69D5ZE6alKU'
                'A9zZhO5vMkI49bEHDtvN3rZayz4V8Q+TdHg9OzncyEYJeVI3O3PnyYtdA/aha801B3IWT1PPTR4Q6Z6P5lSL4oCvFK9Q1UrQsJ8W'
                'VPVrG1iL38/p4J5hcR2UUjutsF9uOI6cXAUp5Tm1xCGUgAMKlLtMDuxRetbu5n6htqzLBUbwn8uWeZbalD8o0XpBM/hdxY9WZ0i3'
                'NPXPbKfUcD+4AjT+v7fFUaKKf/LxYVpmX9LFT+CwNXz2flzUFK1HYMTctKIGkba0wauYn5RjwwzeBXaBhUedUQzuPJK3/MlQX3ef'
                '8NiUHT8MTAQ7stmdVhybPqAEMs1z2d8Pq+Q2PU9JmbZS6W5svslHb8Gxt9ZrhRrpSIlM7QavlRUwVdtxLIwSXyuMCmttcN5lZe7p'
                'WZSq2/EyxM01f/8NOepYuYmWi0uhsqrHS8dYt7v74whah+5LVvMS1s37qI7OvnNYi0xuIoH7bKhqw8E3Nm1XVdPVm2P/9LT+VLpx'
                'mb+Ucl7iMSnGUHTaA7LmIlL3VrX322x9LZbtS+Uf6dRcoTP09vFEpiUfWCRhXVhXS1//LmPs1Us4mx9ie4XteTQ+XDaF7juh3RSt'
                'UBb1LGkehio2ev7F6a7Xn1cT+vo5ZPlYe+/iJNBi8+9jdxenNuHXf+56McrgG7V0N1VR9gQnzqPsybi/adJl9YlKp+gEiFpBGZIQ'
                'QVBk+Z1vVpBfVFDmlP4UOZnv/HOyM8AFUcl5A2kY5nFaQkexPS4xsYhUxAZuNvHb3Zx8RuuowUwsiJLLSQhhscUTRVrqpSdJnfOK'
                'TIti24WtziuKiHzhNZxSyN+hc87PSYqBEmWNiv6aJcRQIbS7VOmr33RecfiUYkDMJkKp2Ov8fEZRQF1HSMIjkk0FAog3c8J8XqHJ'
                '+XZiEAboiWz5QYkc+7AhgXJKxp2eEYkNnqSncisVnVlCvbq0R6mAbB/BbrBcMB/8qshz/9+zfMFUbXv9/hLp9nanuEt0AKUnXypc'
                'ZPTxNi76pFWy6XEaaPWx36vvoDkNuXrT+B8MAmyhKp13K0bRGG0kQ+pMCtvU88GCxzBLNlqimh5v4ezuLo4Csfqk28Ion9e8QFq0'
                '/0qi5EBHBlMnjshvF5rglpXyElhMxsFfOwdHbTdaLDsSpwDDqvku1wnXiQd64j+Mhoei'
            ),
        },
    },
    'sans': {
        26: {
            "ascent": 25,
            "descent": 7,
            "glifos": {
                32: (8.266, 0, 0, 0, 0, 0),
                33: (10.422, 3, -19, 4, 19, 0),
                34: (11.953, 2, -19, 8, 7, 76),
                35: (21.781, 2, -18, 18, 18, 132),
                36: (16.547, 2, -20, 13, 24, 456),
                37: (24.703, 1, -19, 23, 19, 768),
                38: (20.281, 1, -19, 19, 19, 1205),
                39: (7.141, 2, -19, 3, 7, 1566),
                40: (10.141, 2, -20, 6, 23, 1587),
                41: (10.141, 2, -20, 6, 23, 1725),
                42: (13.0, 0, -19, 13, 12, 1863),
                43: (21.781, 2, -16, 18, 16, 2019),
                44: (8.266, 2, -3, 4, 6, 2307),
                45: (9.375, 1, -8, 8, 2, 2331),
                46: (8.266, 2, -3, 4, 3, 2347),
                47: (8.766, 0, -19, 9, 21, 2359),
                48: (16.547, 1, -19, 14, 19, 2548),
                49: (16.547, 2, -19, 13, 19, 2814),
                50: (16.547, 1, -19, 13, 19, 3061),
                51: (16.547, 1, -19, 14, 19, 3308),
                52: (16.547, 1, -19, 15, 19, 3574),
                53: (16.547, 2, -19, 13, 19, 3859),
                54: (16.547, 1, -19, 14, 19, 4106),
                55: (16.547, 2, -19, 13, 19, 4372),
                56: (16.547, 1, -19, 14, 19, 4619),
                57: (16.547, 1, -19, 14, 19, 4885),
                58: (8.766, 3, -13, 3, 13, 5151),
                59: (8.766, 2, -13, 4, 16, 5190),
                60: (21.781, 2, -15, 18, 14, 5254),
                61: (21.781, 2, -12, 18, 7, 5506),
                62: (21.781, 2, -15, 18, 14, 5632),
                63: (13.797, 1, -19, 11, 19, 5884),
                64: (26.0, 1, -18, 24, 23, 6093),
                65: (17.781, 0, -19, 18, 19, 6645),
                66: (17.844, 2, -19, 14, 19, 6987),
                67: (18.156, 1, -19, 16, 19, 7253),
                68: (20.016, 2, -19, 17, 19, 7557),
                69: (16.422, 2, -19, 13, 19, 7880),
                70: (14.953, 2, -19, 12, 19, 8127),
                71: (20.141, 1, -19, 18, 19, 8355),
                72: (19.547, 2, -19, 15, 19, 8697),
                73: (7.672, 2, -19, 4, 19, 8982),
                74: (7.672, -2, -19, 8, 24, 9058),
                75: (17.047, 2, -19, 16, 19, 9250),
                76: (14.484, 2, -19, 13, 19, 9554),
                77: (22.438, 2, -19, 18, 19, 9801),
                78: (19.453, 2, -19, 15, 19, 10143),
                79: (20.469, 1, -19, 18, 19, 10428),
                80: (15.672, 2, -19, 13, 19, 10770),
                81: (20.469, 1, -19, 18, 22, 11017),
                82: (18.062, 2, -19, 16, 19, 11413),
                83: (16.5, 1, -19, 15, 19, 11717),
                84: (15.875, -1, -19, 17, 19, 12002),
                85: (19.031, 2, -19, 15, 19, 12325),
                86: (17.781, 0, -19, 18, 19, 12610),
                87: (25.703, 0, -19, 25, 19, 12952),
                88: (17.812, 0, -19, 17, 19, 13427),
                89: (15.875, 0, -19, 16, 19, 13750),
                90: (17.812, 1, -19, 16, 19, 14054),
                91: (10.141, 2, -20, 6, 23, 14358),
                92: (8.766, 0, -19, 9, 21, 14496),
                93: (10.141, 2, -20, 6, 23, 14685),
                94: (21.781, 2, -19, 17, 7, 14823),
                95: (13.0, -1, 4, 15, 2, 14942),
                96: (13.0, 2, -21, 7, 5, 14972),
                97: (15.938, 1, -14, 13, 14, 15007),
                98: (16.5, 2, -20, 14, 20, 15189),
                99: (14.297, 1, -14, 12, 14, 15469),
                100: (16.5, 1, -20, 14, 20, 15637),
                101: (16.0, 1, -14, 14, 14, 15917),
                102: (9.156, 0, -20, 10, 20, 16113),
                103: (16.5, 1, -14, 14, 19, 16313),
                104: (16.484, 2, -20, 13, 20, 16579),
                105: (7.219, 2, -20, 3, 20, 16839),
                106: (7.219, -1, -20, 6, 25, 16899),
                107: (15.062, 2, -20, 13, 20, 17049),
                108: (7.219, 2, -20, 3, 20, 17309),
                109: (25.328, 2, -14, 22, 14, 17369),
                110: (16.484, 2, -14, 13, 14, 17677),
                111: (15.906, 1, -14, 14, 14, 17859),
                112: (16.5, 2, -14, 14, 19, 18055),
                113: (16.5, 1, -14, 14, 19, 18321),
                114: (10.688, 2, -14, 9, 14, 18587),
                115: (13.547, 1, -14, 12, 14, 18713),
                116: (10.188, 0, -18, 10, 18, 18881),
                117: (16.484, 2, -14, 13, 14, 19061),
                118: (15.391, 0, -14, 15, 14, 19243),
                119: (21.266, 1, -14, 20, 14, 19453),
                120: (15.391, 0, -14, 15, 14, 19733),
                121: (15.391, 0, -14, 15, 19, 19943),
                122: (13.641, 1, -14, 12, 14, 20228),
                123: (16.547, 3, -20, 11, 24, 20396),
                124: (8.766, 3, -20, 3, 26, 20660),
                125: (16.547, 3, -20, 11, 24, 20738),
                126: (21.781, 2, -11, 18, 5, 21002),
                176: (13.0, 2, -19, 9, 8, 21092),
                183: (8.266, 2, -11, 4, 3, 21164),
            },
            "dados": (
                'eNrtPAd0FdW2c9M7NQkkhBpIQCC0R1dpdiyIBQREKYqfIiCKBRQRpCqIqEQUFELRCIpKBwlFegAhkFAC6Qnp/d7ctv8+dc7coM/3'
                'Pt/3/lv/rGTu2XtmTt1nn93ONASY0/AP/usBzPYAmKpVwRgtB57QkuFeTUnqs3Ngs6b9DDP+0V9e1Bnor2kBVouvKLueo9pb0x6C'
                'X2Rtj8NuvC6DtyTmE3gVrxegp8QkQ2dNC4EydwIsBWM6fQsMSZ/RYi7B32Qx10gxjaHEXSCaQ4FJ00bC9/KRF+AbvK6FyRRyKReH'
                'qjYGUwvIwesY+ipL4yEOr3HwgsRshufxmg2tBMKUD800rS2kyUc6QipeJ8KX6mTMOv73gW5fXrNB0fFlfd007S2naFpf7R6Anb3n'
                'Hm/Ua+rhXtq3cNZDvnMOluoFnCD9F8ASgJneAgjJBKjKTH86nEJh3zhowUcGUDB09GErIpwviubUHZsH1Q1k2+4EGCIBbyeMkMCj'
                'AN32xT4S6TfrRPSb5XDSlEKKtZHLxQit8ei4xFyHM2fHOG/evzlqt99RgbdVYLYERp4xF8W35kBYWX49mplJW18UydDfwUj629gK'
                'r9drewK2Uegh2CtmcD9e24CVkK5/mpm/tRDeIz83oQ0dq1maAZ1H0DG2S16SmkghrZw2P83tuPMu0bwwG1YZdQR+cpntN2kDS6K0'
                'xqX59ZWOPXfOUrIlSsMpHIWDd6y67OcY5e4DpJKx9NXKLhLrd8PSRgssg6XBzXfCUYleDG9r2hBIQrIPsUAjju1gS8YmvwKrCZAE'
                'fTiFHoO78WeGQPdm6JdgLVu3pJBgCzSm2EalBXTqgypYlcfYw9/AaJZ5kTawqhsF7ocDcvmfMJdv78zyDRYlm4vPfdrXJJvbKosT'
                'c3uJOgCWl8O820w80k5gQgFe14ypA9CmqynIKmdLpnVg7uqC6ghQcIcRk4H153dUMGE5sO/OIihkzU6BOZq2BVIDtY75UEw66G2B'
                'R7VwB3JXXOA5UNpD0+6FSj+cKaBE2ToDynojAX5CpgKiaCktbkDFDGdlOGEJ8AqrJ+Iq1kyXVyKU8ikfhCtuEMl0r4aqt6O9Ant/'
                'bAYzVFAu1y+HD5fl3YhMKIwmuDrTEwptRcfmhmla5yrIbIocuvYfeRcSNc3tHDyoaePI7Lldh2cIcZX7ado2+Ap7ZYZnNe0uIDT+'
                'FpTiK59DCl6/h1/ptOyieUJqsRT/Jn2GPY/vIulqP1DSuR/KcVGZrpHykXAJpbidJfVq/SExHsZi5g5HbgD+bIT5eO0NFYGUe08g'
                'vADOaZS3IPP0tVHqOkvX0HbYh9f1cJ7uIBk0/xted1A8fYY9z959h5ZzhZTZi5a/gdTVjtYbD+PEVPdUdiEd2DqSAyO3aEGHYXsE'
                'AhE74FCQpg3PLI+F2PLM4fRB/3k4OfP82Vv+7yHwnh/ND+OPDUPCPAQ7SAFNaQFbR/GiR239oxaw1B4qXcj3L8H0c90FfWpj/rUt'
                '1CqRHPG/vgPeeRLyA2NR2rme7q3tY61rIn57AswQ/+zFDxi3I+T2IGcI5Wwfelvs72eBTW4zqKlDM1NhJ7tzkK1WraHdyVjrGMF6'
                'f6TCCNKAmbEAbSgksTtxbOvQPEuA8aJ7KPFi+hRWMD6cRaQoTD2gyINmFpD1yHjPY7LLptEHCs2pn7KNynsn62HlwwT6AmBxhF//'
                'JKhGphnjhMV0cy+AHzVtBVTVZbsnOBtrqbBDMtCxAU6Yy4uuho+QMY7VRK3b7+SiDxUfDqOg8QiHDsFp4z3je8YyjfW5tMXYTuyD'
                'c1ET336sD7J/VY+IvhdZrn9G+95q5MpEGyeFSD4KbDNJjZvULVYlm5X/54Dj+hKLNALNnl9/Js9akDCVME6LwKd1QsCxZWhj33ZL'
                'rJDfQNsWzQoaDvCuXv51OKgDhynfZMkjH36WwCjQBdqwm3BViDm+x8Hanee9toNzlHj5e3COF/nvAP6L592/AZgi8hsBpvO829cA'
                'rwlq/hzgDVFZI4WzlBoAzXvAoiNploqkT+kGPUPcsM8movSPk3o28W42AsXLUXr36ubAGYVrxEKNAn0CeTrglw7rRNPChpyBG01o'
                'PoFKaR8Gazrk2N9fjljzJ06BfYxeivsOqA7Wwb5A9z2emgJXNcTm/qQEvA9DTQP3i3PvauXv1WzUbwDvaB6y47Z5RDqduj2lvCb/'
                'yPzWehFdUYx+Ti/jIqjgEjiqgH0cWX100P8qPNReBz/BruvgQGdefR0MSofHNR1cSxmjAB+GgmAdbJALwzQdXA0/aAq4z7BnNHQB'
                'db6udOGfAzvJUtNqA9Hy6T8PHCuw5u+f7KcWfQOXWsftz3YI8uu2ygk3I+TjzwB8rbdoO1R5SwClYl2wRFnwrlvf+Rmq5TtPA6zX'
                'kuf3a+Xn1/UTBxQ003XSqyiQtp6643KFJeunsWIHNg37IcOSdWAyJcGwY/zR7whjvQbV70Z7B/Ze/inVh6p02eJvoOjjKOfVKOrI'
                'FZVXBAB86D/nkrn01Ky6RJ+GxVdYBZkxZOytsLK1Z8SbVsgMJKz4M74pwoxghNgW6ZaF+kspFPACd6ASfBDyJXQN1RLxZDbs0UIr'
                'YBWFUOOZSBf8x609w9+wwiVvakZgKak5fWZAfLa1+NBkX7KbKzq7CkhZ37sITshuPaVwOm0XVAWJPEr1+ly+pWoZV+Gq1FtwB3xT'
                '3lgL9nA5XBWwXd7AcXhcYbr5niLfGuADeeN9pY04VscVvU9p47dKG+tbVHpruzKpwnpz73ha+gQr7/bZUBQnnJA9Ktyv41ogSu8a'
                'cDLtcSPZTY7AVfb6YwAPoVh/RULdUat1Ms1nA2T7aO67IXNEY7/2q8EymLC/6VcpQ4ynwkz4V5VsPsg20D4XrjzVxL/DRzYiY52A'
                'G0x6GgfwWFM5YG5FsKGHzq9/g1/aqPe+M+XB9SCxQqYR4kh5Ityvwwob3KyjmT4R05pDFc2+X12pshUeeo1JFe1ir1SX/zaXGQMm'
                '2/iDnagwBmcG+QU+fBlyG2qmVMijLQstQAEsRiqXC1AQHEJGQ1DI/Y8DlxEJNLMb/ssp+8I9D3JpO0PyAb5FpRlODfANeCgZl8TP'
                '1MpC0+x82ESUpM2ZNYXbB/o64WN94noBNRnxNB+cLSUQmEuVGr7A48COK7dlwuho33oPHGIrN1IoglSsNfWNTaoou7A0kovG7E+7'
                'VdLvqv9/lH5H1Dam0KlnVJTvsB12XUnQTP2+LCMcdL4bg6PnpxNLzSpuCQiefApB87ePshXi9eRPNrLlPh+kKiRnZ4QpFRDM0UnK'
                'tqt5P/UzvmXbMcJfQQZPOU3Eww0PeijItu+T2vNX9lJwpv5ryhGZ+p6b2ovhO9Ve8J5OO+v9DyhI/2D6MyX33T3Sr9ZbFV8PUpse'
                'GluMj2Ytaq/gvIZ8R+TGM9NCFWSdcQloUbTvGO6rICNmnscHy9f0VyuJWZLl0q+ouakqptE0MtjlawdwIh69B0fPvvMZVrLnI99U'
                'k2mczo1SoZ8VkRYubm/oxbp71F7cuWeUv+sItViWYq44McVDM73Omd1B30hIm9TUt8tugHktl1A69EnFnUUTGpiUtE9SqwDfXrgM'
                'N9wGG1nuWQdsYSTY1w4buRV5N5wXjDsP5omCKnSTVGUt65Qx+QAxxv5BloqiQ9deKLCVnP64n/qq15Q8Oe2Jup07/CQ4947vUMer'
                'SZ/5V8GxgKMjc+F0NymVTiqBD5k0dwk2qbPWPg9eJr+rYKuxoe2qqnAji7RlE0NfncXXa7I+D5tADCivw0KiOJPxqn+JNqZgOcHX'
                'teK2caXSh1rabo4MbfhUNlAjznGoF0J15vp2Z18qUdkpPh6iO8FyjZjLLgiNegI1K7UYQMf2abF9rqP4S1bfzlSouF88n0DwMZCA'
                'Zn5SfkOHk1ot29sQ73eCaKnpVT7UHJ/3TEiDx9G0N/3h32AN7S6xB4cw8aWACBL2RYQrdHbeIBRT/4M0a86a8BcKTizkJvxNUjlw'
                'YQDpsNz9VjdiSmC/NFr6zT0ouVNUCji+fz4qyCt88IoS2KnLWoHvVYjpvTnJzeCjGbflcpn5+tbnXOj/IJC5UFIrXL05hubMg0Kn'
                '2MXYtpoBCw9SiVCk+wDajYWahprivjitBVUzwmCOHAtR4TYpquJEsAaTmQBphE6kRnX3HFipG1eHMhdOMd8NlkOxF9f/n2ZsoIBL'
                'iWhm2cUtJXpyNGHisJLIbtfYLrZe0tJrJmLrdzYTmEepXJ1MzZR83ZSgAaU3wCS9g19CZcBqsIcalLGxXJ+05uwc7a5ol7i31CMQ'
                'aU39nlsBvT0cwtE8DNZACWmvofimQ+iCCJeQ6SBkmzhUt0c8OEcrNex7UK2vYKmPqMEj4sVCOO6vlznICfN0CE0qVxToF6hRoOtQ'
                'rEPEO8Qh9yZYprOf0j/LeFG7o/TUIuG0illwPLem9GIsY0L1vpW+pmMdUJVFwe/A8KY+DXp9VIkL0Osk2F8UPPlwgjYFiOtBcLc3'
                'tDTI81JI7g6gC18Vjp9W4TdAuCWENAaqE4T4Tgz3x7q8j+UvMyyMNMj1VOEpqsqD7fM+BTZhuGp2KAH7h2rD/mER3vV6fFiB/cOZ'
                'j5f9P9qBjc+iE3nWsqRVd4m5q849v34yoyllcK3rGjAEjr1ncPfpyDNz2mg6CWmmmU64GqAgiPyH24iK8C2ALAMCLRnQ2oDAMXzK'
                'gECV4SUDAo0RM//4CRzHJw0ItMu0MrSjEO2VLi191aUvl/05wqPh36ahSSI70jgeX9eXA2S+eSFucojriMFCV0Bv0O0AdDuaK3B7'
                '67l1pUd+D5jqkm9yq6L+iTxPX7nmb1f5fzfP5Oy5B7PMVenbhLxZd4NDmrdWkRVCOMrh0a0D/KImogKA+7/3abCNk+buYsS8DDrn'
                'RwllvGbKgCwPF7eAok1LmjZiXLmLyl92sSZ56M8IjLGchYgx1kUwpky1PQSD7gIZH8ExPmfA+pwBozVD0TlhVCt/j4Z3f1YCQHbw'
                'epudurTHheh28w5nW6qzDyzo6jLCy7GSvxBUU23wX9UqV/B2/avk/G/wG858JkDNHKuhikiKHmlwGIWRlusBxmvDyDzsdteGOUuP'
                'TvZUCSXkN3C8oMMRl8E2XL/fOh3Mg/W6OuRBRX+97h7FUNRdX9r9KyC3g77UB5shLVJf+jNskBJhYEFJISoztENpdxUeY4bSbirr'
                'uNcMJd1UVnKfBYq7qKzlAUR0VlkNIoo6q2P1YA0UxagLZXANFMao44GIgo7qQnoYER3+d/eBfz0g07BagBTKmiHzySKYAiG2zQGG'
                'yRbuPrc0zBPMQuHWuxdy1lJMtMMexsXzhV9QTMAu5t9Ba2UbjnmKmRmnIOVyjFch3EnDlZ4XGHQSYgxBV6jwl5gYFN3RWfqFJjEY'
                'dzbGt4QErEjMJDgyEpI1BYMaTAr1ykoMNg5soQYMCsnbNANGpP8JBgZycBUDTxpBYRZm4Em45K6Ag4RZkIEB24AZ2zjY3iG0d1b1'
                'esgPUMAWViqFCxAdi2UNFbBRFdm/JIiWTHOEAtYtxlHWQVT87VEK6JcD8QqIRk/nKQX0TOUEwwdkhBF0QxdXFvM2xV4qsWTumVpH'
                '+Br3C5IsfJZZMjAu7ZuBDXwip+Yxqd3nHNhHcOv3aXAiz5quqBuNSiDNw5QO+V6quvAUbtYr9JkJB1iDG/pwZbIy4KKLWvErFLoo'
                'HrvAVvuZ2uXUrsvYHhQunjK2uRjbTPvFvYX1T4HzYd73zQPqe7d6GfvOIprCfxHjUzRaaq+fp5TWZO+dVkdf4vaio3Maqeu9eCDn'
                'BD53LLdDWahkC+9iyRKoD7BdZxgVcPTWd95BazYDvNt+YIOKRno9pffySh3Fx+c2/us4238EMZX9CWJaX4uYnqxFTJ4uxAS1iOkt'
                'l/EpGK6PYXIpkcrbu5iVzZDS0Ih62AanAoyoZxyw10uQYPHJBU1ddp2Kh/WJ846eZ4HqcHUiXyGObwWuA3Rz0Se6nBp2JFyXOTcl'
                '/BqLNRDlv18Dqf6G+vdGGNqT3V8hpPr3HIOaASph+Z6D3Dpq+d0BFhnasxWqQ1W4k5MYWhXC/B6qG6lwZ2KaUAn3B/KApnX57EK5'
                'NTtx/Whyw7RECv+FlPPC2eEtfUIe2WRH0LsMTvDpb7OZem/HKhMwwBBxoLUC2KDOzwmAL7voIZdRmYSP7FsyhFsW6y/IZZE2ywSf'
                '7vziykREnK+rl9HmFwNJanVuwk21jh8AVP/BbrCZOsUKW1tXK2743cAS92RT7/qdF5UTr1o3XQypRi+n6Y4JGxIza8w5v8xqwiLU'
                'DamyFoIXPYyEQavp/xEcsY/GaIpo8CP/nuBe4XfGdB4Ob6Vx9izdgO0rwSms397oUkZx4lEOPoj6Q0AJnGE053MKyusQD2zikGCP'
                'ho+cYiE3bwhjg2M2I+EPz5TYS84uj6ZSmjVYDbCGMb3JeQmZviESZ4r0FSHTMZOIPLTudhKYl6jRGQ3Ty3XfEjFMo/G6gNsd23KW'
                'O1QEymN0tiOCG8FZODrazncJDdYWwgLUhV2zIw+cipfGdDS4n2em+ZW6UZ6Y4ycqRnm8iyv1tGK4R7G30Avtoy8bHABDlxocAOgk'
                '2JlrcBKgIwHA4Ei4hbNBdUj4WaV7excN3uB22L24y3H3jQf6O+K5vkFGB73eDTiXLRUc5VmyQ94jhOTX4OsMYF6VNVDlSSr5iMfZ'
                'jImDl7hJfA/dSmmX3csgkp3y0JqwyAKshNgfu0K2Fs3Cv5CUejPh/zG6A20kEf/RVLmu9GQ9WUaDOieQuJkXaVDMHr5fn8WxKoa2'
                'RI3ZRE6b8Ci2+eCoi7FC+TRiKIeuxF7CDP8ImoTIyLqVYKz0KlYFreQD3CumMI/HeHRg7JZCQaKpkAkOr8GGED1QDivpCyVuLFI4'
                '60mQ0cJYyW4aRYlDXInZCg99TqQ1ioRf7VIkDxBHZ94GNcIep72Cz/HdIKpoXCxiYIn06OxPgwW5A7WbjS2CH6GUWip8kyGZrsyw'
                'EubO+whsXLMfDSRCe4CThNSL0KeSMIw3OyVtaOEl8ONXYG6rk9jzhA6nqUS3Az0RJhWBLpqfVHg0eUWJCYwohW37oLiRdPfvh4LQ'
                'ZuU8Wo2G+BJ6myB30uhq6v3D5wrpNuZxCjKphNm8ArYw5ZiF6Wvaf9EVi4MgiN/0C4bI+VyCy9JL36IS4rdDsQxgiLFCrBgcwg7O'
                'QlqgMqBYNpFJtkEpFRk6Wdl6Dy2kFOJ5Dq75C27/ApkOx528oHgob9bZqjtCgvNh/zm47KscxkJ+qMY9YDDQ4j/aUf51sMuhr5Eu'
                '8AhVALLDjQY62KwAqjspURyJRvlondFejDO/X2Fpd9sgTWGLEflQ3Vnx5WOEw0jl5a+MXqfJSJeKcfouG2Qo+0yTm4bjKN4nAZ5V'
                'Xl5jFLGQpx9UDd0XjP2PS3KBj1Arv7gSgvlrr3rtKWKflmHsGNjubgx1l8HvyLrSNWOAvAyZ14PoMaw+0hhor4fey2B8GZ6vB+xj'
                'CH+QMahfD/OXgf/yKADS3OrXSRfy2JWW9JdeXWonkjZSyVqF1wXRoPDVEhPwK7oxVwCs4hj/Q1BxP+4bTi4j+CVAHh3WEVbKpX33'
                'wxUeaDawDBeCzx44Luk9JhsWGeON+rmAL0N+I+Yl3E0q9ExgjLnhdQvdrtqXX/LVPAd9dDLbWvTrzCAW/cdSagvcM34a1bGBb+T0'
                'PCXMUYu2q4deEsnhqOBZh/Jr6FtLtTtLZO0rfXMg7cV2QUhLx2DlQ+BsI0SMlS9RrYk4TPAxDMilXfREVXdlqAWS7gkKGHT06hkc'
                'kpd5tEUXSrb37ym1pH4cQWg4TomDJxR4u6BO8TnmlPlBDLqvmkUStyDQrze/i/EOm2GGc14IQbyJxwiPRUjEAv6KB2nj4DIvbzbq'
                'PXHiAKP2HIC/AfJzfdJYCq/hMVbD0ZvxHb0av2KG86T2n+8305alt2Kt7rIlz3J5AVcAg15NyK/JOjQN5dP++XwqftC6VkPepOZe'
                'YX0/iEXRNzdCV3bH6C53Z109zLVQ8b0VKixTf6aT8i6qrbJMrQvWNbGZZ+O+S2OR2xfKNqC0++bR4pr0hKm6r4GUEnnboEHbC6su'
                'zPBi0BxW757uBELp61Af3wbPF36PkNsNOEGZSReUtyLR636PiA2GyGlg8ZRRpJEL4YYmznqpUK9aTxpLITV4yRrIPnmwt0/952jt'
                'mvYeDyrpzlp9z86i6qSZ3rwPdd84WmTN2cI8ineLGSRSdMcquDYi1LP1cqr9HIbsYG7qKwm4Q26aPuUwBC29YiM7Au+hhGi32x0O'
                'JzFZfLpQZRBfTIUKhVt1VkPeyao9G6RDHcvh+gstvQJbD1yYhLJVj3RZCqEI3wk7MRYlZferTPgftLvISc8xPkrtJJupAnksyp2b'
                'jPgxKYwl7ia9wlQGmCDDJicooZntpSb31+a0+3cq9LRApaeRKIf09Kk/Mo/MqHs6HKGk0A7XZSSGm/eXISCR08HM5YInbkFP1xXI'
                '+ORdhlLcM9QaiNKFtdcbmcvoiccv78FSiDnvgd1F1dhqNDQF6tM3CzJ1oFEefE5MX690DfaMGJMB5ih6HoxbeGhQWNSi41nWsnMf'
                'NHflk7cFiPwqy5K6tB4FehbTai/WQeBIxredvUNnO3GrixPnNFZDIQZV20KFjtMyTpwYCkPFME4ID2hpHCjrQWDQ7QWWwnH2J/sh'
                'MX/3jz3scq2dfu/Jf/Z6jCpzCdTgt0nzf8wMk4iskhH0uiN3XdP/hVmlqucZyIrhQIcM+K0Jv3NvGewO4o+Ns8EXHuwdE6r7s3gB'
                'ezdCzQhRmjhrTYGTF6Gwm6ynYSKU3SkrxRO/VffJFvjthpohsjleW8E+UrbNfR04J8iGktMJr/75Oaz9RwrqsDmn8iSJOglbcc2S'
                'tsif1tWfnbJ4WWubzWKIPIj8kLOmnVerH8DaIuVQH5+Q98n5O+wlPT3jg4LScS9miTmJWG7uWg1wH/9wgdUjjhwIZ+4Eh4+wIoRI'
                '6p8KJTKGrJmcmKli60Zs838X7P+9tU+sg7FXqysvfdSc2RDsjFOaie3vEYBz9/oHDUkFW2/N7Rqk0D2z8U1chH1kRBKqra2ngYPb'
                '7PE4yMgF8owVHiOcvtAAGZ/sw8N0aVBka6whidoTQqlYjtG0pwf6BT56FWzEUTWRt8zCrJLtPr9WXZW8ovl/iHR7e+T8/xA58TZI'
                'zGRc2n2Vbv8OM4MI09qKlJC3tasPZcDfmTgnjuSDeE2M5n6XYf3nMtih+IyasuRt5AzQfCHuzSNnvDZ3r+sb+dC6magAZpr0M5iZ'
                '0qna1gYHHxeayDTy3ZuUtUPpKEcvTiRnyVK5ccK374IyyJLvPaYbYQk/6r14y/OdG3mGPH4Vbnqvkg7yflrgkM8T82ylp+Y1YtEb'
                'R2RIyO/nBkvFV8/92Xf/Xu4TGS7/vlxXePT02briZDSvTWv6RSqeGlp5WhxXQXJsfnuBUwJAvtT8MPlqCveaNI/nVndsNzR/DSzU'
                'vNwRF3PzCAuc6eEZPK5wEwKEjVEbWC8CaIN/Ka0684KJFI1+G+H1aFCD++NG6dOZApZ6ZMPrLMxDqFG4pXOjFBIM+WLWXPSbMPt1'
                'BrG5t3BStulVwM1TByjdDQVnK+63sDci9uwEbnkvQ0tVI7v4Pg5uPJfQml/ur6/j7pdITJMmPoF1Qo0MQK+2nBZ2AIJb6I9x42UG'
                '/9bMQ2ALfI+6hbQo4Efwl+Hc4tYWSq2IpeyYzwX8HIBXJTWbfg/4eRd3+l0dFHp2kngr9xKIuAQ9iGekwpN4RLKI0S4Zez6LsJXt'
                'bEyi8UTsCjwAnkCqJ3Yf0010tR1A/0agrcYfq+/Azs1s87PYgoim+MBEbsYaC2WDKenNgQ9/4O5pPBP6K/UD9IWLpeIoJDlcSkbB'
                'g5zG4/r/Z3iojOoxP+ljgobsH8UOxghmggij8L0Ayf7k8GpFFPcakbCGgBS44EsdAywQt3019vuOKvatI+ZkmHwJkvz0U73oZdad'
                'EH55qm2ChjbF6RasCjgL8psytP7VUN1BmHWr22u+5yElgDu3SE+jKuiZs3aV3EI6nFjy/S7CRT9B7+YY/NIS/06QFlKD/qHP4IpJ'
                'CGyl/uTAA4syww/5LKMno77l3kxqFnsCrFTG2ca8Sh5Z1BXWxM4/5DEbbrgR10E6s8uG1sADmnuW9AJtRP/kELAInb8P2JvsVo5D'
                'nYX1TkItPBEbX6JicC82nGxFU2+RGhxwGpYo0L3g0M+9enS/oXxkjYSklDZTwMKfOigBv/K0gJrX5HewKrtKQ7rtAZ4d4pCBE72r'
                'pQ+qTaH8SFfoddjJVWb/03Cay0weO+B6qDxHVBgl4yPNvfXTJnob0lzb0zXuaiUJM8J5p4IIzS4C89A6bEJ3MpeSRk/OLdPHaekt'
                's3L0LsvjiA1sXLXxitlJIvr4ZyvOMH2fZE9zM4x31wNQJY6rN3boJ8yv6WcbE/Uqbt0GpZG7dJfxIqh+jFt3ovVuat02XKtyDsZP'
                'Bt7GvwRr4bHXfWTnxPlNj5abwSEcQS31w/vueuSApn+75neyNfr3JVLhU12TrhkfzGbLc3mZ6JzH4lKRXQi2SaEmPpRr9MLG6VU8'
                '+YcVu0sjFn5vkDfdvfkGcDSU3dzEemwrOv6G7y31/QBc0+2+SLOkfs0tPS1/8/FcyAMhkme09Wkzt4qcKE4cFhrQ/QNuCawco/V5'
                'jbXc6+mfcs3JS4iI4vbqtZrLU03ULYUpFnfqpF5+vS9B97eowNMb3phNWUBPeKs/nO/h25N8QO57+jDyVM9306zXXnXT1A8w/TfM'
                'BQE6'
            ),
        },
        34: {
            "ascent": 32,
            "descent": 9,
            "glifos": {
                32: (10.812, 0, 0, 0, 0, 0),
                33: (13.625, 5, -25, 4, 25, 0),
                34: (15.641, 3, -25, 10, 9, 100),
                35: (28.484, 2, -25, 24, 25, 190),
                36: (21.625, 2, -26, 17, 31, 790),
                37: (32.312, 1, -25, 30, 25, 1317),
                38: (26.516, 2, -25, 24, 25, 2067),
                39: (9.344, 3, -25, 4, 9, 2667),
                40: (13.266, 2, -26, 9, 30, 2703),
                41: (13.266, 2, -26, 9, 30, 2973),
                42: (17.0, 1, -25, 15, 16, 3243),
                43: (28.484, 3, -21, 22, 21, 3483),
                44: (10.812, 2, -4, 6, 8, 3945),
                45: (12.266, 1, -11, 10, 3, 3993),
                46: (10.812, 3, -4, 5, 4, 4023),
                47: (11.453, 0, -25, 12, 28, 4043),
                48: (21.625, 2, -25, 18, 25, 4379),
                49: (21.625, 3, -25, 16, 25, 4829),
                50: (21.625, 2, -25, 17, 25, 5229),
                51: (21.625, 2, -25, 17, 25, 5654),
                52: (21.625, 1, -25, 19, 25, 6079),
                53: (21.625, 2, -25, 17, 25, 6554),
                54: (21.625, 2, -25, 18, 25, 6979),
                55: (21.625, 2, -25, 17, 25, 7429),
                56: (21.625, 2, -25, 18, 25, 7854),
                57: (21.625, 2, -25, 18, 25, 8304),
                58: (11.453, 3, -18, 5, 18, 8754),
                59: (11.453, 2, -18, 6, 22, 8844),
                60: (28.484, 3, -20, 22, 18, 8976),
                61: (28.484, 3, -16, 22, 10, 9372),
                62: (28.484, 3, -20, 22, 18, 9592),
                63: (18.047, 2, -25, 14, 25, 9988),
                64: (34.0, 2, -24, 30, 30, 10338),
                65: (23.266, 0, -25, 23, 25, 11238),
                66: (23.328, 3, -25, 18, 25, 11813),
                67: (23.734, 1, -25, 21, 25, 12263),
                68: (26.188, 3, -25, 22, 25, 12788),
                69: (21.484, 3, -25, 17, 25, 13338),
                70: (19.562, 3, -25, 15, 25, 13763),
                71: (26.344, 1, -25, 23, 25, 14138),
                72: (25.562, 3, -25, 20, 25, 14713),
                73: (10.031, 3, -25, 4, 25, 15213),
                74: (10.031, -2, -25, 9, 32, 15313),
                75: (22.297, 3, -25, 20, 25, 15601),
                76: (18.938, 3, -25, 16, 25, 16101),
                77: (29.328, 3, -25, 24, 25, 16501),
                78: (25.438, 3, -25, 20, 25, 17101),
                79: (26.766, 1, -25, 24, 25, 17601),
                80: (20.5, 3, -25, 17, 25, 18201),
                81: (26.766, 1, -25, 24, 29, 18626),
                82: (23.625, 3, -25, 20, 25, 19322),
                83: (21.578, 2, -25, 18, 25, 19822),
                84: (20.766, -1, -25, 22, 25, 20272),
                85: (24.891, 2, -25, 20, 25, 20822),
                86: (23.266, 0, -25, 23, 25, 21322),
                87: (33.625, 1, -25, 32, 25, 21897),
                88: (23.297, 1, -25, 22, 25, 22697),
                89: (20.766, 0, -25, 21, 25, 23247),
                90: (23.297, 1, -25, 21, 25, 23772),
                91: (13.266, 2, -26, 8, 30, 24297),
                92: (11.453, 0, -25, 12, 28, 24537),
                93: (13.266, 3, -26, 8, 30, 24873),
                94: (28.484, 3, -25, 22, 9, 25113),
                95: (17.0, -1, 5, 19, 3, 25311),
                96: (17.0, 2, -27, 9, 6, 25368),
                97: (20.828, 2, -19, 16, 19, 25422),
                98: (21.578, 3, -26, 17, 26, 25726),
                99: (18.688, 1, -19, 16, 19, 26168),
                100: (21.578, 1, -26, 18, 26, 26472),
                101: (20.922, 1, -19, 19, 19, 26940),
                102: (11.969, 0, -26, 13, 26, 27301),
                103: (21.578, 1, -19, 18, 26, 27639),
                104: (21.547, 3, -26, 16, 26, 28107),
                105: (9.453, 3, -26, 4, 26, 28523),
                106: (9.453, -1, -26, 8, 33, 28627),
                107: (19.688, 3, -26, 17, 26, 28891),
                108: (9.453, 3, -26, 4, 26, 29333),
                109: (33.125, 3, -19, 28, 19, 29437),
                110: (21.547, 3, -19, 16, 19, 29969),
                111: (20.797, 1, -19, 18, 19, 30273),
                112: (21.578, 3, -19, 17, 26, 30615),
                113: (21.578, 1, -19, 18, 26, 31057),
                114: (13.984, 3, -19, 11, 19, 31525),
                115: (17.719, 1, -19, 16, 19, 31734),
                116: (13.328, 0, -24, 13, 24, 32038),
                117: (21.547, 2, -19, 17, 19, 32350),
                118: (20.125, 1, -19, 19, 19, 32673),
                119: (27.812, 1, -19, 26, 19, 33034),
                120: (20.125, 1, -19, 18, 19, 33528),
                121: (20.125, 1, -19, 19, 26, 33870),
                122: (17.844, 1, -19, 16, 19, 34364),
                123: (21.625, 4, -26, 14, 31, 34668),
                124: (11.453, 4, -26, 4, 34, 35102),
                125: (21.625, 4, -26, 14, 31, 35238),
                126: (28.484, 3, -14, 22, 7, 35672),
                176: (17.0, 3, -25, 11, 11, 35826),
                183: (10.812, 3, -14, 5, 4, 35947),
            },
            "dados": (
                'eNrtXQd4FcX237R700ghhBoIvaN0pIkgTZoIiqCg9OIDRUEF5VEE5CECIiiI0lQUpT8pSpcmRUB6CSSBBNITQurNLed/zuzs7sze'
                'G4X/8/ne83O/D+6d397szszOnDlzzu+cjQeYHn+f/64CTDoO8NIugIHrAXp9CvDY+wCNFdNh/rs9AGUVZSLA4N/7m3HPVDhMH4MB'
                'uopVqQMwmz5XgaOEiI8C6EyfcfCzVPUvwR6MH5UA5kv4TThGHy8APCnClQHm0ucKcJUU8UEA3enzOpznyBTwcMQ/OM6OrgCj6PMQ'
                'pHqJt10IUBk/StjhK6n2l+AqffQCeFGEKwJ8SJ9LAMqL+HBe+6t67Qd7qk3hg+Ps6AgwnD4PmGo/E6AGflgLYINU+0Nwhz7aAowT'
                '4QAbfM17toGIdwAYTZ+7IV26/AyAOvjhlwubpMtjNeijJcAr5oFcH6Y8ODDVKHh1/+xCLkDW+a0Tm3jTaDwtdEcPHD4pIANfA7i+'
                'bt8KppVv2mfB6ScUaz5rjHGXKgDZ3iKAIzDXRwR8s9i8ECo2H6BocYtGBhB0kG7nhJMTWvAe8nsjmVfiztvBHOo455AK3ahtNG7x'
                'cxscADeDxOa3vAswXuqPyQDfSUA3gOMS8DLArjpra+hA9G2cqPXBtf+lhoH1YUbDaZlY6Rr11QrYeN1eUbyeFnowfSC74EPTf7hV'
                'CHkXvhocaPR8Q/NzedgMPGQGGvzqs41eftOW9I0o6nYb3dD6HquQw5hdzwH05F9LJkNSZ/8m56CoIUfCko0hOBXgCXquDtjCkWWQ'
                'E6WdPQdx7AltA3sAAx5xwqvaSasT1rEvbwO0YI/+Fzjjo50tC7BQm7tsNk8EZ3NFOMsEl/K8erZSLnxkNA2vvJp9eVW98lZIChVa'
                'fh4usc91YMcu7w3wrGmetcOPqALYikPtFvwgdWqpNEh83NrwNNib0MgsqKYokQtiCtO2dWSnH8tlPekcik/MAW8rSj0+MNVHUWVF'
                'QlHKhmaK4n0MLlmUgGuQ/UxArQMA3aSbvMSqMBLgBertdFnGl70Lq/BjF2T6UnGBKjO142tIL4Uf6bCHFfsB9DFOdgIYStPaBWtZ'
                'uR2Xw+zwj4GD9LC8XbBek3OjBOFWVJd9SVcXKlpK+mona9vUVYoG1T02ij8GqKKd3Q+x6sNXRquSM/QunNJOvqiOHyYQr1Nv1Nxn'
                '9EbJNPjGGPCpYk+yRSu7nNG2Motu2DJ2dNSKliE7k4oyLu58s7EkRKud06dfGwEOiwOP+LtY3tU+wlKx63unWwn4NVBlt+nwQtnS'
                '3AOuoAR4yBN+FGCGJ3wICo1HPOA+xwAy6rvj1alZqQ+b4WbprEWZLWS4GsLfPoYS6l47jlxh8+QIwHZvpcEdgHxVCfEpAGeg0h1/'
                'SGOq6nWs1VNsFgPsU5TVAEvVEXkWwP48fpkHMERRUMSN5N16GKfCCCXkLtzyV5QLxngK2I7VevVjdT1HdegLrWp+a/GEC7bR92ko'
                'QvVe8/oQT+SXZtXH3rytSTL/f1ALZ2oLMBSteDzCN6LVjCT8NfCF2mu1uExdr78Yq6sOutFZGmr7IEyxngLIUS8cPGpjXG7hrb0T'
                'K7HuRfmYFE1q22/9Y3/8NwA2DstkwQ4uEqEZu44ddjHgMy5eSxdCgo8q3GABO3OWD8BoXBf96MsI4FP5M02nOwkwgn3J4HPHF/j1'
                'Q/FLPe1LfekUzls+0U5of75cu+cwgL3sS5R2UwV7oi37Ml4Tw6UKIFEVzp+g6qyOoyLYrT6FpdpdSmfBTl2GdSqZpalCr2t6bWAq'
                'XPRm3yZr+m+pQrjqxYUXv/KT2gLsnwf2SPZtl6b8ob6kaoc9cGlnX6piI0OY3Mcv6iTAB9aFfUnWBGCK9kU7RT9mw6ua9uf6BfEW'
                'a6Wb6tXQK6ZVNaIQrrH2TGJjH4d2ClzSHinrcOyEjcLkmwgTlfso9l5fXi+WX//kIcge682K3mOz4VDwrHw40QiLjU9C/izUeKLW'
                'OB2X4JLDuYavvY32Yqv2NtLVBxycsIcLiPIr+Y9X4j2CpuXCycbqpXKnoWqVPY7faFw2/Nh7g1CNDb0fqAn6URvgS3eZ9T+CDve0'
                'FUh8EPTP0Q9MlEzh//vh/5OVJihuqypvACxTlB+goIJiyYP3Saug5aK/1v7PPH0biP9VN/2n3WgW20poqlquP/+Ks1zXOl8VdoIH'
                'wFFK0xcc8KMGo37ymvZ9o3F1aw5c1GBc2N7Vvi/nOigtF0mQpCkNuNJ9ov1kjqCmXYJcq7b2gjG/J6oqG9/2OSI0pdEJB4SlXdeA'
                'twBU01bEPLigwb1AU6dIydE1Cu8UuKPVqzXrdPV4z1ChcMubYxUfoXefDTfyM86+V0ffBxzkj8A+Tb1W5HVjqKrry0789m3zoNID'
                'YkGVmY/rpyJuAFz1JYUarqoLBTvZXQkuAHhZuweuYSuVzmA0jrruJj20NL1iPfF0CVxJjulIXUSabhAeshKGSOfvxUFooRr9SJfX'
                'Dxcac9x+09f9Ou73es2tPl1Mdb7loV3KP+W292CKMo176h/szGu+Wh82C4xkfcj05NI3jH5ewPe+h7RnMcNbe159N8YWZJ6bp+ra'
                'XpW7v/n5KdJjfDWNnB+eyx3its19sWk/vaxo6+RfZc/lY5Kknv5bZZ+HR328/0aOIztm3QtMLPUXzt7paQLANZwBZ6Z0KGsJa7+B'
                'HnR95amVuv4+FjQ9Qzt2oLIuAUPxJ8Ei8BQCASKAescdacZfEkQDHa+glK4ulJvieJollCuhvn/QR9hfopn0cqSwscILxgj2tbJY'
                'vhFllMvj5iGuklGOws1RfLRwfRz4N6sINkfca92qapSr3HQvJ1QTKjjLtKC2+W1ACWo7Yd1J1OBTjsxvwvf6xrG5jAmAGESW75z6'
                'ZKMoS0DNEZdp8opd6I/KlKO0iDTGn7QXgSAQVi066iFQUyj7orD/ybBQVB74Mz64OpoNTLUabCuviIDjvUhFAnBPI+hWQXVGXwRh'
                'qWD7p1U47JqJiCUGYIU0puaCbhdVj9dI0onHIoDTUuMSAdYI5cAt1NohP0zu2rBikG/Jln/H87gjHC09hPOREmBfjDq2b5OxX56I'
                'vWfPvLr+lTKyskEqADQUkdLpbtB63BvKUB+A5TKE9qoT9WToc9xI1pagbrRnlKCQBLhslaFPwNVakaD2LliiSFDgDbhVQoY+4AYr'
                'A2rp5PNch6yXIS1ShnC9eV6RoAZ2vn80oP5u6uX39wfJap3cq/8m6GmxAhfuF9gjXezfBcRuuGW7e/2b4YGKqaYZg9yqTobGJ3dP'
                'eKxmiDXqqc2EDBKv1i0PzRGS0kXeA8mL45Mqi1xm8/hMAvaaAJ8U08ymi3Yz3TbZ//nj83o1rBhoqdB7E1VssMlzMVd2ZSQPIEHU'
                'eOzak3E5RWlnV/azGNerNfVogi3ll3VDKnCl6SOn7LYpc8HkyAkk6XNycGVrYLU+nx7mcgNmeQuVrIvXWCW1E20v2RHSeoV2qOUm'
                'u7Wp+2gVdIUrXTffsqX+NIstNdOxzwO/5LUpmuLFZt3P3xo1/IgZTNBStP3xUEuNSdkIPUOOIoD3uHxG089FmnRw1dswu0JNVOHh'
                'He3G4aRddpeeOD7K16IlJI3cB9c0IxRJIPyrAWQ7vKZdGS1CaKWtWKDfvW6W6lGglWtbhxBL9Texhq4O9Hi2Cw9skipjlrp4+Z7u'
                'MWyy6HymLWnP6+FsSTfN9j1mYIMZ6Ct27zuoCFvER4Ir8AfiD7qAyX75Dcg26ZKFAH8TAfSPFISLwC8miynuHaGTCKAx8KY4dPyz'
                'hOfALf2uKiKwj1khBcWBHpbJIZct6kret4TdHPdDgmQb/RaM3SHT53EATTApU3Zp4cI9wRaxTB3dSwTQNJbsK7V84bG0orxb28fz'
                'XWu4MWrvjWGP+4z4pCZzw2bcmNqBpVt8ghWy11KUBKxoCH84LuqoEJC2xLgljUDkUQ1ZCfBPxStF/s1cpgtcMK7jwG1HEOq8caNr'
                'BUY2X2YDF9uqWhfnabW5wU1AvkMyVeAQtym1FraR68JoqcQhcWVItCW4yXv47VSg4o9Kwh7+OJrnAMyjJ2rXFcm30PZqXSrqSOj7'
                'hubop99qDDOSgSvMv2n9lngddCZBeVLPdvkb9zpLngmAS4Mr+QWx+uD8VColiv28mrbD0fv1ctF0rhO3+ejn9KL8xO8n686GRh/+'
                'kmFL2P+yJseC12p/lKqaGINOCZsA5lwiC/TpvpF+UcNxbtlQL6yHknGbOukiUN/czPxO+aWN7T3Ki12GG5KREibSaDP8+nh6F3rY'
                '+NaTI7dpWvxTR8ivEYIPOU/TJFtSnarQ/1vVTWxJJtYfor+Fk31K+VYYGscclo8o5Yz+cU1WLctRRziQO6ATcK97t89jcvIuvV+F'
                'TMWFfpLcXic+KmbluGsmJgzTTbbalEOL7WERKIOdSc42pf3Rt9tU8Q9pOI2M9tPk/S8NJxlJ5qLAu8XUfTG5ude3DA4R7Fim/5QH'
                'Pjxepbj//5XjAc1uHo7q0/ebocixx0TDJHs0/bfZqd8SBHnZcbXqGD7/lu5ibDT/jqoB/ENfECpNvsigtI/baOapsBE/siUr58tu'
                'uuyru7GQzavvBgTKXA1w/TiqpFw/Qh3fv1BCRutuYlcoWN9HUreU8JEH2d3uruzkI52IfkutWfKHJmda4wVqK2Jn15P9a53WqC0+'
                'NylaOhE4YLu5d3hPjjtu7kn1qDFj/+9oOv6dj3+9ZgM3mR6Cdt2s5Y96mdBh6oh5t66E+vX8Wl1WTr9WTjoRPHAH62vn7hflARD5'
                'tyPsOed/3V1aUZXKb6m6aepik6fzobk32Ylrb5gctW2XpXvo32YL75jR2u/EqBYC4wpRE1USR+oSfVSVHHVArdm6HlrNggZ8V8Ra'
                'sWew1gq/7mtVesCZCeXMvXNzTl23nvy0nbknB23ua/X0PMu8ti2hIPfqCjIVl15m157SYm9Si/XjAyylzGtfKqDObLQBOeu+Ndai'
                '8wLg78bVUP9YbZRwSfxUL4TmiKSAz3HShwnkLVcfgbNjmN9niZenvanu8/ZJErc9zXFpNPYGAyQzBZIhjhil0dIaMdq0YhR/YE2u'
                '/39KfHhM3Rmb67h3fdtkN2e+V79LQkf//Iz8d2dMs+ewYN56kWRa4sJ+NcJ9gmo8uTCB1EBdMUYXOFx8ylCLvV9AFbaoi96T9qmy'
                'wPPHHU5OLcYGyof8Hm7tR+XoqDejabie8tA97zETRAfdQP3U9tTC2BX1yGKKS4vfFbIK7YEURhvyX6+2pWCQepY2aVXLOuEtRdN3'
                'VBvWAvVshBOGIamISdU2iH/RPNC/0Uc0adiiFQuz58M19qdr9BVzhHb2BHyyidvzb0CSr6F6l1JJRgv38SGabyhMS9WzvnkwaT8f'
                'zgWGYsTPPoFEm62c4RMLd3yMCYBnfU5Aut8iXisc6m/q+xA867eG9LGhKuVPeRSxlc0CrfXnO0hRGnQeR6uVPFZvclam1hvz1c8T'
                'dPOfIZlJhoDNnF/4Yg+2Zs62cD/RP7i5YmeaLX7VQ0r3rCvrRvLp5ncNnH2KH+ePu6Dg8eJP437CLjtpvd/62BjLuHGGI8LmrPNP'
                'ummKjjfJMHDuvc41Qq1RbWf8QquiSHrpEmcyPUVKd7L87bZx7nQXd32n8/yDdwod6UfntfZQc+QRaAQD8aBl3lnBjDbXN1CKaUeG'
                'm5WrJpT2m4+hemq6K0qhGLIkfCrDu0gDRfrUvUCJkOokR6PXTZOFaIqqBr9r2q9eV/fMuIVxCQwuHEpFpTgFY5oBr9K0evSixenL'
                'QjCK437qCuAQDNI4drL57gddY59r8EHDcYaDOK+E7r+EDpqag9cb5tnqfljfQssHs3F3dlMQ3uUkiVhhCfsIBR1KnzA0g0wVxSMw'
                'RsYY7AdJ6cI1fR2jq+w1D4HCcDLwSnt9pSx2wEvvm58IUQ/hpG7rL0g6MLuO2R0Ark+sJoRtvNZpW/ug+m+SttDPQMhelksuRhEh'
                'yXVRRt6hVURCVtMgEJEaeJ3XDSSg3kS0J10Jlutj3xQu19A2O8LcCsgdKdTZEtUHN4Lou5TujsuDrZqEBOGQnych5Ls8ISO4v02U'
                'kR/QFCAhwWi/OiAhy2ju6Yhfhb60t84sZepney9TK260F9plzzi36ilhT2nt8cGJm3mFKWdWj9S2yn5jEow/dmxijJeIA+56dCTp'
                'cUVr+lcLtVZ8bE4MA73JKLBfn3w+A28mqra6reI+tuRSxZd8VGEmiUGuuL+ZhQuOcVuwGTxv3gfTkaPR50SdGMyGYmqNbggUxain'
                'X9I1P3YDcR4ddQPR3FYYZAbRmQIvudUJp3x8qBkdhz/dJPZSODbGh4bcXt0X6D0gnnq+NPnAbav7VS1hjXp05hWuYEce9LTX8Rsr'
                'rA6O9Zprwb/XhycT8m2pZ1YPi9CHhz0j9tSal5sJxgbhuDje6gFFa1cjjrJhGRzV8uXttJwVtBJQlW5CBpG0aBOqeC0FRleUUcUP'
                'd4GO6maU3Ey4/phR5TY5ZNxQVKiy3VEkWIO/G0rdX94NJVt/LY+/LeeGkmppdUM3kgPajHrhrmi7G0rKyhtu/YDi2l7VU5+tMvVZ'
                'FRQhkFLRQIPKtxi3jZ5FfgsPz+3cw+5P88Ir0jN2ZMafXvNKU8/jAV3+9wVsMRuw/hhAph3cF/AfqumDtQV6Pyiw5DeLW4q//+9b'
                'NI5Zv138w2r1exV1fXvOoRt37Zmx37/fQ3eW+AwX2EpQsFrd75baa3p0yYom3u3rhtQp5RdZb/DaHBX2pdV+v+GvCZt8N1n1n8B6'
                'yXgThXszC1qab5Rwqxp5YUe61xilSUGA4mmZ82QF8LgkygttG91AQkvtm+6wBQTvngHTtT+Sr3uY4ItuNWGwe70Z/AxohGwJdu8T'
                'BpOVXe5BFfYllWef0d/Ws6oPT306X79Yu6RPUHTXeWTfYnzuUvtMz3Kduk3zHRkrKMbfdxLGydwjsdlFKRfXja3mYTQRQ6XN/yhm'
                'Ph4E+7P0wX1j/+5/sqj6c3xBzU6Ng9iu0SHOcrddiSI1JIsZNmorvtWm4Tb2JM1pmn7t1C829PofdmaenhdtnndWMh197CVigT+o'
                'vA8BCznEDbAGFoHsM9crUiXLoQB1DpMqHo3bpKJnpdWjJu4GCnpIK0oD9NjldJBWmeboHc5qKa087dCxktpQWo1i0QqdWNttzS2s'
                '7kGhWOsjYz9QQMMX3vLqFkhCbbW3vOIF/kjGOS95FQymLvnUS14Zg8m7ucxLXi1L/AS6lNf7KuQ4WddNq2roSeC8CaHvw09x8rT4'
                'jEqeUXko0rOMwDEBc0xytRQFds0yr9x/lX/3smTquq/yTBNlSdtQ3BIG5Xxxo9HRWEtTdPysSF3vxcoMX3YF8kM0HGf5eA2fzIPa'
                'aAtdBL88puEVnLqDBH87XsfJAlhDM5gXRRp4f41g1pjoBwaOhlC1CR9SsgADJ/2F1AFLOqT4iXgLlcX8NHMbCDgGSeSHMgPcQzL+'
                'Bql15RwsCFTEETpKJ8eZcKJF17qo+oYkHFWn3Vy0Srg1AzQ6roSTdYazcWS8qc7gl3Hj+KNwsFeTmJRl2dhZ6wFzNnDHDAeHhh1D'
                'F0tLE7YM6Vv7zVhNh07I0jEyfJ8wYxULtUg6AyM3oxrWJ2CROZxuJGDkeoizmLDQDNWQJmI0DpICTVjAHWYJkzCyG2eGmTC/GzS4'
                'ZYwYxrllTJg3muY+NGEUEW7rYsIoFOCoGeugygMJI2qnG9bcA6Ywt09ZTdAP/uZiWlHSL8uf8hdGRdC0HF3qJAzW17Coc5I8Ws//'
                'JIoIO5lzWpa2lO+ynJzP+5mBzofWui2aY7X2RY0sg54E2GjsJCLRMudCR44f2lNvi7bO5g42x/qCEAqjqTXOcmRJtMnmwU6MX3XO'
                'yJmgqSZ22ot5sHtilXZ4Mn3iyn3ck/UTRcplSzG/V3I9Xn8nGWGPuddnKYk1W4hb/Z9j+7Kxiokd6CyvWNB6lyg2uKlDjQAj5ui3'
                'hpoScYmzC31p3GzUGC41z+sBQBR5ARmzHynlV64TEfvgIDeoVrogPd9N+q4xeGauYTAdJtIlSw1dfzmjKOXcZ30D5DUt/86+WdXN'
                'i5zrowDzqrfNR18WAx+eTU7pMeI62aqQgmPFhXMxEclEgIydj4sAOXb6/OovlpiuId8l4KFZBcwiLdd0p6/clk8Cjbagg+fdmv9l'
                '9rDfANwEQEBxAmCIdzECYGNAMQLgoKUYAbCwGAFAa4VHAbClGAHgiipGAAwsRgAsK0YA7CxGAJx4QAFwqhgBsKsYAfBBMQLgeWZ+'
                'chMA9nDFL9GDACBy8wR3AWCv51kATPUsAL709iQAXPN8PAmAg20UswBgJKSFHkaXH+0Kx3s4QXRfZ18PJ6j2Ba08nIhCX1h6TWHK'
                'pRxd3NaTIn2gsgflOq6MOAkCao6jLvjMNDGIeZpvNU2WVxgpVcZagZrQSsRacwa2iL3GEyMIWPk73DmtYf41X6ZcLc+61dk50q0d'
                'a6u5tzerlzTBLdVHoBJia2feJCJfIr6Eqb21bJzrLtb5fZ52Q8Qi81XPuiREUE/PDjVhFXH2v20WNkgCTws0YbWcFI9sEko4rxMt'
                'JqyRZoxtu/hYSmFewtnd7/evTv1X96jYWeh+aX4XZCSATIr7B9YI9CtTr/34r2IaU9YXThTSji/MQWmkR5li0re7OTKR2eySuVYN'
                'cAq4Nj8X5R4/mLZjWgdNt3pJr+LdpfynYa8c0Xhz+TqzILDdhK9VFrR0l1bkG0yV3afLQSLJ0BWLNBuBfqCE/UZGEqRgZoUyP6Gt'
                'ZuE0gyBYlmR943XgPDS5M0bbRbR+l/jP28yb1svlTKSGlSjwA5uPWLL3XEKuPStm8+uVeOIkD3nZHgSVHIBhbuLhL/RPgAZj4Wnh'
                'JFoU7v6Fecb8TAGBb5MDLE9WlVCWX0bqoqSXbKdN+NcSEc16l0y3w6TQqBGsFIhb5HgtSLopCoDLXiwJJNyd3SLct+Sji1BRdj2h'
                '0W7k6CE8xmbqyO1+2pVLjP42JsueceWLF6y8jukWd+5UPXO0mFLGTjr5CTHMRFG1n8Jw2o3bpUjpc4zFRZyvVxU5frqLyhA7K8Af'
                'qgwxxidrZCgvaZxPRuyzDyT+TU1NwqfqXJStuvetOhjpLtFWpjHbiAe32XiAGg+OWHNFpfRoNZ01F5yrPcuHpKDvVVqQ9EKRkceo'
                'oA24jW+azPabr5r4RLYfcQPJILXJxA0kJmEPFn42yMw73ECEDhPLDVmKtpI/u7EUidNI3IvW7h5UIsXfJ1+yGHYl2+9+L6reX0hR'
                'cGcUIdMlvDhDDDInfcypSxtKo1G5PQgp47ZSRXoKLLp4xb/QyJfqlQk3hbinHxlf/aDBWn8Yp9FNPULRWshSM+FV4hQ9OrH7l+Dg'
                'Sn879c5kzKmksWCcoaP0cNuplLxEbcUgLQb0NNE25+qhu5+rCV94oH1dNkpT+e7Hks9dPDM1SvkYZkDbqKZqZfpqVS12qQLXAiPZ'
                '0OzCA+PUqJNAG5kl8LjD8hc25pPiB73jD6uRtDVVK5N3NtOWfA1K52xV2Izgl9kBRYHMeqslx6FtTznGVo7iCbo6MjucFhARWMTU'
                '41s8S1ZrZgPfLqhpR0nCVdF8XNjwQ4pPtuDdRgbsJSIpDVF4ZIEtgOJAa2jnadqXXqXnYMEn1n4ChbTpmxWUPE/H6gB22PR/gpgr'
                'Fn01W41A06AiOJgpUQjmsBE+RrDpyVkaujJAjwmax/J6CEM+mFTENC8xaYwc1kpX3Gxw4ojOpIVLYKK6HGHmt1ejVf0vi9HpIfE8'
                'mRBmDDC6DfX2VNU7j2T67IrGvTmHPyBGI0VT8JwuuNq5+IxBdT4hTGQoZpVnGT7VFMK8ZXEkz8tnmtgSNCYHIiH0uqzsYuZkHAtO'
                'k1wJSRDiq2XN4pJb2AptllPNAWt1Ctx6FEcw+tVugilzMfHX8mvjUE0Sw4yb2GmXS70gpKuwovza76XaL7qJS/K9ynxTn6Bt/9s4'
                'Ne9KZJouTYNuEP1N0aNXOmn01oxygik3PpgHSvc3NPdM5jkMT5S1fkyu7HqMOLVJEabF9jo5by+KXVUNFYm/V8zWYwGY9EN5d9qX'
                'IoQczcWAa1sDlbyr93XVXLYJxC37XV1YeSEv52dfLare8YiWiMZW30hBc4W2SVVyhaWgQhazGXuhf/WEYeDAXZyzJUXNF9aV23Gl'
                'do7Ao2G7bco2ifYgOVxlELMf1DENApzSyIi+H6X1Tw562n8Nv2+wt+nSLW2CbBCMICf9ZcyKMiwlyvRDFEFFbRR3CvBoE9bObs7m'
                'gMYsTJlwxKRZBmAI3e2yph9+hSOpuYeAjyEmrLODJ/4WJwoOsP1yVKASjJa2eJOI8UKGa34j0x//XQ0Il46eLndRVhsn4vfyEFZC'
                'cU9/PVzGvHEO5NRTfjvm8vCk+wZL8SAhD58OZv/73/302C4xk52Y4U7MfCdmxBMz5UkZ9MTMemLGPSkTn5ihT8zcJ2X0qyFk+hMz'
                'AEqZAcWMgWImQTHDoJR50D9XyDkhZCqUMhiKmQ3FjIdSJkQxQ6KYOZFlVNym9mt/8yc3tf3Pfv5au1jPnVbTcUtHSRbB6xrqBjqu'
                'mWACc7sHbZNg4u8kYUoCH9xIuYYJ4EU1gOlNlwZHILhfE+j9C1lKOCUCt5drDYH4aCbBBL4rxvvWjgXXiKfdBMHT9wf5buNrvxL4'
                'EzhVRS/iCqSrFcR09SfV0fvQXU3NaVfIVJ+Icd8l2u5d/3oAk3NllhTqBsY6JutCRiUqX3q9WYRveJvFuLpgsqopunUEXXkuMf8Z'
                'UQSkaJn+6nap/sw9CTk8v81WJfhLsRX7vOUgkQNkGtk/tFFpfy+2/T+wRxAGKF8PJArKO8qDAxnG5iIKNakDZ3W5EPkzXW8u8cVa'
                'hFtrvcbyARwok2Hk/0Df5AGlpfaGg9SevamslJpx6p4t8ceJEcQSOJBMpD3x+AOB+h9cupt7ZVEtDZjMzdeF41XgY6PfXmMABkz0'
                'K22p9gYqg/aGDNin+g3rptOzQyC3vKGYOaOThcRxvhio/WIy3zhqLo1FyWL6HBQyXyUL/U+ZCb/z9Au3a+gR4D531LvklDWSwrmo'
                'HrBblWW102inw9py7plIS5WJqJfaGxOw1Gjt62p/TOH9YZug9djDSy5n511dbPRlwPBvr2cX3jyx7Em2Ex+YbMQZqNtlsUzBNbnz'
                'WoZbKjYdtXWOEoK3vlFT2s8U1ZcTeokp88giKJrRSoD6Og9dwwa+6y7mvPnv3a6PJhWbqIZj0nWIqSbnlIecuY+E+lVoOnLLHHVV'
                'ldqrDEuXy0qJsd/dzM+LP760lymk7QOKQfmDEa9nt92x3T4wNkhDSmlRfjGNVKTEWSMyYSNDSFwd7hbuX3d2gRo3U82lO1nb5jME'
                'bRIJ2uZ2MkOOC9kKQvHvpnuhbGsl8u2nU0bZMmJM53RMnQ5BYpylh9+4X4fuNUW6F0s7G2jMIESqY53XqHVupdaZOZsOPhFmrTOT'
                't0sJOW9uuxKppZe90VjvwwE7koqSDo4PNvo5aMzW+Ly8+A2DdOV5oP5Wl5iGRqyYduQ15cw72Nc/2t+/9kQcNDf9WWJ33eRd/jrz'
                'nL8k2ma6MfG5Q6RB+jnpnTqoUzscDqfT6XKpy0BokNtyVqGCGxQVKhoM+VFoSr6l5rla4256sJvelVACW5GgE+rCZw/ge/3CTzpG'
                '+obUGri2QLULvOGS9l1qy4xYmbQ3+aPzeXrFpQx71rkVffR13n/c/lQ7t1GG85G6mhtT9IIFn+en1S26yzXTT+AknBK3icd0dVPP'
                'OvErBelv/hwFxfv5HbJAKHPUJBDCLponxQpSILqG+9eelqdOnJounQfeLIchqBPE+hvaNSInBAJKiTw+kY2MQgf5ZC8tugaKEQjy'
                'b7yKzNehlzvo9wqme5GYvmGV6lPL4K43VevM8m3s6xJmrTUtlwuE8CtS20nKlDum989y/jIq70HfJ9nu/DguiKwuckA9Ja182Jyi'
                'NUfaYjfK5Eayfe/3rBfpW7ItuaEK6/B0ZfqhigUDucs16crjN/6SWJCfsHNCuCc15w8pR8/6JbPw5ldteXl4rpFODMvzjEaMVNWO'
                '/b0i/SqMwbU/2Y/K87201xpBFyyf8jasaFOSBfMIunmWiroQehfWivVB5XXdf3sZNeaO4j+xL83n/pV/2vV+7bO4437//g/8fJx7'
                'QVurrhv2XhZMIOoMUHwb7CGK3GdsfA1VPzd6KZ+5Mg4M9flD9xLFAH1wOi/3MYAxTsZT0gH0aDnHGH/igy0o7GNcI/A7dDU8alw0'
                'At0ztxsYd4lG38flSsZt+yGz9qcIoR64XO4MFCuGAvFiWRF4Ev/kSnmx6tXRCXEtSmxLVZQ81yuJjYtGQlJcZbG1FVFjuVlVbH4F'
                'TIOeUF3sj3JY3du1xA6ilLhJdcQei8SFPaX+7zkbfu0fu3GdBReycs7PZZ0QPfN0esG1Dyvwar/K3zyXhVrn0AL1e3Zrdm6RLtiy'
                'S4/Sv6eWVKXcto5hljqkPO8shF1dS1pqLWEBL8lGuvFPjfdFEAE0hs6d8DLernCeS0J6uQ6+L073gnnlClYtXD7qiVIxgc8WOtCn'
                '1VIcm/GMW6bTqNr8de5Xzv21qt13WSUMzD+TXpR8ZJpGcrCu0PT8fNWNZREzyizmrli4NKCMpfLLaSxcQIl26Plto/GhJPqRASGr'
                'tBDf8zS5hxfp4us4hW7axNcGoDw9TtuaWqLKFRul8QIUHpyS5v4b+Trv0LIi3esY+XXF+jzKaD2VHLpppSI6gBN81XZdeLa0X6Vx'
                'KWq7FMuP5rYr/iv1/tF9hA0XnMUAhKPTo/6yUP0uFqr/0PL/l6nl32Zq+Y+Zz9hDrjH7dKqzkL5OYDZ9G35dwjMpsfF6vG8Zb3Ua'
                'fumjjY2EQH2YzDRGTFfja0P3cfQHfCXd6409twsKEs9sHsuMsAPvGdML/S0dRTtNGKOIJb9cN8i3TIMei66EUipIKaG9txOKfOU3'
                'TsPbojNmJL04ckFfIz8dxekTOeiLHpqiM/eCes+Lekaq8M7vUJx4rninBlfFhOYKo53lSt5y/Au/mutqCQ7IVIxkdB0Y17ikX9l2'
                'JHg/ZZGN+pFURvF6xpiPx1Wj7yMLTmba755f1c1L1w0MU8MDF0SCwaziC//yff6fhcti4ZSRz5DxYYwYHqRgxT8eLFBQ9Vor88SC'
                '8sQ3N0hlmoWi5q4iJLSb9L8DlMNFSjHeCgyTkLvs8hd6b5KSZdBZ27EgK2SX7laHc6U4BpDPYGfrQP/aLAEiAhZjnF3fzExVVWJ4'
                '+USVZartKnDCkUxb4veDfVk9TktM6CeJ7jqeUlzoxwaKWCptFyZ3WCFj/24TnOSj1PAQfLXZTS9DqL+u5e3U/d/O8tzVvkLnbv6g'
                'Ze3h74K4psdp3OBuYsyGn8Pl3HRO9frYeG9JNfWVD5YMYVgdYcFU6IG85SXU8BTj8b6riO2oG26TxBZy8f4xRo+q1ph8CcfkUDNf'
                '9q7jolKmlzKZQweJPKm/33mirqYQT/OCMRkexZEeq+gv8uArJXIT863eGdrbo8kTyjkwvRkjcRNnraJFMs3FfcQfsqidcZzxGeqA'
                '1Wc5F/Q8ixysx8maSL944QM12W+kS7UZJqsaK6JRvVRGTz9Q3260TiVknkM+Ml7xC3X4TuRCdz27wjKqxW32ekNowpndyMLsx5Kf'
                'zqUro38gSx25t8hquQxckay1Y0hR3KKn5xyPVzin9tB64jS9rBPZ/lmBU8sPQ7pXnErhJq0Yp9Vg7lRArRqfeKqXQeg+B45Qrtyf'
                'E14ZtpxNB3UjwZSG0QJPW6fysWRaupgvAwYfk15hcVuiXxcFGm9vUNm2FTMEKvxT7B2MvYG/eArPZqrKP3I90xhJ0QeNy2fIiuyP'
                'Fd3rrY70PHVc1s1jTL+2DoMhjxRh+yPht0TeItIkY9GeE2cEPoYxi669pcgxI432bYkyhRd3iVQoK0uG/YtVIv2npYmMLiLB9ewp'
                'vFCtvHoaI47TVP3fGzvvrL/QGmJJ5zP3Z918lbf4iF1n/uLUtLdQQmIF+g6O7tgQlIq3dOZWSWztV8elKAUkjCb6DJFeCbOT9KuA'
                'LEG5RKa+I4rNzpUCNXWragbJ5bEF3vGcIXRQrxQOznhW8+d0abBe6ztLGldPIm1gL6tzkRfzab5Be7GDCzL91dVPN4ruZtINpV2M'
                'l9CM/UwrNkiVvnfAVT0kD2yRUpjcnNESm1qp5ISk0+xd9BK9k4JZFFmAmYNL6RVCBaaXOixy98RdFLV0hccCmOIAvY+Zwo59amCw'
                'YKaQGq23vqsyQXt9Zch2aYrVlNNK9Ob9RnmQHLaxW8h++pwLzgshxI/a4E5Fo1grA3IEymHkDXAIb/IKOCbRKL036lxdhUeXfCNo'
                'okjVPSwQNns64JrAIm6SC2lC9qToJCmEN/QCuMTopRmm9v7jN8oaSXvekeR8LRajP3vJAS8F8NepD9ZIbjCjpr+x4dsrJcZ5T4pH'
                'EV4/sEx6ZcqvlVZJkeF7BGa/Ur5QX669I3vh8pRk1dzBZBDtoBiloxUVoQTJmibpW+45ehWl8ZjruqS5cFK8H/G5hbp8ct9tkNsu'
                '94vcZ9SfU6trA1jua/k5YFXfP5pSAIOR7lj9v+HfAee92B3jgqR+vh4pljjjBJ9WaKv9PLOkvgSDoAiliaYvUuEaK2KMVdP7K12V'
                'BM9JkbVP8S+b5JzInzQJEqInxH5+NkMozXIK554gZ07rEC/dJnFQES1/I6Wg4Mekeja7vzbIbZf6JcroM68Sj+DESPLU16bn4MyN'
                '2/Fy8K9510ih67gyJi/r/Gd9Nfnr/9Z1pdFx/f2km4bVsZZo9HYiJHa1e6AxH0KT696BlSylO72nvzAs/x3L8Nu6QGwwae8tW/qh'
                't9FQ2TjSczXKLrlli19Ilsz6KmPrdm3F/wYcbWxtcgyuWUZAMikp4akw+BvurngXvtrH1dlhsHcjf7HcTPj2FbhNDQm5A6ND8L2h'
                'LUu0/BniApTWanx4Mvm/q6y8XXRrSTn1DaXmd5b/H3pXiSo='
            ),
        },
    },
    'mono': {
        26: {
            "ascent": 25,
            "descent": 7,
            "glifos": {
                32: (15.656, 0, 0, 0, 0, 0),
                33: (15.656, 6, -19, 4, 19, 0),
                34: (15.656, 4, -19, 8, 7, 76),
                35: (15.656, 0, -18, 16, 18, 132),
                36: (15.656, 2, -20, 13, 24, 420),
                37: (15.656, 0, -19, 16, 19, 732),
                38: (15.656, 0, -19, 16, 19, 1036),
                39: (15.656, 6, -19, 3, 7, 1340),
                40: (15.656, 5, -20, 7, 23, 1361),
                41: (15.656, 4, -20, 7, 23, 1522),
                42: (15.656, 2, -19, 12, 12, 1683),
                43: (15.656, 1, -15, 14, 14, 1827),
                44: (15.656, 5, -4, 5, 7, 2023),
                45: (15.656, 4, -8, 8, 2, 2058),
                46: (15.656, 6, -4, 4, 4, 2074),
                47: (15.656, 1, -19, 13, 21, 2090),
                48: (15.656, 1, -19, 13, 19, 2363),
                49: (15.656, 3, -19, 11, 19, 2610),
                50: (15.656, 1, -19, 13, 19, 2819),
                51: (15.656, 1, -19, 13, 19, 3066),
                52: (15.656, 1, -19, 14, 19, 3313),
                53: (15.656, 1, -19, 13, 19, 3579),
                54: (15.656, 1, -19, 13, 19, 3826),
                55: (15.656, 1, -19, 13, 19, 4073),
                56: (15.656, 1, -19, 13, 19, 4320),
                57: (15.656, 1, -19, 13, 19, 4567),
                58: (15.656, 6, -13, 4, 13, 4814),
                59: (15.656, 5, -13, 5, 16, 4866),
                60: (15.656, 1, -15, 14, 13, 4946),
                61: (15.656, 1, -12, 14, 7, 5128),
                62: (15.656, 1, -15, 14, 13, 5226),
                63: (15.656, 3, -19, 11, 19, 5408),
                64: (15.656, 0, -18, 15, 22, 5617),
                65: (15.656, 0, -19, 16, 19, 5947),
                66: (15.656, 2, -19, 13, 19, 6251),
                67: (15.656, 1, -19, 13, 19, 6498),
                68: (15.656, 1, -19, 14, 19, 6745),
                69: (15.656, 2, -19, 12, 19, 7011),
                70: (15.656, 2, -19, 13, 19, 7239),
                71: (15.656, 1, -19, 14, 19, 7486),
                72: (15.656, 1, -19, 13, 19, 7752),
                73: (15.656, 2, -19, 12, 19, 7999),
                74: (15.656, 1, -19, 12, 19, 8227),
                75: (15.656, 1, -19, 15, 19, 8455),
                76: (15.656, 2, -19, 13, 19, 8740),
                77: (15.656, 1, -19, 14, 19, 8987),
                78: (15.656, 1, -19, 13, 19, 9253),
                79: (15.656, 1, -19, 14, 19, 9500),
                80: (15.656, 2, -19, 13, 19, 9766),
                81: (15.656, 1, -19, 14, 22, 10013),
                82: (15.656, 1, -19, 15, 19, 10321),
                83: (15.656, 1, -19, 13, 19, 10606),
                84: (15.656, 0, -19, 16, 19, 10853),
                85: (15.656, 1, -19, 13, 19, 11157),
                86: (15.656, 0, -19, 15, 19, 11404),
                87: (15.656, 0, -19, 16, 19, 11689),
                88: (15.656, 0, -19, 16, 19, 11993),
                89: (15.656, 0, -19, 16, 19, 12297),
                90: (15.656, 1, -19, 14, 19, 12601),
                91: (15.656, 5, -20, 7, 23, 12867),
                92: (15.656, 1, -19, 13, 21, 13028),
                93: (15.656, 4, -20, 6, 23, 13301),
                94: (15.656, 1, -19, 14, 7, 13439),
                95: (15.656, 0, 4, 16, 2, 13537),
                96: (15.656, 3, -21, 7, 5, 13569),
                97: (15.656, 1, -14, 13, 14, 13604),
                98: (15.656, 2, -20, 13, 20, 13786),
                99: (15.656, 2, -14, 12, 14, 14046),
                100: (15.656, 1, -20, 13, 20, 14214),
                101: (15.656, 1, -14, 14, 14, 14474),
                102: (15.656, 2, -20, 12, 20, 14670),
                103: (15.656, 1, -14, 13, 19, 14910),
                104: (15.656, 2, -20, 12, 20, 15157),
                105: (15.656, 2, -20, 12, 20, 15397),
                106: (15.656, 2, -20, 8, 25, 15637),
                107: (15.656, 3, -20, 13, 20, 15837),
                108: (15.656, 2, -20, 12, 20, 16097),
                109: (15.656, 1, -14, 14, 14, 16337),
                110: (15.656, 2, -14, 12, 14, 16533),
                111: (15.656, 1, -14, 13, 14, 16701),
                112: (15.656, 2, -14, 13, 19, 16883),
                113: (15.656, 1, -14, 13, 19, 17130),
                114: (15.656, 4, -14, 11, 14, 17377),
                115: (15.656, 2, -14, 12, 14, 17531),
                116: (15.656, 1, -18, 13, 18, 17699),
                117: (15.656, 2, -14, 12, 14, 17933),
                118: (15.656, 1, -14, 14, 14, 18101),
                119: (15.656, 0, -14, 16, 14, 18297),
                120: (15.656, 1, -14, 14, 14, 18521),
                121: (15.656, 1, -14, 14, 19, 18717),
                122: (15.656, 2, -14, 12, 14, 18983),
                123: (15.656, 2, -20, 11, 24, 19151),
                124: (15.656, 6, -20, 3, 26, 19415),
                125: (15.656, 2, -20, 11, 24, 19493),
                126: (15.656, 1, -10, 14, 4, 19757),
                176: (15.656, 3, -19, 9, 8, 19813),
                183: (15.656, 6, -11, 4, 4, 19885),
            },
            "dados": (
                'eNrlXAd8FsW2n/SeEBJIgAABISBNaSZoaIoIXEC6IBYEFBBFUFQQpEkXURSFK6GJdAWUIiIKhI50MISaBiG9fkm+ft6ZuvMBehve'
                'e997+9Ps/NndmdnZmVP+58w3HiB6/B/8Pw6g5nCAkP7gdO8MxSQWMoh+6PfugGmEJMNz/+iZ1zQJPiKkL+yUNe+DroQsgbEC+pmt'
                'AYRcg8YCPwUHCKkDmfL2+fA+Ia/AV7Q8E/Qj4S5sPH5LPv4hffxlWC3xGWhDyAZ4XsAwZ7EnccuG6hSYXaqrdxfGIwmaE7IV+ovH'
                'q0GuG/EodIYL/BxsJDiUZ2RrK+FlOgALJE6HOoT8QgdAHZOP6eC4Dn6VpbqfJtsgfff4uljuUSb6k0dIhAl+ajrleI2Oc7CSMZAf'
                'pGpbBPuMqmfDdTcFOgEs8lONfg9QlpHasxIDPgvYG1vXsNEgoc8dMFsBsurLjvoNNcEeo9fvgCNIge4AUQrMhWLPeRsG1vOdfCzq'
                'XRvMIUtpvRb6Z7MXCXz6i8MZduft7X3k+007ob32VH0Mpuij874EXtNSLJfHuqkL37EBWShhF7jUxr99irO5wHPgCfzbCyYKPBc6'
                'MvyewF3hQmu/9il0ZhBSL5aQHay+lXTkV9i+JsR7Rqr12tvupPYy2+XB7rKZmkutV1/wkKjGYsuNoZ4SVVtkTnvFS6KIheUZo7xJ'
                '1Nf5FfvbIU689boPIZE3aSs2nAxNfOldi2FdrZDR9hT5XheKaQWroInAF4s4bibw57C2VvBIe5ZstHomrc/RXw1LrfWFFYef5OX6'
                'K9OtuZs6yEstS/kkilSLMrVzYGSnTRECl8MzLuKgCHq74O3wrQuOd0IvHTcrgsK6Bny81HwWTvtKWDvf3rnKLVhGy+dw2NfCh4S0'
                't8MQtkAbB1uBPjsZyh8i5DpUaQVWOibuP8LVkAB7GmkHwCYeVrFlGHxGokDIGqzCYokh5CjcqimEB8zDU5wFskZU924wowTgEo48'
                '6VnCX982qxRmsa83/2J5efLiGGzU1rw7ZN39Hx3P8jza7np4B/+2gWx/QqfKHPpCDmiEp1lwmn04KvFQtDAx8TTQNY+rE+jrfwBl'
                '9I7PWH2IyunpdX6tJ7DXruzkY38ePub3nGPf0g5N+YKdT0+xzpwAel4LE9hUxJ71hb206HYGetJzD7hCp4tbKgzmovMQPTUEXk0m'
                'n/xb4Ud6eg9MdFa/BFCF94O+TAeAR3n/KRrKr03md37Hn8titTQGNiXnwGHaXjprrxdcxdbdzsLThAr/n9VMyPqE3Fke80kALzfa'
                'V3u6/UYnLHu9b7ndjjT5GVYU7Dlnmc++dt8UgJ0x/Mk+tMzkUuOfYWXBnvOWeUFkui3lSfrsFEtmuzGLZJ37a/9eu+zoADfJfUSp'
                'usaY64r+jPZQHMBi/mcTwBTUZAWVWwC8RSZCig/ZD8/ST8bVlzyfBBip/68q9c9hE5sfb0BhkCx7pcMH6sJQKJPajrhfBmMoB4Al'
                'SoHTXBsL8eqor8BBqiGl0AB4WIFdhoVAHgaIV2ATJKpyjAO6KLCcrzZ2RFnAkHuLIFkJ6fAyeEldmAnpSiYHF8IYdeFdyPHXxVfw'
                'zKTy/H0DedU3+MCtoLP7GJieD6z5JcDrbGUwM2I35PiRzXCLtfkE4JQvEPaGVzl8Xo1+DXacgn1tAAZKlZXyJMBfyIuFp2vhKs7r'
                'AfAkCg54m6yAMnZlRPH5OvSKyzMutal2PLEd7MFN1oPHAUVxL+DLfhd9Mex16XOBNZayXpOaKaDUGyEhsy6VF+wfhKWqfRaesIHJ'
                'mMWseHzLW7F/5UWuo/4bi4vVIrupFUntV7/7rdCctr49vSdP/vti1CV5ttVdwoIeOwAwCeV5PW79/AalSkOhccOkHz8GAjylwCQA'
                'NZ09k+G8bjL3kOVHLGJ8qXK4BSf85HRMhmS5fIJOQnpNUfbZB9kNZKXboOAhUXZbA6WxsqIvoLy9LFfSJMtYF0AqD15+3mS5+e1f'
                '6H3b5L9vwJm/Yt3gZmGBLdYDU1Di2AnlAQqgCmipwIugrHLithuyvUXTj34Hdj4l7Vixc29HogAk9pRPhD26iQ2vst7A0VQBnzKY'
                'bVy6oQkF33K20vgxEeCljoffi4/2rfLYOidc9umk3vO3OsQ9duovV0stt3cN81ZPjARNUNYs0dEue7KBXoRF3ygUWZAZbKAtqH8V'
                'GkAtXonCss31DbSOujkS9YBrvgqF3OTzhaNFsIkYaIeuE0a6Itm5b1yE/T+Mhqga4+4CZuPuvxs4DhWbU7+Oc6mafr2B67pEe0e+'
                'gPLkNXV3eIqmOMgLoNmNkcAGTOgUzV4nEQBTFRgEzGjg0uky5AY0O/p2bJRX+IBkgKFUNfDD/jZOyi7LTqSbTUmLH5TLLuF6uenY'
                'G6HM6neK9Y7lCQB7OgT5PjRvOjqHFbBOuQ5zoLCSavkKLFXlICf0U6AlQJNGG7LMaaubMQnfl1vP1mfxs0NmRp+ggK5XwRzTGRcD'
                'Wz1NnfDZowA/SZV3oRY6XVJfF7iVaQC1h7gtEUXJMFFBEwcqVq+rkNE7MLxXOpQ/QMiDt/nrVLBuhc66UGq+9mUDpkTVsUMHyukk'
                'z2rrGL1Pw9mq64RRCsyCCjUUHjdhvbqArl1nBbZChtKtETaYqQvMegokazq7LWgaeDWYApWSLTNkJF237RT4Fa6pL9QMYLK68Ck4'
                'ainQcVOGxXRhQQ1aXiBeuggFZD+A422Dqg0tgJwQHN7iKmImvogsAzdEqwIaNEeELxtG1eIkKAyjYDDYGhC/Y3DkscDIIfnMvPWb'
                'yvyqw8y/eXBjBdMts3CxtyuGH+KCajyXCccC3W/AMTYuD+OYtAIYxrt4AJL7UMXOjq+g7CmA4Rzsh+wqDviVPdPUCtuRKoAf44Kq'
                'DUwHZwcSsFe8j200lb0Dd9y2ll1awhxB98F7cq1ZO9my8toublvOvFpIqO9V+yNAu8bfRP1/PFZAjk9HgAEMNADoMlgKeA8rzNPB'
                'tvbabaf8y+AXUQEk09Fd19S39gK4DanE92fe5r4FkITK6uXEQnPyZO8EOGKIjMPah0Vn7nUFxoBD2Yj1C2Azno4+W8+n+sg8yKcf'
                'VrzOLdar1suTK/KPTwzG4u/arNpx1z33+vO7x9+2o7Wj6eKJSl29cFia9qThxwVUA9J57D1wPxYz51BL4YF5Ofght/ZgVMEGlEpJ'
                'b0s3OxUsxuCQjXjt7BthEtabj89ZvukmKQbvQQfo2MyJkTc0/IS2d0g59b4vHlF94Wvn84l/0yH5u44/qmX3uMoud1Z8ZRhO76Th'
                'HedHh0h/4amNyDCZElorG+GNc3jDqVeUTGi1pAig5HlVQchWo58PfZInr1V+7RQ+d3pEoKyzbPkjzF7IwH++8FqI6suax1RVu9/U'
                '+0lCJv5aUpE0H42xHrli1tUjWcUfNPZ9YBFObpJQVXgfUFU8MQIUFfMRWEUbLSrY4sOjeS6c5//YvAiSqnEK7TacE+bee1BWQxkY'
                'h2QvfoJtsrjXKN77OGs8du8i0gKf/VZYfmEKt+cCV4lPdInyeYEHwTS7RUhA14uQ6E7n+9U6vIvXoTtpD4W1lRu3Bo3G0bLGAHtS'
                'ZVsxNV97Hy4rWBN5O7crrGOvQ48r2aZJMA6lntP5Qa2QnhlgWkR5oE+4Io0D0yp4nJA9gvDMNq2gsnCP8OFyTB9Rp+0TWMK6DqY3'
                'YQoOntMxvWZw9zQwPcoENG/oerbJu8hORUSfw2VFm6NSTWSh5mJyW6+/jl8A23AdowlwZGhdv2oDNxkUAj2cVYRFOnjDleLy5M8i'
                'FVWrW6ikBTU5NTwNLgM8QDSHd9JFOhLSH0XJ+hHsV/hVyHHrDHY1A3fD19TSFRQ5CTRTV3I3E4j06AdOFBHjoMRbqg7q6jaSbohH'
                'Hu9bOnzBeS8A5hgkCBL/I2N5tuCGjTqmUyUm+TLyI6Oq32Wt0QOjArWo+JYEdiNq2qGemif7nYHfBH2EJyROAEswozGh9LcvqJFx'
                'UzZkG0UBndJBHU6Bo6UAyGQ5sNcSkBRUyQpkoR6U4CGAGQIEd0mGrHBVdcGqKKMde2IH2U5g3Hqw9zZq+xFyfBXojbpPAbQpRimA'
                'OnmIAgkAzTnwa4ajeNB4HzhfXYDy1O9eFDRC4FuJ2ebUn1+l3zX+lrhxFYoxE2QOq+7TYGrpKuJ1AW5yQr32ePIMwCA1KXZAkSKM'
                'ST7sUOUauoPWFBRRTZcUvHnvKzV0iw+Zge1Eo1YKPXXz2qB2vS9BOpdUNZFWiCuHmy9Fese8X7KKmldZxvvgN3j3cK4l7ZfRlakH'
                '5iy8/NUAdxFN4EdSI456uYfGzi6BohiOmDFbSG0Dicjb1LNWqAa1jBXCET6soQOQr6HtYNfQZiRNf+/aAbSr9TqPuLT36e/0Bft5'
                'lPfTrVLsLPUO4v0ai7d1Fl1Zw999mrGq9t9RrmSIiX+pLI8hd5TvV/33asuulwM1TR99JzAMiPsB5NHrLnB/2/l7APMl/3rFVPzb'
                'hqepCHZf7JSjz4hH2PxoYHD8aucQxpZ/yB94shdl5VIUw0iJccOtxRgmtDXQZ4ZdwWh88DDQNrAKFhQPT7zmbiB8ThiIYxGNYF69'
                'RCjW3jEQRlYuuBloAOUWFcIQKCS08A/veo4hr5Xi9RyzuM+2Cv3o3z5tqC1bfCLvzwXquAv8u3pggPFGB8L1srAkojSr4r++/Afv'
                '0kmLbetldrz2Hyq/zuNgklWIMJaM1WtCK+5IJMMpkuBY2yXcqx5O3XFUbwvp60UqDd14Ic+Wt3+0tz59WxbD6RAFG+fBb+Hqar1M'
                'uFZd3VwzFTKiiYRVL0NWDJEw9BwUNJVx9F6Bx6DkERVWH7QPQPpiCClf86YBwXIWKhoq6OhXuxSOe0j4LnvtiapmdPoPgaWpAUkD'
                'M5z2MiClRqdp0PM02Fpo79vcBhe8tdefDRioNKDPJbDHGZDoI/V/BqhjvAtAu2Yr56+QsZ6LyBwiph1FaZytOmLJougjBw10RsP2'
                'ZIrG77NXoetqMEevwKsYvy4P5CjMehDt5c2EI7LLWfMD6CvR8zD+aomvREEVuehlSUS+peEehfpBgZeBJJ/2pyBKF/LowlK4GS9N'
                'PQkqQg2Qw30bDubCZQO0S6MungDxk5gLI0CE1VZNAbKR8ngSdIB0DwUwq6aHAcbALgNUKnPUUQAV7xwDtILsFQogZZhjgKGUopPA'
                'v1AD6G0yjjxq0ZXygqOvc7O4bRGfGUeo3xyWBxndAiImO9BDo/ywg4Uo54GzKSUUOH9Y3YmLqT7Q1CI+kr9SM2CAZEhL6VxqK2M2'
                'EDZRuGGMpoyeLkLwbE0+6HrN9TnXOo32LsFJ6vvt5ZkmtC/YP8dDnM924rlKAaR386/6np2zuB1EtsMxTszX+uxaRdGxMZ7K7DPf'
                '2jnEU7cBT4YL4zC03S9ISypL0eMoUiDKbET28GUFHkPb455XPI7h+2q1/aS1c6aqAJbMH4Z5uVqkfya4HxNg9p8xAR5wea6qXqfF'
                'TZ8ASAekGRPgY30CQCt9AjBJ115MgNNhYgJcR8osJ8wYjbYmOKqxY+3L4JwRCiUdf42V9qclc9dLXoZxyiqtyiGyLSGxmIm1X0HG'
                'b1EDVcE+LHytYAvGsSjYw/XqRjZOHPo3Qw3/md7u5df0bpTN9Caq3aqjTDw9SVYlvG5V815I9dYghmpGaRDdx3RvDT5FiWMDoo2f'
                '5q3B/pxXbp5wtbwkactw6upPcohuJbMg6r5OVf1bzDcl02+2k5vk1ReTelq4mDyix1hqAk/9kcEQx4cq6NGMhrEvLn+ef6way1gy'
                'YMWnfGH7d5n+k5mS9/Lu0L/qwRP3M1RuGKGUbAMsgxtkqzAcI/IwXgnmZZ3Dfeq8nArOx4j61BbMZqw3euuFXFvRqQX1WdBGPyrd'
                'iY1U0jtTS/9/4nog015PwrH/PHhAA0ejNXAwXKWZnIEf3Cwy/ScNQ/NH4BSzWpvTRYNO5XctfCv1vwm5GKaZKZzkPEa6t1mbbjWd'
                'm43m+wOcdhQx1hMoLg8bM30qspW2IJlbhMIL46vdpVec5Ua8SmSO0W2WGPAtXJTkV1/+SCT3aq00UBTp5HkvO4SgPsUiUZ4lwhKf'
                'AelcV/Fci1gANO2nwjWxQHKoQXdQRmeRdf2WBFjVwnwGCty7gclHZmDYoPVCjbNPhAnnaLqvSik664QaCjah6k6bFBgYmSV4v4Va'
                'ZhosPqplVvo4YcxqUGnAdP50maStW0z1qdufJw+KUL3F4yGWnrIGqFU2BSN0/k7oRDUUTRRMoN3NwCh6sLMUtlDpjMmEP6Mf8Tis'
                'KEGz6DIVal/gME+AoT9hTnQ5VUZjUc98Cw1nQK8qzBnrBldIeoFbV5jdEvPGaafMkZi7Ferc25t1FWOJw6jUuVQ0DtZy7fgD7cxy'
                '2MnpkO/BasfAzXBMCB4k9N4ZzpbwaCQSJZTWdisSaZ7tBV39I9ympy/BKjJlqpXQl6icgwYjO9ZAcXWetvIXYZKMEvL8Cop799Nw'
                'mAvfRlZKhYwES2OVEFwSWTkP+WaZCZcKK5dAso8a6J7gdDjbaZ8P9dwyDbphEHCThkeCwy7DvrSjRbBkKVxWWSqbITu0arEibzHA'
                '/gJ1dct4DCYwjelQnxvCTfkYrI14UAC6UUfWzlJO2YzDnBOP05AqBH5LJw7wWwA9jWh7Rd12BknskQTXfTCiVVxFBbR60axWliKB'
                'oZ7b3KKYDjbm8E4FGxsg/3Q6zCSiFJlTSSHH0xT+vFBR8SEkThvYjFyCFg7ovw3OGZRWAlrnyjemAfhiULEO8QVUbO0uHuPfjPdq'
                'GuwTF/SxTqk7jMjiYP1SWA5cM3IJ14BTpWyRziBGmo12CqSqsCd+Y7pKxdHaAV8aiTLnICNYTz4zNg8gJWDE2d0OQGYlPZ1CzQJS'
                'vYiZsiqDI9uw/Dx0fZ3s6YKi2amTcYpjrvB/+KR1aQJNvLxnPqdLpqdrDqhLdiiJsupRQz2j1DXX1CUL1TU/1SVz1TWn1SXb1TUP'
                'FhWrFr50yZ11yap1ybd1zcR1ydGl2bvvMhbsGP/LfN1/6987Wifu2wGMSP486mgKshrpEHh1F9zm7xxrRnHsl8jt1qjbTC8Gn4KN'
                'bsTvlAhwhl/C0PBGWCs+XFSqs6+rqQkb7sTRTJmja2MtZ9JzOJz14Z+f6VuPPc7OxP3RuUcyLHnHpoTqhFE2OlIdD45vVcmjcver'
                'cMNT/+wag19CYwEB437JYvtaMGIek6YlYZ6CkvExtMEcGNtYLkZvG4ztKu1iTPId+6iQij4nEHhnwY1uwQGdjpnKsYKnbTzHrF8W'
                'tctab8m13trQEg2EsQtA2xNzP4DX5MvmrI1NGTixm7fagwKHc0o1346XqVZFHc32HdQ1Y5RkgRSWm+ESgpvSzHX6LJALCNOtIhcg'
                'RytBhHabw1tVsAmNOVl1dAV+edro+xE+HS5BUSSC4z9wv6Mb66j31KuWrPVCaVeefDjPkvwu1aldCgSdUI08Yoa0IdW8a48vnkCO'
                'w03OHcc810RlZDGtpyjlqVBB7lUeYeyMoZbbK+rCCbjF46V1nqVtpb8U6VVrbAGaVl0KeR/O0cth7x8tsF6epLnQUbrE+BfAM4lF'
                'pQe7RwkFzI4ZFOCCWlffu9lPDgqS4RBdKL4Y9o9vKAPObyJ4RqYs4LyLHyXMK1IXwUgJ0FaP7y8JeHpbjEw/pxUg85BIbSgfWjXu'
                'doOv63k33ePQuzOdd3RgYonpUA/R65BJxwvNN5Zw8yZWJDKW0JlftxAyBoX6xO2HvEiaGGNi/fPLwFkW7pTRs3eRb0RuoI2ylvzQ'
                'RLTb7Q4ncziqj9AXfjSm5ftploYTdLvtezjko4n4IjgzINIzosUr26hJFZepcsRZCuib+zHT7vSy3kJNV1mSbhMprH5J7LZpPGXa'
                '8YxU5Cu0nS67BJvKbYoEaebIY5pe1u/5Lyn3TywpOdSTf8CFvJvvUYBW6PeNfR7caaPgPJz05GkEEF9PSvs3EPST8Zw4fXLV5dMu'
                'WJ9pXCW24RW8KCOU8bgXgoU7WNW00R1NvBtuL2Xd+ZjHpl8FoDbYgEOlxfs71VY0Gp+3EZq+p2z1zunxkV51ZjhgBPNIxBYIOpfr'
                'TD6SZc3a0Zt9nrOaRfqvlfsmFpUd+QsrT+WJRk9TP8P8VtXgHlnYpblq+sADc8EZKtzhLnP51jCCtlj/uXzvF82LHKjqv4/lO6XM'
                '75X/5rGfvWH8XeW/s/77XdaM9mt6WTjJpnue73WMFBthRhobYn73+ft1fgNyCd87TNk6/2ctMONr1vyNSnh2Zq+sTlwyWe8XqH0V'
                'jlcWICYd9gWJK82yYbuvuC22ANZ7iWc6lsKX7qKCLRVQEiprA2c5cxgZsL80AIRhzrjIZWBpqRr1T4JrwaoHzSpgg9Gd0UCXquzo'
                'VqhopkDlDEgO5JuzuRmhl7nM+a8qx2rlZor8RwXjQCrGyMtPf0w6zC3LuSrjzvTOYlpOgBlzCvLnuQ9JqdhfFx1qpkW/on8OIip+'
                'JBwn+pJQ3PcVkUCpiGfYttMb8HgCTSVrC04Pmtc3KIGSHK2YpbMXhiZQEfQwm3e7YYQLGvlnoP9FcrHpyhRz8an3md56yc7lxw00'
                'TlrY4FwHv/BRZZQG/Qbywvm2f+iDe/B4zp77LViNGZb9ZK7v2Xi1teELyGirfIglkNFIu+0cVsCZQPdMDA5/K6pGw64/aWWHs+19'
                'w0aWwXlcfcNFd9IZDfbQ6lRL6ZlplWhs9ZD3lKvm2183YCHYI3t4tmJHChyOSZG+na4h70T34rPkUSRs3kHgrCZ2gR1GkCqDZaUI'
                'TsjUVfBZCscV8FW3TcXty1oFx1TVMVbknGij70X4PH6Fvgl2h28bMD/FOuo787ola10j1lEtf/mfATTAuTO//PRQYqL05Wt8cD6k'
                'AKmywy196iwDJ4JvICuY22UwHMd6nvipABj+IGeSMVyCIF59HysMb6sD9OL6qNu8zCJbjO3o2AaZQXwMEMQ54GAL7+hlTtoopeNY'
                'ljzrG3nih4KKM8N4R+XxT4KRUESiP79ecW1VXSy24tsbN4yE0ospz0f4PvjKHLoTLkKpsVcMjVZNFS2Gniu6f0VcPMuvVZQmbXwa'
                'J2tvm1C+zxGvXDjzRKhfTN+tA2jkr7XmYCmOzCsT0l5rKDb/dKKCr/TI+8wVCxuzjabf5srtidHvlWs7mUaDXdn1b4Lds0vi23E1'
                'vGuMNGFWbXep/1OiiUfb+Udv2QqPTAiS7u9J3Rf+m2Cg5mlEuYB/prZ/AMzVNpqiQ1Rs7HjE7T1La0nN4XZc6w4JmZ9ENUnUnyEj'
                'ZdkNy7NFTAZ3Jw+cSH+YhHdrIJr3zcUm1IGVLXC+jV+tRflUvvIfbrH2omW31y+ac7+PpXUuhKviPdAfaN1cJqdg5hfGTi+KuIxH'
                'NrUjJkCWB19/TtRzNZ2cbV+NypDQX7OgrpdvMZ/1w6DYl4ZpzUyXBFdQmbtFRlk2oqkSYpZ5Qz3AXGko5IvBxQk7bC/fnUDYLuOz'
                'dnhMU+pw3fgkl0GED9KNvRNU485bq3GvXhXQfaSMNlGiF/VbY5FVyFOQzhO3PBr+6sdSttfitm4MNcykZhO1bK9T1fQ2ZenTk5As'
                'qcK+cxwUuzeCd86cwt6n0EbKoMmb0HimM2IW/9WcX2D4j6k4oi/8zMNT02FtxefEPXdjCTTkmVJWGlhYY4UczkzboNyPTfUtkvSg'
                'BGeonQXRWpjFC3odh+NeuO7Nzfnv7OTXZntir+LK6up0shBe4CW06KrnyO0Djcvg1X1w0NPYHAo5NbTNq9qOy2ikdHbKPYA+GJ4s'
                'UVuJl0J25CCwPy6od+eTNLyQRYVaIxNTP/64w8WTBCTBIU/R6nzsV77Yao1bLJ+eAMWCoq9UAW9UtQi/k4yiOU/rJdN7gu6uby88'
                '1Macf0jisZcFfDWOgUychJ63OdNYqYx+uR5gChZcwFY6z5bJT22tGm6FVkTGWMe/Iekx+vtESWeN6EkABr7KQ4gx7fhn5Ec3TVhS'
                'wvqKxjGZjb0Bbg0SoViGAxg3qvivDVDxa181zoYEa6WXZTXfwBl/lUGTLdMQ+jkt0ud6uEzppappKnLqfQj2eChO5KqME42D4oYy'
                'FmJ3dBPF+oUiM5ko7c368Nqd/fEaezDHckkYTzy7gv5+FPzY0EtuGYlXP5ABtY1EwKh7FuXU62WswJlQxiadW+izpTx4SRNMypcH'
                'yGLZXzm35BY2rML4UamFYHJTO3dUZU8aTdy7D1onHwYlWfCFfojxJHe8JvEedzDXltwJsu7jfw87y25saktUIo1dyNsgZFRXGr86'
                'cNrQOylGUsPNexTfMoqvQyExBljulAopgEOthaZueUi9XPMDshiSD7+28ZWPNVGVlRpN3PrjPmid/Fx2PeDJfM7G8deM48WKlM3C'
                'MG+7uzh/bz/2DaNfHs/TGE72Dw8bkT839UingBrPnGT/lNV8Gp/VPfaWZC2lxlXHgxU5X2I4tSezya9Udk83DwmuvQbmNWBCzz31'
                '1INMJrndOOORXTYosNZKNPKf494EzpOeJ8x5qyLv2rr6P/AWpOM='
            ),
        },
        34: {
            "ascent": 32,
            "descent": 9,
            "glifos": {
                32: (20.469, 0, 0, 0, 0, 0),
                33: (20.469, 8, -25, 4, 25, 0),
                34: (20.469, 5, -25, 10, 9, 100),
                35: (20.469, 0, -25, 21, 25, 190),
                36: (20.469, 3, -26, 16, 31, 715),
                37: (20.469, 0, -25, 20, 25, 1211),
                38: (20.469, 0, -25, 21, 25, 1711),
                39: (20.469, 8, -25, 4, 9, 2236),
                40: (20.469, 7, -26, 8, 30, 2272),
                41: (20.469, 5, -26, 9, 30, 2512),
                42: (20.469, 2, -25, 16, 16, 2782),
                43: (20.469, 1, -19, 19, 17, 3038),
                44: (20.469, 6, -5, 7, 10, 3361),
                45: (20.469, 5, -11, 10, 3, 3431),
                46: (20.469, 8, -5, 5, 5, 3461),
                47: (20.469, 1, -25, 17, 28, 3486),
                48: (20.469, 2, -25, 17, 25, 3962),
                49: (20.469, 4, -25, 15, 25, 4387),
                50: (20.469, 2, -25, 16, 25, 4762),
                51: (20.469, 2, -25, 16, 25, 5162),
                52: (20.469, 1, -25, 18, 25, 5562),
                53: (20.469, 2, -25, 16, 25, 6012),
                54: (20.469, 2, -25, 17, 25, 6412),
                55: (20.469, 2, -25, 16, 25, 6837),
                56: (20.469, 2, -25, 17, 25, 7237),
                57: (20.469, 2, -25, 17, 25, 7662),
                58: (20.469, 8, -18, 5, 18, 8087),
                59: (20.469, 6, -18, 7, 23, 8177),
                60: (20.469, 1, -19, 19, 17, 8338),
                61: (20.469, 1, -16, 19, 10, 8661),
                62: (20.469, 1, -19, 19, 17, 8851),
                63: (20.469, 4, -25, 14, 25, 9174),
                64: (20.469, 0, -23, 20, 28, 9524),
                65: (20.469, 0, -25, 20, 25, 10084),
                66: (20.469, 2, -25, 17, 25, 10584),
                67: (20.469, 2, -25, 16, 25, 11009),
                68: (20.469, 2, -25, 17, 25, 11409),
                69: (20.469, 3, -25, 16, 25, 11834),
                70: (20.469, 3, -25, 16, 25, 12234),
                71: (20.469, 1, -25, 18, 25, 12634),
                72: (20.469, 2, -25, 17, 25, 13084),
                73: (20.469, 3, -25, 15, 25, 13509),
                74: (20.469, 1, -25, 15, 25, 13884),
                75: (20.469, 2, -25, 19, 25, 14259),
                76: (20.469, 3, -25, 16, 25, 14734),
                77: (20.469, 1, -25, 19, 25, 15134),
                78: (20.469, 2, -25, 17, 25, 15609),
                79: (20.469, 1, -25, 18, 25, 16034),
                80: (20.469, 3, -25, 16, 25, 16484),
                81: (20.469, 1, -25, 18, 29, 16884),
                82: (20.469, 2, -25, 19, 25, 17406),
                83: (20.469, 2, -25, 17, 25, 17881),
                84: (20.469, 0, -25, 20, 25, 18306),
                85: (20.469, 2, -25, 17, 25, 18806),
                86: (20.469, 0, -25, 20, 25, 19231),
                87: (20.469, 0, -25, 21, 25, 19731),
                88: (20.469, 0, -25, 21, 25, 20256),
                89: (20.469, 0, -25, 20, 25, 20781),
                90: (20.469, 2, -25, 18, 25, 21281),
                91: (20.469, 7, -26, 8, 30, 21731),
                92: (20.469, 1, -25, 17, 28, 21971),
                93: (20.469, 5, -26, 8, 30, 22447),
                94: (20.469, 1, -25, 19, 9, 22687),
                95: (20.469, 0, 5, 21, 3, 22858),
                96: (20.469, 4, -27, 9, 6, 22921),
                97: (20.469, 2, -19, 16, 19, 22975),
                98: (20.469, 3, -26, 16, 26, 23279),
                99: (20.469, 3, -19, 15, 19, 23695),
                100: (20.469, 2, -26, 16, 26, 23980),
                101: (20.469, 2, -19, 17, 19, 24396),
                102: (20.469, 3, -26, 15, 26, 24719),
                103: (20.469, 2, -19, 16, 26, 25109),
                104: (20.469, 3, -26, 15, 26, 25525),
                105: (20.469, 2, -26, 17, 26, 25915),
                106: (20.469, 3, -26, 11, 33, 26357),
                107: (20.469, 3, -26, 17, 26, 26720),
                108: (20.469, 2, -26, 16, 26, 27162),
                109: (20.469, 1, -19, 18, 19, 27578),
                110: (20.469, 3, -19, 15, 19, 27920),
                111: (20.469, 2, -19, 17, 19, 28205),
                112: (20.469, 3, -19, 16, 26, 28528),
                113: (20.469, 2, -19, 16, 26, 28944),
                114: (20.469, 6, -19, 14, 19, 29360),
                115: (20.469, 3, -19, 15, 19, 29626),
                116: (20.469, 2, -24, 16, 24, 29911),
                117: (20.469, 3, -19, 15, 19, 30295),
                118: (20.469, 1, -19, 18, 19, 30580),
                119: (20.469, 0, -19, 21, 19, 30922),
                120: (20.469, 1, -19, 19, 19, 31321),
                121: (20.469, 1, -19, 19, 26, 31682),
                122: (20.469, 3, -19, 15, 19, 32176),
                123: (20.469, 3, -26, 14, 31, 32461),
                124: (20.469, 8, -26, 4, 34, 32895),
                125: (20.469, 3, -26, 14, 31, 33031),
                126: (20.469, 1, -13, 19, 5, 33465),
                176: (20.469, 4, -25, 12, 11, 33560),
                183: (20.469, 8, -14, 5, 5, 33692),
            },
            "dados": (
                'eNrtfQd8FNX2/2yymx4SkhCS0ANIMUCkC0iR8kRipQkIUqxIFSwgoiD4RKkKgjRRsQAiKCBFURQILRSpAYFQQkjvbTe7e/7ntpl7'
                'Z32I76c+3v85nw/snu9mZu69c++5p884gPxxN/nvGYD0AQBn7wU42B7gu9sB1lcH+EAzHebzHgd4TdP8AM7/0d/EHUcBtMePjVBk'
                'NZqxDkp9NM2SA9uktmXATvy/GcAkA2sM8Ap+jAG40wBHAnTEjy+h2GaAa6DMFy+ZBTukS16HH/D/OICXKRkKHsfTvwOkx35Iwf/D'
                'XLDYuA1SS/CjH8CDBojUQ/ixHCoqGeAKqAjBjyvwk9TKq7Ab/28kWqmVe9z7td8DkuMYnCHtcsO7xm1CWSsfAuhjgPcBDMCPBQCR'
                'BjgbIBo/foZTUisPwTl2yfcMLNgJS9kl+xlgT4BB+DEfIEqdfHGigzo9xUS/YqJfNYhW7x4rhopLuxb1J00L+szocrqmee0kX9w6'
                'PRA/PolvDq/WaDdi9WEyVWC1fL+jAF1l+iCdUQa9BGCVTDdzAWzs1NJo72hyLxfsG9mIA92O8dYceUA0+NXvGLLUS+/PvAc+wxNf'
                'l/s/FKA8Uh6Pn9nw6fTnAC/J9G6AUZ8lWATdAS/YJhnOv3ZXUBxMazylGDmAJZneuIzdP6exFvepXR+uo7TJYY9/croESk99/KCX'
                'PsTx8njTpThVoZuank8Tj+dn0LaxR0tzv+og/+z/Pb2/e6KEvQ8lwwJjFoK7uw5Vc8IT5PMruirYMRCKaTM7gytYYGPgNP2sBVBH'
                'YIOgyML+zh0isOouGMaud9C473IoeTI8eiFAL0pGPL/XpgX8yAaIsp87PyqHstaa5jP+WFn+NpwsQU/iEz47Icy4xu0LC8CxrqsB'
                '2B7BK6RMrmogNWemg/Pre40htvT82gXXptfQtPDZF+ypS2pQdube8TBhjnUv0fvnIqurOqsu/Xvvn+FsR9+meyDDuHFvqCCPMCRD'
                'LHY83oPt9PNNSNKxtfA+/XwSrunYYs5x/wk/61h/cDTAj0rXYY6OWZPhYvfAuB+hoLrEjNNo+4r/IT/VqgsuOdI/uk1fpivPldhT'
                'Pu0TKP3JNL4wYYaBDdLnowTisrzQP9qvbo8FzxuD6gZ3XfM2FgRwRfM4ssAe5AGuAhjnATZxQmGsB7oW4FiACZtJmviJir0HsOmq'
                '6bK4Q33g1cYOFZ0ouQcyNS2mFI740u0qgzxnbSdc0LQ3ACiH+BDXKf6oJZIndhKcdCvzxzm2Aj/Pw2eaxQnX2bVj8+iW5Iaxmg+u'
                'am+G9nKD/c5R4MJ+5AN05u14HSAtFzbgt+0AP/E/9dqGncivjd8G45dVPgy9B7iA4HUIv50aUcunaq81yOjAQTlEtcsGiy3FC/xA'
                'T4rcKrCf76hcADCQXeuupWcKyy+v7YczfQbA9UodAD7/rX/kvO5sX/U9B2fICniOXTA4Cy6Qpk8EIMzCegUcEfiZAPAN2+rhcTIz'
                'CtjKvwvYBJ/If/4Y2ETeCzBeo4MJg5kwAL35Zx8Z3wPwHPn8CGAu+ZwAsJV8YhvT6FrA4aUz8FOAp/gGR1eb9yWoqEK+jAd4kXwG'
                'ZkAKlXLGAjxKPn3OQrKV9/OZwDT4jo3WEwD92TK7BJd8hZg0lm2pRZDKxJplYiPoJgbfmgvumvTbBoBnNX7rr+mXLjjL2ILEZxND'
                'eY2diV6alsZ7Tro8hH65IL6InywOgHbkSxSwzV/rKi44Qdzia35TWz5vxj8AdtFfVvL+VirhjR/Lu2O7ApdpB58CeIQO0XUq5enH'
                'NojXbo6e85qvTrfdExVWDGe7Mjr0PRfuXLG4fD+ugvQj1+HKELINtN0LualwAgpf9ufX6IsD4FxiSDq9ka54rwqnWu9hf1/wkh/Z'
                'Vz51w+pIvN6AdLg0wBJWBOfE/Ra7cSecO01qz97o390fsWcSSeM/Bb3pIT9abw66JVqvaV+w/UP92ASEbVgyAQrDUEah8tZogILK'
                'VA6cRvWO/FAi7tANNEp0av6vfSNbcsKv/ae06iWAdTLtizympQzg9FemvdcvAD1kALWFI8olDwsewY8eqFN5y8BOXSVhR0tcr34y'
                'gMMxWaZvc0FhqAwgg3lbpqPLwV5NBt5mu5F+hBSCu4EMTAb4Uqb90lEYlYFnBIfghzcuuHtk4BGQJBFyHNH3FHYgj0lR+v2DYH1i'
                '1QJk+svAl6DKqQ1cUBQmAys4oxdHjB0cNczCQNSUpOzS85/ocun9OXxKrGYiQieHvhq+IMzGHzlp+YTowE77gG1P48Us8cdHeclG'
                'NnnOR7V2+FNPIrjC/fzqZwAWEZnIJXTFRWRcpqPEKe4/HHdhyycA3woAtxSo/g1VbO5Kzp9noVMdJTZYTtk7svX6+H/bA0AUNjJl'
                '+2o18f8u7C+6nS9Y5MX+gl1DiPQATT413aWGRztIS4UgvpC0tLa0JE7TO55CjYnRd+Jv99JthHzgJEFx4zLKIAE4WcrGRwV0TMRf'
                'niS/3F2hj+kGKsdrD+Zy+lMhUEZPPZxTdvEztnjCu4xdfrBEZ0jZKn8ykWd3vfNEm/4S92Iixd8kOWYo/L3hjUmvuCdW7v8lz5G1'
                'b9ZtQpLkh3uhv0KjLcpX6376g6fbNwi3VRt2CQz1lypeOFOL5dVLNPfusnqB9HBV8meChDRh5R11qjRVyQTBOTBUotcD7LUY5PPI'
                'O6SV39cF9s4G2d0OLokHty9ROG6LfMVSFYd3ekNiOji5Fxhk3VS0Axg3roWy9YcGWf0iwBpvZTuRj4W/RWvV+72940JJRc7hd1vR'
                'CziNH9dHqDScwH0wZe24jg3CrFV6ERPFUml8LLj2y4MlgHCIu2QGLjEt8Xtz6ef1Eru2Vu+3H+Wre4TlkR4Xu2syvdRfU2i41Eu/'
                'mE/twcg63YPl278PUFJLAmxnAd6U+TbqV/tMitllmUZh5oxEWvH8LdK+/A42YeTn21/t2TTG1y92CBqG4LL/Nnm0C1trMp0Uh2Jv'
                '18kbj1wqqsg5+n43i7KLoKoCs2XgXjAhgZfMyBy4fFpB7nDCQ0ky4p2EGoqCjIfyegpSsximawqyGVL8FaQve5IGEpIGmzUFWQJl'
                'sQrS3s1tRAKxnYILfgoyRRhVBBJbBl9pCvKgWZ5MvhlEGqIk06j+8ch86c7Om6MVY9ifQP+4M8ORuZ9xXOn+rvd8Te35HoWN178Y'
                'cke0rXKHeaUIvCVdqOE1XOHREtBJ7L6aIYuslOl1ygqh9GaZPqFKia3weiMMsvo5XLGR726ffHfjSGtwy2m51Ei9Sn6yX3rJdPlU'
                '5B+hAxfvuVLsLE3d9qKhrdV/JTHVXnRiaS+mMvu+qYtg1KRo+9q4CAXmkcU7pp5fQP1HNxKRMQ7Fi+9DVNvQVVki9iswDQXqwGWy'
                'JYsYKLZrJllythY+/URJ/qn3mjEzIzwdl8Y3wwXeVF4dma43DE1yKJGdh6sjYmwxw9CKhIbon/D/VPZIqmWSwSU2FsH1XsThs66R'
                '5K14sgO/Sc3cfA9FoP0IE9CumXTKHQg00K5xJZ1dFN0xc7D7xm3RZlQVd7irw6Os0UOvALMdDJYeE9MVhhWKWT+ds7pqL+9Ld+Qe'
                'mVNfo34e5Ug30ckmepqsXZSCWzbKPYtT3qQZDFX1nWLZ3LdEVRYDCgyjGG03bj0yb0brkGztRu+Lu7ZEzxU2F74VZQmDibCZQpE8'
                'Mb5V10xtN3NRiQPlp/PSzb1TVRUFxTC3vKl9pWqLURXGkyPHJNyEJDul5TyV6PXjbhxX2fBu67f2fJEj86fp/BZxJ8To26n8UifL'
                '9EBQgYKd3aICG7+MY+hsqFXCdbaeK1susnqbg7AsUXfEGq0N0RI48AnRCSvj37XlwC4qGKHF6jNGN3eCsxETerZ2qRrQcFIeX6/h'
                'G128FancneT3PPNh7G7M7TXXdTnzY7KQh+I4r+kQ7BM7DqWvg35adLE+peohMp1M9FSbIexle6Fx4GNZdrwdGf58XQFGoNt+kzrU'
                'EfnddW4ypUpMnadBlzlq4cK5oAVnEEGrY7Ct9ijy7Rk0EVZIY7qJCETdrulNX8Q2TL9h61OKHVmJs4RKHTBq67XyvNOLxcProPd2'
                'FZWSWtsVnql5I2t1zY7zC+68jUnJD+vCsmUVlcOWorhn6O4oyB2QNrwNpBe/CLsjFTzQQCkDc4nsZDrFbVtqqOyVCDOo3Af/e0y/'
                'LWql1hScN7Ma+wZ12gqp6KOsp91ljEd/F7VP/kNodhOC8T+ykENe/DHTfnldGzK9yhQxaghIbg2N+cQUw0SVYsWpSU30BbIxZDSf'
                '2uGHX2xdHe3cm5G+4M95peBVDTQF2FWfu8Gm7b5Unnt6Obdb3JxF6AbHDS5wEx//7vFHmMpMR8Dwg96qce7dfEW99Bu8RzEXag3m'
                'UiuKYz2XEH36/8B0kue4Dbbum5mEzn+/NRfPH95OnEfuHwb7Kx6ZqzNiVZne/aa3p9/mwis1ZVG/9w7qtd0xQJ4ZdWfRO+a910pm'
                '94/sUtvFWj+PtX7DfbLMMGSv2kfGOBbmmyEU9Ucc8v6/Wlz/kOPfbsSkRU1+5VqJQ/w8L587r6FsYpt6ka2pAT7SxtX1E8reM9+S'
                'HXyhI5Mol/y2t9znpguoNef6DHmf9Om3jewYLvXRt0xRx8v6wFcVyl/dPjuDXmsm3/BDnjpA7/hdHxtv12oiNUPW2/W4DPsa88z+'
                'ONBH7eP8Rmq39z2mWCK1Se819Rz9dguSsity904hinmXw2Jsc3pqWrEkBbdGas/TjQIiunxLNkBts5ifGPngNlzMLcDYaFHVQqqF'
                'TqGbqUSXkGplAfcHE5ENRYaLQvKNwW0kU+xBlY5jv5tIptS8ZoLojGNoCDULpY1U03YoppGDirySdAPqRkc2Fwt+L0UW9fPfny8p'
                'Ore8vWFoWi6c0LCaP6P4THB/1b+ef0hXFEq/pbPjjlxI6WxIWeSiAefhimEi2gQZviRapqKZZBcC6KRF2hWbsncJ+hQng5M+KJ9x'
                'BwuLD7/gfx7loBNMl4o8wtpy7BLMr+SC0WSaJkLF1Oq+LchePr8bE7Ae5/qIFUMn5iOBfBn342Rd0Zr/PLhREPBz6jfPhPkzoZAY'
                'AIx9/BDMnw4lLFRirP4Y5qPFxUbPnaf7z+cPZr5D5R6t2b6jtMVaTP32pM2vVPNpThSW+TgJzpJtuyrv24nLiPXl5jyf8YeKS46/'
                'GnQSMe+LcMSDn/Um4pr5QGvPBDPmh2reB1VMoDfay/OX9YoNCGs13fDEdEjUleQY42/jJ+88m+tIS5xlbA5WIoyMVC/ZhZy3TcXm'
                'Uak5WMFwKe00SR8YtXYSR/JDk4toLrqVsmVelUicIccVA1ukC8r9SQDW24rq8h11AEkmEJTEXkDXAvJPPfTCr5iZQr+VVkMvdAqR'
                'Z/ICGBFnS7iAi5u6k/tFLKlcvbFk6JpnS+EIJhI9H1N0BBxn3x5DkcFHBG1IB7XL1zDbJ5k2Jx/UJrdd0qbvZYbcYJRxR+lutCKq'
                'JxH5srbs3jlEnfUnjNHAICp3jLdqgY3AreGpu4C7tQ1tZUtnof1kJs6J54zNOFYHmQASRdGZt8AW80AiFfA7G03ywYCtRBkgj7pQ'
                'AZARuxTgDRKyIAGhOP4fGXepMRANgCUN1HYk36k0rPz9EHPT8x/TpJbeR4S7J5TbonG8JEYGvHGrfFkGMDAKdigAClKnFQBDBU8p'
                'AHL7b2WAPC79otaIzotx9y2upo6pe7ja9Ou9jb44co5/PFDfR716Lj2RZb+2YQBbOC0OilPOkG2vR5lxjWPIv5F0f9C5ik/1vutc'
                'x4idFMqFm7XRYupceFx1oZ72kmaMW/WY3qPspnRHcMvxQe9INhce0vOLSeQ+fqPfzee/bLr+vab7R4LicaCz+aTUfrIMFGeJDTX9'
                'MhGg1hCdcm1Rk3et6BTuU633GieOl/aAXRk/dNYdlecbmSL3rTiV47i2Ecefmr0rMs58MaqmCGYQh2NZVRVAQ35jBqzWbFVajjtF'
                'HnIYByinmcQCq7YZ6jYqbe46MhBRQTQSCdC+I4tfBpAjlVtl4FGi1MsAMYd0lAFirLhPBpoRn9IN/4Jco5MMkJkUZ2qH3SYDyIUP'
                'm/vyhgwsBhLYZowHceqs4eNhjWgxFt3FkBGhjumVOGWQK1ZG6aNekZX85Zha+igp5umboJU4i7+Alo4pN0P/1e37He2HhN+ia6v0'
                'SzdDyxa8v4I2jlE3Rf/V7fsjae5OeHn3lfK8I7OFDhc836kbF8PprnxAmYW4FxFL/fERtX1Dm409QRH0LsJKYWAchCqQPxoz9yr6'
                '6KMeN0fz7kW1KegvWKwAxBI5WkGae5h/iIDaSUGIO58ZTqawRvchf9NRQZqLMAwdiWEmS8M61QdTMSTnNUW24FajIiiVQlMFCSyU'
                'PEMUIfZXmOUlI1YSbJo4oJotuN1yF5ObqxyXxvks3VsqLxPqmnt1ZaG2T99/zZ59ZFZTTdk1SEgYtLyVAeW4OeC/p3O/AXyudC3q'
                'xqSQntNVvelvktu8f+dIHtNFsZsgNcET/tvJ14AmKmlGLtNhNSBje5zB7TAOZ148rAhnFIk56Itqce7c9lVstcej9lngH69ufV5D'
                'Luo2helMP1l+ssCRdWhuQxNb0ga5SCCcDN2PMuDHFhm6G70jG6zyiW3xrjt85Ws1RePEngBNguqjP/lIiCZBNdFhezpCk6CqaNW7'
                'KKI5KVQZFdVrutmcQEEYq5jVWJOgdSSR6iNNhhgj7iZDqM8hy75cSYbs3RqVS35IhJwPsz3mHgNaQ5QSPDU1VG4qmpmcurVE7/Zs'
                'IoSrUABGi6WFKRAVzT9RIaLE0tw7CQpN06Vp/XE8JEncspukrwpF4fhnRZJsSc2USfk3/YfSSuDAb9ELieYSqUm80UogIckEFBvQ'
                'Lt1nz6FD4IrmVrRDHHozm8lblcpgIodmLGUZaEOg/DYBdQU3SYjaAhujBOSdQdJMwhwwQIdQk91HDKalQQaEYTa1UHFYrxmQVxpM'
                'rOrE1EkDQpvAoWehJECG0L78C6zVZMhylQb4yhBx1hb5q1Ab5nOXITGnb2VoI3V4GLEsDWnQyO1m4F0zkB+gALkiDkkAy4qJ5VAC'
                'Zi/nBhYdQKPnMgVAQ3lxJQV4nMWfG0BgPjVFGgDxjbRXgDjqLJEATDoqD1eAR4mpWwZ8s+GcRQYIR+yqAPXdsE4BcII54hQAjXHz'
                'FMB6nQyMBPDQXwmo6TIB2mYzkEABZld76+ecspSNA3SlZ4oIy9rPN5tXjWV7gRru2+K3a4MjA1qgZZnMbOo/yqspAt/daJWtBroV'
                'OxCjUObRFAoQfq+VNMF8lZRmjmHpmMG8Tw86p3kBaFjPIoH1wuuFyDDNITkafBEZbwPZ7Ifb3RQSkWBkIOIJMz3/RqswX4e4oZR7'
                'DcdkcbU9HRUb4DDao2fAyL1eTqJJaJj+c5yN5bPwFPS55FQXRkN3c+Z1gtRBVfzvWE0yEAyfNztS2BUt00XcxaF6uvdzzonc8ktf'
                'D7JKlgx3/rk1Q/1Nlo30BJOlw/WwsIR4RfQigkJeZcMyYllCBk2ylATg0G+XLSeYn/WLTOOTzpTpdervgTnK+ZZl0vUtEQnEQZ8f'
                'prTP3U9pb+aDRv8Kzq8bEXBrWI5uSMsraqDnijpY12NFXYz0WFHrPVYUCdE2ragFHivqoueKivJYUR09VtTwP2hFTfVYUc973Osx'
                'jxXV1WNFRdJ+SSsKlYPq6op6h428saLgDp6Vo6+odcKqq3MuLl2/KlbUT9WkFZVHkCHKU/TChrmGq15KlFPcTymQFQPmj1dSINuX'
                'M3w0ERHrzDm+6kGrHq5qmEnaeUBQ1olDRODxjnpoN2EEfgZEFg6RlPookBbtZi46CdJSWGKXDF1gbEaCwpzM4SZB7/J0AA55hXUj'
                'wYRLzE11zfNWoeJpsR59zL5Hh8i1wrtjoE1FOxnCsUI2QDOHpUbULuN5ulK7cOu8bFOhqHKghQHkPuJsSfZSoUZuOmAyRIxhh00Q'
                'MbT9Q4VICt+PJmigiJxss+hYriPj5I6Zvag+E/GVlFFA6GRQATKMX/aMtIY16DBuwzZSi8HksEbn0V5lGn1gjm1fq2h2bOJnRsgA'
                'iR88IgfNWs9Qr8PKobra2EiEMZ6fxbGqK8SKqHibW0Kjxn5TxKAtunvK2vaFvUyFlo5OOaqyTkP91LIhEWqCCV4IH0gzGSA+Xjke'
                'IPxn4hsedGDO4Db1I6yBTSamUbffUEV/2OClAM7ZuOS8459ckXg2q6Lk6raXawquajo23iz2r/Scv7FbG5vPHaEaS04F6/8U4D3X'
                'BFhmqYCTmHR0TwAGueRhfRHD/vYsWc+YNeEMNbycW7WgYr4HYGBkMQ1cIfvEV51DfetOwO24BM1vlU5Li2cA5SvbBZnXV1jLPjhb'
                '5Ej/bgI1fVnSQCpYQp3jw0k6xjEDw4pY7mgSWeSuIlV+IbybhLQbJYtSWFLi91KEXCyPq5soSUQYxpHlxcJ79GCHNcJSlKJnvZBw'
                '2gFC8vpUdzHzWJteukEXc0n2sG8kjCdO7CxCKNrKg7WsRUaGI1aJ2MRLU6SKVtXBaBMrkwmX6T1KZgWzfpIrUs2lTqxAu1wlpStN'
                'c7gHRGUKGtBSSEKQ3ubVM4x4ox4k1EdO/8bxmBXuNsaHS2lJfZmEZRzHwLXWlPdNQmDcUKIGjnag0fKmyK4cyT2F3x9WfsVo9cf3'
                'm0qxWHA0O31kyvEmeaTRU4SmpOnRbYUk8/6gKRDtMImNUkIzxhNLSgCWovFVo8EwRDqVxLdrGhEaw5kBcRCdSncjcY4metMQmVY0'
                '8GqoRuq4sGhqNOKG0FkwlQZ3pZCqI75uWnQjgT7LVyD/FcjBVAZmDrmNRkttgm1dyB3vZiHwtgqSzpgOUwMr8L5Dea2oX6CYOD27'
                'oQjyDl6GDRrOrfB+4AzGff8Ayf2P4324YzYcJWvb7rMdXH48a/+B3UTyRk209Rm+unGqjCuhuflXYXQxL7OGkV472GJYA1t5pJdm'
                'KYEKVjplLOA6G8NG62chVZPAMjEZ1gGfZlaSxR1rxG63Eakjdm894KzMpkckabwkAjXzaqJQAM1nxJl2QTwlWzLXhmIKjdAZzAMp'
                'iBFPtYgZAqMK9UmGJZe4ToZzKFHkIbTDZ9+KfTriNCn7C//C67BiwyI5x4MIVzwnz240G6VWz2LTwpiqGE12zaNMXzPih84M94yF'
                'VJPTiJaE2asirUY/plGm2VnBGmCcDwYOn1LCLnF0N3kdUWNnSXp/bSLNFhkRkxHZrDTdRvleODhnSQBgfXzCXaQwmW5iaZxiT8vv'
                'HC/1g07dHHEvrFJUGGMk6NJ7NbJLHAfrT5F7WZCB/WyVi9XhvXAk3e1VHfqULbZcVjC1CKrh/hP3jjBZ3M2urAVflzhDrINJ0ag3'
                '2usYHP0EmXOWJL27rdy0XhzjUO6WYvA2GNbnH7hRrFwIyjVLqbveC6N4/ik/mVPeGqbqXTdCSAPQlPu4f6qa24b1FdJmkkJu8lzZ'
                'R5/rncpzbe32LE9FWFF5dRNmciv+f4EFmYXuoN9Gin0VS4vdVEzECxfkLiX3CCsZFSulwmoXm84hYazqOcPM5xAX0ihzOo56zkPm'
                'c4jHSj1npfmcbuZzAi6az5lvPqeNy3SOz0nzOdPM58Q5TOd4HzCHpzziUS7z6ZtAeJL3tl/5/I47ZP9bP3+1X9Ww0kx17Ua1aGi1'
                'msrajerZeFa88aiJQzbDi2pWzFFTXR3PyjveF8wymrl6j2d9H48KQJ41gjyqCNE6QzHajSoRedYq8qhmRIQ3td6RR0Ukz5pJHlWV'
                'POsueZsrM3nUbvKs7kS40hc8fHm/+ZMv1P/azxv1S6NF8YoUcwwzTl+RjTj93eBC/Wi/8bha4/b4VGSyJFBUv05NtNUu6HnZgUeB'
                'FSCtfRXc9Kl5bdRrGTTIoOU5tVmShbhJDlyvQWTgVQb3alUARwPhV46Xbh6MOAtuFnpXOw3ymAk+vgCOsTV4t12Y8LGbT4tNw04a'
                'Fzh03eXyggtfDKWbTtDUfN2Y3NHk8S5pT+j8xQ/V8PWr/ywOBWbSDJ8sgsFjS+QkL41mZIwycWwigNaatPVyEQ+cm6d5GfURqLd0'
                'mZqUQczdZ59tEuzFEgMWokq+39+I8V/4ndBiNZqosnCvoUuSGMKFa3S5LpoYKxcS2/v69pV9G0zIAJRpFvoYGv1ucn0tVtg0d0VM'
                'oapCwNjduY6r29ETRegkOchEo4lifz7dZVNa2cWVrQU9mZunX2f0HL0HkyjthI/u8IsYiLE29oaE5pnjNbOIuoZ0Ni8JgEaDAmuS'
                'URKAuB+aJEkGW7QQPJLEC4HyWKxnkiS+g6LeBNPvT5vO72e6fiPp/pilnuOVRCeBaN8i1v4P433DBmD7ebUYvX8TWP8ncWvoVDE+'
                'Xbekl6Ws0O2vlgeWn86xX/2M1fBpqRcS+B41wF6lxuRartUnpQNW3h1mq3rvx87lZA8rFWWdWrxUx6WID6gqZfnKtXmZT5gfXyvK'
                'FdnqXvrXv5rONV25jlvXRjVerKJUjPntL2i3FZI2dwmzRfZY7sBIpvvL5B4h0zqlpwRRZcHroZVn8hypa3upIuouU6Dun0T7jt6d'
                'VXJqWmVO1z3DmvZLLKUj9OqtB38iNMqOsKKZX5XH0nAWQEIM/jeL8RYSDZDwnCFSvEDotYYxiUyuhFNSiDByp4Q0aXLinpqQL01e'
                'dDslXDP9flw6H4OLEz41XX+0cX8SMpwQWaG2j9hOYEVT34ghrP1aZT0M7wDtnxbL2c0vdfTx2ZNdemZ6mD5+QaO+uVJWcPq9O/iN'
                '+6TrBRmsek1vfhCVqjPeKLFfjLVSe/TkofBkwTu8Y9FX2EmSn3NCiBdeGN0c+y61bRobY3+MLnI5nS6Xy82uPeqKaW95Mc+82VwR'
                'qqamZ2/CYAVYZKrPQ9TispqKFoNmgaNiA7YOwZHujisua2rzYFt0zznpVKgbJ/WWSXkPpup5JR+zaAHfoZ+fL7Bf2zJeKmndenUK'
                'WRY8PO5JXrGDkXXEhsNINDxduzdMXqqj1OTH7io75iaLPcqArL4xaTr3f4H0GbU3u/jUNDGxa/Do+eSalK6kew5/oDQpDLWudUDl'
                'fpcATSQJ4XZh5K5O6h4kYHHq3GDdxgkJnxgBCSQHgSzcZ6UsBWVhJ/36wn9Q/v24xOnT2cL/SHLoJ6DDID9E3zUhIcIhgkhrZNGF'
                'T7zzX7YJCOlzicQtJWgh53QXG+t/rZOMPB65ixlbfUYn5pacfCWExArIuZ9ot4R6mlK6LheX82dcsrKsY8v+Eux8tIYtrAfaNd2t'
                'ebkOflDZs6OQa5xvMGbg1Xt9miPn6NwGfPLKzPpPJqvNOlmc99NjFka25yVVMMQYyScKRLMfI2QaLG7iGzGikOQk7gFRXYx4fGvu'
                '0Wv2WfDx3bvH8KugyXjEHsM0hZW1x+0xJgC6tidKrbqFSP4VGbiqRP4bwO87dvEhD7154A9r6a0HmI1vtX8b4HYGo4LHb3690ZFg'
                'lE/59a+/+27/0a9c2AjBHVoTr+TgRdqpTZ058aKfqyAeMSHdXA8VX4s7UR4MjsvLYnlkRYQ51OIvBZ5FZ8rDEoC2Vvt90l+gVFrW'
                'UzoFRdPSbtI1UF0r7ixdFNXMwg7SXTB8K7+tdFviQvneIgH0GC8Dl1EnKm9mAOdrWTCT97S/DmC5hWq5wF+CIxrWT1RF1ZuOrDIr'
                'WgYq4T6ywyJ3v6OLWjyk8UBjhj1eBnyOknvLQ9gYha8lj0hKiWx8/Ve02F7/p+nRur1C97EkasrbbcAliwcWtFid6uCnKJPs4P4/'
                'ywqVxoqqO+kOHIfe44W1NhamvWXTWv5QnLE4mPiTP0yh9R9vo9vyFoIwadnJ6kdBE5Jp9EZYs/PEpVedCHPj4tmbLdAnVxFM45xW'
                'xLOSJG1Y2BROjG/iWR2eusxH7O2GA/Es2CKGVy+xw7F45pmtwtMzS+A0RyI4UgzJtz7yt8TzGxJP60Wn88pTt47kc9a2Ui+20lbE'
                'cOhusJY8WvbEg2F+TRYgJzqJ7lqiNgYJmzfml7SWij/TwNsxUqjPSOKJWyK9+IAUfg1fYyqnWG+z5AANITVe1pr/4n0pKoNeY4wa'
                'UJRubsdXNO5Damlf6l6H4w9U9r19PvbltE1jte2EdZUa+Hw+FHSqcB+3XXymwJ62Y7Q/j5lpq/XYml56fkkTQfMAYMdzjDYMZo9T'
                '2gnLiU0FLSIF0YTmtqj6+SSgCOlUHz0n8SKhRVhMQxKhnGxEDFvQp3h3sqT5IxPokyypL2hpe8z0e1/T+d1M14+W7v8qKbhjtK9e'
                'PnkotP3LmlCbChRVI/Q8vX9Psv6/zQ0CE8T43Lcjs+zCUn18ZAb6Z9PUZrM5rfzColpEq8WuBGxhzcttT2nLN3rqwkeEJgGeP3YK'
                'rPSPI8RmNINccBcNSggksSgzmhul47sR+lkjFtWCYtKMxdKGgbEtM9ZIrjpk/TM2S+WG0PIzY53p96Wm88eart/GuH9X+mjQ9bGL'
                'SnsBRyhNNpxdHQOCeyRhPA3pn57dcH0V7X/QdqX/RBDZcr384uI62nzVLPqX0E4ipYS9cCCzJPmLhy2Eaisqy8YhdaduHybUfrg6'
                'poF/aJOBmxqTaJc9IZL2UBAt6xLvKJpFgkLVV6hIhYr4z1Fkh158LL8ia9fz1JVr1V0vhaO9aCCe8S4FLRyf7cEHqlpD287MRhKN'
                'ede5GT9wQX0SDy3XIMPXcVyRKij6ow1nSxvD23UfeSFk9pY3BnFzYJMvWH0f93ZeJSy424TPiAqQZ7hove6/rAbdoSBkl3QrkolR'
                '+ZmplYwAoXKsVVO8sncNn/CWCxwkDEZ2mxVjveDXdEfXRbqCA4Z9edVRkrJhqJ/Ev5T3IP0f6JOqBlnvt+g/+v5/CH2OpaDI3nrF'
                'CrxFKW1GGXr5mGqGb7tehdo/baxbpbW2HyTTmPx6t6b8IpEYvjRxlyFzYdcnbjEkMpysE5frXIHw0InIWDOpxcGPhEhNJK+kONTR'
                'L6j7AUglktFmvQ4zFZSqcc/BrhAmN4W+mVyWtXeED20Gvje3OECu6PkRqc/XV5OSYHqSOmCywJJtJTG4pUFGqsli5sLj8RaWy6wG'
                'yxj5jThXyaKNckJ5iOCfIoGTF+K7Jmp/jeDl9zvq20coRpFUZiU4pxklZTDVyCtdJGVSHXA7jcg7qgcH4ftTI0gYoeKjeNKaJV4q'
                'x30JO3vogclUjMwF52Y1voSyM2ekqea4Whnfi2RdDNUNrzXN9ZsHfi6PKznwudQaY0paiSAaUAuQXgWq0RDqtRpWoCyxqi7wcTTu'
                'Np5FyIiaAK1ogutTUuhYDpTa6Ev8VrIyXdCE2oKJDwRjczG23bcUDhOrwCC+6E6SSvqd4cKT5EG8w19vsZSEcr4Oi2tBkQ2FUncY'
                'D1J9CSvLP4TruYNPOQ9TxWtvCKpwhuDzeq2VrpRmQFovkrFzP+wZxRKRmENyLQl/CHZUbNBjrZ8nb5pl0dwuyNL0oqOQ582r+Hwt'
                'WHU5D3clAvOLmlHpnqZDeWVzKdqyXYq7QCuEA0N6qqaLGt5a6GU+Rbq7oaiuqDm73SKWxEEby9NJ514h634q4tcpALfuCqiTD64u'
                '3nuFE0+E2qSigLnfZp5J+XWUGDbiZVWDdIjg41JlQeqpTpENj+0qoHy3XqiexptiR8aFX5MTpdAPvc2idXNDWVMjpD4zikUpnWH7'
                'brNyzot8jvDQ3MBkEdqsNSxhb2VEXeKkv2EYKKpPciHKm8rx8kd8qzrkgHmMycryIXFMM+U4jrn0hysiTyoIr9+YuRO7GlX99nF3'
                'mnCdfM+TDfBdufwdCDUwbCyIl6jlD3KSPtfuR7OXxl/NxYfR+xpb9a2kbI4ZLMz3HSkOF19kgK9TsmWCPUKu9XsnueQaY6T7EpPD'
                'OiVwypYBeZhid0WuT/gWjRafqQR6UV7cwMOIflCV+8nrYsdo5ig4RxWPF7NuUJHQIlFERG5EqhIUFvOyS33ZCpNeUkPNUL4cdYyQ'
                '8+rK+ubsBf3odkOyo9I16d2BLUrhuPFiicgrkGMEXtp+AqcUwrJYz2nlk3C1VJPYDklGiGC1dP4GWmZJPgiOjkpVypFKosMy6f0n'
                'Tkg0xM062ZAWbVq7RgdX3ZAUi3vkpvMFTl7MP+Kcnt7IdjOJQpU68a5QPnmqgLGv0Vd1lGhyAewMTX4pSPrNUe2kFBpaG+SUEmso'
                'ghoD4kn69CC9sCmxqloMquAxqegpytm6Ahjcdh3IG5xlt/KYn1Lu10VpS6ub7oPad3VcqqjLCsdzd/tKFu3Xxlp9DlrAs5svFrmS'
                '8Faf3wr/+kBpxr75zZRxdg6TKSgS4fS+9aa4lVrMm5QXF7yqFw3hU32lkgO46uao0XpWF9/yJeEEM0GlV0nii4vh1INVBAvskK2M'
                'c9QuiWqeKv3mhQ/kyqAYq1GI2dhYBitFZUcpGU3jlJrTN+qD2nd1XKQx84l9yS3eHayOtfk5lGcd0J+R5t1/U7r92vfPcQkx6APv'
                '24+IssVr7q/uW3/C9V9/44B7Xc8Iv3r91vM4EvtkbbSocBg5dndO6ek5rMJp6405ZUfHUkFiKCva+ANK7fEOWFbDv3cW4WBr2Lug'
                '7wZXLRT4uvBImuHeQhL9DEP6CjgbPoDWrk1sxXdyu+trd7lhRb2A3plUhhzPFKlE2u0uW/PKjz/ve4N3ePw/udK7NA=='
            ),
        },
    },
}
