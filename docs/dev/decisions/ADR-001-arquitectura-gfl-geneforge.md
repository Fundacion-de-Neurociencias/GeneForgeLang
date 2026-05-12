# ADR-001 — Arquitectura y Contrato de Frontera: GeneForgeLang ↔ GeneForge

**Estado:** Aceptado  
**Fecha:** 2026-03-11  
**Autores:** Equipo NeuroIA (Agente GeneForge + Agente GeneForgeLang)  
**Repositorios afectados:** GeneForgeLang (GFL), GeneForge  

---

## Contexto

Durante la sesión de revisión arquitectónica del 11 de marzo de 2026, el equipo de bioinformáticos identificó varias ambigüedades en la separación de responsabilidades entre los repositorios **GeneForgeLang (GFL)** y **GeneForge**. Este ADR formaliza las decisiones tomadas para resolver dichas ambigüedades y establece el contrato de frontera entre ambos proyectos.

> **Nota:** Este documento es el espejo del ADR-001 en el repositorio GeneForge. Ambos deben mantenerse sincronizados. La copia canónica puede consultarse en cualquiera de los dos repos; en caso de discrepancia, prevalece la versión con fecha de actualización más reciente.

---

## Decisiones

---

### ADR-001.1 — Separación formal de responsabilidades entre GFL y GeneForge

**Decisión:**

| Componente | Repositorio propietario |
|---|---|
| Sintaxis, gramática, parser, validación semántica, sistema de tipos | **GeneForgeLang (GFL)** |
| Motor de inferencia probabilística básico | **GeneForgeLang (GFL)** |
| Primitivas biológicas de bajo nivel (`bio_primitives/`) | **GeneForgeLang (GFL)** |
| Contratos de interfaz de plugin (`entry_points`) | **GeneForgeLang (GFL)** |
| Language Server Protocol (`gfl_lsp`) y API FastAPI | **GeneForgeLang (GFL)** |
| Orquestación de workflows avanzados | **GeneForge** |
| IA avanzada: Foundation Models, Active Learning, Inverse Design | **GeneForge** |
| Procesamiento de imágenes y análisis celular | **GeneForge** |
| Consumo de primitivas GFL como cliente | **GeneForge** |
| Interfaz de usuario y modelo de negocio | **GeneForge (WebApp)** |

**Consecuencias:**
- Ningún repositorio debe implementar lógica que pertenezca al otro según la tabla anterior.
- Cualquier excepción debe ser documentada con un nuevo ADR.

---

### ADR-001.2 — Mecanismo de registro de plugins bioinformáticos

**Contexto:** Existe una dualidad entre plugins internos de GeneForge y plugins externos bioinformáticos en GFL. El mecanismo de resolución ya está implementado en GFL.

**Decisión:** El mecanismo de registro oficial para **todos los plugins bioinformáticos** es el sistema de `entry_points` de Python, definido en el `pyproject.toml` de GFL mediante el grupo `gfl.plugins`. El `PluginRegistry` de GFL los descubre en tiempo de ejecución vía `importlib.metadata.entry_points`.

Para registrar un plugin externo, su `pyproject.toml` debe incluir:
```toml
[project.entry-points."gfl.plugins"]
nombre-plugin = "paquete.modulo:ClasePlugin"
```

**Consecuencias:**
- Los plugins de IA avanzada (Active Learning, Inverse Design) permanecen en GeneForge.
- Los plugins bioinformáticos (BLAST, samtools, GATK, DeepVariant, etc.) se registran en GFL mediante `entry_points`.
- Documentar este mecanismo explícitamente en `CONTRIBUTING.md` de GFL.

---

### ADR-001.3 — Migración bidireccional de lógica entre repositorios

**Lógica que debe migrar de GeneForge → GFL:**
- Traducción DNA→RNA→Proteína (tabla de codones) en `InferenceEngine`
- Recuperación de secuencias vía NCBI Entrez (`handle_find_gene_sequence`)
- Primitivas de biología molecular (complementación, transcripción)

Destino en GFL: módulo `gfl/bio_primitives/`.

**Lógica que debe migrar de GFL → GeneForge:**
- `gfl/execution_engine.py` — orquestación de workflows completos
- `gfl/staging/` — gestión de ficheros en tiempo de ejecución
- Bio-Skills clínicas (`PharmGx`, `NutriGx`, `Geriatric Risk`)

**Criterio de graduación (módulo experimental `gfl/` → estable `src/geneforgelang/`):**

Un módulo puede promoverse cuando cumpla:
1. Cobertura de tests ≥ 80%
2. API pública documentada con docstrings
3. Sin breaking changes no documentadas en los últimos 2 sprints
4. Revisión aprobada por al menos un miembro distinto al autor

Este criterio debe añadirse a `CONTRIBUTING.md`.

**Consecuencias:**
- La migración debe coordinarse entre repositorios para no romper la API pública.
- Crear tickets de trabajo separados para cada bloque de migración.
- No mezclar migraciones con features nuevas en el mismo PR.

---

### ADR-001.4 — Dualidad `gfl/` vs `src/geneforgelang/` — Diseño intencional

**Contexto:** El equipo observó que `main.py` importa desde `gfl/` y no desde `src/geneforgelang/`, y que los tests apuntan a `gfl/`.

**Decisión:** Esta dualidad es **deliberada y correcta**, documentada en `REPOSITORY_COHERENCE_ANALYSIS.md`:
- `gfl/`: núcleo activo experimental. Iteración rápida, features en validación.
- `src/geneforgelang/`: API pública estable, fachada para consumidores downstream.

Los tests apuntan a `gfl/` porque es el núcleo real. Esto no es un error.

**Consecuencias:**
- Documentar el criterio de graduación en `CONTRIBUTING.md` (ver ADR-001.3).
- No forzar imports de `src/` en código que consuma `gfl/` directamente hasta que la feature se haya graduado.

---

### ADR-001.5 — Política de releases, tags y ancla de submódulo

**Decisión:**
- GeneForgeLang debe publicar la tag `v1.0.0` como primer punto de anclaje estable.
- GeneForge actualizará `.gitmodules` para anclar `gfl_core` a esa tag.
- Los submódulos deben anclarse **siempre a tags de release**, nunca a SHAs de commits ordinarios.

**Proceso de release de GFL:**
1. Crear tag: `git tag v1.0.0 && git push origin v1.0.0`
2. Publicar en PyPI: `python -m build && twine upload dist/*`
3. Activar GitHub Pages: Settings → Pages → Branch: `gh-pages`
4. Notificar a GeneForge para actualizar el puntero del submódulo `gfl_core`

**Consecuencias:**
- El README debe actualizar la instrucción de instalación: `pip install -e .` es el método correcto para desarrollo local hasta que PyPI esté disponible.
- El workflow `docs.yml` está correctamente configurado; la activación de GitHub Pages es una acción de configuración de repositorio, no de código.

---

### ADR-001.6 — `docs/reasoning.md`: artefacto histórico

**Decisión:** El archivo `docs/reasoning.md` es un artefacto histórico generado instrumentalmente durante el desarrollo. No es un módulo RAG activo. El sistema no se autoprograma sobre archivos `.md`.

**Consecuencias:**
- Limpiar o archivar `docs/reasoning.md`.
- Si hay interés en RAG introspectivo en el futuro, implementarlo como un plugin explícito en `gfl-plugin-rag-engine`, que es el lugar arquitectónicamente correcto.

---

### ADR-001.7 — Desarrollo web: diferido hasta consolidación del core

**Decisión:** El desarrollo de interfaz web queda **formalmente diferido** hasta que se cumplan:
1. Tag `v1.0.0` publicada, tests de conformidad pasando
2. CLI de GFL funcional y documentada
3. API FastAPI documentada con OpenAPI y cobertura ≥ 70%
4. Pipeline de GeneForge reproducible desde cero

**Consecuencias:**
- La arquitectura actual ya separa `geneforgelang` (core) de `GeneForge-WebApp` (frontend). Esta decisión no tiene coste de refactorización.

---

## Consecuencias Generales

- Este ADR debe ser referenciado en el `CONTRIBUTING.md` de ambos repositorios.
- Cualquier decisión que contradiga este ADR debe documentarse en un nuevo ADR que lo superceda explícitamente.
- Revisión programada: 2026-09-11 o cuando se complete la migración bidireccional de lógica.

---

## Referencias

- `COLLABORATION_PROPOSAL_GFL_GF.md` (sep. 2024)
- `REPOSITORY_COHERENCE_ANALYSIS.md` (oct. 2025)
- `STANDARDIZATION_PLAN.md` (oct. 2025)
- `MIGRATION_NOTES.md`
- ADR-001 en repositorio GeneForge (`docs/decisions/`)
- Protocolo de Buenas Prácticas NeuroIA v1.0 (mar. 2026)
