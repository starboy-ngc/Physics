"""Palette de l'outil : une seule source pour l'ecran et les documents.

Les couleurs vivaient en quatre exemplaires — la fenetre, le rapport, les
slides, les graphiques — et avaient commence a diverger : l'encre valait
`#111c26` a l'ecran et `#1b2733` dans les documents. Elles sont reunies
ici, dans le moteur, parce que les documents sont produits sans interface.

Un theme ne declare que deux couleurs : l'encre et l'accent. Tout le reste
— gris de lecture, filets, aplats, survols — en est deduit par melange avec
le blanc, ce qui garantit qu'un theme reste coherent sans avoir a accorder
vingt valeurs a la main.

Trois familles ne suivent pas le theme, et c'est deliberé :

* les couleurs de severite (vigilance, critique, conforme) portent un sens
  qu'un choix esthetique ne doit pas pouvoir contredire ;
* le couple femmes / hommes est fixe dans la famille bleu-orange, la seule
  qui reste distinguable pour un daltonisme deutan — le plus repandu ;
* la palette categorielle sert a *distinguer* des modalites, pas a signer
  un document ; seule sa premiere couleur suit l'accent.

L'utilisateur choisit son accent — dans une palette integree, ou en
tapant le code couleur de sa charte. Ce qu'il ne peut pas faire, c'est
rendre l'outil illisible : tout accent, choisi ou tape, doit laisser le
blanc lisible sur lui, et il est refuse sinon. Le reste de la palette —
encre, gris, filets, severites — ne se saisit pas : il se deduit.
"""

from __future__ import annotations

from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Tuple

WHITE = "#ffffff"

#: Theme applique quand rien n'est configure.
DEFAULT_THEME = "auroral"


# --------------------------------------------------------------- melanges

def _rgb(colour: str) -> Tuple[int, int, int]:
    value = colour.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def _hex(rgb: Tuple[float, float, float]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(part))):02x}" for part in rgb)


def mix(colour: str, other: str, weight: float) -> str:
    """`colour` melange a `other`, `weight` etant la part de `other`."""
    first, second = _rgb(colour), _rgb(other)
    return _hex(tuple(a + (b - a) * weight for a, b in zip(first, second)))


def _luminance(colour: str) -> float:
    """Luminance relative WCAG."""
    channels = []
    for part in _rgb(colour):
        ratio = part / 255.0
        channels.append(ratio / 12.92 if ratio <= 0.04045
                        else ((ratio + 0.055) / 1.055) ** 2.4)
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first: str, second: str) -> float:
    """Rapport de contraste WCAG entre deux couleurs, de 1 a 21."""
    light, dark = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def distance(first: str, second: str) -> float:
    """Ecart euclidien entre deux couleurs, pour juger qu'elles se separent."""
    return sum((a - b) ** 2 for a, b in zip(_rgb(first), _rgb(second))) ** 0.5


# ------------------------------------------------------------ invariants

#: Severites. Un theme ne les touche pas : du vert sur « critique » serait
#: un contresens, pas une preference.
WARN = "#8a5a12"
CRIT = "#8f2f2f"
OK = "#2f6b4f"
#: Leurs aplats ne sont pas de simples eclaircies : un melange lineaire au
#: blanc rend un beige eteint, la ou l'oeil attend un fond chaud qui signale
#: sans crier. Ils sont donc poses, pas calcules.
WARN_SOFT = "#fdf4e3"
CRIT_SOFT = "#fbeded"

#: Couple femmes / hommes. Les deux teintes sont la meme couleur a la
#: rotation pres : meme luminosite, meme saturation, canaux rouge et bleu
#: echanges. Elles se lisent comme un couple et non comme deux choix
#: separes, et le rouge y gagne au passage un contraste de 7,9 sur blanc
#: contre 3,8 a l'orange qu'il remplace.
#:
#: Le rouge est pose a 330 degres et non a zero : a zero il vaut #8a2f2f,
#: soit cinq points de distance du rouge « critique » — mesure faite, les
#: deux etaient indiscernables cote a cote. A 330 il en reste 46, et il se
#: lit encore comme un rouge et non comme un violet.
#:
#: Rouge et bleu restent distincts pour un daltonisme deutan, ce qui n'est
#: le cas ni du vert-rouge ni du vert-orange.
FEMALE = "#8a2f5d"
MALE = "#2f5d8a"
#: Remplissages clairs du couple. Une boite a moustaches se lit par son
#: contour ; l'aplat ne fait qu'appartenir au sexe, il ne doit pas peser.
FEMALE_SOFT = "#f0e0e8"
MALE_SOFT = "#dfe7ee"

#: Reserve ou puiser la palette categorielle des graphiques. Sa premiere
#: couleur suit l'accent du theme ; les suivantes sont prises ici, dans
#: l'ordre, en ecartant celles qui ressembleraient trop a cet accent — sans
#: quoi le theme Prune donnerait deux violets voisins dans une meme legende.
SERIES_POOL: Tuple[str, ...] = (
    "#c26b3f", "#4f8f6d", "#8a5f9e", "#b0453f", "#3f7d9e",
    "#8d7b3a", "#6b6b6b", "#7a4f6d", "#4a6d3f", "#2f7d7a", "#9e5f3f",
)

#: Ecart minimal entre deux couleurs de series pour qu'on les separe.
SERIES_GAP = 55.0

#: Nombre de modalites coloriees avant de recycler les couleurs.
SERIES_COUNT = 10


def _series(accent: str) -> Tuple[str, ...]:
    """Serie categorielle menee par l'accent, sans couleur trop voisine.

    Seule la distance a l'accent est verifiee : la reserve est deja un jeu
    de teintes distinctes, c'est la couleur ajoutee en tete qui pourrait y
    faire doublon.
    """
    chosen = [accent]
    for colour in SERIES_POOL:
        if len(chosen) >= SERIES_COUNT:
            break
        if distance(colour, accent) >= SERIES_GAP:
            chosen.append(colour)
    return tuple(chosen)


class Palette(NamedTuple):
    """Toutes les couleurs nommees par leur role, jamais par leur teinte."""

    theme: str
    # neutres, du plus dense au plus clair
    ink: str
    ink_soft: str
    muted: str
    faint: str
    disabled: str
    line_strong: str
    line: str
    grid: str
    panel: str
    stripe: str
    canvas: str
    # accent et ses declinaisons
    accent: str
    accent_hover: str
    accent_soft: str
    accent_deep: str
    # severites
    warn: str
    warn_soft: str
    crit: str
    crit_soft: str
    ok: str
    # lecture par sexe
    female: str
    male: str
    # series categorielles
    series: Tuple[str, ...]


def _build(name: str, ink: str, accent: str) -> Palette:
    """Deduit une palette complete de son encre et de son accent."""
    return Palette(
        theme=name,
        ink=ink,
        # Les poids ne sont pas choisis a l'oeil : ils sont ceux qui
        # reproduisent, sur l'encre du theme d'origine, les rapports de
        # contraste de la palette d'avant — 8,9 pour le texte courant,
        # 4,5 pour le secondaire, seuil AA — le gris secondaire est
        # legerement resserre pour que le theme le plus clair le
        # tienne aussi. Un theme ne peut donc pas
        # rendre l'outil moins lisible qu'il ne l'etait.
        ink_soft=mix(ink, WHITE, 0.205),
        muted=mix(ink, WHITE, 0.390),
        faint=mix(ink, WHITE, 0.599),
        disabled=mix(ink, WHITE, 0.772),
        line_strong=mix(ink, WHITE, 0.822),
        line=mix(ink, WHITE, 0.901),
        grid=mix(ink, WHITE, 0.930),
        panel=mix(ink, WHITE, 0.962),
        stripe=mix(ink, WHITE, 0.980),
        canvas=WHITE,
        accent=accent,
        # Le survol fonce l'accent vers l'encre plutot que vers le noir :
        # la teinte reste celle du theme.
        accent_hover=mix(accent, ink, 0.28),
        accent_soft=mix(accent, WHITE, 0.90),
        accent_deep=mix(accent, ink, 0.45),
        warn=WARN,
        warn_soft=WARN_SOFT,
        crit=CRIT,
        crit_soft=CRIT_SOFT,
        ok=OK,
        female=FEMALE,
        male=MALE,
        series=_series(accent),
    )


class Theme(NamedTuple):
    key: str            # nom technique, ASCII, ecrit dans la configuration
    label: str          # intitule affiche
    description: str    # a quoi il sert, pour choisir sans essayer
    palette: Palette


THEMES: Dict[str, Theme] = {
    theme.key: theme for theme in (
        Theme("auroral", "Auroral",
              "Bleu-vert lumineux sur nuit polaire.",
              _build("auroral", "#0b1d26", "#00768c")),
    )
}


#: Contraste minimal entre le blanc et un accent. C'est le seuil AA pour le
#: texte courant : le bouton principal ecrit en blanc sur l'accent, et un
#: accent trop clair rendrait son libelle illisible.
ACCENT_CONTRAST = 4.5

#: La palette integree : des accents tout faits, repartis sur le cercle des
#: teintes. Aucun n'est la pour faire joli — chacun tient le contraste
#: ci-dessus, et un test le verifie, de sorte qu'un clic ne peut pas rendre
#: l'outil illisible. Celui qui veut exactement la couleur de sa maison la
#: tape ; elle passe le meme controle, et elle est refusee si elle le rate.
ACCENTS: Tuple[Tuple[str, str], ...] = (
    ("Auroral", "#00768c"),
    ("Ardoise", "#2f5d8a"),
    ("Marine", "#17457a"),
    ("Indigo", "#4a3f9e"),
    ("Prune", "#6d3f63"),
    ("Grenat", "#8c2f4a"),
    ("Brique", "#9c4221"),
    ("Bronze", "#80601c"),
    ("Forêt", "#2f6b4f"),
    ("Olive", "#5c6b1f"),
    ("Graphite", "#4c5764"),
    ("Encre", "#2b3440"),
)


def names() -> List[Tuple[str, str]]:
    """Couples (cle, intitule) dans l'ordre d'affichage."""
    return [(theme.key, theme.label) for theme in THEMES.values()]


def normalise_accent(value: Any) -> Optional[str]:
    """Un code couleur ecrit a la main, ramene a « #rrggbb ».

    Accepte la forme courte a trois chiffres et le croisillon facultatif,
    parce que c'est sous ces trois formes qu'une charte graphique donne
    une couleur. Rend None sur tout le reste : mieux vaut garder l'accent
    en place que poser une couleur devinee.
    """
    texte = str(value or "").strip().lstrip("#").lower()
    if len(texte) == 3 and all(car in "0123456789abcdef" for car in texte):
        texte = "".join(car * 2 for car in texte)
    if len(texte) != 6 or not all(car in "0123456789abcdef" for car in texte):
        return None
    return f"#{texte}"


def accent_is_readable(colour: Optional[str]) -> bool:
    """Le blanc tient-il sur cet accent, et sur son survol ?

    Le survol est verifie lui aussi : il fonce l'accent vers l'encre, donc
    il ne peut qu'ameliorer le contraste au blanc — mais la regle est
    posee ici une fois pour toutes plutot que deduite d'un melange qui
    pourrait changer.
    """
    teinte = normalise_accent(colour)
    if teinte is None:
        return False
    fonce = mix(teinte, THEMES[DEFAULT_THEME].palette.ink, 0.28)
    return (contrast(WHITE, teinte) >= ACCENT_CONTRAST
            and contrast(WHITE, fonce) >= ACCENT_CONTRAST)


def by_name(name: Optional[str]) -> Palette:
    """Palette d'un theme, accent personnalise compris.

    Le nom peut porter un accent apres deux-points — « auroral:#8c2f4a ».
    C'est ce qui permet au theme de voyager dans un resultat d'analyse
    sous la forme d'une seule chaine, et donc a un document de se rejouer
    exactement tel qu'il a ete produit.

    Un nom inconnu retombe sur le theme par defaut, et un accent illisible
    ou mal ecrit est ignore : une configuration editee a la main doit
    pouvoir ouvrir l'outil, jamais l'empecher de s'ouvrir.
    """
    texte = str(name or "").strip().lower()
    base, _, accent = texte.partition(":")
    theme = THEMES.get(base) or THEMES[DEFAULT_THEME]
    if not accent:
        return theme.palette
    teinte = normalise_accent(accent)
    if teinte is None or not accent_is_readable(teinte):
        return theme.palette
    return _build(f"{theme.key}:{teinte}", theme.palette.ink, teinte)


def compose(theme_name: Optional[str], accent: Optional[str]) -> str:
    """Le nom que `by_name` relit, depuis un theme et un accent choisis."""
    base = str(theme_name or DEFAULT_THEME).strip().lower()
    teinte = normalise_accent(accent)
    if teinte is None or not accent_is_readable(teinte):
        return base
    if teinte == (THEMES.get(base) or THEMES[DEFAULT_THEME]).palette.accent:
        # L'accent d'origine n'est pas une personnalisation : l'ecrire
        # ferait porter au document un nom de theme qui n'existe pas.
        return base
    return f"{base}:{teinte}"


def resolve(config) -> Palette:
    """Palette du theme configure, accent personnalise compris."""
    return by_name(compose(
        config.get("theme_parameters.theme", DEFAULT_THEME),
        config.get("theme_parameters.accent", "")))


def from_analysis(analysis) -> Palette:
    """Palette du theme porte par une analyse.

    Le nom du theme voyage dans le resultat plutot que la configuration
    entiere : un document se rejoue ainsi tel qu'il a ete produit, meme si
    le parametrage a change depuis.
    """
    return by_name((analysis or {}).get("theme"))


def series_map(groups: Sequence[str], colours: Sequence[str],
               other: Optional[str] = None,
               neutral: Any = None) -> Dict[str, Any]:
    """Couleur de chaque modalite, le regroupement mis a part.

    Les quatre supports — ecran, HTML, SVG, PDF — coloriaient le nuage
    chacun de leur cote, par la position dans la liste. Le jour ou le
    moteur a regroupe la queue des modalites sous « Autres », il aurait
    fallu les corriger quatre fois, et le premier oubli aurait donne un
    regroupement de la couleur d'un vrai poste. La regle tient donc ici :
    la serie dans l'ordre, et le regroupement dans un neutre qui ne
    ressemble a aucune modalite.
    """
    mapping: Dict[str, Any] = {}
    rang = 0
    for group in groups:
        if other is not None and group == other:
            mapping[group] = neutral
            continue
        mapping[group] = colours[rang % len(colours)]
        rang += 1
    return mapping
