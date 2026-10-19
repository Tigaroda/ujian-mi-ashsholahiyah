import streamlit as st
import pandas as pd

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Ujian MI Ashsholahiyah Cilamaya", page_icon="🏫", layout="wide")

st.title("🏫 UJIAN MI ASHSHOLAHIYAH CILAMAYA")
st.markdown("---")

# Widget Real-time Sidebar & Info
st.sidebar.title("Navigasi")
menu = st.sidebar.radio("Pilih Menu:", ["Portal Siswa", "Ruang Guru", "Ruang Admin"])

if menu == "Portal Siswa":
    st.subheader("Silakan Masuk Untuk Mengerjakan Ujian")
    # Form Pilih Kelas, No Peserta, Password
    pilih_kelas = st.selectbox("Pilih Kelas", ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])
    no_peserta = st.text_input("Nomor Peserta")
    password = st.text_input("Password", type="password")
    
    if st.button("Masuk Kelas Ujian"):
        st.success(f"Memverifikasi data siswa kelas {pilih_kelas}...")
        # Logika pengecekan ke Google Sheets ditaruh di sini

elif menu == "Ruang Guru":
    st.subheader("Login Ruang Guru Kelas")
    # Form login guru

elif menu == "Ruang Admin":
    st.subheader("Login Admin Master (2FA OTP)")
    # Form login admin (nasruddinrudi / nasruddinHoja)
