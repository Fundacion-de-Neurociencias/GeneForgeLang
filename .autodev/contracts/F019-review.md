# Evaluator review of the F019 contract (verbatim, language as returned)

Revisión del contrato F019. Solo he leído el contrato y la entrada en features.json. No he ejecutado nada ni editado ningún archivo.

**Veredicto:** el contrato puede usarse si se corrige, pero tiene huecos. D1, D3 y D4 se pueden verificar por CLI. D2 y parte de la aceptación 3 no están cubiertos tal como los pide la feature.

1. D1: falta el comando grep exacto y la regex, y guardar la salida en `evidence/F019/`.
2. Aceptación 2 ("affected examples and the LSP still run"): D2 lo sustituye por "imports sin cambios + suite verde". Falta el comando que arranca el servidor LSP (responder a `initialize`) y al menos un ejemplo ejecutado, con salida guardada.
3. Aceptación 3 ("on the publish branch"): D3 corre sobre HEAD de `autodev/F019`, no sobre la rama de publicación. Concretar la rama y ejecutar el check sobre ella. Documentar que el prefiltro de `publish_check` busca por nombre.
4. "Outside documented test fixtures": el test nuevo contiene rutas de ejemplo; el contrato no dice cómo se excluyen ni dónde se documenta.
5. Excepciones legítimas (`/home/vscode`, `C:\Users\Public`): enumerarlas en un solo sitio.
6. A1 se falsifica con la propia herramienta evaluada: añadir una comprobación independiente de que el árbol de publicación no contiene `.autodev/`.
7. Historial git: las rutas siguen en commits antiguos; la decisión de aceptarlo debe quedar escrita.
8. A2: verificar que los enlaces relativos nuevos no salen del repositorio.
9. Puertas de calidad: ruff sobre el test nuevo y `language_check` del diff.
