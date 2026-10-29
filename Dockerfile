# Base exacta de la plantilla comprobada; no actualizar sin nueva validación.
FROM hearmeman/comfyui-minimax-template@sha256:b606d93b33b467d99861bca83f5eccd3bd7d1c7e6da785eec55375287034059f

# Activa el provisionamiento automático que ya incluye la plantilla original.
# Se puede cambiar en las variables de RunPod sin reconstruir la imagen.
ENV download_minimax_h3=true
ENV minimax_quant=int8

# El pack KJNodes y los nodos de ComfyUI Core vienen en la imagen original.
# Instalamos únicamente los cuatro packs que faltan en el workflow de 60 s.
# Los modelos grandes NO se incluyen en la imagen.
RUN set -eu; \
    git clone --depth=1 https://github.com/j955229/ComfyUI-MiniMax-H3-Motion-Director.git /ComfyUI/custom_nodes/minimax-h3-motion-director; \
    git clone --depth=1 https://github.com/jlucasmcrell/ComfyUI-H3-Multishot.git /ComfyUI/custom_nodes/ComfyUI-H3-Multishot; \
    git clone --depth=1 https://github.com/xmarre/ComfyUI-DiffAid-Patches.git /ComfyUI/custom_nodes/ComfyUI-DiffAid-Patches; \
    git clone --depth=1 https://github.com/ShmuelRonen/ComfyUI-FreeMemory.git /ComfyUI/custom_nodes/ComfyUI-FreeMemory; \
    for node_dir in \
        /ComfyUI/custom_nodes/minimax-h3-motion-director \
        /ComfyUI/custom_nodes/ComfyUI-H3-Multishot \
        /ComfyUI/custom_nodes/ComfyUI-DiffAid-Patches \
        /ComfyUI/custom_nodes/ComfyUI-FreeMemory; do \
        if [ -f "$node_dir/requirements.txt" ]; then \
            python3 -m pip install -r "$node_dir/requirements.txt"; \
        fi; \
    done

COPY fix_r2v.py /opt/jimena/fix_r2v.py
COPY inject_boot.py /opt/jimena/inject_boot.py

# Modifica solo el punto de entrada que se sincroniza después a runtime.
# En cada arranque se inyecta el hook antes de iniciar ComfyUI.
RUN python3 /opt/jimena/inject_boot.py --entrypoint
