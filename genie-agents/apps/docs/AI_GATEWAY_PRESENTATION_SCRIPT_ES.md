# Guion de presentación: Databricks AI Gateway

Presentación fuente: **Databricks AI Gateway — Problem–Solution Presentation**  
Alcance: únicamente las **13 diapositivas visibles**. Las diapositivas ocultas no forman parte de este guion.  
Duración sugerida: **35–45 minutos**, más preguntas.

> Nota para el presentador: los ejemplos relacionados con operaciones, infraestructura, redes, ciberseguridad y generación de energía son ilustrativos. Conviene validarlos con Central Puerto antes de describirlos como casos reales de la organización.

## Mensaje principal de toda la presentación

AI Gateway es la **capa central de acceso, gobierno, observabilidad y confiabilidad** para el tráfico de IA generativa. No crea por sí solo la lógica de negocio de un agente y tampoco sustituye a las herramientas que utiliza el agente. Se ubica entre las aplicaciones y los modelos para decidir quién puede llamar a qué modelo, bajo qué límites y salvaguardas, dejando además evidencia de uso, costo, calidad y comportamiento.

Una frase corta para repetir durante la exposición:

> “AI Gateway convierte el acceso disperso a modelos de IA en un servicio empresarial gobernado.”

---

## Diapositiva 1 — Databricks AI Gateway: el plano de control de GenAI

### Objetivo

Abrir la conversación y establecer que la presentación trata de control operativo y gobierno, no solamente de acceso técnico a modelos.

### Guion hablado

“Buenos días. Hoy vamos a hablar de Databricks AI Gateway y, sobre todo, del problema empresarial que resuelve.

En muchas organizaciones, la adopción de IA generativa empieza de forma descentralizada. Un equipo utiliza OpenAI, otro usa Claude, otro prueba Gemini y otro despliega un modelo abierto. Esa libertad ayuda a experimentar, pero con el tiempo aparecen preguntas difíciles: ¿quién está utilizando cada modelo?, ¿con qué datos?, ¿cuánto cuesta?, ¿qué ocurre si el proveedor falla?, ¿cómo evitamos que se envíe información sensible?, ¿y cómo demostramos todo esto ante seguridad, auditoría o cumplimiento?

AI Gateway funciona como un plano de control para ese tráfico. La idea es disponer de un punto común desde el cual podamos acceder a distintos modelos, gobernar su utilización y observar qué está ocurriendo.

Cuando decimos ‘plano de control’, no significa que AI Gateway reemplace las aplicaciones o los modelos. Significa que centraliza las políticas y la evidencia operativa. La aplicación continúa haciendo su trabajo y el modelo continúa generando respuestas, pero las llamadas pasan por una capa gestionada que aplica controles consistentes.

Durante la presentación veremos cuatro temas recurrentes: acceso unificado, gobierno, observabilidad y confiabilidad.”

### Ejemplo para Central Puerto

“Imaginemos distintos equipos explorando asistentes para mantenimiento, análisis documental, soporte de infraestructura, programación o ciberseguridad. Sin una capa común, cada iniciativa puede terminar con credenciales, proveedores, límites y registros diferentes. AI Gateway ofrece una forma de operar todas esas iniciativas con reglas compartidas.”

### Transición

“Antes de ver la solución, conviene entender por qué el crecimiento de GenAI se vuelve difícil de administrar.”

---

## Diapositiva 2 — El desafío de gestionar GenAI a escala

### Objetivo

Explicar los cuatro problemas: proliferación de modelos, falta de visibilidad, riesgo de cumplimiento y confiabilidad en producción.

### Guion hablado

“Esta diapositiva resume cuatro dificultades que aparecen cuando GenAI deja de ser un experimento y comienza a utilizarse a escala.

La primera es la **proliferación de modelos**, o *model sprawl*. El mercado cambia muy rápido: aparecen modelos nuevos, cambian precios, capacidades y ventanas de contexto, y cada equipo quiere probar la opción más adecuada. El problema no es tener variedad; el problema es administrarla mediante integraciones independientes. Si habilitar un modelo requiere un nuevo proceso de seguridad, compras, credenciales y desarrollo, la plataforma central se convierte en un cuello de botella. Cuando la habilitación tarda demasiado, los usuarios buscan atajos y aparecen accesos no gobernados.

La segunda dificultad es la **falta de visibilidad**. Sin telemetría central no sabemos qué equipos usan cada modelo, cuántas solicitudes realizan, cuántos tokens consumen, cuánto cuestan o qué latencia experimentan. Tampoco podemos comparar proveedores ni detectar aplicaciones anómalas. En ese contexto, optimizar gasto o planificar capacidad se vuelve prácticamente imposible.

El tercer problema es el **riesgo de cumplimiento**. Una solicitud puede incluir datos personales, secretos, credenciales, información contractual o contenido operativo sensible. Si esa solicitud se envía directamente a un proveedor externo y no queda un rastro auditable, la organización pierde capacidad de investigación y demostración de controles. Una única interacción sin seguimiento puede convertirse en un incidente.

El cuarto problema es la **confiabilidad en producción**. Una prueba puede tolerar que una API no responda. Una aplicación crítica no. Si el sistema depende de un único proveedor o endpoint, una interrupción, una cuota agotada o un aumento de latencia puede dejar fuera de servicio una funcionalidad completa. Para producción necesitamos rutas alternativas, límites, monitoreo y procedimientos consistentes.”

### Pregunta para involucrar a la audiencia

“De estos cuatro puntos —proliferación, visibilidad, cumplimiento y confiabilidad—, ¿cuál representa hoy el mayor desafío para ustedes?”

### Ejemplo para Central Puerto

“Pensemos en un asistente que resume procedimientos técnicos. Aunque el caso parezca sencillo, debemos saber quién accede, qué documentos puede consultar, qué modelo recibe el contenido, cuál es el costo y qué alternativa existe si el proveedor no está disponible.”

### Transición

“AI Gateway responde a estos cuatro desafíos con una capa central, pero sin obligarnos a utilizar un único modelo.”

---

## Diapositiva 3 — Databricks AI Gateway: la respuesta

### Objetivo

Presentar los tres pilares de la solución: acceso consolidado, gobierno centralizado y confiabilidad.

### Guion hablado

“La respuesta se organiza en tres pilares.

El primero es el **acceso consolidado**. Desde una interfaz común podemos trabajar con modelos de proveedores como OpenAI, Anthropic o Google, además de modelos abiertos o modelos alojados en Databricks. También existe la opción de utilizar credenciales administradas por la organización, lo que suele llamarse *bring your own key*. El valor de esto es desacoplar la aplicación del proveedor concreto.

El segundo pilar es el **gobierno centralizado**. Podemos controlar identidades y permisos, imponer límites de uso, aplicar guardrails y capturar telemetría. Los datos operativos se integran con Unity Catalog, de manera que el gobierno del tráfico de GenAI se conecta con el modelo general de gobierno de datos y activos de la plataforma.

El tercer pilar es la **confiabilidad de nivel productivo**. La plataforma puede utilizar balanceo y mecanismos de *fallback*. Si una ruta principal falla, alcanza un límite o deja de cumplir las condiciones esperadas, podemos enviar la solicitud a una alternativa configurada. Esto no elimina todos los riesgos —los modelos pueden comportarse de forma diferente—, pero evita que una sola dependencia técnica sea el único punto de falla.

La idea no es declarar que todos los modelos son iguales. La idea es dar a las aplicaciones una forma común y gobernada de acceder a ellos, conservando la capacidad de elegir el modelo adecuado para cada caso.”

### Aclaración importante

“AI Gateway no garantiza por sí solo que una respuesta sea correcta. Los guardrails reducen ciertos riesgos y la observabilidad aporta evidencia, pero la calidad debe evaluarse con pruebas, métricas, trazas, revisión humana cuando corresponda y evaluación continua.”

### Transición

“Veamos ahora cómo estos pilares benefician de forma diferente al equipo de plataforma y al equipo de desarrollo.”

---

## Diapositiva 4 — Una capa común para plataforma y desarrollo

### Objetivo

Explicar la interfaz estándar, el gobierno y la observabilidad como capacidades compartidas.

### Guion hablado

“Esta diapositiva conecta dos perspectivas.

Para el **equipo de desarrollo**, el beneficio principal es poder llamar a diferentes modelos mediante una interfaz estándar. La aplicación no debería necesitar una arquitectura completamente nueva cada vez que cambia el proveedor. Esto acelera pruebas, comparaciones y evolución tecnológica.

Para el **equipo de plataforma**, el valor está en centralizar permisos, límites de consumo y guardrails. La plataforma puede ofrecer acceso como un servicio gobernado, en lugar de entregar credenciales de proveedores y esperar que cada aplicación implemente controles por separado.

Para ambos equipos existe un tercer beneficio: la **observabilidad unificada**. Las métricas de uso y el registro de payloads permiten estudiar costo, cumplimiento y calidad desde una ubicación común.

Aquí conviene distinguir dos conceptos. El *usage tracking* registra información de consumo: solicitudes, tokens, latencia, errores y señales de costo. El *payload logging* puede conservar el contenido de entrada y salida para auditoría o análisis. Registrar payloads aporta mucho valor, pero debe configurarse de acuerdo con las políticas de privacidad, retención y acceso. No todo contenido debería quedar visible para cualquier operador.

Por eso, centralizar no significa abrir indiscriminadamente la información. Significa aplicar controles consistentes y decidir de manera explícita qué se registra, durante cuánto tiempo y quién puede consultarlo.”

### Ejemplo

“Un desarrollador podría comparar dos modelos sin gestionar dos integraciones totalmente independientes. Al mismo tiempo, plataforma puede imponer un presupuesto o una tasa máxima y seguridad puede verificar que se aplican los controles definidos.”

### Transición

“La siguiente diapositiva muestra el recorrido concreto de una solicitud a través del Gateway.”

---

## Diapositiva 5 — Recorrido de una solicitud

### Objetivo

Explicar visualmente el flujo completo: cliente, controles previos, modelo, controles posteriores y telemetría.

### Guion hablado

“Leamos este diagrama de izquierda a derecha.

Primero tenemos el **cliente**, que puede ser una persona, una aplicación, un agente o una herramienta de programación. El cliente envía una solicitud a una interfaz estándar.

Antes de llamar al modelo, AI Gateway puede verificar los **permisos**. La pregunta es: ¿esta identidad está autorizada a utilizar este endpoint o esta categoría de modelo?

Después aplica los **límites de tasa o consumo**. Estos límites evitan que una aplicación monopolice capacidad, ayudan a controlar costos y protegen frente a errores como un bucle que genera miles de llamadas.

Luego aparecen los **guardrails de entrada**. Su función puede incluir detectar o bloquear categorías de contenido, identificar información sensible o impedir ciertas solicitudes antes de que salgan hacia el modelo. Es importante decir ‘puede’ porque el comportamiento exacto depende de la configuración.

La solicitud llega entonces a la API del modelo seleccionado: Anthropic, Llama, otro proveedor o incluso un proveedor personalizado.

Cuando vuelve la respuesta, pueden aplicarse **guardrails de salida** para revisar el contenido generado. Estos controles ayudan a bloquear o marcar respuestas que incumplen políticas, pero no sustituyen la validación de negocio.

En paralelo se realiza **seguimiento de uso** y, si la política lo permite, **registro del payload**. Así obtenemos evidencia sobre volumen, costo, latencia, errores y contenido.

Finalmente aparecen el **balanceo y los fallbacks**. El balanceo permite distribuir tráfico entre endpoints; el fallback permite intentar una ruta alternativa cuando la principal no está disponible o no satisface una condición operativa.

El punto importante es que los controles ya no dependen de que cada desarrollador los implemente correctamente en cada aplicación. Se convierten en una capacidad de plataforma.”

### Matiz sobre fallback

“Un fallback técnico no siempre es semánticamente transparente. Dos modelos pueden producir respuestas distintas o admitir herramientas diferentes. Por eso hay que probar la compatibilidad y definir qué degradación es aceptable.”

### Transición

“Sobre esta base, Databricks presenta una experiencia renovada para descubrir, administrar y observar endpoints.”

---

## Diapositiva 6 — Novedades de AI Gateway

### Objetivo

Explicar descubrimiento y administración, visibilidad, APIs/fallbacks y soporte para asistentes de código.

### Guion hablado

“Aquí se destacan cuatro mejoras operativas.

La primera es **Discover & Manage**. Existe una entrada central en la navegación para descubrir y administrar recursos, crear endpoints y controlar el acceso mediante permisos de Unity Catalog. Esto facilita que la plataforma publique accesos aprobados para casos de uso concretos.

La segunda es **Unified Visibility**. Se ofrecen paneles listos para usar, métricas en tiempo real, seguimiento de gasto y logging más rápido. El hecho de que la información quede integrada con Unity Catalog ayuda a mantener gobierno, permisos y trazabilidad.

La tercera es una cobertura más amplia de **APIs y fallbacks**. Los fallbacks entre múltiples endpoints permiten automatizar la conmutación ante fallos. El soporte de APIs nativas de proveedores también es relevante porque algunas capacidades avanzadas no siempre encajan completamente en una interfaz genérica.

La cuarta es el soporte para **agentes de programación**, como Claude Code, Codex o Gemini CLI. Estas herramientas pueden generar un consumo significativo y además procesar código o contexto sensible. El Gateway permite aplicar presupuestos, límites, observabilidad y selección de proveedor desde una plataforma común.

Esto extiende el alcance del gobierno: no se limita a una aplicación web de chatbot; también puede cubrir herramientas que los equipos técnicos utilizan directamente.”

### Ejemplo para la conversación

“Podríamos autorizar una herramienta de programación a un grupo concreto, asignarle un límite mensual, registrar su consumo y decidir qué proveedor o endpoint puede utilizar, sin distribuir credenciales externas a cada usuario.”

### Transición

“Estas novedades se apoyan en un conjunto más amplio de capacidades de gobierno que veremos ahora.”

---

## Diapositiva 7 — Gobierno de modelos y agentes

### Objetivo

Agrupar las capacidades en logging, cumplimiento, costo, tráfico y gobierno.

### Guion hablado

“Esta diapositiva puede entenderse como el catálogo de controles.

En **logging** tenemos seguimiento de uso y registro de payloads. Esto responde a preguntas como quién llamó, cuándo, a qué endpoint, con qué latencia, cuántos tokens utilizó y, cuando esté permitido, qué entrada y salida se procesaron.

En **cumplimiento** aparecen los guardrails. Son políticas aplicadas al contenido de entrada o salida para reducir riesgos. Debemos verlos como una capa de defensa, no como una garantía absoluta.

En **control de costos** tenemos rate limiting. Los límites pueden proteger capacidad, evitar abuso y asociar consumo a identidades o equipos. Un límite técnico se convierte así en un mecanismo financiero y operativo.

En **gestión de tráfico** aparecen pruebas A/B y fallbacks. Las pruebas A/B ayudan a comparar rutas o modelos con tráfico real controlado. Los fallbacks mejoran continuidad. Para comparar correctamente, debemos observar no solo disponibilidad y latencia, sino también calidad y costo.

Finalmente, en **gobierno** tenemos permisos e integración con Unity Catalog. Esta parte conecta el acceso a modelos con las identidades, grupos y políticas ya utilizadas para otros activos.

El valor no está en una función aislada. Está en aplicar estas capacidades de forma consistente a distintos modelos y aplicaciones.”

### Ejemplo

“Un equipo de operaciones podría tener acceso a un endpoint aprobado con un límite determinado, mientras que un entorno de pruebas tendría otro límite y quizá modelos menos costosos. Seguridad podría consultar evidencia sin necesidad de entrar en cada aplicación.”

### Transición

“Ahora debemos precisar exactamente qué tipo de sistemas gobierna AI Gateway y cuáles quedan fuera de su alcance principal.”

---

## Diapositiva 8 — Qué gobierna AI Gateway

### Objetivo

Diferenciar modelos externos, modelos alojados en Databricks, agentes inteligentes y ML clásico.

### Guion hablado

“Esta distinción es fundamental para evitar expectativas incorrectas.

Primero, AI Gateway gobierna **modelos externos**: OpenAI, Claude, Gemini, Azure OpenAI, Cohere u otros proveedores personalizados. La organización puede exponerlos mediante endpoints gobernados.

Segundo, gobierna **modelos alojados en Databricks**: modelos fundacionales, modelos ajustados y modelos personalizados servidos mediante Model Serving. Aunque el modelo esté dentro de la plataforma, seguimos necesitando políticas, métricas de uso y telemetría de calidad.

Tercero, cubre el tráfico de **agentes inteligentes**. Un agente puede usar RAG, invocar herramientas o coordinar varios componentes. Cada vez que el agente llama a un modelo a través de un endpoint gobernado, AI Gateway puede aplicar sus controles.

Pero aquí está el límite: **AI Gateway gobierna el tráfico hacia los modelos; no gobierna toda la lógica de negocio del agente**. No decide por sí solo si una orden de mantenimiento debe aprobarse, si una acción sobre infraestructura está autorizada o si una recomendación es técnicamente segura. Esas decisiones requieren permisos de herramientas, reglas de negocio, aprobación humana y otros controles.

Por último, el **machine learning clásico** tiene un alcance diferente. Un modelo de fraude, pronóstico, clasificación o anomalías puede servirse y monitorearse con capacidades de Model Serving y monitoreo, pero los guardrails diseñados para lenguaje generativo no son necesariamente el control apropiado.

En resumen: AI Gateway está optimizado para tráfico GenAI y llamadas a LLMs. No debemos presentarlo como un sustituto universal de gobierno para cualquier modelo analítico.”

### Ejemplo para energía

“Un modelo que pronostica demanda o detecta anomalías en sensores es ML clásico. Un asistente que explica el resultado del pronóstico utilizando lenguaje natural sí genera tráfico GenAI. Ambos pueden coexistir, pero se gobiernan con controles parcialmente distintos.”

### Transición

“Con el alcance claro, veamos dónde se ubica el Gateway dentro de una arquitectura de agentes.”

---

## Diapositiva 9 — AI Gateway dentro de una arquitectura de agentes

### Objetivo

Explicar la arquitectura sin leer cada etiqueta del diagrama.

### Guion hablado

“Esta es la diapositiva más densa. No hace falta leer cada caja; conviene explicar el flujo por capas.

En la primera capa tenemos los **canales de entrada**: una consulta SQL con funciones de IA, una aplicación web o una Databricks App. Todas representan formas distintas de recibir una petición de usuario.

Después viene la **construcción del prompt**. La consulta puede combinarse con instrucciones, contexto, plantillas y ejemplos. En un agente también puede incluir información recuperada desde datos empresariales.

La siguiente capa es la **inferencia**. La aplicación puede llamar a un modelo personalizado, un modelo fundacional alojado en Databricks o un modelo externo. AI Gateway se coloca en esta ruta para aplicar límites, guardrails, seguimiento de uso y registro.

Luego está la capa de **monitoreo y evaluación**. Aquí aparecen tablas de inferencia, trazas, métricas, evaluación de agentes, Lakehouse Monitoring y tablas del sistema. Estas capacidades permiten responder no solo ‘¿funcionó la API?’, sino ‘¿qué calidad tuvo la respuesta?, ¿cuánto costó?, ¿qué latencia presentó?, ¿qué ocurrió durante la ejecución?’.

También puede incorporarse **feedback de usuario**, que ayuda a identificar respuestas útiles o problemáticas y alimenta el ciclo de mejora.

El mensaje arquitectónico es que AI Gateway no vive aislado. Se integra con el ciclo completo: aplicaciones, construcción de prompts, modelos, telemetría, evaluación y gobierno.

La diapositiva indica además que los modelos externos pueden accederse mediante Mosaic AI Gateway, creando un punto central para límites y monitoreo. Esa centralización evita tener una conexión opaca y diferente desde cada aplicación hacia cada proveedor.”

### Forma simple de resumir el diagrama

“Entrada, contexto, modelo, controles, evidencia y mejora continua.”

### Transición

“Los agentes, además de hablar con modelos, necesitan conectarse con herramientas. Ahí entra MCP.”

---

## Diapositiva 10 — Ejemplos concretos de servidores MCP

### Objetivo

Explicar MCP y diferenciar el gobierno del modelo del gobierno de las herramientas.

### Guion hablado

“MCP, o *Model Context Protocol*, es un protocolo que permite a un agente descubrir e invocar herramientas y fuentes de contexto mediante una interfaz estándar.

En **datos y analítica**, un servidor MCP podría exponer Databricks SQL, Genie, funciones de Unity Catalog o Vector Search. El agente podría consultar datos gobernados o recuperar contexto empresarial.

En **ingeniería**, podría conectarse con GitHub, Jira, sistemas de CI/CD, Terraform o inventarios de nube. El agente podría inspeccionar un repositorio, preparar un ticket o validar un despliegue.

En **operaciones de TI y redes**, las herramientas podrían incluir ServiceNow, una CMDB, DNS/IPAM, SD-WAN u observabilidad. Un agente podría recopilar evidencia de un incidente y proponer una remediación.

En **ciberseguridad**, podría integrarse con SIEM, SOAR, escáneres de vulnerabilidades, IAM o inteligencia de amenazas.

Aquí debemos separar dos planos. AI Gateway gobierna la llamada al **modelo**: identidad, consumo, guardrails, proveedor, registro y disponibilidad. El servidor MCP y la herramienta deben gobernar la **acción**: qué operación puede ejecutar el agente, sobre qué recursos, con qué credenciales y si requiere aprobación.

Un guardrail de lenguaje no reemplaza un control de autorización. Si un agente puede reiniciar un servicio, modificar infraestructura o crear un ticket, esa acción debe estar protegida por permisos de mínimo privilegio, validaciones y, cuando corresponda, aprobación humana.

La combinación correcta es: Gateway para gobernar el razonamiento basado en modelos; MCP y los sistemas de destino para gobernar herramientas y acciones.”

### Ejemplo para Central Puerto

“Un agente de incidentes podría consultar telemetría, buscar procedimientos y preparar una hipótesis. Pero una acción que cambie una configuración de red o un sistema operativo debería requerir permisos específicos y posiblemente aprobación. AI Gateway registra y controla el tráfico del modelo; no sustituye ese circuito de autorización.”

### Transición

“Con esa separación clara, podemos revisar escenarios concretos de control.”

---

## Diapositiva 11 — Escenarios prácticos de control

### Objetivo

Traducir capacidades técnicas a cuatro casos de uso.

### Guion hablado

“El primer escenario es un **copiloto de infraestructura**. Podemos enrutar las solicitudes al modelo preferido, configurar una alternativa si el proveedor falla y limitar tokens o gasto por equipo. Esto combina continuidad operativa con control financiero.

El segundo es un **agente de incidentes de red**. Antes de enviar información al modelo podemos ocultar credenciales o identificadores sensibles. Durante la ejecución podemos registrar prompts, llamadas a herramientas y respuestas, y después analizar latencia, errores y trazas. El objetivo es reconstruir qué hizo el agente y por qué.

El tercero es un **agente de triaje de seguridad**. Se pueden aplicar controles de entrada y salida y restringir el acceso a modelos o servidores MCP según la identidad, el workspace y el caso de uso autorizado. Un analista y una aplicación automatizada no tienen por qué disponer de los mismos permisos.

El cuarto son los **asistentes de programación**. Herramientas como Claude Code, Codex y Gemini CLI pueden gobernarse con presupuestos, límites, logging y elección de proveedor. Esto ayuda a evitar credenciales dispersas y a conocer el consumo real.

Estos ejemplos muestran que una misma plataforma puede aplicar controles comunes a experiencias muy distintas. La política puede variar por caso de uso, pero la forma de administrarla y observarla es coherente.”

### Preguntas sugeridas para Central Puerto

1. “¿Qué casos de uso necesitan continuidad mediante fallback?”
2. “¿Qué categorías de datos nunca deberían enviarse a un proveedor externo?”
3. “¿Qué acciones de un agente requerirían aprobación humana?”
4. “¿Conviene asignar límites por persona, equipo, aplicación o centro de costo?”

### Transición

“Para tomar esas decisiones necesitamos datos consolidados de uso, y eso es lo que muestra la siguiente diapositiva.”

---

## Diapositiva 12 — Seguimiento centralizado del uso

### Objetivo

Explicar el valor de un dashboard unificado y cómo usarlo para operación y decisiones.

### Guion hablado

“Aquí el mensaje es sencillo: todo el tráfico de GenAI debe producir señales que puedan analizarse de forma centralizada.

Un dashboard de AI/BI puede mostrar consumo por endpoint, proveedor, modelo, aplicación, usuario o equipo. También puede ayudar a observar tokens, solicitudes, latencia, errores y costo estimado.

Esto permite varios tipos de decisiones.

Desde el punto de vista financiero, podemos identificar qué casos de uso concentran el gasto y si existe una alternativa más eficiente.

Desde operaciones, podemos detectar aumentos de errores, degradación de latencia o proximidad a cuotas.

Desde gobierno, podemos verificar quién utiliza modelos determinados y si el patrón coincide con el acceso aprobado.

Desde calidad, podemos relacionar telemetría de uso con evaluaciones y feedback. Un modelo más barato no necesariamente es mejor si produce respuestas de menor calidad; un modelo más potente tampoco es automáticamente conveniente si su latencia y costo no justifican el beneficio.

La observabilidad convierte una discusión basada en impresiones en una discusión basada en evidencia. En lugar de preguntar ‘¿parece que utilizamos mucho este modelo?’, podemos medirlo y atribuirlo.”

### Aclaración

“El dashboard no debe convertirse en una exposición indiscriminada de prompts. Las métricas agregadas y el acceso al contenido de payloads pueden requerir niveles de permiso diferentes.”

### Transición

“Terminemos condensando toda la propuesta en cuatro ideas.”

---

## Diapositiva 13 — Cuatro conclusiones

### Objetivo

Cerrar con una síntesis memorable y orientar los próximos pasos.

### Guion hablado

“La primera conclusión es **un endpoint gobernado** para modelos, agentes y asistentes de programación. Esto simplifica la experiencia de acceso y reduce integraciones y credenciales dispersas.

La segunda es **un plano de políticas** para identidad, límites y guardrails. Las reglas dejan de depender de implementaciones aisladas y pasan a administrarse como una capacidad común.

La tercera es **un rastro de evidencia** para uso, payloads, calidad y costo. Esto hace posible operar, auditar y mejorar los sistemas con datos.

La cuarta es **una capa de confiabilidad** para enrutamiento, fallback y selección de proveedor. Las aplicaciones pueden evolucionar y resistir fallas sin quedar completamente atadas a una única ruta.

Estas cuatro ideas se resumen en dos beneficios:

Primero, **integrar sin quedar atados a un único proveedor**. Esto no significa que cambiar de modelo sea siempre automático; cada cambio debe probarse. Significa que la arquitectura reduce el acoplamiento y conserva opciones.

Segundo, **operar con control**. La innovación continúa, pero con identidad, límites, monitoreo, evidencia y mecanismos de continuidad.

Si tuviera que resumirlo en una sola frase, diría:

‘AI Gateway permite ofrecer GenAI como una capacidad empresarial compartida, en lugar de una colección de conexiones individuales a modelos.’

El siguiente paso no debería ser habilitar todos los modelos para todos los usuarios. Debería ser seleccionar uno o dos casos de uso, definir identidades, datos permitidos, métricas, límites, fallback y criterios de calidad, y ejecutar un piloto gobernado.”

### Cierre propuesto

“Para avanzar con Central Puerto, propongo identificar un caso de uso de bajo riesgo y alto valor, y responder cinco preguntas:

1. ¿Quién utilizará la solución?
2. ¿Qué datos puede procesar y cuáles deben bloquearse o enmascararse?
3. ¿Qué modelos o proveedores están autorizados?
4. ¿Qué límites, métricas y evidencia necesitamos?
5. ¿Qué debe ocurrir ante un fallo o una respuesta de baja confianza?

Con esas respuestas podemos diseñar un piloto en el que la seguridad, el costo y la observabilidad formen parte de la arquitectura desde el principio.”

---

## Apertura breve alternativa, de 60 segundos

“La adopción de IA generativa suele comenzar con muchas conexiones directas: distintas aplicaciones, modelos, proveedores y credenciales. Ese enfoque permite experimentar rápido, pero complica seguridad, costos, auditoría y continuidad operativa. Databricks AI Gateway introduce una capa común entre las aplicaciones y los modelos. Desde allí podemos controlar quién accede, aplicar límites y guardrails, observar uso y costo, registrar evidencia y configurar rutas alternativas. No reemplaza la lógica de negocio ni los permisos de las herramientas; gobierna el tráfico de GenAI. Hoy veremos cómo esta capa ayuda a escalar la innovación sin perder control.”

## Respuestas preparadas para preguntas frecuentes

### “¿AI Gateway reemplaza una API Gateway tradicional?”

“No completamente. Comparten conceptos como autenticación, límites y enrutamiento, pero AI Gateway incorpora controles y telemetría específicos de GenAI, como tokens, payloads de prompts y respuestas, guardrails, selección de modelos y señales de calidad. Puede convivir con una API Gateway empresarial.”

### “¿Obliga a utilizar un único proveedor?”

“No. Uno de sus objetivos es ofrecer acceso gobernado a diferentes proveedores y modelos. Sin embargo, la portabilidad no es perfecta: capacidades, formatos, herramientas, calidad y comportamiento varían entre modelos, por lo que cualquier cambio o fallback debe probarse.”

### “¿Los datos siempre quedan dentro de Databricks?”

“La telemetría y los registros configurados pueden almacenarse y gobernarse en Databricks. Pero si se llama a un modelo externo, el payload se envía al proveedor correspondiente. Por eso deben revisarse contratos, residencia, retención, red y políticas del proveedor, además de aplicar redacción o bloqueo cuando corresponda.”

### “¿Los guardrails eliminan el riesgo de fuga de información?”

“No. Reducen riesgo, pero forman parte de una defensa en profundidad. También necesitamos clasificación de datos, permisos, enmascaramiento, políticas de red, contratos, capacitación, pruebas y control de las fuentes que utiliza la aplicación.”

### “¿AI Gateway controla lo que hace un agente mediante MCP?”

“Controla la llamada del agente al modelo cuando pasa por el endpoint gobernado. Las acciones MCP deben controlarse además en el servidor MCP y en el sistema de destino mediante mínimo privilegio, autenticación, autorización, validaciones y aprobaciones.”

### “¿Qué ocurre si falla el proveedor principal?”

“Puede configurarse un fallback a otro endpoint. Aun así, hay que validar compatibilidad funcional y calidad porque el modelo alternativo puede producir resultados diferentes. La conmutación técnica debe acompañarse con pruebas y observabilidad.”

### “¿Cómo ayuda con los costos?”

“Centraliza métricas de solicitudes y tokens, permite atribuir uso a aplicaciones o equipos, imponer límites y comparar modelos. Eso ayuda a detectar consumo anómalo y elegir una combinación adecuada de costo, latencia y calidad.”

### “¿También sirve para machine learning tradicional?”

“Su foco principal es el tráfico GenAI y los LLMs. Los modelos clásicos se sirven y monitorean mediante otras capacidades de Model Serving y monitoreo. Los controles deben ajustarse al tipo de modelo.”

## Recomendaciones de exposición

- No leer literalmente los diagramas densos; explicar el flujo por capas.
- Repetir la separación entre **gobierno del modelo** y **gobierno de las acciones del agente**.
- Evitar prometer que un fallback conserva exactamente la misma calidad.
- No afirmar que un guardrail garantiza cumplimiento.
- Presentar los ejemplos de Central Puerto como hipótesis para validar.
- Hacer una pausa después de las diapositivas 2, 8 y 11 para preguntas.
- Cerrar con un piloto concreto, no con una adopción masiva.
