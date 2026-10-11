#!/usr/bin/env python3
"""Trajetórias estimadas de vídeos/frames do mesmo evento, alinhadas pelo início."""
import argparse
import csv
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from store import save_result

ROOT = Path(__file__).resolve().parent
EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def frames(path, temporary, label):
    if path.is_dir():
        found = sorted(p for p in path.iterdir() if p.suffix.lower() in EXTS)
    elif path.suffix.lower() in EXTS:
        raise ValueError("Movimento precisa de vários frames, não uma imagem")
    else:
        folder = Path(temporary) / label
        folder.mkdir()
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vsync", "0",
                        str(folder / "%06d.png")], check=True)
        found = sorted(folder.glob("*.png"))
    if len(found) < 3:
        raise ValueError(f"{path}: são necessários ao menos 3 frames")
    return found


def crop_box(value):
    if not value:
        return None
    x, y, w, h = map(int, value.split(","))
    if w <= 0 or h <= 0:
        raise ValueError("Recorte inválido")
    return x, y, x + w, y + h


def manifest(path):
    sidecar = path / "manifest.json" if path.is_dir() else path.with_suffix(path.suffix + ".json")
    return json.loads(sidecar.read_text()) if sidecar.exists() else None


def trace(paths, fps, region, threshold, onset, timestamps=None):
    if fps <= 0:
        raise ValueError("FPS precisa ser positivo")
    if timestamps is not None and len(timestamps) != len(paths):
        raise ValueError("frame_times do manifesto não corresponde ao número de frames")
    images = []
    for path in paths:
        with Image.open(path) as image:
            part = image.convert("RGB")
            if region:
                part = part.crop(region)
            images.append(np.asarray(part, dtype=np.int16))
    if any(image.shape != images[0].shape for image in images):
        raise ValueError("Frames de um mesmo vídeo têm dimensões diferentes")
    base = images[0]
    h, w = base.shape[:2]
    rows = []
    for i, image in enumerate(images):
        difference = np.abs(image - base).mean(axis=2)
        changed = difference > threshold
        ys, xs = np.nonzero(changed)
        if len(xs):
            x, y = int(xs.min()), int(ys.min())
            bw, bh = int(xs.max() - x + 1), int(ys.max() - y + 1)
        else:
            x = y = bw = bh = 0
        rows.append(dict(frame=i, time=round(timestamps[i] if timestamps is not None else i / fps, 5),
                         changed=float(changed.mean()), energy=float(difference.mean() / 255),
                         x=x / w, y=y / h, width=bw / w, height=bh / h,
                         area=(bw * bh) / (w * h)))
    if onset is None:
        onset = next((i for i, row in enumerate(rows[1:], 1) if row["changed"] >= .002), None)
        if onset is None:
            raise ValueError("Evento não detectado; escolha --onset-* ou ajuste --threshold")
    if onset < 0 or onset >= len(rows) - 1:
        raise ValueError("Onset fora da sequência")
    start = rows[onset]["time"]
    for row in rows:
        row["aligned_time"] = round(row["time"] - start, 5)
    return rows, onset


def settle(rows, onset, key):
    values = np.asarray([r[key] for r in rows], dtype=float)
    final = float(np.median(values[-max(2, len(values) // 5):]))
    tolerance = max(.005, abs(final - values[max(0, onset - 1)]) * .05)
    for i in range(onset, len(rows)):
        if np.all(np.abs(values[i:] - final) <= tolerance):
            return rows[i]["aligned_time"], final
    return rows[-1]["aligned_time"], final


def plot(folder, a, b):
    img = Image.new("RGB", (900, 650), "#17191c")
    d = ImageDraw.Draw(img)
    colors = ("#77baff", "#ffb775")
    d.text((24, 14), "Tahoe (azul)  /  Hyprmac (laranja)", fill="white")
    longest = max(a[-1]["aligned_time"], b[-1]["aligned_time"], .01)
    for key, heading, y0, height in (("area", "Caixa dos pixels alterados", 54, 245),
                                     ("energy", "Intensidade aparente da mudanca", 348, 245)):
        d.text((50, y0 - 15), heading, fill="#cfd4db")
        top = max(max(r[key] for r in a), max(r[key] for r in b), .01)
        for rows, color in zip((a, b), colors):
            points = [(50 + 820 * max(0, r["aligned_time"]) / longest,
                       y0 + height - height * r[key] / top) for r in rows if r["aligned_time"] >= 0]
            if len(points) >= 2:
                d.line(points, fill=color, width=3)
        d.line([(50, y0), (50, y0 + height), (870, y0 + height)], fill="#72777f", width=1)
    img.save(folder / "trajetoria.png")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tahoe", required=True, type=Path, help="Vídeo ou pasta de frames do Tahoe em execução")
    p.add_argument("--hyprmac", required=True, type=Path)
    p.add_argument("--component", required=True)
    p.add_argument("--event", required=True, help="Ex.: popover-open, dock-hover")
    p.add_argument("--tahoe-fps", required=True, type=float)
    p.add_argument("--hyprmac-fps", required=True, type=float)
    p.add_argument("--tahoe-crop", help="x,y,largura,altura")
    p.add_argument("--hyprmac-crop", help="x,y,largura,altura")
    p.add_argument("--onset-tahoe", type=int)
    p.add_argument("--onset-hyprmac", type=int)
    p.add_argument("--threshold", type=float, default=20, help="Diferença RGB média por pixel")
    p.add_argument("--output", type=Path)
    p.add_argument("--record", action="store_true", help="Persistir par de origem/estado verificados no SQLite")
    args = p.parse_args()
    try:
        if args.threshold <= 0:
            raise ValueError("--threshold precisa ser positivo")
        tm, hm = manifest(args.tahoe), manifest(args.hyprmac)
        mismatch = [k for k in ("component", "state", "theme", "accent", "wallpaper") if tm and hm and tm.get(k) != hm.get(k)]
        if args.record and (not tm or not hm or mismatch or tm.get("source_type") != "video" or hm.get("origin") != "hyprmac-live"):
            raise ValueError("Para --record, importe vídeo Tahoe e capture sequência Hyprmac com capture.py em condições equivalentes")
        if tm and tm.get("component", "").lower() != args.component.lower():
            raise ValueError("--component diverge do manifesto Tahoe")
        with tempfile.TemporaryDirectory() as temporary:
            ta, ti = trace(frames(args.tahoe, temporary, "tahoe"), args.tahoe_fps,
                           crop_box(args.tahoe_crop), args.threshold, args.onset_tahoe,
                           tm.get("frame_times") if tm else None)
            hy, hi = trace(frames(args.hyprmac, temporary, "hyprmac"), args.hyprmac_fps,
                           crop_box(args.hyprmac_crop), args.threshold, args.onset_hyprmac,
                           hm.get("frame_times") if hm else None)
        ta_area, tfinal = settle(ta, ti, "area")
        hy_area, hfinal = settle(hy, hi, "area")
        td = max(ta_area, settle(ta, ti, "energy")[0])
        hd = max(hy_area, settle(hy, hi, "energy")[0])
        ttime = np.asarray([r["aligned_time"] for r in ta[ti:]])
        htime = np.asarray([r["aligned_time"] for r in hy[hi:]])
        common = np.linspace(0, min(ttime[-1], htime[-1]), 80)
        error = {}
        for key in ("x", "y", "width", "height", "area", "energy"):
            tv = np.interp(common, ttime, [r[key] for r in ta[ti:]])
            hv = np.interp(common, htime, [r[key] for r in hy[hi:]])
            error[key] = round(float(np.mean(np.abs(tv - hv))), 4)
        tmax = max(r["area"] for r in ta[ti:])
        hmax = max(r["area"] for r in hy[hi:])
        overshoot = {"tahoe": round(max(0, tmax - tfinal), 4),
                     "hyprmac": round(max(0, hmax - hfinal), 4)}
        delta_ms = round((hd - td) * 1000)
        priority = "P0" if abs(delta_ms) > 150 or error["area"] > .15 or error["energy"] > .15 else "P1" if abs(delta_ms) > 60 or error["area"] > .07 or error["energy"] > .07 else "P2"
        folder = args.output or ROOT / "resultados" / args.component.lower().replace(" ", "-") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        folder.mkdir(parents=True, exist_ok=False)
        for name, rows in (("tahoe", ta), ("hyprmac", hy)):
            with (folder / f"{name}-trajetoria.csv").open("w", newline="") as f:
                writer = csv.DictWriter(f, rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        plot(folder, ta, hy)
        result = dict(component=args.component, event=args.event, priority=priority,
                      diagnostic=bool(not tm or not hm or mismatch or tm.get("source_type") != "video" or hm.get("origin") != "hyprmac-live"),
                      onset_frame={"tahoe": ti, "hyprmac": hi},
                      duration_ms={"tahoe": round(td * 1000), "hyprmac": round(hd * 1000)},
                      duration_delta_ms=delta_ms, trajectory_mae=error,
                      apparent_area_overshoot=overshoot,
                      limitations="Trajetória é a caixa da diferença contra o primeiro frame; energy é intensidade aparente, não opacidade real. Mudanças de fundo/luminosidade afetam ambas. Damping e parâmetros de spring não são identificáveis sem segmentação ou observação adicional.")
        (folder / "metricas.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        if args.record:
            result["db_id"] = save_result(args.component, "movimento", args.tahoe, args.hyprmac, folder / "metricas.json", result, priority)
            (folder / "metricas.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"output": str(folder), "priority": priority,
                          "duration_delta_ms": delta_ms, "trajectory_mae": error}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        p.error(str(exc))


if __name__ == "__main__":
    main()
