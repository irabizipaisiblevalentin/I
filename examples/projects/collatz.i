# The Collatz sequence

umurimo collatz(n: int) -> int
    shyira steps = 0
    wihuse n != 1
        niba n % 2 == 0
            n = n / 2
        cyangwa
            n = 3 * n + 1
        iherezo
        n = uburengero(n)
        steps = steps + 1
    iherezo
    subira steps
iherezo

shyira_ko N = 27
andika "Collatz steps for 27 = " + shobora_umuntu(collatz(N))

kuri n muri 1 kugeza 20
    andika shobora_umuntu(n) + " -> " + shobora_umuntu(collatz(n)) + " steps"
iherezo
