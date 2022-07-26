from .countries.default import Default
from .countries.belgium import VregBelgium
from .countries.sweden import SE_Bjerke_Energi, SE_FalbygdensEnergi, SE_Gothenburg, SE_Karlstad, SE_Kristinehamn, SE_Linde_Energi, SE_Malarenergi, SE_Malung_Salen, SE_Nacka_normal, SE_NACKA_timediff, SE_Partille, SE_SHE_AB, SE_Skovde, SE_Sollentuna
from .countries.norway import NO_AgderEnergi, NO_Elvia, NO_GlitreEnergi, NO_LNett, NO_Lede, NO_Tensio, NO_BKK


"""LOCALETYPES"""
LOCALE_SE_GOTHENBURG = "Gothenburg, Sweden"
LOCALE_SE_KARLSTAD = "Karlstad, Sweden"
LOCALE_SE_KRISTINEHAMN = "Kristinehamn, Sweden"
LOCALE_SE_NACKA_NORMAL = "Nacka, Sweden (Normal tariffe)"
#LOCALE_SE_NACKA_TIMEDIFF = "Nacka, Sweden (Time differentiated tariffe)"
LOCALE_SE_PARTILLE = "Partille, Sweden"
LOCALE_DEFAULT = "Other, just want to test"
LOCALE_SE_SALA = "Sala-Heby Energi AB, Sweden"
LOCALE_SE_MALUNG_SALEN = "Malung-Sälen, Sweden (Malungs elverk)"
LOCALE_SE_SKOVDE = "Skövde, Sweden"
LOCALE_SE_SOLLENTUNA = "Sollentuna Energi, Sweden"
LOCALE_BE_VREG = "Belgium (VREG)"
LOCALE_SE_BJERKE_ENERGI = "Bjärke Energi, Sweden"
LOCALE_NO_GLITRE_ENERGI = "Glitre Energi, Norway"
LOCALE_NO_AGDER_ENERGI = "Agder Energi, Norway"
LOCALE_NO_LNETT = "LNett, Norway"
LOCALE_NO_TENSIO = "Tensio, Norway"
LOCALE_SE_LINDE_ENERGI = "Linde Energi, Sweden"
LOCALE_SE_FALBYDGENS_ENERGI = "Falbygdens Energi, Sweden"
LOCALE_NO_ELVIA = "Elvia, Norway"
LOCALE_NO_LEDE = "Lede, Norway"
LOCALE_NO_BKK = "BKK, Norway"
LOCALE_SE_MALARENERGI = "Mälarenergi, Sweden"

LOCALETYPEDICT = {
    LOCALE_DEFAULT: Default,
    LOCALE_SE_GOTHENBURG: SE_Gothenburg,
    LOCALE_SE_PARTILLE: SE_Partille,
    LOCALE_SE_KARLSTAD: SE_Karlstad,
    LOCALE_SE_KRISTINEHAMN: SE_Kristinehamn,
    LOCALE_SE_NACKA_NORMAL: SE_Nacka_normal,
    LOCALE_SE_MALUNG_SALEN: SE_Malung_Salen,
    LOCALE_SE_SALA: SE_SHE_AB,
    LOCALE_SE_SKOVDE: SE_Skovde,
    LOCALE_SE_SOLLENTUNA: SE_Sollentuna,
    LOCALE_BE_VREG: VregBelgium,
    LOCALE_SE_BJERKE_ENERGI: SE_Bjerke_Energi,
    LOCALE_NO_GLITRE_ENERGI: NO_GlitreEnergi,
    LOCALE_NO_AGDER_ENERGI: NO_AgderEnergi,
    LOCALE_NO_LNETT: NO_LNett,
    LOCALE_NO_TENSIO: NO_Tensio,
    LOCALE_SE_LINDE_ENERGI: SE_Linde_Energi,
    LOCALE_SE_FALBYDGENS_ENERGI: SE_FalbygdensEnergi,
    LOCALE_NO_ELVIA: NO_Elvia,
    LOCALE_NO_LEDE: NO_Lede,
    LOCALE_NO_BKK: NO_BKK,
    LOCALE_SE_MALARENERGI: SE_Malarenergi
}

"""Lookup locales for config flow"""
LOCALES = [
    LOCALE_BE_VREG,
    LOCALE_NO_AGDER_ENERGI,
    LOCALE_NO_BKK,
    LOCALE_NO_ELVIA,
    LOCALE_NO_GLITRE_ENERGI,
    LOCALE_NO_LEDE,
    LOCALE_NO_LNETT,
    LOCALE_NO_TENSIO,
    LOCALE_SE_BJERKE_ENERGI,
    LOCALE_SE_FALBYDGENS_ENERGI,
    LOCALE_SE_KRISTINEHAMN,
    LOCALE_SE_LINDE_ENERGI,
    LOCALE_SE_MALUNG_SALEN,
    LOCALE_SE_MALARENERGI,
    LOCALE_SE_NACKA_NORMAL,
    LOCALE_SE_PARTILLE,
    LOCALE_SE_SALA,
    LOCALE_SE_SKOVDE,
    LOCALE_SE_SOLLENTUNA,
    LOCALE_DEFAULT
    ]

class LocaleBase:
    pass
