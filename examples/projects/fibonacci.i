# Fibonacci numbers in I

umurimo fibonacci(n: int) -> int
    niba n munsi_ya 2
        subira n
    iherezo
    subira fibonacci(n - 1) + fibonacci(n - 2)
iherezo

andika "Fibonacci numbers (first 12):"
kuri i muri 0 kugeza 12
    andika fibonacci(i)
iherezo
