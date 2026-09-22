import importlib.util
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/plano-real/scripts/generar-diagrama.py"
FIXTURE = ROOT / "examples/expediente-ejemplo/04_plano-real.md"

spec = importlib.util.spec_from_file_location("generar_diagrama", SCRIPT)
assert spec is not None and spec.loader is not None
gen = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gen
spec.loader.exec_module(gen)


class LayoutTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        meta, tablas = gen.leer_secciones(FIXTURE.read_text(encoding="utf-8"))
        cls.nodos, cls.rutas = gen.grafo(meta, tablas)
        cls.tmp = tempfile.TemporaryDirectory(prefix="plano-real-test-")
        cls.ac, cls.motor, cls.aviso = gen.acomodo_con_motor(
            cls.nodos, cls.rutas, "iso5807", pathlib.Path(cls.tmp.name)
        )
        if cls.ac is None:
            cls.ac = gen.acomodo_interno(cls.nodos, cls.rutas, "iso5807")

    def test_every_node_has_separate_title_lines_and_metadata(self):
        for node in self.nodos:
            node_id = node["id"]
            x, y, width, height = self.ac["nodos"][node_id]
            shape = gen.resolver_forma(node["fila"], "iso5807")
            lines = gen.wrap(
                gen.etiqueta_nodo(node, node_id),
                gen.FORMAS.get(shape, gen.FORMAS["actividad"])[3],
            )
            title_y, metadata_y = gen.posiciones_texto(
                shape, y, height, lines, gen.renglon_chico(node)
            )
            self.assertEqual(len(title_y), len(set(title_y)), node_id)
            self.assertTrue(all(b - a >= 12 for a, b in zip(title_y, title_y[1:])), node_id)
            if metadata_y is not None:
                self.assertGreaterEqual(metadata_y - title_y[-1], 10, node_id)
            self.assertGreaterEqual(min(title_y), y + 6, node_id)
            self.assertLessEqual(max(title_y), y + height - 4, node_id)

    def test_decisions_have_real_branches(self):
        decisions = [
            n["id"] for n in self.nodos
            if gen.resolver_forma(n["fila"], "iso5807") == "decision"
        ]
        for node_id in decisions:
            outgoing = [r for r in self.rutas if r["desde"] == node_id]
            self.assertGreaterEqual(len(outgoing), 2, node_id)
            self.assertTrue(all(r["etiqueta"] for r in outgoing), node_id)

    def test_layout_has_no_shape_or_route_crossings(self):
        cajas = [
            (x, y, w, h, node_id)
            for node_id, (x, y, w, h) in self.ac["nodos"].items()
        ]
        self.assertEqual(gen.choques(cajas), [])
        self.assertEqual(gen.cruces(self.ac), [])
        self.assertEqual(gen.problemas_texto(self.nodos, self.ac, "iso5807"), [])
        self.assertEqual(gen.problemas_etiquetas(self.ac), [])

    def test_approval_cannot_make_a_node_verified(self):
        for receipt in ('[firmado] plano revisado por responsable', '[aprobado] plano',
                        '[dicho] "observado por el jefe"', 'no observado'):
            with self.subTest(receipt=receipt):
                self.assertNotIn(gen.clase_evidencia(receipt), gen.SOLIDA)
        self.assertIn(gen.clase_evidencia('[observado] caso T'), gen.SOLIDA)
        self.assertIn(gen.clase_evidencia('[medido] tiempo'), gen.SOLIDA)


if __name__ == "__main__":
    unittest.main()
