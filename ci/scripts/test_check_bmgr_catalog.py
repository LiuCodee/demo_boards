import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("check_bmgr_catalog.py")
SPEC = importlib.util.spec_from_file_location("check_bmgr_catalog", SCRIPT_PATH)
check_bmgr_catalog = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(check_bmgr_catalog)


class FakeProvider:
    selected_profile_id = "5.5"

    def __init__(self, supported_chips):
        self.supported_chips = supported_chips

    def chip(self, chip):
        if chip not in self.supported_chips:
            raise KeyError(chip)


class CheckBmgrCatalogTest(unittest.TestCase):
    def test_accepts_chip_present_in_selected_catalog(self):
        provider = FakeProvider({"esp32s3"})

        supported, profile = check_bmgr_catalog.check_compatibility(
            Path("/unused"),
            "5.5.4",
            "ESP32-S3",
            provider_loader=lambda _root, _version: provider,
        )

        self.assertTrue(supported)
        self.assertEqual(profile, "5.5")

    def test_reports_chip_missing_from_selected_catalog_as_unsupported(self):
        provider = FakeProvider({"esp32s3"})

        supported, profile = check_bmgr_catalog.check_compatibility(
            Path("/unused"),
            "5.5.4",
            "esp32s31",
            provider_loader=lambda _root, _version: provider,
        )

        self.assertFalse(supported)
        self.assertEqual(profile, "5.5")

    def test_does_not_classify_catalog_load_errors_as_unsupported(self):
        def broken_loader(_root, _version):
            raise RuntimeError("catalog is corrupt")

        with self.assertRaisesRegex(RuntimeError, "catalog is corrupt"):
            check_bmgr_catalog.check_compatibility(
                Path("/unused"),
                "5.5.4",
                "esp32s31",
                provider_loader=broken_loader,
            )
