# Palindromic primes: primes whose digit reversal is also prime

umurimo ni_prime(n: int) -> int
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

umurimo reverse(n: int) -> int
    shyira reversed = 0
    wihuse n irenze 0
        reversed = reversed * 10 + n % 10
        n = uburengero(n / 10)
    iherezo
    subira reversed
iherezo

shyira_ko MAX = 200

andika "Palindromic primes below " + shobora_umuntu(MAX) + ":"
kuri n muri 2 kugeza MAX
    niba ni_prime(n) == 1
        niba ni_prime(reverse(n)) == 1
            andika n
        iherezo
    iherezo
iherezo
