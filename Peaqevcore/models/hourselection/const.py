NON_HOUR = "Charging stopped"
CAUTION_HOUR = "Charging-permittance degraded"
CHARGING_PERMITTED = "Charging permitted"
# moved to core

CAUTIONHOURTYPE_SUAVE = "Suave"
CAUTIONHOURTYPE_INTERMEDIATE = "Intermediate"
CAUTIONHOURTYPE_AGGRESSIVE = "Aggressive"

CAUTIONHOURTYPE = {
    CAUTIONHOURTYPE_SUAVE: 0.75,
    CAUTIONHOURTYPE_INTERMEDIATE: 0.5,
    CAUTIONHOURTYPE_AGGRESSIVE: 0.4
}

CAUTIONHOURTYPE_NAMES =[
    CAUTIONHOURTYPE_SUAVE,
    CAUTIONHOURTYPE_INTERMEDIATE,
    CAUTIONHOURTYPE_AGGRESSIVE
]