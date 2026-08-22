-- 1. Tabel Admin Users
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'admin',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabel Pengumuman
CREATE TABLE IF NOT EXISTS pengumuman (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('kegiatan', 'oprec', 'ultah', 'lainnya')),
    content TEXT NOT NULL,
    image_url TEXT,
    date_published DATE NOT NULL,
    author TEXT DEFAULT 'Pengurus PMK',
    views INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabel Divisi
CREATE TABLE IF NOT EXISTS divisi (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    order_priority INTEGER DEFAULT 0
);

-- 4. Tabel Pengurus
CREATE TABLE IF NOT EXISTS pengurus (
    id TEXT PRIMARY KEY,
    divisi_id TEXT REFERENCES divisi(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    photo_url TEXT,
    period TEXT NOT NULL,
    order_priority INTEGER DEFAULT 0
);

-- 5. Tabel Link Form Dinamis
CREATE TABLE IF NOT EXISTS form_links (
    key TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    google_form_url TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
