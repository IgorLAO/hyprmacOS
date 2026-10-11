# Comparador Tahoe ↔ Hyprmac

Ferramentas sob demanda; requerem Python com Pillow e NumPy. SSIM aparece quando `scikit-image` está instalado. Vídeos usam `ffmpeg`; capturas Hyprmac usam `grim` (e `slurp` para seleção). O volume `/mnt/macos/root` contém arquivos do sistema, **não** screenshots de uma sessão. `referencias/` aceita somente captura identificada da interface em execução; fotos podem ser importadas, mas o comparador as trata apenas como diagnóstico. `capturas/` guarda Hyprmac; `resultados/` guarda overlays, mapas, métricas e trajetórias. O SQLite conserva somente o resumo e os caminhos.

## Par de imagens

No macOS Tahoe em execução, capture o componente no estado desejado (por exemplo, `screencapture -x -R x,y,w,h control-center.png`). Registre resolução, escala, Light/Dark, accent, wallpaper e estado. No Hyprmac, reproduza **o mesmo layout de controles e estado**. Fotos com perspectiva, imagens de `Assets.car`, montagens e cenas promocionais não são pares válidos para pontuação de fidelidade.

```sh
cd /home/igor/Projects/hyprmac
P=BaseConhecimento/MacTahoe/comparador
python3 "$P/capture.py" tahoe --file /caminho/control-center.png \
  --component 'Control Center' --state aberto --theme dark --accent blue \
  --scale 2 --wallpaper 'nome-do-papel' --origin 'Tahoe 26, sessão local' \
  --source-type screenshot
python3 "$P/capture.py" hyprmac --component 'Control Center' --state aberto \
  --theme dark --accent blue --scale 1 --wallpaper 'nome-do-papel' \
  --rect '1602,45 306x525'
python3 "$P/compare.py" --component 'Control Center' \
  --tahoe "$P/referencias/control-center/ARQUIVO.png" \
  --hyprmac "$P/capturas/control-center/ARQUIVO.png" \
  --mask /caminho/mascara.png
```

Os dois recortes devem conter a mesma superfície. `--tahoe-crop` e `--hyprmac-crop` aceitam `x,y,largura,altura` para ajustar a área sem alterar os originais. A máscara branca inclui o componente; preto exclui wallpaper, relógio ou outros elementos dinâmicos. Ela deve ser criada conscientemente, sem apagar partes do controle. Metadados divergentes impedem a pontuação; `--allow-mismatch` e `--allow-photo` geram somente diagnóstico. A diferença de tamanho lógico é medida **antes** de redimensionar o Hyprmac para comparar pixels. MAE, contornos (F1) e SSIM opcional não substituem revisão visual de `overlay.png` e `diferenca.png`.

## Par de animações

Grave a interação Tahoe com alguns frames antes e depois do evento. Importe o vídeo e capture a região Hyprmac enquanto aciona a mesma interação:

```sh
python3 "$P/capture.py" tahoe-motion --file /caminho/popover.mp4 \
  --component 'Control Center' --state popover-open --theme dark --accent blue \
  --scale 2 --wallpaper 'nome-do-papel' --origin 'Tahoe 26, sessão local' --fps 60
python3 "$P/capture.py" hyprmac-sequence --component 'Control Center' \
  --state popover-open --theme dark --accent blue --scale 1 \
  --wallpaper 'nome-do-papel' --rect '1602,45 306x525' --fps 30 --seconds 3
python3 "$P/motion.py" --component 'Control Center' --event popover-open \
  --tahoe "$P/referencias/control-center/VIDEO.mp4" \
  --hyprmac "$P/capturas/control-center/SEQUENCIA" \
  --tahoe-fps 60 --hyprmac-fps 30 --record
```

`capture.py` registra timestamps reais de cada frame feito com `grim`; a taxa pedida é apenas uma meta. Em vídeo, informe a taxa real da gravação ou consulte `ffprobe`. `motion.py` detecta o primeiro frame alterado; se necessário, use `--onset-tahoe` e `--onset-hyprmac`. Ajuste recortes com `--tahoe-crop` e `--hyprmac-crop`. A trajetória inclui a caixa dos pixels alterados e a intensidade média aparente em relação ao primeiro frame. A segunda ajuda a observar fades, mas **não é opacidade real**; brilho, vídeo ao fundo e wallpaper contaminam ambas. Duração, área e overshoot são **estimativas**, não parâmetros oficiais da Apple. Use os CSVs e o gráfico para inspecionar a trajetória antes de editar o componente.

Após um ajuste, faça nova captura com as mesmas condições e compare os dois resultados. O banco recebe só pares verificados; fotos e metadados incompatíveis não são registrados como fidelidade.
