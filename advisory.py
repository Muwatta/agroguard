def get_advice(pest):
    """Get advice for detected pest based on new 5-class model"""
    advice_map = {
        "armyworm": "Apply biological pesticides like Bt or neem oil immediately.",
        "aphid": "Spray insecticidal soap or neem oil; encourage ladybugs for natural control.",
        "mealybug": "Remove infested plant parts and apply neem oil or horticultural oil.",
        "stem_borer": "Use pheromone traps, and remove and destroy affected stems.",
        "weevil": "Apply diatomaceous earth around plant bases and remove affected plants."
    }
    return advice_map.get(pest, "Consult agricultural extension for this pest.")