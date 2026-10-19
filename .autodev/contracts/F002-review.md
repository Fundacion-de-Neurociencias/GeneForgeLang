# Evaluator review of the F002 contract (2026-10-19, verbatim)

Reviewed at HEAD 0a7a97b by the `autodev:evaluator` subagent, contract only.

---

Revisión del contrato F002 (`C:\Users\usuario\.autodev\workspaces\geneforgelang\.autodev\contracts\F002.md`). Solo he revisado el contrato; no hay implementación que verificar. No he escrito ningún archivo. Los comandos y búsquedas los he ejecutado en HEAD 0a7a97b.

**Veredicto:** el contrato se puede verificar por CLI en casi todo, pero D3, D6 y D7 no se pueden cumplir tal como están escritos o se cumplen en vacío. Además, varias de las afirmaciones del inventario que el contrato dice cubrir no están en la denylist. Conviene corregirlo antes de construir.

**Lo que comprobé y se sostiene:**
- **A1 se cumple.** `geneforgelang.core.api.parse/validate` funcionan bajo pytest con el venv y devuelven un dict y `[]`.
- **SECURITY.md no existe en main.**
- **CHANGELOG no tiene "100% passing" ni "Mythos".**
- **C6 ("5-Model Consensus") no aparece en el README de main.**

**Observaciones**

1. **D6 no se puede cumplir.** El contrato pide que `git grep "10.1101/2024.08.31"` salga vacío en todo el repositorio. Pero `.autodev/` está versionado en esta rama, y la cadena aparece en `.autodev/features.json:41`, `.autodev/brief.md:34` y `.autodev/spec/claims-inventory.md:20`. El builder tiene prohibido tocar `features.json`, y el hook lo bloquea.
   - *Corrección:* `git grep -n "10.1101/2024.08.31" -- ':!.autodev'`, y lo mismo en la línea correspondiente de "Verification channel".

2. **D3 no comprueba nada en `whitepaper.md`.** El whitepaper no tiene ningún bloque de código cercado (`grep '```' whitepaper.md` no devuelve nada). La sintaxis no implementada aparece como código inline en las líneas 21, 26, 28 y 33, y en la tabla de las líneas 74-81 (por ejemplo "Temporal representation ✅ TIME(x)").
   - Así, el criterio de aceptación 3 de la feature ("checked by running the parser over every fenced GFL block") y la etiqueta "Proposed, not implemented" de D4 no los hace cumplir ningún test.
   - *Corrección:* añadir a D4 una aserción en el test que exija la etiqueta "Proposed, not implemented" en cada sección o fila que contenga `~d`, `:r`, `TIME(`, `PATHWAY`, `EDIT(`, SBOL, GenBank o ProForma. Incluir también la fila "Temporal representation" de la tabla comparativa.

3. **D3 se puede esquivar en el README.**
   - Basta con etiquetar los bloques como `text` o `bash` para que el parser no los revise.
   - Los ejemplos GFL del README van dentro de strings de bloques `python` (líneas 113 y siguientes, `workflow = """design: ..."""`), y esos bloques quedan fuera.
   - Además, esos mismos bloques empiezan con `from geneforgelang import parse`, que falla.
   - *Corrección:*
     - Exigir que todo bloque cuyo contenido cargue como YAML con claves GFL de primer nivel (`design`, `optimize`, `experiment`, `analyze`, …) se etiquete `gfl` o `yaml`.
     - Extraer los literales `"""..."""` de los bloques `python` y pasarlos también por parse/validate.
     - Marcar los bloques `python` que usan la importación rota como "does not run yet (F010)".

4. **D7 choca con el árbol actual y con D5. Falta definir qué frases se aplican a qué archivos y cómo funciona la exención por etiqueta.**
   - La denylist de D1 aplicada a `docs/**/*.md` falla en `docs/geneforgelang/features/design_block.md:5` ("revolutionary"), que está fuera del alcance de F002.
   - D5 conserva las puntuaciones en el manuscrito bajo un banner. Pero el manuscrito y `GFL_GENESIS_FINAL_REPORT.md:63` contienen "89.7%" y "84.8%", que están en la denylist.
   - El paso de la feature dice "without the simulation label", y el contrato no define esa exención.
   - *Corrección:*
     - Una tabla en el contrato con columnas frase → archivos donde se aplica.
     - Regla explícita: las cifras están permitidas solo en archivos o secciones con el banner "illustrative simulation" o "np.random.beta".
     - Decidir si las frases se buscan sin distinguir mayúsculas y declararlo.

5. **La denylist de D7 deja fuera afirmaciones del inventario y de la feature.**
   - **C4:** el H1 "GeneForgeLang v2.0 Beta" y las líneas 9 y 13 del README no están cubiertas; solo lo está "version-2.0.0". Añadir "v2.0 Beta" y "v2.0" al README, o justificar que se mantengan hasta F011.
   - **C7:** "Automatic generation of Reproducibility Packages" (README:43). El inventario dice "keep only if a test proves it", y D1 no lo menciona.
   - **C13:** el contrato solo cubre "Anthropic OSS Scanner". Le falta "enforced on all pull requests", que el paso de la feature incluye.
   - **C8/C1:** los números simulados que quedan en el README ("24 seconds", "<30% off-target", ">80% on-target") deben quedar bajo el encabezado de simulación. Añadirlo a D1 como aserción: el test debe exigir que ninguna cifra del bloque BRCA1 aparezca fuera de la sección "Illustrative simulation".
   - **`examples/real_project/README.md:12`** dice "Evaluate on-target efficiency using machine learning models", y son extracciones de `np.random.beta`. Incluirlo en D5.

6. **El banner del Scope debe ser obligatorio.** El Scope dice "same banner if they repeat the scores" para `GFL_GENESIS_FINAL_REPORT.md`. Las repite (líneas 63, 90, 142 y 158).
   - *Corrección:* incluirlo en D5 de forma explícita.

7. **El smoke run de D5 está poco especificado.**
   - `execute_genesis_real.py` escribe en las rutas relativas `results/...` (líneas 131, 180 y 185). Si se ejecuta desde el repositorio, sobrescribe resultados versionados.
   - No usa semilla.
   - *Corrección:*
     - Copiar el script a un directorio temporal y lanzarlo con cwd allí y `MPLBACKEND=Agg`.
     - Comprobar con `git status --porcelain examples/real_project/results` que no cambió nada.
     - Comprobar con `git diff -- execute_genesis_real.py` que solo cambiaron docstrings, comentarios y strings de print. Por ejemplo, con un diff sobre el AST sin docstrings.

8. **D8 es débil: basta con que falle cualquier test.** Cualquier fallo en origin/main lo satisface; por ejemplo, solo el aviso de D2.
   - *Corrección:* exigir que en origin/main fallen al menos tres familias, cada una con su ID de test parametrizado en la salida:
     - la denylist (README: "has been validated", PyPI badge);
     - el aviso (D2);
     - las etiquetas de los bloques cercados (D3).
   - Y guardar ambas salidas.

9. **D10 restringe el criterio de aceptación 1 de la feature.** La feature dice: "Every row … has status 'fixed' with the PR diff hunk". El contrato deja C15-C20 en `open`, C11-C13 como `prevented`, y usa el hash del commit en lugar del hunk.
   - **Justificación:** sí está justificado en el fondo. C15-C20 pertenecen a F011, F008, F004, F006 y F009 según el propio inventario, y C11-C13 no existen en main. Pero contradice literalmente el criterio de aceptación.
   - *Corrección:* registrar la restricción como desviación explícita para que la confirme el owner o el planificador (el builder no puede editar `features.json`). En C1-C10 y C14, poner como evidencia el hunk (archivo:líneas antes/después) además del hash.

10. **D6/A2 restringe el criterio "after the owner confirms the Zenodo DOI".** El contrato sustituye la confirmación del owner por los metadatos de la API de Zenodo.
    - **Justificación:** es razonable, porque el creador es "Fundación de Neurociencias" y el título coincide. Pero no es una confirmación del owner.
    - *Corrección:* dejar el DOI en `CITATION.cff`, listarlo en la descripción del PR como "pending owner confirmation (A2)", y que el evaluador lo clasifique como claim no confirmado por el owner.

11. **D1 pasa por alto un enlace roto en una línea que este sprint va a editar.** README:88 enlaza a `examples/gfl-genesis/Manuscript_GeneForge_v2_Beta.md`, que no existe; el archivo real está en `examples/real_project/`. Está dentro de la sección BRCA1 que se reescribe.
    - *Corrección:* añadir a D1 "the manuscript link resolves", y que el test verifique los enlaces relativos de README.md.

12. **El texto de D1 sobre la insignia de versión no coincide con lo que pide la feature.**
    - La feature dice "replace the version badge with the single version from pyproject".
    - El inventario dice "no version badge until F011".
    - El contrato solo prohíbe "version-2.0.0".
    - *Corrección:* elegir una opción y hacerla verificable. Lo recomendable es no poner insignia de versión, con una aserción `not re.search(r"img.shields.io/badge/version", readme)`.

13. **Error menor en la redacción del Scope.** "`CHANGELOG.md` content other than nothing on main needs it" no tiene sentido.
    - *Corrección:* "Does not change `CHANGELOG.md` (no C11/C12 text on main; guarded by D7)".

14. **D2 y D9 están bien.** D11 está bien acotado: comprobar que no se ha hecho push ni merge a main.
    - Falta un detalle en D9: `pytest.ini` tiene `--strict-config` y `asyncio_mode`, así que el comando de D8 en el worktree temporal debe usar el mismo `.venv` con ruta absoluta y `-p no:cacheprovider`. Si no, se rompe la configuración o el fallo no se debe a la denylist.
    - *Corrección:* escribir en D8 el comando exacto, con `--python <repo>/.venv`, y añadir `git worktree remove --force` al final.
