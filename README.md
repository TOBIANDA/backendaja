# Backend API PMK Daniel FILKOM UB ⚡

Backend REST API untuk website resmi PMK Daniel FILKOM Universitas Brawijaya. Dibangun di atas arsitektur serverless **Cloudflare Workers**, framework **Hono.js**, database **Cloudflare D1 (SQLite)**, dan media storage **Cloudflare R2**.

---

## 🛠️ Tech Stack

* **Runtime:** Cloudflare Workers (Edge Serverless)
* **Framework:** Hono.js (TypeScript)
* **Database:** Cloudflare D1 (SQL / SQLite)
* **Object Storage:** Cloudflare R2 (S3-compatible)
* **Authentication:** JWT + Web Crypto SHA-256

---

## 🚀 Menjalankan Secara Lokal (Development)

1. **Install Dependencies:**
   ```bash
   npm install
   ```

2. **Jalankan Migrasi & Data Awal (D1 Lokal):**
   ```bash
   npm run migrate:local
   npm run seed:local
   ```

3. **Jalankan Server Development:**
   ```bash
   npm run dev
   ```
   *Server akan aktif di: `http://localhost:8787`*

---

## 📡 Daftar Endpoint API

### 1. Public Endpoints
* `GET /` — Health check & status API.
* `GET /api/pengumuman` — Daftar pengumuman (mendukung `?kategori=kegiatan|oprec|ultah`, `?search=...`, `?page=1&limit=10`).
* `GET /api/pengumuman/:idOrSlug` — Detail pengumuman berdasarkan ID atau slug.
* `GET /api/pengurus` — Struktur divisi dan profil anggota pengurus.
* `GET /api/forms` — Link Google Form aktif (Maba, Alumni, Kepanitiaan).

### 2. Authentication
* `POST /api/auth/login` — Login admin (`username`, `password`) -> mengembalikan JWT token.
  * *Default Akun:* `admin` / `admin123`
* `GET /api/auth/me` — Cek status & validitas token admin.
* `PUT /api/auth/change-password` — Ganti password admin (*Protected*).

### 3. Admin Protected Endpoints (Memerlukan header `Authorization: Bearer <token>`)
* `GET /api/stats` — Statistik ringkas dashboard (total pengumuman, views, pengurus, divisi).
* `POST /api/pengumuman` — Buat postingan pengumuman baru.
* `PUT /api/pengumuman/:id` — Update pengumuman.
* `DELETE /api/pengumuman/:id` — Hapus pengumuman.
* `POST /api/upload` — Upload gambar ke bucket Cloudflare R2 (multipart form-data).
* `POST /api/pengurus/divisi` — Tambah divisi.
* `POST /api/pengurus/member` — Tambah anggota pengurus.
* `DELETE /api/pengurus/member/:id` — Hapus anggota pengurus.
* `PUT /api/forms/:key` — Update URL Google Form (`maba`, `alumni`, `kepanitiaan`).

---

## ☁️ Panduan Deploy ke Cloudflare (Production)

1. **Login ke Akun Cloudflare:**
   ```bash
   npx wrangler login
   ```

2. **Buat Database D1 di Cloudflare:**
   ```bash
   npx wrangler d1 create pmk-db
   ```
   *(Salin `database_id` yang dihasilkan ke dalam `wrangler.jsonc`).*

3. **Buat Bucket R2 di Cloudflare:**
   ```bash
   npx wrangler r2 bucket create pmkdaniel-media
   ```

4. **Jalankan Migrasi Database ke Cloudflare D1:**
   ```bash
   npm run migrate:remote
   npm run seed:remote
   ```

5. **Deploy Worker API:**
   ```bash
   npm run deploy
   ```
