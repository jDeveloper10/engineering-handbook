# -*- coding: utf-8 -*-
"""
Visualizador Neuronal Interactivo del Engineering Handbook.
Renderiza el grafo completo de capas, sinapsis, reglas inquebrantables
y simulaciones de flujo de datos en tiempo real usando Tkinter nativo.
"""

import math
import os
import random
import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox

# -----------------------------------------------------------------------------
# PALETA DE COLOR Y ESTILOS
# -----------------------------------------------------------------------------
BG_COLOR = "#070a13"
PANEL_BG = "#0d1322"
CARD_BG = "#131c31"
TEXT_COLOR = "#f1f5f9"
TEXT_MUTED = "#94a3b8"
TEXT_DIM = "#64748b"

COLOR_INPUT = "#38bdf8"       # Cyan
COLOR_ROUTER = "#c084fc"      # Purple
COLOR_DOMAIN = "#34d399"      # Emerald
COLOR_RULES = "#fb923c"       # Orange/Amber
COLOR_QA = "#60a5fa"          # Blue
COLOR_OUTPUT = "#4ade80"      # Neon Green
COLOR_SYNAPSE = "#1e293b"     # Dark Slate
COLOR_SYNAPSE_ACTIVE = "#38bdf8"

# -----------------------------------------------------------------------------
# ESTRUCTURA DE LA RED NEURONAL (CAPAS Y NODOS)
# -----------------------------------------------------------------------------
LAYERS = [
    {
        "id": "input",
        "name": "1. ENTRADA (Estímulos)",
        "color": COLOR_INPUT,
        "nodes": [
            {"id": "t_api", "label": "Nuevo Endpoint / API", "file": "03_API/API_ENGINEERING_STANDARD.md", "desc": "Petición para crear o modificar un endpoint REST."},
            {"id": "t_ui", "label": "Nueva UI / Pantalla", "file": "01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md", "desc": "Diseño y codificación de vista React/Tailwind."},
            {"id": "t_and", "label": "App Android (APK)", "file": "05_Security/MOBILE_SECURITY_STANDARD.md", "desc": "Desarrollo y empaquetado móvil Expo/React Native."},
            {"id": "t_dsk", "label": "App Desktop (Tauri)", "file": "01_Frontend/Core/DESKTOP_ENGINEERING_STANDARD.md", "desc": "App de escritorio con Tauri v2 + Rust + SQLite."},
            {"id": "t_pay", "label": "Cobros / Checkout", "file": "05_Security/PAYMENTS_SECURITY_STANDARD.md", "desc": "Integración con Stripe, webhooks y precios seguros."},
            {"id": "t_bug", "label": "Bugfix / Incidente", "file": "11_Debugging/DEBUGGING_TOOLKIT.md", "desc": "Diagnóstico y resolución con test de regresión."}
        ]
    },
    {
        "id": "router",
        "name": "2. CEREBRO & AUTO-RUTEO",
        "color": COLOR_ROUTER,
        "nodes": [
            {"id": "ag_core", "label": "AGENTS.md (Cerebro)", "file": "AGENTS.md", "desc": "Sistema de decisión central y mapa de auto-ruteo obligatorio."},
            {"id": "ai_flow", "label": "AI_WORKFLOW.md", "file": "13_AI_Rules/AI_WORKFLOW.md", "desc": "Protocolo de clasificación previa: ¡No codificar sin clasificar!"},
            {"id": "op_gate", "label": "Operating Gate", "file": "Engineering-OS/32-Operating-Gate.md", "desc": "Filtro de perfil de riesgo y completitud operativa."}
        ]
    },
    {
        "id": "domain",
        "name": "3. DOMINIOS TÉCNICOS",
        "color": COLOR_DOMAIN,
        "nodes": [
            {"id": "d_fe", "label": "01_Frontend (React/UI)", "file": "01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md", "desc": "Arquitectura modular, accesibilidad, CSS tokens y componentes."},
            {"id": "d_be", "label": "02_Backend / Workers", "file": "02_Backend/BACKEND_ENGINEERING_STANDARD.md", "desc": "Cloudflare Workers multi-worker y API REST estandarizada."},
            {"id": "d_db", "label": "04_Database & RLS", "file": "04_Database/DATABASE_ENGINEERING_STANDARD.md", "desc": "Supabase, RLS como fuente de verdad y recetas SQL."},
            {"id": "d_sec", "label": "05_Security & Threats", "file": "05_Security/SECURITY_ENGINEERING_STANDARD.md", "desc": "Modelo de amenazas, CSP estricta y zero-trust."},
            {"id": "d_mob", "label": "Mobile / Desktop Std", "file": "05_Security/MOBILE_SECURITY_STANDARD.md", "desc": "Reglas nativas para Android Keystore y Tauri IPC."}
        ]
    },
    {
        "id": "rules",
        "name": "4. REGLAS INQUEBRANTABLES",
        "color": COLOR_RULES,
        "nodes": [
            {"id": "r_s01", "label": "S-001 (Zod Obligatorio)", "file": "05_Security/SECURITY_ENGINEERING_STANDARD.md", "desc": "Todo payload de entrada se valida con esquemas Zod estrictos."},
            {"id": "r_mon", "label": "MONEY-001 / DB-008", "file": "04_Database/DATABASE_ENGINEERING_STANDARD.md", "desc": "Dinero en centavos (bigint), el backend fija el precio."},
            {"id": "r_rls", "label": "TENANT-001 / DB-001", "file": "04_Database/References/RLS_POLICIES_LIBRARY.md", "desc": "Aislamiento multi-tenant por RLS. Prohibido SELECT *."},
            {"id": "r_fe", "label": "FE-001 / FE-005", "file": "01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md", "desc": "Cero 'any' en TypeScript. 4 estados UI obligatorios."},
            {"id": "r_sec", "label": "MSEC-001 / DSEC-004", "file": "05_Security/DESKTOP_SECURITY_STANDARD.md", "desc": "Cero secretos en bundles. Tokens en Keystore/Keychain."}
        ]
    },
    {
        "id": "qa",
        "name": "5. AUDITORÍA & QA",
        "color": COLOR_QA,
        "nodes": [
            {"id": "q_lint", "label": "lint-handbook.mjs", "file": "tools/lint-handbook.mjs", "desc": "Linter estático que detecta SELECT *, any y mala praxis."},
            {"id": "q_test", "label": "06_Testing Pipeline", "file": "06_Testing/Pipelines/03_CI_CD.md", "desc": "Vitest para unitarios + Playwright para E2E."},
            {"id": "q_audit", "label": "Auditoría nmap & curl", "file": "05_Security/EXTERNAL_AUDIT_CHECKLIST.md", "desc": "Pruebas de caja negra con curl y nmap antes de producción."}
        ]
    },
    {
        "id": "output",
        "name": "6. TARGET DE SALIDA",
        "color": COLOR_OUTPUT,
        "nodes": [
            {"id": "o_web", "label": "🌐 Web App (Pages)", "file": "01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md", "desc": "Producción Web segura, responsive y accesible."},
            {"id": "o_and", "label": "📱 Android App (APK)", "file": "05_Security/MOBILE_SECURITY_STANDARD.md", "desc": "Binario APK firmado y blindado con Keystore."},
            {"id": "o_dsk", "label": "🖥️ Desktop App (Tauri)", "file": "01_Frontend/Core/DESKTOP_ENGINEERING_STANDARD.md", "desc": "App de escritorio con SQLite local y updater firmado."},
            {"id": "o_wrk", "label": "⚡ Edge Workers + DB", "file": "02_Backend/BACKEND_ENGINEERING_STANDARD.md", "desc": "Infraestructura Cloudflare distribuida con Supabase."}
        ]
    }
]

# Rutas estándar de sinapsis por defecto (interconexión completa)
SYNAPSES = [
    # Capa 1 -> Capa 2
    ("t_api", "ag_core"), ("t_ui", "ag_core"), ("t_and", "ag_core"),
    ("t_dsk", "ag_core"), ("t_pay", "ag_core"), ("t_bug", "ag_core"),
    ("ag_core", "ai_flow"), ("ai_flow", "op_gate"),

    # Capa 2 -> Capa 3
    ("op_gate", "d_fe"), ("op_gate", "d_be"), ("op_gate", "d_db"),
    ("op_gate", "d_sec"), ("op_gate", "d_mob"),

    # Capa 3 -> Capa 4 (Reglas)
    ("d_fe", "r_fe"), ("d_be", "r_s01"), ("d_db", "r_rls"),
    ("d_sec", "r_s01"), ("d_sec", "r_sec"), ("d_mob", "r_sec"),
    ("d_be", "r_mon"), ("d_fe", "r_mon"),

    # Capa 4 -> Capa 5 (QA)
    ("r_s01", "q_lint"), ("r_mon", "q_lint"), ("r_rls", "q_lint"),
    ("r_fe", "q_lint"), ("r_sec", "q_lint"),
    ("q_lint", "q_test"), ("q_test", "q_audit"),

    # Capa 5 -> Capa 6 (Salida)
    ("q_audit", "o_web"), ("q_audit", "o_and"),
    ("q_audit", "o_dsk"), ("q_audit", "o_wrk"),
]

# Escenarios predefinidos de simulación (recorrido exacto del impulso)
PRESETS = {
    "pay": {
        "title": "💳 Simulación: Endpoint de Cobros / Stripe",
        "path": ["t_pay", "ag_core", "ai_flow", "op_gate", "d_be", "d_sec", "r_mon", "r_s01", "q_lint", "q_test", "q_audit", "o_wrk"],
        "desc": "El flujo aplica MONEY-001 (backend fija precio), Zod para validar webhooks, y auditoría antes de desplegar en Workers."
    },
    "and": {
        "title": "📱 Simulación: App Móvil Android (APK Seguro)",
        "path": ["t_and", "ag_core", "ai_flow", "op_gate", "d_mob", "d_sec", "r_sec", "q_lint", "q_test", "q_audit", "o_and"],
        "desc": "El flujo exige MSEC-001 (cero secrets en bundle), almacenamiento Keystore y compilación con firma protegida."
    },
    "dsk": {
        "title": "🖥️ Simulación: App Desktop (Tauri v2 + SQLite)",
        "path": ["t_dsk", "ag_core", "ai_flow", "op_gate", "d_fe", "d_mob", "r_sec", "r_fe", "q_lint", "q_test", "q_audit", "o_dsk"],
        "desc": "El flujo aplica DESK-001 (lógica pesada en Rust), SQLite local offline, Keychain del SO y tests en Vitest."
    },
    "ui": {
        "title": "🎨 Simulación: Nueva Pantalla / Dashboard Web",
        "path": ["t_ui", "ag_core", "ai_flow", "op_gate", "d_fe", "r_fe", "q_lint", "q_test", "q_audit", "o_web"],
        "desc": "El flujo exige FE-001 (cero any) y FE-005 (Loading, Empty, Error, Success) con tests E2E en Playwright."
    },
    "sec": {
        "title": "🛡️ Simulación: Auditoría Externa (curl + nmap)",
        "path": ["t_bug", "ag_core", "ai_flow", "op_gate", "d_sec", "r_rls", "q_audit", "o_wrk", "o_web"],
        "desc": "Escaneo de puertos VPS con nmap, verificación de CSP/CORS con curl y endurecimiento de políticas RLS."
    }
}


class NeuralPulse:
    """Representa un impulso eléctrico viajando por una sinapsis."""
    def __init__(self, from_node, to_node, color, speed=0.03):
        self.from_node = from_node
        self.to_node = to_node
        self.color = color
        self.progress = 0.0
        self.speed = speed
        self.finished = False

    def update(self):
        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.finished = True

    def get_pos(self):
        x = self.from_node.x + (self.to_node.x - self.from_node.x) * self.progress
        y = self.from_node.y + (self.to_node.y - self.from_node.y) * self.progress
        return x, y


class Node:
    """Representa una neurona en el mapa."""
    def __init__(self, raw_data, layer_idx, node_idx, total_nodes, layer_color):
        self.id = raw_data["id"]
        self.label = raw_data["label"]
        self.file = raw_data.get("file", "")
        self.desc = raw_data.get("desc", "")
        self.layer_idx = layer_idx
        self.layer_color = layer_color
        self.radius = 16
        self.x = 0
        self.y = 0
        self.active_energy = 0.0  # Para animación de brillo
        self.highlighted = False

    def contains(self, px, py):
        return math.hypot(px - self.x, py - self.y) <= (self.radius + 10)


class NeuralHandbookVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Engineering Handbook — Red Neuronal de Decisiones y Auto-Ruteo")
        self.root.geometry("1240x820")
        self.root.minsize(1050, 700)
        self.root.configure(bg=BG_COLOR)

        # Directorio base del handbook
        self.handbook_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # Inicialización de nodos y sinapsis
        self.nodes = {}
        self.pulses = []
        self.selected_node = None
        self.hovered_node = None
        self.active_scenario = None
        self.continuous_mode = True

        self._build_nodes()
        self._build_ui()
        self._layout_nodes()

        # Eventos
        self.canvas.bind("<Configure>", lambda e: self._on_resize())
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_mouse_click)

        # Loop de animación (~60 FPS)
        self.last_auto_pulse = time.time()
        self._animate()

    def _build_nodes(self):
        for l_idx, layer in enumerate(LAYERS):
            tot = len(layer["nodes"])
            for n_idx, raw in enumerate(layer["nodes"]):
                node = Node(raw, l_idx, n_idx, tot, layer["color"])
                self.nodes[node.id] = node

    def _build_ui(self):
        # 1. Header / Barra superior
        top_bar = tk.Frame(self.root, bg=PANEL_BG, height=64, padx=16, pady=8)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        title_lbl = tk.Label(
            top_bar,
            text="🧠 MAPA NEURONAL DEL HANDBOOK",
            font=("Segoe UI", 13, "bold"),
            fg="#38bdf8",
            bg=PANEL_BG
        )
        title_lbl.pack(side=tk.LEFT)

        subtitle_lbl = tk.Label(
            top_bar,
            text=" |  Visualizador de Capas, Sinapsis y Auto-Ruteo en Tiempo Real",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=PANEL_BG
        )
        subtitle_lbl.pack(side=tk.LEFT)

        # Botón de modo continuo
        self.btn_pulse_mode = tk.Button(
            top_bar,
            text="⚡ Impulsos: ON",
            font=("Segoe UI", 9, "bold"),
            bg="#1e293b",
            fg="#38bdf8",
            activebackground="#334155",
            activeforeground="#ffffff",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._toggle_pulse_mode
        )
        self.btn_pulse_mode.pack(side=tk.RIGHT, padx=6)

        # 2. Barra de Simulaciones (Presets)
        sim_bar = tk.Frame(self.root, bg="#0b101d", padx=12, pady=6)
        sim_bar.pack(side=tk.TOP, fill=tk.X)

        sim_title = tk.Label(
            sim_bar,
            text="SIMULAR TAREA:",
            font=("Segoe UI", 8, "bold"),
            fg="#94a3b8",
            bg="#0b101d"
        )
        sim_title.pack(side=tk.LEFT, padx=(4, 8))

        buttons = [
            ("💳 Cobros / Stripe", "pay", "#fb923c"),
            ("📱 Android APK", "and", "#34d399"),
            ("🖥️ Desktop Tauri", "dsk", "#c084fc"),
            ("🎨 UI Dashboard", "ui", "#38bdf8"),
            ("🛡️ Auditoría nmap", "sec", "#f43f5e"),
        ]

        for text, key, col in buttons:
            btn = tk.Button(
                sim_bar,
                text=text,
                font=("Segoe UI", 8, "bold"),
                bg="#131c31",
                fg=col,
                activebackground="#1e293b",
                activeforeground="#ffffff",
                bd=0,
                padx=10,
                pady=3,
                cursor="hand2",
                command=lambda k=key: self._run_scenario(k)
            )
            btn.pack(side=tk.LEFT, padx=3)

        # 3. Contenedor Principal (Canvas a la izquierda, Inspector a la derecha)
        main_box = tk.Frame(self.root, bg=BG_COLOR)
        main_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Canvas de dibujo
        self.canvas = tk.Canvas(
            main_box,
            bg=BG_COLOR,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Panel lateral del Inspector
        self.inspector = tk.Frame(main_box, bg=PANEL_BG, width=320, padx=16, pady=16)
        self.inspector.pack(side=tk.RIGHT, fill=tk.Y)
        self.inspector.pack_propagate(False)

        self._build_inspector_panel()

    def _build_inspector_panel(self):
        tk.Label(
            self.inspector,
            text="INSPECTOR DE NODO",
            font=("Segoe UI", 10, "bold"),
            fg="#94a3b8",
            bg=PANEL_BG
        ).pack(anchor="w")

        self.ins_title = tk.Label(
            self.inspector,
            text="Selecciona una neurona",
            font=("Segoe UI", 12, "bold"),
            fg="#f8fafc",
            bg=PANEL_BG,
            wraplength=280,
            justify="left"
        )
        self.ins_title.pack(anchor="w", pady=(8, 4))

        self.ins_layer = tk.Label(
            self.inspector,
            text="Capa: —",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg=PANEL_BG
        )
        self.ins_layer.pack(anchor="w", pady=(0, 8))

        self.ins_desc = tk.Label(
            self.inspector,
            text="Pasa el ratón o haz clic sobre cualquier neurona para ver el estándar asociado, reglas y rol en el pipeline.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=PANEL_BG,
            wraplength=280,
            justify="left"
        )
        self.ins_desc.pack(anchor="w", pady=(0, 12))

        self.ins_file_lbl = tk.Label(
            self.inspector,
            text="Archivo fuente:",
            font=("Segoe UI", 8, "bold"),
            fg="#64748b",
            bg=PANEL_BG
        )
        self.ins_file_lbl.pack(anchor="w")

        self.ins_file = tk.Label(
            self.inspector,
            text="—",
            font=("Consolas", 8),
            fg="#e2e8f0",
            bg=CARD_BG,
            padx=8,
            pady=6,
            wraplength=270,
            justify="left"
        )
        self.ins_file.pack(fill=tk.X, pady=(4, 12))

        self.btn_open_file = tk.Button(
            self.inspector,
            text="📄 Abrir documento en IDE / Editor",
            font=("Segoe UI", 9, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            bd=0,
            pady=6,
            cursor="hand2",
            command=self._open_current_file
        )
        self.btn_open_file.pack(fill=tk.X, pady=(0, 16))

        # Sección de Estado de Simulación
        tk.Label(
            self.inspector,
            text="ESTADO DE LA SINAPSIS",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg=PANEL_BG
        ).pack(anchor="w", pady=(10, 4))

        self.sim_info_lbl = tk.Label(
            self.inspector,
            text="Red en reposo. Pulsa una simulación para ver el viaje del impulso.",
            font=("Segoe UI", 8),
            fg="#64748b",
            bg=PANEL_BG,
            wraplength=280,
            justify="left"
        )
        self.sim_info_lbl.pack(anchor="w")

    def _layout_nodes(self):
        w = max(self.canvas.winfo_width(), 700)
        h = max(self.canvas.winfo_height(), 500)

        num_layers = len(LAYERS)
        x_margin = 80
        y_margin = 60

        usable_w = w - (x_margin * 2)
        layer_spacing = usable_w / (num_layers - 1) if num_layers > 1 else 0

        for l_idx, layer in enumerate(LAYERS):
            x = x_margin + l_idx * layer_spacing
            nodes_in_layer = [n for n in self.nodes.values() if n.layer_idx == l_idx]
            tot = len(nodes_in_layer)

            usable_h = h - (y_margin * 2)
            y_spacing = usable_h / (tot + 1) if tot > 0 else 0

            for n_idx, node in enumerate(nodes_in_layer):
                node.x = x
                node.y = y_margin + (n_idx + 1) * y_spacing

    def _on_resize(self):
        self._layout_nodes()

    def _toggle_pulse_mode(self):
        self.continuous_mode = not self.continuous_mode
        if self.continuous_mode:
            self.btn_pulse_mode.configure(text="⚡ Impulsos: ON", fg="#38bdf8")
        else:
            self.btn_pulse_mode.configure(text="💤 Impulsos: OFF", fg="#94a3b8")

    def _run_scenario(self, key):
        if key not in PRESETS:
            return
        preset = PRESETS[key]
        self.active_scenario = preset
        self.sim_info_lbl.configure(text=f"{preset['title']}\n\n{preset['desc']}", fg="#38bdf8")

        # Apagar todos los nodos y encender la ruta del escenario
        path_ids = preset["path"]
        for node in self.nodes.values():
            node.highlighted = (node.id in path_ids)
            if node.id in path_ids:
                node.active_energy = 1.0

        # Lanzar impulsos encadenados a través de la ruta
        for i in range(len(path_ids) - 1):
            n1 = self.nodes.get(path_ids[i])
            n2 = self.nodes.get(path_ids[i + 1])
            if n1 and n2:
                # Disparo con retardo progresivo
                delay = i * 220
                self.root.after(delay, lambda f=n1, t=n2: self.pulses.append(NeuralPulse(f, t, "#38bdf8", speed=0.04)))

    def _on_mouse_move(self, event):
        hovered = None
        for node in self.nodes.values():
            if node.contains(event.x, event.y):
                hovered = node
                break

        if hovered != self.hovered_node:
            self.hovered_node = hovered
            if hovered:
                self.canvas.config(cursor="hand2")
                self._update_inspector(hovered)
            else:
                self.canvas.config(cursor="")
                if self.selected_node:
                    self._update_inspector(self.selected_node)

    def _on_mouse_click(self, event):
        for node in self.nodes.values():
            if node.contains(event.x, event.y):
                self.selected_node = node
                self._update_inspector(node)
                node.active_energy = 1.0

                # Disparar impulsos hacia todas sus conexiones salientes
                for f_id, t_id in SYNAPSES:
                    if f_id == node.id and t_id in self.nodes:
                        self.pulses.append(NeuralPulse(node, self.nodes[t_id], node.layer_color, speed=0.035))
                break

    def _update_inspector(self, node):
        layer_meta = LAYERS[node.layer_idx]
        self.ins_title.configure(text=node.label, fg=node.layer_color)
        self.ins_layer.configure(text=f"Capa {layer_meta['name']}", fg=node.layer_color)
        self.ins_desc.configure(text=node.desc)
        self.ins_file.configure(text=node.file if node.file else "(Regla lógica del sistema)")

    def _open_current_file(self):
        target_node = self.selected_node or self.hovered_node
        if not target_node or not target_node.file:
            messagebox.showinfo("Información", "Por favor selecciona un nodo que tenga un archivo fuente asociado.")
            return

        full_path = os.path.normpath(os.path.join(self.handbook_dir, target_node.file))
        if not os.path.exists(full_path):
            messagebox.showwarning("Archivo no encontrado", f"No se encontró el archivo:\n{full_path}")
            return

        try:
            if sys.platform == "win32":
                os.startfile(full_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", full_path])
            else:
                subprocess.Popen(["xdg-open", full_path])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

    def _animate(self):
        self.canvas.delete("all")

        # 1. Impulsos automáticos continuos de fondo
        now = time.time()
        if self.continuous_mode and (now - self.last_auto_pulse > 0.45):
            self.last_auto_pulse = now
            f_id, t_id = random.choice(SYNAPSES)
            if f_id in self.nodes and t_id in self.nodes:
                n1, n2 = self.nodes[f_id], self.nodes[t_id]
                self.pulses.append(NeuralPulse(n1, n2, n1.layer_color, speed=random.uniform(0.02, 0.045)))

        # 2. Dibujar títulos de columnas / Capas
        for l_idx, layer in enumerate(LAYERS):
            nodes_in_layer = [n for n in self.nodes.values() if n.layer_idx == l_idx]
            if nodes_in_layer:
                x = nodes_in_layer[0].x
                self.canvas.create_text(
                    x, 24,
                    text=layer["name"],
                    fill=layer["color"],
                    font=("Segoe UI", 9, "bold"),
                    anchor="center"
                )

        # 3. Dibujar Sinapsis (Líneas de conexión)
        for f_id, t_id in SYNAPSES:
            if f_id in self.nodes and t_id in self.nodes:
                n1 = self.nodes[f_id]
                n2 = self.nodes[t_id]

                is_highlighted = (n1.highlighted and n2.highlighted)
                line_color = n1.layer_color if is_highlighted else COLOR_SYNAPSE
                line_width = 2 if is_highlighted else 1

                self.canvas.create_line(
                    n1.x, n1.y, n2.x, n2.y,
                    fill=line_color,
                    width=line_width
                )

        # 4. Actualizar y dibujar Impulsos eléctricos (Partículas en movimiento)
        alive_pulses = []
        for p in self.pulses:
            p.update()
            if not p.finished:
                alive_pulses.append(p)
                px, py = p.get_pos()

                # Halo brillante
                self.canvas.create_oval(
                    px - 5, py - 5, px + 5, py + 5,
                    fill="",
                    outline=p.color,
                    width=1
                )
                # Núcleo del impulso
                self.canvas.create_oval(
                    px - 2.5, py - 2.5, px + 2.5, py + 2.5,
                    fill="#ffffff",
                    outline=p.color
                )
            else:
                # Al llegar a destino, activar energía del nodo receptor
                p.to_node.active_energy = 1.0

        self.pulses = alive_pulses

        # 5. Dibujar Neuronas (Nodos)
        for node in self.nodes.values():
            # Disipación de energía de activación
            if node.active_energy > 0:
                node.active_energy = max(0.0, node.active_energy - 0.03)

            r = node.radius
            is_hover = (node == self.hovered_node)
            is_sel = (node == self.selected_node)
            is_hl = node.highlighted

            # Brillo exterior si está activo o seleccionado
            if node.active_energy > 0.05 or is_hl or is_sel or is_hover:
                glow_r = r + 6 + (node.active_energy * 6)
                self.canvas.create_oval(
                    node.x - glow_r, node.y - glow_r,
                    node.x + glow_r, node.y + glow_r,
                    fill="",
                    outline=node.layer_color,
                    width=2 if is_sel else 1
                )

            # Cuerpo de la neurona
            node_bg = "#1e293b" if not (is_hl or is_sel or is_hover) else "#0f172a"
            border_col = node.layer_color if (is_hl or is_sel or is_hover or node.active_energy > 0.1) else "#334155"

            self.canvas.create_oval(
                node.x - r, node.y - r,
                node.x + r, node.y + r,
                fill=node_bg,
                outline=border_col,
                width=2
            )

            # Punto central brillante
            core_r = 4
            core_col = "#ffffff" if (node.active_energy > 0.1 or is_sel) else node.layer_color
            self.canvas.create_oval(
                node.x - core_r, node.y - core_r,
                node.x + core_r, node.y + core_r,
                fill=core_col,
                outline=""
            )

            # Etiqueta de texto bajo la neurona
            label_col = "#ffffff" if (is_hover or is_sel or is_hl) else TEXT_MUTED
            self.canvas.create_text(
                node.x, node.y + r + 10,
                text=node.label,
                fill=label_col,
                font=("Segoe UI", 8, "bold" if (is_hover or is_sel) else "normal"),
                anchor="n",
                width=115,
                justify="center"
            )

        # Repetir loop cada ~16ms (60 FPS)
        self.root.after(16, self._animate)


def main():
    root = tk.Tk()
    app = NeuralHandbookVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
