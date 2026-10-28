# Fases 0 y 1, arranque y entrevistas
## Objetivo
Acordar el trabajo con quien autoriza y reconstruir casos con quien los ejecuta, sin confundir alcance comercial con observación operativa.
## Qué necesita para empezar
Leer [las convenciones](00-convenciones.md). Para fase 0: cliente, proceso candidato, interlocutor y destino resueltos. No exigir alcance aprobado para redactar su borrador. Para fase 1: alcance aprobado, responsables, permiso del cliente y de las personas, y acceso autorizado a los casos.
## Pasos de trabajo
1. Recuperar los campos del alcance ya conocidos y preguntar solo los pendientes con el banco de arranque. **Termina cuando:** cada campo está confirmado o tiene pendiente y responsable, y el alcance está listo para aprobación.
2. Registrar responsables y obtener la aprobación y permisos antes de entrevistar. **Termina cuando:** se puede identificar qué proceso y personas están autorizados para el levantamiento.
3. Conducir las entrevistas con casos y registrar citas, excepciones y contradicciones. **Termina cuando:** hay un caso caminado de punta a punta con recibo y las contradicciones no resueltas están visibles.
Dos trabajos distintos: arrancar el expediente con el alcance, y sacar de la gente lo que solo ella sabe. El primero es con quien firma, el segundo es con quien ejecuta.
### Arranque, las ocho preguntas del alcance
Una por turno, cada una con hipótesis de trabajo. Las decisiones son del usuario o del cliente; los hechos se buscan en archivos antes de preguntarlos.
1. **Qué proceso.** Un proceso, no la empresa. Hipótesis: el que más duele y el que más gente necesita. Si traen tres, se pregunta cuál duele más y por qué ese.
2. **Para qué lo quieren.** Qué van a hacer con el plano: automatizar, delegar, abrir sucursal, dejar de depender de alguien. Sin esto, el criterio de éxito se inventa.
3. **Quién es quién.** El que decide, el que firma el cheque, el que ejecuta el proceso, el que autoriza excepciones, y los que no van a querer que esto pase.
4. **Qué se intentó antes.** Software comprado, consultoría, proyecto interno, y en qué quedó. Pregunta obligatoria: ¿sigue en uso?
5. **Dónde vive el trabajo hoy.** Los sistemas, los archivos y las cabezas. Se pide la lista, no la descripción.
6. **Accesos y evidencia.** Qué registros se pueden ver: pedidos, expedientes, bitácoras, exportaciones, capturas. Sin esto no hay línea base, solo opiniones.
7. **Calendario y disponibilidad.** Las tres semanas, quién está disponible cuándo, y qué fechas no se pueden tocar.
8. **Confidencialidad.** Qué no se puede ver, qué no se puede nombrar, quién revisa antes de compartir, y qué se puede usar como caso anónimo después.
Al cerrar, escribir `00_AGENT_BRIEF.md` y `01_alcance.md` con lo confirmado, lo pendiente y las reglas para razonar. Todo `dicho` hasta que exista recibo de otra clase.
### Entrevistas, las siete reglas de conducción
1. **Una pregunta por turno.** Un cuestionario en bloque produce respuestas diluidas.
2. **Cada pregunta con hipótesis.** "Mi hipótesis es que esto se atora aquí porque nadie sabe quién sigue. ¿Es así o me equivoco?" Corregir es más rápido que redactar.
3. **Se pide el caso, no la opinión.** La pregunta madre: "no me digas cómo funciona, dime el último caso que atendiste y qué pasó". El proceso se reconstruye con casos, nunca con descripciones.
4. **Se persigue la excepción.** Después de cada paso: "¿y cuando no es así?", "¿y la última vez que se atoró?", "¿y qué pasó cuando no estaba el que sabe?". Ahí vive el trabajo real y el rediseño.
5. **Hechos se buscan, decisiones se preguntan.** Lo que está en un archivo no se pregunta: se revisa antes y se llega con el dato.
6. **No se corrige a la persona en el momento.** Se anota y se sigue. Corregir en la entrevista cierra el flujo de información.
7. **Se registra la cita textual.** Cada hallazgo sale con quién lo dijo, su puesto, cuándo y dónde. Sin eso, es `dicho` sin recibo y no sirve para nada más.
### A quién se entrevista, y qué da cada uno
| Rol | Qué da | Qué no se le pide |
|---|---|---|
| El que ejecuta | los pasos reales, las excepciones, los rodeos, los atajos | la intención del negocio |
| El jefe de área | los criterios, los números del área, las decisiones que autoriza | los pasos finos: los cuenta de memoria y los cuenta mal |
| El dueño o dirección | la intención, la prioridad, el límite de inversión | la descripción del trabajo: tiene tolerancia al desorden y describe lo que quiere, no lo que pasa |
| El que revisa o autoriza | los umbrales, los retrabajos que ve, lo que regresa | lo que él no toca |
| Ventas o atención | por qué un caso se atora antes de entrar, las promesas que se hacen | el proceso interno que no vive |
Se entrevista también por lo que se fue: si alguien clave renunció, se pregunta qué se fue con él y qué rodeo se inventó el equipo después. Ese rodeo suele ser el proceso nuevo, mal documentado.
### Bancos de preguntas
#### A. El caso real, de punta a punta (el banco principal)
1. ¿Cuál fue el último caso de este tipo? Fecha exacta, no aproximada.
2. ¿Cómo entró? ¿Quién lo recibió y por dónde llegó?
3. ¿Qué fue lo primero que se hizo con él?
4. ¿Dónde se registró y con qué datos?
5. ¿Quién lo tocó después y qué le hizo?
6. ¿Cuánto esperó entre un paso y el siguiente? ¿Quién lo empujó?
7. ¿En qué momento se decidió algo, quién decidió y con qué información?
8. ¿Algo se devolvió o se rehizo? ¿Por qué?
9. ¿Cómo supieron que ya estaba terminado? ¿Quién avisó a quién?
10. ¿Qué se anotó en algún lado, y dónde está eso hoy?
11. Si el cliente pregunta hoy en qué va, ¿cómo se contesta y en cuánto tiempo?
#### B. Excepciones
¿Qué es lo que casi nunca pasa pero pasa? ¿Cuál fue la última vez que el sistema no aguantó? ¿Qué haces cuando el dato no está? ¿Quién puede autorizar esto y hasta cuánto? ¿Qué pasa si llega a las 7 de la tarde? ¿Qué haces el día que no está la persona que sabe?
#### C. Sistemas y datos
¿Dónde vive la información de un caso, en cuántos lugares, y cuál es la verdad? ¿Qué se copia a mano de un lado a otro? ¿Qué se pierde entre uno y otro? ¿Qué exporta el sistema y qué solo muestra en pantalla? ¿Quién puede verlo y quién no?
#### D. Decisiones y criterios
¿Qué decisiones de este proceso solo puedes tomar tú? ¿Cómo sabes que un caso es normal o es problema? ¿Qué te hace devolver un caso? ¿Qué está escrito y qué vive en tu cabeza? ¿A quién le preguntas cuando no sabes?
#### E. Costo y volumen
¿Cuántos casos al mes? ¿Cuántas personas tocan un caso? ¿Cuántas horas a la semana se va esta gente en esto? ¿Qué pasa los viernes? Todo lo que se conteste aquí se anota como `dicho` y se busca el registro para subirlo a `medido`: volumen y costo nunca se cierran con una respuesta de memoria.
#### F. La pregunta de cierre obligatoria
Se hace al final de cada entrevista, sin excepción: **"si mañana no vienes a trabajar, ¿qué se cae primero?"** Y después: "¿y por qué eso?"
## Si falta evidencia
Faltan permisos: detener entrevistas. Falta un caso o una fuente: anotar qué se requiere, quién lo tiene y qué parte del levantamiento bloquea. Las contradicciones se conservan hasta caminar el caso; no elegir la versión cómoda.
## Archivos que produce o actualiza
Actualizar `00_AGENT_BRIEF.md`, `01_alcance.md`, `02_quien-es-quien.md` y las notas en `03_entrevistas/`. Guardar los registros recibidos en `fuentes/`.
Cada entrevista produce una nota en `03_entrevistas/AAAA-MM-DD-puesto.md` con: quién, puesto, fecha y dónde se hizo; los casos reales mencionados con sus fechas; los hallazgos, cada uno con su clase de evidencia y su cita textual; las excepciones que aparecieron con la familia a la que pertenecen; los pendientes con nombre de quién los tiene; y el dato que se pidió y no se pudo dar.
Al terminar todas las entrevistas se comparan entre sí, y las contradicciones no se resuelven eligiendo la versión cómoda: se llevan juntas al expediente y se cierran caminando el caso.
## Termina cuando
Para fase 0: el alcance y los permisos están aprobados y los responsables identificados; auditar con fase 0. Para cerrar fase 1 y pasar al plano, deben cumplirse todos los puntos siguientes y auditar con fase 1:
- Hay al menos un caso real elegido y caminado, con fecha y quién lo ejecutó.
- Existen los ocho campos del alcance, con sus huecos marcados como pendientes.
- Hay al menos una excepción contada en cada familia que aplique al proceso.
- El brief del expediente refleja el estado real.
- La auditoría del expediente sale en cero.
## Entrega al siguiente paso
Entregar a fase 2 casos identificados, entrevistas con recibos, excepciones y contradicciones pendientes con responsable. No repetir preguntas ya resueltas.
Actualizar el brief y cerrar en el chat con resultado, sustento, archivo, pendiente y siguiente movimiento según [la guía principal](../SKILL.md).
