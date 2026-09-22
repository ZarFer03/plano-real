"""Contrato estructural; no simula la conducta de un agente ni valida un cliente."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / '.agents/skills/plano-real'
PHASES = ('01-arranque-y-entrevistas.md', '02-plano-real.md',
          '03-medicion-y-prioridad.md', '04-rediseno-y-prueba.md', '05-sostener.md')


class ConduccionTests(unittest.TestCase):
    def test_main_is_an_execution_guide(self):
        text = (SKILL / 'SKILL.md').read_text()
        for heading in ('## Cuándo usar', '## Paso 0: Localizar y evaluar el expediente',
                        '## Paso 1: Precisar la decisión y el alcance',
                        '## Paso 2: Ejecutar la fase correspondiente',
                        '## Paso 3: Verificar el resultado',
                        '## Paso 4: Archivar y entregar', '## Límites y errores que evitar'):
            self.assertIn(heading, text)
        self.assertGreaterEqual(text.count('**Termina cuando:**'), 5)
        self.assertIn('reanudación', text)
        self.assertIn('--fase N', text)
        self.assertNotIn('/home/', text)

    def test_each_phase_has_a_complete_execution_contract(self):
        for filename in PHASES:
            with self.subTest(phase=filename):
                text = (SKILL / 'references' / filename).read_text()
                for heading in ('## Objetivo', '## Qué necesita para empezar',
                                '## Pasos de trabajo', '## Si falta evidencia',
                                '## Archivos que produce o actualiza', '## Termina cuando',
                                '## Entrega al siguiente paso'):
                    self.assertIn(heading, text)
                self.assertIn('**Termina cuando:**', text)
                self.assertEqual([x for x in text.splitlines() if x.startswith('## ')], [
                    '## Objetivo', '## Qué necesita para empezar', '## Pasos de trabajo',
                    '## Si falta evidencia', '## Archivos que produce o actualiza',
                    '## Termina cuando', '## Entrega al siguiente paso'])

    def test_baseline_closure_requires_current_approval(self):
        text = (SKILL / 'references/03-medicion-y-prioridad.md').read_text()
        closure = text.split('## Termina cuando\n', 1)[1].split('## Entrega', 1)[0]
        self.assertIn('[aprobado]', closure)
        self.assertIn('versión vigente', closure)
        self.assertNotIn('o queda anotado', closure)

    def test_local_markdown_links_resolve(self):
        files = [SKILL / 'SKILL.md'] + list((SKILL / 'references').glob('*.md'))
        for path in files:
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if link.startswith(('http:', 'https:', '#', 'mailto:')):
                    continue
                with self.subTest(file=path.name, link=link):
                    self.assertTrue((path.parent / link.split('#')[0]).exists())


if __name__ == '__main__':
    unittest.main()
