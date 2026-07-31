# Diamond pattern with loops and string building

shyira_ko N = 4
shyira_ko M = 2 * N - 1

kuri i muri 0 kugeza M
    shyira content = ""
    shyira stars = N - i
    niba i irenze N - 1
        stars = i - N + 2
    iherezo
    kuri s muri 0 kugeza N - stars
        content = content + " "
    iherezo
    kuri st muri 0 kugeza 2 * stars - 1
        content = content + "*"
    iherezo
    andika content
iherezo
