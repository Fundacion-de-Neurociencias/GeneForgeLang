name: Reporte de Bug (NeuroIA Protocol)
description: Crear un reporte de error siguiendo el protocolo estricto
title: "[BUG]: "
labels: ["bug", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        Gracias por tomarte el tiempo para reportar un error.
        Por favor, asegúrate de seguir las directrices de NeuroIA y de que tu reporte no esté relacionado con regresiones conocidas (ej. reintroducción de `gfl/`, archivos duplicados en `examples/`, o scripts duplicados en `resources/tools/`).
  - type: textarea
    id: description
    attributes:
      label: Descripción del problema
      description: Una descripción clara y concisa de lo que es el error.
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: Pasos para reproducir
      description: Pasos exactos para reproducir el comportamiento.
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Comportamiento esperado
      description: Una descripción clara y concisa de lo que esperabas que pasara.
    validations:
      required: true
  - type: textarea
    id: ci_cd_status
    attributes:
      label: Estado de CI/CD local
      description: ¿Has corrido pytest y ruff localmente? (Sí/No) Si hay errores, adjúntalos.
    validations:
      required: true
