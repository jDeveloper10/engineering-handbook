# Estándar de Desarrollo Desktop (DESK-001 a DESK-005)

> 🔒 **Este documento define cómo se construye la app, no qué la mantiene segura.** Las reglas de seguridad del runtime de escritorio (ACL de IPC, validación de comandos nativos, CSP del webview, secretos en el keychain, updater firmado, code signing) viven en [05_Security/DESKTOP_SECURITY_STANDARD.md](../../05_Security/DESKTOP_SECURITY_STANDARD.md) (`DSEC-001` a `DSEC-011`) y son de lectura obligatoria antes de exponer cualquier comando al webview. Ante conflicto, manda el documento de seguridad.

## 🎯 Stack
- **Framework:** Tauri v2 + React
- **Backend nativo:** Rust
- **Comunicación:** IPC (invoke) + Events
- **Almacenamiento:** SQLite local + Supabase sync
- **Auto-updater:** Tauri updater

---

## ⚡ REGLAS INQUEBRANTABLES

### DESK-001: LÓGICA PESADA EN RUST, UI EN REACT

**Regla:**
Todo lo que requiera filesystem, procesamiento intensivo, o acceso al SO debe ir en Rust.
React solo para UI.

```
src-tauri/
├── src/
│   ├── main.rs        # Entry point
│   ├── commands/       # Comandos IPC
│   │   ├── files.rs   # File I/O
│   │   ├── printer.rs # Impresión
│   │   └── sync.rs    # Sincronización
│   └── db.rs          # SQLite local
src/
├── App.tsx            # React UI
└── ...
```

---

### DESK-002: COMUNICACIÓN IPC RUST → REACT

```rust
// src-tauri/src/commands/files.rs
#[tauri::command]
async fn read_file(path: String) -> Result<String, String> {
    std::fs::read_to_string(&path)
        .map_err(|e| format!("Error leyendo archivo: {}", e))
}

#[tauri::command]
async fn save_pdf(data: Vec<u8>, path: String) -> Result<(), String> {
    std::fs::write(&path, data)
        .map_err(|e| format!("Error guardando PDF: {}", e))
}
```

```typescript
// src/hooks/useFileSystem.ts
import { invoke } from '@tauri-apps/api/tauri'

export function useFileSystem() {
  const readFile = async (path: string) => {
    return await invoke('read_file', { path })
  }
  
  const savePdf = async (data: Uint8Array, path: string) => {
    return await invoke('save_pdf', { data: Array.from(data), path })
  }
  
  return { readFile, savePdf }
}
```

---

### DESK-003: OFFLINE TOTAL CON SQLITE

```rust
// src-tauri/src/db.rs
use rusqlite::{Connection, params};

pub fn init_db() -> Connection {
    let conn = Connection::open("omnisuite.db").unwrap();
    conn.execute_batch("
        CREATE TABLE IF NOT EXISTS proposals (
            id TEXT PRIMARY KEY,
            client_name TEXT NOT NULL,
            total_cents INTEGER NOT NULL,
            status TEXT NOT NULL,
            synced INTEGER DEFAULT 0
        );
    ").unwrap();
    conn
}

#[tauri::command]
async fn get_unsynced() -> Vec<Proposal> {
    let conn = init_db();
    let mut stmt = conn.prepare("SELECT id, title, status, updated_at FROM proposals WHERE synced = 0").unwrap();
    // ... retornar propuestas no sincronizadas
}
```

---

### DESK-004: AUTO-UPDATER

```json
// src-tauri/tauri.conf.json
{
  "updater": {
    "active": true,
    "endpoints": [
      "https://updates.omnisuite.com/{{target}}/{{current_version}}"
    ],
    "dialog": true,
    "pubkey": "YOUR_PUBLIC_KEY"
  }
}
```

---

### DESK-005: IMPRESIÓN DIRECTA

```rust
#[tauri::command]
async fn print_document(html: String) -> Result<(), String> {
    // Usar una librería de impresión nativa
    // o abrir diálogo de impresión del SO
    native_print::print(html)
}
```
