# ADR 001: Adopción del Protocolo de Buenas Prácticas NeuroIA

**Fecha**: 2026-03-08
**Estado**: Aceptado
**Autor**: Antigravity (IA)

## Contexto
El repositorio de GeneForgeLang (GFL) ha crecido orgánicamente, acumulando múltiples scripts en la raíz y careciendo de una estructura estandarizada para datos y resultados. Para escalar de forma profesional y asegurar la reproducibilidad científica exigida por NeuroIA, es necesario formalizar la estructura y los flujos de trabajo.

## Decisión
Se ha decidido adoptar el "Protocolo de Buenas Prácticas para Repositorios NeuroIA v1.0". Los cambios realizados incluyen:
1. Reestructuración de carpetas (`data/`, `results/`, `docs/decisions/`, etc.).
2. Movimiento de scripts de utilidad de la raíz a `scripts/`.
3. Implementación de CI/CD mediante GitHub Actions.
4. Protección de la rama `main` (configuración manual requerida en GitHub).
5. Estandarización de mensajes de commit y flujo de PRs.

## Consecuencias
- **Positivas**: Mayor orden, facilidad de onboarding, reproducibilidad garantizada por CI, trazabilidad de decisiones técnicas.
- **Negativas**: Mayor rigor en el flujo de trabajo inicial para los desarrolladores.
- **Neutrales**: Necesidad de mantener actualizada la carpeta `docs/decisions/` para cambios futuros.
