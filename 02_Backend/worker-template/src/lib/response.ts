/**
 * Helper para estandarizar todas las respuestas HTTP (Regla 01 y 09).
 */

export type AppError = {
  code: string;
  message: string;
};

export type AppResponse<T = unknown> = 
  | { success: true; data: T }
  | { success: false; error: AppError };

function jsonResponse(body: AppResponse, status: number, corsHeaders?: HeadersInit): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders,
    },
  });
}

/**
 * Devuelve una respuesta exitosa (HTTP 200).
 */
export function ok<T>(data: T, corsHeaders?: HeadersInit): Response {
  return jsonResponse({ success: true, data }, 200, corsHeaders);
}

/**
 * Devuelve un error estandarizado (HTTP configurable).
 * Nunca exponer detalles técnicos en `message`, solo mensajes seguros para el usuario.
 */
export function fail(code: string, message: string, status: number, corsHeaders?: HeadersInit): Response {
  return jsonResponse({ success: false, error: { code, message } }, status, corsHeaders);
}
