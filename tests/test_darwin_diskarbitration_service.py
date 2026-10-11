import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Provide a lightweight stand-in for the disk utility module so the service
# can be exercised without Gtk/GIO installed.
standin = types.ModuleType("shell.linux_storage_adapter")


def fake_read_block_devices():
    return [
        {"path": "/dev/sda", "size": 500000000000, "type": "disk",
         "fstype": "", "mountpoint": "", "model": "Samsung SSD", "children": [
             {"path": "/dev/sda1", "size": 524288000, "type": "part",
              "fstype": "vfat", "mountpoint": "/boot/efi", "model": "", "children": []},
         ]},
    ], ""


standin.read_block_devices = fake_read_block_devices
sys.modules["shell.linux_storage_adapter"] = standin

spec = importlib.util.spec_from_file_location(
    "darwin_diskarbitration_service",
    ROOT / "shell" / "darwin_diskarbitration_service.py",
)
mod = importlib.util.module_from_spec(spec)
sys.modules["darwin_diskarbitration_service"] = mod
spec.loader.exec_module(mod)


def test_list_volumes_from_udisks():
    service = mod.DiskArbitrationService()
    volumes = service.list_volumes()
    assert len(volumes) == 1
    assert volumes[0].device == "/dev/sda"
    assert volumes[0].mounted is False
    assert volumes[0].children[0].mounted is True
    assert volumes[0].children[0].filesystem == "vfat"


def test_darwin_disk_list_dicts():
    data = mod.darwin_disk_list()
    assert data[0]["device"] == "/dev/sda"
    assert data[0]["children"][0]["mountpoint"] == "/boot/efi"


def test_empty_on_error():
    standin.read_block_devices = lambda: ([], "boom")
    service = mod.DiskArbitrationService()
    assert service.list_volumes() == []
    standin.read_block_devices = fake_read_block_devices

import unittest


class TestDarwinDiskArbitrationService(unittest.TestCase):
    def test_list_volumes_from_udisks(self):
        standin.read_block_devices = fake_read_block_devices
        service = mod.DiskArbitrationService()
        volumes = service.list_volumes()
        self.assertEqual(len(volumes), 1)
        self.assertEqual(volumes[0].device, "/dev/sda")
        self.assertFalse(volumes[0].mounted)
        self.assertTrue(volumes[0].children[0].mounted)

    def test_darwin_disk_list_dicts(self):
        standin.read_block_devices = fake_read_block_devices
        data = mod.darwin_disk_list()
        self.assertEqual(data[0]["device"], "/dev/sda")
        self.assertEqual(data[0]["children"][0]["mountpoint"], "/boot/efi")

    def test_empty_on_error(self):
        standin.read_block_devices = lambda: ([], "boom")
        service = mod.DiskArbitrationService()
        self.assertEqual(service.list_volumes(), [])
        standin.read_block_devices = fake_read_block_devices


if __name__ == "__main__":
    unittest.main()
