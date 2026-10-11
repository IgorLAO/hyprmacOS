// Agent Loader - carrega as dependências e configuração para cada agente
const fs = require('fs');
const path = require('path');

const agentType = process.argv[process.argv.indexOf('--agent') + 1];

// Configurações específicas por agente
const agentConfigs = {
  visual: {
    focus: ['materials', 'colors', 'typography', 'spacing', 'radii', 'shadows', 'assets'],
    sources: [
      'extraido/CoreMaterial/',
      'extraido/DesignLibrary/',
      'minerar/apps-internos/car/Notes.json',
      'minerar/cores/',
      'minerar/apps-internos/plists.json'
    ]
  },
  ux: {
    focus: ['menus', 'keyboard_shortcuts', 'states', 'layouts', 'accessibility'],
    sources: [
      'minerar/apps-internos/strings/Notes-mainmenu.txt',
      'minerar/apps-internos/car/Notes.json',
      'minerar/apps-internos/plists.json',
      'minerar/re-auto/'
    ]
  },
  intents: {
    focus: ['app_intents', 'parameters', 'phrases', 'activities', 'urls'],
    sources: [
      'minerar/apps-internos/intents-loc.json',
      'minerar/apps-internos/entitlements-symbols.json',
      'minerar/apps-internos/plists.json',
      'minerar/apps-internos/records.json'
    ]
  },
  glass: {
    focus: ['glass_parameters', 'quicklook', 'refraction', 'animations'],
    sources: [
      'minerar/glass-parameters.json',
      'minerar/apps-internos/quicklook-plugins.json',
      'minerar/re-auto/',
      'extraido/CoreMaterial/'
    ]
  }
};

const config = agentConfigs[agentType] || {};
console.log(`[AGENT:${agentType}] Carregado com foco em: ${config.focus.join(', ')}`);

module.exports = {
  agentType,
  config,
  basePath: process.env.HOME + '/.local/share/hyprmac-pesquisa/macos-26.6.1'
};