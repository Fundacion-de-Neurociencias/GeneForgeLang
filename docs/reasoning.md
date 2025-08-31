`gfl
vector(AAV9,serotype=9,tropism=retina,payload_kb=4.7)
target(tissue:retina)
repeat_edit(CAG,interruption:CAA)
risk(off_target:0.2)
governance(value:transparency)
`
"@ | Out-File -Encoding UTF8 -Append "C:\Users\usuario\GeneForge\GeneForgeLang\gfl\syntax.md"

if (!(Test-Path "C:\Users\usuario\GeneForge\GeneForgeLang\docs")) { New-Item "C:\Users\usuario\GeneForge\GeneForgeLang\docs" -ItemType Directory }
@"
# Probabilistic reasoning layer

| Regla | LR | Descripción |
|-------|----|-------------|
| ector_tropism_match | **3.0** | Tropismo de vector coincide con tejido |
| epeat_interruption  | **4.0** | Interrupción de tripletes patogénicos |
|
on_equity_governance| **0.5** | Falta valor ético clave |
| high_offtarget       | **0.4** | Riesgo off‑target > 0.6 |
