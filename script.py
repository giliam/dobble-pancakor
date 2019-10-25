"""
Permet de construire un jeu de dooble.

Issu de http://math.univ-lyon1.fr/~deleglis/PDF/dobble.pdf. 
"""
VERBOSE = False

# nb premier
p = 5
nb_sym_per_cards = p + 1
print(nb_sym_per_cards, "symboles par carte")

points = range(p)
nb_cards = p * p + p + 1
print(nb_cards, "cartes")

infinite_projection = [nb_cards - p - 1 + i for i in range(p + 1)]


def build_line_vertical(p, start):
    return [start + p * i for i in range(p)] + [infinite_projection[-1]]


def build_line(p, start, slope):
    if slope == "inf" or slope >= p:
        if VERBOSE:
            print("Wrong slope")
        return build_line_vertical(p, start)
    return [(start * p + (slope * p + 1) * i) % (p * p) for i in range(p)] + [
        infinite_projection[slope]
    ]


"""
La grille va ressembler à ça :

...
3 . . . .
2 . . . .
1 . . . .
0 . . . .
  0 1 2 3 
"""

cards = []

# On parcourt à abscisse = 0 et on monte sur les ordonnées...
for slope in range(p):
    for start in range(p):
        card = build_line(p, start, slope)
        cards.append(card)
        if VERBOSE:
            print("Start", start)
            print("Slope", slope)
            print("Card", card)

# ...sauf pour les droites verticales qu'il faut de toute façon créer pour chaque abscisse
for i in range(p):
    cards.append(build_line_vertical(p, i))

# On n'oublie pas la carte "infinie"
cards.append(infinite_projection)

print("Nb de cartes", len(cards))
print("Cartes", cards)


def check_validity(cards):
    _cards = [set(c) for c in cards]

    nb_errors = 0
    for i, card1 in enumerate(_cards):
        for j, card2 in enumerate(_cards[i + 1 :]):
            if len(card1.intersection(card2)) != 1:
                nb_errors += 1
                if VERBOSE:
                    print(card1, card2)
                if VERBOSE:
                    print(card1.intersection(card2))
    print(nb_errors, "erreur(s)")


check_validity(cards)
