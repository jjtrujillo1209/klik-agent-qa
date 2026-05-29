# Ai Programas Documentation Map

Este mapa separa los documentos utiles del workspace de los archivos generados, dependencias y resultados. La prioridad de marca queda en `01-ACTIVO/MUNDO_ORQUESTADOR/docs/`.

## Canon De Mundo Orquestador

- `01-ACTIVO/MUNDO_ORQUESTADOR/README.md`: entrada rapida del proyecto.
- `01-ACTIVO/MUNDO_ORQUESTADOR/docs/`: documentacion limpia de marca, producto, arquitectura y operacion.
- `01-ACTIVO/MUNDO_ORQUESTADOR/n8n_projects/`: workflows y documentacion tecnica de n8n.
- `99-Graphify/01-ACTIVO/MUNDO_ORQUESTADOR.md`: indice autogenerado, no canon editorial.

## Carpetas Del Workspace

| Carpeta | Uso |
|---|---|
| `01-ACTIVO/` | Productos y sistemas activos |
| `02-BIA/` | Documentos, propuestas y activos de BIA Energy |
| `03-PROSPECTING/` | Bases, scripts y resultados de prospeccion |
| `04-DATOS/` | QA, facturas, RUES y limpieza de datos |
| `05-ESTRATEGIA/` | Estrategia comercial, leads, paid media |
| `06-INFRAESTRUCTURA/` | Herramientas tecnicas, n8n, skills y dev tooling |
| `07-ARCHIVO/` | Material archivado o historico |
| `99-Graphify/` | Indices autogenerados para navegar el vault |
| `docs/` | Documentos sueltos de apoyo |

## Reglas De Limpieza

- No usar `node_modules`, `venv`, `.venv`, `.git`, `__pycache__` ni `logs` como fuentes documentales.
- No tratar outputs `.csv`, `.xlsx`, `.db` o screenshots de debug como documentacion de marca.
- Mantener Mundo Orquestador como marca limpia desde `01-ACTIVO/MUNDO_ORQUESTADOR/docs/`.
- Usar `99-Graphify` para descubrimiento, no como fuente final de narrativa.

## Siguiente Orden Recomendado

1. Revisar docs canonicos de Mundo Orquestador.
2. Mover futuros documentos de marca al hub `docs/`.
3. Archivar reportes historicos que no sean necesarios para venta, producto u operacion.
4. Regenerar Graphify excluyendo dependencias y entornos virtuales.
