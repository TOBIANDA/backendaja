import { Context, Next } from "hono";
import { verify } from "hono/jwt";
import { Env } from "../types";
import { errorResponse } from "../utils/response";

export async function authMiddleware(c: Context<{ Bindings: Env }>, next: Next) {
    const authHeader = c.req.header("Authorization");
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
        return c.json(errorResponse("Unauthorized", "Header Authorization Bearer token diperlukan"), 401);
    }

    const token = authHeader.split(" ")[1];
    const secret = c.env.JWT_SECRET || "pmk_daniel_super_secret_jwt_key_2026";

    try {
        const payload = await verify(token, secret, "HS256");
        c.set("user" as any, payload);
        await next();
    } catch (err) {
        return c.json(errorResponse("Invalid or expired token", "Token tidak valid atau sudah kedaluwarsa"), 401);
    }
}
