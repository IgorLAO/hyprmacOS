// VisualSpecsAgent - Minerar especificações visuais da Journal (materiais, cores, tipografia)

import { JournalMiningAgent } from "./agent-wrangler";

interface MaterialRecipe {
  styles: {
    stroke?: string;
    fill?: string;
  };
  baseMaterial: {
    materialFiltering: {
      luminanceAmount: number;
      luminanceValues: [number, number, number, number];
      saturation: number;
      blurRadius: number;
      backdropScale: number;
      blurAtEnd: boolean;
    };
  };
}

interface ColorSet {
  dark: string;
  light: string;
  source: string;
}

export class VisualSpecsAgent extends JournalMiningAgent {
  #basePath = "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1";

  async startMining() {
    console.log("[VisualSpecsAgent] Iniciando mineração de especificações visuais da Journal...");

    const journalPath = `${this.#basePath}/mnt/root/System/Applications/Journal.app/Contents/Resources`;
    const materialRecipes = `${journalPath}/.materialrecipes` || `${this.#basePath}/extraido/CoreMaterial`;
    const assetsPath = `${journalPath}/Assets.car`;

    // Buscar material recipes relevantes à Journal
    const materials = await this.extractMaterialRecipes(materialRecipes, [
      // Estes nomes são baseados no código-da-Apple e sugestões do HyprMac
      "journalEntry", "journalPanel", "journalModal", "journalInput"
    ]);

    // Extrair cores semânticas
    const colors = await this.extractSemanticColors(materialRecipes);

    // Extrair tipografia
    const typography = await this.extractTypography(assetsPath);

    // Extrair spacing tokens
    const spacing = await this.extractSpacing(tokensPath);

    // Extrair radii
    const radii = await this.extractRadii();
  }

  async extractMaterialRecipes(path: string, keywords: string[]): Promise<Array<{
    name: string;
    recipe: MaterialRecipe;
  }>> {
    const found: Array<{ name: string; recipe: MaterialRecipe }> = [];

    // Buscar por mediaRecipe e materialset na pasta do app
    const searchPaths = [
      `${this.#basePath}/mnt/root/System/Applications/Journal.app/Contents/Resources`,
      // Se não existir, usar CoreMaterial extraído (estilo do Dock)
      `${this.#basePath}/extraido/CoreMaterial`
    ];

    for (const searchPath of searchPaths) {
      for (const entry of await this._listDir(searchPath)) {
        if (entry.endsWith(".materialrecipe")) {
          try {
            const { readFileSync } = await import("fs");
            const recipePath = `${searchPath}/${entry}`;
            const content = readFileSync(recipePath, "utf-8");
            const recipe = JSON.parse(content);

            const name = entry.replace(".materialrecipe", "");

            // Verificar keywords
            const matchesKeyword = keywords.some(kw =>
              name.toLowerCase().includes(kw.toLowerCase())
            );

            if (matchesKeyword) {
              found.push({ name, recipe });
            }
          } catch (e) {
            console.warn(`Failed to parse ${entry}:`, e);
          }
        }
      }
    }

    return found;
  }

  async extractSemanticColors(materialPath: string): Promise<Record<string, ColorSet>> {
    // Buscar car archivos do Assets.car
    // Nota: brute-force parse manual não é trivial; vamos pegar de MLs e strings
    const found: Record<string, ColorSet> = {};

    // Extrair de material recipes se contiverem tcdefs
    const recipes = await this.extractMaterialRecipes(materialPath, []);
    for (const { recipe } of recipes) {
      if (recipe.baseMaterial?.materialFiltering) {
        const filter = recipe.baseMaterial.materialFiltering;
        const lightColors = this.luminanceToRGB(filter.luminanceValues[1]);
        const darkColors = this.luminanceToRGB(filter.luminanceValues[2]);

        if (filter.saturation > 0) {
          // A entrada não tem nome de token; vamos anotar como "journal-material-XXX"
          // Aplicação no HyprMac tem precedência semântica de tokens
        }
      }
    }

    return found;
  }

  async extractTypography(assetsPath: string): Promise<Record<string, any>> {
    // Distração baseada no Assets.car com object-controller
    const typography: Record<string, any> = {};
    // Nota: full parse do Assets.car requer ferramenta especializada como actool
    // Buscar referências em strings/intents como "12 pt. SF Pro", "13 pt. Semibold"
    const stringsPath = `${this.#basePath}/mnt/root/System/Applications/Journal.app/Contents/Resources/Localizable.loctable`;
    const { readFileSync } = await import("fs");
    const content = readFileSync(stringsPath, "utf-8");

    // Regex para encontrar tokens de tipografia (Em vez de NOME do token, é descrição)
    // Ex: "Aa", "12 pt. SF Pro Regular", "13 pt. system-ui.semibold-semibold", "Label"
    const fontPattern = /13 pt\.\s*([\w\s\-\(\).'"]+)/gi;
    let match;
    while ((match = fontPattern.exec(content)) !== null) {
      const fontString = match[1].trim();
      typography[fontString] = {
        source: stringsPath,
        file_line: match.index,
        detected_at: "string-literal" // Não é token Mac padrão
      };
    }

    return typography;
  }

  spawn(verb: string, args: string[]) {
    return this.exec(verb, args, {
      // Procurar no PATH; em ambientes sem macports/userbrew, executável pode estar em ~/Applications/.app_contents/MacOS/
      // Aqui, eu forço a confiança no path se existir (no HyprMac)
      extra_search_paths: [
        `${this.#basePath}/mnt/root/System/Applications/Journal.app/Contents/MacOS/Journal`
      ]
    });
  }

  _listDir(dir: string): Promise<[string]> {
    return this.execSync("ls", [dir], { output: "content" });
  }

  luminanceToRGB(luminance: number): string {
    // simpler_ring: linear to sRGB
    const sRGB = (v: number) => {
      if (v <= 0.0031308) return Math.max(0, 12.92 * v);
      return Math.max(0, 1.055 * Math.pow(v, 1.0 / 2.4) - 0.055);
    };
    const R = sRGB(luminance * 12.92 + 0.055 / 12.92);
    const G = sRGB(luminance);
    const B = sRGB(1.0 - luminance);
    return `rgba(${Math.round(R * 255)}, ${Math.round(G * 255)}, ${Math.round(B * 255)}, 1.0)`;
  }
}