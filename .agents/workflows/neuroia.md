# `/neuroia` — Protocolo de Buenas Prácticas NeuroIA

> [!IMPORTANT]
> Este workflow es **vinculante**. Aplicarlo en todas las operaciones de escritura al repositorio. No hay excepciones.

---

## Regla 0 — Identificación de Repositorio

Antes de cualquier `git` operation, confirmar en qué repositorio y rama estás:

```text
1. ¿Qué repo? → neurodiagnoses-monorepo | GeneForge | neurodiagnoses-webapp
2. ¿Qué rama? → NUNCA trabajar directamente en `main`
3. ¿Coincide con el trabajo que estoy haciendo?
```

> [!CAUTION]
> **NUNCA mezclar cambios de un repo en otro.** Verificar la ruta local antes de ejecutar cualquier `git` command.

---

## Regla 1 — Estructura de Ramas

```text
main          → Solo recibe merges via Pull Request. NUNCA commit directo.
feature/*     → Nueva funcionalidad  (ej. feature/gwas-psychiatric-study)
fix/*         → Corrección de bug    (ej. fix/fusion-engine-audit-log)
refactor/*    → Refactorización      (ej. refactor/pps-identifiability)
experiment/*  → Exploración técnica  (ej. experiment/sgpm-v2-ablation)
docs/*        → Solo documentación   (ej. docs/adr-002-decision-theory)
```

**Flujo obligatorio:**
```text
feature/mi-trabajo → (PR revisada) → main
```

---

## Regla 2 — Convención de Commits

Formato: `tipo(scope): descripción breve en imperativo`

| Tipo | Cuándo usarlo |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `refactor` | Cambio sin añadir funcionalidad ni corregir bug |
| `docs` | Solo documentación |
| `test` | Tests nuevos o corregidos |
| `chore` | Tareas de mantenimiento (deps, gitignore...) |
| `perf` | Mejora de rendimiento |

**Ejemplos correctos:**
```text
feat(pps): implement decision theory over equivalence classes v84.0
fix(gwas): activate HuggingFaceGWASSource as default ingestor
docs(adr): add ADR-002 for causal translation layer architecture
test(ncip): add NCIP benchmark suite with recall@k metrics
```

> [!WARNING]
> No commitear nunca: `.pyc`, `__pycache__/`, `.egg-info/`, `.env`, credenciales, datos crudos (>10MB), ni archivos de submodule como fichero plano.

---

## Regla 3 — Checklist Pre-Commit

Antes de `git add`:

- [ ] ¿El `.gitignore` excluye artefactos de build (`__pycache__/`, `*.pyc`, `*.egg-info/`, `.env`)?
- [ ] ¿Ningún archivo contiene credenciales o datos clínicos reales?
- [ ] ¿El código nuevo tiene al menos un test asociado?
- [ ] ¿Estoy en la rama feature correcta (no en `main`)?

```bash
# Verificar qué va al staging ANTES de añadir
git status --short
git diff --stat HEAD

# Solo añadir código fuente
git add src/ backend/ gf/ schemas/ tests/ docs/ *.py *.md *.yaml *.json
```

---

## Regla 4 — Proceso Completo de Sincronización

```bash
# 1. Asegurarse de estar en la rama correcta
git checkout feature/mi-trabajo    # o crearla si no existe

# 2. Añadir solo los archivos correctos
git add <archivos-específicos>
git status --short                  # verificar antes de commitear

# 3. Commit con mensaje convencional
git commit -m "feat(scope): descripción"

# 4. Push a la rama remota (NUNCA a main)
git push origin feature/mi-trabajo

# 5. Crear Pull Request via gh CLI
gh pr create \
  --repo "Fundacion-de-Neurociencias/<REPO>" \
  --base main \
  --head feature/mi-trabajo \
  --title "tipo(scope): título descriptivo" \
  --body "$(cat docs/merges/MR_<FEATURE>.md)"
```

---

## Regla 5 — Documento de Merge Request

Cada PR debe tener un documento en `docs/merges/MR_<FEATURE>.md` con:

```markdown
## Descripción
Qué hace este cambio y por qué.

## Componentes modificados
- archivo.py — qué hace y por qué se modificó

## Cómo reproducir
Pasos para ejecutar o verificar el cambio.

## Tests ejecutados
- [ ] test_xxx.py — resultado

## Impacto en el ecosistema
Qué otros servicios o repos se ven afectados.
```

---

## Regla 6 — Uso de IA (Antigravity)

- La IA **propone**, el desarrollador **aprueba**.
- La IA no decide arquitectura. Ver `docs/decisions/` (ADRs).
- Cada commit generado con ayuda de IA debe ser revisado línea a línea antes de mergearse.
- Prohibido incluir datos clínicos reales en prompts.

---

## Regla 7 — Control de Cambios Estricto mediante Reglas de Protección de Ramas

Como tenéis la suscripción Pro activa, podéis (y debéis) forzar la calidad y seguridad en las ramas principales de vuestros repositorios privados:
- **Bloqueo de Commits Directos a main**: Obligar a que cualquier cambio (código o datos) se proponga mediante un Pull Request (PR).
- **Aprobaciones Requeridas**: Configurar la rama para exigir al menos la revisión y aprobación de otro investigador antes de fusionar.
- **Status Checks Obligatorios**: Impedir el merge si los tests automáticos (CI/CD) de GitHub Actions o los análisis de código limpio no han pasado con éxito.

---

## Regla 8 — Automatización con CODEOWNERS

Definir un archivo `.github/CODEOWNERS` para automatizar quién debe revisar qué parte del proyecto. GitHub Pro permite esto en repositorios privados:

- **Ejemplo de uso**: Si un investigador modifica los algoritmos de redes neuronales o el procesador de datos clínicos, GitHub asignará automáticamente como revisor obligatorio al experto del equipo en esa área.

```text
# Ejemplo de archivo CODEOWNERS
/src/modelos_ia/      @investigador_ia_principal
/data/procesamiento/   @bioinformatico_principal
```

---

## Regla 9 — Aprovechar al máximo GitHub Actions

Integrar flujos de trabajo (pipelines) automáticos en cada Pull Request para asegurar el rigor científico del software:
- **Validación de Modelos**: Ejecutar tests rápidos que verifiquen que los pesos del modelo de IA o las funciones matemáticas no devuelven infinitos o NaN tras una modificación.
- **Auditorías Automáticas**: Añadir linters estáticos y checkers de dependencias vulnerables (pip-audit, npm audit) directamente en el flujo para evitar que dependencias inseguras entren al ecosistema de investigación.

---

## Regla 10 — Documentación Centralizada en Wikis y Pages Privadas

- **Wiki Privada**: GitHub Pro habilita Wikis en repositorios privados. Utilizarla para mantener el diccionario de variables clínicas de NeuroIA, manuales de instalación de entornos de computación local (ej. CUDA, PyTorch) y bitácoras de experimentos.
- **GitHub Pages Privado**: Ideal para alojar reportes interactivos de análisis de datos generados con Jupyter Notebooks o RMarkdown de forma interna y compartida solo con tu equipo.

---

## Verificación rápida de estado

```bash
# Estado de la rama actual vs remoto
git status
git log origin/<rama> --oneline -n 5

# PRs abiertas en este repo
gh pr list --state open

# Últimos commits en todas las ramas
git log --oneline --all --simplify-by-decoration -n 15
```

---

## Workflows relacionados

| Slash command | Archivo | Descripción |
|---|---|---|
| `/neuroia` | `neuroia.md` | **Este archivo** — protocolo git y PRs |
| `/default` | `default.md` | Reglas base del repo |
| `/prompt_compiler` | `prompt_compiler.md` | Compilador de intención antes de actuar |
