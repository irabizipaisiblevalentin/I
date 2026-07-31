# Greatest common divisor and least common multiple

umurimo gcd(a: int, b: int) -> int
    wihuse b != 0
        shyira r = a % b
        a = b
        b = r
    iherezo
    subira a
iherezo

umurimo lcm(a: int, b: int) -> int
    subira a / gcd(a, b) * b
iherezo

andika "gcd(48, 36) = " + shobora_umuntu(gcd(48, 36))
andika "gcd(17, 5)  = " + shobora_umuntu(gcd(17, 5))
andika "lcm(12, 18) = " + shobora_umuntu(lcm(12, 18))
andika "lcm(7, 5)   = " + shobora_umuntu(lcm(7, 5))
