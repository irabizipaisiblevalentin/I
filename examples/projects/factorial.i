# Factorials, recursive and iterative

umurimo factorial_rec(n: int) -> int
    niba n munsi_ya 2
        subira 1
    iherezo
    subira n * factorial_rec(n - 1)
iherezo

umurimo factorial_iter(n: int) -> int
    shyira result = 1
    kuri i muri 1 kugeza n + 1
        result = result * i
    iherezo
    subira result
iherezo

kuri n muri 0 kugeza 10
    andika shobora_umuntu(n) + "! = " + shobora_umuntu(factorial_rec(n)) + " (recursive) / " + shobora_umuntu(factorial_iter(n)) + " (iterative)"
iherezo
