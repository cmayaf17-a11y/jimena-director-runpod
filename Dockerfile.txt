# Base exacta de la plantilla comprobada; no actualizar sin nueva validación.
FROM hearmeman/comfyui-minimax-template@sha256:b606d93b33b467d99861bca83f5eccd3bd7d1c7e6da785eec55375287034059f

COPY fix_r2v.py /opt/jimena/fix_r2v.py
COPY inject_boot.py /opt/jimena/inject_boot.py

# Modifica solo el punto de entrada que se sincroniza después a runtime.
# En cada arranque se inyecta el hook antes de iniciar ComfyUI.
RUN python3 /opt/jimena/inject_boot.py --entrypoint
