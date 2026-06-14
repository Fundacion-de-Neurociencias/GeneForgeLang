# Protocolo de Buenas Prácticas - NeuroIA v1.0 (GFL Adaptation)

Este documento detalla los estándares y flujos de trabajo adoptados en el repositorio de GeneForgeLang (GFL) para garantizar la reproducibilidad científica, colaboración eficiente y trazabilidad.

## 1. Estructura del Repositorio
- `data/raw/`: Datos crudos nunca modificados manualmente.
- `data/processed/`: Salidas de procesamiento intermedio.
- `src/`: Código fuente reutilizable (paquete `geneforgelang`).
- `notebooks/`: Exploración y prototipado.
- `results/`: Salidas reproducibles y figuras finales.
- `docs/decisions/`: Registro de decisiones técnicas (ADRs).
- `scripts/`: Utilidades y herramientas de mantenimiento.
- `tests/`: Suite de pruebas automatizadas.

## 2. Flujo de Git
- **main**: Rama siempre estable y desplegable.
- **feature/*, fix/*, experiment/***: Ramas de trabajo.
- **Pull Requests (PR)**: Obligatorios para cualquier cambio en `main`. Deben incluir descripción técnica, pasar todos los tests del CI y ser revisados por un par.
- **Commits Atómicos**: Cada commit debe representar una unidad lógica de cambio. Evitar commits "monolíticos".

## 3. Convención de Commits
Formato: `tipo: descripción`
- `feat`: Nueva funcionalidad.
- `fix`: Corrección de error.
- `refactor`: Mejora interna sin cambio funcional.
- `docs`: Cambios en documentación.
- `test`: Añadir o corregir pruebas.
- `chore`: Tareas de mantenimiento (dependencias, configuración).
- `atomic`: Se requiere que los commits sean **atómicos** (una tarea, un commit).

### Guía Rápida de Comandos
```bash
# 1. Crear rama de trabajo
git checkout -b feature/nombre-tarea

# 2. Hacer commit atómico
git add .
git commit -m "feat: descripción clara de la tarea"

# 3. Subir e iniciar PR
git push origin feature/nombre-tarea
```

## 4. Reproducibilidad
- Versiones fijadas en `requirements.txt`.
- Uso de semillas (seeds) en procesos estocásticos.
- Generación automática de Reproducibilidad Packages (hashes, timestamps).

## 5. Uso de IA (Antigravity/GitHub Copilot)
- Revisión humana obligatoria de todo código generado.
- Prohibido subir credenciales o datos sensibles en prompts.
- La IA asiste en la implementación, pero el desarrollador es responsable de la arquitectura.
