"""Shared colour palette so static and interactive views agree."""

# Restaurants
COLOR_BAMBU = "#2a9d8f"
COLOR_CAMAROES = "#e63946"
COLOR_UNKNOWN_RESTAURANT = "#00b4d8"

# Ingredient categories
COLOR_INGREDIENT = {
    "PROTEINA": "#e76f51",
    "CARBOIDRATO": "#f4a261",
    "VEGETAL": "#8ab17d",
    "LATICINIO": "#e9c46a",
    "TEMPERO_MOLHO": "#b5838d",
    "OUTRO": "#9e9e9e",
}


def dish_color(restaurant: str) -> str:
    if restaurant == "Bambu":
        return COLOR_BAMBU
    if restaurant == "Camarões":
        return COLOR_CAMAROES
    return COLOR_UNKNOWN_RESTAURANT


def ingredient_color(category: str | None) -> str:
    return COLOR_INGREDIENT.get(category or "OUTRO", COLOR_INGREDIENT["OUTRO"])
