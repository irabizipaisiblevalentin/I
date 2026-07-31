# Sum of the digits of a number

umurimo umubare_umubare(n: int) -> int
    shyira total = 0
    wihuse n irenze 0
        total = total + n % 10
        n = n / 10
        n = uburengero(n)
    iherezo
    subira total
iherezo

andika "Sum of digits of 12345 = " + shobora_umuntu(umubare_umubare(12345))
andika "Sum of digits of 987654 = " + shobora_umuntu(umubare_umubare(987654))
andika "Sum of digits of 7 = " + shobora_umuntu(umubare_umubare(7))
