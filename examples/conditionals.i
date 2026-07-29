# Conditional examples in I

# Simple if
shyira x = 10
niba x irenze 5
    andika "X ni kure"
iherezo

# If-else
niba x irenze 15
    andika "X ni binini"
cyangwa
    andika "X si binini"
iherezo

# If-elif-else
niba x irenze 20
    andika "X ni cyane"
cyangwa_niba x irenze 15
    andika "X ni binini"
cyangwa
    andika "X ni gitoya"
iherezo
