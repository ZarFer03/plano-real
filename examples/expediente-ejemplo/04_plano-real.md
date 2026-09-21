# 04, Plano real, ejemplo
Cliente: Taller de flotillas (ejemplo inventado, sin datos de ninguna empresa)
Proceso: Alta y cierre de una orden de servicio
Fase: 2, plano real
Evidencia dominante: observado
Hallazgo: El caso espera mas de un dia sin que nadie lo trabaje, y la espera no esta en el area que todos culpan.
Entradas: solicitud del chofer por WhatsApp, unidad disponible, presupuesto del area
Salidas: orden de servicio cerrada, unidad reparada, factura emitida
Secuencia: recibe el jefe de patio, captura el auxiliar, autoriza y asigna el jefe de patio, ejecuta el mecanico, cotiza y compra compras, avisa atencion a clientes, cierra administracion
Criterios: autorizacion del jefe de patio hasta 8 mil pesos, arriba de eso direccion, refaccion por proveedor unico
Recursos: pizarron de patio, hoja de servicios en Excel, sistema contable, proveedor de refacciones
Responsables: jefe de patio es dueno del proceso, direccion autoriza el gasto mayor, administracion cierra y factura
Riesgos: caso sin responsable mientras espera refaccion, presupuesto autorizado sin registro, dato de la unidad capturado a mano
Mejora: se cuenta el mismo metodo cada trimestre y se compara contra la linea base
Casos caminados: caso A, 2026-09-18, con el jefe de patio. Caso B, 2026-09-19, con el mecanico.
| id | paso | quien | sistema | forma | tipo | condicion | excepcion | ruta | regreso | trabajo | espera | evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Recibe la solicitud de la unidad | jefe de patio | WhatsApp | datos | ejecuta | falta un dato | por dato faltante | ruta B: pide el dato al chofer | 1 | 5 min | 5 min | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 2 | Captura en la hoja de servicios | auxiliar administrativo | Excel | documento | ejecuta | | ninguna | | | 12 min | 4 h | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 3 | Valida el presupuesto autorizado | jefe de patio | Excel | decision | decide | no autorizado | por autorizacion | ruta D: sube a direccion | 3 | 8 min | 1 d | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 4 | Asigna unidad y mecanico | jefe de patio | pizarron | decision | decide | no hay unidad libre | por capacidad | ruta E: espera unidad libre | 4 | 10 min | 3 h | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 5 | Levanta el diagnostico tecnico | mecanico | papel | documento | ejecuta | | ninguna | | | 45 min | 2 h | [observado] caso B caminado con el mecanico, el 2026-09-19 |
| 6 | Cotiza refacciones | compras | correo | documento | ejecuta | arriba de 8 mil | por monto | ruta C: sube a direccion | 6 | 25 min | 6 h | [medido] 12 casos en la ventana de 3 dias, promedio 6 h de espera |
| 7 | Solicita refacciones al proveedor | compras | proveedor | datos | ejecuta | | ninguna | | | 15 min | 2 d | [dicho] "el proveedor depende de si hay credito" (compras, 2026-09-19) |
| 8 | Ejecuta la reparacion | mecanico | taller | actividad | ejecuta | falta refaccion | por sistema | ruta F: no hay refaccion alternativa | 8 | 3 h | 1 d | [observado] caso B caminado con el mecanico, el 2026-09-19 |
| 9 | Avisa al cliente | atencion a clientes | WhatsApp | datos | ejecuta | | ninguna | | | 6 min | 30 min | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 10 | Cierra y factura | administracion | sistema contable | base-de-datos | ejecuta | falta un dato | por dato faltante | ruta B: pide el dato al chofer | 1 | 20 min | 5 h | sin observar |
## Diagrama del plano
El dibujo se genera desde la tabla de arriba y no se edita a mano.
<!-- diagrama:inicio -->
```mermaid
flowchart TB
  w0(("espera 5 min"))
  n0[/"Recibe la solicitud de la unidad"/]
  w1(("espera 4 h"))
  n1[/"Captura en la hoja de servicios"\]
  w2(("espera 1 d"))
  n2{"Valida el presupuesto autorizado"}
  w3(("espera 3 h"))
  n3{"Asigna unidad y mecanico"}
  w4(("espera 2 h"))
  n4[/"Levanta el diagnostico tecnico"\]
  w5(("espera 6 h"))
  n5[/"Cotiza refacciones"\]
  w6(("espera 2 d"))
  n6[/"Solicita refacciones al proveedor"/]
  w7(("espera 1 d"))
  n7["Ejecuta la reparacion"]
  w8(("espera 30 min"))
  n8[/"Avisa al cliente"/]
  w9(("espera 5 h"))
  n9[("Cierra y factura")]
  w0 --> n0
  n0 --> w1
  w1 --> n1
  n1 --> w2
  w2 --> n2
  n2 --> w3
  w3 --> n3
  n3 --> w4
  w4 --> n4
  n4 --> w5
  w5 --> n5
  n5 --> w6
  w6 --> n6
  n6 --> w7
  w7 --> n7
  n7 --> w8
  w8 --> n8
  n8 --> w9
  w9 --> n9
  subgraph rutas de excepcion
    direction TB
    e0["por dato faltante: ruta B: pide el dato al chofer"]
    n0 -.-> e0
    e2["por autorizacion: ruta D: sube a direccion"]
    n2 -.-> e2
    e3["por capacidad: ruta E: espera unidad libre"]
    n3 -.-> e3
    e5["por monto: ruta C: sube a direccion"]
    n5 -.-> e5
    e7["por sistema: ruta F: no hay refaccion alternativa"]
    n7 -.-> e7
    e9["por dato faltante: ruta B: pide el dato al chofer"]
    n9 -.-> e9
  end
```
<!-- diagrama:fin -->
