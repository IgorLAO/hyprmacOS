#!/usr/bin/env python3
"""Importa uma captura do Tahoe ou recorta o Hyprmac via grim, sob demanda."""
import argparse
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def slug(value):
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not value:
        raise ValueError("Nome de componente/estado vazio")
    return value


def geometry(value):
    if not re.fullmatch(r"-?\d+,-?\d+ \d+x\d+", value):
        raise ValueError("Área inválida; use 'x,y larguraXaltura', por exemplo '100,50 400x300'")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("tahoe", "hyprmac"):
        p = sub.add_parser(action)
        p.add_argument("--component", required=True)
        p.add_argument("--state", required=True, help="Ex.: aberto, hover, pressed")
        p.add_argument("--theme", required=True, choices=("light", "dark"))
        p.add_argument("--accent", required=True)
        p.add_argument("--scale", required=True, type=float, help="Pixels por ponto lógico")
        p.add_argument("--wallpaper", default="desconhecido")
        p.add_argument("--note", default="")
        if action == "tahoe":
            p.add_argument("--file", required=True, type=Path, help="Screenshot do Tahoe em execução")
            p.add_argument("--origin", required=True, help="Máquina/sessão que gerou a captura")
            p.add_argument("--source-type", required=True, choices=("screenshot", "video-frame", "photo"))
        else:
            group = p.add_mutually_exclusive_group(required=True)
            group.add_argument("--rect", help="Área 'x,y larguraXaltura'")
            group.add_argument("--select", action="store_true", help="Selecionar área com slurp")
    seq = sub.add_parser("hyprmac-sequence", help="Captura frames sob demanda; acione a interação durante a gravação")
    seq.add_argument("--component", required=True)
    seq.add_argument("--state", required=True)
    seq.add_argument("--theme", required=True, choices=("light", "dark"))
    seq.add_argument("--accent", required=True)
    seq.add_argument("--scale", required=True, type=float)
    seq.add_argument("--wallpaper", default="desconhecido")
    seq.add_argument("--rect", required=True)
    seq.add_argument("--fps", type=float, default=30)
    seq.add_argument("--seconds", type=float, default=2)
    seq.add_argument("--note", default="")
    video = sub.add_parser("tahoe-motion", help="Importa gravação real do Tahoe")
    video.add_argument("--file", required=True, type=Path)
    video.add_argument("--component", required=True)
    video.add_argument("--state", required=True)
    video.add_argument("--theme", required=True, choices=("light", "dark"))
    video.add_argument("--accent", required=True)
    video.add_argument("--scale", required=True, type=float)
    video.add_argument("--wallpaper", default="desconhecido")
    video.add_argument("--origin", required=True)
    video.add_argument("--fps", required=True, type=float)
    video.add_argument("--note", default="")
    args = parser.parse_args()
    if args.scale <= 0:
        parser.error("--scale precisa ser positivo")
    if args.action in ("hyprmac-sequence", "tahoe-motion"):
        if args.fps <= 0:
            parser.error("--fps precisa ser positivo")
        folder = ROOT / ("capturas" if args.action == "hyprmac-sequence" else "referencias") / slug(args.component)
        folder.mkdir(parents=True, exist_ok=True)
        name = f"{slug(args.component)}__{slug(args.state)}__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        if args.action == "tahoe-motion":
            if not args.file.is_file():
                parser.error(f"Arquivo inexistente: {args.file}")
            target = folder / (name + args.file.suffix.lower())
            shutil.copy2(args.file, target)
            manifest_path = target.with_suffix(target.suffix + ".json")
            extra = dict(source_type="video", origin=args.origin)
        else:
            if not 0 < args.seconds <= 60:
                parser.error("--seconds precisa estar entre 0 e 60")
            try:
                region = geometry(args.rect)
            except ValueError as exc:
                parser.error(str(exc))
            target = folder / name
            target.mkdir()
            stamps = []
            start = time.monotonic()
            frame = 0
            while time.monotonic() - start < args.seconds:
                scheduled = start + frame / args.fps
                time.sleep(max(0, scheduled - time.monotonic()))
                stamp = time.monotonic() - start
                try:
                    subprocess.run(["grim", "-g", region, str(target / f"{frame:06d}.png")],
                                   check=True, stdout=subprocess.DEVNULL)
                except (OSError, subprocess.CalledProcessError) as exc:
                    parser.error(f"Falha na gravação do frame {frame}: {exc}")
                stamps.append(round(stamp, 6))
                frame += 1
            manifest_path = target / "manifest.json"
            extra = dict(source_type="frame-sequence", origin="hyprmac-live",
                         region=region, frame_times=stamps, actual_fps=round((len(stamps) - 1) / max(.001, stamps[-1] - stamps[0]), 2))
        meta = dict(component=args.component, state=args.state, theme=args.theme,
                    accent=args.accent, scale=args.scale, wallpaper=args.wallpaper,
                    requested_fps=args.fps, note=args.note,
                    captured_at=datetime.now(timezone.utc).isoformat(), **extra)
        manifest_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
        print(target)
        return
    name = f"{slug(args.component)}__{slug(args.state)}__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    folder = ROOT / ("referencias" if args.action == "tahoe" else "capturas") / slug(args.component)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{name}.png"
    if args.action == "tahoe":
        if not args.file.is_file():
            parser.error(f"Arquivo inexistente: {args.file}")
        from PIL import Image
        try:
            with Image.open(args.file) as image:
                image.verify()
        except Exception as exc:
            parser.error(f"Imagem inválida: {exc}")
        shutil.copy2(args.file, target.with_suffix(args.file.suffix.lower()))
        target = target.with_suffix(args.file.suffix.lower())
        origin = args.origin
        region = None
    else:
        try:
            region = subprocess.check_output(["slurp"], text=True).strip() if args.select else geometry(args.rect)
            region = geometry(region)
            subprocess.run(["grim", "-g", region, str(target)], check=True)
        except (OSError, subprocess.CalledProcessError, ValueError) as exc:
            parser.error(f"Falha na captura: {exc}")
        origin = "hyprmac-live"
    from PIL import Image
    with Image.open(target) as image:
        size = image.size
    meta = dict(component=args.component, state=args.state, theme=args.theme,
                accent=args.accent, scale=args.scale, wallpaper=args.wallpaper,
                origin=origin, region=region, size=size, note=args.note,
                source_type=args.source_type if args.action == "tahoe" else "screenshot",
                captured_at=datetime.now(timezone.utc).isoformat())
    target.with_suffix(target.suffix + ".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(target)


if __name__ == "__main__":
    main()
