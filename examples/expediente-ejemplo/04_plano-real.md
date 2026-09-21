# 04, Plano real, ejemplo
Cliente: Taller de flotillas (ejemplo inventado, sin datos de ninguna empresa)
Proceso: Alta y cierre de una orden de servicio
Fase: 2, plano real
Evidencia dominante: observado
Hallazgo: El caso espera mas de un dia sin que nadie lo trabaje, y la espera no esta en el area que todos culpan.
Casos caminados: caso A, 2026-09-18, con el jefe de patio. Caso B, 2026-09-19, con el mecanico.
| id | paso | quien | sistema | forma | tipo | excepcion | ruta | trabajo | espera | evidencia |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Recibe la solicitud de la unidad | jefe de patio | WhatsApp | datos | ejecuta | por dato faltante | ruta B: pide el dato al chofer | 5 min | 5 min | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 2 | Captura en la hoja de servicios | auxiliar administrativo | Excel | documento | ejecuta | ninguna | | 12 min | 4 h | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 3 | Valida el presupuesto autorizado | jefe de patio | Excel | decision | decide | por autorizacion | ruta D: sube a direccion | 8 min | 1 d | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 4 | Asigna unidad y mecanico | jefe de patio | pizarron | decision | decide | por capacidad | ruta E: espera unidad libre | 10 min | 3 h | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 5 | Levanta el diagnostico tecnico | mecanico | papel | documento | ejecuta | ninguna | | 45 min | 2 h | [observado] caso B caminado con el mecanico, el 2026-09-19 |
| 6 | Cotiza refacciones | compras | correo | documento | ejecuta | por monto | ruta C: arriba de 8 mil sube a direccion | 25 min | 6 h | [medido] 12 casos en la ventana de 3 dias, promedio 6 h de espera |
| 7 | Solicita refacciones al proveedor | compras | proveedor | datos | ejecuta | ninguna | | 15 min | 2 d | [dicho] "el proveedor depende de si hay credito" (compras, 2026-09-19) |
| 8 | Ejecuta la reparacion | mecanico | taller | actividad | ejecuta | por sistema | ruta F: no hay refaccion alternativa | 3 h | 1 d | [observado] caso B caminado con el mecanico, el 2026-09-19 |
| 9 | Avisa al cliente | atencion a clientes | WhatsApp | datos | ejecuta | ninguna | | 6 min | 30 min | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 10 | Cierra y factura | administracion | sistema contable | base-de-datos | ejecuta | por dato faltante | ruta B: pide el dato al chofer | 20 min | 5 h | sin observar |
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
    e5["por monto: ruta C: arriba de 8 mil sube a direccion"]
    n5 -.-> e5
    e7["por sistema: ruta F: no hay refaccion alternativa"]
    n7 -.-> e7
    e9["por dato faltante: ruta B: pide el dato al chofer"]
    n9 -.-> e9
  end
```
<!-- diagrama:fin -->
