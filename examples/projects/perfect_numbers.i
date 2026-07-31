# Perfect numbers below 1000

umurimo ni_perfect(n: int) -> int
    shyira total = 0
    kuri d muri 1 kugeza n
        niba n % d == 0
            total = total + d
        iherezo
    iherezo
    niba total == n
        subira 1
    iherezo
    subira 0
iherezo

shyira_ko MAX = 1000

andika "Perfect numbers below " + shobora_umuntu(MAX) + ":"
kuri n muri 2 kugeza MAX
    niba ni_perfect(n) == 1
        andika n
    iherezo
iherezo
