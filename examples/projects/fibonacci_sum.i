# Sum of even Fibonacci numbers below 4,000,000 (iterative)

shyira a = 0
shyira b = 1
shyira total = 0

wihuse a munsi_ya 4000000
    niba a % 2 == 0
        total = total + a
    iherezo
    shyira next = a + b
    a = b
    b = next
iherezo

andika "Sum of even Fibonacci numbers below 4,000,000 = " + shobora_umuntu(total)
