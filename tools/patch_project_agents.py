# -*- coding: utf-8 -*-
import os

security_note = """# AGENTS.md

> 🚨 **PRIORIDAD CRÍTICA DE SEGURIDAD (SEC-LEAK):**
> Antes de tocar cualquier funcionalidad de pagos, storage o trading, lee y ejecuta **[REMEDIACION_SEGURIDAD.md](REMEDIACION_SEGURIDAD.md)**.
> **Regla inquebrantable:** Prohibido usar secretos con prefijo `VITE_` (`VITE_METAAPI_*`, `VITE_R2_SECRET_*`, `VITE_NOWPAYMENTS_*`). Todas las llamadas con API keys privadas se ejecutan exclusivamente a través de los Workers correspondientes (`trading-worker`, `payments-worker`, `admin-worker`).
"""

targets = [
    r"E:\Trabajo\03_Trading\ingenusfx\AGENTS.md",
    r"E:\Trabajo\03_Trading\ingenusfx\CLAUDE.md"
]

for target in targets:
    if os.path.exists(target):
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        if "PRIORIDAD CRÍTICA DE SEGURIDAD" not in content:
            if content.startswith("# AGENTS.md"):
                new_content = content.replace("# AGENTS.md\n", security_note + "\n", 1)
            elif content.startswith("# CLAUDE.md"):
                new_content = content.replace("# CLAUDE.md\n", security_note.replace("AGENTS.md", "CLAUDE.md") + "\n", 1)
            else:
                new_content = security_note + "\n" + content
            with open(target, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Patched {target}")
        else:
            print(f"Already patched {target}")
