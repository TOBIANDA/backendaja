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

        # 2. Seed Divisi & Struktur Sesuai Diagram Figma
        if db.query(models.Divisi).count() == 0:
            print("Seeding 12 divisi struktur organisasi PMK Daniel...")
            divisi_list = [
                models.Divisi(
                    id="ketua_umum",
                    name="Ketua Umum",
                    komisi="BPH",
                    icon_name="crown",
                    description="Bertanggung jawab penuh atas arah kepemimpinan, visi misi rohani, serta koordinasi seluruh badan pelayanan PMK Daniel FILKOM UB.",
                    group_photo_url="/images/bastian.webp",
                    order_priority=1
                ),
                models.Divisi(
                    id="sekretaris",
                    name="Sekretaris",
                    komisi="BPH",
                    icon_name="pen",
                    description="Mengelola tata kelola administrasi surat-menyurat, persuratan resmi, proposal, arsip notulensi, dan inventaris berkas PMK Daniel.",
                    group_photo_url="/images/persekutuan.webp",
                    order_priority=2
                ),
                models.Divisi(
                    id="wakil_ketua_umum",
                    name="Wakil Ketua Umum",
                    komisi="BPH",
                    icon_name="shield",
                    description="Mendampingi Ketua Umum dalam koordinasi internal komisi-komisi dan pengawasan jalannya program kerja persekutuan.",
                    group_photo_url="/images/christo.webp",
                    order_priority=3
                ),
                models.Divisi(
                    id="bendahara",
                    name="Bendahara",
                    komisi="BPH",
                    icon_name="wallet",
                    description="Mengatur perputaran sirkulasi keuangan, pembukuan kas persekutuan, transparansi anggaran, serta alokasi dana persepuluhan dan persembahan.",
                    group_photo_url="/images/persekutuan.webp",
                    order_priority=4
                ),
                models.Divisi(
                    id="pembinaan",
                    name="Pembinaan",
                    komisi="Komisi 1",
                    icon_name="book",
                    description="Merancang kurikulum pembinaan rohani mahasiswa Kristen FILKOM, kelompok kecil (KTB), pendalaman Alkitab, dan mentoring rohani.",
                    group_photo_url="/images/campdaniel.webp",
                    order_priority=5
                ),
                models.Divisi(
                    id="pemerhati",
                    name="Pemerhati",
                    komisi="Komisi 2",
                    icon_name="heart",
                    description="Melayani doa syafaat, kepedulian jemaat, sambutan mahasiswa baru, ucapan ulang tahun, serta konseling dan kunjungan kasih.",
                    group_photo_url="/images/persekutuan.webp",
                    order_priority=6
                ),
                models.Divisi(
                    id="acara",
                    name="Acara",
                    komisi="Komisi 3",
                    icon_name="sparkles",
                    description="Merancang konsep dan alur liturgi persekutuan mingguan, Welcoming Party, Retreat, Natal, Paskah, dan ibadah tematik.",
                    group_photo_url="/images/campdaniel.webp",
                    order_priority=7
                ),
                models.Divisi(
                    id="media_relasi",
                    name="Media & Relasi",
                    komisi="Komisi 4",
                    icon_name="video",
                    description="Pusat media kreatif publikasi, dokumentasi, siaran visual, serta membangun kemitraan relasi eksternal dengan lembaga Kristen.",
                    group_photo_url="/images/joshua.webp",
                    order_priority=8
                ),
                models.Divisi(
                    id="teknis_inventaris",
                    name="Teknis & Inventaris",
                    komisi="Sub Komisi 3 (Acara)",
                    icon_name="settings",
                    description="Mengelola sarana perlengkapan sound system, instrumen musik, proyektor, logistik ruangan, dan tata letak teknis persekutuan.",
                    group_photo_url="/images/persekutuan.webp",
                    order_priority=9
                ),
                models.Divisi(
                    id="acara_sub",
                    name="Acara",
                    komisi="Sub Komisi 3 (Acara)",
                    icon_name="calendar",
                    description="Pelaksana teknis jalannya rundown persekutuan, koordinasi worship leader, singer, dan pembicara hamba Tuhan.",
                    group_photo_url="/images/campdaniel.webp",
                    order_priority=10
                ),
                models.Divisi(
                    id="minat_bakat",
                    name="Minat Bakat & Misi Pelayanan",
                    komisi="Sub Komisi 3 (Acara)",
                    icon_name="music",
                    description="Wadah pengembangan talenta musik, vokal, tari/drama, serta pengutusan misi sosial pelayanan kasih ke panti asuhan.",
                    group_photo_url="/images/persekutuan.webp",
                    order_priority=11
                ),
                models.Divisi(
                    id="media",
                    name="Media",
                    komisi="Sub Komisi 4 (Medrel)",
                    icon_name="camera",
                    description="Bertanggung jawab atas fotografi, videografi recap, desain feed Instagram, live streaming, dan maintenance website.",
                    group_photo_url="/images/joshua.webp",
                    order_priority=12
                ),
                models.Divisi(
                    id="relasi",
                    name="Relasi",
                    komisi="Sub Komisi 4 (Medrel)",
                    icon_name="users",
                    description="Menjalin hubungan persaudaraan dengan PMK fakultas lain di UB, gereja lokal, alumni PMK Daniel, dan lembaga pelayanan kampus.",
                    group_photo_url="/images/persekutuan.webp",
                    order_priority=13
                ),
            ]
            db.add_all(divisi_list)
            db.commit()

        # 3. Seed Pengurus / Anggota Divisi
        if db.query(models.Pengurus).count() == 0:
            print("Seeding data anggota pengurus...")
            pengurus_list = [
                # BPH
                models.Pengurus(id="png_01", divisi_id="ketua_umum", name="Bastian Nevan Baruch", role="Ketua Umum", photo_url="/images/bastian.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_02", divisi_id="wakil_ketua_umum", name="Christo Emmanuel", role="Wakil Ketua Umum", photo_url="/images/christo.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_03", divisi_id="sekretaris", name="Gracia Stephanie", role="Sekretaris 1", photo_url="/images/persekutuan.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_04", divisi_id="sekretaris", name="Patricia Putri", role="Sekretaris 2", photo_url="/images/persekutuan.webp", period="2025/2026", order_priority=2),
                models.Pengurus(id="png_05", divisi_id="bendahara", name="Nathania Michelle", role="Bendahara 1", photo_url="/images/persekutuan.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_06", divisi_id="bendahara", name="Samuel Timothy", role="Bendahara 2", photo_url="/images/persekutuan.webp", period="2025/2026", order_priority=2),

                # Pembinaan
                models.Pengurus(id="png_07", divisi_id="pembinaan", name="Jonathan Kevin", role="Ketua Pembinaan", photo_url="/images/campdaniel.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_08", divisi_id="pembinaan", name="Debora Angeline", role="Wakil Ketua Pembinaan", photo_url="/images/campdaniel.webp", period="2025/2026", order_priority=2),
                models.Pengurus(id="png_09", divisi_id="pembinaan", name="Daniel Ezra", role="Anggota Pembinaan", photo_url="/images/campdaniel.webp", period="2025/2026", order_priority=3),
                models.Pengurus(id="png_10", divisi_id="pembinaan", name="Ruth Valerie", role="Anggota Pembinaan", photo_url="/images/campdaniel.webp", period="2025/2026", order_priority=4),

                # Pemerhati
                models.Pengurus(id="png_11", divisi_id="pemerhati", name="Joshua Alexander", role="Ketua Pemerhati", photo_url="/images/joshua.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_12", divisi_id="pemerhati", name="Ester Naomi", role="Wakil Ketua Pemerhati", photo_url="/images/persekutuan.webp", period="2025/2026", order_priority=2),
                models.Pengurus(id="png_13", divisi_id="pemerhati", name="Grace Febiola", role="Anggota Pemerhati", photo_url="/images/persekutuan.webp", period="2025/2026", order_priority=3),

                # Acara
                models.Pengurus(id="png_14", divisi_id="acara", name="Timothy Aaron", role="Koordinator Komisi Acara", photo_url="/images/campdaniel.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_15", divisi_id="acara", name="Rachel Jovita", role="Wakil Koordinator Acara", photo_url="/images/campdaniel.webp", period="2025/2026", order_priority=2),

                # Media & Relasi
                models.Pengurus(id="png_16", divisi_id="media_relasi", name="Dave Christian", role="Koordinator Komisi Medrel", photo_url="/images/joshua.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_17", divisi_id="media_relasi", name="Hanna Pricilla", role="Wakil Koordinator Medrel", photo_url="/images/persekutuan.webp", period="2025/2026", order_priority=2),

                # Sub-Divisi
                models.Pengurus(id="png_18", divisi_id="teknis_inventaris", name="Michael Ryan", role="Ketua Divisi Teknis", photo_url="/images/persekutuan.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_19", divisi_id="acara_sub", name="Sarah Clarissa", role="Ketua Divisi Acara Pelaksana", photo_url="/images/campdaniel.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_20", divisi_id="minat_bakat", name="David Christian", role="Ketua Divisi Minat Bakat", photo_url="/images/persekutuan.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_21", divisi_id="media", name="Jeremy Matthew", role="Ketua Divisi Media Visual", photo_url="/images/joshua.webp", period="2025/2026", order_priority=1),
                models.Pengurus(id="png_22", divisi_id="relasi", name="Rebeca Amanda", role="Ketua Divisi Relasi Eksternal", photo_url="/images/persekutuan.webp", period="2025/2026", order_priority=1),
            ]
            db.add_all(pengurus_list)
            db.commit()

        # 4. Seed Form Links
        if db.query(models.FormLink).count() == 0:
            print("Seeding form links...")
            form_links = [
                models.FormLink(key="maba", title="Form Pendataan Mahasiswa Baru", google_form_url="https://forms.gle/maba-pmk-daniel", is_active=1),
                models.FormLink(key="alumni", title="Form Pendataan Alumni PMK Daniel", google_form_url="https://forms.gle/alumni-pmk-daniel", is_active=1),
                models.FormLink(key="kepanitiaan", title="Form Pendaftaran Kepanitiaan", google_form_url="https://forms.gle/kepanitiaan-pmk-daniel", is_active=1),
            ]
            db.add_all(form_links)
            db.commit()

        print("Database initialization and seed complete!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db_and_seed()
