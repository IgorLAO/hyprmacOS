"""Shared artifact checks for the manifest based application factory."""

import configparser
import json
import os
import re
import shlex
import sys
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shell"))
from app_factory_registry import all_manifests, load_manifest  # noqa: E402


class AppFactoryArtifactsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads((ROOT / "BaseConhecimento/referencias/tahoe-apps-70.json").read_text())
        cls.catalog = json.loads((ROOT / "BaseConhecimento/referencias/hyprmac-apps-progress.json").read_text())

    def test_manifest_registry_covers_missing_apps_only(self):
        missing = [a for a in self.inventory["apps"] if a["implementacao"] == "AUSENTE"]
        manifests = all_manifests()
        self.assertEqual(len(missing), 55)
        self.assertEqual(len(manifests), 55)
        self.assertEqual(len({m["id"] for m in manifests}), 55)
        for app in missing:
            app_id = "dev.hyprmac." + re.sub(r"[^A-Za-z0-9]", "", app["nome"])
            with self.subTest(app=app_id):
                manifest = load_manifest(app_id)
                self.assertEqual(manifest["name"], app["nome"])
                self.assertEqual(manifest["bundle_id"], app["bundle_id"])
                self.assertEqual(manifest["evidence"]["inventory"],
                                 "BaseConhecimento/referencias/tahoe-apps-70.json")

    def test_launchers_and_icons_are_usable(self):
        launchers = ROOT / "shell/app-launchers"
        self.assertEqual(len(list(launchers.glob("*.desktop"))), 55)
        for manifest in all_manifests():
            app_id = manifest["id"]
            with self.subTest(app=app_id):
                launcher = launchers / f"{app_id}.desktop"
                parser = configparser.ConfigParser(interpolation=None)
                self.assertTrue(parser.read(launcher))
                entry = parser["Desktop Entry"]
                self.assertEqual(entry["Type"], "Application")
                self.assertEqual(entry["Name"], manifest["name"])
                self.assertEqual(entry["StartupWMClass"], app_id)
                executable, argument = shlex.split(entry["Exec"])
                self.assertEqual(argument, app_id)
                self.assertTrue(os.access(executable, os.X_OK))
                icon = ROOT / manifest["icon"]
                self.assertEqual(Path(entry["Icon"]), icon)
                with Image.open(icon) as image:
                    self.assertEqual(image.format, "PNG")
                    self.assertEqual(image.size, (256, 256))
                    image.verify()

    def test_catalog_and_existing_apps(self):
        apps = self.catalog["apps"]
        self.assertEqual(len(apps), 70)
        self.assertEqual(len({a["id"] for a in apps}), 70)
        existing = [a for a in self.inventory["apps"] if a["implementacao"] == "PARCIAL"]
        self.assertEqual(len(existing), 15)
        for app in existing:
            stem = re.sub(r"[^A-Za-z0-9]", "", app["nome"])
            with self.subTest(app=app["nome"]):
                self.assertFalse((ROOT / "shell/app-launchers" / f"dev.hyprmac.{stem}.desktop").exists())
                self.assertFalse((ROOT / "shell/app-manifests" / f"{stem}.json").exists())


if __name__ == "__main__":
    unittest.main()
