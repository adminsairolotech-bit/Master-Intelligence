# AutoCAD Bridge Configuration
# Connects AI (Opus 4.7) to AutoCAD for Roll Forming Drawings

# ============================================
# AUTOCAD SETTINGS
# ============================================
AUTOCAD_VERSION = "AutoCAD.Application"
AUTOCAD_VISIBLE = True

# ============================================
# ROLL FORMING PROFILES
# ============================================

C_CHANNEL_SIZES = [
    {"name": "C-75", "web": 75, "flange": 35, "lip": 12, "thickness": 1.5},
    {"name": "C-100", "web": 100, "flange": 40, "lip": 15, "thickness": 1.5},
    {"name": "C-125", "web": 125, "flange": 45, "lip": 15, "thickness": 2.0},
    {"name": "C-150", "web": 150, "flange": 50, "lip": 15, "thickness": 2.0},
    {"name": "C-200", "web": 200, "flange": 65, "lip": 20, "thickness": 2.5},
    {"name": "C-250", "web": 250, "flange": 75, "lip": 20, "thickness": 3.0},
    {"name": "C-300", "web": 300, "flange": 80, "lip": 25, "thickness": 3.0},
]

Z_PURLIN_SIZES = [
    {"name": "Z-100", "web": 100, "flange": 40, "lip": 15, "thickness": 1.5},
    {"name": "Z-150", "web": 150, "flange": 50, "lip": 15, "thickness": 2.0},
    {"name": "Z-200", "web": 200, "flange": 60, "lip": 20, "thickness": 2.5},
    {"name": "Z-250", "web": 250, "flange": 65, "lip": 20, "thickness": 3.0},
    {"name": "Z-300", "web": 300, "flange": 75, "lip": 25, "thickness": 3.0},
    {"name": "Z-350", "web": 350, "flange": 75, "lip": 25, "thickness": 3.0},
]

# ============================================
# SHAFT SPECIFICATIONS
# ============================================

SHAFT_SIZES = {
    "C-75 to C-100": {"diameter": 40, "length": 250, "material": "EN8"},
    "C-100 to C-150": {"diameter": 50, "length": 350, "material": "EN8"},
    "C-150 to C-200": {"diameter": 60, "length": 400, "material": "EN9"},
    "C-200 to C-300": {"diameter": 75, "length": 500, "material": "EN24"},
    "Z-200 to Z-400": {"diameter": 80, "length": 550, "material": "EN24"},
}

BEARING_SIZES = {
    40: {"model": "6308", "bore": 40, "od": 90, "width": 23},
    50: {"model": "6310", "bore": 50, "od": 110, "width": 27},
    60: {"model": "6312", "bore": 60, "od": 130, "width": 31},
    75: {"model": "6315", "bore": 75, "od": 160, "width": 37},
    80: {"model": "6316", "bore": 80, "od": 170, "width": 39},
}

# ============================================
# LAYER SETTINGS
# ============================================

LAYERS = {
    "PROFILE": {"color": 1, "description": "Roll Forming Profile"},
    "FLOWER": {"color": 4, "description": "Flower Pattern (Pass Sequence)"},
    "ROLLS": {"color": 5, "description": "Roll Assembly"},
    "SHAFT": {"color": 2, "description": "Shaft and Keyway"},
    "BEARING": {"color": 3, "description": "Bearing Details"},
    "CENTER": {"color": 1, "description": "Center Lines"},
    "DIM": {"color": 3, "description": "Dimensions"},
    "TEXT": {"color": 1, "description": "Text and Labels"},
    "KEYWAY": {"color": 6, "description": "Keyway Details"},
    "TITLE": {"color": 2, "description": "Title Block"},
}

# ============================================
# STANDARD DIMENSIONS
# ============================================

ROLL_DIAMETERS = {
    "small": 120,    # For light profiles
    "medium": 160,   # For standard profiles
    "large": 200,    # For heavy profiles
    "xlarge": 250,   # For extra heavy
}

# Scale for drawing (1 unit = 1mm in AutoCAD)
DRAWING_SCALE = 1.0

# ============================================
# FILLET AND CHAMFER RADII
# ============================================

STANDARD_FILLETS = {
    "light": 1.5,    # For thin material
    "medium": 2.0,   # For standard
    "heavy": 3.0,    # For thick material
}

# ============================================
# MATERIAL PROPERTIES
# ============================================

MATERIALS = {
    "GI": {"yield": 250, "springback": 3, "color": "Galvanized"},
    "MS": {"yield": 350, "springback": 4, "color": " Mild Steel"},
    "SS304": {"yield": 500, "springback": 7, "color": "Stainless Steel"},
    "SS316": {"yield": 550, "springback": 7, "color": "Stainless Steel 316"},
    "Aluminum": {"yield": 150, "springback": 2, "color": "Aluminum"},
}
