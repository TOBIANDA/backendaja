import { Hono } from "hono";
import { Env, Pengumuman } from "../types";
import { successResponse, errorResponse } from "../utils/response";
import { authMiddleware } from "../middleware/auth";

const pengumumanRouter = new Hono<{ Bindings: Env }>();

/**
 * Helper to generate URL-friendly slug
 */
function slugify(text: string): string {
    return text
        .toString()
        .toLowerCase()
        .trim()
        .replace(/\s+/g, "-")
        .replace(/[^\w\-]+/g, "")
        .replace(/\-\-+/g, "-");
}

/**
 * GET /api/pengumuman (Public)
 * Support query: ?kategori=kegiatan|oprec|ultah&search=...&limit=10&page=1
 */
pengumumanRouter.get("/", async (c) => {
    const kategori = c.req.query("kategori");
    const search = c.req.query("search");
    const limit = parseInt(c.req.query("limit") || "10", 10);
    const page = parseInt(c.req.query("page") || "1", 10);
    const offset = (page - 1) * limit;

    let query = "SELECT * FROM pengumuman WHERE 1=1";
    const params: any[] = [];

    if (kategori && kategori !== "all") {
        query += " AND category = ?";
        params.push(kategori);
    }

    if (search) {
        query += " AND (title LIKE ? OR content LIKE ?)";
        params.push(`%${search}%`, `%${search}%`);
    }

    query += " ORDER BY date_published DESC, created_at DESC LIMIT ? OFFSET ?";
    params.push(limit, offset);

    const { results } = await c.env.DB.prepare(query).bind(...params).all<Pengumuman>();

    // Count total for pagination
    let countQuery = "SELECT COUNT(*) as total FROM pengumuman WHERE 1=1";
    const countParams: any[] = [];
    if (kategori && kategori !== "all") {
        countQuery += " AND category = ?";
        countParams.push(kategori);
    }
    if (search) {
        countQuery += " AND (title LIKE ? OR content LIKE ?)";
        countParams.push(`%${search}%`, `%${search}%`);
    }
    const countResult = await c.env.DB.prepare(countQuery).bind(...countParams).first<{ total: number }>();
    const total = countResult?.total || 0;

    return c.json(successResponse({
        items: results || [],
        pagination: {
            page,
            limit,
            total,
            totalPages: Math.ceil(total / limit)
        }
    }));
});

/**
 * GET /api/pengumuman/:idOrSlug (Public)
 */
pengumumanRouter.get("/:idOrSlug", async (c) => {
    const idOrSlug = c.req.param("idOrSlug");

    const item = await c.env.DB.prepare(
        "SELECT * FROM pengumuman WHERE id = ? OR slug = ?"
    ).bind(idOrSlug, idOrSlug).first<Pengumuman>();

    if (!item) {
        return c.json(errorResponse("Pengumuman tidak ditemukan"), 404);
    }

    // Increment views asynchronously
    c.executionCtx.waitUntil(
        c.env.DB.prepare("UPDATE pengumuman SET views = views + 1 WHERE id = ?").bind(item.id).run()
    );

    return c.json(successResponse(item));
});

/**
 * POST /api/pengumuman (Protected - Admin)
 */
pengumumanRouter.post("/", authMiddleware, async (c) => {
    const body = await c.req.json<{
        title?: string;
        category?: 'kegiatan' | 'oprec' | 'ultah' | 'lainnya';
        content?: string;
        image_url?: string;
        date_published?: string;
        author?: string;
    }>();

    if (!body.title || !body.category || !body.content || !body.date_published) {
        return c.json(errorResponse("Field title, category, content, dan date_published wajib diisi"), 400);
    }

    const id = `ann_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    const baseSlug = slugify(body.title);
    const slug = `${baseSlug}-${Math.random().toString(36).substring(2, 6)}`;
    const author = body.author || "Pengurus PMK";
    const imageUrl = body.image_url || null;

    await c.env.DB.prepare(
        `INSERT INTO pengumuman (id, title, slug, category, content, image_url, date_published, author)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(id, body.title, slug, body.category, body.content, imageUrl, body.date_published, author).run();

    const created = await c.env.DB.prepare("SELECT * FROM pengumuman WHERE id = ?").bind(id).first<Pengumuman>();
    return c.json(successResponse(created, "Pengumuman berhasil ditambahkan"), 201);
});

/**
 * PUT /api/pengumuman/:id (Protected - Admin)
 */
pengumumanRouter.put("/:id", authMiddleware, async (c) => {
    const id = c.req.param("id");
    const body = await c.req.json<{
        title?: string;
        category?: 'kegiatan' | 'oprec' | 'ultah' | 'lainnya';
        content?: string;
        image_url?: string;
        date_published?: string;
        author?: string;
    }>();

    const existing = await c.env.DB.prepare("SELECT * FROM pengumuman WHERE id = ?").bind(id).first<Pengumuman>();
    if (!existing) {
        return c.json(errorResponse("Pengumuman tidak ditemukan"), 404);
    }

    const title = body.title ?? existing.title;
    const category = body.category ?? existing.category;
    const content = body.content ?? existing.content;
    const imageUrl = body.image_url !== undefined ? body.image_url : existing.image_url;
    const datePublished = body.date_published ?? existing.date_published;
    const author = body.author ?? existing.author;

    await c.env.DB.prepare(
        `UPDATE pengumuman 
         SET title = ?, category = ?, content = ?, image_url = ?, date_published = ?, author = ?, updated_at = CURRENT_TIMESTAMP
         WHERE id = ?`
    ).bind(title, category, content, imageUrl, datePublished, author, id).run();

    const updated = await c.env.DB.prepare("SELECT * FROM pengumuman WHERE id = ?").bind(id).first<Pengumuman>();
    return c.json(successResponse(updated, "Pengumuman berhasil diperbarui"));
});

/**
 * DELETE /api/pengumuman/:id (Protected - Admin)
 */
pengumumanRouter.delete("/:id", authMiddleware, async (c) => {
    const id = c.req.param("id");

    const existing = await c.env.DB.prepare("SELECT * FROM pengumuman WHERE id = ?").bind(id).first<Pengumuman>();
    if (!existing) {
        return c.json(errorResponse("Pengumuman tidak ditemukan"), 404);
    }

    await c.env.DB.prepare("DELETE FROM pengumuman WHERE id = ?").bind(id).run();
    return c.json(successResponse(null, "Pengumuman berhasil dihapus"));
});

export default pengumumanRouter;
