#!/usr/bin/env python3
"""Compara recortes equivalentes sem apagar diferenças de cor ou geometria."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from store import save_result

ROOT = Path(__file__).resolve().parent


def box(text):
    values = [int(x) for x in text.split(",")]
    if len(values) != 4 or values[2] <= 0 or values[3] <= 0:
        raise ValueError("Recorte deve ser x,y,largura,altura")
    return tuple(values[:2] + [values[0] + values[2], values[1] + values[3]])


def metadata(path):
    sidecar = path.with_suffix(path.suffix + ".json")
    return json.loads(sidecar.read_text()) if sidecar.exists() else None


def edges(image):
    gray = np.asarray(image.convert("L"), dtype=np.int16)
    dx = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    dy = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    return ((dx + dy) > 45).astype(np.uint8) * 255


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tahoe", required=True, type=Path)
    p.add_argument("--hyprmac", required=True, type=Path)
    p.add_argument("--component", required=True)
    p.add_argument("--tahoe-crop", help="x,y,largura,altura em pixels da imagem")
    p.add_argument("--hyprmac-crop", help="x,y,largura,altura em pixels da imagem")
    p.add_argument("--mask", type=Path, help="PNG branco = área avaliada; preto = fundo ignorado")
    p.add_argument("--output", type=Path, help="Pasta da execução")
    p.add_argument("--allow-photo", action="store_true", help="Diagnóstico visual apenas, sem nota de fidelidade")
    p.add_argument("--allow-mismatch", action="store_true", help="Permite metadados incompatíveis; diagnóstico apenas")
    p.add_argument("--no-db", action="store_true")
    args = p.parse_args()
    try:
        tm, hm = metadata(args.tahoe), metadata(args.hyprmac)
        if not tm or not hm:
            raise ValueError("Faltam sidecars .json; importe/capture primeiro com capture.py")
        if tm.get("source_type") == "photo" and not args.allow_photo:
            raise ValueError("Foto possui perspectiva; use --allow-photo somente para diagnóstico")
        if tm.get("source_type") not in ("screenshot", "video-frame", "photo"):
            raise ValueError("A origem Tahoe deve ser screenshot, video-frame ou photo")
        if hm.get("origin") != "hyprmac-live":
            raise ValueError("A imagem Hyprmac precisa ser capturada com capture.py")
        mismatches = [k for k in ("component", "state", "theme", "accent") if tm.get(k) != hm.get(k)]
        if mismatches and not args.allow_mismatch:
            raise ValueError("Condições diferentes: " + ", ".join(mismatches))
        if tm.get("component", "").lower() != args.component.lower():
            raise ValueError("--component diverge do metadado Tahoe")
        with Image.open(args.tahoe) as im:
            t = im.convert("RGB")
        with Image.open(args.hyprmac) as im:
            h = im.convert("RGB")
        for label, image, spec in (("Tahoe", t, args.tahoe_crop), ("Hyprmac", h, args.hyprmac_crop)):
            if spec:
                x1, y1, x2, y2 = box(spec)
                if x1 < 0 or y1 < 0 or x2 > image.width or y2 > image.height:
                    raise ValueError(f"Recorte {label} sai da imagem")
        if args.tahoe_crop:
            t = t.crop(box(args.tahoe_crop))
        if args.hyprmac_crop:
            h = h.crop(box(args.hyprmac_crop))
        original_sizes = {"tahoe": t.size, "hyprmac": h.size}
        if min(*t.size, *h.size) < 4:
            raise ValueError("Recortes precisam ter ao menos 4 pixels por dimensão")
        # A diferença de tamanho físico/lógico permanece nas métricas; o resize
        # serve só para comparar cor e contorno dentro de regiões correspondentes.
        t_scale, h_scale = float(tm["scale"]), float(hm["scale"])
        logical = {"tahoe": [round(x / t_scale, 2) for x in t.size],
                   "hyprmac": [round(x / h_scale, 2) for x in h.size]}
        size_delta = [round(logical["hyprmac"][i] / logical["tahoe"][i] - 1, 4) for i in (0, 1)]
        h = h.resize(t.size, Image.Resampling.LANCZOS) if h.size != t.size else h
        mask = Image.open(args.mask).convert("L").resize(t.size, Image.Resampling.NEAREST) if args.mask else Image.new("L", t.size, 255)
        keep = np.asarray(mask) >= 128
        if not keep.any():
            raise ValueError("Máscara sem pixels selecionados")
        ta = np.asarray(t, dtype=np.int16)
        ha = np.asarray(h, dtype=np.int16)
        delta = np.abs(ta - ha)
        mae = float(delta[keep].mean())
        high = float((delta[keep].mean(axis=1) > 35).mean())
        te, he = edges(t), edges(h)
        # Tolerância de 1 px para anti-aliasing, sem mover as imagens.
        te_near = np.asarray(Image.fromarray(te).filter(ImageFilter.MaxFilter(3))) > 0
        he_near = np.asarray(Image.fromarray(he).filter(ImageFilter.MaxFilter(3))) > 0
        tp, hp = (te > 0) & keep, (he > 0) & keep
        precision = float((hp & te_near).sum() / max(1, hp.sum()))
        recall = float((tp & he_near).sum() / max(1, tp.sum()))
        edge_f1 = 1.0 if not tp.any() and not hp.any() else 2 * precision * recall / max(1e-9, precision + recall)
        try:
            from skimage.metrics import structural_similarity
            ssim = float(structural_similarity(np.asarray(t), np.asarray(h), channel_axis=2, data_range=255))
        except ImportError:
            ssim = None
        wallpaper_mismatch = tm.get("wallpaper") != hm.get("wallpaper")
        diagnostic = bool(mismatches or tm["source_type"] == "photo" or (wallpaper_mismatch and not args.mask))
        priority = "DIAGNOSTICO" if diagnostic else ("P0" if max(map(abs, size_delta)) > .12 or edge_f1 < .42 else
                    "P1" if max(map(abs, size_delta)) > .05 or edge_f1 < .7 or mae > 25 else
                    "P2" if mae > 12 or edge_f1 < .85 else "P3")
        if diagnostic:
            notes = ["Par não equivalente: métricas não orientam correções e não entram no SQLite."]
            if tm["source_type"] == "photo":
                notes.append("Foto com perspectiva: obtenha screenshot direto do Tahoe para medir geometria.")
            if wallpaper_mismatch and not args.mask:
                notes.append("Wallpapers diferentes: forneça --mask ou iguale o fundo.")
            if mismatches:
                notes.append("Metadados divergentes: " + ", ".join(mismatches))
        else:
            notes = []
            if max(map(abs, size_delta)) > .05:
                notes.append(f"Ajustar geometria: Hyprmac {size_delta[0]:+.1%} na largura e {size_delta[1]:+.1%} na altura lógica.")
            if edge_f1 < .7:
                notes.append("Rever posição, alinhamento, contorno e espaçamento das subviews.")
            if mae > 25:
                notes.append("Rever cor/material somente após igualar wallpaper e estado.")
            if wallpaper_mismatch:
                notes.append("Wallpapers diferentes: máscara excluiu o fundo, mas o material pode reagir de outro modo.")
        folder = args.output or ROOT / "resultados" / args.component.lower().replace(" ", "-") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        folder.mkdir(parents=True, exist_ok=False)
        t.save(folder / "tahoe.png")
        h.save(folder / "hyprmac.png")
        Image.blend(t, h, .5).save(folder / "overlay.png")
        heat = np.clip(delta.mean(axis=2) * 3, 0, 255).astype(np.uint8)
        heat[~keep] = 0
        Image.fromarray(heat, "L").save(folder / "diferenca.png")
        Image.fromarray(np.stack([te, he, np.zeros_like(te)], axis=2), "RGB").save(folder / "bordas.png")
        mask.save(folder / "mascara.png")
        metrics = dict(component=args.component, priority=priority, diagnostic=diagnostic,
                       source={"tahoe": str(args.tahoe.resolve()), "hyprmac": str(args.hyprmac.resolve())},
                       original_sizes=original_sizes, logical_sizes=logical, size_delta=size_delta,
                       mae=round(mae, 3), changed_fraction=round(high, 4),
                       edge_f1=round(edge_f1, 4), ssim=None if ssim is None else round(ssim, 4),
                       mask_coverage=round(float(keep.mean()), 4), warnings=notes)
        (folder / "metricas.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
        if not args.no_db and not diagnostic:
            metrics["db_id"] = save_result(args.component, "imagem", args.tahoe, args.hyprmac, folder / "metricas.json", metrics, priority)
            (folder / "metricas.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"output": str(folder), "priority": priority, "mae": round(mae, 2),
                          "edge_f1": round(edge_f1, 3), "size_delta": size_delta, "warnings": notes}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as exc:
        p.error(str(exc))


if __name__ == "__main__":
    main()
