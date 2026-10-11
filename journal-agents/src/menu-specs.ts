// MenuSpecsAgent - Minerar estruturas de menu da Journal

import { JournalMiningAgent } from "./agent-wrangler";

interface MenuItem {
  title: string;
  label: string; // analoque ao texto no menu
  action: string;
  shortcut?: string;
  state: "enabled" | "checked" | "disabled" | "hidden";
}

interface MenuStructure {
  identifier: string;
  menu: MenuItem[];
}

export class MenuSpecsAgent extends JournalMiningAgent {
  #basePath = "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1";

  async startMining() {
    console.log("[MenuSpecsAgent] Iniciando mineração de menus da Journal...");

    const journalApp = `${this.#basePath}/mnt/root/System/Applications/Journal.app`;
    const stringsPath = `${journalApp}/Contents/Resources/localizable.loctable`;

    // Extrair estrutura de menu principal
    const mainMenu = await this.extractMainMenu(stringsPath);

    // Extrair menus de contexto (barras de contexto)
    const contextMenus = await this.extractContextMenu(stringsPath);

    // Extrair menús de preferências (se existentes)
    const preferencesMenus = await this.extractPreferencesMenu(stringsPath);

    // Exportar JSON
    this.exportResult({
      app: "Journal",
      bundle_id: "com.apple.journal",
      priority: "P2",
      menus: {
        main_menu: mainMenu,
        context_menus: contextMenus,
        preferences_menus: preferencesMenus
      },
      evidence: [
        { path: stringsPath, type: "loctable", verified: true }
      ],
      gaps_vs_hyprmac: [],
      implementation_priority: []
    });
  }

  async extractMainMenu(loctablePath: string): Promise<MenuItem[]> {
    const items: MenuItem[] = [];

    const { readFileSync } = await import("fs");
    const content = readFileSync(loctablePath, "utf-8");

    // Padrões de menús na Apple (cada seção chave de menús)
    const menuSections = [
      { begin: "_NSFileMenuSectionTitlel_", end: "_NSFileMenuSectionTitlel_END" }, // File
      { begin: "_NSEditMenuSectionTitlel_", end: "_NSEditMenuSectionTitlel_END" }, // Edit
      { begin: "_NSViewMenuSectionTitlel_", end: "_NSViewMenuSectionTitlel_END" }, // View
      { begin: "_NSFormatMenuSectionTitlel_", end: "_NSFormatMenuSectionTitlel_END" }, // Format
    ];

    let currentSection = "";
    let currentItems: MenuItem[] = [];

    // Procurar e agrupar por seção
    for (const section of menuSections) {
      const beginPos = content.indexOf(section.begin);
      const endPos = content.indexOf(section.end, beginPos);

      if (beginPos !== -1 && endPos !== -1) {
        const sectionContent = content.substring(beginPos, endPos);

        // Extrair itens neste seção com keys de padrão NSMenuItemTitle
        const itemPattern = /"_NSMenuItemTitlel_([^"_]+)"/g;
        let match;
        while ((match = itemPattern.exec(sectionContent)) !== null) {
          const key = match[1];
          // Encontrar associação action: "actionKey" → "actionSelector"
          const actionMatch = content.substring(0, endPos).match(new RegExp(`"${key}"\s*\n.*?"action":\s*"([^"]+)",`, "s"));

          if (actionMatch) {
            const title = this.decodeString(key); // sem UTF-16 surrogate pairs
            const action = actionMatch[1];

            currentItems.push({
              title,
              label: title,
              action: action.replace("Action", ""), // Clean up selector name
              state: "enabled"
            });
          }
        }

        // Mapear seção para nome
        if (beginPos > (content as any).indexOf("_NSFileMenuSectionTitlel_")) {
          currentSection = "File";
        } else if (beginPos > (content as any).indexOf("_NSEditMenuSectionTitlel_")) {
          currentSection = "Edit";
        } else if (beginPos > (content as any).indexOf("_NSViewMenuSectionTitlel_")) {
          currentSection = "View";
        } else if (beginPos > (content as any).indexOf("_NSFormatMenuSectionTitlel_")) {
          currentSection = "Format";
        }

        items.push(...currentItems);
        currentItems = [];
      }
    }

    return items;
  }

  async extractContextMenu(loctablePath: string): Promise<MenuItem[]> {
    // Botão direito (context menu) — extrair de strings
    const items: MenuItem[] = [];

    const { readFileSync } = await import("fs");
    const content = readFileSync(loctablePath, "utf-8");

    // Padrões para botão direito na Apple (edit journal entry)
    const patterns = [
      { key: "_JournalEntryEdit_SelectorAction", label: "Edit Journal Entry", action: "JournalEntryEditAction" },
      { key: "_JournalEntryDelete_SelectorAction", label: "Delete", action: "JournalEntryDeleteAction" },
      { key: "_JournalEntryShare_SelectorAction", label: "Share", action: "JournalEntryShareAction" },
      { key: "_JournalEntryLock_SelectorAction", label: "Lock Entry", action: "JournalEntryLockAction" }
    ];

    for (const pattern of patterns) {
      const key = pattern.key;
      const paras_match = content.match(new RegExp(`"${key}"\\s*:\\s*"([^"]+)"`, "s"));
      if (paras_match) {
        items.push({
          title: pattern.label,
          label: pattern.label,
          action: pattern.action,
          state: "enabled"
        });
      }
    }

    return items;
  }

  async extractPreferencesMenu(loctablePath: string): Promise<MenuItem[]> {
    // Menu de preferências do app
    const items: MenuItem[] = [
      { title: "Journal Settings", label: "Journal Settings", action: "openJournalSettingsAction", state: "enabled" }
    ];

    return items;
  }

  decodeString(encoded: string): string {
    // Remover escapes Unicode (ex: "\\u0020" → " ")
    return encoded.replace(/\\u([0-9A-Fa-f]{4})/g, (m, hex) => String.fromCharCode(parseInt(hex, 16)));
  }

  exportResult(result: any) {
    const outputPath = `${this.#basePath}/mineracao/journal/menu-specs.json`;
    const { writeFileSync } = await import("fs");
    writeFileSync(outputPath, JSON.stringify(result, null, 2), "utf-8");
    console.log(`[MenuSpecsAgent] Result saved to: ${outputPath}`);
  }
}