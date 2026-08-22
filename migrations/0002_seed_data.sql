-- Seed Admin User (Default: admin / admin123)
-- SHA-256 hash for 'admin123'
INSERT OR IGNORE INTO users (id, username, password_hash, role) VALUES 
('usr_admin_01', 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin');

-- Seed Divisi
INSERT OR IGNORE INTO divisi (id, name, description, order_priority) VALUES
('div_bph', 'Badan Pengurus Harian (BPH)', 'Bertanggung jawab atas kepengurusan, koordinasi umum, dan kepemimpinan PMK Daniel.', 1),
('div_acara', 'Divisi Acara', 'Merancang, menyusun, dan memandu jalannya setiap persekutuan, ibadah, dan kegiatan PMK Daniel.', 2),
('div_medkom', 'Divisi Media & Komunikasi', 'Mengelola publikasi, dokumentasi, media sosial, dan platform digital PMK Daniel.', 3),
('div_doa', 'Divisi Doa & Pemerhati', 'Mendukung kehidupan rohani jemaat lewat doa syafaat dan pelayanan pastoral/pemerhati.', 4),
('div_musik', 'Divisi Musik & Pujian', 'Memimpin pujian dan penyembahan dalam setiap persekutuan jumat dan acara khusus.', 5);

-- Seed Pengurus
INSERT OR IGNORE INTO pengurus (id, divisi_id, name, role, photo_url, period, order_priority) VALUES
('png_01', 'div_bph', 'Bastian Nevan Baruch', 'Ketua PMK Daniel', '/images/bastian.webp', '2025/2026', 1),
('png_02', 'div_bph', 'Christo', 'Wakil Ketua', '/images/christo.webp', '2025/2026', 2),
('png_03', 'div_medkom', 'Joshua', 'Kepala Divisi Medkom', '/images/joshua.webp', '2025/2026', 3);

-- Seed Form Links
INSERT OR IGNORE INTO form_links (key, title, google_form_url, is_active) VALUES
('maba', 'Form Pendataan Mahasiswa Baru', 'https://forms.gle/maba-pmk-daniel', 1),
('alumni', 'Form Pendataan Alumni PMK Daniel', 'https://forms.gle/alumni-pmk-daniel', 1),
('kepanitiaan', 'Form Pendaftaran Kepanitiaan', 'https://forms.gle/kepanitiaan-pmk-daniel', 1);

-- Seed Pengumuman
INSERT OR IGNORE INTO pengumuman (id, title, slug, category, content, image_url, date_published, author) VALUES
('ann_01', 'Persekutuan Jumat Perdana Semester Ganjil', 'persekutuan-jumat-perdana-semester-ganjil', 'kegiatan', 'Syalom keluarga PMK Daniel! Mari bersama-sama hadir dalam Persekutuan Jumat Perdana dengan tema "Together to be Better". Diselenggarakan pada hari Jumat di Gedung F FILKOM UB.', '/images/persekutuan.webp', '2026-08-28', 'Divisi Acara'),
('ann_02', 'Open Recruitment Panitia Camp Daniel 2026', 'open-recruitment-panitia-camp-daniel-2026', 'oprec', 'Panggilan pelayanan bagi seluruh anggota aktif PMK Daniel angkatan 2024 dan 2025! Oprec panitia Camp Daniel kini telah dibuka untuk berbagai divisi.', '/images/campdaniel.webp', '2026-08-25', 'BPH PMK Daniel'),
('ann_03', 'Selamat Ulang Tahun Anggota PMK Daniel Bulan Agustus', 'selamat-ulang-tahun-anggota-pmk-daniel-bulan-agustus', 'ultah', 'Tuhan memberkati setiap langkah dan pertambahan usia bagi saudara-saudari kita yang berulang tahun di bulan Agustus ini. Tetap menjadi berkat dan terang!', '/images/joshua.webp', '2026-08-20', 'Divisi Pemerhati');
