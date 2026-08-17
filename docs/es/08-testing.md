# 08 - Testing [EN](../en/08-testing.md)

## Proposito

Explicar como probar servidores MCP y sus herramientas antes de utilizarlos en entornos reales.

El testing no depende unicamente del protocolo MCP. Tambien depende de las herramientas, recursos, prompts, transportes y sistemas externos que el servidor exponga.

## Indice

- [Introduccion](#introduccion)
- [Capas de testing](#capas-de-testing)
- [Tests unitarios](#tests-unitarios)
- [Tests de contrato MCP](#tests-de-contrato-mcp)
- [Tests con MCP Inspector](#tests-con-mcp-inspector)
- [Tests de integracion](#tests-de-integracion)
- [Mocks y entornos controlados](#mocks-y-entornos-controlados)
- [Tests especificos de DevOps](#tests-especificos-de-devops)
- [Tests negativos y de seguridad](#tests-negativos-y-de-seguridad)
- [Tests de transporte](#tests-de-transporte)
- [Tests de rendimiento y concurrencia](#tests-de-rendimiento-y-concurrencia)
- [Tests end-to-end](#tests-end-to-end)
- [Automatizacion en CI/CD](#automatizacion-en-cicd)
- [Matriz de pruebas](#matriz-de-pruebas)
- [Checklist final](#checklist-final)
- [Idea clave](#idea-clave)

---

## Introduccion

Un servidor MCP puede parecer correcto porque inicia y muestra sus herramientas, pero eso no demuestra que sea seguro, compatible o adecuado para un entorno real.

Una prueba completa debe validar:

- El codigo interno.
- El contrato MCP.
- Las herramientas expuestas.
- Los recursos y prompts.
- El transporte utilizado.
- Los permisos.
- Las integraciones externas.
- El comportamiento ante errores.

No todas las pruebas necesitan Kubernetes, Docker, Terraform o credenciales reales. Una estrategia adecuada separa la logica propia de las dependencias externas y utiliza mocks, fixtures y entornos aislados cuando sea posible.

## Capas de testing

Las pruebas pueden organizarse de menor a mayor alcance:

```text
Tests unitarios
  |
  +-- Contratos y esquemas MCP
        |
        +-- Integracion con el servidor
              |
              +-- Transporte stdio o HTTP
                    |
                    +-- Sistemas DevOps externos
                          |
                          +-- Host MCP real
```

Cada capa encuentra problemas diferentes:

| Capa | Que comprueba | Coste habitual |
|---|---|---:|
| Unitaria | Logica aislada | Bajo |
| Contrato | Compatibilidad MCP | Bajo |
| Integracion | Servidor y cliente | Medio |
| Transporte | Comunicacion real | Medio |
| Externa | Kubernetes, Docker o cloud | Alto |
| End-to-end | Flujo completo | Alto |

La mayoria de las pruebas deberian estar en las capas rapidas. Las pruebas externas y end-to-end deben reservarse para los flujos que realmente necesiten validar una integracion completa.

## Tests unitarios

Los tests unitarios prueban la logica del servidor sin iniciar necesariamente todo el proceso MCP.

Pueden cubrir:

- Validacion de argumentos.
- Conversion de datos.
- Filtrado de logs.
- Limites de paginacion.
- Construccion de respuestas.
- Gestion de errores.
- Redaccion de secretos.
- Traduccion de estados externos a errores MCP.

Ejemplo conceptual:

```text
Entrada:
  namespace = staging
  lines = 100

Resultado esperado:
  namespace valido
  lines dentro del limite
  consulta permitida
```

Tambien deben probarse los casos invalidos:

```text
lines = -1       -> rechazar
lines = 1000000  -> rechazar
namespace = prod -> rechazar si no esta autorizado
```

Estos tests deben ser rapidos, deterministas y no depender de una red, un cluster o credenciales reales.

## Tests de contrato MCP

Los tests de contrato comprueban que el servidor cumple lo que anuncia a traves de MCP.

Conviene validar:

- `initialize`.
- `tools/list`.
- `tools/call`.
- `resources/list`.
- `resources/read`.
- `prompts/list`.
- `prompts/get`.
- Esquemas JSON.
- Campos obligatorios.
- Tipos de entrada y salida.
- Capacidades declaradas.

Un servidor no deberia anunciar una capacidad que no puede ejecutar correctamente. Del mismo modo, una herramienta debe declarar un esquema coherente con los argumentos que realmente acepta.

Ejemplo de comprobacion:

```text
tools/list
  |
  +-- La herramienta existe
  +-- Tiene nombre unico
  +-- Tiene descripcion
  +-- Tiene inputSchema valido
  +-- Los campos requeridos coinciden con la implementacion
```

Esta capa comprueba que el servidor habla MCP correctamente, aunque no ejecute todavia operaciones reales sobre Kubernetes o Terraform.

## Tests con MCP Inspector

MCP Inspector es una herramienta interactiva oficial para probar y depurar servidores MCP. Puede utilizarse como primera comprobacion manual durante el desarrollo.

Con Inspector se pueden revisar:

- Conexion mediante `stdio`.
- Conexion mediante `Streamable HTTP`.
- Negociacion inicial.
- Herramientas disponibles.
- Esquemas y argumentos.
- Recursos y suscripciones.
- Prompts y sus argumentos.
- Resultados de ejecucion.
- Logs y notificaciones.

Flujo recomendado:

```text
1. Iniciar el servidor con Inspector.
2. Comprobar la conexion.
3. Revisar initialize y las capacidades.
4. Listar tools, resources y prompts.
5. Ejecutar casos validos.
6. Ejecutar casos invalidos.
7. Revisar resultados, errores y logs.
```

El Inspector es muy util durante el desarrollo, pero no sustituye a los tests automatizados. Una prueba manual puede descubrir un problema; un test automatizado ayuda a evitar que reaparezca.

Ejemplo conceptual de ejecucion:

```bash
npx @modelcontextprotocol/inspector <comando-del-servidor> <argumentos>
```

El comando exacto depende del lenguaje y del gestor de paquetes utilizado por el servidor.

## Tests de integracion

Los tests de integracion prueban el servidor completo junto con un cliente MCP o un cliente de prueba.

Pueden validar:

- Inicio real del proceso.
- Comunicacion por `stdio`.
- Endpoint HTTP.
- Negociacion de capacidades.
- Llamadas reales a herramientas.
- Respuestas y errores.
- Cancelacion y timeouts.
- Reinicios del servidor.
- Limpieza de recursos al terminar.

Una prueba de integracion tipica podria seguir este flujo:

```text
Iniciar servidor
  |
  +-- Conectar cliente MCP
  +-- Ejecutar initialize
  +-- Listar herramientas
  +-- Llamar una herramienta de lectura
  +-- Verificar resultado
  +-- Cerrar conexion
  +-- Comprobar apagado limpio
```

En esta capa ya se prueba la comunicacion entre componentes, pero conviene seguir utilizando un entorno controlado para los sistemas externos.

## Mocks y entornos controlados

Las dependencias externas deben simularse cuando no sea necesario comprobar el sistema real.

Ejemplos:

- API de Kubernetes simulada.
- Cliente Docker mock.
- Terraform en modo plan.
- API cloud simulada.
- Fixtures de logs.
- Directorios temporales.
- Respuestas HTTP predefinidas.

La separacion puede resumirse asi:

```text
Logica propia:
  Tests rapidos y deterministas.

Integraciones externas:
  Mocks o sandbox.

Produccion:
  Nunca usarla como entorno de pruebas normal.
```

Un mock debe representar los casos relevantes, incluidos los fallos. Simular siempre una respuesta correcta crea una falsa sensacion de seguridad.

Conviene cubrir tambien:

- Recurso inexistente.
- Permiso insuficiente.
- Timeout.
- Respuesta incompleta.
- Error de autenticacion.
- Servicio externo no disponible.
- Datos malformados.

## Tests especificos de DevOps

Las pruebas concretas dependen de las herramientas que el servidor exponga.

### Kubernetes

Pueden probarse:

- Namespaces autorizados.
- Recursos inexistentes.
- Pods sin logs.
- Permisos insuficientes.
- Limites de cantidad de logs.
- Contexto de cluster incorrecto.
- Acciones sobre produccion bloqueadas.

### Docker

Pueden probarse:

- Contenedor inexistente.
- Contenedor detenido.
- Limites de salida.
- Acceso al socket.
- Imagen no permitida.
- Operaciones de borrado bloqueadas.

### Terraform

Pueden probarse:

- Plan sin cambios.
- Cambios esperados.
- Estado bloqueado.
- Workspace no autorizado.
- Error de credenciales.
- Bloqueo de `destroy`.
- Separacion entre `plan` y `apply`.

### Cloud

Pueden probarse:

- Regiones permitidas.
- Cuentas autorizadas.
- Recursos fuera de alcance.
- Limites de coste.
- Credenciales caducadas.
- Operaciones de escritura sin aprobacion.

## Tests negativos y de seguridad

Los tests negativos comprueban que el servidor rechaza correctamente lo que no debe aceptar.

Casos recomendados:

- Argumentos malformados.
- Campos ausentes.
- Valores fuera de rango.
- Inyeccion de comandos.
- Rutas no autorizadas.
- Namespaces no permitidos.
- Credenciales caducadas.
- Tokens destinados a otro servidor.
- Operaciones destructivas sin confirmacion.
- Secretos en respuestas o logs.
- Peticiones HTTP con `Origin` invalido.
- Acceso sin permisos.

Un test de seguridad no debe comprobar solo que la operacion falla. Tambien debe comprobar que:

- No se modifica el estado externo.
- No se filtran datos sensibles.
- El error es comprensible.
- La operacion queda registrada si corresponde.
- No se reintenta automaticamente una accion peligrosa.

Ejemplo:

```text
Peticion: delete_resource(production_namespace)
Resultado esperado:
  - Operacion rechazada
  - Cluster sin cambios
  - Sin secretos en la respuesta
  - Evento registrado
```

## Tests de transporte

### stdio

Las pruebas de `stdio` deben comprobar:

- `stdout` contiene unicamente mensajes MCP validos.
- Los logs se escriben en `stderr`.
- El proceso termina correctamente.
- El cliente detecta cierres inesperados.
- Se controlan timeouts y cancelaciones.
- Las rutas de configuracion funcionan fuera del directorio de desarrollo.

Una salida accidental en `stdout` puede romper la comunicacion:

```text
stdout correcto:
  JSON-RPC valido

stdout incorrecto:
  Starting server...
  JSON-RPC valido
```

### Streamable HTTP

Las pruebas de `Streamable HTTP` deben cubrir:

- HTTPS.
- Cabeceras obligatorias.
- Validacion de `Origin`.
- Respuestas JSON.
- Respuestas SSE.
- Errores HTTP `400`, `401`, `403` y `500`.
- Limites de tamaño.
- Timeouts.
- Conexiones concurrentes.
- Cancelacion de operaciones.

El objetivo no es solo demostrar que existe un endpoint, sino comprobar que responde de forma predecible y segura ante peticiones validas e invalidas.

## Tests de rendimiento y concurrencia

No todos los servidores necesitan un benchmark completo, pero conviene medir los flujos que puedan afectar a la experiencia o a la infraestructura.

Se pueden medir:

- Latencia de las herramientas.
- Tamaño de las respuestas.
- Muchas llamadas simultaneas.
- Operaciones largas.
- Cancelacion.
- Uso de memoria.
- Limites de conexiones.
- Saturacion del sistema externo.

Las operaciones largas deben tener un comportamiento definido:

```text
Inicio
  |
  +-- Progreso observable
  +-- Timeout controlado
  +-- Cancelacion posible
  +-- Resultado final o error claro
```

No se deben lanzar pruebas de carga contra produccion sin autorizacion y sin limites bien definidos.

## Tests end-to-end

Los tests end-to-end prueban el flujo completo:

```text
Usuario
  |
  v
Host MCP
  |
  v
Cliente MCP
  |
  v
Servidor MCP
  |
  v
Kubernetes, Docker, Terraform o cloud
```

Son pruebas de alto valor, pero tambien mas lentas, fragiles y costosas. Deben ejecutarse en un entorno controlado y con datos de prueba.

Un flujo end-to-end puede verificar:

- El host descubre el servidor.
- Las herramientas aparecen correctamente.
- El usuario autoriza una operacion.
- El servidor valida los argumentos.
- El sistema externo ejecuta el cambio.
- El resultado vuelve al host.
- La auditoria queda registrada.

No conviene utilizar produccion como entorno end-to-end habitual.

## Automatizacion en CI/CD

Una secuencia razonable para cada pull request seria:

```text
Pull request
  |
  +-- Lint y tipos
  +-- Tests unitarios
  +-- Tests de contrato
  +-- Tests de seguridad
  +-- Tests de integracion
  +-- Build del servidor
  +-- Publicacion o despliegue controlado
```

Los tests que necesitan credenciales reales, servicios costosos o entornos especiales deben quedar separados y protegidos.

Una politica sencilla podria ser:

- Cada cambio ejecuta tests unitarios y de contrato.
- Cada cambio en transporte ejecuta tests de integracion del transporte.
- Cada cambio en una herramienta ejecuta sus casos validos e invalidos.
- Los cambios de permisos ejecutan tests de seguridad.
- Los tests contra un sandbox se ejecutan antes de publicar una version.
- Las pruebas destructivas requieren una ejecucion manual y controlada.

## Matriz de pruebas

| Area | Unitario | Integracion | End-to-end |
|---|---:|---:|---:|
| Validacion de argumentos | Si | Si | Opcional |
| `tools/list` | No | Si | Si |
| Kubernetes | Mock | Sandbox | Opcional |
| Secretos | Si | Si | No usar produccion |
| `stdio` | No | Si | Si |
| Streamable HTTP | No | Si | Si |
| Permisos | Si | Si | Si |
| Destruccion de recursos | Mock | Sandbox | Solo controlado |

Esta matriz no es una regla universal. Sirve para decidir donde colocar cada prueba y evitar que todo dependa de una unica prueba end-to-end.

## Checklist final

Antes de utilizar un servidor MCP en un entorno real:

- [ ] El servidor inicia correctamente.
- [ ] `initialize` funciona.
- [ ] Las capacidades declaradas son correctas.
- [ ] Las herramientas tienen esquemas validos.
- [ ] Se prueban entradas validas e invalidas.
- [ ] Se prueban errores y permisos insuficientes.
- [ ] No se filtran secretos.
- [ ] `stdio` mantiene `stdout` limpio.
- [ ] HTTP valida autenticacion y transporte.
- [ ] Las operaciones destructivas estan protegidas.
- [ ] Existen tests automatizados en CI.
- [ ] Las integraciones reales utilizan sandbox o entornos controlados.
- [ ] Se han probado timeouts y cancelaciones.
- [ ] Los logs son utiles y no contienen credenciales.
- [ ] Existe una forma de reproducir los fallos.

## Idea clave

Probar un servidor MCP no significa solamente comprobar que arranca.

```text
Servidor inicia
  + contrato MCP valido
  + herramientas correctas
  + entradas validadas
  + errores controlados
  + permisos comprobados
  + transporte probado
  + integraciones aisladas
  + regresiones automatizadas
  = servidor mas confiable
```

La estrategia debe crecer junto con el servidor. Un servidor con una herramienta local de solo lectura puede necesitar principalmente tests unitarios, de contrato e integracion. Un servidor que modifica Kubernetes, Terraform o cloud necesita ademas sandbox, pruebas negativas, autorizacion, auditoria y controles para operaciones destructivas.

Fuentes principales:

- [MCP Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)
- [MCP Debugging Guide](https://modelcontextprotocol.io/docs/tools/debugging)
- [MCP Python SDK](https://py.sdk.modelcontextprotocol.io/get-started/)
