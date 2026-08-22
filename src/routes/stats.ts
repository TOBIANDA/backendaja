import { Hono } from "hono";
import { Env } from "../types";
import { successResponse } from "../utils/response";
import { authMiddleware } from "../middleware/auth";

const statsRouter = new Hono<{ Bindings: Env }>();

/**
 * GET /api/stats (Protected - Admin)
 */
statsRouter.get("/", authMiddleware, async (c) => {
    const totalPengumuman = await c.env.DB.prepare(
        "SELECT COUNT(*) as count FROM pengumuman"
    ).first<{ count: number }>();

    const totalViews = await c.env.DB.prepare(
        "SELECT SUM(views) as count FROM pengumuman"
    ).first<{ count: number }>();

    const totalPengurus = await c.env.DB.prepare(
        "SELECT COUNT(*) as count FROM pengurus"
    ).first<{ count: number }>();

    const totalDivisi = await c.env.DB.prepare(
        "SELECT COUNT(*) as count FROM divisi"
    ).first<{ count: number }>();

    const latestPengumuman = await c.env.DB.prepare(
        "SELECT id, title, category, date_published, views FROM pengumuman ORDER BY created_at DESC LIMIT 5"
    ).all();

    return c.json(successResponse({
        totalPengumuman: totalPengumuman?.count || 0,
        totalViews: totalViews?.count || 0,
        totalPengurus: totalPengurus?.count || 0,
        totalDivisi: totalDivisi?.count || 0,
        latestPengumuman: latestPengumuman?.results || []
    }));
});

export default statsRouter;
