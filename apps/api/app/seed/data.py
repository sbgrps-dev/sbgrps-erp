"""Seed data taken from 'STOCK REQUIREMENT-TPJ,MDU,MS PFTR, MS OFFICE-NOV-26.xlsx'.

HSN codes are blank in the source file; fill them in from the Products screen.
"""

from decimal import Decimal as D

SITES = [
    # code, display name, sort order
    ("TPJ_BIO", "TPJ BIO", 10),
    ("MDU_BIO", "MDU BIO", 20),
    ("MSPFTR_PT", "MS PFTR & PT", 30),
    ("MS_OFFICE", "MS OFFICE", 40),
    ("TPJ_FORT", "TPJ FORT", 50),
    ("JTJ_KPD", "JTJ & KPD", 60),
    ("SRR", "SRR", 70),
]

VENDORS = [
    {
        "name": "Muthu Enterprises",
        "address": "No.26, E.H Road\nVyasarpadi\nChennai - 600039",
        "gstin": "33BXZPM3047C1ZC",
        "emails": ["jashwenth@gmail.com"],
        "phones": ["+91 98411 40557", "+91 98413 93557"],
        "products_supplied": "Tools",
    },
    {
        "name": "Transchem",
        "address": "D-18, Industrial Estate\nMogappair West\nChennai - 600037",
        "gstin": "33AMEPL5035A1ZP",
        "emails": ["sales@transchem-in.com"],
        "phones": ["+91 89390 79075"],
        "website": "www.transchem-in.com",
        "products_supplied": (
            "Type - 1\nKitchen Degreaser\nAromatic Disinfectant Spray\nSanitary care"
        ),
    },
    {
        "name": "Nathan Industries",
        "emails": ["nathanindustries1997@gmail.com", "hariprakashco@gmail.com"],
        "phones": ["+91 94440 60114"],
        "products_supplied": "Phenyl",
    },
    {
        "name": "Nova Products",
        "address": "No.46, Sidco Industrial Estate\nValavanthan Kottai, Thuvakudi\nThiruchirapalli",
        "gstin": "33FKQPP0323A1ZJ",
        "emails": ["novaenterprises5194@gmail.com"],
        "phones": ["+91 97913 85794"],
        "products_supplied": "Type - 1 (red)",
    },
    {
        "name": "Supernova Products",
        "address": "2/59, Gangai Sathakulam V.P\nSithan nagar, Vedarapuliangulam\nMadurai - 625006",
        "emails": ["sales@supernovachemicals.com"],
        "phones": ["+91 89400 04539", "+91 98207 98762"],
        "website": "www.supernovachemicals.com",
        "products_supplied": "Liquid Soap",
    },
    {
        "name": "Hariprakash Company",
        "address": "New no: 24 / Old no: 83, Millers Road\nGround floor, Kilpauk\nChennai - 600010",
        "gstin": "33AAAPL1664R1ZG",
        "emails": ["hariprakashco@gmail.com"],
        "website": "www.hariprakashcompany.in",
        "products_supplied": "Multipurpose Liquid\nSodium Hypochlorite",
    },
    {
        "name": "HNR Corporate Solutions",
        "address": (
            "796/5, 12th A main 76th cross, 6th block\nAdjacent to Rajaji Nagar estate\n"
            "Rajaji Nagar, Bangalore - 560010"
        ),
        "gstin": "29ABCPW0753B1ZR",
        "emails": ["hnrcorps@gmail.com"],
        "phones": ["044-23158993", "+91 98805 98993"],
        "drug_licence": "KA-B11-190757/190758",
    },
    {
        "name": "Adhithya Business Solution",
        "gstin": "33AAWFA6483D1Z8",
        "emails": ["adhithyabusinesssolution@gmail.com"],
        "phones": ["044-48566336", "+91 99401 50505"],
        "products_supplied": "Polythene Bags",
    },
    {
        "name": "DVR Medical Systems",
        "address": (
            "No. 97-B, Rajendran Street, IInd Floor\nThiru Nagar, Valasaravakkam\nChennai - 600087"
        ),
        "gstin": "33ABUPV3477H1ZY",
        "emails": ["dvrmedicalsystems@gmail.com"],
        "phones": ["044-24862070", "+91 89393 11000", "+91 96774 66611"],
        "products_supplied": "Hand Gloves",
    },
    {
        "name": "Ethamozhy Coir Cluster Pvt Ltd",
        "address": "5-137C, Elluvillai\nRajakkamangalam\nKanyakumari - 629502",
        "gstin": "33AAECE3220F2ZA",
        "emails": ["info@ethamozhycoirs.in"],
        "products_supplied": "Palmera Railway Banister\nIndoor coir Brooms",
    },
    {
        "name": "Professional Care",
        "address": "4/1, Thirumangalam Road\nVillivakkam\nChennai - 600049",
        "gstin": "33AQBPS7991M2Z2",
        "emails": ["proffesionalcare696@gmail.com"],
        "phones": ["044-26187178", "044-26187111", "+91 98410 386853"],
        "products_supplied": "Swipol",
    },
    {
        "name": "R.M Fabrics",
        "address": "W/23, 13th Street, Anna nagar west extn.\nAnna Nagar\nChennai - 600101",
        "gstin": "33AAJPM5823GIZS",
        "emails": ["rm.fabrics@ymail.com"],
        "phones": ["044-26153254", "+91 98400 24179", "+91 98401 56836"],
        "products_supplied": "Uniform",
    },
    {
        "name": "Hygiene Tissue Paper Technologies",
        "address": "Vinayagar koil street, Sivaprakasam Nagar\nSurapet\nChennai - 600066",
        "gstin": "33AMJPJ6717E2Z6",
        "emails": ["htptok@gmail.com"],
        "phones": ["+91 63820 40034"],
        "products_supplied": "Toilet tissue",
    },
    {
        "name": "Gorana Ventures",
        "gstin": "27BOAPG8976E2ZP",
        "emails": ["Goranaventures@gmail.com"],
    },
]

MUTHU = "Muthu Enterprises"
HNR = "HNR Corporate Solutions"
TRANSCHEM = "Transchem"

# code, name, aliases, unit, gst %, [(vendor, price, preferred)]
PRODUCTS = [
    (
        "SCRUB-PAD",
        "Steel Scrubber Pad (round)",
        ["steel scrubber"],
        "Nos",
        18,
        [(MUTHU, D("6.20"), True)],
    ),
    ("FACE-MASK", "Face Mask", [], "Nos", 18, [(MUTHU, D("1.25"), True)]),
    (
        "GLOVE-YEL-LONG",
        "Hand Gloves Yellow (long size)",
        [],
        "Set",
        18,
        [(MUTHU, D("90.00"), True)],
    ),
    ("GLOVE-YEL", "Hand Gloves Yellow", [], "Pair", 18, [(MUTHU, D("25.00"), True)]),
    ("BRUSH-WOOD", "Wooden Hand Brush", [], "Nos", 18, [(MUTHU, D("68.00"), True)]),
    (
        "GLOVE-SURG",
        "Surgical Hand Gloves",
        ["Surgical Gloves"],
        "Box",
        18,
        [(MUTHU, D("250.00"), True)],
    ),
    ("APC-F", "APC-F (original)", ["APC F", "APCF"], "Litres", 18, [(HNR, D("75.68"), True)]),
    (
        "STERIX-A",
        "Sterix-A Super",
        ["STERIX A SUPER", "STERIX SUPER", "Sterix"],
        "Litres",
        18,
        [(HNR, D("100.60"), True), (TRANSCHEM, D("30.00"), False)],
    ),
    ("KLEAN-SHINE", "Klean & Shine", ["Klean and Shine"], "Litres", 18, [(HNR, D("103.54"), True)]),
    ("FRESHEX", "Freshex", [], "Litres", 18, [(HNR, D("89.61"), True)]),
    (
        "APC-F-T1",
        "APC-F (Type 1 Blue)",
        ["Type 1 Blue", "Type - 1"],
        "Litres",
        18,
        [(TRANSCHEM, D("17.00"), True)],
    ),
    ("NIMYLE-5L", "Nimyle (5 Litres can)", ["Nimyle"], "Cans", 18, [(MUTHU, D("610.00"), True)]),
    ("SPONGE-DUSTER", "Sponge Duster", [], "Pcs", 18, [(MUTHU, D("18.00"), True)]),
    (
        "GARBAGE-BAG-24X48",
        "Garbage Bag (24x48)",
        ["Garbage Bag 24'48", "Garbage cover"],
        "Kg",
        18,
        [(MUTHU, D("80.00"), True)],
    ),
    (
        "COCO-BROOM",
        "Co-Co Brooms",
        ["Coco broom", "Coconut broom"],
        "Nos",
        5,
        [(MUTHU, D("30.00"), True)],
    ),
    ("COTTON-CLOTH", "Cotton Cloth", [], "Dozen", 5, [(MUTHU, D("95.00"), True)]),
    ("ODONIL", "Odonil Cake", ["Odonil"], "Nos", 18, [(MUTHU, D("30.00"), True)]),
    ("ROOM-FRESH", "Room Freshener", ["Room freshner"], "Nos", 18, [(MUTHU, D("80.00"), True)]),
    (
        "URINAL-CUBES",
        "Urinal Cubes (6 pcs)",
        ["Urinal cube"],
        "Packet",
        18,
        [(MUTHU, D("50.00"), True)],
    ),
    (
        "JRT-SCENT-500",
        "JRT Scent 500 ML",
        ["JRT Scent"],
        "Bottle",
        18,
        [(MUTHU, D("475.00"), True)],
    ),
]
