import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("initialize_board_pack.py")
SPEC = importlib.util.spec_from_file_location("initialize_board_pack", SCRIPT_PATH)
initialize_board_pack = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(initialize_board_pack)


class InitializeBoardPackTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name) / "demo_boards"
        self.repo_root.mkdir()
        board_dir = self.repo_root / "example_board"
        board_dir.mkdir()
        (board_dir / "board_info.yaml").write_text(
            "board: example_board\nchip: esp32s3\n", encoding="utf-8"
        )
        self._write_template_files()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_template_files(self):
        for filename in ("README.md", "README_CN.md"):
            (self.repo_root / filename).write_text(
                "\n".join(
                    [
                        "# YOUR_VENDOR_NAME",
                        "YOUR_VENDOR_NAME: YOUR_NAMESPACE/YOUR_COMPONENT_NAME",
                        "<!-- BEGIN SUPPORTED_BOARDS -->",
                        "<!-- END SUPPORTED_BOARDS -->",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
        (self.repo_root / "idf_component.yml").write_text(
            'version: "0.7.0"\ndescription: "Board definitions for ESP Board Manager"\n',
            encoding="utf-8",
        )
        (self.repo_root / "LICENSE").write_text(
            "Copyright 2026 CHANGE_ME\n", encoding="utf-8"
        )
        workflow = self.repo_root / ".github" / "workflows"
        workflow.mkdir(parents=True)
        (workflow / "ci.yml").write_text(
            '\n'.join(
                [
                    '--namespace "${{ github.repository_owner }}"',
                    '--name "${{ github.event.repository.name }}"',
                    '',
                ]
            ),
            encoding="utf-8",
        )

    def test_collects_bilingual_prompts_and_applies_entered_metadata(self):
        answers = iter(["Acme", "", "acme_board_pack", "", ""])
        prompts = []

        def input_fn(prompt):
            prompts.append(prompt)
            return next(answers)

        config = initialize_board_pack.collect_config(
            self.repo_root, input_fn=input_fn, default_namespace="acme"
        )
        initialize_board_pack.apply_config(self.repo_root, config)

        self.assertEqual(config.vendor_name, "Acme")
        self.assertEqual(config.namespace, "acme")
        self.assertEqual(config.component_name, "acme_board_pack")
        self.assertEqual(
            config.description,
            "ESP Board Manager board definitions for Acme development boards",
        )
        self.assertEqual(config.copyright_holder, "Acme")
        self.assertIn("厂商名称 / Vendor name", prompts[0])
        self.assertIn("组件命名空间 / Component namespace", prompts[1])
        self.assertIn("组件名 / Component name", prompts[2])
        self.assertIn(
            "Acme: acme/acme_board_pack",
            (self.repo_root / "README.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            'description: "ESP Board Manager board definitions for Acme development boards"',
            (self.repo_root / "idf_component.yml").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "Copyright 2026 Acme",
            (self.repo_root / "LICENSE").read_text(encoding="utf-8"),
        )
        self.assertIn(
            '--name "acme_board_pack"',
            (self.repo_root / ".github" / "workflows" / "ci.yml").read_text(
                encoding="utf-8"
            ),
        )
        self.assertIn(
            '--namespace "${{ github.repository_owner }}"',
            (self.repo_root / ".github" / "workflows" / "ci.yml").read_text(
                encoding="utf-8"
            ),
        )

    def test_uses_a_fixed_namespace_when_it_differs_from_repository_owner(self):
        answers = iter(["Acme", "vendor_namespace", "", "", ""])

        config = initialize_board_pack.collect_config(
            self.repo_root,
            input_fn=lambda _prompt: next(answers),
            default_namespace="acme",
        )
        initialize_board_pack.apply_config(self.repo_root, config)

        self.assertIn(
            '--namespace "vendor_namespace"',
            (self.repo_root / ".github" / "workflows" / "ci.yml").read_text(
                encoding="utf-8"
            ),
        )
