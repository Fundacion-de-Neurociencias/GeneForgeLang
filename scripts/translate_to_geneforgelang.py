import re
import sys


# Nuevas reglas de reconocimiento con patrones suaves
def traducir_a_geneforge(secuencia):
    motivos = []

    # Dom(Kin): 3 o más K seguidos al principio
    if re.search(r"^M*K{3,}", secuencia):
        motivos.append("Dom(Kin)")

    # Mot(NLS): presencia de varias R o K juntas, típica señal nuclear
    if re.search(r"[RK]{3,}", secuencia):
        motivos.append("Mot(NLS)")

    # Mot(PEST): alta densidad de E o D (glutámico o aspártico)
    if len(re.findall(r"E", secuencia)) >= 5 or "DEG" in secuencia:
        motivos.append("Mot(PEST)")

    # *AcK@X: presencia de "KQAK" o "QAK" como motivo de acetilación
    if re.search(r"KQAK|QAK", secuencia):
        motivos.append("*AcK@X")

    # *P@X: motivos de fosforilación comunes
    if re.search(r"[RST]P", secuencia):
        motivos.append("*P@X")

    # Localize(Nucleus): presencia de PRKRK, PKKKRKV
    if "PRKRK" in secuencia or "PKKKRKV" in secuencia:
        motivos.append("Localize(Nucleus)")

    # Localize(Membrane): patrones hidrofóbicos como AILFL o LAGGAV
    if re.search(r"(AILFL|LAGGAV|LVLL|AAVL)", secuencia):
        motivos.append("Localize(Membrane)")

    if not motivos:
        return "// No se encontraron motivos reconocibles"

    return "^p:" + "-".join(sorted(set(motivos)))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python traducir_a_geneforgelang_v2.py <secuencia_proteina>")
        sys.exit(1)

    secuencia = sys.argv[1].upper()
    resultado = traducir_a_geneforge(secuencia)
    print("🔍 GeneForgeLang:")
    print(resultado)
