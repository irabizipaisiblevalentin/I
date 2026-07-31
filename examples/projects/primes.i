# Prime numbers below 50

umurimo ni_umubare_mwiza(n: int) -> int
    niba n munsi_ya 2
        subira 0
    iherezo
    shyira i = 2
    wihuse i * i <= n
        niba n % i == 0
            subira 0
        iherezo
        i = i + 1
    iherezo
    subira 1
iherezo

andika "Prime numbers below 50:"
kuri n muri 2 kugeza 50
    niba ni_umubare_mwiza(n) == 1
        andika n
    iherezo
iherezo
