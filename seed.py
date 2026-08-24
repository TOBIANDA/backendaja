from database import engine, SessionLocal, Base
import models
from utils.auth import hash_password

def init_db_and_seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Admin User
        admin_user = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin_user:
            print("Seeding admin user...")
            admin = models.User(
                id="usr_admin_01",
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin"
            )
            db.add(admin)

        # 2. Seed Divisi
        if db.query(models.Divisi).count() == 0:
            print("Seeding divisi...")
            divisi_list = [
                models.Divisi(id="div_bph", name="Badan Pengurus Harian (BPH)", description="Bertanggung jawab atas kepengurusan, koordinasi umum, dan kepemimpinan PMK Daniel.", order_priority=1),
                models.Divisi(id="div_acara", name="Divisi Acara", description="Merancang, menyusun, dan memandu jalannya setiap persekutuan, ibadah, dan kegiatan PMK Daniel.", order_priority=2),
                models.Divisi(id="div_medkom", name="Divisi Media & Komunikasi", description="Mengelola publikasi, dokumentasi, media sosial, dan platform digital PMK Daniel.", order_priority=3),
                models.Divisi(id="div_doa", name="Divisi Doa & Pemerhati", description="Mendukung kehidupan rohani jemaat lewat doa syafaat dan pelayanan pastoral/pemerhati.", order_priority=4),
                models.Divisi(id="div_musik", name="Divisi Musik & Pujian", description="Memimpin pujian dan penyembahan dalam setiap persekutuan jumat dan acara khusus.", order_priority=5),
            ]
            db.add_all(divisi_list)

        # 3. Seed Pengurus
        if db.query(models.Pengurus).count() == 0:
            print("Seeding pengurus...")
            pengurus_list = [
                models.Pengurus(id="png_01", divisi_id="div_bph", name="Bastian Nevan Baruch", role="Ketua PMK Daniel", photo_url="/images/bastian.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_02", divisi_id="div_bph", name="Christo", role="Wakil Ketua", photo_url="/images/christo.webp", period="2025/2026", order_priority=2),
                models.Pengurus(id="png_03", divisi_id="div_medkom", name="Joshua", role="Kepala Divisi Medkom", photo_url="/images/joshua.webp", period="2025/2026", order_priority=3),
            ]
            db.add_all(pengurus_list)

        # 4. Seed Form Links
        if db.query(models.FormLink).count() == 0:
            print("Seeding form links...")
            form_links = [
                models.FormLink(key="maba", title="Form Pendataan Mahasiswa Baru", google_form_url="https://forms.gle/maba-pmk-daniel", is_active=1),
                models.FormLink(key="alumni", title="Form Pendataan Alumni PMK Daniel", google_form_url="https://forms.gle/alumni-pmk-daniel", is_active=1),
                models.FormLink(key="kepanitiaan", title="Form Pendaftaran Kepanitiaan", google_form_url="https://forms.gle/kepanitiaan-pmk-daniel", is_active=1),
            ]
            db.add_all(form_links)

        # 5. Seed Pengumuman
        if db.query(models.Pengumuman).count() == 0:
            print("Seeding pengumuman...")
            pengumuman_list = [
                models.Pengumuman(
                    id="ann_01",
                    title="Persekutuan Jumat Perdana Semester Ganjil",
                    slug="persekutuan-jumat-perdana-semester-ganjil",
                    category="kegiatan",
                    content="Syalom keluarga PMK Daniel! Mari bersama-sama hadir dalam Persekutuan Jumat Perdana dengan tema 'Together to be Better'. Diselenggarakan pada hari Jumat di Gedung F FILKOM UB.",
                    image_url="/images/persekutuan.webp",
                    date_published="2026-08-28",
                    author="Divisi Acara"
                ),
                models.Pengumuman(
                    id="ann_02",
                    title="Open Recruitment Panitia Camp Daniel 2026",
                    slug="open-recruitment-panitia-camp-daniel-2026",
                    category="oprec",
                    content="Panggilan pelayanan bagi seluruh anggota aktif PMK Daniel angkatan 2024 dan 2025! Oprec panitia Camp Daniel kini telah dibuka untuk berbagai divisi.",
                    image_url="/images/campdaniel.webp",
                    date_published="2026-08-25",
                    author="BPH PMK Daniel"
                ),
                models.Pengumuman(
                    id="ann_03",
                    title="Selamat Ulang Tahun Anggota PMK Daniel Bulan Agustus",
                    slug="selamat-ulang-tahun-anggota-pmk-daniel-bulan-agustus",
                    category="ultah",
                    content="Tuhan memberkati setiap langkah dan pertambahan usia bagi saudara-saudari kita yang berulang tahun di bulan Agustus ini. Tetap menjadi berkat dan terang!",
                    image_url="/images/joshua.webp",
                    date_published="2026-08-20",
                    author="Divisi Pemerhati"
                )
            ]
        # 6. Seed Sample Dynamic Form
        if db.query(models.DynamicForm).count() == 0:
            print("Seeding sample dynamic form...")
            import json
            sample_fields = [
                {
                    "id": "nama_lengkap",
                    "label": "Nama Lengkap",
                    "type": "text",
                    "placeholder": "Contoh: Daniel Bastian",
                    "required": True,
                    "helpText": "Nama lengkap sesuai KTM/KTP"
                },
                {
                    "id": "nim",
                    "label": "NIM (Nomor Induk Mahasiswa)",
                    "type": "text",
                    "placeholder": "Contoh: 245150200111000",
                    "required": True
                },
                {
                    "id": "program_studi",
                    "label": "Program Studi / Jurusan",
                    "type": "select",
                    "required": True,
                    "options": [
                        "Teknik Informatika",
                        "Sistem Informasi",
                        "Teknologi Informasi",
                        "Teknik Komputer",
                        "Pendidikan Teknologi Informasi"
                    ]
                },
                {
                    "id": "no_whatsapp",
                    "label": "Nomor WhatsApp Aktif",
                    "type": "text",
                    "placeholder": "Contoh: 081234567890",
                    "required": True
                },
                {
                    "id": "pilihan_divisi",
                    "label": "Minat Pelayanan Utama (Pilih 1)",
                    "type": "radio",
                    "required": True,
                    "options": [
                        "Divisi Acara",
                        "Divisi Musik & Pujian",
                        "Divisi Media & Komunikasi",
                        "Divisi Doa & Pemerhati"
                    ]
                },
                {
                    "id": "talenta_minat",
                    "label": "Talenta & Keahlian Tambahan (Boleh lebih dari 1)",
                    "type": "checkbox",
                    "required": False,
                    "options": [
                        "Main Musik (Gitar / Keyboard / Drum / Bass)",
                        "Vocal / Singer / WL",
                        "Desain Grafis / Canva / Figma",
                        "Fotografi / Videografi",
                        "Public Speaking / MC",
                        "IT / Web / Coding"
                    ]
                },
                {
                    "id": "alasan_motivasi",
                    "label": "Ceritakan Motivasi / Harapan Anda di PMK Daniel",
                    "type": "textarea",
                    "placeholder": "Tuliskan harapan dan kerinduan Anda dalam bersekutu di PMK Daniel...",
                    "required": True
                },
                {
                    "id": "foto_ktm",
                    "label": "Upload Foto Diri / KTM / Bukti Penerimaan",
                    "type": "file",
                    "required": False,
                    "helpText": "Format diperbolehkan: JPG, PNG, PDF (Maksimal 10MB)"
                }
            ]

            sample_form = models.DynamicForm(
                id="form_maba_2026",
                title="Form Pendataan Mahasiswa Baru PMK Daniel 2026",
                slug="pendataan-maba-2026",
                description="Syalom saudara/i terkasih! Selamat datang di FILKOM UB. Formulir ini digunakan untuk pendataan anggota baru dan pemetaan minat pelayanan di keluarga PMK Daniel.",
                fields_schema=json.dumps(sample_fields, ensure_ascii=False),
                is_active=1
            )
            db.add(sample_form)

        db.commit()
        print("Database initialization and seed complete!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db_and_seed()
