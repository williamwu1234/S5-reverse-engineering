#!/usr/bin/env python3
"""Check distributable files against SHA256SUMS.json; offline, no camera access."""
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    manifest = json.loads((root / 'SHA256SUMS.json').read_text(encoding='utf-8'))
    errors = []
    for name, expected in manifest['files'].items():
        path = (root / name).resolve()
        if root not in path.parents or not path.is_file():
            errors.append(name + ': missing or outside package')
            continue
        h = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                h.update(chunk)
        if h.hexdigest() != expected['sha256'] or path.stat().st_size != expected['bytes']:
            errors.append(name + ': checksum/size mismatch')
    print(json.dumps({'checked_files': len(manifest['files']), 'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
