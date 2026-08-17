# 09 - Casos de uso DevOps [EN](../en/09-devops-use-cases.md)

## Proposito

Mostrar casos de uso reales en los que MCP puede aportar valor dentro de operaciones DevOps.

MCP no sustituye a Kubernetes, Docker, Terraform, los sistemas cloud o las plataformas CI/CD. Proporciona una interfaz controlada para consultar esos sistemas y, cuando corresponda, ejecutar operaciones sobre ellos.

El objetivo de este capítulo es relacionar las capacidades de MCP con problemas operativos concretos y definir una progresión segura para construir un servidor MCP DevOps.

## Indice

- [Introduccion](#introduccion)
- [Como analizar un caso de uso](#como-analizar-un-caso-de-uso)
- [Diagnostico de servicios](#diagnostico-de-servicios)
- [Lectura y analisis de logs](#lectura-y-analisis-de-logs)
- [Consultas Kubernetes](#consultas-kubernetes)
- [Operaciones Kubernetes controladas](#operaciones-kubernetes-controladas)
- [Operaciones Docker](#operaciones-docker)
- [Terraform](#terraform)
- [Integracion con CI/CD](#integracion-con-cicd)
- [Automatizacion de runbooks](#automatizacion-de-runbooks)
- [Observabilidad e incidentes](#observabilidad-e-incidentes)
- [Relacion entre tools, resources y prompts](#relacion-entre-tools-resources-y-prompts)
- [Que no deberia hacer el primer servidor](#que-no-deberia-hacer-el-primer-servidor)
- [Evolucion recomendada](#evolucion-recomendada)
- [Matriz de riesgo](#matriz-de-riesgo)
- [Idea clave](#idea-clave)

---

## Introduccion

En DevOps existen muchas tareas repetitivas que requieren consultar diferentes sistemas:

- Kubernetes.
- Docker.
- Terraform.
- Plataformas cloud.
- Sistemas CI/CD.
- Herramientas de observabilidad.
- Repositorios de codigo.
- Sistemas de tickets e incidencias.

MCP puede proporcionar una interfaz comun para consultar esos sistemas y, de forma controlada, ejecutar acciones.

Un servidor MCP DevOps podria permitir:

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
Servidor DevOps MCP
  |
  +-- Kubernetes
  +-- Docker
  +-- Terraform
  +-- CI/CD
  +-- Observabilidad
```

La capacidad de ejecutar operaciones no debe implicar que todas las acciones sean automaticas. Cada herramienta debe tener un alcance definido, unos permisos concretos y un nivel de riesgo conocido.

---

## Como analizar un caso de uso

Cada caso de uso deberia documentarse utilizando una estructura comun:

```text
Objetivo
  |
  +-- Sistema externo
  +-- Herramientas MCP
  +-- Recursos MCP
  +-- Prompts opcionales
  +-- Permisos necesarios
  +-- Riesgos
  +-- Tests
  +-- Nivel de automatizacion
```

Para cada caso conviene responder:

* Que problema resuelve.
* Que datos necesita.
* Que herramientas MCP expone.
* Que operaciones son de solo lectura.
* Que operaciones modifican el estado.
* Que confirmaciones son necesarias.
* Que errores pueden producirse.
* Que permisos requiere.
* Como se puede probar.
* Que nivel de riesgo tiene.

Una herramienta deberia representar una accion concreta:

```text
get_pod_logs(namespace, pod, lines)
```

En lugar de una herramienta demasiado general:

```text
run_shell(command)
```

Las herramientas concretas son mas faciles de validar, autorizar, probar y auditar.

## Diagnostico de servicios

El diagnostico de servicios es uno de los primeros casos de uso recomendables porque puede aportar valor sin modificar la infraestructura.

Un usuario podria preguntar:

```text
¿Por que el servicio api esta fallando?
```

El servidor MCP podria seguir este flujo:

```text
1. Consultar el estado del deployment.
2. Consultar los pods asociados.
3. Leer eventos recientes.
4. Leer logs recientes.
5. Comparar replicas esperadas y disponibles.
6. Identificar errores frecuentes.
7. Devolver un resumen del diagnostico.
```

Herramientas posibles:

```text
get_service_status
list_service_pods
get_recent_events
get_pod_logs
```

Un resultado podria incluir:

```text
Servicio: api
Entorno: staging

Estado:
  - Replicas deseadas: 3
  - Replicas disponibles: 1
  - Pods con errores: 2

Indicadores:
  - ImagePullBackOff
  - Reinicios frecuentes
  - Error de conexion con la base de datos

Siguiente paso sugerido:
  - Revisar las credenciales y el estado de la base de datos.
```

Este caso deberia comenzar con herramientas de solo lectura.


## Lectura y analisis de logs

La lectura de logs es una tarea frecuente en operaciones y soporte.

Una herramienta podria definirse como:

```text
get_pod_logs(namespace, pod, lines, since)
```

Debe aplicar limites como:

* Namespaces permitidos.
* Numero maximo de lineas.
* Tiempo maximo de consulta.
* Tamaño maximo de respuesta.
* Redaccion de secretos.
* Filtros de texto controlados.

Ejemplo de entrada:

```json
{
  "namespace": "staging",
  "pod": "api-123",
  "lines": 100,
  "since": "15m"
}
```

Es importante diferenciar entre leer logs e interpretar logs:

```text
Leer logs:
  Operacion de consulta.

Analizar logs:
  Operacion de analisis.

Modificar el sistema por un error detectado:
  Operacion separada y con confirmacion.
```

Un servidor no deberia ejecutar automaticamente una accion de reparacion simplemente porque un log contenga una instruccion o un error conocido.

## Consultas Kubernetes

Kubernetes ofrece una gran cantidad de recursos que pueden consultarse mediante MCP:

* Pods.
* Deployments.
* Services.
* Ingresses.
* Jobs.
* Events.
* Namespaces.
* ConfigMaps no sensibles.
* Estado de nodos.

Herramientas de lectura posibles:
```text
list_pods(namespace)
get_deployment(namespace, name)
list_services(namespace)
get_ingress(namespace, name)
get_recent_events(namespace)
```

El servidor debe limitar:

* Contexto del cluster.
* Namespaces.
* Tipos de recursos.
* Cantidad de resultados.
* Acceso a datos sensibles.
* Identidades que pueden realizar consultas.

No deberia exponerse automaticamente el contenido de todos los Secrets de Kubernetes. El hecho de que una identidad pueda consultar el cluster no significa que deba leer todos sus secretos.

## Operaciones Kubernetes controladas

Las operaciones que modifican Kubernetes deben separarse de las consultas.

```text
Lectura:
  list_pods
  get_deployment
  get_pod_logs

Escritura:
  restart_deployment
  scale_deployment
  apply_manifest

Destructiva:
  delete_resource
  delete_namespace
```

Las operaciones de escritura deberian indicar claramente:

* Cluster afectado.
* Entorno.
* Namespace.
* Recurso.
* Cambio que se realizara.
* Identidad utilizada.
* Posibilidad de rollback.
* Requisitos de confirmacion.

Ejemplo conceptual:

```text
Herramienta: scale_deployment
Namespace: staging
Deployment: api
Replicas actuales: 3
Replicas nuevas: 5
Confirmacion requerida: si
```

Las operaciones destructivas deberian tener controles adicionales:

* Bloqueadas por defecto.
* Limitadas a entornos no productivos.
* Protegidas por confirmacion humana.
* Limitadas a una lista de recursos.
* Registradas en auditoria.
* Sujetas a permisos especificos.

## Operaciones Docker

Docker puede utilizarse para tareas locales o para gestionar contenedores en un host.

Casos posibles:

* Listar contenedores.
* Consultar el estado de un contenedor.
* Leer logs.
* Inspeccionar imagenes.
* Consultar consumo de recursos.
* Reiniciar un contenedor autorizado.

Herramientas posibles:

```text
list_containers
get_container_status
get_container_logs
inspect_image
restart_container
```

El acceso al socket de Docker requiere especial cuidado. Dependiendo de la configuracion, quien pueda utilizarlo puede obtener permisos muy amplios sobre el sistema anfitrion.

Por ello, un servidor MCP Docker deberia:

* Limitar los contenedores accesibles.
* Evitar comandos arbitrarios.
* Restringir imagenes y volumenes.
* No exponer secretos.
* Separar consultas de operaciones de escritura.
* Ejecutarse con permisos minimos.

---

## Terraform

Terraform es un caso de uso importante porque combina lectura de configuracion, analisis de cambios y modificaciones potencialmente destructivas.

La progresion recomendada seria:

```text
terraform fmt
  |
  v
terraform validate
  |
  v
terraform plan
  |
  v
Revision humana
  |
  v
terraform apply autorizado
```

Herramientas posibles:

```text
terraform_format
terraform_validate
terraform_plan
terraform_apply
```
Cada herramienta deberia tener una responsabilidad concreta:

```text
terraform_validate:
  Comprueba la configuracion.

terraform_plan:
  Muestra los cambios previstos.

terraform_apply:
  Ejecuta cambios autorizados.

terraform_destroy:
  Debe estar bloqueado o protegido con controles reforzados.
```

El resultado de un plan deberia resumir:

* Recursos que se crearan.
* Recursos que se modificaran.
* Recursos que se eliminaran.
* Posibles riesgos.
* Workspace utilizado.
* Entorno afectado.

El servidor no deberia aplicar automaticamente un plan solo porque el modelo lo haya solicitado. El plan debe poder revisarse y la aplicacion debe requerir autorizacion adecuada.

---

## Integracion con CI/CD

MCP puede utilizarse para consultar y controlar plataformas CI/CD.

Casos de lectura:

* Consultar ejecuciones.
* Obtener el estado de un pipeline.
* Leer logs de un job.
* Buscar el commit desplegado.
* Consultar artefactos.
* Identificar el paso que fallo.

Casos de escritura:

* Reintentar un job.
* Cancelar una ejecucion.
* Crear una ejecucion.
* Promover una version.
* Desplegar en un entorno.

La diferencia de riesgo se puede resumir asi:

```text
Consultar pipeline:
  Riesgo bajo.

Leer logs de una ejecucion:
  Riesgo bajo o medio.

Reintentar pipeline:
  Riesgo medio.

Promover una version:
  Riesgo alto.

Desplegar en produccion:
  Riesgo muy alto.
```

Herramientas posibles:

```text
get_pipeline_status
get_job_logs
get_deployment_commit
retry_pipeline
promote_release
```

Las operaciones de despliegue deberian requerir:

* Entorno explicito.
* Version o commit concreto.
* Permisos adecuados.
* Confirmacion.
* Auditoria.
* Posibilidad de detener el proceso.

## Automatizacion de runbooks

MCP puede ayudar a estructurar y ejecutar runbooks operativos.

Ejemplo de runbook para un servicio no disponible:

```text
1. Consultar estado del servicio.
2. Consultar pods.
3. Leer eventos.
4. Leer logs.
5. Verificar dependencias.
6. Proponer posibles causas.
7. Esperar confirmacion.
8. Ejecutar una accion permitida.
9. Verificar recuperacion.
10. Registrar el resultado.
```

Los prompts pueden ayudar a guiar este flujo:

```text
diagnose-service-failure
```

Las herramientas proporcionarian las operaciones:

```text
get_service_status
get_pod_logs
get_recent_events
restart_deployment
```

Los recursos podrian exponer:

```text
runbook://services/api/recovery
```

El runbook no deberia convertirse en una autorizacion global. Cada accion seguiria necesitando sus propios controles.

---

## Observabilidad e incidentes

Otro caso de uso es reunir informacion de distintos sistemas para investigar un incidente.

El servidor podria:

* Consultar metricas.
* Correlacionar logs y eventos.
* Comparar el estado actual con el anterior.
* Identificar errores recientes.
* Preparar una linea temporal.
* Generar un resumen de incidente.
* Preparar informacion para un postmortem.

Flujo conceptual:

```text
Incidente detectado
  |
  +-- Consultar metricas
  +-- Consultar logs
  +-- Consultar cambios recientes
  +-- Consultar despliegues
  +-- Correlacionar informacion
  +-- Preparar resumen
  +-- Esperar decision operativa
```

Este caso de uso puede aportar mucho valor utilizando principalmente permisos de lectura.

---

## Relacion entre herramientas, recursos y prompts

Los casos DevOps pueden dividirse entre los tres bloques principales de MCP:

| Elemento MCP | Uso DevOps |
|---|---|
| Herramienta | Ejecutar una consulta o accion |
| Recurso | Exponer logs, estados, documentacion o configuracion |
| Prompt | Guiar diagnosticos y runbooks repetibles |

Ejemplo:

```text
Herramienta:
  get_pod_logs

Recurso:
  kubernetes://clusters/staging/namespaces/api

Prompt:
  diagnose-service-failure
```

La eleccion depende de la naturaleza del contenido:

* Si debe ejecutarse una accion, probablemente sea una herramienta.
* Si se expone informacion consultable, puede ser un recurso.
* Si se estructura una forma de trabajo, puede ser un prompt.

No todo debe convertirse en una herramienta. Exponer documentacion operativa como recurso puede ser mas apropiado que crear una herramienta que devuelva texto estatico.

---

## Que no deberia hacer el primer servidor

El primer servidor DevOps deberia tener un alcance pequeño y controlado.

No deberia comenzar con:

* Shell arbitrario.
* Acceso a todos los clusters.
* Credenciales administrativas globales.
* Modificaciones automaticas en produccion.
* Lectura general de secretos.
* Logs sin limites ni filtrado.
* Una herramienta que mezcle diagnostico y destruccion.
* Acceso simultaneo a todos los sistemas de la organizacion.

Un comienzo mas razonable seria:

```text
Servidor local
  |
  +-- stdio
  +-- Herramientas de solo lectura
  +-- Entorno de desarrollo o staging
  +-- Permisos limitados
  +-- Tests automatizados
  +-- Auditoria basica
```

## Evolucion recomendada

Una progresion posible para el futuro servidor DevOps seria:

```text
Fase 1:
  Diagnostico local con stdio.

Fase 2:
  Herramientas de lectura para Docker o Kubernetes.

Fase 3:
  Resources para logs, estados y documentacion.

Fase 4:
  Prompts para runbooks.

Fase 5:
  Terraform plan y analisis de cambios.

Fase 6:
  Operaciones de escritura con confirmacion.

Fase 7:
  Streamable HTTP y autorizacion.

Fase 8:
  Integracion con CI/CD y entornos compartidos.
```

Cada fase deberia completarse con:

* Tests.
* Revision de permisos.
* Documentacion.
* Logs.
* Manejo de errores.
* Revision de riesgos.

## Matriz de riesgo

| Caso de uso | Lectura | Escritura | Riesgo inicial |
|---|---|---|---|
| Listar pods | Si | No | Bajo |
| Leer logs | Si | No | Bajo/medio |
| Reiniciar deployment | No | Si | Medio |
| Escalar servicio | No | Si | Medio/alto |
| Terraform plan | Si | No | Medio |
| Terraform apply | No | Si | Alto |
| Eliminar recursos | No | Si | Muy alto |
| Desplegar en produccion | No | Si | Muy alto |

El nivel de riesgo depende de:

* Permisos.
* Entorno.
* Tipo de recurso.
* Posibilidad de rollback.
* Confirmacion humana.
* Alcance de las credenciales.
* Calidad de los tests.
* Auditoria disponible.

## Idea clave

El primer servidor DevOps deberia comenzar como una herramienta de diagnostico y consulta, no como un sistema de automatizacion completa.

```text
Lectura
  |
  +-- Diagnostico
        |
        +-- Propuesta de accion
              |
              +-- Confirmacion
                    |
                    +-- Escritura controlada
                          |
                          +-- Verificacion
                                |
                                +-- Auditoria
```

MCP puede proporcionar una interfaz comun para interactuar con herramientas DevOps, pero cada operacion debe tener permisos, validaciones y limites claros.

La estrategia recomendada es comenzar con capacidades de solo lectura y ampliar progresivamente el servidor cuando existan:

* Permisos adecuados.
* Tests suficientes.
* Confirmaciones.
* Auditoria.
* Rollback o recuperacion.
* Limites claros de entorno.

Este enfoque prepara el camino para construir una plantilla reutilizable de servidor MCP DevOps sin mezclar desde el principio todas las tecnologias y riesgos posibles.

Fuentes principales:

* [MCP Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
* [MCP Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
* [MCP Resources](https://modelcontextprotocol.io/specification/2026-07-28/server/resources)
* [MCP prompts](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts)
* [MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)
