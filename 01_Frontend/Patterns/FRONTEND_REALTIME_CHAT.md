---
title: "Patrón Chat en Tiempo Real (Supabase)"
category: 01_Frontend
tags: [react, realtime, chat, supabase, websockets]
status: current
---

# 💬 PATRÓN CHAT EN TIEMPO REAL

## 🎯 ¿Qué es y por qué es crítico?
Un chat moderno no puede depender de recargar la página ni de polling lento. Requiere WebSockets, manejo de escritura en vivo (typing indicators), y envío optimista para que la app se sienta instantánea, incluso en redes inestables (3G).

> **REGLA INQUEBRANTABLE:** Todo envío de mensaje DEBE ser *Optimistic*. El mensaje aparece en pantalla al instante, antes de confirmarse en el servidor. Si falla, mostrar error y un botón de reintento.

---

## 🗄️ ESQUEMA SQL & RLS (Supabase)

```sql
-- 1. Tablas
CREATE TABLE chat_rooms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_participants (
  room_id UUID REFERENCES chat_rooms(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  PRIMARY KEY (room_id, user_id)
);

CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  room_id UUID REFERENCES chat_rooms(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  is_edited BOOLEAN DEFAULT FALSE
);

CREATE TABLE message_reads (
  message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  read_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (message_id, user_id)
);

-- 2. Activar Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE messages;

-- 3. Row Level Security (RLS) - Crucial para seguridad
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Solo participantes pueden leer mensajes" ON messages
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM chat_participants cp WHERE cp.room_id = messages.room_id AND cp.user_id = auth.uid())
  );

CREATE POLICY "Solo participantes pueden enviar mensajes" ON messages
  FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM chat_participants cp WHERE cp.room_id = room_id AND cp.user_id = auth.uid())
    AND auth.uid() = user_id
  );
```

---

## 💻 HOOK: `useChat` (Realtime + Broadcast)

```tsx
import { useEffect, useState, useRef } from 'react'
import { supabase } from '@/lib/supabase'

export type Message = {
  id: string
  room_id: string
  user_id: string
  content: string
  created_at: string
  status?: 'sending' | 'sent' | 'error' // Propiedad del UI
}

export function useChat(roomId: string, currentUserId: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set())
  const [error, setError] = useState<string | null>(null)
  
  const channel = useRef<ReturnType<typeof supabase.channel> | null>(null)

  // 1. Cargar historial y suscribirse
  useEffect(() => {
    const fetchHistory = async () => {
      const { data } = await supabase
        .from('messages')
        .select('id, room_id, sender_id, body, created_at') // DB-001: nunca select('*')
        .eq('room_id', roomId)
        .order('created_at', { ascending: true })
      if (data) setMessages(data)
    }
    
    fetchHistory()

    // 2. Suscripción Realtime (WebSockets)
    channel.current = supabase.channel(`room:${roomId}`)
      
      // Escuchar nuevos mensajes en la DB
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages', filter: `room_id=eq.${roomId}` }, 
        (payload) => {
          const newMsg = payload.new as Message
          // Evitar duplicados si fue nuestro propio mensaje (ya insertado optimistamente)
          setMessages(prev => {
            const exists = prev.find(m => m.id === newMsg.id)
            if (exists) return prev.map(m => m.id === newMsg.id ? { ...newMsg, status: 'sent' } : m)
            return [...prev, { ...newMsg, status: 'sent' }]
          })
        }
      )
      
      // 3. Escuchar "Typing Indicator" (Broadcast, no toca la DB)
      .on('broadcast', { event: 'typing' }, ({ payload }) => {
        if (payload.userId !== currentUserId) {
          setTypingUsers(prev => new Set(prev).add(payload.userId))
          // Remover "escribiendo..." después de 3 segundos
          setTimeout(() => {
            setTypingUsers(prev => {
              const newSet = new Set(prev)
              newSet.delete(payload.userId)
              return newSet
            })
          }, 3000)
        }
      })
      .subscribe()

    return () => { supabase.removeChannel(channel.current!) }
  }, [roomId, currentUserId])

  // 4. Enviar Mensaje (Optimistic)
  const sendMessage = async (content: string) => {
    const optimisticId = crypto.randomUUID()
    const newMsg: Message = {
      id: optimisticId,
      room_id: roomId,
      user_id: currentUserId,
      content,
      created_at: new Date().toISOString(),
      status: 'sending'
    }

    // 1. Mostrar en UI instantáneamente
    setMessages(prev => [...prev, newMsg])

    // 2. Enviar a DB
    const { error } = await supabase
      .from('messages')
      .insert([{ id: optimisticId, room_id: roomId, user_id: currentUserId, content }])

    // 3. Manejo de error
    if (error) {
      setMessages(prev => prev.map(m => m.id === optimisticId ? { ...m, status: 'error' } : m))
      setError('Error al enviar el mensaje.')
    }
  }

  // 5. Emitir "Typing..."
  const sendTypingEvent = () => {
    channel.current?.send({
      type: 'broadcast',
      event: 'typing',
      payload: { userId: currentUserId }
    })
  }

  return { messages, typingUsers, sendMessage, sendTypingEvent, error }
}
```

---

## 🎨 UI: COMPONENTE CHAT WINDOW (Virtualizado)

Para salas con miles de mensajes, es **OBLIGATORIO** usar listas virtualizadas (ej: `react-virtuoso`) para evitar destruir la RAM y los frames por segundo (FPS) del navegador.

```tsx
import { useState, useRef, useEffect } from 'react'
import { Virtuoso } from 'react-virtuoso'
import { useChat } from './useChat'

export function ChatWindow({ roomId, currentUserId }) {
  const { messages, typingUsers, sendMessage, sendTypingEvent } = useChat(roomId, currentUserId)
  const [text, setText] = useState('')
  const virtuosoRef = useRef<VirtuosoHandle>(null)

  // Scroll automático abajo cuando llega un mensaje nuevo
  useEffect(() => {
    if (messages.length > 0) {
      virtuosoRef.current?.scrollToIndex({ index: messages.length - 1, align: 'end', behavior: 'smooth' })
    }
  }, [messages.length])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim()) return
    sendMessage(text)
    setText('')
  }

  return (
    <div className="flex flex-col h-[600px] border rounded-lg bg-gray-50">
      
      {/* 1. Área de Mensajes (Virtualizada) */}
      <div className="flex-1 overflow-hidden">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-400">
            No hay mensajes aún. ¡Di hola!
          </div>
        ) : (
          <Virtuoso
            ref={virtuosoRef}
            data={messages}
            initialTopMostItemIndex={messages.length - 1}
            itemContent={(index, msg) => {
              const isMe = msg.user_id === currentUserId
              return (
                <div className={`p-4 flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[70%] rounded-2xl p-3 ${
                    isMe ? 'bg-blue-600 text-white' : 'bg-white border text-gray-900'
                  } ${msg.status === 'error' ? 'border-red-500 opacity-50' : ''}`}>
                    <p>{msg.content}</p>
                    
                    {/* Indicador de Status Optimistic */}
                    <div className="text-[10px] text-right mt-1 opacity-70">
                      {msg.status === 'sending' && 'Enviando...'}
                      {msg.status === 'error' && 'Fallo al enviar. Clic para reintentar.'}
                      {msg.status === 'sent' && new Date(msg.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              )
            }}
          />
        )}
      </div>

      {/* 2. Typing Indicator */}
      {typingUsers.size > 0 && (
        <div className="px-4 py-2 text-xs text-gray-500 italic">
          Alguien está escribiendo...
        </div>
      )}

      {/* 3. Input de Mensaje */}
      <form onSubmit={handleSubmit} className="p-4 bg-white border-t flex gap-2">
        <input 
          type="text" 
          value={text}
          onChange={(e) => {
            setText(e.target.value)
            sendTypingEvent() // Emite el evento de broadcast
          }}
          placeholder="Escribe un mensaje..."
          className="flex-1 p-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button 
          type="submit" 
          disabled={!text.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-full disabled:opacity-50"
        >
          Enviar
        </button>
      </form>
    </div>
  )
}
```
