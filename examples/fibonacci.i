# Fibonacci sequence in I

umurimo fibonacci(n: int) -> int
    niba n munsi_ya 2
        subira n
    iherezo
    subira fibonacci(n - 1) + fibonacci(n - 2)
iherezo

# Print first 10 Fibonacci numbers
buri i muri 0 kugeza 10
    andika fibonacci(i)
iherezo
