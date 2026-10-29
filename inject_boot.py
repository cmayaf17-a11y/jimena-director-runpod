#!/usr/bin/env python3
"""Install a durable R2V prelaunch hook into the Hearmeman v10 boot chain.

At build time, modify the image's entry script. At each boot, after that
script syncs the pinned runtime, inject a hook just before ComfyUI launches.
The runtime provisions custom nodes before launch, so the R2V fix sees the
actual conditioning.py loaded by ComfyUI.
"""

from pathlib import Path
import sys


ENTRYPOINT = Path('/start_script.sh')
RUNTIME = Path('/comfyui-runtime/src/start.sh')
INJECTOR = '/opt/jimena/inject_boot.py'
FIXER = '/opt/jimena/fix_r2v.py'
ENTRY_ANCHOR = 'exec bash /comfyui-runtime/src/start.sh /comfyui-minimax'
RUNTIME_ANCHOR = 'echo "▶️  Starting ComfyUI"'
ENTRY_MARKER = '# JIMENA_BOOTSTRAP_R2V'
RUNTIME_MARKER = '# JIMENA_PRELAUNCH_R2V'


def replace_once(path: Path, anchor: str, marker: str, hook: str) -> None:
    body = path.read_text(encoding='utf-8')
    if marker in body:
        print(f'Hook ya presente: {path}')
        return
    occurrences = body.count(anchor)
    if occurrences != 1:
        raise RuntimeError(f'{path}: marcador de inicio esperado una vez, encontrado {occurrences}')
    path.write_text(body.replace(anchor, hook + anchor), encoding='utf-8')
    print(f'Hook instalado: {path}')


def main(mode: str) -> None:
    if mode == '--entrypoint':
        replace_once(
            ENTRYPOINT,
            ENTRY_ANCHOR,
            ENTRY_MARKER,
            f'{ENTRY_MARKER}\npython3 {INJECTOR} --runtime || exit 1\n',
        )
    elif mode == '--runtime':
        replace_once(
            RUNTIME,
            RUNTIME_ANCHOR,
            RUNTIME_MARKER,
            f'{RUNTIME_MARKER}\npython3 {FIXER} || {{ echo "ERROR: parche R2V fallido" >&2; exit 1; }}\n',
        )
    else:
        raise ValueError('Use --entrypoint or --runtime')


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except Exception as exc:
        print(f'ERROR Jimena boot: {exc}', file=sys.stderr)
        sys.exit(1)
