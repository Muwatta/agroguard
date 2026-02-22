ADVICE = {
"bird":"Use netting or reflective tape.",
"armyworm":"Apply neem or approved pesticide early.",
"beetle":"Use light traps or remove manually.",
"weevil":"Remove residues and dry crops.",
"grasshopper":"Use barriers or organic spray."
}

def get_advice(pest):
    return ADVICE.get(pest,"Monitor farm.")