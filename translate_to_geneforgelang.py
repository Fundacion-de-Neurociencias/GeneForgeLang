import sys

# Reglas de reconocimiento simbólico
reglas = [
    ("KKK", "Dom(Kin)"),
    ("MKKK", "Dom(Kin)"),
    ("MAKK", "Dom(Kin)"),
    ("MEKK", "Dom(Kin)"),
    ("PRKR", "Mot(NLS)"),
    ("PRKRK", "Mot(NLS)"),
    ("PKKKRKV", "Mot(NLS)"),
    ("PEST", "Mot(PEST)"),
    ("DEGEDE", "Mot(PEST)"),
    ("EEEEE", "Mot(PEST)"),
    ("KQAK", "*AcK@X"),
    ("AcK", "*AcK@X"),
    ("RP", "*P@X"),
    ("SP", "*P@X"),
    ("TP", "*P@X"),
    ("PRKRK", "Localize(Nucleus)"),
    ("AILFL", "Localize(Membrane)"),
    ("LAGGAV", "Localize(Membrane)")
]

def traducir_a_geneforge(secuencia):
    frase = set()
    for patron, traduccion in reglas:
        if patron in secuencia:
            frase.add(traduccion)
    if not frase:
        return "// No se encontraron motivos reconocibles"
    return "^p:" + "-".join(sorted(frase))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python traducir_a_geneforgelang.py <secuencia_proteina>")
        sys.exit(1)

    secuencia = sys.argv[1].upper()
    resultado = traducir_a_geneforge(secuencia)
    print("🔍 GeneForgeLang:")
    print(resultado)