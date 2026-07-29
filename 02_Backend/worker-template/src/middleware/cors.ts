/**
 * Encabezados CORS centralizados (Regla 03).
 */

export const corsHeaders = {
  "Access-Control-Allow-Origin": "*", // Cambiar por el dominio específico en prod si es necesario
  "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, x-client-info",
  "Access-Control-Max-Age": "86400",
};

/**
 * Maneja las peticiones preflight (OPTIONS).
 */
export function handleOptions(request: Request): Response {
  if (
    request.headers.get("Origin") !== null &&
    request.headers.get("Access-Control-Request-Method") !== null &&
    request.headers.get("Access-Control-Request-Headers") !== null
  ) {
    return new Response(null, { headers: corsHeaders });
  }

  // Handle standard OPTIONS request.
  return new Response(null, {
    headers: {
      Allow: "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    },
  });
}
