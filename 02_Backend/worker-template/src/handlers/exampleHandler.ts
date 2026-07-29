import { z } from "zod";
import { Env } from "../lib/env";
import { ok, fail } from "../lib/response";
import { requireAuth } from "../middleware/auth";
import { corsHeaders } from "../middleware/cors";
import { ExampleService } from "../services/exampleService";
import { logger } from "../lib/logger";

// Regla 05: Validación de entrada con Zod
const createExampleSchema = z.object({
  title: z.string().min(3, "El título debe tener al menos 3 caracteres.").max(100),
  description: z.string().max(500).optional().default(""),
});

export async function handleCreateExample(request: Request, env: Env): Promise<Response> {
  // 1. Auth middleware (Regla 04)
  const auth = await requireAuth(request, env);
  if (!auth.success) {
    return auth.errorResponse;
  }

  // 2. Parse body
  let body: unknown;
  try {
    body = await request.json();
  } catch (e) {
    return fail("VALIDATION_ERROR", "JSON mal formado.", 400, corsHeaders);
  }

  // 3. Validation (Regla 05)
  const parsed = createExampleSchema.safeParse(body);
  if (!parsed.success) {
    const message = parsed.error.issues.map(i => i.message).join(" ");
    return fail("VALIDATION_ERROR", message, 400, corsHeaders);
  }

  // 4. Service execution (Regla 02)
  const service = new ExampleService(auth.context.supabase);
  
  try {
    const result = await service.createExample(auth.context.user.id, parsed.data);
    return ok(result, corsHeaders);
  } catch (e) {
    logger.error("Error in handleCreateExample", e);
    return fail("INTERNAL_ERROR", "Ocurrió un error al procesar tu solicitud.", 500, corsHeaders);
  }
}
