import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Ujian MI Ashsholahiyah Cilamaya",
    page_icon="🏫",
    layout="wide"
)

# --- 2. KONEKSI GOOGLE SHEETS API ---
@st.cache_resource(ttl=60)
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Membaca credentials dari st.secrets (TOML)
    creds_dict = dict(st.secrets["gsheets"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

try:
    client = init_connection()
    # Membuka Spreadsheet berdasarkan sheet_name di Secrets atau nama langsung
    sheet_name = st.secrets["gsheets"].get("sheet_name", "DB_Ujian_MI_Ashsholahiyah")
    spreadsheet = client.open(sheet_name)
    db_terhubung = True
except Exception as e:
    db_terhubung = False
    st.error(f"Gagal terhubung ke Google Sheets. Periksa konfigurasi Secrets. Error: {e}")

# Fungsi membaca data dari tab tertentu
def load_data(tab_name):
    if not db_terhubung:
        return pd.DataFrame()
    sheet = spreadsheet.worksheet(tab_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Fungsi menambah baris baru ke tab tertentu
def append_data(tab_name, row_list):
    if db_terhubung:
        sheet = spreadsheet.worksheet(tab_name)
        sheet.append_row(row_list)
        st.cache_data.clear()

# --- 3. HEADER & WIDGET INFO ---
st.markdown("<h1 style='text-align: center; color: #0d5c3b;'>UJIAN MI ASHSHOLAHIYAH CILAMAYA</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"📅 **Hari/Tanggal:** {datetime.now().strftime('%d %b %Y')}")
with col2:
    st.markdown(f"⏰ **Jam:** {datetime.now().strftime('%H:%M:%S')} WIB")
with col3:
    if db_terhubung:
        st.success("🟢 Google Sheets Connected")
    else:
        st.error("🔴 Google Sheets Disconnected")

st.markdown("---")

# --- 4. NAVIGASI UTAMA ---
st.sidebar.title("Navigasi Sistem")
menu = st.sidebar.radio("Pilih Portal:", ["Portal Siswa", "Ruang Guru", "Ruang Admin"])

# Inisialisasi State Login
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "guru_logged_in" not in st.session_state:
    st.session_state.guru_logged_in = None

# ==========================================
# 5. RUANG ADMIN MASTER
# ==========================================
if menu == "Ruang Admin":
    if not st.session_state.admin_logged_in:
        st.subheader("🔐 Login Admin Master")
        with st.form("login_admin_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            btn = st.form_submit_button("Masuk Admin")
            if btn:
                if u == "nasruddinrudi" and p == "nasruddinHoja":
                    st.session_state.admin_logged_in = True
                    st.success("Login Berhasil!")
                    st.rerun()
                else:
                    st.error("Username / Password Admin Salah!")
    else:
        st.subheader("👑 Panel Kontrol Utama Admin Master")
        if st.button("Logout Admin"):
            st.session_state.admin_logged_in = False
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["Manajemen Siswa", "Manajemen Guru", "Bank Soal"])

        # --- TAB MANAJEMEN GURU (SINKRON GOOGLE SHEETS) ---
        with tab2:
            st.markdown("### Kelola Akun Guru Kelas (Data Live dari Google Sheets)")
            
            # Membaca data langsung dari tab 'Guru' di Google Sheets
            df_guru = load_data("Guru")
            st.dataframe(df_guru, use_container_width=True)

            st.markdown("---")
            st.markdown("#### Tambah Guru Baru ke Google Sheets")
            with st.form("tambah_guru_form"):
                nama_guru = st.text_input("Nama Guru")
                kelas_ajar = st.text_input("Kelas Ajar (misal: 4 / 1a)")
                pass_guru = st.text_input("Password Guru")
                btn_simpan_guru = st.form_submit_button("Simpan Guru ke Google Sheets")

                if btn_simpan_guru and nama_guru:
                    # Menambahkan data ke baris paling bawah tab 'Guru'
                    append_data("Guru", [nama_guru, kelas_ajar, pass_guru, "offline", "offline"])
                    st.success(f"Guru {nama_guru} berhasil ditambahkan ke Google Sheets!")
                    st.rerun()

        # --- TAB MANAJEMEN SISWA ---
        with tab1:
            st.markdown("### Database Siswa")
            df_siswa = load_data("Siswa")
            st.dataframe(df_siswa, use_container_width=True)

        # --- TAB BANK SOAL ---
        with tab3:
            st.markdown("### Bank Soal")
            df_soal = load_data("BankSoal")
            st.dataframe(df_soal, use_container_width=True)

# ==========================================
# 6. RUANG GURU
# ==========================================
elif menu == "Ruang Guru":
    st.subheader("👨‍🏫 Login Ruang Guru Kelas")
    df_guru = load_data("Guru")
    
    with st.form("login_guru_form"):
        u_guru = st.text_input("Nama / Username Guru")
        p_guru = st.text_input("Password", type="password")
        btn_g = st.form_submit_button("Masuk Ruang Guru")
        
        if btn_g and not df_guru.empty:
            # Validasi langsung dengan data di Google Sheets
            cek = df_guru[(df_guru['nama_guru'].astype(str).str.lower() == u_guru.lower()) & 
                          (df_guru['password'].astype(str) == str(p_guru))]
            if not cek.empty:
                st.success(f"Selamat Datang, {u_guru}!")
            else:
                st.error("Data guru tidak ditemukan di Google Sheets.")

# ==========================================
# 7. PORTAL SISWA
# ==========================================
elif menu == "Portal Siswa":
    st.subheader("🎓 Portal Masuk Ujian Siswa")
    df_siswa = load_data("Siswa")
    
    with st.form("login_siswa_form"):
        no_p = st.text_input("Nomor Peserta")
        pass_s = st.text_input("Password", type="password")
        btn_s = st.form_submit_button("Masuk Ujian")
        
        if btn_s and not df_siswa.empty:
            cek_s = df_siswa[(df_siswa['no_peserta'].astype(str) == str(no_p)) & 
                             (df_siswa['password'].astype(str) == str(pass_s))]
            if not cek_s.empty:
                st.success(f"Selamat Mengerjakan, {cek_s.iloc[0]['nama']}!")
            else:
                st.error("Nomor Peserta atau Password Siswa Salah.")
