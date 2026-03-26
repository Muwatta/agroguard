def get_advice(pest):
    """Get advice for detected pest"""
    advice_map = {
        "bird": "Install bird netting or reflective tape to deter birds.",
        "armyworm": "Apply biological pesticides like Bt or neem oil immediately.",
        "beetle": "Use pheromone traps or hand-pick beetles in early morning.",
        "weevil": "Apply diatomaceous earth around plant bases.",
        "grasshopper": "Use biological control with Nosema locustae or neem oil."
    }
    return advice_map.get(pest, "Consult agricultural extension for this pest.")
