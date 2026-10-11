#!/usr/bin/env python3
"""Inventário somente leitura: metadados, receitas e nomes; não decodifica CoreUI.

O JSON contém medidas e identificadores, nunca imagens/fontes/binários Apple.
--output deve apontar para fora do volume de referência.
"""

import argparse
import collections
import json
import plistlib
import re
import shutil
import subprocess
from pathlib import Path

TARGETS = (
    "CoreServices/SystemAppearance.bundle",
    "CoreServices/Dock.app",
    "CoreServices/ControlCenter.app",
    "CoreServices/SystemUIServer.app",
    "CoreServices/NotificationCenter.app",
    "CoreServices/WindowManager.app",
    "CoreServices/Finder.app",
    "CoreServices/Spotlight.app",
    "Frameworks/AppKit.framework",
    "PrivateFrameworks/CoreUI.framework",
    "Frameworks/Carbon.framework/Versions/A/Frameworks/HIToolbox.framework",
    "PrivateFrameworks/CoreMaterial.framework",
    "PrivateFrameworks/DesignLibrary.framework",
    "PrivateFrameworks/WindowManagement.framework",
    "PrivateFrameworks/Wallpaper.framework",
    "Fonts",
)
NAMES = re.compile(
    r"slider|knob|button|popover|material|glass|rimcolor|menubar|selected|disabled|"
    r"NSAppearanceName|vibran|inactive|highcontrast",
    re.IGNORECASE,
)


def metadata(path, root):
    return {
        "path": str(path.relative_to(root)),
        "type": path.suffix or "binary",
        "bytes": path.stat().st_size,
    }


def inventory(root):
    library = root / "System/Library"
    result = {
        "schema": 1,
        "source": str(root),
        "version": plistlib.loads(
            (library / "CoreServices/SystemVersion.plist").read_bytes()
        ),
        "tools": {
            name: shutil.which(name)
            for name in ("assetutil", "cartool", "carutil", "strings")
        },
        "limitations": [
            "strings gives identifiers, not rendition metadata or proof of runtime use",
            "scales in filenames are hints; dimensions, cap insets and rendering modes undecoded",
            "CoreMaterial recipes present in macOS can be shared or legacy; surface binding unverified",
            "blurRadius is an Apple recipe parameter, not Hyprland size or hyprglass blur_strength",
        ],
        "catalogs": [],
        "resources": [],
        "recipes": {},
        "style_roles": {},
        "owners": {},
    }
    for path in sorted(library.rglob("*.car")):
        if path.is_symlink():
            continue
        entry = metadata(path, root)
        relative = str(path.relative_to(library))
        if any(relative.startswith(target + "/") for target in TARGETS):
            with path.open("rb") as stream:
                entry["signature"] = stream.read(8).decode("ascii", errors="replace")
            if result["tools"]["strings"]:
                lines = subprocess.run(
                    [result["tools"]["strings"], "-n", "7", str(path)],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                ).stdout.splitlines()
                names = sorted({s for s in lines if len(s) <= 120 and NAMES.search(s)})
                entry["identifier_count"] = len(names)
                entry["identifier_sample"] = names[:60]
        result["catalogs"].append(entry)
    for target in TARGETS:
        files = sorted(
            p
            for p in (library / target).rglob("*")
            if p.is_file() and not p.is_symlink()
        )
        result["owners"][target] = dict(
            collections.Counter(p.suffix or "binary" for p in files)
        )
        for path in files:
            if ".lproj" in str(path):
                continue
            result["resources"].append(metadata(path, root))
            if path.suffix == ".materialrecipe":
                result["recipes"][str(path.relative_to(root))] = plistlib.loads(
                    path.read_bytes()
                )
            elif path.suffix == ".visualstyleset":
                data = plistlib.loads(path.read_bytes())
                result["style_roles"][path.name] = {
                    "roles": {k: v for k, v in data.items() if k != "styles"},
                    "styles": {
                        k: {
                            "tint": v.get("tinting"),
                            "blend": v.get("blending"),
                            "filter": v.get("filtering", {}).get("filterType"),
                        }
                        for k, v in data.get("styles", {}).items()
                    },
                }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/mnt/macos/root"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output.is_relative_to(root) or output.is_relative_to(Path("/mnt/macos")):
        parser.error("O inventário deve ser escrito fora do volume macOS")
    result = inventory(root)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(
        f"{len(result['catalogs'])} catálogos; {len(result['recipes'])} receitas; {output}"
    )


if __name__ == "__main__":
    main()
