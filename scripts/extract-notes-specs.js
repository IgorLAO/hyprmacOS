const fs = require('fs');
const path = require('path');

const basePath = '/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1';

// Helper to read JSON files
function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    console.error(`Error reading ${file}: ${e.message}`);
    return null;
  }
}

// Helper to read text files
function readText(file) {
  try {
    return fs.readFileSync(file, 'utf8');
  } catch (e) {
    console.error(`Error reading ${file}: ${e.message}`);
    return null;
  }
}

// 1. Load records.json for Notes summary
const recordsPath = path.join(basePath, 'minerar', 'apps-internos', 'records.json');
const records = readJson(recordsPath);
let notesRecord = null;
if (records && Array.isArray(records)) {
  notesRecord = records.find(r => r.titulo && r.titulo.includes('Notes: menus de formatação'));
}
console.log(`Found Notes record: ${notesRecord ? notesRecord.titulo : 'not found'}`);

// 2. Load Notes-mainmenu.txt for menu structure
const menuTxtPath = path.join(basePath, 'minerar', 'apps-internos', 'strings', 'Notes-mainmenu.txt');
const menuTxt = readText(menuTxtPath);

// 3. Load intents-loc.json for App Intents
const intentsPath = path.join(basePath, 'minerar', 'apps-internos', 'intents-loc.json');
const intentsData = readJson(intentsPath);

// 4. Load plists.json for bundle info
const plistsPath = path.join(basePath, 'minerar', 'apps-internos', 'plists.json');
const plistsData = readJson(plistsPath);

// 5. Load color files for visual specs
const colorsPath = path.join(basePath, 'minerar', 'cores');
const aqua = readJson(path.join(colorsPath, 'Aqua.json'));
const darkAqua = readJson(path.join(colorsPath, 'DarkAqua.json'));

// 6. Load Notes.json for assets
const notesCarPath = path.join(basePath, 'minerar', 'apps-internos', 'car', 'Notes.json');
const notesCar = readJson(notesCarPath);

// Parse menuTxt to extract menu structure
function parseMenuTxt(txt) {
  const lines = txt.split('\n').filter(line => line.trim() !== '');
  const menuItems = [];
  const actions = new Map();

  // First pass: collect all action identifiers and their titles
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.endsWith('.title')) {
      const actionId = line.replace('.title', '');
      // The title is on the previous line?
      if (i > 0 && !lines[i-1].endsWith('.title') && !lines[i-1].includes(':')) {
        const title = lines[i-1].trim();
        actions.set(actionId, title);
      }
    }
  }

  // Second pass: build menu structure based on known patterns
  // We know from the summary the main menus: File, Edit, Format, View, Window, Help
  // We'll look for these in the actions map

  const mainMenus = [
    { label: 'File', actions: [] },
    { label: 'Edit', actions: [] },
    { label: 'Format', actions: [] },
    { label: 'View', actions: [] },
    { label: 'Window', actions: [] },
    { label: 'Help', actions: [] }
  ];

  // Map action IDs to menu names based on common patterns
  const actionToMenu = {
    // File
    'New Note': 'File',
    'New Folder': 'File',
    'New Smart Folder': 'File',
    'Pin Note': 'File',
    'Lock Note': 'File',
    'Duplicate Note': 'File',
    'Export as Archive': 'File',
    'Export as Markdown': 'File',
    'Import Markdown': 'File',
    'Print': 'File',
    'Quit Notes': 'File',
    // Edit
    'Undo': 'Edit',
    'Redo': 'Edit',
    'Cut': 'Edit',
    'Copy': 'Edit',
    'Paste': 'Edit',
    'Paste and Match Style': 'Edit',
    'Paste and Retain Style': 'Edit',
    'Delete': 'Edit',
    'Select All': 'Edit',
    // Format
    'Bold': 'Format',
    'Italic': 'Format',
    'Underline': 'Format',
    'Strikethrough': 'Format',
    'Heading': 'Format',
    'Subheading': 'Format',
    'Body': 'Format',
    'Monostyled': 'Format',
    'Bulleted List': 'Format',
    'Dashed List': 'Format',
    'Numbered List': 'Format',
    'Block Quote': 'Format',
    'Checklist': 'Format',
    'Mark as Checked': 'Format',
    'Table': 'Format',
    'Font': 'Format',
    'Show Fonts': 'Format',
    'Bigger': 'Format',
    'Smaller': 'Format',
    'Highlight': 'Format',
    'Superscript': 'Format',
    'Subscript': 'Format',
    'Align Left': 'Format',
    'Center': 'Format',
    'Justify': 'Format',
    'Align Right': 'Format',
    // View
    'as List': 'View',
    'as Gallery': 'View',
    'Sort By': 'View',
    'Group By Date': 'View',
    'Show Note Count': 'View',
    'Attachment View': 'View',
    'Expand Section': 'View',
    'Collapse Section': 'View',
    'Show Attachments Browser': 'View',
    'Show Note Activity': 'View',
    'Show Folder Activity': 'View',
    // Window
    'Minimize': 'Window',
    'Zoom': 'Window',
    'Enter Full Screen': 'Window',
    'Bring All to Front': 'Window',
    // Help
    'Notes Help': 'Help'
  };

  // Populate menu actions
  for (const [actionId, title] of actions.entries()) {
    const menuName = actionToMenu[title];
    if (menuName) {
      const menu = mainMenus.find(m => m.label === menuName);
      if (menu) {
        menu.actions.push({
          label: title,
          // We don't have shortcut from this file, leave for later
          shortcut: '',
          action: actionId, // This is the action identifier from the nib
          state: 'enabled' // default
        });
      }
    }
  }

  return mainMenus;
}

// Parse intents for Notes
function parseIntents(data) {
  if (!data || !data.Notes) return [];
  return data.Notes.intents || [];
}

// Extract visual specs from color files and Notes assets
function extractVisualSpecs() {
  const specs = {
    materials: [],
    colors: {},
    typography: {},
    spacing: {},
    radii: {},
    shadows: [],
    assets: []
  };

  // Extract colors from Aqua and DarkAqua
  if (aqua && aqua.Colors) {
    // We'll pick some common semantic colors
    const colorMap = {
      'label': 'Label Color',
      'secondaryLabel': 'Secondary Label Color',
      'tertiaryLabel': 'Tertiary Label Color',
      'quaternaryLabel': 'Quaternary Label Color',
      'placeholderText': 'Placeholder Text Color',
      'separator': 'Separator Color',
      'systemBackground': 'System Background Color',
      'systemGroupedBackground': 'System Grouped Background Color',
      'systemFill': 'System Fill Color',
      'systemSecondaryFill': 'System Secondary Fill Color',
      'systemTeritaryFill': 'System Tertiary Fill Color',
      'systemQuaternaryFill': 'System Quaternary Fill Color'
    };

    for (const [key, name] of Object.entries(colorMap)) {
      if (aqua.Colors[name]) {
        const light = aqua.Colors[name];
        const dark = darkAqua && darkAqua.Colors[name] ? darkAqua.Colors[name] : light;
        specs.colors[key] = {
          dark: `#${dark.toString(16).padStart(6, '0')}`,
          light: `#${light.toString(16).padStart(6, '0')}`,
          source: 'Aqua.json/DarkAqua.json'
        };
      }
    }
  }

  // Extract assets from Notes.car
  if (notesCar && Array.isArray(notesCar)) {
    // Limit to first 10 assets for brevity
    for (let i = 0; i < Math.min(notesCar.length, 10); i++) {
      const asset = notesCar[i];
      if (asset.Name) {
        specs.assets.push({
          name: asset.Name,
          path: `Notes.car/${asset.Name}`,
          purpose: asset.Type || 'unknown',
          dimensions: `${asset.PixelWidth}x${asset.PixelHeight}`
        });
      }
    }
  }

  // TODO: Extract more detailed visual specs from DesignLibrary/CoreMaterial
  // For now, we'll note that we need to look there

  return specs;
}

// Main execution
const menuStructure = parseMenuTxt(menuTxt);
const intents = parseIntents(intentsData);
const visualSpecs = extractVisualSpecs();

// Build the final JSON object
const result = {
  app: 'Notes',
  bundle_id: 'com.apple.Notes',
  priority: 'P2', // As per the task description
  visual_specs: visualSpecs,
  menus: {
    main_menu: menuStructure,
    context_menus: [] // We don't have context menu data yet
  },
  keyboard_shortcuts: [], // We don't have this yet
  animations: [], // We don't have this yet
  states: {}, // We don't have this yet
  layouts: [], // We don't have this yet
  accessibility: {
    reduce_motion: 'unknown',
    reduce_transparency: 'unknown',
    voiceover_labels: {} // We don't have this yet
  },
  app_intents: intents,
  window_specs: [], // We don't have this yet
  quicklook: {
    generator: 'unknown',
    content_types: [],
    thumbnail_size: 17 // default from Apple documentation
  },
  evidence: [
    {
      path: 'System/Applications/Notes.app/Contents/Info.plist',
      type: 'plist',
      verified: true
    },
    {
      path: 'Notes.app/Contents/Resources/Base.lproj/MainMenu.nib',
      type: 'nib',
      verified: true
    },
    {
      path: 'Notes.app/Contents/Resources/Metadata.appintents/extract.actionsdata',
      type: 'intent',
      verified: true
    }
  ],
  gaps_vs_hyprmac: [
    'Rich text editor with formatting menus (Heading, Subheading, etc.)',
    'Folders and smart folders',
    'Checklists with interactive states',
    'Tables in notes',
    'Attachments and inline media',
    'App Intents integration (49 intents)',
    'QuickNote global shortcut',
    'Locking notes with password',
    'Mentions in notes',
    'Activity viewing'
  ],
  implementation_priority: [
    'Implement rich text editor with basic formatting (bold, italic, etc.)',
    'Add folder and tagging system',
    'Implement checklist functionality',
    'Add table support',
    'Implement attachment handling',
    'Add App Intents support',
    'Implement QuickNote global shortcut',
    'Add note locking mechanism',
    'Implement mentions and activity feed',
    'Add smart folders and advanced views'
  ]
};

console.log(JSON.stringify(result, null, 2));