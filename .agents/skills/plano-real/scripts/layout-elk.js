// Acomodo del plano con ELK (Eclipse Layout Kernel).
// Uso: node layout-elk.js entrada.json salida.json
// Entrada: grafo en el formato de ELK. Salida: posiciones de nodos, rutas y etiquetas.
// Si no encuentra elkjs, sale con codigo 3 para que el generador sepa que debe instalarlo.
const fs = require("fs");

let ELK = null;
for (const candidato of ["elkjs/lib/elk.bundled.js", "elkjs", process.env.ELK_JS || ""]) {
  if (!candidato) continue;
  try {
    ELK = require(candidato);
    break;
  } catch (e) {
    /* siguiente candidato */
  }
}
if (!ELK) {
  console.error("no encontre elkjs");
  process.exit(3);
}

const [, , rutaEntrada, rutaSalida] = process.argv;
const grafo = JSON.parse(fs.readFileSync(rutaEntrada, "utf8"));

new ELK()
  .layout(grafo)
  .then((g) => {
    const nodos = {};
    for (const c of g.children || []) nodos[c.id] = { x: c.x, y: c.y, w: c.width, h: c.height };
    const rutas = [];
    for (const e of g.edges || []) {
      const secciones = [];
      for (const s of e.sections || []) {
        const puntos = [s.startPoint, ...(s.bendPoints || []), s.endPoint].filter(Boolean);
        secciones.push(puntos.map((p) => [p.x, p.y]));
      }
      const l = (e.labels || [])[0];
      rutas.push({
        id: e.id,
        desde: e.sources[0],
        hacia: e.targets[0],
        secciones,
        etiqueta: l ? { x: l.x, y: l.y, w: l.width, h: l.height } : null,
      });
    }
    fs.writeFileSync(rutaSalida, JSON.stringify({ ancho: g.width, alto: g.height, nodos, rutas }), "utf8");
    console.log("elk: " + g.children.length + " nodos, " + (g.edges || []).length + " rutas");
  })
  .catch((err) => {
    console.error("elk fallo: " + err.message);
    process.exit(4);
  });
