import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { prettyJSON } from "hono/pretty-json";
import { Env } from "./types";
import { successResponse, errorResponse } from "./utils/response";

// Sub routers
import authRouter from "./routes/auth";
import pengumumanRouter from "./routes/pengumuman";
import pengurusRouter from "./routes/pengurus";
import formsRouter from "./routes/forms";
import uploadRouter from "./routes/upload";
import statsRouter from "./routes/stats";

const app = new Hono<{ Bindings: Env }>();

// Global Middlewares
app.use("*", logger());
app.use("*", prettyJSON());
app.use("*", cors({
    origin: (origin) => origin || "*",
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowHeaders: ["Content-Type", "Authorization"],
    exposeHeaders: ["Content-Length"],
    maxAge: 86400,
    credentials: true,
}));

// Root / Health Check
app.get("/", (c) => {
    return c.json(successResponse({
        service: "PMK Daniel API",
        version: "1.0.0",
        status: "healthy",
        timestamp: new Date().toISOString()
    }, "API PMK Daniel is running smoothly"));
});

// Mount Routes
app.route("/api/auth", authRouter);
app.route("/api/pengumuman", pengumumanRouter);
app.route("/api/pengurus", pengurusRouter);
app.route("/api/forms", formsRouter);
app.route("/api/upload", uploadRouter);
app.route("/api/stats", statsRouter);

// 404 Handler
app.notFound((c) => {
    return c.json(errorResponse("Endpoint tidak ditemukan", `Route ${c.req.path} not found`), 404);
});

// Error Handler
app.onError((err, c) => {
    console.error("Internal Server Error:", err);
    return c.json(errorResponse("Terjadi kesalahan internal server", err.message), 500);
});

export default app;
