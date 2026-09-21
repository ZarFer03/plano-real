# 04, Plano real, ejemplo
Cliente: Taller de flotillas (ejemplo inventado, sin datos de ninguna empresa)
Proceso: Alta y cierre de una orden de servicio
Fase: 2, plano real
Evidencia dominante: observado
Hallazgo: El caso espera mas de un dia sin que nadie lo trabaje, y la espera no esta en el area que todos culpan.
Casos caminados: caso A, 2026-09-18, con el jefe de patio. Caso B, 2026-09-19, con el mecanico.
| id | paso | quien | sistema | tipo | excepcion | ruta | trabajo | espera | evidencia |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Recibe la solicitud de la unidad | jefe de patio | WhatsApp | ejecuta | por dato faltante | ruta B: pide el dato al chofer | 5 min | 5 min | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 2 | Captura en la hoja de servicios | auxiliar administrativo | Excel | ejecuta | ninguna | | 12 min | 4 h | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 3 | Valida el presupuesto autorizado | jefe de patio | Excel | decide | por autorizacion | ruta D: sube a direccion | 8 min | 1 d | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 4 | Asigna unidad y mecanico | jefe de patio | pizarron | decide | por capacidad | ruta E: espera unidad libre | 10 min | 3 h | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 5 | Levanta el diagnostico en piso | mecanico | papel | ejecuta | ninguna | | 45 min | 2 h | [observado] caso B caminado con el mecanico, el 2026-09-19 |
| 6 | Cotiza refacciones | compras | correo | ejecuta | por monto | ruta C: arriba de 8 mil sube a direccion | 25 min | 6 h | [medido] 12 casos en la ventana de 3 dias, promedio 6 h de espera |
| 7 | Solicita refacciones al proveedor | compras | proveedor | ejecuta | ninguna | | 15 min | 2 d | [dicho] "el proveedor depende de si hay credito" (compras, 2026-09-19) |
| 8 | Ejecuta la reparacion | mecanico | taller | ejecuta | por sistema | ruta F: no hay refaccion alternativa | 3 h | 1 d | [observado] caso B caminado con el mecanico, el 2026-09-19 |
| 9 | Avisa al cliente | atencion a clientes | WhatsApp | ejecuta | ninguna | | 6 min | 30 min | [observado] caso A caminado con el jefe de patio, el 2026-09-18 |
| 10 | Cierra y factura | administracion | sistema contable | ejecuta | por dato faltante | ruta B: pide el dato al chofer | 20 min | 5 h | sin observar |
## Diagrama del plano
El dibujo se genera desde la tabla de arriba y no se edita a mano.
<!-- diagrama:inicio -->
```mermaid
flowchart LR
  n1["Recibe la solicitud de la unidad"]
  n2["Captura en la hoja de servicios"]
  n3{{"Valida el presupuesto autorizado"}}
  n4{{"Asigna unidad y mecanico"}}
  n5["Levanta el diagnostico en piso"]
  n6["Cotiza refacciones"]
  n7["Solicita refacciones al proveedor"]
  n8["Ejecuta la reparacion"]
  n9["Avisa al cliente"]
  n10["Cierra y factura"]
  n1 -->|Excel| n2
  n2 -->|Excel| n3
  n3 -->|pizarron| n4
  n4 -->|papel| n5
  n5 -->|correo| n6
  n6 -->|proveedor| n7
  n7 -->|taller| n8
  n8 -->|WhatsApp| n9
  n9 -->|sistema contable| n10
  subgraph rutas de excepcion
    direction TB
    e1["por dato faltante: Recibe la solicitud de la unidad"]
    n1 -.-> e1
    e3["por autorizacion: Valida el presupuesto autorizado"]
    n3 -.-> e3
    e4["por capacidad: Asigna unidad y mecanico"]
    n4 -.-> e4
    e6["por monto: Cotiza refacciones"]
    n6 -.-> e6
    e8["por sistema: Ejecuta la reparacion"]
    n8 -.-> e8
    e10["por dato faltante: Cierra y factura"]
    n10 -.-> e10
  end
```
<!-- diagrama:fin -->
