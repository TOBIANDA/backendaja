# Backend API PMK Daniel FILKOM UB (Python FastAPI) 🐍⚡

Backend REST API untuk website resmi **PMK Daniel FILKOM Universitas Brawijaya**. Dibangun menggunakan **Python**, framework **FastAPI**, ORM **SQLAlchemy (SQLite / D1)**, dan integrasi penyimpanan media **Cloudflare R2**.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Framework:** FastAPI
* **Server:** Uvicorn (ASGI)
* **ORM & Database:** SQLAlchemy + SQLite (kompatibel Cloudflare D1)
* **Storage:** Cloudflare R2 (via Boto3 S3 Client) dengan fallback lokal
* **Authentication:** JWT (PyJWT) + SHA-256 Hashing
* **API Documentation:** Interactive Swagger UI (`/docs`) & ReDoc (`/redoc`)

---

## 🚀 Menjalankan Secara Lokal (Development)

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Inisialisasi Database & Data Awal (Seed Data):**
   ```bash
   python seed.py
   ```
   *(Secara otomatis membuat database `pmkdaniel.db` dan mengisi data awal pengumuman, divisi, pengurus, serta akun admin).*

3. **Jalankan Server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   * Server API aktif di: **`http://localhost:8000`**
   * **Dokumentasi Interaktif (Swagger UI):** **`http://localhost:8000/docs`**

---

## 🔑 Kredensial Admin Default

* **Username:** `admin`
* **Password:** `admin123`

---

## 📡 Daftar Endpoint API

### 1. Public Endpoints
* `GET /` — Health check & status API.
* `GET /docs` — Swagger UI interaktif untuk mencoba semua API langsung di browser.
* `GET /api/pengumuman` — Daftar pengumuman (support `?kategori=kegiatan|oprec|ultah`, `?search=...`, `?page=1&limit=10`).
* `GET /api/pengumuman/{id_or_slug}` — Detail pengumuman (otomatis menambah jumlah *views*).
* `GET /api/pengurus` — Struktur divisi dan anggota pengurus.
* `GET /api/forms` — Link Google Form aktif (Maba, Alumni, Kepanitiaan).

### 2. Autentikasi
* `POST /api/auth/login` — Login admin (`username`, `password`) -> mengembalikan JWT token.
* `GET /api/auth/me` — Cek status & validitas token admin.
* `PUT /api/auth/change-password` — Ganti password admin (*Protected*).

### 3. Admin Protected Endpoints (Header: `Authorization: Bearer <token>`)
* `GET /api/stats` — Ringkasan total data dashboard admin.
* `POST /api/pengumuman` — Buat pengumuman baru.
* `PUT /api/pengumuman/{id}` — Update pengumuman.
* `DELETE /api/pengumuman/{id}` — Hapus pengumuman.
* `POST /api/upload` — Upload gambar (JPEG, PNG, WebP) ke Cloudflare R2 / lokal.
* `POST /api/pengurus/divisi` — Tambah divisi.
* `POST /api/pengurus/member` — Tambah pengurus.
* `DELETE /api/pengurus/member/{id}` — Hapus pengurus.
* `PUT /api/forms/{key}` — Update URL Google Form.

---

## ☁️ Integrasi Cloudflare R2 Storage (Production)

Isi kredensial Cloudflare R2 Anda di file `.env`:
```env
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=pmkdaniel-media
R2_PUBLIC_DOMAIN=https://pub-pmkdaniel.r2.dev
```
Jika variabel R2 tidak diisi, file yang diunggah akan otomatis tersimpan di folder lokal `./uploads` dan dapat diakses publik di `/uploads/{filename}`.
