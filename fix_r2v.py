#!/usr/bin/env python3
"""Fix the MiniMax H3 Director R2V call for the verified ComfyUI 0.42.1 signature.

Idempotent and deliberately strict: an unexpected upstream change is an error,
not permission to replace arbitrary source text.
"""

import ast
import pathlib
import sys


TARGET = pathlib.Path(
    "/ComfyUI/custom_nodes/minimax-h3-motion-director/nodes/conditioning.py"
)


def fix(path: pathlib.Path) -> str:
    original = path.read_text(encoding="utf-8")
    tree = ast.parse(original, filename=str(path))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "execute"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "MiniMaxH3ReferenceToVideo"
    ]
    if len(calls) != 1:
        raise RuntimeError(f"Se esperaba 1 llamada R2V, hay {len(calls)}")

    call = calls[0]
    names = [arg.id if isinstance(arg, ast.Name) else None for arg in call.args]
    expected_old = [
        "clip", "vae", "audio_vae", "prompt", "width", "height", "length", "ref_image_size"
    ]
    expected_new = ["clip", "prompt", "width", "height", "length"]
    if names == expected_new:
        print("R2V: argumentos ya corregidos")
        return "already-correct"
    if names != expected_old:
        raise RuntimeError(f"Firma R2V desconocida: {names!r}")

    keyword_names = [kw.arg for kw in call.keywords]
    expected_keywords = ["ref_images", "ref_videos", "ref_video_audios", "ref_audios"]
    if keyword_names != expected_keywords:
        raise RuntimeError(f"Keywords R2V desconocidas: {keyword_names!r}")

    lines = original.splitlines(keepends=True)
    start, end = call.lineno - 1, call.end_lineno
    indentation = " " * call.col_offset
    replacement = (
        f"{indentation}MiniMaxH3ReferenceToVideo.execute(\n"
        f"{indentation}    clip, prompt, width, height, length,\n"
        f"{indentation}    ref_image_size=ref_image_size,\n"
        f"{indentation}    vae=vae, audio_vae=audio_vae,\n"
        f"{indentation}    ref_images=ref_images, ref_videos=ref_videos,\n"
        f"{indentation}    ref_video_audios=ref_video_audios, ref_audios=ref_audios,\n"
        f"{indentation})\n"
    )
    # Keep the original assignment prefix (e.g., "out = ") on the first line.
    first = lines[start]
    prefix = first[: first.index("MiniMaxH3ReferenceToVideo.execute(")]
    replacement = prefix + replacement.lstrip()
    updated = "".join(lines[:start]) + replacement + "".join(lines[end:])
    compile(updated, str(path), "exec")
    temporary = path.with_suffix(".py.r2vtmp")
    temporary.write_text(updated, encoding="utf-8")
    temporary.replace(path)
    print("R2V: corregido correctamente")
    return "fixed"


if __name__ == "__main__":
    try:
        fix(pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else TARGET)
    except Exception as exc:
        print(f"ERROR R2V: {exc}", file=sys.stderr)
        raise SystemExit(1)
