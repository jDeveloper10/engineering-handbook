/**
 * Utilidad básica de logs estructurados (Regla 10).
 */

export const logger = {
  info: (event: string, context?: Record<string, unknown>) => {
    console.log(JSON.stringify({ level: "info", event, ...context, timestamp: new Date().toISOString() }));
  },
  warn: (event: string, context?: Record<string, unknown>) => {
    console.warn(JSON.stringify({ level: "warn", event, ...context, timestamp: new Date().toISOString() }));
  },
  error: (event: string, err?: Error | unknown, context?: Record<string, unknown>) => {
    const errorMessage = err instanceof Error ? err.message : String(err);
    const stack = err instanceof Error ? err.stack : undefined;
    console.error(JSON.stringify({ level: "error", event, error: errorMessage, stack, ...context, timestamp: new Date().toISOString() }));
  }
};
