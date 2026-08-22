import { Hono } from "hono";
import { sign } from "hono/jwt";
import { Env, User } from "../types";
import { hashPassword, verifyPassword } from "../utils/password";
import { successResponse, errorResponse } from "../utils/response";
import { authMiddleware } from "../middleware/auth";

const authRouter = new Hono<{ Bindings: Env }>();

/**
 * POST /api/auth/login
 */
authRouter.post("/login", async (c) => {
    const { username, password } = await c.req.json<{ username?: string; password?: string }>();

    if (!username || !password) {
        return c.json(errorResponse("Username dan password wajib diisi"), 400);
    }

    const user = await c.env.DB.prepare(
        "SELECT * FROM users WHERE username = ?"
    ).bind(username).first<User>();

    if (!user) {
        return c.json(errorResponse("Kredensial tidak valid", "Username atau password salah"), 401);
    }

    const isValid = await verifyPassword(password, user.password_hash);
    if (!isValid) {
        return c.json(errorResponse("Kredensial tidak valid", "Username atau password salah"), 401);
    }

    const secret = c.env.JWT_SECRET || "pmk_daniel_super_secret_jwt_key_2026";
    const token = await sign(
        {
            id: user.id,
            username: user.username,
            role: user.role,
            exp: Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 7 // 7 hari
        },
        secret
    );

    return c.json(successResponse({
        token,
        user: {
            id: user.id,
            username: user.username,
            role: user.role
        }
    }, "Login berhasil"));
});

/**
 * GET /api/auth/me (Protected)
 */
authRouter.get("/me", authMiddleware, async (c) => {
    const userPayload = c.get("user" as any);
    return c.json(successResponse(userPayload, "Token valid"));
});

/**
 * PUT /api/auth/change-password (Protected)
 */
authRouter.put("/change-password", authMiddleware, async (c) => {
    const userPayload = c.get("user" as any);
    const { oldPassword, newPassword } = await c.req.json<{ oldPassword?: string; newPassword?: string }>();

    if (!oldPassword || !newPassword || newPassword.length < 6) {
        return c.json(errorResponse("Password baru minimal 6 karakter"), 400);
    }

    const user = await c.env.DB.prepare(
        "SELECT * FROM users WHERE id = ?"
    ).bind(userPayload.id).first<User>();

    if (!user) {
        return c.json(errorResponse("User tidak ditemukan"), 404);
    }

    const isValid = await verifyPassword(oldPassword, user.password_hash);
    if (!isValid) {
        return c.json(errorResponse("Password lama tidak sesuai"), 400);
    }

    const newHash = await hashPassword(newPassword);
    await c.env.DB.prepare(
        "UPDATE users SET password_hash = ? WHERE id = ?"
    ).bind(newHash, user.id).run();

    return c.json(successResponse(null, "Password berhasil diperbarui"));
});

export default authRouter;
