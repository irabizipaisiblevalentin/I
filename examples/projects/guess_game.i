# Guess the number game (interactive — reads from standard input)
#
# Run: i examples/projects/guess_game.i -r
# Non-interactive: echo 7 | i examples/projects/guess_game.i -r

shyira secret = 7
shyira found = false
shyira attempts = 0

kugeza found
    andika "Guess a number between 1 and 10:"
    shyira guess = uburengero(soma())
    attempts = attempts + 1
    niba guess == secret
        andika "Correct! You took " + shobora_umuntu(attempts) + " attempt(s)."
        found = true
    cyangwa_niba guess irenze secret
        andika "Too high."
    cyangwa
        andika "Too low."
    iherezo
iherezo
