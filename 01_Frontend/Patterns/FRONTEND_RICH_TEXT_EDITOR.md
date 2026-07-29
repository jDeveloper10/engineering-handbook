---
title: "Editor de Texto Enriquecido (WYSIWYG)"
category: 01_Frontend
doc_type: estandar
tags: [tiptap, editor, wysiwyg, react, markdown]
summary: "Editor WYSIWYG con TipTap: configuración base, hook useDocumentEditor con autoguardado, componente de editor y serialización del contenido hacia Supabase."
keywords: [tiptap, editor, wysiwyg, react, markdown, texto, enriquecido, configuracion, base, hook, usedocumenteditor, autoguardado, componente, serializacion]
updated: 2026-07-29
status: current
---

# ✍️ EDITOR DE TEXTO ENRIQUECIDO (TipTap)

## 🎯 ¿Qué es y cuándo usarlo?
TipTap es el editor WYSIWYG headless (sin estilos propios) basado en ProseMirror. Es la elección estándar para este stack porque es React-first, TypeScript nativo, extensible por extensiones, y su output es JSON (Tiptap JSON) o HTML puro — lo que facilita la serialización en Supabase y la exportación.

> **[REQUIRED] REGLA:** El contenido del editor NUNCA se guarda como HTML crudo en la DB. Se guarda como **JSON serializado** (TipTap `JSONContent`) y se convierte a HTML solo en el momento de renderizar o exportar. Esto previene XSS estructural y facilita la colaboración CRDT.
>
> **Por qué:** guardar el HTML que produce el editor tal cual lo entrega el navegador expone al backend a renderizar contenido que el propio usuario controló en el cliente — un vector de XSS estructural. El JSON de TipTap no es HTML ejecutable: se convierte a HTML solo en el momento de renderizar, bajo control del propio sistema.

---

## ⚙️ 1. INSTALACIÓN Y CONFIGURACIÓN BASE

```bash
npm install @tiptap/react @tiptap/pm @tiptap/starter-kit @tiptap/extension-collaboration @tiptap/extension-mention @tiptap/extension-placeholder
```

---

## 💻 2. HOOK: `useDocumentEditor`

El hook encapsula la instancia de TipTap, la configuración de extensiones y la lógica de guardado.

```tsx
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Mention from '@tiptap/extension-mention'
import { useCallback, useEffect } from 'react'
import { useDebouncedCallback } from 'use-debounce'

export interface UseDocumentEditorOptions {
  documentId: string
  initialContent: JSONContent          // importado de @tiptap/core
  onSave: (content: JSONContent) => Promise<void>
  editable?: boolean
  teamMembers?: { id: string; label: string }[]
}

export function useDocumentEditor({
  documentId,
  initialContent,
  onSave,
  editable = true,
  teamMembers = []
}: UseDocumentEditorOptions) {
  
  // Guardado auto-guardado: 2s después del último cambio
  const debouncedSave = useDebouncedCallback(async (content: JSONContent) => {
    await onSave(content)
  }, 2000)

  const editor = useEditor({
    editable,
    extensions: [
      // 1. Extensiones base (headings, bold, italic, code, lists, blockquote)
      StarterKit.configure({
        history: false  // IMPORTANTE: deshabilitar history de StarterKit cuando se usa Yjs CRDT
      }),
      
      // 2. Placeholder
      Placeholder.configure({
        placeholder: 'Empieza a escribir tu documento aquí...'
      }),
      
      // 3. @menciones a miembros del equipo
      Mention.configure({
        HTMLAttributes: { class: 'mention' },
        suggestion: {
          items: ({ query }) =>
            teamMembers
              .filter(m => m.label.toLowerCase().includes(query.toLowerCase()))
              .slice(0, 5),
          render: () => {
            // Se implementa con un componente flotante de shadcn/ui (Popover)
            // Ver sección 4 de este documento
            return {
              onStart: () => {},
              onUpdate: () => {},
              onKeyDown: () => false,
              onExit: () => {}
            }
          }
        }
      })
    ],
    
    // Contenido inicial desde la DB (JSON)
    content: initialContent ?? { type: 'doc', content: [] },
    
    // Auto-guardar al cambiar
    onUpdate: ({ editor }) => {
      if (!editable) return
      debouncedSave(editor.getJSON())
    }
  })

  // Limpiar al desmontar
  useEffect(() => () => { editor?.destroy() }, [editor])

  // Obtener contenido para guardado manual
  const getContent = useCallback(() => editor?.getJSON(), [editor])
  
  // Exportar como Markdown (para exportación a .md)
  const getMarkdown = useCallback(() => {
    // TipTap no convierte a Markdown nativo; usar '@tiptap/extension-markdown' o convertir JSON
    // [NO CUBIERTO TOTALMENTE: requiere extensión adicional @tiptap/extension-markdown]
    return editor?.getText() ?? ''
  }, [editor])

  // Insertar imagen (upload a R2 primero)
  const insertImage = useCallback(async (file: File) => {
    if (!editor) return
    
    // 1. Subir a R2 con useFileUpload hook (PLAYBOOK_UPLOAD_FAIL.md)
    // 2. Una vez confirmada la URL, insertar
    const imageUrl = `https://assets.collabscribe.com/uploads/${documentId}/${crypto.randomUUID()}`
    
    editor.chain().focus().setImage({ src: imageUrl, alt: file.name }).run()
  }, [editor, documentId])

  return { editor, getContent, getMarkdown, insertImage }
}
```

---

## 🎨 3. COMPONENTE `DocumentEditor`

```tsx
import { EditorContent } from '@tiptap/react'
import { useDocumentEditor } from '@/hooks/useDocumentEditor'

export function DocumentEditor({
  documentId,
  initialContent,
  onSave,
  editable,
  teamMembers
}) {
  const { editor } = useDocumentEditor({
    documentId, initialContent, onSave, editable, teamMembers
  })

  if (!editor) return (
    <div className="h-96 bg-surface animate-pulse rounded-lg" />
  )

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Barra de herramientas */}
      {editable && <EditorToolbar editor={editor} />}
      
      {/* Área de escritura */}
      <EditorContent
        editor={editor}
        className="prose dark:prose-invert max-w-none min-h-[500px] p-8 focus:outline-none"
      />
    </div>
  )
}

function EditorToolbar({ editor }) {
  return (
    <div className="flex flex-wrap gap-1 p-2 border-b bg-surface sticky top-0 z-10">
      {/* Bold */}
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        className={`px-3 py-1 rounded text-sm font-bold ${editor.isActive('bold') ? 'bg-primary text-primary-foreground' : 'hover:bg-surface'}`}
      >
        B
      </button>
      
      {/* Italic */}
      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        className={`px-3 py-1 rounded text-sm italic ${editor.isActive('italic') ? 'bg-primary text-primary-foreground' : 'hover:bg-surface'}`}
      >
        I
      </button>
      
      {/* Headings */}
      {[1, 2, 3].map(level => (
        <button
          key={level}
          onClick={() => editor.chain().focus().toggleHeading({ level }).run()}
          className={`px-3 py-1 rounded text-sm ${editor.isActive('heading', { level }) ? 'bg-primary text-primary-foreground' : 'hover:bg-surface'}`}
        >
          H{level}
        </button>
      ))}
      
      {/* Code Block */}
      <button
        onClick={() => editor.chain().focus().toggleCodeBlock().run()}
        className={`px-3 py-1 rounded text-sm font-mono ${editor.isActive('codeBlock') ? 'bg-primary text-primary-foreground' : 'hover:bg-surface'}`}
      >
        {'</>'}
      </button>
    </div>
  )
}
```

---

## 💾 4. SERIALIZACIÓN Y GUARDADO EN SUPABASE

```typescript
// El contenido se guarda como JSON serializado (TEXT en la DB)
// Columna: documents.content TEXT (DATABASE_ENGINEERING_STANDARD.md §2.4)

// GUARDAR: JSON → string para la DB
async function saveDocument(docId: string, content: JSONContent) {
  const { error } = await supabase
    .from('documents')
    .update({ content: JSON.stringify(content) }) // DB-001: columnas explícitas
    .eq('id', docId)

  if (error) throw error
}

// LEER: string → JSON para el editor
async function loadDocument(docId: string) {
  const { data, error } = await supabase
    .from('documents')
    .select('id, title, content, status')  // DB-001: NUNCA SELECT *
    .eq('id', docId)
    .single()

  if (error) throw error

  return {
    ...data,
    content: data.content ? JSON.parse(data.content) : null
  }
}
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

- [ ] `StarterKit` con `history: false` si se usa Yjs (ver FRONTEND_CRDT_COLLABORATION.md)
- [ ] Auto-save con debounce de 2000ms — NUNCA guardar en cada keystroke
- [ ] Validación Zod del JSON antes de guardar (longitud máxima de contenido)
- [ ] Modo `editable: false` para lectores (Viewer role)
- [ ] Serialización como JSON, nunca HTML crudo en la DB
- [ ] Extensión Mention configurada con lista de miembros del equipo
- [ ] Estilos Tailwind con clase `prose` para tipografía del editor
