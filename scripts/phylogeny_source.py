"""Literature-based family-level phylogeny of birds, keyed to the family names
used by the eBird/Clements checklist v2026.

HOW TO READ THIS
----------------
The tree is a nested Python literal. A plain string is a terminal: a Clements
family. A tuple (name, [children]) is an internal clade; `name` may be None
where the clade has no established name. Nodes with three or more children are
POLYTOMIES, and they are deliberate — they mark nodes where the cited studies
disagree or where support is weak. They are not placeholders for laziness, and
resolving one requires a citation, not a guess.

PRIMARY SOURCES
---------------
One citation per line; a line beginning with '#' is a grouping header, not a
source. generate_phylogeny.py parses this block, so keep the format.

# Backbone and non-passerine orders
Prum, R.O. et al. 2015. A comprehensive phylogeny of birds (Aves) using targeted next-generation DNA sequencing. Nature 526:569-573.
Jarvis, E.D. et al. 2014. Whole-genome analyses resolve early branches in the tree of life of modern birds. Science 346:1320-1331.
Kuhl, H. et al. 2021. An unbiased molecular approach using 3'-UTRs resolves the avian family-level tree of life. Mol. Biol. Evol. 38:108-127.
Stiller, J. et al. 2024. Complexity of avian evolution revealed by family-level genomes. Nature 629:851-860.
# Palaeognathae
Cloutier, A. et al. 2019. Whole-genome analyses resolve the phylogeny of flightless birds (Palaeognathae). Syst. Biol. 68:937-955.
Sackton, T.B. et al. 2019. Convergent regulatory evolution and loss of flight in paleognathous birds. Science 364:74-78.
# Strisores
Chen, A. & Field, D.J. 2020. Phylogenetic definitions for Caprimulgimorphae and other avian clades. BMC Evol. Biol. 20:146.
# Procellariiformes
Estandia, A. et al. 2021. Substitution rate variation in a robust procellariiform seabird phylogeny. Mol. Phylogenet. Evol. 160:107158.
# Charadriiformes
Baker, A.J. et al. 2007. Multiple gene evidence for expansion of extant penguins out of Antarctica. Biol. Lett. 3:205-209.
Cerny, D. & Natale, R. 2022. Comprehensive taxon sampling and vetted fossils help clarify the time tree of shorebirds. Mol. Phylogenet. Evol. 177:107620.
# Passeriformes backbone
Oliveros, C.H. et al. 2019. Earth history and the passerine superradiation. PNAS 116:7916-7925.
Moyle, R.G. et al. 2016. Tectonic collision and uplift of Wallacea triggered the global songbird radiation. Nat. Commun. 7:12709.
# Passerida
Cai, T. et al. 2019. Near-complete phylogeny and taxonomic revision of the world's babblers. Mol. Phylogenet. Evol. 130:346-356.
Alstrom, P. et al. 2013. Multilocus phylogeny of the avian family Alaudidae. Mol. Phylogenet. Evol. 69:1043-1056.
# Emberizoidea
Barker, F.K. et al. 2015. New insights into New World biogeography: an integrated view from the phylogeny of blackbirds, cardinals, sparrows, tanagers, warblers, and allies. Auk 132:333-348.

KNOWN LIMITATION
----------------
The base of Neoaves is left as a polytomy of well-supported superorders. This
is the famously recalcitrant part of the avian tree: Jarvis 2014, Prum 2015,
Kuhl 2021 and Stiller 2024 each recover a different arrangement of these
lineages, with short internodes and extensive gene-tree conflict. Asserting any
one of them here would misrepresent the state of the literature.
"""

# --- Palaeognathae: Cloutier 2019, Sackton 2019 (tinamous nested in ratites) --
PALAEOGNATHAE = ("Palaeognathae", [
    "Struthionidae",
    ("Notopalaeognathae", [
        "Rheidae",
        (None, [
            "Tinamidae",
            ("Novaeratitae", ["Apterygidae", "Casuariidae"]),
        ]),
    ]),
])

GALLOANSERAE = ("Galloanserae", [
    ("Anseriformes", [
        "Anhimidae",
        ("Anseres", ["Anseranatidae", "Anatidae"]),
    ]),
    ("Galliformes", [
        "Megapodiidae",
        (None, [
            "Cracidae",
            (None, [
                "Numididae",
                (None, ["Odontophoridae", "Phasianidae"]),
            ]),
        ]),
    ]),
])

# --- Strisores: Chen & Field 2020 -------------------------------------------
STRISORES = ("Strisores", [
    "Caprimulgidae",
    (None, [
        ("Nyctibiiformes+Steatornithiformes", ["Steatornithidae", "Nyctibiidae"]),
        (None, [
            "Podargidae",
            ("Daedalornithes", [
                "Aegothelidae",
                ("Apodiformes", [
                    ("Apodi", ["Apodidae", "Hemiprocnidae"]),
                    "Trochilidae",
                ]),
            ]),
        ]),
    ]),
])

COLUMBAVES = ("Columbaves", [
    ("Otidimorphae", [
        "Musophagidae",
        (None, ["Otididae", "Cuculidae"]),
    ]),
    ("Columbimorphae", [
        "Columbidae",
        (None, ["Mesitornithidae", "Pteroclidae"]),
    ]),
])

# --- Gruimorphae: Gruiformes + Charadriiformes (Prum 2015, Kuhl 2021) --------
GRUIFORMES = ("Gruiformes", [
    ("Ralloidea", [
        "Sarothruridae",
        (None, ["Heliornithidae", "Rallidae"]),
    ]),
    ("Gruoidea", [
        "Psophiidae",
        (None, ["Aramidae", "Gruidae"]),
    ]),
])

CHARADRIIFORMES = ("Charadriiformes", [
    ("Charadrii", [
        (None, ["Chionidae", "Pluvianellidae"]),
        "Burhinidae",
        "Pluvianidae",
        (None, [
            ("Recurvirostridae+", ["Ibidorhynchidae", "Recurvirostridae"]),
            (None, ["Haematopodidae", "Charadriidae"]),
        ]),
    ]),
    (None, [
        ("Scolopaci", [
            (None, ["Rostratulidae", "Jacanidae"]),
            (None, ["Thinocoridae", "Pedionomidae"]),
            "Scolopacidae",
        ]),
        ("Lari", [
            "Turnicidae",
            (None, ["Dromadidae", "Glareolidae"]),
            (None, [
                "Stercorariidae",
                (None, ["Alcidae", "Laridae"]),
            ]),
        ]),
    ]),
])

GRUIMORPHAE = ("Gruimorphae", [GRUIFORMES, CHARADRIIFORMES])

MIRANDORNITHES = ("Mirandornithes", ["Phoenicopteridae", "Podicipedidae"])

PHAETHONTIMORPHAE = ("Phaethontimorphae", [
    "Phaethontidae",
    ("Eurypygiformes", ["Rhynochetidae", "Eurypygidae"]),
])

# --- Aequornithes (core waterbirds): Prum 2015, Kuhl 2021 -------------------
AEQUORNITHES = ("Aequornithes", [
    "Gaviidae",
    ("Austrodyptornithes", [
        "Spheniscidae",
        ("Procellariiformes", [
            "Oceanitidae",
            (None, [
                "Diomedeidae",
                (None, ["Hydrobatidae", "Procellariidae"]),
            ]),
        ]),
    ]),
    (None, [
        "Ciconiidae",
        (None, [
            ("Suliformes", [
                "Fregatidae",
                (None, [
                    "Sulidae",
                    (None, ["Anhingidae", "Phalacrocoracidae"]),
                ]),
            ]),
            ("Pelecaniformes", [
                "Threskiornithidae",
                (None, [
                    "Ardeidae",
                    ("Pelecani", [
                        (None, ["Scopidae", "Balaenicipitidae"]),
                        "Pelecanidae",
                    ]),
                ]),
            ]),
        ]),
    ]),
])


# --- Telluraves: Afroaves + Australaves (Prum 2015, Kuhl 2021) --------------
AFROAVES = ("Afroaves", [
    ("Accipitrimorphae", [
        "Cathartidae",
        ("Accipitriformes", [
            "Sagittariidae",
            (None, ["Pandionidae", "Accipitridae"]),
        ]),
    ]),
    (None, [
        ("Strigiformes", ["Tytonidae", "Strigidae"]),
        ("Coraciimorphae", [
            "Coliidae",
            ("Cavitaves", [
                "Leptosomidae",
                ("Eucavitaves", [
                    "Trogonidae",
                    ("Picocoraciae", [
                        ("Bucerotiformes", [
                            ("Upupiformes", ["Upupidae", "Phoeniculidae"]),
                            "Bucerotidae",
                        ]),
                        ("Picodynastornithes", [
                            ("Coraciiformes", [
                                ("Coracii", ["Coraciidae", "Brachypteraciidae"]),
                                ("Alcedinimorphae", [
                                    "Meropidae",
                                    ("Alcedines", [
                                        "Alcedinidae",
                                        ("Todidae+Momotidae", ["Todidae", "Momotidae"]),
                                    ]),
                                ]),
                            ]),
                            ("Piciformes", [
                                ("Galbuli", ["Galbulidae", "Bucconidae"]),
                                ("Pici", [
                                    (None, ["Indicatoridae", "Picidae"]),
                                    ("Ramphastides", [
                                        "Megalaimidae",
                                        (None, [
                                            "Lybiidae",
                                            (None, [
                                                "Capitonidae",
                                                (None, ["Semnornithidae", "Ramphastidae"]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ]),
])

# --- Passeriformes ----------------------------------------------------------
# Backbone: Oliveros et al. 2019; Moyle et al. 2016.
TYRANNI = ("Tyranni", [
    ("Eurylaimides", [
        "Sapayoidae",
        (None, [
            "Pittidae",
            (None, [
                "Calyptomenidae",
                (None, ["Eurylaimidae", "Philepittidae"]),
            ]),
        ]),
    ]),
    ("Tyrannides", [
        ("Furnariida", [
            ("Thamnophilida", [
                "Thamnophilidae",
                (None, ["Melanopareiidae", "Conopophagidae"]),
            ]),
            ("Furnariida s.s.", [
                (None, ["Grallariidae", "Rhinocryptidae"]),
                (None, ["Formicariidae", "Furnariidae"]),
            ]),
        ]),
        ("Tyrannida", [
            ("Tityroidea", ["Tityridae", "Oxyruncidae", "Onychorhynchidae"]),
            (None, ["Cotingidae", "Pipridae"]),
            "Tyrannidae",
        ]),
    ]),
])

MELIPHAGIDES = ("Meliphagides", [
    "Maluridae",
    (None, [
        "Dasyornithidae",
        (None, [
            "Meliphagidae",
            ("Pardalotidae+Acanthizidae", ["Pardalotidae", "Acanthizidae"]),
        ]),
    ]),
])

# Corvides. Basal grade (Campephagidae, Mohouidae, Neosittidae, Psophodidae,
# Cinclosomatidae) then the three core superfamilies. Relationships among
# Orioloidea, Malaconotoidea and Corvoidea are not consistently recovered.
CORVIDES = ("Corvides", [
    (None, ["Campephagidae", (None, ["Mohouidae", "Neosittidae"])]),
    (None, ["Psophodidae", "Cinclosomatidae"]),
    ("Orioloidea", [
        ("Falcunculidae+", ["Eulacestomatidae", "Oreoicidae", "Falcunculidae"]),
        (None, ["Paramythiidae", "Vireonidae"]),
        (None, ["Pachycephalidae", "Oriolidae"]),
    ]),
    ("Malaconotoidea", [
        (None, ["Machaerirhynchidae", "Artamidae"]),
        "Rhagologidae",
        (None, [
            ("Vangoidea", ["Platysteiridae", "Vangidae"]),
            (None, ["Pityriasidae", (None, ["Aegithinidae", "Malaconotidae"])]),
        ]),
    ]),
    ("Corvoidea", [
        (None, ["Rhipiduridae", "Dicruridae"]),
        (None, [
            (None, ["Paradisaeidae", "Ifritidae"]),
            (None, ["Monarchidae", (None, ["Corcoracidae", "Melampittidae"])]),
        ]),
        (None, ["Platylophidae", "Laniidae", "Corvidae"]),
    ]),
])

PASSERI = ("Passeri", [
    ("Menurides", ["Menuridae", "Atrichornithidae"]),
    (None, [
        ("Climacterides", ["Ptilonorhynchidae", "Climacteridae"]),
        (None, [
            MELIPHAGIDES,
            (None, [
                ("Orthonychides", ["Orthonychidae", "Pomatostomidae"]),
                (None, [CORVIDES, "__PASSERIDES__"]),
            ]),
        ]),
    ]),
])


# --- Passerides (= Passerida sensu lato): Cai 2019, Oliveros 2019 ----------
# Sylvioidea is a rapid radiation; Alstrom 2013 recovers most of its
# superfamily-level lineages as an unresolved burst, kept here as a polytomy.
SYLVIOIDEA = ("Sylvioidea", [
    "Macrosphenidae",
    "Nicatoridae",
    (None, ["Panuridae", "Alaudidae"]),
    "Cisticolidae",
    ("Locustelloidea", [
        "Acrocephalidae",
        (None, ["Locustellidae", "Donacobiidae"]),
        (None, ["Bernieridae", "Pnoepygidae"]),
    ]),
    (None, ["Hirundinidae", "Pycnonotidae"]),
    "Hyliidae",
    "Erythrocercidae",
    ("Cettioidea", [
        "Phylloscopidae",
        (None, ["Cettiidae", "Aegithalidae"]),
    ]),
    ("Sylviida s.s.", [
        (None, ["Sylviidae", "Paradoxornithidae"]),
        "Zosteropidae",
        (None, [
            "Timaliidae",
            (None, ["Pellorneidae", "Leiothrichidae"]),
        ]),
    ]),
])

SYLVIIDA = ("Sylviida", [
    "Hyliotidae",
    ("Paroidea", [
        "Stenostiridae",
        (None, ["Paridae", "Remizidae"]),
    ]),
    SYLVIOIDEA,
])

MUSCICAPIDA = ("Muscicapida", [
    "Regulidae",
    "Elachuridae",
    ("Certhioidea", [
        (None, ["Sittidae", "Tichodromidae"]),
        (None, [
            (None, ["Certhiidae", "Salpornithidae"]),
            (None, ["Polioptilidae", "Troglodytidae"]),
        ]),
    ]),
    ("Muscicapoidea", [
        "Cinclidae",
        (None, [
            (None, ["Buphagidae", "Sturnidae"]),
            "Mimidae",
        ]),
        (None, ["Turdidae", "Muscicapidae"]),
    ]),
    ("Bombycilloidea", [
        "Mohoidae",
        "Hylocitreidae",
        "Hypocoliidae",
        "Dulidae",
        (None, ["Bombycillidae", "Ptiliogonatidae"]),
    ]),
])

# Emberizoidea (the New World nine-primaried oscines): Barker et al. 2015,
# Auk 132:333-348. The four Antillean endemic families form a grade whose
# order is not consistently recovered, so they sit in a polytomy.
EMBERIZOIDEA = ("Emberizoidea", [
    "Calcariidae",
    (None, [
        "Rhodinocichlidae",
        (None, [
            "Emberizidae",
            (None, [
                "Passerellidae",
                (None, [
                    "Calyptophilidae",
                    "Phaenicophilidae",
                    "Zeledoniidae",
                    "Teretistridae",
                    (None, [
                        (None, ["Icteridae", "Parulidae"]),
                        (None, [
                            "Mitrospingidae",
                            (None, ["Cardinalidae", "Thraupidae"]),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ]),
])

PASSERIDA = ("Passerida", [
    (None, ["Promeropidae", "Modulatricidae"]),
    ("Nectariniidae+Dicaeidae", ["Dicaeidae", "Nectariniidae"]),
    (None, ["Irenidae", "Chloropseidae"]),
    "Peucedramidae",
    "Urocynchramidae",
    "Prunellidae",
    ("Ploceoidea", [
        "Ploceidae",
        (None, ["Estrildidae", "Viduidae"]),
    ]),
    (None, ["Passeridae", "Motacillidae"]),
    (None, ["Fringillidae", EMBERIZOIDEA]),
])

PASSERIDES = ("Passerides", [
    "Melanocharitidae",
    "Cnemophilidae",
    ("Callaeoidea", ["Callaeidae", "Notiomystidae"]),
    "Petroicidae",
    ("core Passerides", [
        ("Picathartides", [
            "Picathartidae",
            (None, ["Chaetopidae", "Eupetidae"]),
        ]),
        (None, [
            SYLVIIDA,
            (None, [MUSCICAPIDA, PASSERIDA]),
        ]),
    ]),
])

PASSERIFORMES = ("Passeriformes", [
    "Acanthisittidae",
    ("Eupasseres", [TYRANNI, PASSERI]),
])

AUSTRALAVES = ("Australaves", [
    "Cariamidae",
    ("Eufalconimorphae", [
        "Falconidae",
        ("Psittacopasseres", [
            ("Psittaciformes", [
                "Strigopidae",
                (None, [
                    "Cacatuidae",
                    ("Psittacoidea", ["Psittaculidae", "Psittacidae"]),
                ]),
            ]),
            PASSERIFORMES,
        ]),
    ]),
])

TELLURAVES = ("Telluraves", [AFROAVES, AUSTRALAVES])

# Base of Neoaves: deliberately unresolved. See module docstring.
NEOAVES = ("Neoaves", [
    STRISORES,
    COLUMBAVES,
    GRUIMORPHAE,
    MIRANDORNITHES,
    PHAETHONTIMORPHAE,
    "Opisthocomidae",
    AEQUORNITHES,
    TELLURAVES,
])

TREE = ("Aves", [
    PALAEOGNATHAE,
    ("Neognathae", [GALLOANSERAE, NEOAVES]),
])
