#!/usr/bin/env python3
"""
Generate SQL INSERT statements for BaseConhecimento/base.db from mining results.
"""
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

# Load all mining results
mining_files = [
    'mining_a22f4e35e301cfd70.json',      # DesignLibrary
    'mining_aeecc8ebdfe875636.json',      # ControlCenter
    'mining_a55fb0d87496cb97d.json',      # Preview
    'mining_a7b0a88092453fb7f.json',      # Reminders (menus only)
    'mining_aad81990a265ed553.json',      # QuickTime Player
    'mining_a7c7d3a67d1fc8810.json',      # TextEdit
    'mining_af02cd494f60c345a.json',      # Photos
    'mining_a2b7fb7d592fa4018.json',      # Stickies
    'corematerial_mined_output.json',      # CoreMaterial
    'quicklook-generators-mining.json',    # QuickLook Generators
]

base_path = Path('/home/igor/Projects/hyprmac')
all_results = []

for fname in mining_files:
    fpath = base_path / fname
    if fpath.exists():
        with open(fpath) as f:
            data = json.load(f)
            all_results.append(data)
            print(f"Loaded {fname}")
    else:
        print(f"Missing {fname}")

# Also check for other mining files that might have been saved as text
results_dir = base_path / 'results'
if results_dir.exists():
    for f in results_dir.glob('*.json'):
        if f.name not in [Path(x).name for x in mining_files]:
            with open(f) as fp:
                data = json.load(fp)
                all_results.append(data)
                print(f"Loaded {f.name}")

print(f"\nTotal mining results: {len(all_results)}")

# Generate SQL INSERT statements
sql_statements = []
sql_statements.append("-- Generated from Tahoe 26 DMG mining results")
sql_statements.append(f"-- Generated: {datetime.now().isoformat()}")
sql_statements.append("-- Source: ~/.local/share/hyprmac-pesquisa/macos-26.6.1/")
sql_statements.append("BEGIN;")

# Helper to compute SHA256 of evidence paths
def compute_sha256(paths):
    hasher = hashlib.sha256()
    for p in sorted(paths):
        hasher.update(p.encode())
    return hasher.hexdigest()

# Helper to properly escape strings for SQL
def sql_escape(s):
    """Escape string for SQL single-quoted string literal."""
    return s.replace("'", "''")

# Current timestamp
now = datetime.now().isoformat()

for result in all_results:
    app = result.get('app', 'unknown')
    bundle_id = result.get('bundle_id', 'unknown')
    priority = result.get('priority', 'P2')

    # Collect evidence paths
    evidence_paths = []
    if 'evidence' in result:
        for ev in result['evidence']:
            if isinstance(ev, dict) and 'path' in ev:
                evidence_paths.append(ev['path'])
            elif isinstance(ev, str):
                evidence_paths.append(ev)

    # Also add from visual_specs if there are sources
    if 'visual_specs' in result:
        vs = result['visual_specs']
        for key in ['materials', 'colors', 'typography', 'spacing', 'radii', 'shadows', 'assets']:
            if key in vs and vs[key]:
                if isinstance(vs[key], list):
                    for item in vs[key]:
                        if isinstance(item, dict) and 'source' in item:
                            evidence_paths.append(item['source'])
                elif isinstance(vs[key], dict):
                    for subkey, subval in vs[key].items():
                        if isinstance(subval, dict) and 'source' in subval:
                            evidence_paths.append(subval['source'])

    # Compute hash
    evidence_hash = compute_sha256(evidence_paths)

    # Create documentos entry
    doc_path = f"tahoe26:apps:{bundle_id}"
    impl_priority_json = sql_escape(json.dumps(result.get('implementation_priority', [])))
    gaps_json = sql_escape(json.dumps(result.get('gaps_vs_hyprmac', [])[:3]))

    sql_statements.append(f"""INSERT OR REPLACE INTO documentos (
    caminho, sha256, presente, tipo, estado, versao_macos, componente, fonte,
    confianca, implementacao, verificado_em, revisado_em, resumo, atualizado_em
) VALUES (
    '{doc_path}',
    '{evidence_hash}',
    1,
    'mining_result',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    '{sql_escape(app)}',
    'local:macos-26.6.1',
    'verified',
    '{impl_priority_json}',
    '{now}',
    '{now}',
    '{gaps_json}',
    '{now}'
);""")

    # Create registros entries for each component
    component_map = {
        'visual_specs': 'visual_specs',
        'menus': 'menus',
        'keyboard_shortcuts': 'keyboard_shortcuts',
        'animations': 'animations',
        'states': 'states',
        'layouts': 'layouts',
        'accessibility': 'accessibility',
        'app_intents': 'app_intents',
        'window_specs': 'window_specs',
        'quicklook': 'quicklook',
    }

    for comp_key, comp_name in component_map.items():
        if comp_key in result and result[comp_key]:
            reg_id = f"tahoe26:apps:{bundle_id}:{comp_name}"
            evidence_json = sql_escape(json.dumps(result[comp_key]))
            gaps_full_json = sql_escape(json.dumps(result.get('gaps_vs_hyprmac', [])))
            impl_priority_short_json = sql_escape(json.dumps(result.get('implementation_priority', [])[:3]))
            fonte_caminho_json = sql_escape(json.dumps(evidence_paths[:5]))

            # Build resumo
            if isinstance(result[comp_key], dict):
                resumo_dict = {k: str(v)[:100] for k, v in list(result[comp_key].items())[:3]}
                resumo_json = sql_escape(json.dumps(resumo_dict))
            else:
                resumo_json = sql_escape(str(result[comp_key])[:200])

            evidence_sha = hashlib.sha256(json.dumps(result[comp_key]).encode()).hexdigest()

            sql_statements.append(f"""INSERT OR REPLACE INTO registros (
    id, tipo, componente, estado, versao_macos, titulo, resumo, evidencia,
    fonte_caminho, confianca, implementacao, verificado_em, revisado_em, sha256, atualizado_em
) VALUES (
    '{reg_id}',
    'referencia_apple',
    '{sql_escape(app)}',
    'verified',
    'Tahoe 26.6.1 (25G76)',
    '{sql_escape(app)} - {comp_name}',
    '{resumo_json}',
    '{evidence_json[:5000]}',
    '{fonte_caminho_json}',
    'verified',
    '{impl_priority_short_json}',
    '{now}',
    '{now}',
    '{evidence_sha}',
    '{now}'
);""")

sql_statements.append("COMMIT;")

# Write to file
output_path = base_path / 'tahoe26_mining_inserts.sql'
with open(output_path, 'w') as f:
    f.write('\n'.join(sql_statements))

print(f"\nSQL INSERT statements written to: {output_path}")
print(f"Total statements: {len(sql_statements)}")
