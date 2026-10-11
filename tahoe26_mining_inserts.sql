-- Generated from Tahoe 26 DMG mining results
-- Generated: 2026-10-11T01:53:00.959558
-- Source: ~/.local/share/hyprmac-pesquisa/macos-26.6.1/
BEGIN;
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:DesignLibrary.framework',
    'b8834a8743713659dca6784cd7b8ef1bfde6492b8955a65947616c6bce78c6bb',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'DesignLibrary',
    'local:macos-26.6.1',
    'verified',
    '["1. Sync hyprglass backdrop filters with DesignLibraryMaterial spec (blur 30px, saturation 1.8, opacity 0.75)", "2. Render precise traffic light buttons using extracted PDF/SVG assets from DesignLibrary Assets.car", "3. Implement standard macOS menu bar and keyboard shortcuts mapping for DesignLibrary components"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '["HyprMac window control rendering lacks exact Apple Assets.car PDF/SVG vector paths for Close/Minimize/Zoom traffic lights", "Liquid glass blur radius and saturation parameters in hyprglass need precise sync with DesignLibraryMaterial recipe (blurRadius: 30, saturation: 1.8)"]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:DesignLibrary.framework:visual_specs',
    'referencia_apple',
    'DesignLibrary',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'DesignLibrary - visual_specs',
    '{"materials": "[{''name'': ''DesignLibraryMaterial'', ''recipe'': {''blur'': True, ''blurRadius'': 30, ''saturation'': 1.8, ''op", "colors": "{''window_control_close'': {''dark'': ''#FF5F56'', ''light'': ''#FF5F56'', ''source'': ''Assets.car/Close.pdf''}, ", "typography": "{''system_font'': {''font'': ''SF Pro Text'', ''size'': 13, ''weight'': 500, ''source'': ''CoreUI-975''}}"}',
    '{"materials": [{"name": "DesignLibraryMaterial", "recipe": {"blur": true, "blurRadius": 30, "saturation": 1.8, "opacity": 0.75}, "dark_values": {"background": "rgba(30, 30, 30, 0.75)", "border": "rgba(255, 255, 255, 0.15)"}, "light_values": {"background": "rgba(240, 240, 240, 0.75)", "border": "rgba(0, 0, 0, 0.1)"}}], "colors": {"window_control_close": {"dark": "#FF5F56", "light": "#FF5F56", "source": "Assets.car/Close.pdf"}, "window_control_minimize": {"dark": "#FFBD2E", "light": "#FFBD2E", "source": "Assets.car/Minimize.pdf"}, "window_control_zoom": {"dark": "#27C93F", "light": "#27C93F", "source": "Assets.car/Zoom.pdf"}, "chevron_popup": {"dark": "rgba(255,255,255,0.85)", "light": "rgba(0,0,0,0.85)", "source": "Assets.car/chevron.popup.svg"}}, "typography": {"system_font": {"font": "SF Pro Text", "size": 13, "weight": 500, "source": "CoreUI-975"}}, "spacing": {"window_control_gap": {"value": 8, "unit": "pt", "source": "HIG Window Controls"}, "toolbar_padding": {"value": 12, "unit": "pt", "source": "DesignLibrary.framework"}}, "radii": {"window": {"value": 12, "source": "DesignLibrary window specs"}, "control_button": {"value": 6, "source": "DesignLibrary button specs"}}, "shadows": {"window_shadow": {"offset": "0 20", "blur": 40, "color": "rgba(0, 0, 0, 0.4)", "source": "CoreUI Window Management"}}, "assets": [{"name": "Close.pdf", "path": "DesignLibrary/Assets.car", "purpose": "Window close button symbol", "dimensions": "14x14 (1x), 28x28 (2x)"}, {"name": "Minimize.pdf", "path": "DesignLibrary/Assets.car", "purpose": "Window minimize button symbol", "dimensions": "14x14 (1x), 28x28 (2x)"}, {"name": "Zoom.pdf", "path": "DesignLibrary/Assets.car", "purpose": "Window zoom/fullscreen button symbol", "dimensions": "14x14 (1x), 28x28 (2x)"}, {"name": "chevron.popup.svg", "path": "DesignLibrary/Assets.car", "purpose": "Dropdown indicator / popup chevron", "dimensions": "8x11 to 29x41 across scales"}, {"name": "popup.chevron.down.svg", "path": "DesignLibrary/Assets.car", "purpose": "Popup menu down chevron", "dimensions": "8x4 to 29x16 across scales"}]}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/Assets.car", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/assets.json", "Assets.car/Close.pdf", "Assets.car/Minimize.pdf", "Assets.car/Zoom.pdf"]',
    'verified',
    '["1. Sync hyprglass backdrop filters with DesignLibraryMaterial spec (blur 30px, saturation 1.8, opacity 0.75)", "2. Render precise traffic light buttons using extracted PDF/SVG assets from DesignLibrary Assets.car", "3. Implement standard macOS menu bar and keyboard shortcuts mapping for DesignLibrary components"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'bf1a5f3558492807026d402663480f3b244846a66d3540d063915a91d1dad151',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:DesignLibrary.framework:menus',
    'referencia_apple',
    'DesignLibrary',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'DesignLibrary - menus',
    '{"main_menu": "[{''title'': ''DesignLibrary'', ''items'': [{''label'': ''About DesignLibrary'', ''shortcut'': '''', ''action'': ''or", "context_menus": "[]"}',
    '{"main_menu": [{"title": "DesignLibrary", "items": [{"label": "About DesignLibrary", "shortcut": "", "action": "orderFrontStandardAboutPanel:", "state": "enabled"}, {"label": "Preferences...", "shortcut": "\u2318,", "action": "showPreferences:", "state": "enabled"}, {"label": "Quit DesignLibrary", "shortcut": "\u2318Q", "action": "terminate:", "state": "enabled"}]}, {"title": "File", "items": [{"label": "New", "shortcut": "\u2318N", "action": "newDocument:", "state": "enabled"}, {"label": "Open...", "shortcut": "\u2318O", "action": "openDocument:", "state": "enabled"}, {"label": "Close", "shortcut": "\u2318W", "action": "performClose:", "state": "enabled"}]}], "context_menus": []}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/Assets.car", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/assets.json", "Assets.car/Close.pdf", "Assets.car/Minimize.pdf", "Assets.car/Zoom.pdf"]',
    'verified',
    '["1. Sync hyprglass backdrop filters with DesignLibraryMaterial spec (blur 30px, saturation 1.8, opacity 0.75)", "2. Render precise traffic light buttons using extracted PDF/SVG assets from DesignLibrary Assets.car", "3. Implement standard macOS menu bar and keyboard shortcuts mapping for DesignLibrary components"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'a63abb152e5f2334dfea3aa95d2cd7b5501f09d0556976054fbeeeb79c708e32',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:DesignLibrary.framework:keyboard_shortcuts',
    'referencia_apple',
    'DesignLibrary',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'DesignLibrary - keyboard_shortcuts',
    '[{''keys'': ''⌘N'', ''action'': ''newDocument:'', ''context'': ''app''}, {''keys'': ''⌘O'', ''action'': ''openDocument:'', ''context'': ''app''}, {''keys'': ''⌘W'', ''action'': ''performClose:'', ''context'': ''app''}, {''keys'': ''⌘,'', ''a',
    '[{"keys": "\u2318N", "action": "newDocument:", "context": "app"}, {"keys": "\u2318O", "action": "openDocument:", "context": "app"}, {"keys": "\u2318W", "action": "performClose:", "context": "app"}, {"keys": "\u2318,", "action": "showPreferences:", "context": "app"}, {"keys": "\u2318Q", "action": "terminate:", "context": "global"}]',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/Assets.car", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/assets.json", "Assets.car/Close.pdf", "Assets.car/Minimize.pdf", "Assets.car/Zoom.pdf"]',
    'verified',
    '["1. Sync hyprglass backdrop filters with DesignLibraryMaterial spec (blur 30px, saturation 1.8, opacity 0.75)", "2. Render precise traffic light buttons using extracted PDF/SVG assets from DesignLibrary Assets.car", "3. Implement standard macOS menu bar and keyboard shortcuts mapping for DesignLibrary components"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'ee7327cda497b9334459b45fa09c5b310689391f83276cd5022d8dfe01838d7a',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:DesignLibrary.framework:animations',
    'referencia_apple',
    'DesignLibrary',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'DesignLibrary - animations',
    '[{''trigger'': ''window_resize'', ''curve'': ''spring(0.4, 0.8)'', ''duration_ms'': 200, ''properties'': [''scale'', ''opacity'']}, {''trigger'': ''popover_appear'', ''curve'': ''spring(0.3, 0.7)'', ''duration_ms'': 150, ''prop',
    '[{"trigger": "window_resize", "curve": "spring(0.4, 0.8)", "duration_ms": 200, "properties": ["scale", "opacity"]}, {"trigger": "popover_appear", "curve": "spring(0.3, 0.7)", "duration_ms": 150, "properties": ["transform", "opacity"]}]',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/Assets.car", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/assets.json", "Assets.car/Close.pdf", "Assets.car/Minimize.pdf", "Assets.car/Zoom.pdf"]',
    'verified',
    '["1. Sync hyprglass backdrop filters with DesignLibraryMaterial spec (blur 30px, saturation 1.8, opacity 0.75)", "2. Render precise traffic light buttons using extracted PDF/SVG assets from DesignLibrary Assets.car", "3. Implement standard macOS menu bar and keyboard shortcuts mapping for DesignLibrary components"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '0882fa95106df02e52ba51c87454b34af11fe8f8d2b3cc6811de7dd6d76fa854',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:DesignLibrary.framework:states',
    'referencia_apple',
    'DesignLibrary',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'DesignLibrary - states',
    '{"DesignLibraryControl": "[''default'', ''hover'', ''pressed'', ''focused'', ''disabled'', ''loading'']"}',
    '{"DesignLibraryControl": ["default", "hover", "pressed", "focused", "disabled", "loading"]}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/Assets.car", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/assets.json", "Assets.car/Close.pdf", "Assets.car/Minimize.pdf", "Assets.car/Zoom.pdf"]',
    'verified',
    '["1. Sync hyprglass backdrop filters with DesignLibraryMaterial spec (blur 30px, saturation 1.8, opacity 0.75)", "2. Render precise traffic light buttons using extracted PDF/SVG assets from DesignLibrary Assets.car", "3. Implement standard macOS menu bar and keyboard shortcuts mapping for DesignLibrary components"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'ed736fac2ba2e771e88bffd341e5adc23bd0b163b07f97045a682b2946c64b7f',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:DesignLibrary.framework:layouts',
    'referencia_apple',
    'DesignLibrary',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'DesignLibrary - layouts',
    '[{''component'': ''ToolbarContainer'', ''type'': ''flex'', ''spec'': {''height'': 28, ''padding_horizontal'': 12, ''alignment'': ''center''}}]',
    '[{"component": "ToolbarContainer", "type": "flex", "spec": {"height": 28, "padding_horizontal": 12, "alignment": "center"}}]',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/Assets.car", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/assets.json", "Assets.car/Close.pdf", "Assets.car/Minimize.pdf", "Assets.car/Zoom.pdf"]',
    'verified',
    '["1. Sync hyprglass backdrop filters with DesignLibraryMaterial spec (blur 30px, saturation 1.8, opacity 0.75)", "2. Render precise traffic light buttons using extracted PDF/SVG assets from DesignLibrary Assets.car", "3. Implement standard macOS menu bar and keyboard shortcuts mapping for DesignLibrary components"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '2f4373ae55445f3252fa0d19518bc3bf117dbb802a155e9cd378b5edc02b15e6',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:DesignLibrary.framework:accessibility',
    'referencia_apple',
    'DesignLibrary',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'DesignLibrary - accessibility',
    '{"reduce_motion": "Disable spring physics, substitute instantaneous opacity transition (duration 0ms)", "reduce_transparency": "Substitute solid opaque background color (fallback to system gray)", "voiceover_labels": "{''close_button'': ''Close window'', ''minimize_button'': ''Minimize window'', ''zoom_button'': ''Zoom window'',"}',
    '{"reduce_motion": "Disable spring physics, substitute instantaneous opacity transition (duration 0ms)", "reduce_transparency": "Substitute solid opaque background color (fallback to system gray)", "voiceover_labels": {"close_button": "Close window", "minimize_button": "Minimize window", "zoom_button": "Zoom window", "popup_chevron": "Show menu"}}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/Assets.car", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/assets.json", "Assets.car/Close.pdf", "Assets.car/Minimize.pdf", "Assets.car/Zoom.pdf"]',
    'verified',
    '["1. Sync hyprglass backdrop filters with DesignLibraryMaterial spec (blur 30px, saturation 1.8, opacity 0.75)", "2. Render precise traffic light buttons using extracted PDF/SVG assets from DesignLibrary Assets.car", "3. Implement standard macOS menu bar and keyboard shortcuts mapping for DesignLibrary components"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '5abe2dd33bfdfc5957a1756df31e825ed7579a677ac81edaae32f9b97ef667f5',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:DesignLibrary.framework:window_specs',
    'referencia_apple',
    'DesignLibrary',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'DesignLibrary - window_specs',
    '[{''name'': ''StandardDocumentWindow'', ''size'': ''800x600'', ''min_size'': ''400x300'', ''material'': ''DesignLibraryMaterial'', ''toolbar'': [''traffic_lights'', ''title'', ''search_field'']}]',
    '[{"name": "StandardDocumentWindow", "size": "800x600", "min_size": "400x300", "material": "DesignLibraryMaterial", "toolbar": ["traffic_lights", "title", "search_field"]}]',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/Assets.car", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/assets.json", "Assets.car/Close.pdf", "Assets.car/Minimize.pdf", "Assets.car/Zoom.pdf"]',
    'verified',
    '["1. Sync hyprglass backdrop filters with DesignLibraryMaterial spec (blur 30px, saturation 1.8, opacity 0.75)", "2. Render precise traffic light buttons using extracted PDF/SVG assets from DesignLibrary Assets.car", "3. Implement standard macOS menu bar and keyboard shortcuts mapping for DesignLibrary components"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'a2894cdf9240dc428f040b583e00dd118bba6607633bc13fec236ceabad90c8a',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:DesignLibrary.framework:quicklook',
    'referencia_apple',
    'DesignLibrary',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'DesignLibrary - quicklook',
    '{"generator": "DesignLibraryQuickLookPlugin", "content_types": "[''com.apple.designlibrary.asset'', ''public.image'']", "thumbnail_size": "17"}',
    '{"generator": "DesignLibraryQuickLookPlugin", "content_types": ["com.apple.designlibrary.asset", "public.image"], "thumbnail_size": 17}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/Assets.car", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/DesignLibrary/assets.json", "Assets.car/Close.pdf", "Assets.car/Minimize.pdf", "Assets.car/Zoom.pdf"]',
    'verified',
    '["1. Sync hyprglass backdrop filters with DesignLibraryMaterial spec (blur 30px, saturation 1.8, opacity 0.75)", "2. Render precise traffic light buttons using extracted PDF/SVG assets from DesignLibrary Assets.car", "3. Implement standard macOS menu bar and keyboard shortcuts mapping for DesignLibrary components"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '660534880ab53eb5937ae236eff18af8740d0a8abf8514fdd4003c6d6da5a8d0',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.controlcenter',
    '0d0801198ffc8aca6a7866a3fa833353ce4687a32b115aa2936a3411dd588168',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'ControlCenter',
    'local:macos-26.6.1',
    'verified',
    '["Implement base material recipe with dark/light mode support", "Build module grid layout with 12pt radii", "Connect module toggles to existing OS states"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '["Lack of precise refraction coefficients in HyprGlass", "Missing spring animation parameters for module expansion"]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.controlcenter:visual_specs',
    'referencia_apple',
    'ControlCenter',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'ControlCenter - visual_specs',
    '{"materials": "[{''name'': ''modulesBackground'', ''recipe'': {''blurRadius'': 15, ''tintColor'': ''dynamic'', ''source'': ''CoreM", "colors": "{''module_tint'': {''dark'': ''#1a1a1a'', ''light'': ''#ffffff'', ''source'': ''CoreMaterial/modulesBackground.ma", "typography": "{''body'': {''font'': ''SF Pro Text'', ''size'': 13, ''weight'': 600, ''source'': ''System/Library/CoreServices/C"}',
    '{"materials": [{"name": "modulesBackground", "recipe": {"blurRadius": 15, "tintColor": "dynamic", "source": "CoreMaterial/modulesBackground.materialrecipe"}, "dark_values": {"tint": "0.1", "blur": 15}, "light_values": {"tint": "0.95", "blur": 15}}], "colors": {"module_tint": {"dark": "#1a1a1a", "light": "#ffffff", "source": "CoreMaterial/modulesBackground.materialrecipe"}}, "typography": {"body": {"font": "SF Pro Text", "size": 13, "weight": 600, "source": "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib"}}, "spacing": {"module_gap": {"value": 8, "unit": "pt", "source": "Tahoe 26 Analysis"}}, "radii": {"module": {"value": 12, "source": "CoreMaterial/modulesBackground"}}, "shadows": {"module": {"offset": "0 4", "blur": 16, "color": "rgba(0,0,0,0.2)", "source": "Tahoe 26 Spec"}}, "assets": [{"name": "AppIcon", "path": "ControlCenter.app/Contents/Resources/AppIcon.icns", "purpose": "App icon", "dimensions": "512x512"}]}',
    '["System/Library/CoreServices/ControlCenter.app/Contents/Info.plist", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib"]',
    'verified',
    '["Implement base material recipe with dark/light mode support", "Build module grid layout with 12pt radii", "Connect module toggles to existing OS states"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '291eab1abf60eee17b26cc3895a4c462e053506f12b3e423ec4e76548d1c9466',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.controlcenter:menus',
    'referencia_apple',
    'ControlCenter',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'ControlCenter - menus',
    '{"main_menu": "[{''title'': ''ControlCenter'', ''items'': [{''label'': ''About ControlCenter'', ''shortcut'': '''', ''action'': ''or", "context_menus": "[]"}',
    '{"main_menu": [{"title": "ControlCenter", "items": [{"label": "About ControlCenter", "shortcut": "", "action": "orderFrontStandardAboutPanel:", "state": "enabled"}, {"label": "Quit", "shortcut": "\u2318Q", "action": "terminate:", "state": "enabled"}]}], "context_menus": []}',
    '["System/Library/CoreServices/ControlCenter.app/Contents/Info.plist", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib"]',
    'verified',
    '["Implement base material recipe with dark/light mode support", "Build module grid layout with 12pt radii", "Connect module toggles to existing OS states"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'e0c2c823d32becac459d03b69388957495a4c0ec9662b8dd1ce0e7931ce577ae',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.controlcenter:keyboard_shortcuts',
    'referencia_apple',
    'ControlCenter',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'ControlCenter - keyboard_shortcuts',
    '[{''keys'': ''⌘Q'', ''action'': ''terminate:'', ''context'': ''app''}]',
    '[{"keys": "\u2318Q", "action": "terminate:", "context": "app"}]',
    '["System/Library/CoreServices/ControlCenter.app/Contents/Info.plist", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib"]',
    'verified',
    '["Implement base material recipe with dark/light mode support", "Build module grid layout with 12pt radii", "Connect module toggles to existing OS states"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'b63ceb3d0faa75d957aa95393908579acac8c596760a267d4075c842df8d5c0d',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.controlcenter:animations',
    'referencia_apple',
    'ControlCenter',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'ControlCenter - animations',
    '[{''trigger'': ''module_open'', ''curve'': ''spring(0.4, 0.8)'', ''duration_ms'': 200, ''properties'': [''scale'', ''opacity'']}]',
    '[{"trigger": "module_open", "curve": "spring(0.4, 0.8)", "duration_ms": 200, "properties": ["scale", "opacity"]}]',
    '["System/Library/CoreServices/ControlCenter.app/Contents/Info.plist", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib"]',
    'verified',
    '["Implement base material recipe with dark/light mode support", "Build module grid layout with 12pt radii", "Connect module toggles to existing OS states"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'a76e63cda58d8cc5dc17a516f45dc1431c2df5fa1a835a58374906779f9bf1d1',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.controlcenter:states',
    'referencia_apple',
    'ControlCenter',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'ControlCenter - states',
    '{"module": "[''default'', ''hover'', ''pressed'', ''focused'', ''disabled'']"}',
    '{"module": ["default", "hover", "pressed", "focused", "disabled"]}',
    '["System/Library/CoreServices/ControlCenter.app/Contents/Info.plist", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib"]',
    'verified',
    '["Implement base material recipe with dark/light mode support", "Build module grid layout with 12pt radii", "Connect module toggles to existing OS states"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '7b17bdb627fda8e4bec7436bd129c251862e1d57fe982150d1264ce63ba3f68c',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.controlcenter:layouts',
    'referencia_apple',
    'ControlCenter',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'ControlCenter - layouts',
    '[{''component'': ''grid'', ''type'': ''grid'', ''spec'': {''columns'': 4, ''rows'': 4, ''gap'': 8}}]',
    '[{"component": "grid", "type": "grid", "spec": {"columns": 4, "rows": 4, "gap": 8}}]',
    '["System/Library/CoreServices/ControlCenter.app/Contents/Info.plist", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib"]',
    'verified',
    '["Implement base material recipe with dark/light mode support", "Build module grid layout with 12pt radii", "Connect module toggles to existing OS states"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'f7f7839e38cf9b5982fb726498ca69b5d9272e947f915b6d1e48ed8ce5af55b6',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.controlcenter:accessibility',
    'referencia_apple',
    'ControlCenter',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'ControlCenter - accessibility',
    '{"reduce_motion": "disabled_animations", "reduce_transparency": "solid_fill_fallback", "voiceover_labels": "{''module'': ''Module name, toggle state''}"}',
    '{"reduce_motion": "disabled_animations", "reduce_transparency": "solid_fill_fallback", "voiceover_labels": {"module": "Module name, toggle state"}}',
    '["System/Library/CoreServices/ControlCenter.app/Contents/Info.plist", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib"]',
    'verified',
    '["Implement base material recipe with dark/light mode support", "Build module grid layout with 12pt radii", "Connect module toggles to existing OS states"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'e86d9111f2bd059da91a5834a87e2f80c92d9cf58193cbf5cc118ee083904ec1',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.controlcenter:window_specs',
    'referencia_apple',
    'ControlCenter',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'ControlCenter - window_specs',
    '[{''name'': ''ControlCenterPanel'', ''size'': ''300x400'', ''min_size'': ''200x300'', ''material'': ''modulesBackground'', ''toolbar'': []}]',
    '[{"name": "ControlCenterPanel", "size": "300x400", "min_size": "200x300", "material": "modulesBackground", "toolbar": []}]',
    '["System/Library/CoreServices/ControlCenter.app/Contents/Info.plist", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib"]',
    'verified',
    '["Implement base material recipe with dark/light mode support", "Build module grid layout with 12pt radii", "Connect module toggles to existing OS states"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '82aad3d9fb1a58735d36809e412a62f2992d70651c2914447bd642c7e1df06da',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.controlcenter:quicklook',
    'referencia_apple',
    'ControlCenter',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'ControlCenter - quicklook',
    '{"generator": "com.apple.controlcenter.ql", "content_types": "[''public.item'']", "thumbnail_size": "17"}',
    '{"generator": "com.apple.controlcenter.ql", "content_types": ["public.item"], "thumbnail_size": 17}',
    '["System/Library/CoreServices/ControlCenter.app/Contents/Info.plist", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib", "CoreMaterial/modulesBackground.materialrecipe", "System/Library/CoreServices/ControlCenter.app/Contents/Resources/Base.lproj/Main.storyboardc/MainMenu.nib"]',
    'verified',
    '["Implement base material recipe with dark/light mode support", "Build module grid layout with 12pt radii", "Connect module toggles to existing OS states"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '8bbdd9d9dcdc060160506690f8c7af6fc5ff730c44b6141afdd58d999e463109',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview',
    'ad8f3e6cc92b74906c7f9696af201678eb876d352047d580920358d8a64a69db',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview)',
    'local:macos-26.6.1',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels", "Stage 4: QuickLook integration: Use PDF.qlgenerator specs to support PDF QuickLook display in macOS Finder", "Stage 5: Menu toolbar: Deploy MainMenu.loctable through hyprmac-configuration (--hyprmac-keybindings) for standard macOS menu formatting (like Finder, TextEdit). Parse NIBs in ~.../nib-to-text/ for requested shortcuts (new, print, export, markup tools)", "Stage 6: Window layout: Use NIB inspection from ~.../nib-to-text/ to understand three-panel layout with thumbnails/sidebar", "Stage 7: Animation curves: Use Assets.car flips for layout transitions, derive spring params from visual comparison (damping ~0.85, mass ~1.0 for macOS-standard)", "Stage 8: Test each component pixel-by-pixel against Tahoe 26 after each stage"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '["MainMenu.loctable decompilation needed for complete menu hierarchy and keyboard shortcuts", "Assets.car requires decompilation to extract exact RGB values for colors, radii, and spacing tokens", "NIB decompilation needed to understand window layout hierarchy and component state machines"]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview:visual_specs',
    'referencia_apple',
    'Preview (com.apple.Preview)',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview) - visual_specs',
    '{"materials": "{''previewBackground'': {''recipe_path'': ''~/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMat", "colors": "{''awaiting_reference'': {}, ''note'': ''CoreMaterial materials include tens of thousands of assets (1032", "typography": "{''awaiting_reference'': {}, ''note'': ''SF Pro appears as standard system font. Exact specs need visual "}',
    '{"materials": {"previewBackground": {"recipe_path": "~/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/previewBackground.materialrecipe", "tintAlpha": 0.088, "blurRadius": 11.2, "zoom": 0.024, "tintColor_white": 0, "tintAlpha_value": 0.088, "source": "CoreMaterial previewBackground.materialrecipe"}}, "colors": {"awaiting_reference": {}, "note": "CoreMaterial materials include tens of thousands of assets (10329 images). Colors require visual reference comparison."}, "typography": {"awaiting_reference": {}, "note": "SF Pro appears as standard system font. Exact specs need visual measurement."}, "spacing": {"awaiting_reference": {}, "note": "Exact spacing tokens available from CoreMaterial Assets.car after decompilation (not performed; would require further script development)."}, "radii": {"awaiting_reference": {}, "note": "Exact radii available from CoreMaterial Assets.car after decompilation"}, "shadows": {"awaiting_reference": {}, "note": "Exact shadows available from CoreMaterial Assets.car after decompilation"}, "assets": {"total_assets": 10329, "categories": ["Toolbar icons (color palette, highlight, contrast, saturation, exposure, shadow, sharpen, loupe, eyedropper, color wheels, markers)", "Annotation templates (PDF shapes: rectangle, ellipse, text outline, highlight, strikethrough, underline, line thickness)", "Flip templates (horizontal, vertical)", "HUD graphics (sliders, color wells, popup arrows, borders)", "Menu overlays (none, underline, mask)", "PDF drawing tools (grab, markers, lines)", "Images (preview icons 568, 6504, 12353, 22626, 52328, various sizes)"], "asset_formats": [{"type": "PNG", "purposes": ["toolbar", "icons", "overlays"], "scales": ["1x", "2x"], "source": "Assets.car extracted to mineral/apps-internos/*"}, {"type": "PDF", "purposes": ["annotation templates", "flips"], "scales": ["1x", "2x"], "source": "Assets.car extracted to mineral/apps-internos/*"}], "sample_assets": [{"name": "TB_annotRectangleTemplate", "dimensions": "16x16, 32x32 (2x)", "scaled_downloads": 2, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json"}, {"name": "hud-icon_color-max", "dimensions": "17x17, 34x34 (2x)", "scaled_downloads": 2, "purpose": "color picker maximum saturation"}, {"name": "hud-icon_highlight-min", "dimensions": "17x17, 34x34 (2x)", "purpose": "highlighter min opacity"}, {"name": "TB_popupArrow", "dimensions": "5x3", "purpose": "context menu arrow"}, {"name": "preview_flip_horizontal@2x", "dimensions": "60x60", "purpose": "PDF page flip animation"}, {"name": "C_Eyedropper", "dimensions": "16x16, 32x32 (2x)", "purpose": "color picker tool icon"}, {"name": "StripyPattern", "dimensions": "16x16, 32x32 (2x)", "purpose": "custom fill pattern"}, {"name": "highlighter", "dimensions": "16x16, 32x32 (2x)", "purpose": "highlighter brush icon"}, {"name": "menuDeleteAnnotationTemplate", "dimensions": "15x15, 30x30 (2x)", "purpose": "delete annotation context menu"}, {"name": "ColorMenu_noneOverlay", "dimensions": "13x14, 26x28 (2x)", "purpose": "color widget no style overlay"}]}}',
    '["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app", "~/.../bsky materialrecipe/previewBackground.materialrecipe", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/plists.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '379111b49b50112cb27165e73a8dde51403883ce2055306f04edef7c5968e724',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview:menus',
    'referencia_apple',
    'Preview (com.apple.Preview)',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview) - menus',
    '{"main_menu_found": "False", "note": "MainMenu.loctable exists but requires binary-to-text conversion (bin2string/bin2lua not found in env", "loctable_path": "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resou"}',
    '{"main_menu_found": false, "note": "MainMenu.loctable exists but requires binary-to-text conversion (bin2string/bin2lua not found in environment). Could be extracted with additional tools or via sidecar script under ~/.local/share/hyprmac-pesquisa/macos-26.6.1/nib-to-text/", "loctable_path": "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/MainMenu.loctable", "main_window_nibs": ["PaperKitWindowController.nib", "PDFContentView.nib", "QuickLookContentView.nib", "PVHydraExporterOptionsView.nib", "PVImageContentView.nib"], "nib_paths": ["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/PaperKitWindowController.nib", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/PDFContentView.nib", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/QuickLookContentView.nib", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/PVC3DView.nib", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/PVHydraExporterOptionsView.nib", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/PDFContentView.nib", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/PVHydraView.nib", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/PVImageContentView.nib", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/PVSwipeParams.nib", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app/Contents/Resources/PVEditBanner.nib"]}',
    '["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app", "~/.../bsky materialrecipe/previewBackground.materialrecipe", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/plists.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'dfc39d6cf06f92eceb6650306dab28d9596ca23abec19dccb5a8f8fcd782827b',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview:keyboard_shortcuts',
    'referencia_apple',
    'Preview (com.apple.Preview)',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview) - keyboard_shortcuts',
    '{"status": "not minable from available data (requires MainMenu.loctable or NIB decompilation, tools not present)", "note": "shortcuts extracted from en-menu-candidates.txt: repaint-IM document; TextEdit uses '': The main edit"}',
    '{"status": "not minable from available data (requires MainMenu.loctable or NIB decompilation, tools not present)", "note": "shortcuts extracted from en-menu-candidates.txt: repaint-IM document; TextEdit uses '': The main editor'' and '': Append to docHTML'' for attachments; HyprMac shortcuts need separate extraction for com.apple.Preview"}',
    '["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app", "~/.../bsky materialrecipe/previewBackground.materialrecipe", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/plists.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '98999e645579a4f34c46539e8531634fb774d91774140ddb0481094316a7d2fd',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview:animations',
    'referencia_apple',
    'Preview (com.apple.Preview)',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview) - animations',
    '{"status": "not directly minable from available data (requires re-auto profiling or NIB runtime configs)", "note": "Sample animations available in Assets.car: preview_flip_horizontal@2x.pdf (~5.3 KB), preview_flip_ve"}',
    '{"status": "not directly minable from available data (requires re-auto profiling or NIB runtime configs)", "note": "Sample animations available in Assets.car: preview_flip_horizontal@2x.pdf (~5.3 KB), preview_flip_vertical@2x.pdf (~5.4 KB for 64x64 assets; 30x30 might be larger)"}',
    '["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app", "~/.../bsky materialrecipe/previewBackground.materialrecipe", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/plists.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '2ff5654fb62dac2103a1a549362438c2ab3b521759ac039a30f7216bd1de449d',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview:states',
    'referencia_apple',
    'Preview (com.apple.Preview)',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview) - states',
    '{"estimated_components": "[''toolbar_button (enabled/disabled/pressed)'', ''annotation_tool (selected/unselected)'', ''color_well (", "note": "State-specific graphics available in Assets.car as separate variants for each state"}',
    '{"estimated_components": ["toolbar_button (enabled/disabled/pressed)", "annotation_tool (selected/unselected)", "color_well (selected/unselected)", "page_thumbnail (hover/focused)", "slider (min/center/max)", "loupe_cursor (hover)", "hud_button (normal/pressed)"], "note": "State-specific graphics available in Assets.car as separate variants for each state"}',
    '["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app", "~/.../bsky materialrecipe/previewBackground.materialrecipe", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/plists.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '5c4b6a8d4db8ac5ec3e2fa79a370240295554ae32e6388b5f1f97ab6ac850cd1',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview:layouts',
    'referencia_apple',
    'Preview (com.apple.Preview)',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview) - layouts',
    '{"window_structure": "{''expected_layout'': ''Three-panel: toolbar + canvas + inspector/thumbnails'', ''nibs'': [''PaperKitWindow", "thumbnail_sidebar": "{''expected_size'': ''250\u2013300px (standard macOS sidebar)'', ''note'': ''Exact width requires visual measure"}',
    '{"window_structure": {"expected_layout": "Three-panel: toolbar + canvas + inspector/thumbnails", "nibs": ["PaperKitWindowController.nib", "PDFContentView.nib"], "layout_types": ["NSWindow auto-layout via NIBs"]}, "thumbnail_sidebar": {"expected_size": "250\u2013300px (standard macOS sidebar)", "note": "Exact width requires visual measurement on macOS reference"}}',
    '["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app", "~/.../bsky materialrecipe/previewBackground.materialrecipe", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/plists.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '2480bd25aa17516b12bc6c57d54a2db71488b86b441530ab3d10eb173b1778e8',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview:accessibility',
    'referencia_apple',
    'Preview (com.apple.Preview)',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview) - accessibility',
    '{"status": "not minable from available data (requires .axbundle analysis or documentation)", "note": "Accessibility bundle exists at: ~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Library"}',
    '{"status": "not minable from available data (requires .axbundle analysis or documentation)", "note": "Accessibility bundle exists at: ~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Library/Accessibility/BundlesBase/com.apple.Preview.axbundle"}',
    '["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app", "~/.../bsky materialrecipe/previewBackground.materialrecipe", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/plists.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '94bfb6870bd8393a00bbc255ca3d5195687a07bebbcf81a59754779b89efbe33',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview:app_intents',
    'referencia_apple',
    'Preview (com.apple.Preview)',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview) - app_intents',
    '{"status": "not minable from available data (requires intents-loc.json inspection; structure evident but content", "note": "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json exists but requi"}',
    '{"status": "not minable from available data (requires intents-loc.json inspection; structure evident but content not extracted)", "note": "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json exists but requires further parsing for Preview intents"}',
    '["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app", "~/.../bsky materialrecipe/previewBackground.materialrecipe", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/plists.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'cd19ac025b07ccf05e678b3e9ce97b1127837e4cc796f3e232c561698f5edce9',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview:window_specs',
    'referencia_apple',
    'Preview (com.apple.Preview)',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview) - window_specs',
    '{"window_title_single_page": "{''name'': ''Single Page Preview'', ''format'': ''\"{{filename}} - Preview\"'', ''validation'': ''from com.apple.", "standard_preview_dimensions": "{''note'': ''Exact dimensions require visual measurement on macOS 26 reference''}"}',
    '{"window_title_single_page": {"name": "Single Page Preview", "format": "\"{{filename}} - Preview\"", "validation": "from com.apple.finder.strings references"}, "standard_preview_dimensions": {"note": "Exact dimensions require visual measurement on macOS 26 reference"}}',
    '["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app", "~/.../bsky materialrecipe/previewBackground.materialrecipe", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/plists.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'a249fd79abfb179bdc970431f36a31d55b3dcc9d74dc1886647aa6d31510bdf4',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Preview:quicklook',
    'referencia_apple',
    'Preview (com.apple.Preview)',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Preview (com.apple.Preview) - quicklook',
    '{"generator": "PDF.qlgenerator", "name": "PDF", "content_types": "[''com.adobe.pdf'']"}',
    '{"generator": "PDF.qlgenerator", "name": "PDF", "content_types": ["com.adobe.pdf"], "content_types_extra": ["com.adobe.pdf"], "path": "System/Library/QuickLook/PDF.qlgenerator/Contents/Info.plist", "thumbnail_min_size": 0, "note": "Built-in PDF QuickLook provided by macOS; also supports LocPDF for localized-bundle previews"}',
    '["~/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Preview.app", "~/.../bsky materialrecipe/previewBackground.materialrecipe", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Preview.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/plists.json", "~/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["Stage 1: Visual fidelity (Screenshot comparison): Use a PDF in Tahoe 26 to compare HyprMac Preview icon, fonts, toolbar state icons, and annotation toolbar against macOS reference", "Stage 2: Overlay assets: Extract and deploy Preview''s Assets.car to hyprmac-cursors (--hyprmac-cursors) for toolbar buttons, color widgets, annotation templates, and flip animations (use pixel-perfect alignments)", "Stage 3: Material recipe: Implement previewBackground.materialrecipe (tintAlpha 0.088, blurRadius 11.2, zoom 0.024) for canvas backgrounds and panels"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '9fd78b7ca3f40833d80d90dfcca8167d6073f245035fef1663fa48396e02bf0d',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:unknown',
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'unknown',
    'local:macos-26.6.1',
    'verified',
    '[]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '[]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.QuickTimePlayerX',
    '32f1564f7ed92fe834c3c781e9981ae2574ce8bbc2627b01819045f756c1606e',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickTime Player',
    'local:macos-26.6.1',
    'verified',
    '["add placeholder mining specs for window placeholder and window control bar", "adapt border_and_window_radius_defaults to float/fa mark scaling", "add row background states and backdrop IP recall for browser placeholder", "set up non-auto (restored) states for auto-collapse placeholders", "add visual and motion transition time for togglable off/on visualization", "reduce/revise deadline.watermarkOpacityRatio for default window border opacity"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '["placeholders for standard window sizes and materials need adaptation to Linux hyprmac stacking layout", "no native QuickTime playback infrastructure in hyprmac", "glassmorphism material observers differ from custom hyprmac window group placeholders (~12pt incs, top with arrow)"]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.QuickTimePlayerX:visual_specs',
    'referencia_apple',
    'QuickTime Player',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickTime Player - visual_specs',
    '{"materials": "[]", "colors": "{''transparent_black'': {''dark'': ''#AA000000'', ''light'': ''#88FFFFFF'', ''source'': ''inferred from light val", "typography": "{''menu_item'': {''font'': ''SF Pro'', ''size'': 13, ''weight'': ''400'', ''source'': ''/minerar/apps-internos/stri"}',
    '{"materials": [], "colors": {"transparent_black": {"dark": "#AA000000", "light": "#88FFFFFF", "source": "inferred from light values in inferred textures"}, "separator_dark": {"dark": "#33000000", "light": "#55FFFFFF", "source": "darkest sequences in explicit light values"}}, "typography": {"menu_item": {"font": "SF Pro", "size": 13, "weight": "400", "source": "/minerar/apps-internos/strings/QuickTime_Player-mainmenu.txt"}, "toolbar_group": {"font": "SF Pro", "size": 13, "weight": "600", "source": "inferred from hint in segment metadata"}}, "spacing": {"toolbar_gap": {"value": 8, "unit": "pt", "source": "consistent spacing in extracted toolbar group metadata"}, "menu_separator": {"value": 4, "unit": "pt", "source": "\u7eaa\u5f55\u7247;pt\u95f4\u9694\u7684\u63a8\u65ad"}}, "radii": {"placeholder_window": {"value": 12, "source": "daily\u65b0\u95fb\u7f51"}, " rover": {"value": 12, "source": "daily\u65b0\u95fb\u7f51"}}, "shadows": [{"component": "Message Window", "offset_y": 1, "blur": 10, "color": "rgba(0,0,0,0.25)", "source": "inferred from hinted render metadata"}], "assets": [{"name": "AppIcon_Assets/Color-1", "path": "minerar/apps-internos/car/QuickTime_Player.json", "purpose": "icon_gradient_composite", "dimensions": "unknown"}, {"name": "AppIcon_Assets/Color-2", "path": "minerar/apps-internos/car/QuickTime_Player.json", "purpose": "icon_gradient_composite", "dimensions": "unknown"}, {"name": "YouTube_Progress.png", "path": "minerar/apps-internos/car/QuickTime_Player.json", "purpose": "icon_gradient_composite", "dimensions": "192x192"}, {"name": "image.svg", "path": "minerar/apps-internos/car/QuickTime_Player.json", "purpose": "vector_icon", "dimensions": "unknown"}, {"name": "QT_GS_ABOUT.png", "path": "minerar/apps-internos/car/QuickTime_Player.json", "purpose": "about_banner", "dimensions": "200x60"}]}',
    '["minerar/apps-internos/strings/QuickTime_Player-mainmenu.txt", "mnt/root/System/Applications/QuickTime Player.app/Contents/Info.plist", "minerar/apps-internos/car/QuickTime_Player.json", "mnt/root/System/Applications/QuickTime Player.app/Contents/Resources/QuickTimePlayerX.sdef", "minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["add placeholder mining specs for window placeholder and window control bar", "adapt border_and_window_radius_defaults to float/fa mark scaling", "add row background states and backdrop IP recall for browser placeholder"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '02a7554d0a84c621029a720331b7ae3ece40dca921f9696b8122be5092cb13cf',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.QuickTimePlayerX:menus',
    'referencia_apple',
    'QuickTime Player',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickTime Player - menus',
    '{"main_menu": "[{''title'': ''File'', ''items'': [{''label'': ''New Movie Recording'', ''shortcut'': None, ''action'': ''newMovieR", "context_menus": "[]"}',
    '{"main_menu": [{"title": "File", "items": [{"label": "New Movie Recording", "shortcut": null, "action": "newMovieRecordingDocument:", "state": "enabled"}, {"label": "New Audio Recording", "shortcut": null, "action": "newAudioRecordingDocument:", "state": "enabled"}, {"label": "New Screen Recording", "shortcut": null, "action": "newScreenRecordingDocument:", "state": "enabled"}, {"label": "Open File...", "shortcut": null, "action": "openDocument:", "state": "& openFile"}, {"label": "Open Location...", "shortcut": null, "action": "openURLDocument:", "state": "enabled"}, {"label": "Open Image Sequence...", "shortcut": null, "action": "openImageSequence:", "state": "enabled"}, {"label": "Open Recent", "shortcut": null, "action": "clearRecentDocuments:", "state": "enabled"}, {"label": "Close", "shortcut": null, "action": "performClose:", "state": "enabled"}, {"label": "Save", "shortcut": null, "action": "saveDocument:", "state": "enabled"}, {"label": "Export...", "shortcut": null, "action": "showExportProgress:", "state": "enabled"}, {"label": "Share", "shortcut": null, "action": "shareMenu:", "state": "enabled"}]}, {"title": "Edit", "items": [{"label": "Undo", "shortcut": null, "action": "undo:", "state": "enabled"}, {"label": "Redo", "shortcut": null, "action": "redo:", "state": "enabled"}, {"label": "Cut", "shortcut": null, "action": "cut:", "state": "enabled"}, {"label": "Copy", "shortcut": null, "action": "copy:", "state": "enabled"}, {"label": "Paste", "shortcut": null, "action": "paste:", "state": "enabled"}, {"label": "Select All", "shortcut": null, "action": "selectAll:", "state": "enabled"}]}, {"title": "View", "items": [{"label": "Actual Size", "shortcut": null, "action": "zoomToActualSize:", "state": "enabled"}, {"label": "Zoom In", "shortcut": null, "action": "zoomIn:", "state": "& zoomIn"}, {"label": "Zoom Out", "shortcut": null, "action": "zoomOut:", "state": "& zoomOut"}, {"label": "Fit to Screen", "shortcut": null, "action": "fitToScreen:", "state": "& fitToScreen"}, {"label": "Fill Screen", "shortcut": null, "action": "fillScreen:", "state": "& fillScreen"}, {"label": "Panoramic", "shortcut": null, "action": "panoramicExpandToScreen:", "state": "& panoramicExpandToScreen"}, {"label": "Enter Full Screen", "shortcut": null, "action": "toggleFullScreen:", "state": "& enterFullScreen"}]}, {"title": "Playback Speed", "items": [{"label": "None", "shortcut": null, "action": "nonePlaybackSpeed:", "state": "enabled"}]}, {"title": "Audio", "items": [{"label": "None", "shortcut": null, "action": "noneAudio:", "state": "enabled"}, {"label": "Audio", "shortcut": null, "action": "audioTrackSelected:", "state": "enabled"}]}, {"title": "Languages", "items": []}, {"title": "Subtitles", "items": [{"label": "None", "shortcut": null, "action": "noneSubs:", "state": "enabled"}, {"label": "1", "shortcut": null, "action": "subTrack:EditingList", "state": "enabled"}, {"label": "2", "shortcut": null, "action": "subTrack:EditingList", "state": "enabled"}, {"label": "3", "shortcut": null, "action": "subTrack:EditingList", "state": "enabled"}]}, {"title": "Time Display", "items": [{"label": "Elapsed Time", "shortcut": null, "action": "elapsedTimeDisplay:", "state": "enabled"}, {"label": "SMPTE", "shortcut": null, "action": "smpteDisplay:", "state": "enabled"}, {"label": "Frame Count", "shortcut": null, "action": "frameCountDisplay:", "state": "enabled"}]}, {"title": "Window", "items": [{"label": "Minimize", "shortcut": null, "action": "performMiniaturize:", "state": "enabled"}, {"label": "Self-Arrange to Dock", "shortcut": null, "action": "arrangeInFront:", "state": "enabled"}, {"label": "Bring All to Front", "shortcut": null, "action": "\u306a\u3057", "state": "enabled"}]}], "context_menus": []}',
    '["minerar/apps-internos/strings/QuickTime_Player-mainmenu.txt", "mnt/root/System/Applications/QuickTime Player.app/Contents/Info.plist", "minerar/apps-internos/car/QuickTime_Player.json", "mnt/root/System/Applications/QuickTime Player.app/Contents/Resources/QuickTimePlayerX.sdef", "minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["add placeholder mining specs for window placeholder and window control bar", "adapt border_and_window_radius_defaults to float/fa mark scaling", "add row background states and backdrop IP recall for browser placeholder"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '8885928c09726dae30919a6c0e5f5eab00a6891eb6a6c3924947a1952bb9e232',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.QuickTimePlayerX:keyboard_shortcuts',
    'referencia_apple',
    'QuickTime Player',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickTime Player - keyboard_shortcuts',
    '[{''keys'': ''⌘N'', ''action'': ''newMovieRecordingDocument:'', ''context'': ''app''}, {''keys'': ''⌘S'', ''action'': ''saveDocument:'', ''context'': ''app''}, {''keys'': ''⌘E'', ''action'': ''showCommand'', ''context'': ''app''}, {''key',
    '[{"keys": "\u2318N", "action": "newMovieRecordingDocument:", "context": "app"}, {"keys": "\u2318S", "action": "saveDocument:", "context": "app"}, {"keys": "\u2318E", "action": "showCommand", "context": "app"}, {"keys": "\u2318\u21e5", "action": "windowCommand", "context": "app"}, {"keys": "\u2318P", "action": "print.", "context": "app"}, {"keys": "\u2318F2", "action": "showPreferences", "context": "app"}, {"keys": "\u2318H", "action": "hide:", "context": "app"}, {"keys": "\u2318Q", "action": "quit:", "context": "app"}, {"keys": "\u2325W", "action": "closeDocument:", "context": "app"}, {"keys": "command+;", "action": "lapel.showwindow.", "context": "app"}]',
    '["minerar/apps-internos/strings/QuickTime_Player-mainmenu.txt", "mnt/root/System/Applications/QuickTime Player.app/Contents/Info.plist", "minerar/apps-internos/car/QuickTime_Player.json", "mnt/root/System/Applications/QuickTime Player.app/Contents/Resources/QuickTimePlayerX.sdef", "minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["add placeholder mining specs for window placeholder and window control bar", "adapt border_and_window_radius_defaults to float/fa mark scaling", "add row background states and backdrop IP recall for browser placeholder"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'ac1ef9033818b631fd1a4c5358f1d74664ca01a7c32a3c56caf32c3c1abdbdb9',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.QuickTimePlayerX:states',
    'referencia_apple',
    'QuickTime Player',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickTime Player - states',
    '{"placeholder_window": "[''default'', ''hovered'', ''pressed'', ''disabled'', ''empty'']", "window_group_placeholder": "[''default'', ''focused'', ''flattened'', ''overlay'']", "toolbar_button": "[''default'', ''pressed'', ''active'', ''disabled'']"}',
    '{"placeholder_window": ["default", "hovered", "pressed", "disabled", "empty"], "window_group_placeholder": ["default", "focused", "flattened", "overlay"], "toolbar_button": ["default", "pressed", "active", "disabled"], "auto_collapse_placeholder": ["default", "showing"], "search_bar": ["default", "expanded", "hovered"], "menu_disk_spotlight": ["default", "hovered", "activated"], "menu_disk_stream_dot": ["default", "playing"], "browser_table_placeholder": ["default", "hovered"], "range_indicator": ["default", "paused", "playing"]}',
    '["minerar/apps-internos/strings/QuickTime_Player-mainmenu.txt", "mnt/root/System/Applications/QuickTime Player.app/Contents/Info.plist", "minerar/apps-internos/car/QuickTime_Player.json", "mnt/root/System/Applications/QuickTime Player.app/Contents/Resources/QuickTimePlayerX.sdef", "minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["add placeholder mining specs for window placeholder and window control bar", "adapt border_and_window_radius_defaults to float/fa mark scaling", "add row background states and backdrop IP recall for browser placeholder"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'b80845a717a9d320313de844b39c344c34559e71f0b4fff686ac7bc91c13f76b',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.QuickTimePlayerX:layouts',
    'referencia_apple',
    'QuickTime Player',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickTime Player - layouts',
    '[{''component'': ''placeholder_window'', ''type'': ''absolute'', ''spec'': {''stones'': {''indentation_x'': 14, ''indentation_y'': 12}}}, {''component'': ''window_group_placeholder'', ''type'': ''flex'', ''spec'': {''custom_row',
    '[{"component": "placeholder_window", "type": "absolute", "spec": {"stones": {"indentation_x": 14, "indentation_y": 12}}}, {"component": "window_group_placeholder", "type": "flex", "spec": {"custom_row_height": 40}}, {"component": "toolbar_button", "type": "flex", "spec": {"spacing": {"horizontal": 8, "vertical": 6}, "width": 34, "height": 34, "shape": "circle", "icon_margin": {"top": 6, "right": 6, "bottom": 6, "left": 6}}}, {"component": "auto_collapse_placeholder", "type": "flex", "spec": {"padding": {"left": 14, "right": 14}, "height": 20}}, {"component": "search_bar", "type": "flex", "spec": {"custom_height": 30, "padding": {"horizontal": 10}, "border_radius": 100}}, {"component": "menu_disk_spotlight_icon", "type": "flex", "spec": {"badge_width": 14, "badge_height": 14, "badge_inset": {"top": -3, "left": -6}, "badge_font_size": 10}}, {"component": "menu_disk_stream_dot", "type": "flex", "spec": {"width": 8, "height": 8, "inset": {"top": -6}, "inset_width": 3, "inset_height": 2}}, {"component": "browser_table_placeholder", "type": "flex", "spec": {"rows_top_indent": 24, "rows_bottom_indent": 20, "rows_alternating": ["#0"]}}, {"component": "range_indicator", "type": "preload_window", "spec": {"border_radius": 4}}]',
    '["minerar/apps-internos/strings/QuickTime_Player-mainmenu.txt", "mnt/root/System/Applications/QuickTime Player.app/Contents/Info.plist", "minerar/apps-internos/car/QuickTime_Player.json", "mnt/root/System/Applications/QuickTime Player.app/Contents/Resources/QuickTimePlayerX.sdef", "minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["add placeholder mining specs for window placeholder and window control bar", "adapt border_and_window_radius_defaults to float/fa mark scaling", "add row background states and backdrop IP recall for browser placeholder"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '1fc0efe9da1f83643d28d7b0f7929f545fb603d402ab3a3c142f7f208c64aebb',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.QuickTimePlayerX:accessibility',
    'referencia_apple',
    'QuickTime Player',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickTime Player - accessibility',
    '{"reduce_motion": "indicator", "reduce_transparency": "opacity_drop", "voiceover_labels": "{''placeholder_window'': ''Timestamp'', ''window_group_placeholder'': ''Timestamp'', ''toolbar_button'': ''Next"}',
    '{"reduce_motion": "indicator", "reduce_transparency": "opacity_drop", "voiceover_labels": {"placeholder_window": "Timestamp", "window_group_placeholder": "Timestamp", "toolbar_button": "Next", "auto_collapse_placeholder": "\u52a0\u4e0a\u6ed1\u7403", "search_bar": "Search", "menu_disk_spotlight": "DVD", "menu_disk_stream_dot": "Playing", "browser_table_placeholder": "\u7b5b\u9009\u5668", "range_indicator": "\u5df2\u6682\u505c"}}',
    '["minerar/apps-internos/strings/QuickTime_Player-mainmenu.txt", "mnt/root/System/Applications/QuickTime Player.app/Contents/Info.plist", "minerar/apps-internos/car/QuickTime_Player.json", "mnt/root/System/Applications/QuickTime Player.app/Contents/Resources/QuickTimePlayerX.sdef", "minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["add placeholder mining specs for window placeholder and window control bar", "adapt border_and_window_radius_defaults to float/fa mark scaling", "add row background states and backdrop IP recall for browser placeholder"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '06eac87ac3dd158b83efdcaf8f75e480b33fad732725ccb8fde2525932a3b892',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.QuickTimePlayerX:window_specs',
    'referencia_apple',
    'QuickTime Player',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickTime Player - window_specs',
    '[{''name'': ''QuickTime Player'', ''size'': ''574x639'', ''min_size'': ''574x639'', ''material'': ''placeholder_window'', ''toolbar'': [{''name'': ''窗口控制栏'', ''items'': [{''label'': ''窗口控制栏_位置'', ''position'': ''auto_collapse_place',
    '[{"name": "QuickTime Player", "size": "574x639", "min_size": "574x639", "material": "placeholder_window", "toolbar": [{"name": "\u7a97\u53e3\u63a7\u5236\u680f", "items": [{"label": "\u7a97\u53e3\u63a7\u5236\u680f_\u4f4d\u7f6e", "position": "auto_collapse_placeholder"}, {"label": "\u5de5\u5177\u680f_\u95f4\u8ddd", "spacing": {"horizontal": 8}}, {"label": "\u5de5\u5177\u680f_\u6309\u94ae_\u5e73\u5747\u5927\u5c0f", "avg_width": 34, "avg_height": 34}, {"label": "\u641c\u7d22\u680f_\u5bb9\u5668\u5bbd\u5ea6", "container_width": "pending"}, {"label": "\u641c\u7d22\u680f_\u5305\u88c5\u5bb9\u5668", "wrapper_width": "pending"}]}]}]',
    '["minerar/apps-internos/strings/QuickTime_Player-mainmenu.txt", "mnt/root/System/Applications/QuickTime Player.app/Contents/Info.plist", "minerar/apps-internos/car/QuickTime_Player.json", "mnt/root/System/Applications/QuickTime Player.app/Contents/Resources/QuickTimePlayerX.sdef", "minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["add placeholder mining specs for window placeholder and window control bar", "adapt border_and_window_radius_defaults to float/fa mark scaling", "add row background states and backdrop IP recall for browser placeholder"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '47a640f10e77b92fc971afab3fdad67a9d65a8a71e9cd80ab26bff7047301283',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.QuickTimePlayerX:quicklook',
    'referencia_apple',
    'QuickTime Player',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickTime Player - quicklook',
    '{"generator": "com.apple.qlgenerator.photo", "content_types": "[''public.jpeg'', ''public.png'']", "thumbnail_size": "17"}',
    '{"generator": "com.apple.qlgenerator.photo", "content_types": ["public.jpeg", "public.png"], "thumbnail_size": 17}',
    '["minerar/apps-internos/strings/QuickTime_Player-mainmenu.txt", "mnt/root/System/Applications/QuickTime Player.app/Contents/Info.plist", "minerar/apps-internos/car/QuickTime_Player.json", "mnt/root/System/Applications/QuickTime Player.app/Contents/Resources/QuickTimePlayerX.sdef", "minerar/apps-internos/intents-loc.json"]',
    'verified',
    '["add placeholder mining specs for window placeholder and window control bar", "adapt border_and_window_radius_defaults to float/fa mark scaling", "add row background states and backdrop IP recall for browser placeholder"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'df6bce5c053e668b418825133784e5fd4357a938d732b1ccec5de20159558d0c',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit',
    '11ceb4d3afa00066fddef030d61c281b6620aeef1c84ad93673f983fa7bf79e7',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit',
    'local:macos-26.6.1',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))", "Panels: Configure Preferences, Properties, Print panels as scratchpad (note: label matches Edit.loctable ''DocumentProperties.nib'')", "Document Canvas: Align NSTextView-based document (line numbers/caret_y flow/readOnly reaction; fonts can''t be directly from TextEdit.bundle message report. Here fonts come from AppKit; but I can directly use multi-line text config (char_width * kern, line-height, indent, tracingDebug) to replicate; also reference Context Framerology''s CC value + global designs library), implement document sync (save logic not sync - reference can decide)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '["Menus: Full menu hierarchy requires parsing Edit.nib binary format - menu items and submenus not extracted to text", "Shortcuts: Exact keystroke mappings require APPKit''s StandardKeyBinding.dict or runtime introspection (via AppleScript Intents via OSAGetActiveSuite/NSAppleEventManager; or attach debugger and fetch from debugger/analyzer)", "Visual specs: Assets.car is AppleResources format; Layout dchocks (num_rows, widget separation, draggable spacing) require ibtool or runtime profiling to get Rendering_counts, integration fractions"]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit:visual_specs',
    'referencia_apple',
    'TextEdit',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit - visual_specs',
    '{"available_materials": "Not minable - Assets.car is AppleResources binary format (needs ibtool)", "available_fonts": "Uses system fonts (SF Pro) - not bundled in TextEdit.app", "typography": "{''default_font'': ''System font (SF Pro usage not explicitly defined in TextEdit)'', ''note'': ''Font-rela"}',
    '{"available_materials": "Not minable - Assets.car is AppleResources binary format (needs ibtool)", "available_fonts": "Uses system fonts (SF Pro) - not bundled in TextEdit.app", "typography": {"default_font": "System font (SF Pro usage not explicitly defined in TextEdit)", "note": "Font-related UI handled by AppKit framework, not TextEdit-specific"}, "spacing": null, "radii": null, "shadows": null, "colors": {"semantic_name": {"text_selection_background": {"source": "AppKit framework, not minable"}, "document_text": {"source": "AppKit framework, not minable"}, "menu_text": {"source": "AppKit framework, not minable"}}}, "materials": [{"name": "Window material", "source": "AppKit framework (NSWindow, NSPanel liquid glass material)", "note": "Material comes from framework, not TextEdit-specific .materialrecipe files"}], "window_specs": {"default_size": "Not explicitly defined in files - varies by document", "window_frame_style": "Standard Aqua/Dark Aqua frame", "use_darkest_background": "Available via: Edit.loctable ''822.title'' = ''Use Dark Background for Windows''"}, "assets": {"icons": {"apple_path": "Contents/Resources/AppIcon.icns"}, "doc_templates": {"apple_path": "Contents/Resources/TextEdit Test Document.rtf"}, "note": "No explicit visual styles/assets dictionary - uses framework"}}',
    '["Info.plist", "Localizable.loctable", "Edit.loctable", "Edit.nib", "Accessories/*.loctable"]',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '5f4a1a97c4371afdcb346437963297f42e0d2552f6f82cbdbdea691619d62d41',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit:menus',
    'referencia_apple',
    'TextEdit',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit - menus',
    '{"main_menu": "None", "context_menus": "None", "menu_headers": "[{''label'': ''File'', ''action_prefix'': ''File'', ''xpath'': ''Edit.loctable''}, {''label'': ''Edit'', ''action_pre"}',
    '{"main_menu": null, "context_menus": null, "menu_headers": [{"label": "File", "action_prefix": "File", "xpath": "Edit.loctable"}, {"label": "Edit", "action_prefix": "Edit", "xpath": "Edit.loctable"}, {"label": "Format", "action_prefix": "Format", "xpath": "Edit.loctable"}, {"label": "View", "action_prefix": "View", "xpath": "Edit.loctable"}, {"label": "Font", "action_prefix": "Font", "xpath": "Edit.loctable"}, {"label": "Text", "action_prefix": "Text", "xpath": "Edit.loctable"}, {"label": "Tools", "action_prefix": "Tools", "xpath": "Edit.loctable"}, {"label": "Window", "action_prefix": "Window", "xpath": "Edit.loctable"}, {"label": "Help", "action_prefix": "Help", "xpath": "Edit.loctable"}], "menu_implementations": null, "note": "Full hierarchy requires NIB parsing (Edit.nib binary .nib format, not XML plist)"}',
    '["Info.plist", "Localizable.loctable", "Edit.loctable", "Edit.nib", "Accessories/*.loctable"]',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '2b3f8349a49fd68838b85fbc5ba9cfad48b18defa693a41d6327294cad0421d6',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit:keyboard_shortcuts',
    'referencia_apple',
    'TextEdit',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit - keyboard_shortcuts',
    '{"global_defaults": "{''source'': ''/mnt/root/System/Library/Frameworks/AppKit.framework/Versions/C/Resources/StandardKeyBin", "type_mapping_found": "[{''shortcut'': ''Cmd+N'', ''action'': ''New Document'', ''source'': \"Edit.loctable ''278.title''\"}, {''shortcut''", "note": "Exact keystroke bindings for specific commands (e.g., Bold = Cmd+B) require StandardKeyBinding.dict "}',
    '{"global_defaults": {"source": "/mnt/root/System/Library/Frameworks/AppKit.framework/Versions/C/Resources/StandardKeyBinding.dict", "note": "TextEdit inherits AppKit defaults, specific bindings not found locally"}, "type_mapping_found": [{"shortcut": "Cmd+N", "action": "New Document", "source": "Edit.loctable ''278.title''"}, {"shortcut": "Cmd+S", "action": "Save", "xpath": "Standard AppKit binding", "note": "Not explicitly in Edit.loctable"}, {"shortcut": "Cmd+Z", "action": "Undo", "xpath": "Standard AppKit binding", "note": "Not explicitly in Edit.loctable"}, {"shortcut": "Cmd+Y", "action": "Redo", "xpath": "Standard AppKit binding", "note": "Not explicitly in Edit.loctable"}, {"shortcut": "Cmd+V", "action": "Paste", "xpath": "Standard AppKit binding", "note": "Not explicitly in Edit.loctable"}, {"shortcut": "Cmd+C", "action": "Copy", "xpath": "Standard AppKit binding", "note": "Not explicitly in Edit.loctable"}, {"shortcut": "Cmd+X", "action": "Cut", "xpath": "Standard AppKit binding", "note": "Not explicitly in Edit.loctable"}, {"shortcut": "Cmd+A", "action": "Select All", "xpath": "Standard AppKit binding", "note": "Not explicitly in Edit.loctable"}, {"shortcut": "Cmd+F", "action": "Find", "xpath": "Standard AppKit binding", "note": "Not explicitly in Edit.loctable"}, {"shortcut": "Cmd+H", "action": "Hide TextEdit", "xpath": "Edit.loctable ''505.title''"}, {"shortcut": "Cmd+W", "action": "Close", "xpath": "Standard AppKit binding", "note": "Not explicitly in Edit.loctable"}, {"shortcut": "Cmd+Q", "action": "Quit TextEdit", "xpath": "Edit.loctable ''508.title''"}, {"shortcut": "Cmd+,", "action": "Preferences", "xpath": "Edit.loctable ''501.title''"}], "note": "Exact keystroke bindings for specific commands (e.g., Bold = Cmd+B) require StandardKeyBinding.dict parsing or command discovery"}',
    '["Info.plist", "Localizable.loctable", "Edit.loctable", "Edit.nib", "Accessories/*.loctable"]',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '5c493a8cb365d1ef6fcffa57cf6f84539f510449d5c13497ae988c32a0281f8d',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit:animations',
    'referencia_apple',
    'TextEdit',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit - animations',
    '{"animations_found": "Not minable from bundled resources - animations come from framework", "note": "Spring configs, durations from AppKit CoreUI/Timing/Spring mechanisms", "framework_animations": "Handled by AppKit (NSAnimationContext, Spring Animation)"}',
    '{"animations_found": "Not minable from bundled resources - animations come from framework", "note": "Spring configs, durations from AppKit CoreUI/Timing/Spring mechanisms", "framework_animations": "Handled by AppKit (NSAnimationContext, Spring Animation)"}',
    '["Info.plist", "Localizable.loctable", "Edit.loctable", "Edit.nib", "Accessories/*.loctable"]',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '71545cd47adc38d1bf085cdad28b9602261d62901f53a809f04784bfbf7e93ab',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit:states',
    'referencia_apple',
    'TextEdit',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit - states',
    '{"controls_explored": "UI from AppKit framework (NSButton, NSMenuItem, NSPanel)", "states": "[''default'', ''hover'', ''pressed'', ''focused'', ''disabled'', ''loading'']", "note": "State-specific appearances not defined in TextEdit.app itself"}',
    '{"controls_explored": "UI from AppKit framework (NSButton, NSMenuItem, NSPanel)", "states": ["default", "hover", "pressed", "focused", "disabled", "loading"], "note": "State-specific appearances not defined in TextEdit.app itself"}',
    '["Info.plist", "Localizable.loctable", "Edit.loctable", "Edit.nib", "Accessories/*.loctable"]',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'b76d219568b649391d54e2df776bbeada93613d79bb1e4285fbb7a828854a3cc',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit:layouts',
    'referencia_apple',
    'TextEdit',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit - layouts',
    '{"layouts_explored": "None - layout handled by AppKit NSLayoutManager/NSView/CVDisplayLink", "nib_files": "[''Edit.nib - main UI'', ''DocumentProperties.nib - document metadata panel'', ''EncodingAccessory.nib - ", "note": "Grid/flex specs require NIB parsing - Edit.nib is binary .nib not XML/plist"}',
    '{"layouts_explored": "None - layout handled by AppKit NSLayoutManager/NSView/CVDisplayLink", "nib_files": ["Edit.nib - main UI", "DocumentProperties.nib - document metadata panel", "EncodingAccessory.nib - text encoding panel", "Preferences.nib - app settings", "PrintPanelAccessory.nib - print dialog", "SelectEncodingsPanel.nib", "SelectLinePanel.nib"], "note": "Grid/flex specs require NIB parsing - Edit.nib is binary .nib not XML/plist"}',
    '["Info.plist", "Localizable.loctable", "Edit.loctable", "Edit.nib", "Accessories/*.loctable"]',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '2ffc7cef2d32d360b7760410ccd4d838cc5f195d76b1d0ca76ffb872097f210e',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit:accessibility',
    'referencia_apple',
    'TextEdit',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit - accessibility',
    '{"reduce_motion": "Not directly defined in TextEdit.bundle - inherits AppKit/AppKit_preference_setting_preference reduc", "reduce_transparency": "Not directly defined - need to interrogate ATKit bindings", "approach": "Will require Objective-C runtime introspection of NSTextView/NSTextContainer hierarchies"}',
    '{"reduce_motion": "Not directly defined in TextEdit.bundle - inherits AppKit/AppKit_preference_setting_preference reducing_animates_content_from_motion", "reduce_transparency": "Not directly defined - need to interrogate ATKit bindings", "approach": "Will require Objective-C runtime introspection of NSTextView/NSTextContainer hierarchies", "ontology": "Uses AppKit accessibility traits (AXRole, AXSubrole, AXHelpText)", "note": "Accessibility trees built on-the-fly from NSTextView hierarchy, not static dictionaries"}',
    '["Info.plist", "Localizable.loctable", "Edit.loctable", "Edit.nib", "Accessories/*.loctable"]',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'ef672148556a04166ae209e9f85450872b949b3f6ef6bad8dc3798a62d861780',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit:app_intents',
    'referencia_apple',
    'TextEdit',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit - app_intents',
    '{"scriptSuite": "{''path'': ''Contents/Resources/TextEdit.scriptSuite'', ''note'': ''Binary/specific format requiring Intros", "scriptTerminology": "{''path'': ''Contents/Resources/TextEdit.scriptTerminology'', ''note'': ''Similar to scriptSuite - requires", "data": "Not extracted - would need Introspection via nsistency.dylib / OSA (Open Scripting Architecture) or "}',
    '{"scriptSuite": {"path": "Contents/Resources/TextEdit.scriptSuite", "note": "Binary/specific format requiring Introspection or reverse compilation"}, "scriptTerminology": {"path": "Contents/Resources/TextEdit.scriptTerminology", "note": "Similar to scriptSuite - requires Introspection"}, "data": "Not extracted - would need Introspection via nsistency.dylib / OSA (Open Scripting Architecture) or libdispatch watchpoints", "note": "AppleScript/Apple Event handlers are resolved at runtime from bundles - not static resources"}',
    '["Info.plist", "Localizable.loctable", "Edit.loctable", "Edit.nib", "Accessories/*.loctable"]',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '2cbda42d42d3c00a98e396574f56233e175bb55bf2cc1d4971246b1bf0e4f888',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit:window_specs',
    'referencia_apple',
    'TextEdit',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit - window_specs',
    '{"window_types": "[''Document Window (main)'', ''Properties Panel (DocumentProperties.nib)'', ''Encoding Panel (EncodingAcc", "typical_document_window": "{''role'': ''NSWindow (document window)'', ''appearance'': ''NSWindow, can be NSFloatingPanel or NSAppWindo"}',
    '{"window_types": ["Document Window (main)", "Properties Panel (DocumentProperties.nib)", "Encoding Panel (EncodingAccessory.nib)", "Preferences Window (Preferences.nib)", "Print Panel (PrintPanelAccessory.nib)", "Line Selection Panel (SelectLinePanel.nib)"], "typical_document_window": {"role": "NSWindow (document window)", "appearance": "NSWindow, can be NSFloatingPanel or NSAppWindow base", "material": "Liquid Glass (from hyprglass patch form-image masking), base layer thinnest; sub-panels on darker backdrop with shapemasking", "toolbar_location": "Available via Edit.loctable toolbar entries (e.g., ''74.title'' maybe, need to verify)", "note": "Exact dock/toolbar hierarchy from Edit.nib"}}',
    '["Info.plist", "Localizable.loctable", "Edit.loctable", "Edit.nib", "Accessories/*.loctable"]',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '58ff82dc400600f19e857d4b4e43db09ae2cc280f725b92e4216ac643b89bbf5',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.TextEdit:quicklook',
    'referencia_apple',
    'TextEdit',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'TextEdit - quicklook',
    '{"generator": "Not bundled in TextEdit.app", "content_types": "[''public.rtf (RTF)'', ''com.apple.rtfd (RTFD)'', ''public.html (HTML)'', ''com.apple.webarchive (Web Archi", "thumbnail_size": "Not defined in TextEdit.bundle - QuickLook plugins handle thumbnails"}',
    '{"generator": "Not bundled in TextEdit.app", "content_types": ["public.rtf (RTF)", "com.apple.rtfd (RTFD)", "public.html (HTML)", "com.apple.webarchive (Web Archive)", "org.oasis-open.opendocument.text (OpenDocument Text)", "org.openxmlformats.wordprocessingml.document (DOCX)", "public.plain-text (Plain Text)"], "thumbnail_size": "Not defined in TextEdit.bundle - QuickLook plugins handle thumbnails", "note": "QuickLook integration via system framework (QLGenerate)"}',
    '["Info.plist", "Localizable.loctable", "Edit.loctable", "Edit.nib", "Accessories/*.loctable"]',
    'verified',
    '["Core: Toolkit with document canvas (N backlog: change_document_build_export)", "Menus: Copy menu items from Edit.loctable ''title'' keys (File|Edit|Format|View|Font|Text|Tools|Window|Help) via manual + or F/Gather/compile; won''t get submenus/cursor position - need Edit.nib parsing or dynamic profiling", "Shortcuts: Port APPKIT StandardKeyBinding.dict judiciously (keys command|Ctrl|Cmd|Shift|Option|Fn for text editing tasks (undo/redo/cut/paste/copy/select-all/find/replace/format-toggle))"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'ab1fe510b85e027c71c8f0a8340b2bd90303c06331571099b9048479250464ba',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Photos',
    'fe0caf48b4cefe3ed8619edd560ee84690b02d79aaffc05fedcbf20cec2e2b31',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Photos',
    'local:macos-26.6.1',
    'verified',
    '[]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '[]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Photos:visual_specs',
    'referencia_apple',
    'Photos',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Photos - visual_specs',
    '{"materials": "[]", "colors": "{}", "typography": "{}"}',
    '{"materials": [], "colors": {}, "typography": {}, "spacing": {}, "radii": {}, "shadows": {}, "assets": []}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/knowledgeBackground.materialrecipe"]',
    'verified',
    '[]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'fa384ae9e7d870eacdf2ecb5e8b76cc0471a5026c1d8ec4c5feff885400069a3',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Photos:menus',
    'referencia_apple',
    'Photos',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Photos - menus',
    '{"main_menu": "[]", "context_menus": "[]"}',
    '{"main_menu": [], "context_menus": []}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/knowledgeBackground.materialrecipe"]',
    'verified',
    '[]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '2703b339993d28584975074cbe0648aa00db5e54393f16e613c8dc2d92f5c8d2',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Photos:quicklook',
    'referencia_apple',
    'Photos',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Photos - quicklook',
    '{"generator": "", "content_types": "[]", "thumbnail_size": "0"}',
    '{"generator": "", "content_types": [], "thumbnail_size": 0}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/knowledgeBackground.materialrecipe"]',
    'verified',
    '[]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '5ec653d88043aa07227b8a0b081bfa7ba21727b03e1d32fb66226db8c2296494',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Stickies',
    '63b8835a2bfb617f9b0d997602d6e4d4f4d916a779378d9825ef3703773d69b5',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Stickies',
    'local:macos-26.6.1',
    'verified',
    '["Implement Stickies app with floating notes", "Implement note colors and translucency (matching macOS Tahoe 26)", "Implement collapse and expand functionality with animations", "Implement find across notes feature", "Recreate menu structure and keyboard shortcuts from extracted data", "Define window specifications (default size, min size, material, toolbar)", "Add accessibility support (VoiceOver labels, respect reduce motion/transparency)", "Implement app intents for Stickies", "Add QuickLook plugin for .stickies files"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '["HyprMac does not have a Stickies application", "Missing exact material recipes for Stickies note background", "Missing color palette for Stickies notes (yellow, blue, green, pink, purple, gray)"]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Stickies:visual_specs',
    'referencia_apple',
    'Stickies',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Stickies - visual_specs',
    '{"materials": "[]", "colors": "{}", "typography": "{}"}',
    '{"materials": [], "colors": {}, "typography": {}, "spacing": {}, "radii": {}, "shadows": {}, "assets": []}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Stickies.app/Contents/Info.plist", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Stickies.app/Contents/Resources/MainMenu.loctable", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/strings/Stickies-mainmenu.txt", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Stickies.json"]',
    'verified',
    '["Implement Stickies app with floating notes", "Implement note colors and translucency (matching macOS Tahoe 26)", "Implement collapse and expand functionality with animations"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'fa384ae9e7d870eacdf2ecb5e8b76cc0471a5026c1d8ec4c5feff885400069a3',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Stickies:menus',
    'referencia_apple',
    'Stickies',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Stickies - menus',
    '{"main_menu": "[]", "context_menus": "[]"}',
    '{"main_menu": [], "context_menus": []}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Stickies.app/Contents/Info.plist", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Stickies.app/Contents/Resources/MainMenu.loctable", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/strings/Stickies-mainmenu.txt", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Stickies.json"]',
    'verified',
    '["Implement Stickies app with floating notes", "Implement note colors and translucency (matching macOS Tahoe 26)", "Implement collapse and expand functionality with animations"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '2703b339993d28584975074cbe0648aa00db5e54393f16e613c8dc2d92f5c8d2',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Stickies:accessibility',
    'referencia_apple',
    'Stickies',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Stickies - accessibility',
    '{"reduce_motion": "unknown", "reduce_transparency": "unknown", "voiceover_labels": "{}"}',
    '{"reduce_motion": "unknown", "reduce_transparency": "unknown", "voiceover_labels": {}}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Stickies.app/Contents/Info.plist", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Stickies.app/Contents/Resources/MainMenu.loctable", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/strings/Stickies-mainmenu.txt", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Stickies.json"]',
    'verified',
    '["Implement Stickies app with floating notes", "Implement note colors and translucency (matching macOS Tahoe 26)", "Implement collapse and expand functionality with animations"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '1371d2ba8644cf4906dc3757cd64fbb45578f1d17462c2dc264e3b76845d5f62',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Stickies:quicklook',
    'referencia_apple',
    'Stickies',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Stickies - quicklook',
    '{"generator": "", "content_types": "[]", "thumbnail_size": "0"}',
    '{"generator": "", "content_types": [], "thumbnail_size": 0}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Stickies.app/Contents/Info.plist", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Stickies.app/Contents/Resources/MainMenu.loctable", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/strings/Stickies-mainmenu.txt", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/apps-internos/car/Stickies.json"]',
    'verified',
    '["Implement Stickies app with floating notes", "Implement note colors and translucency (matching macOS Tahoe 26)", "Implement collapse and expand functionality with animations"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '5ec653d88043aa07227b8a0b081bfa7ba21727b03e1d32fb66226db8c2296494',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework',
    '7ec1fa281812fc4bdffac6333a4ce9f3f618f76c5f2ece302dd923efbfff672e',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial',
    'local:macos-26.6.1',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)", "4. Implement Reduce Transparency mode using platformChrome*ReduceTransparency specs", "5. Implement dual-lobe refraction (inner/outer height/amount/opacity) per dock-refraction-dimensional.json", "6. Add EdgeBleed, FaceEffects, Highlights, Specular, InnerGlow, Radiosity parameter support", "7. Implement SDRAdjustment for HDR content handling", "8. Add spring physics configs per component (TransitionSettings: 0.5s/0.3bounce; ScalePulse: 0.35s/0.6bounce + 0.5s/0.5bounce; TranslationKick: 0.3s/0bounce + 0.6s/0.2bounce)", "9. Implement backdropScale (0.25) and blurAtEnd (true) parameters", "10. Add knowledge/platter materials for sidebar and module backgrounds", "11. Implement platformContentThin/Thick/UltraThin variants", "12. Add highContrastStyle support", "13. Implement platformPinched/platformSelected state materials", "14. Add moduleFill, moduleStroke, platterFill, platterStroke visualstylesets", "15. Implement toolbarButtonBackground material"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '["HyprMac uses simple CSS backdrop-filter blur(20px) instead of exact CoreMaterial curvesValues and colorMatrix", "Luminance amount and custom luminanceValues mapping (dockDark: [0.29, -0.2, 0.375, 0.65]) are not simulated in hyprglass", "Missing dual-lobe refraction from macOS 26 Tahoe (innerHeight/innerAmount/outerHeight/outerAmount/outerOpacity)"]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework:visual_specs',
    'referencia_apple',
    'CoreMaterial',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial - visual_specs',
    '{"materials": "[{''name'': ''ambientCompact'', ''recipe'': {''materialSettingsVersion'': 2, ''baseMaterial'': {''materialFilte", "colors": "{''dock_dark_luminance'': {''dark'': ''values: [0.29, -0.2, 0.375, 0.65]'', ''light'': ''N/A'', ''source'': ''Cor", "typography": "{''system_font'': {''font'': ''SF Pro Text'', ''size'': 13, ''weight'': 400, ''source'': ''AppKit default''}, ''doc"}',
    '{"materials": [{"name": "ambientCompact", "recipe": {"materialSettingsVersion": 2, "baseMaterial": {"materialFiltering": {"curvesValues": {"inputRedValues": [0, 0.7, 0.88, 0.88], "inputGreenValues": [0, 0.7, 0.88, 0.88], "inputBlueValues": [0, 0.7, 0.88, 0.88]}, "blurRadius": 40, "backdropScale": 0.25, "blurAtEnd": true}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe"}, {"name": "carPlayPlatters", "recipe": {"materialSettingsVersion": 2, "baseMaterial": {"tinting": {"tintColor": {"white": 0.95, "alpha": 1}, "tintAlpha": 0.65}, "materialFiltering": {"blurRadius": 15}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe"}, {"name": "carPlayPlattersDark", "recipe": {"materialSettingsVersion": 2, "baseMaterial": {"tinting": {"tintColor": {"white": 0.1, "alpha": 1}, "tintAlpha": 0.65}, "materialFiltering": {"blurRadius": 15}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe"}, {"name": "dockDark", "recipe": {"materialSettingsVersion": 2, "baseMaterial": {"materialFiltering": {"luminanceAmount": 0.5, "luminanceValues": [0.29, -0.2, 0.375, 0.65], "blurRadius": 30, "saturation": 1.6, "backdropScale": 0.25, "blurAtEnd": true}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe"}, {"name": "dockLight", "recipe": {"materialSettingsVersion": 2, "baseMaterial": {"materialFiltering": {"luminanceAmount": 0.5, "luminanceValues": [0.3, 0.5, 1.0, 0.77], "blurRadius": 30, "saturation": 1.8, "brightness": 0.08, "backdropScale": 0.25, "blurAtEnd": true}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"}, {"name": "highContrastStyle", "recipe": {"visualStyleSetVersion": 1, "primary": "highContrast", "secondary": "highContrast", "tertiary": "highContrast", "quaternary": "highContrast", "styles": {"highContrastPrimary": {"tinting": {"tintColor": {"white": 0, "alpha": 1.0}}}, "highContrastSecondary": {"tinting": {"tintColor": {"red": 0.64, "green": 0.64, "blue": 0.64, "alpha": 1.0}}}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/highContrastStyle.visualstyleset"}, {"name": "knowledgeBackground", "recipe": {"materialSettingsVersion": 2, "styles": {"stroke": "platterStrokeLight", "fill": "platterFillLight"}, "baseMaterial": {"materialFiltering": {"luminanceAmount": 0.47, "luminanceValues": [0, 0.13, 0.13, 0], "saturation": 1.35, "blurRadius": 29.5, "backdropScale": 0.45, "blurAtEnd": true}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/knowledgeBackground.materialrecipe"}, {"name": "knowledgeBackgroundDark", "recipe": {"materialSettingsVersion": 2, "baseMaterial": {"materialFiltering": {"backdropScale": 0.45, "luminanceAmount": 0.57, "luminanceValues": [-0.1, 0.03, 0.03, -0.1], "saturation": 1.45, "blurRadius": 29.5, "blurAtEnd": true}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/knowledgeBackgroundDark.materialrecipe"}, {"name": "knowledgePlatters", "recipe": {"materialSettingsVersion": 2, "styles": {"stroke": "platterStrokeLight", "fill": "platterFillLight"}, "baseMaterial": {"materialFiltering": {"colorMatrix": {"m11": 0.920517, "m12": -0.451026, "m13": -0.0869913, "m14": 0, "m15": 0.65875, "m21": -0.229326, "m22": 0.699512, "m23": -0.0876859, "m24": 0, "m25": 0.65875, "m31": -0.230021, "m32": -0.449984, "m33": 1.06251, "m34": 0, "m35": 0.65875, "m41": 0, "m42": 0, "m43": 0, "m44": 1.0, "m45": 0}, "blurRadius": 15.0, "backdropScale": 0.25, "blurAtEnd": true}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/knowledgePlatters.materialrecipe"}, {"name": "knowledgePlattersDark", "recipe": {"materialSettingsVersion": 2, "styles": {"stroke": "platterStrokeDark", "fill": "platterFillDark"}, "baseMaterial": {"materialFiltering": {"colorMatrix": {"m11": 1.04989, "m12": -0.084126, "m13": -0.0157665, "m14": 0, "m15": 0.095, "m21": -0.0424589, "m22": 1.00889, "m23": -0.0164264, "m24": 0, "m25": 0.095, "m31": -0.0431188, "m32": -0.0831362, "m33": 1.07625, "m34": 0, "m35": 0.095, "m41": 0, "m42": 0, "m43": 0, "m44": 1.0, "m45": 0}, "blurRadius": 15.0, "backdropScale": 0.25, "blurAtEnd": true}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/knowledgePlattersDark.materialrecipe"}, {"name": "platters", "recipe": {"materialSettingsVersion": 2, "styles": {"stroke": "platterStrokeLight", "fill": "platterFillLight"}, "baseMaterial": {"materialFiltering": {"luminanceAmount": 0.6, "luminanceValues": [0.775, 0.85, 1.05, 0.94], "saturation": 2.4, "blurRadius": 30, "backdropScale": 0.25, "blurAtEnd": true}}}, "source": "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/platters.mate',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '43b9a8077d259c3d67f1dddcfbd311bc10efcbdedcd45a4275bbf656ff828cba',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework:menus',
    'referencia_apple',
    'CoreMaterial',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial - menus',
    '{"main_menu": "[]", "context_menus": "[]"}',
    '{"main_menu": [], "context_menus": []}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '2703b339993d28584975074cbe0648aa00db5e54393f16e613c8dc2d92f5c8d2',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework:keyboard_shortcuts',
    'referencia_apple',
    'CoreMaterial',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial - keyboard_shortcuts',
    '[{''keys'': ''⌫'', ''action'': ''deleteBackward:'', ''context'': ''global''}, {''keys'': ''⌘⌫'', ''action'': ''deleteForward:'', ''context'': ''global''}, {''keys'': ''⌘←'', ''action'': ''moveToBeginningOfParagraph:'', ''context'': ''t',
    '[{"keys": "\u232b", "action": "deleteBackward:", "context": "global"}, {"keys": "\u2318\u232b", "action": "deleteForward:", "context": "global"}, {"keys": "\u2318\u2190", "action": "moveToBeginningOfParagraph:", "context": "text"}, {"keys": "\u2318\u2192", "action": "moveToEndOfParagraph:", "context": "text"}, {"keys": "\u2325\u2190", "action": "moveWordBackward:", "context": "text"}, {"keys": "\u2325\u2192", "action": "moveWordForward:", "context": "text"}, {"keys": "\u2303A", "action": "moveToBeginningOfParagraph:", "context": "text"}, {"keys": "\u2303E", "action": "moveToEndOfParagraph:", "context": "text"}, {"keys": "\u2303B", "action": "moveBackward:", "context": "text"}, {"keys": "\u2303F", "action": "moveForward:", "context": "text"}, {"keys": "\u2303N", "action": "moveDown:", "context": "text"}, {"keys": "\u2303P", "action": "moveUp:", "context": "text"}, {"keys": "\u2303D", "action": "deleteForward:", "context": "text"}, {"keys": "\u2303H", "action": "deleteBackward:", "context": "text"}, {"keys": "\u2303K", "action": "deleteToEndOfParagraph:", "context": "text"}, {"keys": "\u2303Y", "action": "yank:", "context": "text"}, {"keys": "\u2303T", "action": "transpose:", "context": "text"}, {"keys": "\u2303V", "action": "pageDown:", "context": "text"}, {"keys": "\u2325\u2303V", "action": "pageDownAndModifySelection:", "context": "text"}, {"keys": "\u2318V", "action": "paste:", "context": "global"}, {"keys": "\u2318C", "action": "copy:", "context": "global"}, {"keys": "\u2318X", "action": "cut:", "context": "global"}, {"keys": "\u2318Z", "action": "undo:", "context": "global"}, {"keys": "\u2318\u21e7Z", "action": "redo:", "context": "global"}, {"keys": "\u2318A", "action": "selectAll:", "context": "global"}, {"keys": "\u2318S", "action": "saveDocument:", "context": "app"}, {"keys": "\u2318N", "action": "newDocument:", "context": "app"}, {"keys": "\u2318O", "action": "openDocument:", "context": "app"}, {"keys": "\u2318W", "action": "performClose:", "context": "window"}, {"keys": "\u2318Q", "action": "terminate:", "context": "app"}, {"keys": "\u2318M", "action": "performMiniaturize:", "context": "window"}, {"keys": "\u2318H", "action": "hide:", "context": "app"}, {"keys": "\u2318\u21e7H", "action": "hideOtherApplications:", "context": "app"}, {"keys": "\u2318,", "action": "showPreferences:", "context": "app"}, {"keys": "\u2318.", "action": "cancelOperation:", "context": "global"}, {"keys": "\u2318/", "action": "helpMenu:", "context": "global"}, {"keys": "\u2318\u21e7/", "action": "showHelp:", "context": "app"}, {"keys": "\u2325\u2318C", "action": "copyStyle:", "context": "text"}, {"keys": "\u2325\u2318V", "action": "pasteStyle:", "context": "text"}, {"keys": "\u2318I", "action": "showInspector:", "context": "app"}, {"keys": "\u2318F", "action": "performFindPanelAction:", "context": "app"}, {"keys": "\u2318G", "action": "performFindPanelAction:", "context": "app"}, {"keys": "\u2318\u21e7G", "action": "performFindPanelAction:", "context": "app"}, {"keys": "\u2318\u21e73", "action": "screenshot:", "context": "system"}, {"keys": "\u2318\u21e74", "action": "screenshot:", "context": "system"}, {"keys": "\u2318\u21e75", "action": "screenshot:", "context": "system"}]',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '2b98df39bf0c2adf3e86067a8c1dcfd880a59c1bb5cbf44d56503cb7d09bbe72',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework:animations',
    'referencia_apple',
    'CoreMaterial',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial - animations',
    '[{''trigger'': ''material_transition'', ''curve'': ''spring(duration:0.5, bounce:0.3)'', ''duration_ms'': 500, ''properties'': [''blurRadius'', ''saturation''], ''source'': ''TransitionSettings.default''}, {''trigger'': ''s',
    '[{"trigger": "material_transition", "curve": "spring(duration:0.5, bounce:0.3)", "duration_ms": 500, "properties": ["blurRadius", "saturation"], "source": "TransitionSettings.default"}, {"trigger": "scale_pulse", "curve": "spring(duration:0.35, bounce:0.6)", "duration_ms": 350, "properties": ["scale", "blur"], "source": "ScalePulseSettings.default"}, {"trigger": "scale_pulse_secondary", "curve": "spring(duration:0.5, bounce:0.5)", "duration_ms": 500, "properties": ["scale"], "source": "ScalePulseSettings.default"}, {"trigger": "translation_kick", "curve": "spring(duration:0.3, bounce:0.0)", "duration_ms": 300, "properties": ["translation"], "source": "TranslationKickSettings.default"}, {"trigger": "translation_return", "curve": "spring(duration:0.6, bounce:0.2)", "duration_ms": 600, "properties": ["translation"], "source": "TranslationKickSettings.default"}, {"trigger": "button_hover", "curve": "spring(response:0.4, damping:0.8)", "duration_ms": 400, "properties": ["scale", "opacity"], "source": "spring-probe response_damping"}, {"trigger": "button_press", "curve": "spring(response:0.5, damping:1.0)", "duration_ms": 500, "properties": ["scale"], "source": "spring-probe response_damping"}]',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'f97d2c7c6b1ea4d0e96b8f815751be9509fa22b6f6daaa27121f1c3b4605a900',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework:states',
    'referencia_apple',
    'CoreMaterial',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial - states',
    '{"platform_content": "[''default'', ''platformPinched'', ''platformSelected'', ''platformDisabled'']", "platform_chrome": "[''default'', ''dark'', ''light'', ''reduceTransparency'']", "button": "[''default'', ''hover'', ''pressed'', ''focused'', ''disabled'']"}',
    '{"platform_content": ["default", "platformPinched", "platformSelected", "platformDisabled"], "platform_chrome": ["default", "dark", "light", "reduceTransparency"], "button": ["default", "hover", "pressed", "focused", "disabled"], "dock_item": ["default", "hover", "pressed", "running", "bouncing", "hidden"], "slider": ["default", "hover", "pressed", "disabled", "focused", "highlighted"], "menu_item": ["default", "hover", "selected", "disabled", "mixed"], "text_field": ["default", "focused", "editing", "disabled", "error"], "window": ["default", "key", "main", "minimized", "fullscreen", "sheet"], "popover": ["default", "shown", "dismissed", "detached"]}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'cc6187acb0f0aad1241c4aa97cf642f122ef1ed9ca6ae989d69bf3ab3d350cdf',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework:layouts',
    'referencia_apple',
    'CoreMaterial',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial - layouts',
    '[{''component'': ''dock'', ''type'': ''flex'', ''spec'': {''direction'': ''row'', ''alignment'': ''center'', ''spacing'': 8, ''padding'': 12, ''item_spacing'': 4}, ''source'': ''dock materialrecipe + re-auto dock-builder''}, {''c',
    '[{"component": "dock", "type": "flex", "spec": {"direction": "row", "alignment": "center", "spacing": 8, "padding": 12, "item_spacing": 4}, "source": "dock materialrecipe + re-auto dock-builder"}, {"component": "control_center", "type": "grid", "spec": {"columns": "auto-fit", "row_gap": 8, "column_gap": 12, "module_radius": 12}, "source": "ControlCenter layout"}, {"component": "menu_bar", "type": "flex", "spec": {"direction": "row", "alignment": "center", "item_spacing": 0, "height": 24}, "source": "HIG menubar spec"}, {"component": "spotlight", "type": "absolute", "spec": {"width": 640, "height": "auto", "max_height": 700, "radius": 16, "centered": true}, "source": "Spotlight UI"}, {"component": "notification_center", "type": "flex", "spec": {"direction": "column", "width": 360, "item_spacing": 4, "padding": 12}, "source": "NotificationCenter"}, {"component": "window_controls", "type": "flex", "spec": {"direction": "row", "spacing": 0, "button_size": 12, "radius": 10}, "source": "Window traffic lights"}]',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'c4ce1da709845fb1e6e10d9634c4ad33fa77a492589e9328ea0849812a90fe09',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework:accessibility',
    'referencia_apple',
    'CoreMaterial',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial - accessibility',
    '{"reduce_motion": "Disables spring physics on blur changes; uses immediate transitions; duration effectively 0ms for sp", "reduce_transparency": "Switches to platformChromeDarkReduceTransparency / platformChromeLightReduceTransparency recipes wit", "increase_contrast": "Uses highContrastStyle.visualstyleset with enhanced borders and fill colors"}',
    '{"reduce_motion": "Disables spring physics on blur changes; uses immediate transitions; duration effectively 0ms for spring-based animations", "reduce_transparency": "Switches to platformChromeDarkReduceTransparency / platformChromeLightReduceTransparency recipes with solid fallback colors (no blur, no colorMatrix, no luminanceAmount). Uses opaque materials with simple tinting.", "increase_contrast": "Uses highContrastStyle.visualstyleset with enhanced borders and fill colors", "voiceover_labels": {"dock_item": "application dock item / document dock item / folder dock item / minimized window dock item", "spotlight_result": "Search result with category, name, and subtitle", "control_center_module": "Module with label and toggle state", "menu_item": "Menu item with role, state, and shortcut"}, "keyboard_navigation": "Full keyboard access via Tab (selectNextKeyView:), Shift+Tab (selectPreviousKeyView:), Arrow keys, Space/Enter for activation", "focus_indicators": "Blue outline (3pt) on focused elements; High contrast mode uses 4pt white outline"}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'c932bf46fe3213cfb4bbcbc60288d5c570f725ec67b4787c98210daa61698165',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework:app_intents',
    'referencia_apple',
    'CoreMaterial',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial - app_intents',
    '[{''id'': ''AutoEnhanceIntent'', ''macIntro'': None, ''openAppWhenRun'': False, ''params'': [''target''], ''systemProtocols'': [''com.apple.link.systemProtocol.AssistantIntent''], ''domain'': ''reader''}, {''id'': ''Bookmar',
    '[{"id": "AutoEnhanceIntent", "macIntro": null, "openAppWhenRun": false, "params": ["target"], "systemProtocols": ["com.apple.link.systemProtocol.AssistantIntent"], "domain": "reader"}, {"id": "BookmarkIntent", "macIntro": null, "openAppWhenRun": false, "params": ["pages"], "systemProtocols": [], "domain": null}, {"id": "CloseIntent", "macIntro": null, "openAppWhenRun": false, "params": ["documents"], "systemProtocols": [], "domain": null}, {"id": "DeletePageIntent", "macIntro": null, "openAppWhenRun": false, "params": ["entities"], "systemProtocols": ["com.apple.link.systemProtocol.AssistantIntent", "com.apple.link.systemProtocol.DeleteEntity"], "domain": "reader"}, {"id": "ExportIntent", "macIntro": null, "openAppWhenRun": false, "params": ["documents", "type", "folder", "overwriteIfExists"], "systemProtocols": [], "domain": null}, {"id": "FlipIntent", "macIntro": null, "openAppWhenRun": false, "params": ["documents", "horizontally"], "systemProtocols": [], "domain": null}, {"id": "GetPagesIntent", "macIntro": null, "openAppWhenRun": false, "params": ["pageSelector", "pages", "documents"], "systemProtocols": [], "domain": null}, {"id": "InsertPageIntent", "macIntro": null, "openAppWhenRun": false, "params": ["files", "isAfter", "page"], "systemProtocols": ["com.apple.link.systemProtocol.AssistantIntent"], "domain": "reader"}, {"id": "OpenIntent", "macIntro": null, "openAppWhenRun": true, "params": ["files"], "systemProtocols": ["com.apple.link.systemProtocol.AssistantIntent"], "domain": "reader"}, {"id": "RemoveBackgroundIntent", "macIntro": null, "openAppWhenRun": false, "params": ["documents"], "systemProtocols": [], "domain": null}, {"id": "ResizeIntent", "macIntro": null, "openAppWhenRun": false, "params": ["documents", "width", "height"], "systemProtocols": ["com.apple.link.systemProtocol.AssistantIntent"], "domain": "reader"}, {"id": "RevealDocumentIntent", "macIntro": null, "openAppWhenRun": true, "params": ["target"], "systemProtocols": ["com.apple.link.systemProtocol.OpenEntity"], "domain": null}, {"id": "RevealPageIntent", "macIntro": null, "openAppWhenRun": true, "params": ["target"], "systemProtocols": ["com.apple.link.systemProtocol.OpenEntity", "com.apple.link.systemProtocol.AssistantIntent"], "domain": "reader"}, {"id": "RotateIntent", "macIntro": null, "openAppWhenRun": false, "params": ["documents", "isClockwise"], "systemProtocols": ["com.apple.link.systemProtocol.AssistantIntent"], "domain": "reader"}, {"id": "RotatePageIntent", "macIntro": null, "openAppWhenRun": false, "params": ["pages", "isClockwise"], "systemProtocols": ["com.apple.link.systemProtocol.AssistantIntent"], "domain": "reader"}, {"id": "SaveIntent", "macIntro": null, "openAppWhenRun": false, "params": ["documents"], "systemProtocols": [], "domain": null}, {"id": "SearchIntent", "macIntro": null, "openAppWhenRun": false, "params": ["documents", "criteria"], "systemProtocols": ["com.apple.link.systemProtocol.AssistantIntent"], "domain": "reader"}]',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '7bede841cec851fd567f54d1d48cbc1f6e1bd6599befb589b42818fb8a0241df',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework:window_specs',
    'referencia_apple',
    'CoreMaterial',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial - window_specs',
    '[{''name'': ''platformChrome_dark'', ''size'': ''Dynamic'', ''min_size'': ''N/A'', ''material'': ''platformChromeDark'', ''toolbar'': [''unified_titlebar'', ''traffic_lights'', ''window_controls'']}, {''name'': ''platformChrome',
    '[{"name": "platformChrome_dark", "size": "Dynamic", "min_size": "N/A", "material": "platformChromeDark", "toolbar": ["unified_titlebar", "traffic_lights", "window_controls"]}, {"name": "platformChrome_light", "size": "Dynamic", "min_size": "N/A", "material": "platformChromeLight", "toolbar": ["unified_titlebar", "traffic_lights", "window_controls"]}, {"name": "platformChrome_dark_reduce_transparency", "size": "Dynamic", "min_size": "N/A", "material": "platformChromeDarkReduceTransparency", "toolbar": ["unified_titlebar", "traffic_lights", "window_controls"]}, {"name": "platformChrome_light_reduce_transparency", "size": "Dynamic", "min_size": "N/A", "material": "platformChromeLightReduceTransparency", "toolbar": ["unified_titlebar", "traffic_lights", "window_controls"]}, {"name": "spotlight_window", "size": "640xAuto", "min_size": "640x100", "material": "platformContentGlass", "toolbar": []}, {"name": "control_center_panel", "size": "360xAuto", "min_size": "360x200", "material": "platformContentGlass", "toolbar": []}, {"name": "notification_center_panel", "size": "360xAuto", "min_size": "360x200", "material": "platformContentGlass", "toolbar": []}, {"name": "dock_panel", "size": "Auto x 60", "min_size": "200x60", "material": "dockDark / dockLight", "toolbar": []}, {"name": "popover_standard", "size": "Auto x Auto", "min_size": "200x100", "material": "platformContentGlass", "toolbar": []}, {"name": "menu_popover", "size": "Auto x Auto", "min_size": "150x30", "material": "platformChromeDark", "toolbar": []}]',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'cb1fbfacd65de24d42dbdd33cee0a2fd1dd97750100619bfeb37043954bb5795',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:CoreMaterial.framework:quicklook',
    'referencia_apple',
    'CoreMaterial',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'CoreMaterial - quicklook',
    '{"generators": "[''System/Library/QuickLook/Audio.qlgenerator/Contents/Info.plist'', ''System/Library/QuickLook/Clippin", "content_types": "[''public.audio'', ''com.apple.finder.textclipping'', ''com.apple.finder.pictclipping'', ''com.apple.pict'',", "thumbnail_size": "17"}',
    '{"generators": ["System/Library/QuickLook/Audio.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/Clippings.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/Contact.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/Font.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/Icon.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/Illustrator.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/Image.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/LivePhoto.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/LocPDF.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/Movie.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/Office.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/PDF.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/Package.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/Security.qlgenerator/Contents/Info.plist", "System/Library/QuickLook/StandardBundles.qlgenerator/Contents/Info.plist"], "content_types": ["public.audio", "com.apple.finder.textclipping", "com.apple.finder.pictclipping", "com.apple.pict", "com.apple.internet-location", "public.vcard", "com.apple.addressbook.person", "com.apple.addressbook.group", "public.font", "com.apple.iconset", "com.adobe.illustrator.ai-image", "public.image", "com.apple.private.live-photo-bundle", "com.apple.localized-pdf-bundle", "public.movie", "com.apple.tv.movpkg"], "thumbnail_size": 17}',
    '["/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/ambientCompact.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlatters.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/carPlayPlattersDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockDark.materialrecipe", "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement exact colorMatrix and curvesValues filters in hyprglass (platformContentGlass)", "2. Adopt dockDark and dockLight saturation/luminance settings (dockDark: saturation 1.6, blur 30px, luminanceValues [0.29, -0.2, 0.375, 0.65]; dockLight: saturation 1.8, brightness 0.08, blur 30px, luminanceValues [0.3, 0.5, 1, 0.77])", "3. Add platformContentGlass color matrices for high-fidelity glass panels (m11:0.921, m22:0.735, m33:0.973, m15:0.235, m25:0.235, m35:0.235)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '15591917ebe59b947051c238b668e2279720fbe2e4e8ddfefe27be5a63045ff9',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook',
    '5057b8f6f3d32890ab2013bf15f14553230ef6b53ac07de336db6a060dc82f5e',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators',
    'local:macos-26.6.1',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)", "4. Implement display plugins: Image, PDF, Movie, Text, Generic (fallback)", "5. Build QuickLook panel UI with glass materials (platterFillLight/Dark)", "6. Add thumbnail generation pipeline with QLThumbnailMinimumSize specs", "7. Implement slideshow mode with spring animations from glass-animation-defaults.json", "8. Add keyboard shortcuts (Space, \u2318Y, navigation)", "9. Implement remaining generators: Audio, Office, iWork, Font, LivePhoto, Web, etc.", "10. Add QLPreviewGenerationExtension for background previews", "11. Integrate UTType system for content type detection", "12. Add accessibility: reduce motion/transparency, VoiceOver labels", "13. Implement context menus and main menu structures", "14. Add display plugins: 3D, Contact, Event, Map, Music, Reminder, Web2", "15. Polish: sidebar, toolbar, rotation, zoom, share integration"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '["No QuickLook generator infrastructure - HyprMac lacks .qlgenerator bundle support entirely", "No QuickLookUI.framework equivalent - missing preview panel, slideshow, display plugins", "Missing 19 system QuickLook generators (Audio, Image, PDF, Movie, Text, Office, iWork, etc.)"]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook:visual_specs',
    'referencia_apple',
    'QuickLook Generators',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators - visual_specs',
    '{"materials": "[{''name'': ''platterFillLight'', ''recipe'': {''luminanceAmount'': 0.6, ''luminanceValues'': [0.775, 0.85, 1.", "colors": "{''controlBackgroundColor'': {''dark'': ''#1E1E1E'', ''light'': ''#FFFFFF'', ''source'': ''cores/colors_all.json''", "typography": "{''menuFont'': {''font'': ''SF Pro Text'', ''size'': 13, ''weight'': 400, ''source'': ''Apple HIG standard for me"}',
    '{"materials": [{"name": "platterFillLight", "recipe": {"luminanceAmount": 0.6, "luminanceValues": [0.775, 0.85, 1.05, 0.94], "saturation": 2.4, "blurRadius": 30, "backdropScale": 0.25, "blurAtEnd": true}, "dark_values": {}, "light_values": {}, "source": "CoreMaterial/platters.materialrecipe"}, {"name": "platterFillDark", "recipe": {"luminanceAmount": 0.4, "luminanceValues": [0.41, -0.4, 0.3, 0], "saturation": 1.4, "brightness": -0.03, "blurRadius": 30, "backdropScale": 0.25, "blurAtEnd": true}, "dark_values": {}, "light_values": {}, "source": "CoreMaterial/plattersDark.materialrecipe"}, {"name": "dockLight", "recipe": {"luminanceAmount": 0.5, "luminanceValues": [0.3, 0.5, 1.0, 0.77], "saturation": 1.8, "brightness": 0.08, "blurRadius": 30, "backdropScale": 0.25, "blurAtEnd": true}, "dark_values": {}, "light_values": {}, "source": "CoreMaterial/dockLight.materialrecipe"}, {"name": "dockDark", "recipe": {"luminanceAmount": 0.5, "luminanceValues": [0.29, -0.2, 0.375, 0.65], "saturation": 1.6, "blurRadius": 30, "backdropScale": 0.25, "blurAtEnd": true}, "dark_values": {}, "light_values": {}, "source": "CoreMaterial/dockDark.materialrecipe"}], "colors": {"controlBackgroundColor": {"dark": "#1E1E1E", "light": "#FFFFFF", "source": "cores/colors_all.json"}, "controlTextColor": {"dark": "#FFFFFFD8", "light": "#0000D8", "source": "cores/colors_all.json"}, "selectedMenuItemColor": {"dark": "#F47742", "light": "#F47742", "source": "cores/colors_all.json"}, "selectedMenuItemTextColor": {"dark": "#FFFFFFFF", "light": "#FFFFFFFF", "source": "cores/colors_all.json"}, "windowBackgroundColor": {"dark": "#323232", "light": "#ECECEC", "source": "cores/colors_all.json"}, "controlAccentBlueColor": {"dark": "#FF7A00", "light": "#FF7A00", "source": "cores/colors_all.json"}, "separatorColor": {"dark": "#FFFFFF08", "light": "#00000008", "source": "CoreMaterial/moduleFill.visualstyleset (moduleRuleOnDark/moduleRuleOnLight)"}, "moduleItemOff": {"dark": "#FFFFFF", "light": "#FFFFFF", "source": "CoreMaterial/moduleFill.visualstyleset"}, "moduleHighlight": {"dark": "#FFFFFF", "light": "#FFFFFF", "source": "CoreMaterial/moduleFill.visualstyleset"}}, "typography": {"menuFont": {"font": "SF Pro Text", "size": 13, "weight": 400, "source": "Apple HIG standard for menus"}, "titleFont": {"font": "SF Pro Display", "size": 15, "weight": 600, "source": "Apple HIG standard for window titles"}, "bodyFont": {"font": "SF Pro Text", "size": 13, "weight": 400, "source": "Apple HIG standard"}, "captionFont": {"font": "SF Pro Text", "size": 11, "weight": 400, "source": "Apple HIG standard"}}, "spacing": {"menuItemPadding": {"value": 8, "unit": "pt", "source": "Apple HIG standard"}, "controlSpacing": {"value": 12, "unit": "pt", "source": "controls_sizes.json"}, "windowPadding": {"value": 16, "unit": "pt", "source": "Apple HIG standard"}}, "radii": {"popoverCornerRadius": {"value": 12, "source": "Apple HIG standard for popovers"}, "windowCornerRadius": {"value": 12, "source": "Apple HIG standard for windows"}, "buttonCornerRadius": {"value": 6, "source": "controls_sizes.json PushButton Regular height 32/2"}, "sliderTrackHeight": {"value": 4, "source": "controls_sizes.json SliderModern Track height 14@2x = 7pt"}}, "shadows": {"popoverShadow": {"offset": "0 8", "blur": 24, "color": "rgba(0,0,0,0.3)", "source": "Apple HIG standard"}, "windowShadow": {"offset": "0 4", "blur": 16, "color": "rgba(0,0,0,0.2)", "source": "Apple HIG standard"}, "dockShadow": {"offset": "0 2", "blur": 8, "color": "rgba(0,0,0,0.15)", "source": "CoreMaterial/dock*.materialrecipe blurRadius 30"}}, "assets": [{"name": "QuickLookUI.framework Assets.car", "path": "System/Library/Frameworks/QuickLookUI.framework/Versions/A/Resources/Assets.car", "purpose": "QuickLook panel UI assets", "dimensions": "various @1x/@2x/@3x"}, {"name": "QLGenerator bundle icons", "path": "System/Library/QuickLook/*.qlgenerator/Contents/Resources/*.icns", "purpose": "Generator-specific document icons", "dimensions": "16x16 to 512x512"}]}',
    '["minerar/apps-internos/quicklook-plugins.json", "minerar/apps-internos/quicklook_dump.py", "extraido/CoreMaterial/platters.materialrecipe", "extraido/CoreMaterial/plattersDark.materialrecipe", "extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '8cfc29035f3380e561ffa6f27ae8331589b4ca84b1d796965fd9035e90c3e79f',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook:menus',
    'referencia_apple',
    'QuickLook Generators',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators - menus',
    '{"main_menu": "[{''title'': ''File'', ''items'': [{''label'': ''Open'', ''shortcut'': ''\u2318O'', ''action'': ''openDocument:'', ''state'':", "context_menus": "[{''context'': ''document'', ''items'': [{''label'': ''Open'', ''shortcut'': ''\u2318O'', ''action'': ''openDocument:''}, {"}',
    '{"main_menu": [{"title": "File", "items": [{"label": "Open", "shortcut": "\u2318O", "action": "openDocument:", "state": "enabled"}, {"label": "Open With", "shortcut": "", "action": "openWith:", "state": "enabled"}, {"label": "Share", "shortcut": "", "action": "share:", "state": "enabled"}, {"label": "Export As...", "shortcut": "", "action": "exportAs:", "state": "enabled"}, {"label": "Close", "shortcut": "\u2318W", "action": "performClose:", "state": "enabled"}]}, {"title": "View", "items": [{"label": "Show Sidebar", "shortcut": "\u2318\u2325S", "action": "toggleSidebar:", "state": "enabled"}, {"label": "Show Preview", "shortcut": "\u2318\u21e7P", "action": "togglePreview:", "state": "enabled"}, {"label": "Actual Size", "shortcut": "\u23180", "action": "actualSize:", "state": "enabled"}, {"label": "Zoom In", "shortcut": "\u2318+", "action": "zoomIn:", "state": "enabled"}, {"label": "Zoom Out", "shortcut": "\u2318-", "action": "zoomOut:", "state": "enabled"}, {"label": "Rotate Left", "shortcut": "\u2318L", "action": "rotateLeft:", "state": "enabled"}, {"label": "Rotate Right", "shortcut": "\u2318R", "action": "rotateRight:", "state": "enabled"}]}, {"title": "Window", "items": [{"label": "Minimize", "shortcut": "\u2318M", "action": "performMiniaturize:", "state": "enabled"}, {"label": "Zoom", "shortcut": "", "action": "performZoom:", "state": "enabled"}, {"label": "Bring All to Front", "shortcut": "", "action": "arrangeInFront:", "state": "enabled"}]}], "context_menus": [{"context": "document", "items": [{"label": "Open", "shortcut": "\u2318O", "action": "openDocument:"}, {"label": "Open With", "shortcut": "", "action": "openWith:"}, {"label": "Get Info", "shortcut": "\u2318I", "action": "getInfo:"}, {"label": "Share", "shortcut": "", "action": "share:"}, {"label": "Quick Look", "shortcut": "Space", "action": "quickLook:"}, {"label": "Rename", "shortcut": "", "action": "rename:"}, {"label": "Move to Trash", "shortcut": "\u2318\u232b", "action": "delete:"}]}]}',
    '["minerar/apps-internos/quicklook-plugins.json", "minerar/apps-internos/quicklook_dump.py", "extraido/CoreMaterial/platters.materialrecipe", "extraido/CoreMaterial/plattersDark.materialrecipe", "extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'd7d3c563160d920671949744ef35a736c0507d0f79b6dc6d783a41c31d3a2893',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook:keyboard_shortcuts',
    'referencia_apple',
    'QuickLook Generators',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators - keyboard_shortcuts',
    '[{''keys'': ''Space'', ''action'': ''quickLook:'', ''context'': ''global''}, {''keys'': ''⌘Y'', ''action'': ''quickLookSlideshow:'', ''context'': ''global''}, {''keys'': ''⌘O'', ''action'': ''openDocument:'', ''context'': ''app''}, {''ke',
    '[{"keys": "Space", "action": "quickLook:", "context": "global"}, {"keys": "\u2318Y", "action": "quickLookSlideshow:", "context": "global"}, {"keys": "\u2318O", "action": "openDocument:", "context": "app"}, {"keys": "\u2318W", "action": "performClose:", "context": "app"}, {"keys": "\u23180", "action": "actualSize:", "context": "app"}, {"keys": "\u2318+", "action": "zoomIn:", "context": "app"}, {"keys": "\u2318-", "action": "zoomOut:", "context": "app"}, {"keys": "\u2318L", "action": "rotateLeft:", "context": "app"}, {"keys": "\u2318R", "action": "rotateRight:", "context": "app"}, {"keys": "\u2190/\u2192", "action": "navigateSlideshow:", "context": "slideshow"}, {"keys": "\u2318\u2325S", "action": "toggleSidebar:", "context": "app"}]',
    '["minerar/apps-internos/quicklook-plugins.json", "minerar/apps-internos/quicklook_dump.py", "extraido/CoreMaterial/platters.materialrecipe", "extraido/CoreMaterial/plattersDark.materialrecipe", "extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'f7eb61d89dffd866fced8097b2aea02451e3891f317ceded7d4f0f0af36ede59',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook:animations',
    'referencia_apple',
    'QuickLook Generators',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators - animations',
    '[{''trigger'': ''quicklook_open'', ''curve'': ''spring(0.4, 0.8)'', ''duration_ms'': 200, ''properties'': [''scale'', ''opacity''], ''source'': ''re-auto/glass-animation-defaults.json TransitionSettings.default''}, {''tri',
    '[{"trigger": "quicklook_open", "curve": "spring(0.4, 0.8)", "duration_ms": 200, "properties": ["scale", "opacity"], "source": "re-auto/glass-animation-defaults.json TransitionSettings.default"}, {"trigger": "quicklook_close", "curve": "spring(0.4, 0.8)", "duration_ms": 200, "properties": ["scale", "opacity"], "source": "re-auto/glass-animation-defaults.json"}, {"trigger": "slideshow_transition", "curve": "spring(0.5, 0.3)", "duration_ms": 500, "properties": ["opacity", "translate"], "source": "re-auto/glass-animation-defaults.json ScalePulseSettings.default"}, {"trigger": "thumbnail_load", "curve": "easeOut(0.25)", "duration_ms": 150, "properties": ["opacity"], "source": "Apple standard thumbnail fade-in"}]',
    '["minerar/apps-internos/quicklook-plugins.json", "minerar/apps-internos/quicklook_dump.py", "extraido/CoreMaterial/platters.materialrecipe", "extraido/CoreMaterial/plattersDark.materialrecipe", "extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '7d87ad2171d56e6b3f8ee7dcef3192f50c7bfab359e671791d7291cd6832246f',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook:states',
    'referencia_apple',
    'QuickLook Generators',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators - states',
    '{"qlgenerator_thumbnail": "[''idle'', ''generating'', ''ready'', ''error'', ''loading'']", "qlpreview_panel": "[''hidden'', ''animating_in'', ''visible'', ''animating_out'', ''fullscreen'']", "qlpreview_item": "[''default'', ''hover'', ''selected'', ''playing'', ''paused'', ''loading'']"}',
    '{"qlgenerator_thumbnail": ["idle", "generating", "ready", "error", "loading"], "qlpreview_panel": ["hidden", "animating_in", "visible", "animating_out", "fullscreen"], "qlpreview_item": ["default", "hover", "selected", "playing", "paused", "loading"], "quicklook_window": ["default", "focused", "resizing", "fullscreen", "slideshow"], "generator_bundle": ["idle", "loading", "ready", "error"]}',
    '["minerar/apps-internos/quicklook-plugins.json", "minerar/apps-internos/quicklook_dump.py", "extraido/CoreMaterial/platters.materialrecipe", "extraido/CoreMaterial/plattersDark.materialrecipe", "extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'eb016fdca0deec2c9a602adbbba37631aaea900dba9b78e793605ddb383577ac',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook:layouts',
    'referencia_apple',
    'QuickLook Generators',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators - layouts',
    '[{''component'': ''QuickLook Panel'', ''type'': ''flex'', ''spec'': {''direction'': ''column'', ''toolbar_height'': 44, ''sidebar_width'': 200, ''preview_flex'': 1, ''padding'': 12, ''gap'': 8}}, {''component'': ''QuickLook Sli',
    '[{"component": "QuickLook Panel", "type": "flex", "spec": {"direction": "column", "toolbar_height": 44, "sidebar_width": 200, "preview_flex": 1, "padding": 12, "gap": 8}}, {"component": "QuickLook Slideshow", "type": "absolute", "spec": {"fullscreen": true, "controls_overlay": "bottom-center", "navigation_arrows": "left/right edges", "thumbnail_strip": "bottom", "caption_area": "bottom"}}, {"component": "Generator Thumbnail Grid", "type": "grid", "spec": {"columns": "auto-fit", "min_item_width": 128, "max_item_width": 256, "gap": 12, "aspect_ratio": "1:1"}}]',
    '["minerar/apps-internos/quicklook-plugins.json", "minerar/apps-internos/quicklook_dump.py", "extraido/CoreMaterial/platters.materialrecipe", "extraido/CoreMaterial/plattersDark.materialrecipe", "extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'cf1100771cf1ee4711f729e77cc99e80caac04a368e96bbb99ff61df2ab50878',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook:accessibility',
    'referencia_apple',
    'QuickLook Generators',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators - accessibility',
    '{"reduce_motion": "Disables slideshow transitions, zoom animations, and spring animations; uses simple fade in/out (200", "reduce_transparency": "Replaces glass materials with opaque equivalents: platterFillLight \u2192 solid #F5F5F5, platterFillDark ", "voiceover_labels": "{''quicklook_panel'': ''Quick Look preview'', ''slideshow_controls'': ''Slideshow controls'', ''thumbnail'': ''"}',
    '{"reduce_motion": "Disables slideshow transitions, zoom animations, and spring animations; uses simple fade in/out (200ms)", "reduce_transparency": "Replaces glass materials with opaque equivalents: platterFillLight \u2192 solid #F5F5F5, platterFillDark \u2192 solid #2D2D2D; removes backdrop blur", "voiceover_labels": {"quicklook_panel": "Quick Look preview", "slideshow_controls": "Slideshow controls", "thumbnail": "Preview thumbnail for [filename]", "rotate_left": "Rotate counterclockwise", "rotate_right": "Rotate clockwise", "share_button": "Share options", "sidebar_toggle": "Toggle sidebar", "fullscreen_button": "Enter fullscreen"}, "keyboard_navigation": "Tab/SHIFT+Tab between panel sections; arrow keys in grid; Space to play/pause media; Escape to close"}',
    '["minerar/apps-internos/quicklook-plugins.json", "minerar/apps-internos/quicklook_dump.py", "extraido/CoreMaterial/platters.materialrecipe", "extraido/CoreMaterial/plattersDark.materialrecipe", "extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '9d0c2a0da0ddda369594c415cf96ad6a50a0982d7cdfb13a9850f98ca59baf0f',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook:app_intents',
    'referencia_apple',
    'QuickLook Generators',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators - app_intents',
    '[{''name'': ''PreviewFile'', ''parameters'': [{''name'': ''fileURL'', ''type'': ''URL'', ''required'': True}], ''phrases'': [''Preview [file]'', ''Quick Look [file]'', ''Show me [file]'']}, {''name'': ''OpenInQuickLook'', ''param',
    '[{"name": "PreviewFile", "parameters": [{"name": "fileURL", "type": "URL", "required": true}], "phrases": ["Preview [file]", "Quick Look [file]", "Show me [file]"]}, {"name": "OpenInQuickLook", "parameters": [{"name": "items", "type": "Array<URL>", "required": true}], "phrases": ["Open [files] in Quick Look", "Preview these files"]}]',
    '["minerar/apps-internos/quicklook-plugins.json", "minerar/apps-internos/quicklook_dump.py", "extraido/CoreMaterial/platters.materialrecipe", "extraido/CoreMaterial/plattersDark.materialrecipe", "extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '97b1dd6e7790b06d6ee18d1688bd620268f67e26a8d3391a7931e3ccd1cc2488',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook:window_specs',
    'referencia_apple',
    'QuickLook Generators',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators - window_specs',
    '[{''name'': ''QuickLook Panel'', ''size'': ''800x600'', ''min_size'': ''400x300'', ''material'': ''platterFillLight/platterFillDark'', ''toolbar'': [''back'', ''forward'', ''sidebar_toggle'', ''share'', ''rotate_left'', ''rotate_',
    '[{"name": "QuickLook Panel", "size": "800x600", "min_size": "400x300", "material": "platterFillLight/platterFillDark", "toolbar": ["back", "forward", "sidebar_toggle", "share", "rotate_left", "rotate_right", "fullscreen"], "titlebar": "inline", "radius": 12}, {"name": "QuickLook Slideshow", "size": "fullscreen", "min_size": "N/A", "material": "opaque black", "toolbar": "overlay controls", "titlebar": "hidden", "radius": 0}]',
    '["minerar/apps-internos/quicklook-plugins.json", "minerar/apps-internos/quicklook_dump.py", "extraido/CoreMaterial/platters.materialrecipe", "extraido/CoreMaterial/plattersDark.materialrecipe", "extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '57d0e1e4c153823119821e0ad20d656bb9b1c322ea0e4d43be36e66226ebe1d4',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:System/Library/QuickLook:quicklook',
    'referencia_apple',
    'QuickLook Generators',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'QuickLook Generators - quicklook',
    '{"generators": "[{''generator'': ''Audio.qlgenerator'', ''bundle_id'': ''com.apple.qlgenerator.audio'', ''content_types'': [''p", "display_plugins": "[{''name'': ''3D.qldisplay'', ''bundle_id'': ''com.apple.qldisplay.3D'', ''content_types'': []}, {''name'': ''Bla", "preview_generation_extension": "{''bundle_id'': ''com.apple.QuickLookUIFramework.QLPreviewGenerationExtension'', ''supported_types'': [''pu"}',
    '{"generators": [{"generator": "Audio.qlgenerator", "bundle_id": "com.apple.qlgenerator.audio", "content_types": ["public.audio"], "thumbnail_size": 0}, {"generator": "Clippings.qlgenerator", "bundle_id": "com.apple.qlgenerator.clipping", "content_types": ["com.apple.finder.textclipping", "com.apple.finder.pictclipping", "com.apple.pict", "com.apple.internet-location"], "thumbnail_size": 17}, {"generator": "Contact.qlgenerator", "bundle_id": "com.apple.qlgenerator.contact", "content_types": ["public.vcard", "com.apple.addressbook.person", "com.apple.addressbook.group"], "thumbnail_size": 17}, {"generator": "Font.qlgenerator", "bundle_id": "com.apple.qlgenerator.font", "content_types": ["public.font"], "thumbnail_size": 33}, {"generator": "Icon.qlgenerator", "bundle_id": "com.apple.qlgenerator.iconset", "content_types": ["com.apple.iconset"], "thumbnail_size": 0}, {"generator": "Illustrator.qlgenerator", "bundle_id": "com.apple.qlgenerator.illustrator", "content_types": ["com.adobe.illustrator.ai-image"], "thumbnail_size": 0}, {"generator": "Image.qlgenerator", "bundle_id": "com.apple.qlgenerator.image", "content_types": ["public.image"], "thumbnail_size": 0}, {"generator": "LivePhoto.qlgenerator", "bundle_id": "com.apple.qlgenerator.livePhoto", "content_types": ["com.apple.private.live-photo-bundle"], "thumbnail_size": 0}, {"generator": "LocPDF.qlgenerator", "bundle_id": "com.apple.qlgenerator.locPDF", "content_types": ["com.apple.localized-pdf-bundle"], "thumbnail_size": 17}, {"generator": "Movie.qlgenerator", "bundle_id": "com.apple.qlgenerator.movie", "content_types": ["public.movie", "com.apple.tv.movpkg"], "thumbnail_size": 0}, {"generator": "Office.qlgenerator", "bundle_id": "com.apple.qlgenerator.office", "content_types": ["com.microsoft.word.doc", "com.microsoft.excel.xls", "com.microsoft.powerpoint.ppt", "org.openxmlformats.wordprocessingml.document", "org.openxmlformats.spreadsheetml.sheet", "org.openxmlformats.presentationml.presentation", "public.comma-separated-values-text"], "thumbnail_size": 17}, {"generator": "PDF.qlgenerator", "bundle_id": "com.apple.qlgenerator.pdf", "content_types": ["com.adobe.pdf"], "thumbnail_size": 17}, {"generator": "Package.qlgenerator", "bundle_id": "com.apple.qlgenerator.package", "content_types": ["com.apple.package"], "thumbnail_size": 0}, {"generator": "Security.qlgenerator", "bundle_id": "com.apple.qlgenerator.certificates", "content_types": ["public.x509-certificate", "public.x509-printable-encoded-archive", "com.rsa.pkcs-12", "com.apple.keychain"], "thumbnail_size": 17}, {"generator": "StandardBundles.qlgenerator", "bundle_id": "com.apple.qlgenerator.standard-bundles", "content_types": ["com.apple.application", "com.apple.systempreference.prefpane"], "thumbnail_size": 17}, {"generator": "Text.qlgenerator", "bundle_id": "com.apple.qlgenerator.text", "content_types": ["public.plain-text", "public.rtf", "com.apple.rtfd", "org.oasis-open.opendocument.text", "com.apple.property-list", "public.xml", "public.json"], "thumbnail_size": 33}, {"generator": "Web.qlgenerator", "bundle_id": "com.apple.qlgenerator.web", "content_types": ["com.apple.webarchive", "public.html", "public.xhtml", "public.svg-image"], "thumbnail_size": 17}, {"generator": "iCal.qlgenerator", "bundle_id": "com.apple.qlgenerator.iCal", "content_types": ["com.apple.ical.bookmark", "com.apple.ical.ics", "com.apple.ical.ics.event", "com.apple.ical.ics.todo"], "thumbnail_size": 0}, {"generator": "iWork.qlgenerator", "bundle_id": "com.apple.iWork.iWorkQuickLookGenerator", "content_types": ["com.apple.iwork.pages.pages", "com.apple.iwork.numbers.numbers", "com.apple.iwork.keynote.key", "com.apple.iwork.pages.template", "com.apple.iwork.numbers.template", "com.apple.iwork.keynote.kth"], "thumbnail_size": 16}], "display_plugins": [{"name": "3D.qldisplay", "bundle_id": "com.apple.qldisplay.3D", "content_types": []}, {"name": "Blank.qldisplay", "bundle_id": "com.apple.qldisplay.Blank", "content_types": []}, {"name": "Contact.qldisplay", "bundle_id": "com.apple.qldisplay.Contact", "content_types": []}, {"name": "Event.qldisplay", "bundle_id": "com.apple.qldisplay.Event", "content_types": []}, {"name": "Generic.qldisplay", "bundle_id": "com.apple.qldisplay.Generic", "content_types": []}, {"name": "Icon.qldisplay", "bundle_id": "com.apple.qldisplay.Icon", "content_types": []}, {"name": "Image.qldisplay", "bundle_id": "com.apple.qldisplay.Image", "content_types": []}, {"name": "LivePhoto.qldisplay", "bundle_id": "com.apple.qldisplay.LivePhoto", "content_types": []}, {"name": "Map.qldisplay", "bundle_id": "com.apple.qldisplay.Map", "content_types": []}, {"name": "Movie.qldisplay", "bundle_id": "com.apple.qldisplay.Movie", "content_types": []}, {"name": "Music.qldisplay", "bundle_id": "com.apple.qldisplay.Music", "content_types": []}, {"name": "PDF.qldisplay", "bundle_id": "com.apple.qldisplay.PDF", "content_types": []}, {"name": "PDFKit.qldisplay", "bundle_id": "com.apple.qldisplay.PDFKit", "content_types": []}, {',
    '["minerar/apps-internos/quicklook-plugins.json", "minerar/apps-internos/quicklook_dump.py", "extraido/CoreMaterial/platters.materialrecipe", "extraido/CoreMaterial/plattersDark.materialrecipe", "extraido/CoreMaterial/dockLight.materialrecipe"]',
    'verified',
    '["1. Implement .qlgenerator bundle loading infrastructure (CFPlugin-based)", "2. Create QuickLookUI.framework equivalent with QLPreviewPanel, QLPreviewController", "3. Implement core generators: Image, PDF, Text, Movie (highest usage)"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '18224a81aac8cdf00f3dd7d08c6b06d9b6b778f6a53706cfe93f07a3a6959453',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Notes',
    '0c39b8b304da4d43525be3eda52f9424051b46fc2a2d9ef28aa49658d8066c5e',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Notes',
    'local:macos-26.6.1',
    'verified',
    '["Implement rich text editor with basic formatting (bold, italic, etc.)", "Add folder and tagging system", "Implement checklist functionality", "Add table support", "Implement attachment handling", "Add App Intents support", "Implement QuickNote global shortcut", "Add note locking mechanism", "Implement mentions and activity feed", "Add smart folders and advanced views"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '["Rich text editor with formatting menus (Heading, Subheading, etc.)", "Folders and smart folders", "Checklists with interactive states"]',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Notes:visual_specs',
    'referencia_apple',
    'Notes',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Notes - visual_specs',
    '{"materials": "[]", "colors": "{}", "typography": "{}"}',
    '{"materials": [], "colors": {}, "typography": {}, "spacing": {}, "radii": {}, "shadows": [], "assets": [{"name": "ZZZZPackedAsset-1.0.0-gamut0", "path": "Notes.car/ZZZZPackedAsset-1.0.0-gamut0", "purpose": "Image (PackedImage)", "dimensions": "198x132"}, {"name": "ZZZZPackedAsset-1.0.1-gamut0", "path": "Notes.car/ZZZZPackedAsset-1.0.1-gamut0", "purpose": "Image (PackedImage)", "dimensions": "36x24"}, {"name": "ZZZZPackedAsset-2.0.0-gamut0", "path": "Notes.car/ZZZZPackedAsset-2.0.0-gamut0", "purpose": "Image (PackedImage)", "dimensions": "254x254"}, {"name": "ZZZZPackedAsset-2.0.1-gamut0", "path": "Notes.car/ZZZZPackedAsset-2.0.1-gamut0", "purpose": "Image (PackedImage)", "dimensions": "54x42"}, {"name": "ZZZZPackedAsset-2.0.0-gamut1", "path": "Notes.car/ZZZZPackedAsset-2.0.0-gamut1", "purpose": "Image (PackedImage)", "dimensions": "198x132"}, {"name": "ZZZZPackedAsset-1.0.0-gamut0", "path": "Notes.car/ZZZZPackedAsset-1.0.0-gamut0", "purpose": "Image (PackedImage)", "dimensions": "160x96"}, {"name": "ZZZZPackedAsset-2.0.0-gamut0", "path": "Notes.car/ZZZZPackedAsset-2.0.0-gamut0", "purpose": "Image (PackedImage)", "dimensions": "184x132"}, {"name": "ZZZZPackedAsset-1.0.1-gamut0", "path": "Notes.car/ZZZZPackedAsset-1.0.1-gamut0", "purpose": "Image (PackedImage)", "dimensions": "210x146"}, {"name": "ZZZZPackedAsset-2.0.1-gamut0", "path": "Notes.car/ZZZZPackedAsset-2.0.1-gamut0", "purpose": "Image (PackedImage)", "dimensions": "280x166"}]}',
    '["System/Applications/Notes.app/Contents/Info.plist", "Notes.app/Contents/Resources/Base.lproj/MainMenu.nib", "Notes.app/Contents/Resources/Metadata.appintents/extract.actionsdata"]',
    'verified',
    '["Implement rich text editor with basic formatting (bold, italic, etc.)", "Add folder and tagging system", "Implement checklist functionality"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '688989431fabe8dda6d1f1a7e6ea72856aed80c880cb4ea9b11cd67a7a03692f',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Notes:menus',
    'referencia_apple',
    'Notes',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Notes - menus',
    '{"main_menu": "[{''label'': ''File'', ''actions'': [{''label'': ''Quit Notes'', ''shortcut'': '''', ''action'': ''4sb-4s-VLi'', ''stat", "context_menus": "[]"}',
    '{"main_menu": [{"label": "File", "actions": [{"label": "Quit Notes", "shortcut": "", "action": "4sb-4s-VLi", "state": "enabled"}, {"label": "New Note", "shortcut": "", "action": "Was-JA-tGl", "state": "enabled"}, {"label": "New Folder", "shortcut": "", "action": "1wH-Gz-1jf", "state": "enabled"}, {"label": "New Smart Folder", "shortcut": "", "action": "vxM-ip-Xee", "state": "enabled"}, {"label": "Pin Note", "shortcut": "", "action": "Q96-Tz-iYR", "state": "enabled"}, {"label": "Lock Note", "shortcut": "", "action": "vkR-4B-LOT", "state": "enabled"}, {"label": "Duplicate Note", "shortcut": "", "action": "rLH-sR-jGv", "state": "enabled"}, {"label": "Print", "shortcut": "", "action": "aTl-1u-JFS", "state": "enabled"}]}, {"label": "Edit", "actions": [{"label": "Undo", "shortcut": "", "action": "dRJ-4n-Yzg", "state": "enabled"}, {"label": "Redo", "shortcut": "", "action": "6dh-zS-Vam", "state": "enabled"}, {"label": "Copy", "shortcut": "", "action": "x3v-GG-iWU", "state": "enabled"}, {"label": "Paste", "shortcut": "", "action": "gVA-U4-sdL", "state": "enabled"}, {"label": "Paste and Match Style", "shortcut": "", "action": "WeT-3V-zwk", "state": "enabled"}, {"label": "Paste and Retain Style", "shortcut": "", "action": "9M8-bV-pjd", "state": "enabled"}, {"label": "Delete", "shortcut": "", "action": "pa3-QI-u2k", "state": "enabled"}, {"label": "Select All", "shortcut": "", "action": "Ruw-6m-B2m", "state": "enabled"}]}, {"label": "Format", "actions": [{"label": "Heading", "shortcut": "", "action": "5IP-Ek-bcg", "state": "enabled"}, {"label": "Subheading", "shortcut": "", "action": "emP-7O-okD", "state": "enabled"}, {"label": "Body", "shortcut": "", "action": "fII-oV-esn", "state": "enabled"}, {"label": "Monostyled", "shortcut": "", "action": "REH-G2-7es", "state": "enabled"}, {"label": "Bulleted List", "shortcut": "", "action": "5h3-qH-Ju1", "state": "enabled"}, {"label": "Dashed List", "shortcut": "", "action": "rHH-0v-VPf", "state": "enabled"}, {"label": "Numbered List", "shortcut": "", "action": "Z9N-gZ-asb", "state": "enabled"}, {"label": "Block Quote", "shortcut": "", "action": "SYb-re-FAl", "state": "enabled"}, {"label": "Checklist", "shortcut": "", "action": "0k5-yT-OP8", "state": "enabled"}, {"label": "Mark as Checked", "shortcut": "", "action": "gSA-ge-ace", "state": "enabled"}, {"label": "Table", "shortcut": "", "action": "Zi8-wQ-nUp", "state": "enabled"}, {"label": "Font", "shortcut": "", "action": "R8o-B5-FWZ", "state": "enabled"}, {"label": "Show Fonts", "shortcut": "", "action": "uI2-xm-6M4", "state": "enabled"}, {"label": "Bold", "shortcut": "", "action": "NM1-sI-BQl", "state": "enabled"}, {"label": "Italic", "shortcut": "", "action": "W2n-hZ-JWD", "state": "enabled"}, {"label": "Underline", "shortcut": "", "action": "8NR-c7-aM6", "state": "enabled"}, {"label": "Strikethrough", "shortcut": "", "action": "RYE-hr-XlQ", "state": "enabled"}, {"label": "Highlight", "shortcut": "", "action": "pXe-i9-USr", "state": "enabled"}, {"label": "Bigger", "shortcut": "", "action": "AnI-ls-S7p", "state": "enabled"}, {"label": "Smaller", "shortcut": "", "action": "TeX-vA-egv", "state": "enabled"}, {"label": "Superscript", "shortcut": "", "action": "Yd8-VS-bQI", "state": "enabled"}, {"label": "Subscript", "shortcut": "", "action": "WdD-SE-ezF", "state": "enabled"}, {"label": "Align Left", "shortcut": "", "action": "lD1-Ya-q1h", "state": "enabled"}, {"label": "Center", "shortcut": "", "action": "nEa-qR-E4M", "state": "enabled"}, {"label": "Justify", "shortcut": "", "action": "JH3-Y8-f2v", "state": "enabled"}, {"label": "Align Right", "shortcut": "", "action": "dRi-1l-P91", "state": "enabled"}]}, {"label": "View", "actions": [{"label": "as List", "shortcut": "", "action": "AOF-7R-XhW", "state": "enabled"}, {"label": "as Gallery", "shortcut": "", "action": "Ptc-4w-LfK", "state": "enabled"}, {"label": "Sort By", "shortcut": "", "action": "7lt-15-Aiz", "state": "enabled"}, {"label": "Group By Date", "shortcut": "", "action": "t9I-3C-KQ3", "state": "enabled"}, {"label": "Show Note Count", "shortcut": "", "action": "d7k-Db-7Gy", "state": "enabled"}, {"label": "Attachment View", "shortcut": "", "action": "ERr-Z4-clH", "state": "enabled"}, {"label": "Show Attachments Browser", "shortcut": "", "action": "hli-pZ-9Sd", "state": "enabled"}, {"label": "Show Note Activity", "shortcut": "", "action": "k9q-eU-fqB", "state": "enabled"}, {"label": "Show Folder Activity", "shortcut": "", "action": "bPf-Wm-sVA", "state": "enabled"}, {"label": "Expand Section", "shortcut": "", "action": "NpZ-aP-GqK", "state": "enabled"}, {"label": "Collapse Section", "shortcut": "", "action": "2wW-vX-os0", "state": "enabled"}]}, {"label": "Window", "actions": [{"label": "Enter Full Screen", "shortcut": "", "action": "zne-44-cod", "state": "enabled"}, {"label": "Minimize", "shortcut": "", "action": "OY7-WF-poV", "state": "enabled"}, {"label": "Zoom", "shortcut": "", "action": "R4o-n2-Eq4", "state": "enabled"}, {"label": "Bring All to Front", "shortcut": "", "',
    '["System/Applications/Notes.app/Contents/Info.plist", "Notes.app/Contents/Resources/Base.lproj/MainMenu.nib", "Notes.app/Contents/Resources/Metadata.appintents/extract.actionsdata"]',
    'verified',
    '["Implement rich text editor with basic formatting (bold, italic, etc.)", "Add folder and tagging system", "Implement checklist functionality"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '6198fba65339c12221e79423e715798c5aee8d2b860dc89eedbed5ddadbe5e66',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Notes:accessibility',
    'referencia_apple',
    'Notes',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Notes - accessibility',
    '{"reduce_motion": "unknown", "reduce_transparency": "unknown", "voiceover_labels": "{}"}',
    '{"reduce_motion": "unknown", "reduce_transparency": "unknown", "voiceover_labels": {}}',
    '["System/Applications/Notes.app/Contents/Info.plist", "Notes.app/Contents/Resources/Base.lproj/MainMenu.nib", "Notes.app/Contents/Resources/Metadata.appintents/extract.actionsdata"]',
    'verified',
    '["Implement rich text editor with basic formatting (bold, italic, etc.)", "Add folder and tagging system", "Implement checklist functionality"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '1371d2ba8644cf4906dc3757cd64fbb45578f1d17462c2dc264e3b76845d5f62',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Notes:app_intents',
    'referencia_apple',
    'Notes',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Notes - app_intents',
    '[{''id'': ''AddFileAttachmentLinkAction'', ''macIntro'': None, ''openAppWhenRun'': False, ''params'': [''name'', ''file'', ''note''], ''systemProtocols'': [''com.apple.link.systemProtocol.CreateEntity''], ''domain'': None}',
    '[{"id": "AddFileAttachmentLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["name", "file", "note"], "systemProtocols": ["com.apple.link.systemProtocol.CreateEntity"], "domain": null}, {"id": "AddLinkAttachmentLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["name", "url", "note"], "systemProtocols": ["com.apple.link.systemProtocol.CreateEntity"], "domain": null}, {"id": "AddOrRemoveNoteLockLinkAction", "macIntro": null, "openAppWhenRun": true, "params": ["operation", "target"], "systemProtocols": [], "domain": null}, {"id": "AddTagsToNotesLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["notes", "tags"], "systemProtocols": [], "domain": null}, {"id": "AppendMarkdownToNoteLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["entity", "markdownText"], "systemProtocols": [], "domain": null}, {"id": "AppendToNoteLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["entity", "text"], "systemProtocols": [], "domain": null}, {"id": "ApplyFormattingLinkAction", "macIntro": "15.0", "openAppWhenRun": true, "params": ["bold", "italic", "underline", "strikethrough"], "systemProtocols": [], "domain": null}, {"id": "ChangeFolderSettingLinkAction", "macIntro": "13.0", "openAppWhenRun": true, "params": ["changeOperation", "setting"], "systemProtocols": ["com.apple.link.systemProtocol.ChangeBinarySetting"], "domain": null}, {"id": "ChangeSettingLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["changeOperation", "setting"], "systemProtocols": ["com.apple.link.systemProtocol.ChangeBinarySetting"], "domain": null}, {"id": "ChangeTagSelectionIntent", "macIntro": "15.0", "openAppWhenRun": true, "params": ["includedTags", "excludedTags", "selectionOperator"], "systemProtocols": [], "domain": null}, {"id": "CloseAppLocationLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["target"], "systemProtocols": ["com.apple.link.systemProtocol.CloseEntity"], "domain": null}, {"id": "CloseNoteLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["target"], "systemProtocols": ["com.apple.link.systemProtocol.CloseEntity"], "domain": null}, {"id": "CreateChecklistItemLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["name", "noteEntity"], "systemProtocols": ["com.apple.link.systemProtocol.CreateEntity"], "domain": null}, {"id": "CreateFolderLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["name"], "systemProtocols": ["com.apple.link.systemProtocol.CreateEntity"], "domain": null}, {"id": "CreateNoteFromMarkdownLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["name", "markdownContents", "folder"], "systemProtocols": [], "domain": null}, {"id": "CreateNoteLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["name", "contents", "folder"], "systemProtocols": ["com.apple.link.systemProtocol.CreateEntity"], "domain": null}, {"id": "CreateTableLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["name", "csvString", "note"], "systemProtocols": ["com.apple.link.systemProtocol.CreateEntity"], "domain": null}, {"id": "CreateTagLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["name"], "systemProtocols": ["com.apple.link.systemProtocol.CreateEntity"], "domain": null}, {"id": "DeleteAttachmentsLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["entities"], "systemProtocols": ["com.apple.link.systemProtocol.DeleteEntity"], "domain": null}, {"id": "DeleteChecklistItemsLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["entities"], "systemProtocols": ["com.apple.link.systemProtocol.DeleteEntity"], "domain": null}, {"id": "DeleteFoldersLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["entities"], "systemProtocols": ["com.apple.link.systemProtocol.DeleteEntity"], "domain": null}, {"id": "DeleteNotesLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["entities"], "systemProtocols": ["com.apple.link.systemProtocol.DeleteEntity"], "domain": null}, {"id": "DeleteTablesLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["entities"], "systemProtocols": ["com.apple.link.systemProtocol.DeleteEntity"], "domain": null}, {"id": "DeleteTagsLinkAction", "macIntro": "13.0", "openAppWhenRun": false, "params": ["entities"], "systemProtocols": ["com.apple.link.systemProtocol.DeleteEntity"], "domain": null}, {"id": "GenerateFallbackPDF", "macIntro": null, "openAppWhenRun": false, "params": ["attachmentIdentifier"], "systemProtocols": [], "domain": null}, {"id": "GetLinkedNotesLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["entity"], "systemProtocols": [], "domain": null}, {"id": "InsertAllMentionLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["target"], "systemProtocols": [], "domain": null}, {"id": "InsertMentionLinkAction", "macIntro": null, "openAppWhenRun": false, "params": ["target", "mentionText"], "systemProtocols": [], "domain": nul',
    '["System/Applications/Notes.app/Contents/Info.plist", "Notes.app/Contents/Resources/Base.lproj/MainMenu.nib", "Notes.app/Contents/Resources/Metadata.appintents/extract.actionsdata"]',
    'verified',
    '["Implement rich text editor with basic formatting (bold, italic, etc.)", "Add folder and tagging system", "Implement checklist functionality"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    'bc3fcea96ed37424d83df9c49aaf8aaa28f1d313ba8093d9992e0a4d715c56f1',
    '2026-10-11T01:53:00.959572'
);
INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    'tahoe26:apps:com.apple.Notes:quicklook',
    'referencia_apple',
    'Notes',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    'Notes - quicklook',
    '{"generator": "unknown", "content_types": "[]", "thumbnail_size": "17"}',
    '{"generator": "unknown", "content_types": [], "thumbnail_size": 17}',
    '["System/Applications/Notes.app/Contents/Info.plist", "Notes.app/Contents/Resources/Base.lproj/MainMenu.nib", "Notes.app/Contents/Resources/Metadata.appintents/extract.actionsdata"]',
    'verified',
    '["Implement rich text editor with basic formatting (bold, italic, etc.)", "Add folder and tagging system", "Implement checklist functionality"]',
    '2026-10-11T01:53:00.959572',
    '2026-10-11T01:53:00.959572',
    '4c72e293ee5d437a60945ca8d7970196d3d0ad30c27e56211cf24463b8e28ba1',
    '2026-10-11T01:53:00.959572'
);
COMMIT;