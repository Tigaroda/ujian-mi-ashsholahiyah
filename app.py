import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Ujian MI Ashsholahiyah Cilamaya",
    page_icon="🏫",
    layout="wide"
)

# --- 2. KONEKSI GOOGLE SHEETS MENGGUNAKAN ST-GSHEETS-CONNECTION ---
# Membuat koneksi
conn = st.connection("gsheets", type=GSheetsConnection)

# Fungsi membaca data dari tab tertentu (ttl=0 agar selalu real-time)
def load_data(tab_name):
    try:
        # Membaca berdasarkan nama worksheet/tab di spreadsheet
        df = conn.read(worksheet=tab_name, ttl=0)
        return df
    except Exception as e:
        st.warning(f"Gagal memuat tab {tab_name}: {e}")
        return pd.DataFrame()

# --- 3. HEADER & WIDGET INFO ---
st.markdown("<h1 style='text-align: center; color: #0d5c3b;'>UJIAN MI ASHSHOLAHIYAH CILAMAYA</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"📅 **Hari/Tanggal:** {datetime.now().strftime('%d %b %Y')}")
with col2:
    st.markdown(f"⏰ **Jam:** {datetime.now().strftime('%H:%M:%S')} WIB")
with col3:
    st.success("🟢 Google Sheets Connected (St-Gsheets)")

st.markdown("---")

# --- 4. NAVIGASI UTAMA ---
st.sidebar.title("Navigasi Sistem")
menu = st.sidebar.radio("Pilih Portal:", ["Portal Siswa", "Ruang Guru", "Ruang Admin"])

# Inisialisasi State Login
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

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

        with tab2:
            st.markdown("### Kelola Akun Guru Kelas (Data Live dari Google Sheets)")
            df_guru = load_data("Guru")
            st.dataframe(df_guru, use_container_width=True)

        with tab1:
            st.markdown("### Database Siswa")
            df_siswa = load_data("Siswa")
            st.dataframe(df_siswa, use_container_width=True)

        with tab3:
            st.markdown("### Bank Soal")
            df_soal = load_data("BankSoal")
            st.dataframe(df_soal, use_container_width=True)

# ==========================================
# 6. RUANG GURU & 7. PORTAL SISWA
# ==========================================
elif menu == "Ruang Guru":
    st.subheader("👨‍🏫 Ruang Guru Kelas")
    df_guru = load_data("Guru")
    st.dataframe(df_guru, use_container_width=True)

elif menu == "Portal Siswa":
    st.subheader("🎓 Portal Masuk Ujian Siswa")
    df_siswa = load_data("Siswa")
    st.write("Silakan masukkan nomor peserta ujian Anda.")
