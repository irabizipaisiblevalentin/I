# Function examples in I

# Simple function
umurimo sagura(a: int, b: int) -> int
    subira a + b
iherezo

# Function with multiple operations
umurimo kora_ikintu(x: int, y: int) -> int
    shyira result = x * y
    subira result + 10
iherezo

# Calling functions
shyira sum = sagura(5, 3)
andika sum

shyira result = kora_ikintu(4, 5)
andika result
