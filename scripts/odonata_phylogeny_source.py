"""Literature-based family-level phylogeny of Odonata (dragonflies and
damselflies), keyed to the family names used by the World Odonata List.

HOW TO READ THIS
----------------
Same conventions as phylogeny_source.py (birds). The tree is a nested Python
literal. A plain string is a terminal: a World Odonata List family. A tuple
(name, [children]) is an internal clade; `name` may be None where the clade has
no established name. Nodes with three or more children are POLYTOMIES, and they
are deliberate — they mark nodes the cited study did not resolve, did not
sample, or resolved only with poor support. Resolving one requires a citation,
not a guess.

The World Odonata List puts two species of Sciotropis in Calopterygoidea as
"INCERTAE SEDIS". The page and generate_odonata_data.py turn that row into the
pseudo-family "<superfamily> incertae sedis", so it is a tip here too.

PRIMARY SOURCES
---------------
One citation per line; a line beginning with '#' is a grouping header, not a
source. generate_odonata_data.py parses this block, so keep the format.

# Backbone, Zygoptera and Anisoptera
Bybee, S.M. et al. 2021. Phylogeny and classification of Odonata using targeted genomics. Mol. Phylogenet. Evol. 160:107115.
# Classification and family composition
Schorr, M. & Paulson, D. World Odonata List. Slater Museum of Natural History, University of Puget Sound.
Goodman, A. et al. 2025. Systematic and taxonomic revision of emerald and tigertail dragonflies (Anisoptera: Synthemistidae and Corduliidae). Syst. Entomol. e70000.

KNOWN LIMITATION
----------------
Libelluloidea is left as a polytomy of its thirteen families. Goodman et al.
2025 split the old Corduliidae and Synthemistidae into the families used here,
but their family-level tree could not be consulted, and Bybee et al. 2021
sampled too few of these lineages (before the split) to place them. Within the
damselflies, Bybee et al. describe the former Calopterygoidea as a pectinate
grade of four groups toward Coenagrionoidea with low quartet support along
that backbone; the text does not state the order of groups 2 and 3, so they
form a polytomy with group 4 + Coenagrionoidea. Rimanellidae and Sciotropis
were not sampled and are placed only by their World Odonata List superfamily.
"""

# --- Zygoptera: Bybee et al. 2021, sections 4.1.2-4.1.6 ---------------------

# Hemiphlebia sister to the remaining Lestoidea; Perilestidae + Synlestidae
# recovered together (BS 100, PP 1), with Lestidae outside them.
LESTOIDEA = ("Lestoidea", [
    "Hemiphlebiidae",
    (None, [
        (None, ["Perilestidae", "Synlestidae"]),
        "Lestidae",
    ]),
])

# 'Calopterygoidea' group 2 (BS 100, PP 1, QS 0.47/0.44/0.97). The three
# Afrotropical families form a well-supported cluster; Mesagrion is sister to
# Dicteriadidae + Hypolestidae; Heteragrionidae + Polythoridae is one of the
# weakly supported backbone nodes. Philogeniidae's position is not stated and
# Rimanellidae was not sampled.
GROUP2 = ("'Calopterygoidea' group 2", [
    ("Tatocnemidoidea", ["Pentaphlebiidae", "Protolestidae", "Tatocnemididae"]),
    ("Polythoroidea", [
        (None, ["Mesagrionidae", (None, ["Dicteriadidae", "Hypolestidae"])]),
        (None, ["Heteragrionidae", "Polythoridae"]),
        "Philogeniidae",
        "Rimanellidae",
    ]),
])

# 'Calopterygoidea' group 3 (BS 100, PP 1, QS 0.48/0.59/0.96).
# Amanipodagrion + Mesopodagrion is sister to the rest of the group;
# Euphaeidae + Lestoideidae, then Pseudolestidae; (Devadattidae +
# Amphipterygidae) + (Thaumatoneuridae + Rhipidolestidae), the last a
# weakly supported node.
GROUP3 = ("'Calopterygoidea' group 3", [
    ("Mesopodagrionoidea", ["Amanipodagrionidae", "Mesopodagrionidae"]),
    (None, [
        ("Euphaeoidea", [
            (None, ["Euphaeidae", "Lestoideidae"]),
            "Pseudolestidae",
        ]),
        ("Amphipterygoidea", [
            (None, ["Devadattidae", "Amphipterygidae"]),
            (None, ["Thaumatoneuridae", "Rhipidolestidae"]),
        ]),
    ]),
])

# 'Calopterygoidea' group 4 (BS 100, PP 1, QS 0.37/0.42/0.96): "three pairs
# of families", sister to Coenagrionoidea. How the pairs relate is not stated.
# Sciotropis (not sampled) joins Calopterygidae + Chlorocyphidae as a polytomy.
GROUP4 = ("'Calopterygoidea' group 4", [
    ("Philogangoidea", ["Philogangidae", "Philosinidae"]),
    ("Megapodagrionoidea", ["Megapodagrionidae", "Argiolestidae"]),
    ("Calopterygoidea", [
        "Calopterygidae", "Chlorocyphidae", "Calopterygoidea incertae sedis",
    ]),
])

# Isostictidae sister to Platycnemididae + Coenagrionidae (BS 100, PP 1, but
# QS -0.33 — counter-support at this node).
COENAGRIONOIDEA = ("Coenagrionoidea", [
    "Isostictidae",
    (None, ["Platycnemididae", "Coenagrionidae"]),
])

ZYGOPTERA = ("Zygoptera", [
    LESTOIDEA,
    (None, [
        "Platystictidae",                       # Platystictoidea
        (None, [
            "Priscagrionidae",                  # group 1 (Priscagrionoidea)
            (None, [                            # order of groups 2 and 3 unstated
                GROUP2,
                GROUP3,
                (None, [GROUP4, COENAGRIONOIDEA]),
            ]),
        ]),
    ]),
])

# --- Anisozygoptera + Anisoptera: Bybee et al. 2021, sections 4.1.8-4.1.12 ---

# See KNOWN LIMITATION.
LIBELLULOIDEA = ("Libelluloidea", [
    "Pseudocorduliidae", "Gomphomacromiidae", "Synthemistidae",
    "Austrocorduliidae", "Idomacromiidae", "Macromiidae", "Idionychidae",
    "Lauromacromiidae", "Macromidiidae", "Neophyidae", "Libellulidae",
    "Aeschnosomatidae", "Corduliidae",
])

# Aeshnoidea sister to the remaining Anisoptera; Gomphidae + Petaluridae
# (BS 97) sister to Cordulegastroidea + Libelluloidea; within
# Cordulegastroidea, Chlorogomphidae + (Neopetaliidae + Cordulegastridae).
ANISOPTERA = ("Anisoptera", [
    ("Aeshnoidea", ["Austropetaliidae", "Aeshnidae"]),
    (None, [
        ("Gomphoidea", ["Petaluridae", "Gomphidae"]),
        ("Cordulegastroidea + Libelluloidea", [
            ("Cordulegastroidea", [
                "Chlorogomphidae",
                (None, ["Neopetaliidae", "Cordulegastridae"]),
            ]),
            LIBELLULOIDEA,
        ]),
    ]),
])

# Bybee et al. advise against the name Epiprocta, so this clade is left
# descriptive.
TREE = ("Odonata", [
    ZYGOPTERA,
    ("Anisozygoptera + Anisoptera", [
        "Epiophlebiidae",
        ANISOPTERA,
    ]),
])
