# F004 contract review (evaluator, verbatim)

Revisión del contrato F004. Solo leí archivos; no escribí nada en el repo.

Resumen: el contrato todavía no está listo. Hay que corregir los puntos BLOCKING antes de construir. Los más graves son tres. Primero, se rompen tests que el contrato no prevé tocar. Segundo, la lista de excepciones del oráculo AST no coincide con lo que el escaneo encuentra de verdad. Tercero, hay cuatro ítems de "Done means" (2, 5, 7 y 8) con una redacción que no se puede comprobar tal cual.

1. **BLOCKING: tests existentes que fallarán por el `allow_simulated=False` por defecto.**
   - `tests/contract/test_public_contract.py:400-401` (`test_simulated_label_on_execute_matches_the_behaviour`) llama a `api.execute(ast, registry)` con `ProteinVAEGenerator`. Con la refusal por defecto lanzará `SimulatedInputError`.
   - `tests/test_basic_plugin_functionality.py:80` llama a `execute(ast, registry)` con un plugin builtin y también fallará.
   - `tests/test_basic_functionality.py:92` y `tests/test_workflow.py:49` capturan la excepción y no fallarán. Pero quedarán vacíos en silencio: el contrato debería decir que se actualizan, o que se acepta que ya no ejercitan la ejecución.
   - El apartado "Tests:" del Scope no menciona ninguno de estos archivos. El ítem 9 ("0 failures") es incompatible con el Scope tal como está escrito. Hay que listarlos y decir qué cambia: pasar `allow_simulated=True` y afirmar `provenance.kind=='simulated'`.

2. **BLOCKING: la lista de excepciones del ítem 4 no está bien definida y no coincide con el código.** Busqué con grep qué módulos de `src/geneforgelang` importan `random` o `hashlib`.
   - Encontré: `core/parser.py`, `core/performance.py`, `core/enhanced_inference_engine.py`, `governance/behavioral/semantic_hash.py`, `ir/fase4/cache_layer.py`, `ir/fase4/async_retrieval.py` (que usa `hashlib.md5` como clave de caché, línea 182), `plugins/plugin_registry.py`, `ir/external/openmed_connector.py` (md5, línea 100), los dos builtin y `utils/example_implementations.py`.
   - El contrato solo nombra "parser, cache keys, semantic hash". No dice nada de `async_retrieval`, que es md5 y además se importa dentro de una función, ni de `enhanced_inference_engine`.
   - Hay que fijar la lista como un conjunto exacto de rutas de módulo, cada una con su motivo, y decir que el test compara igualdad de conjuntos (para que una excepción que sobra también falle).
   - También hay que definir la detección con precisión:
     - imports dentro de funciones (los hay);
     - `import numpy as np` + `np.random.*`, que es acceso a atributo y no un import;
     - `hashlib.md5` frente a `hashlib.sha256`. La sha256 se usa en performance, plugin_registry y enhanced_inference_engine. Hay que decir si cuenta como "hash-derived" o no. El texto dice "hashlib.md5", pero la feature habla de salida derivada de hash en general.

3. **BLOCKING: el ítem 2 es incoherente.**
   - Dice "nine components", pero enumera unos 14. Hay que dar la cuenta y la lista exactas, iguales a las filas de `components.md`.
   - "the result's `provenance.kind`" es ambiguo. Para OpenMed el contrato usa `result["provenance"]["kind"]` (es un dict); para los plugins usa el atributo `.provenance` de `ProvenancedDict/List`. Hay que fijar el acceso para cada componente.
   - `reset_first_use_warnings()` se usa en el ítem 2 pero no aparece en la API del módulo listada en Scope. Hay que añadirla a la lista pública, porque afecta al snapshot del contrato público.
   - Hay que aclarar si "exactly one warning on first use in a process" es por componente o por clase. En OpenMed, ¿es un warning por método o uno por connector?

4. **BLOCKING: el ítem 5 tiene partes que no se pueden comprobar.**
   - No dice cómo se detecta que "a workflow input is simulated". El AST que recibe `execute` es un dict plano, y `require_real_inputs` necesita saber dónde mirar (¿valores `ProvenancedDict` dentro del AST?). Hay que especificarlo.
   - "the result's `provenance.kind`" para `execute`, que devuelve `dict[str, Any]`: ¿lo lleva el dict de nivel superior (`ProvenancedDict`) o cada bloque?
   - No existe ningún plugin "labelled-clean" en el repo. Hay que decir que el test define uno mínimo con `Provenance("computed", ...)`. Y "no provenance claim added" hay que convertirlo en una aserción concreta: `provenance_of(result) is None`, o `kind=='computed'` heredado.

5. **BLOCKING: el ítem 8 está mal redactado y se contradice con el código.**
   - La frase "A test imports it with matplotlib stubbed out only if the import needs it is not allowed" no se puede interpretar.
   - `examples/real_project/execute_genesis_real.py` importa `matplotlib.pyplot`, `numpy` y `pandas` en la cabecera (líneas 19-21). Importar el módulo exige matplotlib, aunque `simulate_geneforge_engine` no lo use.
   - Propuesta de redacción: "El test hace `pytest.importorskip('matplotlib')`, `('pandas')` y `('numpy')`, carga el script con `importlib.util.spec_from_file_location` (`examples/` no es un paquete), parchea `time.sleep` con monkeypatch, llama a `simulate_geneforge_engine()` y afirma que `json.dumps(result)` funciona, que `result['provenance']['kind']=='simulated'` (o el atributo, según se fije en el punto 3) y que salta un `SimulatedComponentWarning`."
   - También hay que fijar el backend de matplotlib (`MPLBACKEND=Agg`) por si el import abre una ventana en Windows.

6. **BLOCKING: el ítem 7 usa `--against HEAD`.** Después de hacer commit, HEAD ya incluye el cambio, así que la comparación contra HEAD es vacía y siempre pasa. Hay que usar `--against autodev/integration`, o el merge-base. La opción `--against REF` sí existe (`public_contract.py:518`).

7. **ADVISORY: cobertura de la acceptance de features.json.**
   - "documented in the public API reference" está en Scope (`API_CONTRACT.md`), pero ningún ítem de "Done means" lo comprueba. Habría que añadir una comprobación con grep o con un test de docs: la sección existe y nombra `Provenance`, `allow_simulated` y `SimulatedInputError`.
   - "Replacement recorded as future work only": el ítem 3 comprueba los nombres, pero no la columna de oráculo ni el estado. Habría que exigir que cada fila tenga un estado en {simulated, stub, dead} (ninguna "real") y un oráculo que no esté vacío.

8. **ADVISORY: el ítem 6 (grep) es más estrecho que la acceptance.**
   - La acceptance prohíbe claves "named like a guarantee" (`'validated'`, `'calibrated'`) salvo que haya un check real detrás. El contrato solo busca el literal `: True`.
   - Esa búsqueda no detecta, por ejemplo, `"validated": is_ok` con un valor fijo, `privacy_cleared=True` como kwarg, ni comillas simples.
   - Hay que documentar la regex exacta y por qué es suficiente, o ampliarla a la clave con cualquier valor constante.

9. **ADVISORY: viabilidad de `mypy --strict`.**
   - Con `from __future__ import annotations` y `Literal` de `typing`, el código es válido en 3.9. `class ProvenancedDict(dict[str, Any])` también funciona en tiempo de ejecución en 3.9 (PEP 585).
   - Riesgo: `pyproject.toml [tool.mypy]` tiene `packages = ["src/geneforgelang"]` y `python_version = "3.9"`. No he verificado si un archivo pasado por línea de comandos sustituye a `packages`; si no lo hace, mypy revisaría todo el paquete y fallaría por el código legacy.
   - Además, una mypy reciente puede no aceptar `python_version=3.9`. Hay que comprobarlo en el venv antes de dar por buena la A4. El test `test_provenance_module_passes_mypy_strict` debería invocar `mypy --strict --no-incremental <archivo>` y dejar constancia de la versión de mypy.

10. **ADVISORY: componentes que el oráculo no detectará.**
    - Los stubs de valor constante (`alpha_genome.py` devuelve `simulated_results` en la línea 46) no importan nada aleatorio. El ítem 4 no los ve; solo los cubre la lista del autor. El contrato debería reconocer ese límite.
    - `plugins/variant_sim.py` (`VariantSimulationPlugin`, que carga `simulate_variant_effect`) no aparece ni en Scope ni en la lista de excepciones. Hay que revisarlo y clasificarlo en `components.md`, aunque sea como dead o fuera de alcance, con su motivo.

11. **ADVISORY: el ítem 9 y la línea base.** "1035 passed, 23 skipped, 10 xfailed" debería guardarse como evidencia antes del cambio. Con los tests nuevos el número de passed cambia, así que conviene redactarlo como "0 failed, 0 errors, xfailed = baseline-1, y passed ≥ baseline".

12. **ADVISORY: la A1.** El test de contrato registra instancias (`registry.register_generator("ProteinVAEGenerator", generator)`), no clases. El atributo de clase `provenance` sigue siendo visible, así que la A1 aguanta, pero el texto debería decir "class or instance".
