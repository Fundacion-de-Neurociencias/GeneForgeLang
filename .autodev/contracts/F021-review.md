# F021 contract review (evaluator subagent, verbatim)

Revisión del contrato F021, ordenada por importancia. Solo he leído; no he escrito ni ejecutado nada.

**Hechos de "Why now" comprobados contra el código**
- Correcto: `core/api.py` tiene `__all__` con 10 nombres (línea 625).
- Correcto: `get_api_info()` fija `api_version` y `gfl_version` a `"0.1.0"` (líneas 586-587).
- Correcto: `pyproject.toml` y `__version__` dicen `1.0.0`.
- Correcto: el tag más reciente es `v0.2.4`. Existe además `v2025.06-initial-stable`, que el contrato no menciona.
- Correcto: `__init__.py` anuncia 4 nombres en `__all__` pero no importa nada (`try: pass`).
- Correcto: `protein_generator.py` y `simple_optimizer.py` hacen `import random`.
- Impreciso: "`errors.py`" está en `src/geneforgelang/core/errors.py`; en esa ruta están `ErrorCodes`, `ErrorSeverity` y `ErrorCategory`.
- Impreciso: "`infer()` usa un modelo heurístico/dummy". `infer(model, ast, ...)` recibe el modelo del llamante. Solo `infer_enhanced` y `compare_inference_models` importan `geneforgelang.models.dummy.DummyGeneModel` (líneas 358 y 402). Que `infer` lleve la etiqueta `simulated` depende del modelo que se le pase, y la razón tiene que decirlo.

**Problemas, de mayor a menor importancia**

1. **A1 está falsada.** `tests/conformance_suite` contiene `v1.2.0`, `v1.3.0`, `v1.4.0` y `v1.5.0`, no solo `v1.2.0`. Empezar `GRAMMAR_VERSION` en `1.2.0` contradice la propia regla del contrato. Hay que derivarla de la versión más alta de la suite (o justificar otra), y añadir un test que la ate al directorio en vez de escribirla a mano.
2. **La prueba de "simulated" de D4 no está bien definida.** `random.choices` se usa sin semilla y `execute()` no acepta parámetro de semilla, así que "dos semillas difieren" no se puede hacer por el canal público. Propuesta: dos llamadas a `execute()` con el mismo bloque `design` devuelven secuencias distintas, o bien parchear `random.seed`. Además, "assert the plugin module imports `random`" es un test de texto/estructura, no de comportamiento.
3. **El classifier del criterio 2 no cubre los constructos de gramática.** El contrato registra las claves de nivel superior por constructo, pero la tabla de reglas no dice qué tipo de cambio es quitar uno. Hay que declararlo explícitamente (quitar = breaking, añadir = additive).
   - Además, el test "muta la lista registrada, no el parser", así que solo demuestra que `compare()` funciona. No demuestra que `build_contract()` detecte un parser que pierde un constructo. Falta un test que haga monkeypatch de `parse` (o use un sample que deje de parsear) y compruebe que `--check` falla.
   - Hay que fijar qué ficheros de muestra se usan (los de `tests/conformance_suite/vX`), en lugar de "minimal sample".
4. **D3 no es reproducible tal como está escrito.** Pide que `--check-tag v1.0.0` salga con 0, pero ese tag no existe y los existentes (`v0.2.4`) no coinciden con `1.0.0`.
   - Hay que aclarar que `--check-tag` compara el nombre pasado contra los metadatos, sin exigir que el tag exista en git. Así se puede verificar sin crear tags.
   - Para el caso de desacuerdo entre pyproject y `__version__`, falta concretar cómo se inyecta el pyproject temporal: un flag `--pyproject <path>` o una función con argumento.
   - Riesgo: si F011 cambia la versión antes del merge, D3 se rompe.
5. **D2, la integración con git, es vaga.** "`--against HEAD~1` style via `git show`" debe concretarse: el CLI `--against <ref>` ejecutado con `cwd` en un repo temporal, con dos commits (snapshot original y snapshot mutado), y exit code distinto de 0 con el nombre del cambio en stdout.
   - Hay que fijar cómo se lee el changelog en `--against`: el `CHANGELOG.md` del working tree o el del ref.
6. **El criterio 3 dice "in CI" y su verificación real es un owner gate.** Está bien marcarlo así, pero hay que dejar preparado el artefacto: la rama y el texto del PR.
   - El workflow solo se valida con `yaml.safe_load`, que no comprueba la semántica de Actions. Mejor exigir `actionlint` si se puede instalar con `uv`/`pip`, o declarar ese límite en not_proved.
   - Falta definir qué pasa en `pull_request` si `origin/<base>` no tiene todavía snapshot (primer PR, porque el baseline aún no existe): el workflow debe tolerarlo de forma explícita.
7. **Evidencia sin ruta.** No se dice dónde se guardan las salidas: `.autodev/evidence/F021/checks.txt` y las salidas del CLI con sus exit codes. Hay que añadirlo para cada D.
8. **D1, el "scratch copy".** Hay que especificar el mecanismo: test con monkeypatch de la firma de `api.parse`, o una copia en un tmp con `PYTHONPATH` apuntando a ella. Editar el código real sin revertirlo ensucia el repo.
9. **D6, la línea base.** "Skipped/xfailed no higher than baseline" exige registrar la línea base en `autodev/integration` antes del cambio. Falta decirlo y decir dónde se guarda.
10. **Cosas menores.**
    - `EVIDENCE_LABELS` admite `{measured, computed, simulated, stub}`, pero las reglas de clasificación solo hablan de computed y simulated. Falta el orden total (por ejemplo, stub < simulated < computed < measured) para clasificar cualquier transición.
    - La gramática no tiene regla para un cambio MINOR o PATCH.
    - Faltan las reglas de las clases de error públicas: cuáles entran y qué es quitar una.

**Veredicto de la revisión:** casi todo es verificable por CLI y pytest. Antes de construir hay que corregir los puntos 1 a 4: A1 falsada, la prueba de `simulated` sin semilla, el classifier sin regla de constructos y la verificación del parser real, y la reproducibilidad de `--check-tag`.
