#!/usr/bin/env python3
"""Migra com backup e atualiza somente embeddings novos/alterados."""
import argparse
import json
from contextlib import closing
from pathlib import Path
from common import DB, connect
from hybrid import MODEL_DIR, index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=DB)
    parser.add_argument('--download-model', action='store_true', help='Baixar uma vez o modelo quantizado (~220 MB).')
    args = parser.parse_args()
    if args.download_model:
        from huggingface_hub import snapshot_download
        # Revision pinned to the actual downloaded model, also recorded in every vector.
        config = json.loads((Path(__file__).resolve().parents[1] / 'embedding-model.json').read_text())
        snapshot_download(config['repo'], revision=config['revision'], local_dir=MODEL_DIR,
                          allow_patterns=['model_optimized.onnx','config.json','tokenizer.json',
                                          'tokenizer_config.json','special_tokens_map.json'])
        (MODEL_DIR / 'revision.json').write_text(json.dumps(config,indent=2)+'\n')
    with closing(connect(args.db)) as conn:
        print(json.dumps(index(conn),ensure_ascii=False))


if __name__ == '__main__':
    # Permit the documented system-python command without changing global packages.
    from runtime import local_runtime
    local_runtime()
    main()
