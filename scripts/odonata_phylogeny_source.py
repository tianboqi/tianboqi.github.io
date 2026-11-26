"""Literature-based family-level phylogeny of Odonata (dragonflies and
damselflies), keyed to the family names used by the World Odonata List.

HOW TO READ THIS
----------------
Same conventions as phylogeny_source.py (birds). The tree is a nested Python
literal. A plain string is a terminal: a World Odonata List family. A tuple
(name, [children]) is an internal clade; `name` may be None where the clade has
no established name. Nodes with three or more children are POLYTOMIES, and they
are deliberate — they mark nodes the cited study did not resolve or did not
sample. Resolving one requires a citation, not a guess.

The topology is read from Figure 1 of Carter et al. 2026, which summarises
Newton et al. 2026 (all families outside Libelluloidea) and Goodman et al. 2026
(Libelluloidea). Every node of that figure is kept. Nodes the figure marks with
an asterisk (bootstrap below 100 in the source study) are noted with "BS<100"
beside them; they are kept resolved, as Carter et al. use them to define the
superfamilies.

The World Odonata List puts two species of Sciotropis in Calopterygoidea as
"INCERTAE SEDIS". The page and generate_odonata_data.py turn that row into the
pseudo-family "<superfamily> incertae sedis", so it is a tip here too.

PRIMARY SOURCES
---------------
One citation per line; a line beginning with '#' is a grouping header, not a
source. generate_odonata_data.py parses this block, so keep the format.

# Family-level tree (Figure 1) and superfamilies
Carter, P. et al. 2026. The classification and diversity of extant dragonflies and damselflies (Odonata). Int. J. Odonatol. 29:95-124. doi:10.48156/1388.2026.1917385
# Studies the figure summarises
Newton, L.G. et al. 2026. Soaring systematics: an evaluation of biogeography and flight behavior in dragonflies and damselflies (Insecta: Odonata) using phylogenomics. Syst. Biol. doi:10.1093/sysbio/syag005
Goodman, A. et al. 2026. Systematic and taxonomic revision of emerald and tigertail dragonflies (Anisoptera: Synthemistidae and Corduliidae). Syst. Entomol. 51(1):e70000. doi:10.1111/syen.70000
# Classification and family composition
Schorr, M. & Paulson, D. World Odonata List. Slater Museum of Natural History, University of Puget Sound.

KNOWN LIMITATION
----------------
Sciotropis (Calopterygoidea incertae sedis in the World Odonata List) is absent
from the phylogenies Carter et al. 2026 summarise and cannot be placed in a
family, so it forms a polytomy with Calopterygidae and Chlorocyphidae. Eight
nodes rest on bootstrap support below 100 in the source studies.
"""

# --- Zygoptera: Newton et al. 2026, via Carter et al. 2026 Fig. 1 -----------

LESTOIDEA = ("Lestoidea", [                     # BS<100
    "Hemiphlebiidae",
    (None, [
        "Lestidae",
        (None, ["Perilestidae", "Synlestidae"]),
    ]),
])

TATOCNEMIDOIDEA = ("Tatocnemidoidea", [
    "Tatocnemididae",
    (None, ["Pentaphlebiidae", "Protolestidae"]),
])

POLYTHOROIDEA = ("Polythoroidea", [
    (None, ["Rimanellidae", "Polythoridae"]),
    (None, [
        (None, ["Philogeniidae", "Heteragrionidae"]),               # BS<100
        (None, ["Mesagrionidae",                                    # BS<100
                (None, ["Dicteriadidae", "Hypolestidae"])]),
    ]),
])

MESOPODAGRIONOIDEA = ("Mesopodagrionoidea", ["Amanipodagrionidae", "Mesopodagrionidae"])

AMPHIPTERYGOIDEA = ("Amphipterygoidea", [
    (None, ["Devadattidae", "Amphipterygidae"]),
    (None, ["Rhipidolestidae", "Thaumatoneuridae"]),
])

EUPHAEOIDEA = ("Euphaeoidea", [
    "Pseudolestidae",
    (None, ["Lestoideidae", "Euphaeidae"]),
])

PHILOGANGOIDEA = ("Philogangoidea", ["Philogangidae", "Philosinidae"])

MEGAPODAGRIONOIDEA = ("Megapodagrionoidea", ["Megapodagrionidae", "Argiolestidae"])

# Sciotropis is not in the figure: see KNOWN LIMITATION.
CALOPTERYGOIDEA = ("Calopterygoidea", [
    "Chlorocyphidae", "Calopterygidae", "Calopterygoidea incertae sedis",
])

COENAGRIONOIDEA = ("Coenagrionoidea", [
    "Isostictidae",
    (None, ["Platycnemididae", "Coenagrionidae"]),
])

ZYGOPTERA = ("Zygoptera", [
    LESTOIDEA,
    (None, [
        "Platystictidae",                       # Platystictoidea
        (None, [
            "Priscagrionidae",                  # Priscagrionoidea
            (None, [
                (None, [TATOCNEMIDOIDEA, POLYTHOROIDEA]),
                (None, [
                    (None, [                    # BS<100
                        MESOPODAGRIONOIDEA,
                        (None, [AMPHIPTERYGOIDEA, EUPHAEOIDEA]),    # BS<100
                    ]),
                    (None, [
                        (None, [
                            PHILOGANGOIDEA,
                            (None, [MEGAPODAGRIONOIDEA, CALOPTERYGOIDEA]),
                        ]),
                        COENAGRIONOIDEA,
                    ]),
                ]),
            ]),
        ]),
    ]),
])

# --- Anisozygoptera + Anisoptera: Newton et al. 2026 and, for Libelluloidea,
# Goodman et al. 2026, via Carter et al. 2026 Fig. 1 ---------------------------

LIBELLULOIDEA = ("Libelluloidea", [
    (None, [                                    # BS<100
        "Pseudocorduliidae",
        (None, ["Gomphomacromiidae", "Synthemistidae"]),
    ]),
    (None, [
        "Austrocorduliidae",
        (None, [                                # BS<100
            (None, [                            # BS<100
                "Idomacromiidae",
                (None, ["Macromiidae", "Idionychidae"]),
            ]),
            (None, [
                "Lauromacromiidae",
                (None, [
                    "Macromidiidae",
                    (None, [
                        "Neophyidae",
                        (None, [
                            "Corduliidae",
                            (None, ["Aeschnosomatidae", "Libellulidae"]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ]),
])

ANISOPTERA = ("Anisoptera", [
    ("Aeshnoidea", ["Austropetaliidae", "Aeshnidae"]),
    (None, [
        ("Gomphoidea", ["Petaluridae", "Gomphidae"]),
        (None, [
            ("Cordulegastroidea", [
                "Chlorogomphidae",
                (None, ["Neopetaliidae", "Cordulegastridae"]),
            ]),
            LIBELLULOIDEA,
        ]),
    ]),
])

TREE = ("Odonata", [
    ZYGOPTERA,
    ("Anisozygoptera + Anisoptera", [
        "Epiophlebiidae",
        ANISOPTERA,
    ]),
])
