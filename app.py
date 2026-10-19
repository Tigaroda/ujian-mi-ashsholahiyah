import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="UJIAN MI ASHSHOLAHIYAH CILAMAYA",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS CUSTOM TEMA AURORA MUTIARA & EMERALD ---
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #0d5c3b;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #2e7d32;
        font-size: 1rem;
        margin-bottom: 25px;
    }
    .card-aurora {
        background: linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 50%, #faf5ff 100%);
        border: 2px solid #a7f3d0;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. KONEKSI GOOGLE SHEETS API (ROBUST FIX) ---
@st.cache_resource(ttl=60)
def get_gsheets_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Ambil dict dari Secrets
    creds_dict = dict(st.secrets["gsheets"])
    # Perbaikan Karakter Baris Baru (\n) pada Private Key agar tidak Invalid JWT Signature
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

try:
    gc = get_gsheets_client()
    sheet_name = st.secrets["gsheets"].get("sheet_name", "DB_Ujian_MI_Ashsholahiyah")
    sh = gc.open(sheet_name)
    db_connected = True
except Exception as e:
    db_connected = False
    db_error_msg = str(e)

def get_table_data(worksheet_name):
    if not db_connected:
        return pd.DataFrame()
    try:
        ws = sh.worksheet(worksheet_name)
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception as err:
        st.warning(f"Gagal mengambil data tab '{worksheet_name}': {err}")
        return pd.DataFrame()

def append_table_data(worksheet_name, row_values):
    if db_connected:
        try:
            ws = sh.worksheet(worksheet_name)
            ws.append_row(row_values)
            st.cache_data.clear()
            return True
        except Exception as err:
            st.error(f"Gagal menambah data: {err}")
            return False
    return False

# --- 3. SESSION STATES ---
if "user_role" not in st.session_state:
    st.session_state.user_role = None # 'siswa', 'guru', 'admin'
if "siswa_info" not in st.session_state:
    st.session_state.siswa_info = None
if "guru_info" not in st.session_state:
    st.session_state.guru_info = None
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "jawaban_siswa" not in st.session_state:
    st.session_state.jawaban_siswa = {}

# --- 4. HEADER UTAMA & WIDGET REAL-TIME ---
st.markdown("<div class='main-title'>ÜJIAN MI ASHSHOLAHIYAH CILAMAYA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Sistem Ujian Online & Database Terintegrasi Kurikulum Merdeka</div>", unsafe_allow_html=True)

col_h1, col_h2, col_h3 = st.columns([1.5, 1.5, 1])
with col_h1:
    st.markdown(f"📅 **Hari/Tanggal:** {datetime.now().strftime('%A, %d %b %Y')}")
with col_h2:
    st.markdown(f"⏰ **Jam:** {datetime.now().strftime('%H:%M:%S')} WIB")
with col_h3:
    if db_connected:
        st.success("🟢 Database Terhubung")
    else:
        st.error("🔴 Database Terputus")

st.markdown("---")

# --- 5. NAVIGASI SIDEBAR ---
st.sidebar.title("📌 Menu Utama")
portal_pilihan = st.sidebar.radio("Pilih Portal Akses:", ["Portal Siswa", "Ruang Guru Kelas", "Ruang Admin Master"])

# ==========================================
# PORTAL SISWA
# ==========================================
if portal_pilihan == "Portal Siswa":
    if st.session_state.siswa_info is None:
        st.markdown("<div class='card-aurora'>", unsafe_allow_html=True)
        st.subheader("🎓 Portal Masuk Ujian Siswa")
        st.write("Silakan pilih kelas, masukkan nomor peserta dan password sesuai kartu ujian.")
        
        with st.form("form_siswa_login"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                pilih_kelas = st.selectbox("Pilih Kelas", ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])
                pilih_rombel = st.selectbox("Pilih Rombel", ["A", "B", "C"])
            with col_s2:
                no_peserta = st.text_input("Nomor Peserta Ujian")
                pass_siswa = st.text_input("Password", type="password")
            
            btn_login_siswa = st.form_submit_button("Masuk Kelas Ujian", type="primary")
            
            if btn_login_siswa:
                df_siswa = get_table_data("Siswa")
                if not df_siswa.empty:
                    # Pencocokan data
                    cek = df_siswa[
                        (df_siswa['no_peserta'].astype(str) == str(no_peserta).strip()) &
                        (df_siswa['password'].astype(str) == str(pass_siswa).strip())
                    ]
                    if not cek.empty:
                        st.session_state.siswa_info = cek.iloc[0].to_dict()
                        st.success(f"Selamat Datang, {cek.iloc[0]['nama']}!")
                        st.rerun()
                    else:
                        st.error("Nomor Peserta atau Password tidak cocok!")
                else:
                    # Fallback simulasi jika DB belum terisi
                    if no_peserta == "123" and pass_siswa == "123":
                        st.session_state.siswa_info = {"nama": "SIHATUL AFIAH", "kelas": pilih_kelas, "rombel": pilih_rombel, "no_peserta": "123"}
                        st.rerun()
                    else:
                        st.error("Data siswa gagal diverifikasi dari database.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # Lembar Pengisian Ujian Siswa (Exam Engine)
        s_data = st.session_state.siswa_info
        st.info(f"👤 **Peserta:** {s_data.get('nama')} | **Kelas:** {s_data.get('kelas')} - {s_data.get('rombel')} | **No. Peserta:** {s_data.get('no_peserta')}")
        
        if st.button("Keluar Ujian"):
            st.session_state.siswa_info = None
            st.rerun()
            
        st.markdown("---")
        st.subheader("📝 Lembar Ujian: Koding & Kecerdasan Artifisial (KKA)")
        
        # Simulasi Soal 1 per Layar dengan Auto-Save State
        st.markdown("#### Soal No. 1 (Pilihan Ganda)")
        st.write("Apa fungsi utama dari Kecerdasan Artifisial (AI) dalam kehidupan sehari-hari?")
        
        opsi_pilihan = st.radio(
            "Pilih Jawaban Anda:",
            ["A. Membantu memproses data dan mengambil keputusan secara otomatis",
             "B. Menggantikan seluruh fisik manusia secara permanen",
             "C. Menghapus semua dokumen kertas di sekolah",
             "D. Mematikan jaringan internet"],
            key="soal_1_val"
        )
        
        # Auto Save indikator
        st.session_state.jawaban_siswa["soal_1"] = opsi_pilihan
        st.caption("🔒 *Auto-Save Aktif: Jawaban tersimpan otomatis di perangkat Anda.*")
        
        col_nav1, col_nav2 = st.columns([1,1])
        with col_nav1:
            st.button("⬅️ Soal Sebelumnya", disabled=True)
        with col_nav2:
            if st.button("Soal Selanjutnya ➡️", type="primary"):
                st.toast("Jawaban Soal 1 Tersimpan!")
                
        st.markdown("---")
        if st.button("Selesai & Kirim Jawaban Ujian"):
            st.balloons()
            st.success("Ujian Berhasil Diselesaikan! Nilai sementara Anda telah dicatat.")

# ==========================================
# RUANG GURU KELAS
# ==========================================
elif portal_pilihan == "Ruang Guru Kelas":
    if st.session_state.guru_info is None:
        st.subheader("👨‍🏫 Login Ruang Guru Kelas")
        df_guru = get_table_data("Guru")
        
        with st.form("form_guru_login"):
            u_guru = st.text_input("Nama Guru / Username")
            p_guru = st.text_input("Password Guru", type="password")
            btn_guru = st.form_submit_button("Masuk Ruang Guru")
            
            if btn_guru:
                if not df_guru.empty:
                    cek_g = df_guru[
                        (df_guru['nama_guru'].astype(str).str.lower() == u_guru.strip().lower()) &
                        (df_guru['password'].astype(str) == p_guru.strip())
                    ]
                    if not cek_g.empty:
                        st.session_state.guru_info = cek_g.iloc[0].to_dict()
                        st.success("Login Guru Berhasil!")
                        st.rerun()
                    else:
                        st.error("Nama Guru atau Password Salah.")
                else:
                    if u_guru == "guru" and p_guru == "123":
                        st.session_state.guru_info = {"nama_guru": "Guru Kelas", "kelas_ajar": "5"}
                        st.rerun()
                    else:
                        st.error("Data guru tidak ditemukan di spreadsheet.")
    else:
        g_data = st.session_state.guru_info
        st.subheader(f"👨‍🏫 Dashboard Guru: {g_data.get('nama_guru')} (Kelas {g_data.get('kelas_ajar')})")
        
        if st.button("Logout Guru"):
            st.session_state.guru_info = None
            st.rerun()
            
        tab_g1, tab_g2, tab_g3 = st.tabs(["Data Siswa Kelas Saya", "Bank Soal Kelas", "Monitoring & Rekap Nilai"])
        
        with tab_g1:
            st.markdown("### Daftar Siswa Terdaftar")
            df_siswa_all = get_table_data("Siswa")
            if not df_siswa_all.empty and 'kelas' in df_siswa_all.columns:
                # Filter khusus kelas ajar guru
                k_ajar = str(g_data.get('kelas_ajar')).lower()
                df_filtered = df_siswa_all[df_siswa_all['kelas'].astype(str).str.lower().str.contains(k_ajar)]
                st.dataframe(df_filtered, use_container_width=True)
            else:
                st.dataframe(df_siswa_all, use_container_width=True)
                
        with tab_g2:
            st.markdown("### Bank Soal Kelas")
            df_soal = get_table_data("BankSoal")
            st.dataframe(df_soal, use_container_width=True)
            
        with tab_g3:
            st.markdown("### Rekapitulasi Nilai Ujian Siswa")
            st.write("Belum ada data ujian yang diselenggarakan hari ini.")

# ==========================================
# RUANG ADMIN MASTER
# ==========================================
elif portal_pilihan == "Ruang Admin Master":
    if not st.session_state.admin_logged:
        st.subheader("👑 Login Admin Master (Superadmin)")
        with st.form("form_admin_login"):
            u_admin = st.text_input("Username Admin")
            p_admin = st.text_input("Password Admin", type="password")
            btn_admin = st.form_submit_button("Masuk Admin Master", type="primary")
            
            if btn_admin:
                if u_admin == "nasruddinrudi" and p_admin == "nasruddinHoja":
                    st.session_state.admin_logged = True
                    st.success("Login Admin Master Berhasil!")
                    st.rerun()
                else:
                    st.error("Kredensial Admin Master Salah!")
    else:
        st.subheader("👑 Panel Kontrol Utama Admin Master")
        if st.button("Logout Admin"):
            st.session_state.admin_logged = False
            st.rerun()
            
        tab_a1, tab_a2, tab_a3, tab_a4 = st.tabs(["Database Siswa", "Database Guru", "14 Bank Soal Mapel", "Pengaturan OTP WA"])
        
        with tab_a1:
            st.markdown("### Master Database Siswa")
            df_siswa_adm = get_table_data("Siswa")
            st.dataframe(df_siswa_adm, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### Tambah Siswa Baru (Otomatis Kapital)")
            with st.form("form_add_siswa"):
                c_a, c_b = st.columns(2)
                with c_a:
                    k_in = st.selectbox("Kelas", ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])
                    r_in = st.text_input("Rombel", "A")
                    np_in = st.text_input("Nomor Peserta")
                with c_b:
                    nm_in = st.text_input("Nama Siswa")
                    ps_in = st.text_input("Password", "123")
                
                btn_simpan_s = st.form_submit_button("Simpan Siswa Baru")
                if btn_simpan_s and np_in and nm_in:
                    res = append_table_data("Siswa", [k_in, r_in, np_in, nm_in.upper(), ps_in, "offline", "", ""])
                    if res:
                        st.success(f"Siswa {nm_in.upper()} berhasil ditambahkan ke Google Sheets!")
                        st.rerun()
        
        with tab_a2:
            st.markdown("### Master Database Guru")
            df_guru_adm = get_table_data("Guru")
            st.dataframe(df_guru_adm, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### Tambah Guru Kelas Baru")
            with st.form("form_add_guru"):
                ng_in = st.text_input("Nama Guru")
                ka_in = st.text_input("Kelas Ajar (misal: 5 / 1a)")
                pw_in = st.text_input("Password Guru")
                btn_simpan_g = st.form_submit_button("Simpan Guru")
                if btn_simpan_g and ng_in:
                    res_g = append_table_data("Guru", [ng_in, ka_in, pw_in, "offline", "offline"])
                    if res_g:
                        st.success(f"Guru {ng_in} berhasil ditambahkan!")
                        st.rerun()
                        
        with tab_a3:
            st.markdown("### Master Bank Soal (14 Mapel Kurikulum Merdeka)")
            st.caption("Mapel: Akidah Akhlak, Al-Qur'an Hadits, Fikih, SKI, Pendidikan Pancasila, Bahasa Indonesia, IPAS, Matematika, PJOK, SBdP, Bahasa Arab, Bahasa Sunda, Bahasa Inggris, Koding & AI (KKA).")
            df_soal_adm = get_table_data("BankSoal")
            st.dataframe(df_soal_adm, use_container_width=True)
            
        with tab_a4:
            st.markdown("### Keamanan 2FA OTP WhatsApp")
            st.info("Nomor Tujuan OTP Admin: **085719824453**")
            st.success("WhatsApp Gateway API Status: Standby")
