---
title: "Estándar de WebSockets y Socket.io"
category: 02_Backend
doc_type: estandar
tags: [websocket, socket.io, realtime, eventos, streaming]
summary: "Estándar del dominio Backend para WebSockets: Socket.io, eventos, autenticación, salas, rate limiting y patrones."
keywords: [websocket, socket.io, realtime, eventos, streaming, salas]
updated: 2026-08-30
status: current
---

# WEBSOCKETS ENGINEERING STANDARD

> **Stack de referencia:** Socket.io + Express/Node.js
> **Depende de:** BACKEND_ENGINEERING_STANDARD.md (Nivel 1), SECURITY_ENGINEERING_STANDARD.md
> **Aplica a:** Todo proyecto que use WebSockets para comunicación en tiempo real

---

## 01. Configuración

### 1.1 Servidor Socket.io

**[REQUIRED]** Configurar Socket.io con Express:

```typescript
// src/server.ts
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';

const app = express();
const server = createServer(app);

const io = new Server(server, {
  cors: {
    origin: ['https://tuapp.com', 'http://localhost:5173'],
    methods: ['GET', 'POST'],
    credentials: true,
  },
  pingTimeout: 60000,
  pingInterval: 25000,
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### 1.2 Cliente Socket.io

**[REQUIRED]** Conexión del cliente con auto-reconnect:

```typescript
// src/lib/socket.ts
import { io, Socket } from 'socket.io-client';

const URL = import.meta.env.VITE_WS_URL || 'http://localhost:3000';

export const socket: Socket = io(URL, {
  autoConnect: false,
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  timeout: 20000,
});

export function connectSocket(token: string) {
  socket.auth = { token };
  socket.connect();
}

export function disconnectSocket() {
  socket.disconnect();
}
```

---

## 02. Autenticación

### 2.1 Auth en handshake

**[REQUIRED]** Validar token durante la conexión:

```typescript
// Servidor
io.use(async (socket, next) => {
  const token = socket.handshake.auth.token;
  
  if (!token) {
    return next(new Error('Authentication required'));
  }
  
  try {
    const user = await verifyToken(token);
    socket.data.user = user;
    next();
  } catch (err) {
    next(new Error('Invalid token'));
  }
});
```

### 2.2 Re-autenticación

**[REQUIRED]** Manejar expiración de tokens:

```typescript
// Cliente
socket.on('connect_error', (err) => {
  if (err.message === 'Invalid token' || err.message === 'Authentication required') {
    // Refrescar token y reconectar
    refreshToken().then(newToken => {
      socket.auth.token = newToken;
      socket.connect();
    });
  }
});
```

---

## 03. Eventos

### 3.1 Naming de eventos

**[REQUIRED]** Eventos en `kebab-case` con prefijo de dominio:

```typescript
// ✅ CORRECTO
socket.emit('order:created', orderData);
socket.emit('chat:message', message);
socket.emit('typing:start');

// ❌ PROHIBIDO
socket.emit('newOrder', orderData);    // Sin prefijo
socket.emit('CHAT_MESSAGE', message);  // SCREAMING_SNAKE
```

### 3.2 Eventos documentados

**[REQUIRED]** Documentar todos los eventos:

```typescript
// src/lib/events.ts
export const EVENTS = {
  // Cliente → Servidor
  'chat:send': 'chat:send',
  'typing:start': 'typing:start',
  'typing:stop': 'typing:stop',
  
  // Servidor → Cliente
  'chat:message': 'chat:message',
  'user:joined': 'user:joined',
  'user:left': 'user:left',
} as const;
```

### 3.3 Payloads tipados

**[REQUIRED]** Tipar payloads de eventos:

```typescript
// Tipos
interface ChatMessage {
  id: string;
  userId: string;
  content: string;
  timestamp: number;
}

// Emisión tipada
socket.emit('chat:send', { content: 'Hello' } as Omit<ChatMessage, 'id' | 'userId' | 'timestamp'>);

// Escucha tipada
socket.on('chat:message', (msg: ChatMessage) => {
  // msg está tipado
});
```

---

## 04. Salas (Rooms)

### 4.1 Unirse a salas

**[REQUIRED]** Usar salas para agrupar clientes:

```typescript
// Servidor
io.on('connection', (socket) => {
  // Unirse a sala de usuario
  socket.join(`user:${socket.data.user.id}`);
  
  // Unirse a sala de chat
  socket.on('chat:join', (chatId: string) => {
    socket.join(`chat:${chatId}`);
  });
  
  // Enviar mensaje solo a la sala
  socket.on('chat:send', (data) => {
    io.to(`chat:${data.chatId}`).emit('chat:message', {
      ...data,
      userId: socket.data.user.id,
      timestamp: Date.now(),
    });
  });
});
```

### 4.2 Broadcasting selectivo

**[REQUIRED]** Enviar a salas específicas, no a todos:

```typescript
// ❌ PROHIBIDO — envía a TODOS
io.emit('notification', data);

// ✅ CORRECTO — envía a sala específica
io.to(`user:${userId}`).emit('notification', data);

// ✅ CORRECTO — envía a sala de chat
io.to(`chat:${chatId}`).emit('chat:message', message);
```

---

## 05. Seguridad

### 5.1 Rate limiting por socket

**[REQUIRED]** Limitar eventos por conexión:

```typescript
const rateLimits = new Map<string, number[]>();

function checkSocketRateLimit(socketId: string, event: string, maxPerSecond = 10): boolean {
  const key = `${socketId}:${event}`;
  const now = Date.now();
  const timestamps = rateLimits.get(key) || [];
  const recent = timestamps.filter(t => now - t < 1000);
  
  if (recent.length >= maxPerSecond) {
    return false; // Rate limited
  }
  
  recent.push(now);
  rateLimits.set(key, recent);
  return true;
}

// Uso
socket.on('chat:send', (data) => {
  if (!checkSocketRateLimit(socket.id, 'chat:send', 5)) {
    return socket.emit('error', { message: 'Rate limited' });
  }
  // Procesar mensaje
});
```

### 5.2 Validación de payloads

**[REQUIRED]** Validar todo payload con Zod:

```typescript
import { z } from 'zod';

const ChatMessageSchema = z.object({
  content: z.string().min(1).max(1000),
  chatId: z.string().uuid(),
});

socket.on('chat:send', (data) => {
  const validation = ChatMessageSchema.safeParse(data);
  if (!validation.success) {
    return socket.emit('error', { message: 'Invalid payload' });
  }
  // Procesar con validation.data tipado
});
```

### 5.3 CORS estricto

**[REQUIRED]** CORS configurado para WebSocket:

```typescript
const io = new Server(server, {
  cors: {
    origin: ['https://tuapp.com'],  // ← EXPLÍCITO
    methods: ['GET', 'POST'],
    credentials: true,
  },
});
```

---

## 06. Desconexión

### 6.1 Manejo de desconexión

**[REQUIRED]** Limpiar recursos al desconectar:

```typescript
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.data.user.id}`);
  
  socket.on('disconnect', (reason) => {
    console.log(`User disconnected: ${socket.data.user.id}, reason: ${reason}`);
    // Limpiar estado del usuario
  });
});
```

### 6.2 Estado de conexión

**[REQUIRED]** Notificar a otros usuarios cuando alguien se conecta/desconecta:

```typescript
io.on('connection', (socket) => {
  // Notificar a la sala que el usuario se unió
  socket.on('chat:join', (chatId) => {
    socket.join(`chat:${chatId}`);
    socket.to(`chat:${chatId}`).emit('user:joined', {
      userId: socket.data.user.id,
      name: socket.data.user.name,
    });
  });
  
  socket.on('disconnect', () => {
    // Notificar a todas las salas del usuario
    for (const room of socket.rooms) {
      if (room.startsWith('chat:')) {
        socket.to(room).emit('user:left', {
          userId: socket.data.user.id,
        });
      }
    }
  });
});
```

---

## 07. Patrones

### 7.1 Chat en tiempo real

**[REQUIRED]** Patrón de chat con typing indicators:

```typescript
// Cliente
socket.on('chat:message', (msg) => {
  addMessage(msg);
  socket.emit('typing:stop');
});

function sendMessage(content: string, chatId: string) {
  socket.emit('chat:send', { content, chatId });
  socket.emit('typing:start');
}

// Servidor
socket.on('typing:start', () => {
  socket.to(`chat:${socket.data.currentChat}`).emit('typing:start', {
    userId: socket.data.user.id,
  });
});
```

### 7.2 Notificaciones push

**[REQUIRED]** Notificaciones en tiempo real:

```typescript
// Servidor
socket.on('notification:subscribe', (userId) => {
  socket.join(`user:${userId}`);
});

function sendNotification(userId: string, notification: Notification) {
  io.to(`user:${userId}`).emit('notification', notification);
}
```

---

## Checklist WebSockets

- [ ] CORS configurado con orígenes explícitos
- [ ] Auth en handshake con JWT
- [ ] Eventos en kebab-case con prefijo
- [ ] Payloads tipados con Zod
- [ ] Rate limiting por socket
- [ ] Salas para agrupar clientes
- [ ] Manejo de desconexión
- [ ] Broadcasting selectivo (no io.emit a todos)
