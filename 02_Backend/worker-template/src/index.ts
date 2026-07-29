import { Env, validateEnv } from "./lib/env";
import { handleOptions, corsHeaders } from "./middleware/cors";
import { fail } from "./lib/response";
import { handleCreateExample } from "./handlers/exampleHandler";
import { logger } from "./lib/logger";

/**
 * Entry point del worker.
 * Solo se encarga de enrutamiento básico y captura de errores globales.
 * No contiene lógica de negocio (Regla 02).
 */
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    try {
      // 1. Validar entorno (Regla 06)
      validateEnv(env);

      // 2. Manejo de CORS preflight (Regla 03)
      if (request.method === "OPTIONS") {
        return handleOptions(request);
      }

      const url = new URL(request.url);
      const path = url.pathname;
      const method = request.method;

      // 3. Enrutamiento manual básico (puede reemplazarse con Hono o itty-router en el futuro)
      if (method === "POST" && path === "/api/example") {
        return await handleCreateExample(request, env);
      }
      
      // Health check endpoint
      if (method === "GET" && path === "/api/health") {
        return new Response(JSON.stringify({ status: "ok" }), {
          headers: { "Content-Type": "application/json", ...corsHeaders }
        });
      }

      // Ruta no encontrada
      return fail("NOT_FOUND", "La ruta solicitada no existe.", 404, corsHeaders);
      
    } catch (error) {
      // Manejo de errores globales no atrapados
      logger.error("Global unhandled error", error);
      return fail("INTERNAL_ERROR", "Ocurrió un error interno en el servidor.", 500, corsHeaders);
    }
  },
};
