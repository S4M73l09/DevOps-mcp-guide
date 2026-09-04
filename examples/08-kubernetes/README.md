# 08 - Kubernetes [EN](README.en.md)

## Propósito

Este ejemplo muestra cómo utilizar un servidor MCP para consultar información de un clúster Kubernetes mediante tools de solo lectura.

El servidor utiliza el contexto activo de `kubectl` y no cambia de contexto ni modifica recursos.

## Tools incluidas

### `kubernetes_current_context`

Ejecuta:

```bash
kubectl config current-context
```

Muestra el contexto activo sin cambiarlo.

### `kubernetes_list_pods`

Con un namespace concreto:

```bash
kubectl get pods \
  --namespace default \
  --output wide
```

Sin especificar un namespace:

```bash
kubectl get pods \
  --all-namespaces \
  --output wide
```

### `kubernetes_list_events`

Consulta eventos de un namespace:

```bash
kubectl get events \
  --namespace default \
  --sort-by=.lastTimestamp
```

Los eventos ayudan a detectar problemas de scheduling, imágenes, probes, volúmenes y reinicios.

### `kubernetes_list_namespaces`

Ejecuta:

```bash
kubectl get namespace
```

Muestra los namespaces visibles para la identidad activa.

---

## Validación del namespace

Cuando se proporciona un namespace, el servidor comprueba que:

* No esté vacío.
* No empiece por `-`.
* Se utilice como argumento independiente.
* No se concatene dentro de una shell.

Un namespace inválido produce un error controlado y no ejecuta `kubectl`.


## Contexto activo

El servidor consulta el contexto configurado actualmente en `kubectl`.

No realiza automáticamente ninguna de estas acciones:

```bash
kubectl config use-context
kubectl config set-context
```

Antes de consultar un clúster real, se debe comprobar manualmente:

```bash
kubectl config current-context
kubectl auth can-i get pods
```

## Operaciones excluidas

Este ejemplo no ejecuta:

```text
kubectl apply
kubectl delete
kubectl patch
kubectl edit
kubectl replace
kubectl scale
kubectl rollout restart
kubectl rollout undo
kubectl exec
kubectl cp
kubectl create
kubectl config use-context
```
Estas operaciones pueden modificar recursos, ejecutar comandos dentro de contenedores, cambiar el contexto o alterar el estado del clúster.

## Seguridad

Los comandos se ejecutan mediante listas de argumentos y no utilizan `shell=True`.

El servidor:

* No ejecuta comandos arbitrarios.
* No cambia de contexto.
* No modifica recursos.
* No elimina recursos.
* No ejecuta comandos dentro de contenedores.
* Establece un tiempo máximo de ejecución.
* Valida el namespace antes de usarlo.
* Utiliza el contexto activo del usuario.
* Devuelve la salida y el código de retorno de `kubectl`.

La información devuelta por Kubernetes puede contener nombres de servicios, direcciones internas, eventos y datos operativos sensibles.


## Ejecutar el ejemplo

Desde este directorio:

```bash
uv sync
```

Ejecutar los tests:

```bash
uv run pytest
```

---

## Requisitos del entorno

Para utilizar las tools contra un clúster real se necesita:

* `kubectl` instalado.
* Un contexto Kubernetes configurado.
* Acceso a un clúster.
* Permisos de lectura sobre los recursos consultados.

Los tests no necesitan un clúster real porque utilizan mocks.


## Probarlo con MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector@2.0.0 \
  --config mcp-inspector.json \
  --server kubernetes-devops-mcp
```

En la seccion de `Tools` aparecerán:

```text
kubernetes_current_context
kubernetes_list_pods
kubernetes_list_events
kubernetes_list_namespaces
```

---

## Ejemplos de uso

Consultar el contexto actual:

```json
{}
```

Consultar pods de un namespace:

```json
{
    "namespace": "default"
}
```

Consultar pods de todos los namespaces:

```json
{}
```

Consultar eventos de un namespace:

```json
{
    "namespace": "default"
}
```

Consultar todos los namespaces:

```json
{}
```

## Respuestas con errores

Si el namespace está vacío:

```json
{
    "namespace": " "
}
```

La tool devuelve un error controlado y no ejecuta ningún comando.

Si `kubectl` no puede acceder al clúster, la respuesta incluirá:

```json
{
    "ok": false,
    "return_code": 1,
    "stdout": "",
    "stderr": "..."
}
```

El contenido exacto del error depende del contexto activo y de la configuración local de Kubernetes.


## Qué demuestran los tests

Los tests comprueban:

* La consulta del contexto activo.
* La consulta de pods en un namespace.
* La consulta de pods en todos los namespaces.
* La consulta de eventos.
* La consulta de namespaces.
* El rechazo de namespaces vacíos.
* La construcción de comandos sin utilizar una shell.


## Límites del ejemplo

Este servidor no:

* Ejecuta despliegues.
* Elimina recursos.
* Modifica manifiestos.
* Reinicia workloads.
* Escala deployments.
* Ejecuta comandos dentro de contenedores.
* Cambia el contexto activo.
* Cambia de namespace automáticamente.
* Accede a credenciales directamente.
* Realiza operaciones sobre clústeres sin autorización.

El objetivo es demostrar cómo realizar inspecciones Kubernetes de solo lectura mediante un servidor MCP controlado y predecible.

La idea central del ejemplo sería:

```text
contexto activo
       |
       v
namespace opcional
       |
       v
consulta kubectl de solo lectura
       |
       v
resultado estructurado
```

> Un detalle a remarcar: para `kubernetes_current_context`, `kubernetes_list_namespaces` y la consulta de pods sin namespace, la entrada es `{}`. En cambio, pods y eventos aceptan un `namespace` opcional.

---


## Imagenes que muestran el ejemplo

#### Captura que muestra el estado activo del servidor MCP:

![Capture-devops-kubernetes-tools](Images/Capture-devops-kubernetes-tools.png)


#### Captura que muestra la lista de `Tools`:

![Capture-Kubernetes-Devops-mcp-active](Images/Capture-Kubernetes-Devops-mcp-active.png)


### Captura de `Tools`

#### Captura mostrando la tool `current_context`:

![Capture-kubernetes-current-context](Images/Capture-kubernetes-current-context.png)


#### Captura mostrando el error de la tool `current_context`:

![Capture-kubernetes-current-context-result](Images/Capture-kubernetes-current-context-result-error.png)


#### Captura mostrando la tool `list_pods`:

![Capture-kubernetes-list-pods](Images/Capture-kubernetes-list-pods.png)


#### Captura mostrando el error de la tool `list_pods`:

![Capture-kubernetes-list-pods-result](Images/Capture-kubernetes-list-pods-result.png)


#### Captura mostrando la tool `list_events`:

![Capture-kubernetes-list-events](Images/Capture-kubernetes-list-events.png)


#### Captura mostrando el error de la tool `list_events`:

![Capture-kubernetes-list-events](Images/Capture-kubernetes-list-events-result.png)


#### Captura mostrando la tool `list_namespaces`:

![Capture-kubernetes-list-namespaces](Images/Capture-kubernetes-list-namespaces.png)


#### Captura mostrando el error de la tool `list_namespaces`:

![Capture-kubernetes-list-namespaces-result](Images/Capture-kubernetes-list-namespaces-result.png)


> Al no tener un contexto Kubernetes configurado, las cuatro tools devolverán un error al ejecutarse. Esto no significa que las tools estén mal, sino que su funcionamiento es el esperado.
