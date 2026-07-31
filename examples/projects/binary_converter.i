# Decimal to binary

umurimo binary(n: int) -> string
    shyira result = ""
    niba n == 0
        subira "0"
    iherezo
    wihuse n irenze 0
        result = shobora_umuntu(n % 2) + result
        n = uburengero(n / 2)
    iherezo
    subira result
iherezo

kuri n muri 0 kugeza 17
    andika shobora_umuntu(n) + " = " + binary(n)
iherezo
