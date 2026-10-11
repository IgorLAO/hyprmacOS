#!/usr/bin/env python3
"""Registra a validação inicial curada dos componentes prioritários."""
from __future__ import annotations

from common import PROJECT, connect

MAIN_PATHS = {
    "Control Center": "/mnt/macos/root/System/Library/CoreServices/ControlCenter.app",
    "System Settings": "/mnt/macos/root/System/Applications/System Settings.app",
    "Dock": "/mnt/macos/root/System/Library/CoreServices/Dock.app",
    "Top Bar / SystemUIServer": "/mnt/macos/root/System/Library/CoreServices/SystemUIServer.app",
    "AppKit": "/mnt/macos/root/System/Library/Frameworks/AppKit.framework",
    "CoreUI": "/mnt/macos/root/System/Library/PrivateFrameworks/CoreUI.framework",
}

# Somente nomes que respondem a perguntas de estrutura, estado ou comportamento.
CURATED = {
    "Control Center": [
        ("classe", "BluetoothContentView", "View de conteúdo do módulo Bluetooth.", "SIMBOLO"),
        ("classe", "BluetoothCompactView", "Representação compacta do Bluetooth.", "SIMBOLO"),
        ("classe", "BluetoothExpandedView", "Representação expandida do Bluetooth.", "SIMBOLO"),
        ("classe", "BluetoothDeviceDetailsView", "View de detalhes de um dispositivo Bluetooth.", "SIMBOLO"),
        ("classe", "WiFiContentView", "View de conteúdo do módulo Wi-Fi.", "SIMBOLO"),
        ("classe", "WiFiMenuExtraView", "Representação de Wi-Fi como extra da barra.", "SIMBOLO"),
        ("classe", "WiFiNetworkStatusView", "View de estado de uma rede Wi-Fi.", "SIMBOLO"),
        ("classe", "NowPlayingContentView", "View de conteúdo do módulo Tocando Agora.", "SIMBOLO"),
        ("classe", "MenuExtraPopoversController", "Controlador de popovers dos extras da barra.", "SIMBOLO"),
        ("estado", "isInactiveMenuBarView", "Há estado explícito de view inativa na barra de menus.", "SIMBOLO"),
        ("config", "ShowInMenuBar", "Controles podem declarar exposição na barra de menus.", "SIMBOLO"),
    ],
    "System Settings": [
        ("estrutura", "SettingsExtension", "O executável contém infraestrutura para painéis fornecidos por extensões.", "SIMBOLO"),
        ("estrutura", "Sidebar", "A interface principal possui conceitos explícitos de sidebar.", "SIMBOLO"),
        ("estrutura", "Toolbar", "A interface principal possui conceitos explícitos de toolbar.", "SIMBOLO"),
    ],
    "Dock": [
        ("config", "magnification", "O Dock possui configuração/comportamento explícito de magnificação.", "SIMBOLO"),
        ("config", "autohide", "O Dock possui estado de ocultação automática.", "SIMBOLO"),
        ("comportamento", "minimize", "O binário contém caminhos de comportamento para minimização.", "SIMBOLO"),
        ("estado", "badge", "Tiles do Dock admitem estado de badge.", "SIMBOLO"),
    ],
    "Top Bar / SystemUIServer": [
        ("estrutura", "MenuExtra", "SystemUIServer contém infraestrutura de extras da barra.", "SIMBOLO"),
        ("estrutura", "StatusItem", "SystemUIServer contém infraestrutura de itens de estado.", "SIMBOLO"),
        ("relacao", "ControlCenter", "O binário referencia conceitos do Control Center.", "SIMBOLO"),
    ],
    "AppKit": [
        ("estrutura", "NSAlertPanel", "AppKit fornece um NIB específico para o painel de alerta padrão.", "DIRETO"),
        ("classe", "NSButton", "NSAlertPanel contém controles NSButton.", "SIMBOLO"),
        ("classe", "NSWindow", "NSAlertPanel é estruturado sobre uma janela AppKit.", "SIMBOLO"),
    ],
    "CoreUI": [
        ("estrutura", "DesignLibrary-macOS", "CoreUI inclui uma biblioteca de design específica do macOS.", "DIRETO"),
        ("estado", "appearance repositories", "Há catálogos separados para claro/escuro, vibrante e contraste aumentado.", "ASSET"),
    ],
}

EVIDENCE = {
    "Control Center": MAIN_PATHS["Control Center"] + "/Contents/MacOS/ControlCenter",
    "System Settings": MAIN_PATHS["System Settings"] + "/Contents/MacOS/System Settings",
    "Dock": MAIN_PATHS["Dock"] + "/Contents/MacOS/Dock",
    "Top Bar / SystemUIServer": MAIN_PATHS["Top Bar / SystemUIServer"] + "/Contents/MacOS/SystemUIServer",
    "AppKit": MAIN_PATHS["AppKit"] + "/Versions/C/Resources/NSAlertPanel.nib",
    "CoreUI": MAIN_PATHS["CoreUI"] + "/Versions/A/Resources/DesignLibrary-macOS.bundle/Contents/Resources/macOSRepositories",
}

MAPPINGS = {
    "Control Center": [("shell/hyprmac-shell", "PARCIAL", "Possui painel e detalhes internos de Wi-Fi/Bluetooth; faltam confirmar estados e geometria Tahoe.", "Usar as views compact/expanded como roteiro de comparação.")],
    "System Settings": [("shell/hyprmac-ajustes", "PARCIAL", "Implementa app próprio, mas a composição por extensões e a hierarquia nativa ainda não foram comparadas profundamente.", "Mapear sidebar/toolbar painel a painel.")],
    "Dock": [("shell/hyprmac-shell", "PARCIAL", "Magnificação existe, porém fica desativada por padrão e sua curva não foi confirmada contra Tahoe.", "Confirmar parâmetros antes de ajustar.")],
    "Top Bar / SystemUIServer": [("waybar/config.jsonc", "PARCIAL", "Waybar cobre menus e status, com arquitetura diferente de MenuExtra/StatusItem.", "Mapear ownership e estados inativos dos extras."), ("waybar/style.css", "PARCIAL", "Aparência implementada; estados nativos ainda parcialmente documentados.", "Comparar estado inativo e popovers.")],
    "AppKit": [("shell/style.css", "NAO_APLICAVEL", "GTK substitui AppKit; equivalência ocorre no nível de componentes e estilo.", "Usar NIBs específicos como referência estrutural.")],
    "CoreUI": [("hypr/vidro-presets.lua", "NAO_APLICAVEL", "CoreUI não possui equivalente direto; presets e CSS reproduzem parte do resultado visual.", "Consultar catálogos somente para perguntas visuais concretas."), ("shell/style.css", "NAO_APLICAVEL", "CSS consome decisões visuais, não catálogos CoreUI.", "Registrar diferenças por asset quando investigadas.")],
}


def main() -> None:
    conn = connect()
    # Descarta o lote exploratório automático; as descobertas abaixo são a curadoria útil.
    conn.execute("DELETE FROM descobertas WHERE tipo='simbolo' AND valor='Nome encontrado por consulta direcionada de strings.'")
    ids = {r["nome"]: r["id"] for r in conn.execute("SELECT id,nome FROM componentes")}
    for name, path in MAIN_PATHS.items():
        conn.execute("UPDATE componentes SET path_principal=? WHERE id=?", (path, ids[name]))
    for name, discoveries in CURATED.items():
        file_row = conn.execute("SELECT id FROM arquivos WHERE path=?", (EVIDENCE[name],)).fetchone()
        file_id = file_row[0] if file_row else None
        for kind, key, value, confidence in discoveries:
            conn.execute("""INSERT OR IGNORE INTO descobertas
                            (componente_id,arquivo_id,tipo,chave,valor,evidencia,confianca,observacao)
                            VALUES(?,?,?,?,?,?,?,?)""",
                         (ids[name], file_id, kind, key, value, EVIDENCE[name], confidence,
                          "Validação inicial; aprofundar somente sob demanda."))
    for name, mappings in MAPPINGS.items():
        for relative, status, difference, recommendation in mappings:
            assert (PROJECT / relative).exists(), relative
            conn.execute("""INSERT INTO mapeamento_hyprmac(componente_id,arquivo_hyprmac,status,diferenca,recomendacao)
                            VALUES(?,?,?,?,?) ON CONFLICT(componente_id,arquivo_hyprmac) DO UPDATE SET
                            status=excluded.status,diferenca=excluded.diferenca,recomendacao=excluded.recomendacao,
                            atualizado_em=CURRENT_TIMESTAMP""", (ids[name], relative, status, difference, recommendation))
    relations = [
        ("Control Center", "usa", "CoreUI", "Inferido pela responsabilidade visual; confirmar ligação específica quando necessário."),
        ("Top Bar / SystemUIServer", "coordena", "Control Center", "Referência direta a ControlCenter no binário do SystemUIServer."),
        ("AppKit", "usa", "CoreUI", "Relação de framework visual; evidência detalhada fica pendente."),
    ]
    for origin, relation, destination, note in relations:
        conn.execute("""INSERT OR IGNORE INTO relacoes(origem_tipo,origem_id,relacao,destino_tipo,destino_id,observacao)
                        VALUES('componente',? ,?,'componente',?,?)""", (ids[origin], relation, ids[destination], note))
    questions = {
        "Control Center": "Quais estados e transições exatos existem nos subpainéis Wi-Fi e Bluetooth?",
        "System Settings": "Qual é a hierarquia real de sidebar, toolbar e conteúdo no Tahoe?",
        "Dock": "Quais são a curva, alcance e escala exatos da magnificação?",
        "Top Bar / SystemUIServer": "Quais extras pertencem ao SystemUIServer e quais ao ControlCenter?",
        "AppKit": "Quais classes e constraints compõem alerts, sheets e traffic lights prioritários?",
        "CoreUI": "Quais assets respondem a cada estado visual investigado pelo Hyprmac?",
    }
    for name, question in questions.items():
        conn.execute("INSERT OR IGNORE INTO investigacoes(componente_id,pergunta,status) VALUES(?,?,'ABERTA')", (ids[name], question))
    # Recria o índice para eliminar tokens de qualquer lote exploratório removido.
    conn.execute("DELETE FROM conhecimento_fts")
    conn.execute("""INSERT INTO conhecimento_fts(rowid,componente,tipo,chave,valor,evidencia,observacao)
                    SELECT d.id,COALESCE(c.nome,''),d.tipo,d.chave,d.valor,
                           COALESCE(d.evidencia,''),COALESCE(d.observacao,'')
                    FROM descobertas d LEFT JOIN componentes c ON c.id=d.componente_id""")
    conn.commit()
    print("Validação inicial curada registrada para 6 componentes.")


if __name__ == "__main__":
    main()
