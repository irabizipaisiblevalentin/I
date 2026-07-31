# Multiplication table

shyira_ko SIZE = 9

kuri i muri 1 kugeza SIZE + 1
    shyira row = ""
    kuri j muri 1 kugeza SIZE + 1
        shyira cell = i * j
        shyira text_cell = shobora_umuntu(cell)
        niba cell munsi_ya 10
            text_cell = "  " + text_cell
        cyangwa_niba cell munsi_ya 100
            text_cell = " " + text_cell
        iherezo
        row = row + text_cell + " "
    iherezo
    andika row
iherezo
