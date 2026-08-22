import { Hono } from "hono";
import { Env } from "../types";
import { successResponse, errorResponse } from "../utils/response";
import { authMiddleware } from "../middleware/auth";

const uploadRouter = new Hono<{ Bindings: Env }>();

/**
 * POST /api/upload (Protected - Admin)
 * Multipart form data upload to Cloudflare R2
 */
uploadRouter.post("/", authMiddleware, async (c) => {
    try {
        const body = await c.req.parseBody();
        const file = body["file"];

        if (!file || !(file instanceof File)) {
            return c.json(errorResponse("File tidak ditemukan atau format tidak valid"), 400);
        }

        // Validate image mime types
        const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/gif", "image/svg+xml"];
        if (!allowedTypes.includes(file.type)) {
            return c.json(errorResponse("Hanya file gambar (JPEG, PNG, WebP, GIF, SVG) yang diperbolehkan"), 400);
        }

        // 5MB max size
        if (file.size > 5 * 1024 * 1024) {
            return c.json(errorResponse("Ukuran file maksimal 5MB"), 400);
        }

        const extension = file.name.split(".").pop() || "webp";
        const uniqueFileName = `pmk_${Date.now()}_${Math.random().toString(36).substring(2, 8)}.${extension}`;

        const arrayBuffer = await file.arrayBuffer();

        await c.env.STORAGE.put(uniqueFileName, arrayBuffer, {
            httpMetadata: {
                contentType: file.type
            }
        });

        const publicUrl = c.env.PUBLIC_R2_URL
            ? `${c.env.PUBLIC_R2_URL.replace(/\/$/, "")}/${uniqueFileName}`
            : `/api/media/${uniqueFileName}`;

        return c.json(successResponse({
            fileName: uniqueFileName,
            url: publicUrl,
            size: file.size,
            type: file.type
        }, "Upload berhasil"), 201);
    } catch (err: any) {
        return c.json(errorResponse("Gagal mengunggah file", err.message), 500);
    }
});

export default uploadRouter;
