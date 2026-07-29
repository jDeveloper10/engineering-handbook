/**
 * Validación estricta de variables de entorno (Regla 06).
 */

export interface Env {
  SUPABASE_URL: string;
  SUPABASE_SERVICE_ROLE_KEY: string;
}

/**
 * Valida que todas las variables obligatorias estén presentes.
 * Lanza un error genérico (que el router atrapará) si falta alguna,
 * para no exponer internamente qué falta al cliente.
 */
export function validateEnv(env: Env): void {
  if (!env.SUPABASE_URL || !env.SUPABASE_SERVICE_ROLE_KEY) {
    throw new Error("Missing required environment variables.");
  }
}
