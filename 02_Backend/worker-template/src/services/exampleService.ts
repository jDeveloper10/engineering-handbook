import { SupabaseClient } from "@supabase/supabase-js";
import { logger } from "../lib/logger";

export interface CreateExampleData {
  title: string;
  description: string;
}

/**
 * Lógica de negocio y acceso a datos (Regla 02 y Regla 13).
 * Independiente de request/response de HTTP.
 */
export class ExampleService {
  constructor(private supabase: SupabaseClient) {}

  async createExample(userId: string, data: CreateExampleData) {
    logger.info("Creating example", { userId });

    // Regla 13: Columnas explícitas en cada select()
    const { data: result, error } = await this.supabase
      .from("examples")
      .insert({
        user_id: userId,
        title: data.title,
        description: data.description,
      })
      .select("id, title, created_at")
      .single();

    if (error) {
      logger.error("Database insert failed", error, { userId });
      throw new Error("DB_ERROR"); // Se atrapará en el router o handler
    }

    return result;
  }
}
