import { createClient, SupabaseClient, User } from "@supabase/supabase-js";
import { Env } from "../lib/env";
import { fail } from "../lib/response";
import { corsHeaders } from "./cors";

export type AuthContext = {
  user: User;
  supabase: SupabaseClient;
};

export type AuthResult = 
  | { success: true; context: AuthContext }
  | { success: false; errorResponse: Response };

/**
 * Middleware único para autenticación (Regla 04 y Regla 13).
 */
export async function requireAuth(request: Request, env: Env): Promise<AuthResult> {
  const authHeader = request.headers.get("Authorization");
  
  if (!authHeader?.startsWith("Bearer ")) {
    return { 
      success: false, 
      errorResponse: fail("UNAUTHORIZED", "No autorizado.", 401, corsHeaders) 
    };
  }

  const token = authHeader.replace("Bearer ", "");
  
  // Usamos Service Role server-side (Regla 13)
  const supabase = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
    auth: { persistSession: false }
  });

  const { data: { user }, error } = await supabase.auth.getUser(token);

  if (error || !user) {
    return { 
      success: false, 
      errorResponse: fail("UNAUTHORIZED", "Token inválido o expirado.", 401, corsHeaders) 
    };
  }

  return { success: true, context: { user, supabase } };
}
