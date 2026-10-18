#!/usr/bin/env bash
# hyprmac — aplica o visual macOS Tahoe no sistema atual
#   ./install.sh [dark|light]
#
# Idempotente: pode rodar de novo quantas vezes quiser. Na primeira vez guarda
# os arquivos originais em backup/ (nunca sobrescreve um backup existente).
set -euo pipefail

H="$HOME/Projects/hyprmac"
C="$HOME/.config"
mode="${1:-dark}"

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$here" != "$H" ]; then
  echo "erro: o repositório precisa estar em $H (os configs apontam para esse caminho)" >&2
  exit 1
fi

step() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }

# Guarda o original em backup/<rel> se ainda não houver backup e ele não for
# um link nosso
backup() {
  local src="$1" rel="$2"
  [ -e "$src" ] && [ ! -L "$src" ] || return 0
  [ -e "$H/backup/$rel" ] && return 0
  mkdir -p "$(dirname "$H/backup/$rel")"
  cp -a "$src" "$H/backup/$rel"
  echo "   backup: $src -> backup/$rel"
}

# Link simbólico dst -> src, guardando o original antes
link() {
  local src="$1" dst="$2" rel="$3"
  if [ ! -e "$src" ]; then
    echo "   aviso: origem ausente, link preservado: $src" >&2
    return 0
  fi
  backup "$dst" "$rel"
  mkdir -p "$(dirname "$dst")"
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then rm -rf "$dst"; fi
  ln -sfn "$src" "$dst"
  echo "   link: $dst -> $src"
}

step "Links de configuração"
step "Comandos da Waybar em Rust"
cargo build --release --locked --manifest-path "$H/core/waybar-status/Cargo.toml"
link "$H/core/waybar-status/target/release/hyprmac-waybar" "$HOME/.local/bin/hyprmac-waybar" local/bin/hyprmac-waybar
step "Aparência automática em Rust"
cargo build --release --locked --manifest-path "$H/core/appearance/Cargo.toml"
link "$H/core/appearance/target/release/hyprmac-aparencia" "$HOME/.local/bin/hyprmac-aparencia" local/bin/hyprmac-aparencia
step "Ações de janela em Rust"
cargo build --release --locked --manifest-path "$H/core/window-actions/Cargo.toml"
link "$H/core/window-actions/target/release/hyprmac-janela" "$HOME/.local/bin/hyprmac-janela" local/bin/hyprmac-janela
step "Histórico da área de transferência em Rust"
cargo build --release --locked --manifest-path "$H/core/clipboard/Cargo.toml"
link "$H/core/clipboard/target/release/hyprmac-clipboard" "$HOME/.local/bin/hyprmac-clipboard" local/bin/hyprmac-clipboard
step "Acessibilidade em Rust"
cargo build --release --locked --manifest-path "$H/core/accessibility/Cargo.toml"
link "$H/core/accessibility/target/release/hyprmac-acessibilidade" "$HOME/.local/bin/hyprmac-acessibilidade" local/bin/hyprmac-acessibilidade
step "Cor de destaque em Rust"
cargo build --release --locked --manifest-path "$H/core/accent/Cargo.toml"
link "$H/core/accent/target/release/hyprmac-accent" "$HOME/.local/bin/hyprmac-accent" local/bin/hyprmac-accent
link "$H/waybar"             "$C/waybar"             waybar
# itens ocultos da barra (Ajustes ▸ Menu Bar): gerado em tempo de execução; o @import precisa dele
[ -e "$H/waybar/barra-ocultos.css" ] || : > "$H/waybar/barra-ocultos.css"
# Imports gerados pelo shell/plugin precisam existir também no primeiro boot.
for generated_css in contrast.css vidro.css; do
  [ -e "$H/waybar/$generated_css" ] || : > "$H/waybar/$generated_css"
done
link "$H/wofi"               "$C/wofi"               wofi
link "$H/ghostty/config"     "$C/ghostty/config"     ghostty/config
link "$H/kitty/kitty.conf"   "$C/kitty/kitty.conf"   kitty/kitty.conf
for f in "$H"/kde/*.colors; do
  link "$f" "$HOME/.local/share/color-schemes/$(basename "$f")" "color-schemes/$(basename "$f")"
done

step "GTK 3/4"
for v in 3 4; do
  css="$C/gtk-$v.0/gtk.css"
  backup "$css"                     "gtk-$v.0/gtk.css"
  backup "$C/gtk-$v.0/settings.ini" "gtk-$v.0/settings.ini"
  if [ ! -f "$H/gtk/gtk$v.css" ]; then
    echo "   aviso: $H/gtk/gtk$v.css ausente; gtk-$v.0/gtk.css preservado" >&2
    continue
  fi
  mkdir -p "$(dirname "$css")"
  cat > "$css" <<EOF
/* hyprmac — tema macOS Tahoe (backup do original em ~/Projects/hyprmac/backup) */
@import url("file://$H/gtk/gtk$v.css");
EOF
  echo "   $css"
done

step "KDE/Qt"
backup "$C/kdeglobals" kdeglobals

step "Hyprland"
hl="$C/hypr/hyprland.lua"
if [ ! -f "$hl" ]; then
  echo "   aviso: $hl não existe; adicione manualmente:" >&2
  echo "   dofile(os.getenv(\"HOME\") .. \"/Projects/hyprmac/hypr/hyprmac.lua\")" >&2
elif grep -q 'Projects/hyprmac/hypr/hyprmac.lua' "$hl"; then
  echo "   hyprmac.lua já carregado em $hl"
else
  backup "$hl" hypr/hyprland.lua
  cat >> "$hl" <<'EOF'


-----------------
---- HYPRMAC ----
-----------------

-- Aparência macOS Tahoe: molduras, vidro, animações, regras e autostart
dofile(os.getenv("HOME") .. "/Projects/hyprmac/hypr/hyprmac.lua")
EOF
  echo "   dofile adicionado ao fim de $hl"
fi

step "Módulo Tocando Agora da barra (waybar/cffi)"
if make -s -C "$H/waybar/cffi"; then
  echo "   waybar/cffi/nowplaying.so"
else
  echo "   aviso: não compilou (precisa de gcc, gtk3 e playerctl); a barra segue sem o nome da música" >&2
fi

step "Menu Bar Extras (tray nativo da Waybar)"
if "$H/scripts/build-waybar-extras"; then
  echo "   extensão SNI local compilada; /usr/bin/waybar preservado"
else
  echo "   aviso: build indisponível; fallback upstream sem filtros, attention/overlay e destaque de menu aberto" >&2
fi

step "Vigia de inatividade (shell/ocioso)"
if make -s -C "$H/shell/ocioso"; then
  echo "   shell/ocioso/hyprmac-ocioso"
else
  echo "   aviso: não compilou (precisa de gcc, wayland-scanner e wayland-protocols)" >&2
fi

step "Fonte SF Pro (do kit macOS 27, uso pessoal)"
mkdir -p "$HOME/.local/share/fonts/SF-Pro"
cp "$H"/BaseConhecimento/referencias/kit/fontes/*.{ttf,otf} "$HOME/.local/share/fonts/SF-Pro/" 2>/dev/null \
  && fc-cache -f "$HOME/.local/share/fonts" >/dev/null && echo "   SF Pro instalada" || echo "   aviso: fontes da BaseConhecimento não encontradas" >&2
gsettings set org.gnome.desktop.interface font-name 'SF Pro 10'
# Qt/KDE (nautilus, Configurações…): a mesma SF Pro do resto do sistema (Body 13 = 10 pt)
if command -v kwriteconfig6 >/dev/null; then
  kwriteconfig6 --file kdeglobals --group General --key font                 "SF Pro,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  kwriteconfig6 --file kdeglobals --group General --key menuFont             "SF Pro,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  kwriteconfig6 --file kdeglobals --group General --key toolBarFont          "SF Pro,9,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  kwriteconfig6 --file kdeglobals --group General --key smallestReadableFont "SF Pro,8,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  kwriteconfig6 --file kdeglobals --group WM      --key activeFont           "SF Pro,10,-1,5,700,0,0,0,0,0,0,0,0,0,0,1"
fi

step "Finder: Nautilus como gerenciador de arquivos padrão"
# pastas abertas por qualquer app (xdg-open, "Show in Folder", Dock) vão para o Finder
command -v nautilus >/dev/null \
  && xdg-mime default org.gnome.Nautilus.desktop inode/directory application/x-gnome-saved-search \
  && echo "   inode/directory → org.gnome.Nautilus.desktop" \
  || echo "   aviso: nautilus não instalado; padrão de pastas mantido" >&2

step "Janelas: semáforo à esquerda e papel de parede da referência"
# fechar, minimizar, zoom à esquerda, como no Mac (GTK 3/4, libadwaita e o
# Brave/Chromium no tema "GTK" leem daqui)
gsettings set org.gnome.desktop.wm.preferences button-layout 'close,minimize,maximize:'
for v in 3 4; do
  ini="$C/gtk-$v.0/settings.ini"
  [ -f "$ini" ] || printf '[Settings]\n' > "$ini"
  if grep -q '^gtk-decoration-layout=' "$ini"; then
    sed -i 's/^gtk-decoration-layout=.*/gtk-decoration-layout=close,minimize,maximize:/' "$ini"
  else
    echo 'gtk-decoration-layout=close,minimize,maximize:' >> "$ini"
  fi
done
# papel de parede padrão do Tahoe 26 (referencias/telas/macos-tahoe-home-screen.jpg); o
# indigo-referencia.png só imitava a faixa de um print e deixava a barra roxa e chapada
wp="file://$H/wallpapers/tahoe-light-1080p.jpg"
gsettings set org.gnome.desktop.background picture-uri "$wp"
gsettings set org.gnome.desktop.background picture-uri-dark "$wp"

step "Ajustes do Sistema (shell/hyprmac-ajustes)"
mkdir -p "$HOME/.local/share/applications"
sed "s|/home/igor/Projects/hyprmac|$H|g" "$H/shell/dev.hyprmac.Settings.desktop" \
  > "$HOME/.local/share/applications/dev.hyprmac.Settings.desktop"
echo "   System Settings no Dock, no Spotlight e na Central de Controle"

step "Notes (shell/hyprmac-notas)"
sed "s|/home/igor/Projects/hyprmac|$H|g" "$H/shell/dev.hyprmac.Notes.desktop" \
  > "$HOME/.local/share/applications/dev.hyprmac.Notes.desktop"

step "Journal (shell/hyprmac-diario)"
sed "s|/home/igor/Projects/hyprmac|$H|g" "$H/shell/dev.hyprmac.Journal.desktop" \
  > "$HOME/.local/share/applications/dev.hyprmac.Journal.desktop"

step "Photos (shell/hyprmac-fotos)"
sed "s|/home/igor/Projects/hyprmac|$H|g" "$H/shell/dev.hyprmac.Photos.desktop" \
  > "$HOME/.local/share/applications/dev.hyprmac.Photos.desktop"

step "Calculator (shell/hyprmac-calculadora)"
sed "s|/home/igor/Projects/hyprmac|$H|g" "$H/shell/dev.hyprmac.Calculator.desktop" \
  > "$HOME/.local/share/applications/dev.hyprmac.Calculator.desktop"

step "Pré-Visualização (PDF e imagens)"
sed "s|/home/igor/Projects/hyprmac|$H|g" "$H/shell/dev.hyprmac.Preview.desktop" \
  > "$HOME/.local/share/applications/dev.hyprmac.Preview.desktop"
# PDFs e imagens abrem no Preview do hyprmac, como no Mac
xdg-mime default dev.hyprmac.Preview.desktop application/pdf image/png image/jpeg image/gif \
  image/webp image/tiff image/bmp

step "Apps do sistema com nomes do Mac (shell/apps)"
# Photo Booth, Calculator e TextEdit; Papers e Loupe ficam só em "Abrir com"
# (NoDisplay), porque o Preview é o app do hyprmac
cp "$H"/shell/apps/*.desktop "$HOME/.local/share/applications/"
for desktop in "$H"/shell/app-launchers/*.desktop; do
  [ -f "$desktop" ] || continue
  target="$HOME/.local/share/applications/${desktop##*/}"
  temporary=$(mktemp "$HOME/.local/share/applications/.hyprmac-app.XXXXXX")
  sed "s|/home/igor/Projects/hyprmac|$H|g" "$desktop" > "$temporary"
  if [ -f "$target" ] && cmp -s "$temporary" "$target"; then
    rm "$temporary"
    continue
  fi
  if [ -e "$target" ]; then
    backup "$target" "applications/${desktop##*/}"
  fi
  chmod 644 "$temporary"
  mv "$temporary" "$target"
done
command -v gnome-text-editor >/dev/null && xdg-mime default org.gnome.TextEditor.desktop text/plain

step "Permissões dos scripts"
chmod +x "$H"/scripts/* "$H"/shell/hyprmac-shell "$H"/shell/hyprmac-ajustes "$H"/shell/hyprmac-preview "$H"/shell/hyprmac-notas "$H"/shell/hyprmac-diario "$H"/shell/hyprmac-fotos "$H"/shell/hyprmac-calculadora "$H"/shell/hyprmac-app "$H"/waybar/scripts/*.sh

step "Tema ($mode)"
"$H/scripts/theme" "$mode"

if command -v hyprctl >/dev/null && [ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]; then
  step "Recarregando Hyprland"
  hyprctl reload >/dev/null
fi

step "Pronto. Faça logout/login para o autostart (waybar e hyprmac-shell) valer."
