"""Regresiones CLI; los expedientes temporales son fixtures sintéticos."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.agents/skills/plano-real/scripts/auditar-expediente.py'


class AuditorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='plano-audit-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        for name in ('00_AGENT_BRIEF.md', '01_alcance.md'):
            (self.root / name).write_text('# Fixture sintético\n', encoding='utf-8')

    def run_audit(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.root), *args],
                              capture_output=True, text=True)

    def test_phase_must_be_explicit_and_in_range(self):
        for args in ((), ('--fase', '99'), ('--fase', '-1'),
                     ('--fase', 'x'), ('--fase',), ('--fase', '0', '--typo')):
            with self.subTest(args=args):
                result = self.run_audit(*args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertNotIn('EXPEDIENTE OK', result.stdout)

    def test_later_phase_requires_previous_files(self):
        (self.root / '09_custodia.md').write_text(
            '[observado] caso TEST caminado con operador, el 2026-09-18\n', encoding='utf-8')
        result = self.run_audit('--fase', '5')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('05_linea-base.md', result.stdout)
        self.assertIn('03_entrevistas/', result.stdout)

    def test_receipts_require_fields_not_only_tags(self):
        invalid = ('[observado]', '[observado] caso T el 2026-09-18',
                   '[observado] caso T con operador, el 2026-02-30',
                   '[dicho] "dato" ()', '[firmado] aprobado',
                   '[medido] 3 casos',
                   '[medido] tiempo con método suma: 1 + 2 = 3 (fuente: no-existe.csv)')
        for text in invalid:
            with self.subTest(text=text):
                (self.root / '01_alcance.md').write_text(text + '\n', encoding='utf-8')
                result = self.run_audit('--fase', '0')
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('recibo_invalido', result.stdout)

    def test_valid_receipts_pass(self):
        (self.root / 'datos.csv').write_text('valor\n1\n2\n', encoding='utf-8')
        text = ('[observado] caso T caminado con operador, el 2026-09-18\n'
                '[dicho] "dato" (persona, puesto, 2026-09-18, oficina)\n'
                '[firmado] alcance revisado por responsable el 2026-09-18\n'
                '[medido] tiempo con método suma: 1 + 2 = 3 (fuente: datos.csv)\n')
        (self.root / '01_alcance.md').write_text(text, encoding='utf-8')
        result = self.run_audit('--fase', '0')
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_receipt_sources_must_be_relative_to_document(self):
        receipt_file = self.root / 'recibo.txt'
        receipt_file.write_text('Fixture sintético\n', encoding='utf-8')
        for kind, prefix in (
            ('medido', 'tiempo con método suma: 1 + 2 = 3'),
            ('aprobado', 'alcance versión v1 aprobado por responsable el 2026-09-18'),
        ):
            for source, expected in ((str(receipt_file), 1), ('recibo.txt', 0)):
                with self.subTest(kind=kind, source=source):
                    (self.root / '01_alcance.md').write_text(
                        f'[{kind}] {prefix} (fuente: {source})\n', encoding='utf-8')
                    result = self.run_audit('--fase', '0')
                    self.assertEqual(result.returncode, expected, result.stdout)

    def test_style_is_warning_not_evidence_failure(self):
        (self.root / '01_alcance.md').write_text('# Alcance\n\nTexto — estilo.\n', encoding='utf-8')
        result = self.run_audit('--fase', '0')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('linea_en_blanco', result.stdout)
        self.assertIn('guion_largo', result.stdout)

    def test_legacy_signature_is_not_evidence(self):
        (self.root / '01_alcance.md').write_text(
            '[firmado] alcance revisado por responsable el 2026-09-18\n', encoding='utf-8')
        result = self.run_audit('--fase', '0')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('firma_legacy', result.stdout)
        self.assertIn('sin_evidencia', result.stdout)
        evidence_line = next(x for x in result.stdout.splitlines() if x.startswith('Evidencia:'))
        self.assertNotIn('firmado', evidence_line)

    def test_approval_needs_version_author_date_and_local_receipt(self):
        (self.root / 'acta.txt').write_text('Fixture sintético de aprobación\n', encoding='utf-8')
        valid = 'alcance versión v1 aprobado por responsable el 2026-09-18 (fuente: acta.txt)'
        invalid = ('', valid.replace(' versión v1', ''), valid.replace('responsable', ''),
                   valid.replace('2026-09-18', '2026-02-30'), valid.replace('acta.txt', 'ausente.txt'))
        for receipt in invalid:
            with self.subTest(receipt=receipt):
                (self.root / '01_alcance.md').write_text('[aprobado] ' + receipt + '\n', encoding='utf-8')
                result = self.run_audit('--fase', '0')
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('recibo_invalido', result.stdout)
        (self.root / '01_alcance.md').write_text('[aprobado] ' + valid + '\n', encoding='utf-8')
        result = self.run_audit('--fase', '0')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('sin_evidencia', result.stdout)


if __name__ == '__main__':
    unittest.main()
