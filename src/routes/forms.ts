import { Hono } from "hono";
import { Env, FormLink } from "../types";
import { successResponse, errorResponse } from "../utils/response";
import { authMiddleware } from "../middleware/auth";

const formsRouter = new Hono<{ Bindings: Env }>();

/**
 * GET /api/forms (Public)
 */
formsRouter.get("/", async (c) => {
    const { results } = await c.env.DB.prepare(
        "SELECT * FROM form_links WHERE is_active = 1"
    ).all<FormLink>();

    return c.json(successResponse(results || []));
});

/**
 * PUT /api/forms/:key (Protected - Admin)
 */
formsRouter.put("/:key", authMiddleware, async (c) => {
    const key = c.req.param("key");
    const { title, google_form_url, is_active } = await c.req.json<{
        title?: string;
        google_form_url?: string;
        is_active?: number;
    }>();

    const existing = await c.env.DB.prepare("SELECT * FROM form_links WHERE key = ?").bind(key).first<FormLink>();
    if (!existing) {
        return c.json(errorResponse("Form link tidak ditemukan"), 404);
    }

    const newTitle = title ?? existing.title;
    const newUrl = google_form_url ?? existing.google_form_url;
    const newActive = is_active !== undefined ? is_active : existing.is_active;

    await c.env.DB.prepare(
        "UPDATE form_links SET title = ?, google_form_url = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?"
    ).bind(newTitle, newUrl, newActive, key).run();

    const updated = await c.env.DB.prepare("SELECT * FROM form_links WHERE key = ?").bind(key).first<FormLink>();
    return c.json(successResponse(updated, "Link form berhasil diperbarui"));
});

export default formsRouter;
