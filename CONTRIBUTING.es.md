# Contributing

Gracias por contribuir a esta guía sobre MCP aplicado a DevOps.

## Objetivo del proyecto

Esta guía busca explicar MCP progresivamente y construir ejemplos prácticos de servidores MCP orientados a DevOps.

## Tipos de contribuciones

- Correcciones de errores técnicos o lingüísticos.
- Mejoras en la documentación.
- Traducciones entre español e inglés.
- Nuevos ejemplos MCP.
- Diagramas y material visual.
- Casos de uso de Kubernetes, Terraform, Docker, CI/CD u observabilidad.
- Correcciones de seguridad o claridad.

## Estructura de la documentación

- `docs/es/`: documentación en español.
- `docs/en/`: documentación en inglés.
- `examples/`: ejemplos progresivos.
- `complete-server/`: servidor MCP completo de referencia.
- `diagrams/`: diagramas del proyecto.

## Documentación bilingüe

Cada capítulo nuevo debe incluir:

- Una versión en `docs/es/`.
- Una versión equivalente en `docs/en/`.
- Enlaces entre ambas versiones.
- Enlaces actualizados desde `docs/README.md`.

Los cambios conceptuales deben aplicarse en ambos idiomas.

## Fuentes y referencias

Las afirmaciones técnicas importantes deben basarse en documentación oficial de MCP o en fuentes primarias.

Las fuentes utilizadas deben añadirse a:

- `docs/SOURCES.md`

Cuando una parte dependa de una versión concreta de MCP, debe indicarse la versión correspondiente.

## Convenciones de documentación

- Usar Markdown claro y estructurado.
- Mantener índices internos actualizados.
- Preferir ejemplos pequeños y progresivos.
- Explicar primero el concepto y después el código.
- Evitar presentar acciones destructivas como valores por defecto.
- Documentar riesgos y limitaciones en ejemplos DevOps.

## Ejemplos de código

Los ejemplos deben:

- Ser ejecutables o indicar claramente si son conceptuales.
- Mantener una responsabilidad concreta.
- Validar las entradas.
- Evitar comandos arbitrarios.
- No incluir secretos reales.
- Explicar el transporte utilizado.
- Incluir una forma de probarlos.

## Seguridad

Los ejemplos deben priorizar:

- Operaciones de lectura.
- Allow lists.
- Validación de parámetros.
- Límites de tiempo y salida.
- Confirmación humana para operaciones sensibles.
- Protección de secretos y datos internos.

## Pull requests

Una contribución debería comprobar:

- Que el Markdown se renderiza correctamente.
- Que los enlaces internos funcionan.
- Que las versiones española e inglesa están sincronizadas.
- Que los ejemplos no contienen secretos.
- Que la documentación refleja la versión de MCP utilizada.
- Que los cambios se mantienen dentro del objetivo del capítulo.

## Estilo de commits

Usar mensajes claros, por ejemplo:

- `docs: add MCP resources chapter`
- `docs: translate tools chapter`
- `fix: correct architecture links`
- `example: add Kubernetes read-only server`