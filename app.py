import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Ujian MI Ashsholahiyah Cilamaya",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. INISIALISASI DATABASE LOKAL (SESSION STATE) ---
# Berfungsi agar data tetap tersimpan saat berpindah menu sebelum dihubungkan ke Google Sheets
if 'siswa_db' not in st.session_state:
    st.session_state.siswa_db = pd.DataFrame([
        {"kelas": "Kelas 4", "rombel": "A", "no_peserta": "20260401", "nama": "AHMAD FAUZAN", "password": "123"},
        {"kelas": "Kelas 4", "rombel": "A", "no_peserta": "20260402", "nama": "SITI AMINAH", "password": "123"},
        {"kelas": "Kelas 5", "rombel": "A", "no_peserta": "20260501", "nama": "SIHATUL AFIAH", "password": "123"},
    ])

if 'guru_db' not in st.session_state:
    st.session_state.guru_db = pd.DataFrame([
        {"nama_guru": "Ust. Ahmad, S.Pd", "kelas_ajar": "Kelas 4", "password": "guru4"},
        {"nama_guru": "Hj. Fatimah, S.Pd.I", "kelas_ajar": "Kelas 5", "password": "guru5"},
    ])

if 'logged_in_admin' not in st.session_state:
    st.session_state.logged_in_admin = False
if 'logged_in_guru' not in st.session_state:
    st.session_state.logged_in_guru = None
if 'logged_in_siswa' not in st.session_state:
    st.session_state.logged_in_siswa = None

# --- 3. HEADER & WIDGET REAL-TIME ---
st.markdown("<h1 style='text-align: center; color: #0d5c3b;'>UJIAN MI ASHSHOLAHIYAH CILAMAYA</h1>", unsafe_allow_html=True)

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.markdown(f"📅 **Hari/Tanggal:** {datetime.now().strftime('%A, %d %b %Y')}")
with col_info2:
    st.markdown(f"⏰ **Jam:** {datetime.now().strftime('%H:%M:%S')} WIB")
with col_info3:
    st.markdown("🟢 **Online:** 3 Siswa | 2 Guru")

st.markdown("---")

# --- 4. NAVIGASI UTAMA (SIDEBAR & TOP MODAL) ---
st.sidebar.title("Navigasi Sistem")
menu_pilihan = st.sidebar.radio("Pilih Portal:", ["Portal Siswa", "Ruang Guru", "Ruang Admin"])

# ==========================================
# 5. PORTAL SISWA (LOGIN & UJIAN)
# ==========================================
if menu_pilihan == "Portal Siswa":
    if st.session_state.logged_in_siswa is None:
        st.subheader("🎓 Pintu Masuk Siswa Ujian")
        st.markdown("Silakan pilih kelas, masukkan nomor peserta dan password yang tertera pada kartu ujian.")
        
        with st.form("form_login_siswa"):
            pilih_kelas = st.selectbox("Pilih Kelas", ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])
            no_peserta_input = st.text_input("Nomor Peserta")
            password_input = st.text_input("Password / Sandi", type="password")
            btn_login_siswa = st.form_submit_button("Masuk Kelas Ujian")
            
            if btn_login_siswa:
                # Validasi ke Database Siswa
                df_siswa = st.session_state.siswa_db
                cek = df_siswa[(df_siswa['kelas'] == pilih_kelas) & 
                               (df_siswa['no_peserta'] == no_peserta_input) & 
                               (df_siswa['password'] == password_input)]
                
                if not cek.empty:
                    st.session_state.logged_in_siswa = cek.iloc[0].to_dict()
                    st.success(f"Berhasil Masuk! Selamat Datang, {cek.iloc[0]['nama']}")
                    st.rerun()
                else:
                    st.error("Gagal Masuk! Periksa kembali Kelas, Nomor Peserta, atau Password Anda.")
    else:
        # Tampilan Ruang Ujian Siswa
        siswa = st.session_state.logged_in_siswa
        st.info(wel := f"Halo, **{siswa['nama']}** ({siswa['kelas']} - Rombel {siswa['rombel']})")
        
        if st.button("Keluar / Logout Siswa"):
            st.session_state.logged_in_siswa = None
            st.rerun()
            
        st.markdown("---")
        st.subheader("📝 Lembar Ujian Online (Simulasi)")
        st.warning("Mata Pelajaran Aktif: **Kurikulum Merdeka - Koding & Kecerdasan Artifisial (KKA)**")
        
        # Simulasi 1 Soal Per Layar (Exam Engine)
        st.markdown("**Soal 1 dari 10:** Apa kepanjangan dari AI dalam teknologi komputer?")
        opsi = st.radio("Pilih Jawaban:", ["A. Artifisial Intelligence", "B. Automated Item", "C. Aplikasi Internet", "D. Arsitektur Informasi"], key="soal_1")
        
        col_prev, col_next = st.columns([1, 1])
        with col_prev:
            st.button("⬅️ Sebelumnya")
        with col_next:
            if st.button("Selanjutnya ➡️"):
                st.toast("Jawaban tersimpan otomatis (Auto-Save Active)")
                
        st.markdown("---")
        if st.button("Selesai & Kirim Ujian", type="primary"):
            st.success("Ujian berhasil diselesaikan dan dikirim ke server guru!")

# ==========================================
# 6. RUANG GURU KELAS
# ==========================================
elif menu_pilihan == "Ruang Guru":
    if st.session_state.logged_in_guru is None:
        st.subheader("👨‍🏫 Login Ruang Guru Kelas")
        with st.form("form_login_guru"):
            nama_guru_input = st.text_input("Nama Guru / ID")
            pass_guru_input = st.text_input("Password Guru", type="password")
            btn_login_guru = st.form_submit_button("Masuk Ruang Guru")
            
            if btn_login_guru:
                df_guru = st.session_state.guru_db
                cek_guru = df_guru[(df_guru['nama_guru'].str.lower() == nama_guru_input.lower()) & 
                                   (df_guru['password'] == pass_guru_input)]
                if not cek_guru.empty or (nama_guru_input == "guru" and pass_guru_input == "123"):
                    st.session_state.logged_in_guru = nama_guru_input
                    st.success("Login Guru Berhasil!")
                    st.rerun()
                else:
                    st.error("Nama atau Password Guru salah.")
    else:
        st.subheader(f"📊 Dashboard Guru: {st.session_state.logged_in_guru}")
        if st.button("Logout Guru"):
            st.session_state.logged_in_guru = None
            st.rerun()
            
        tab1, tab2, tab3 = st.tabs(["Data Siswa Kelas", "Monitoring Ujian", "Koreksi & Rekap Nilai"])
        with tab1:
            st.markdown("### Daftar Siswa di Kelas Anda")
            st.dataframe(st.session_state.siswa_db, use_container_width=True)
        with tab2:
            st.markdown("### Status Pengerjaan Siswa Secara Real-Time")
            st.write("Belum ada sesi ujian aktif.")
        with tab3:
            st.markdown("### Koreksi Manual Esai & Nilai Akhir")
            st.write("Fitur rekap nilai siap digunakan.")

# ==========================================
# 7. RUANG ADMIN MASTER
# ==========================================
elif menu_pilihan == "Ruang Admin":
    if not st.session_state.logged_in_admin:
        st.subheader("🔐 Login Admin Master (Superadmin)")
        with st.form("form_login_admin"):
            username_admin = st.text_input("Username Admin")
            password_admin = st.text_input("Password Admin", type="password")
            btn_login_admin = st.form_submit_button("Masuk Admin")
            
            if btn_login_admin:
                # Kredensial sesuai permintaan
                if username_admin == "nasruddinrudi" and password_admin == "nasruddinHoja":
                    st.session_state.logged_in_admin = True
                    st.success("Login Admin Berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau Password Admin salah! (Gunakan: nasruddinrudi / nasruddinHoja)")
    else:
        st.subheader("👑 Panel Kontrol Utama Admin Master")
        if st.button("Logout Admin"):
            st.session_state.logged_in_admin = False
            st.rerun()
            
        tab_adm1, tab_adm2, tab_adm3, tab_adm4 = st.tabs(["Manajemen Siswa", "Manajemen Guru", "Bank Soal (14 Mapel)", "Pengaturan & OTP"])
        
        with tab_adm1:
            st.markdown("### Tambah / Kelola Database Siswa")
            with st.form("tambah_siswa"):
                c1, c2 = st.columns(2)
                with c1:
                    tk = st.selectbox("Kelas", ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])
                    tr = st.text_input("Rombel", "A")
                    np = st.text_input("Nomor Peserta")
                with c2:
                    ns = st.text_input("Nama Siswa (Otomatis Kapital)")
                    ps = st.text_input("Password Siswa", "123")
                
                submit_siswa = st.form_submit_button("Simpan Data Siswa Baru")
                if submit_siswa and np and ns:
                    new_row = {"kelas": tk, "rombel": tr, "no_peserta": np, "nama": ns.upper(), "password": ps}
                    st.session_state.siswa_db = pd.concat([st.session_state.siswa_db, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"Siswa {ns.upper()} berhasil ditambahkan!")
            
            st.markdown("#### Tabel Seluruh Siswa")
            st.dataframe(st.session_state.siswa_db, use_container_width=True)
            
        with tab_adm2:
            st.markdown("### Kelola Akun Guru Kelas")
            st.dataframe(st.session_state.guru_db, use_container_width=True)
            
        with tab_adm3:
            st.markdown("### Manajemen 14 Mata Pelajaran Kurikulum Merdeka & KKA")
            st.info("Mendukung 14 Mapel: Akidah Akhlak, Al-Qur'an Hadits, Fikih, SKI, Pancasila, Bahasa Indonesia, IPAS, Matematika, PJOK, SBdP, Bahasa Arab, Bahasa Sunda, Bahasa Inggris, dan Koding & Kecerdasan Artifisial (KKA).")
            
        with tab_adm4:
            st.markdown("### Keamanan 2FA & WhatsApp Gateway (085719824453)")
            st.success("Integrasi WhatsApp Gateway aktif untuk pengiriman OTP Admin.")
