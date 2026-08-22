import { Hono } from "hono";
import { Env, Divisi, Pengurus } from "../types";
import { successResponse, errorResponse } from "../utils/response";
import { authMiddleware } from "../middleware/auth";

const pengurusRouter = new Hono<{ Bindings: Env }>();

/**
 * GET /api/pengurus (Public)
 * Returns all divisions with their nested board members
 */
pengurusRouter.get("/", async (c) => {
    const { results: divisions } = await c.env.DB.prepare(
        "SELECT * FROM divisi ORDER BY order_priority ASC"
    ).all<Divisi>();

    const { results: members } = await c.env.DB.prepare(
        "SELECT * FROM pengurus ORDER BY order_priority ASC"
    ).all<Pengurus>();

    const structured = (divisions || []).map(div => ({
        ...div,
        members: (members || []).filter(m => m.divisi_id === div.id)
    }));

    return c.json(successResponse(structured));
});

/**
 * POST /api/pengurus/divisi (Protected - Admin)
 */
pengurusRouter.post("/divisi", authMiddleware, async (c) => {
    const { name, description, order_priority } = await c.req.json<{
        name?: string;
        description?: string;
        order_priority?: number;
    }>();

    if (!name) {
        return c.json(errorResponse("Nama divisi wajib diisi"), 400);
    }

    const id = `div_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    await c.env.DB.prepare(
        "INSERT INTO divisi (id, name, description, order_priority) VALUES (?, ?, ?, ?)"
    ).bind(id, name, description || null, order_priority || 0).run();

    const created = await c.env.DB.prepare("SELECT * FROM divisi WHERE id = ?").bind(id).first<Divisi>();
    return c.json(successResponse(created, "Divisi berhasil dibuat"), 201);
});

/**
 * POST /api/pengurus/member (Protected - Admin)
 */
pengurusRouter.post("/member", authMiddleware, async (c) => {
    const { divisi_id, name, role, photo_url, period, order_priority } = await c.req.json<{
        divisi_id?: string;
        name?: string;
        role?: string;
        photo_url?: string;
        period?: string;
        order_priority?: number;
    }>();

    if (!divisi_id || !name || !role || !period) {
        return c.json(errorResponse("Field divisi_id, name, role, dan period wajib diisi"), 400);
    }

    const id = `png_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    await c.env.DB.prepare(
        "INSERT INTO pengurus (id, divisi_id, name, role, photo_url, period, order_priority) VALUES (?, ?, ?, ?, ?, ?, ?)"
    ).bind(id, divisi_id, name, role, photo_url || null, period, order_priority || 0).run();

    const created = await c.env.DB.prepare("SELECT * FROM pengurus WHERE id = ?").bind(id).first<Pengurus>();
    return c.json(successResponse(created, "Pengurus berhasil ditambahkan"), 201);
});

/**
 * DELETE /api/pengurus/member/:id (Protected - Admin)
 */
pengurusRouter.delete("/member/:id", authMiddleware, async (c) => {
    const id = c.req.param("id");
    await c.env.DB.prepare("DELETE FROM pengurus WHERE id = ?").bind(id).run();
    return c.json(successResponse(null, "Pengurus berhasil dihapus"));
});

export default pengurusRouter;
