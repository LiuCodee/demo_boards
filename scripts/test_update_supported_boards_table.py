import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("update_supported_boards_table.py")
SPEC = importlib.util.spec_from_file_location("update_supported_boards_table", SCRIPT_PATH)
update_supported_boards_table = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(update_supported_boards_table)


class UpdateSupportedBoardsTableTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _add_board(self, relative_dir: str, board: str, chip: str):
        board_dir = self.repo_root / relative_dir
        board_dir.mkdir(parents=True)
        (board_dir / "board_info.yaml").write_text(
            f"board: {board}\nchip: {chip}\n", encoding="utf-8"
        )

    def test_updates_board_and_chip_columns_and_preserves_manual_details(self):
        self._add_board("audio/speaker_board", "speaker_board", "esp32s3")
        self._add_board("display/round/screen_board", "screen_board", "esp32p4")
        readme = self.repo_root / "README.md"
        readme.write_text(
            "\n".join(
                [
                    "# Boards",
                    "<!-- BEGIN SUPPORTED_BOARDS -->",
                    "| Board | Chip | Audio | SD Card | LCD | LCD Touch | Camera | Buttons | LED Strip | Knob |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| `speaker_board` | ESP32-S3 | ES8311 | | | | | | | |",
                    "<!-- END SUPPORTED_BOARDS -->",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        update_supported_boards_table.update_readme(readme, self.repo_root, "en")

        self.assertEqual(
            readme.read_text(encoding="utf-8"),
            "\n".join(
                [
                    "# Boards",
                    "<!-- BEGIN SUPPORTED_BOARDS -->",
                    "| Board | Chip | Audio | SD Card | LCD | LCD Touch | Camera | Buttons | LED Strip | Knob |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| `speaker_board` | ESP32-S3 | ES8311 | | | | | | | |",
                    "| `screen_board` | ESP32-P4 | | | | | | | | |",
                    "<!-- END SUPPORTED_BOARDS -->",
                    "",
                ]
            ),
        )

    def test_preserves_existing_rows_and_appends_new_boards(self):
        self._add_board("existing_board", "existing_board", "esp32s3")
        self._add_board("1/new_board", "new_board", "esp32c6")
        readme = self.repo_root / "README.md"
        readme.write_text(
            "\n".join(
                [
                    "# Boards",
                    "<!-- BEGIN SUPPORTED_BOARDS -->",
                    "| Board | Chip | Audio | SD Card | LCD | LCD Touch | Camera | Buttons | LED Strip | Knob |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| `existing_board` | ESP32 | ES8311 | | | | | | | |",
                    "| `manual_board` | ESP32-H2 | | | | | | | | |",
                    "<!-- END SUPPORTED_BOARDS -->",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        update_supported_boards_table.update_readme(readme, self.repo_root, "en")

        self.assertEqual(
            readme.read_text(encoding="utf-8"),
            "\n".join(
                [
                    "# Boards",
                    "<!-- BEGIN SUPPORTED_BOARDS -->",
                    "| Board | Chip | Audio | SD Card | LCD | LCD Touch | Camera | Buttons | LED Strip | Knob |",
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| `existing_board` | ESP32 | ES8311 | | | | | | | |",
                    "| `manual_board` | ESP32-H2 | | | | | | | | |",
                    "| `new_board` | ESP32-C6 | | | | | | | | |",
                    "<!-- END SUPPORTED_BOARDS -->",
                    "",
                ]
            ),
        )
