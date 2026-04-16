import streamlit as st
import numpy as np
from PIL import Image
import io

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Color2Grey Converter", 
    page_icon="🎨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kustomisasi CSS sedikit untuk menyembunyikan menu default dan merapikan tampilan
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .st-emotion-cache-1v0mbdj > img {border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);}
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER APLIKASI ---
st.markdown("<h1 style='text-align: center; color: #2e6c80;'>🎨 Color2Grey Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Aplikasi Konversi Citra RGB ke Grayscale Secara Spasial (Algoritmik)</p>", unsafe_allow_html=True)
st.divider()

# --- 3. SIDEBAR (PENGATURAN & IDENTITAS) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3003/3003035.png", width=80)
    st.markdown("### 👨‍💻 Profil Pengembang")
    st.markdown("**Azmi Naifah Iftinah**<br>NPM: 140810230013<br>Teknik Informatika Unpad", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### ⚙️ Panel Kendali")
    uploaded_file = st.file_uploader("1. Unggah Gambar (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
    
    metode = st.selectbox(
        "2. Pilih Metode Konversi:",
        (
            "Averaging (Perataan)", 
            "Weighting (Luma BT.709)", 
            "Desaturation", 
            "Decomposition (Max)", 
            "Decomposition (Min)", 
            "Single Channel (Green)"
        )
    )

# --- 4. AREA UTAMA (TABS) ---
tab1, tab2 = st.tabs(["🎛️ Ruang Kerja (Konverter)", "📚 Dasar Teori"])

with tab2:
    st.header("Dasar Teori Algoritma")
    st.markdown("""
    Aplikasi ini memproses citra tanpa menggunakan *library* instan. Setiap piksel disisir dan dihitung menggunakan metode berikut:
    * **Averaging:** Menjumlahkan R, G, B lalu membaginya dengan 3.
    * **Weighting (BT.709):** Memberikan bobot spesifik (Merah 21.26%, Hijau 71.52%, Biru 7.22%).
    * **Desaturation:** Mengambil nilai tengah antara intensitas tertinggi dan terendah pada piksel.
    * **Decomposition:** Mengambil nilai mutlak tertinggi (Max) atau terendah (Min) dari elemen RGB.
    * **Single Channel:** Murni hanya mengambil intensitas dari warna Hijau (Green).
    """)

with tab1:
    if uploaded_file is not None:
        # Membaca gambar yang diunggah
        image = Image.open(uploaded_file).convert('RGB')
        
        # [FITUR PINTAR] Auto-Resize
        max_size = 400 # Diperkecil sedikit lagi agar web merespon lebih instan
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size))
            st.info(f"💡 Info: Gambar di-resize otomatis menjadi {image.size} piksel agar algoritma manual berjalan lancar di browser.")
            
        img_array = np.array(image)
        tinggi, lebar, _ = img_array.shape
        
        # UI: Menampilkan informasi gambar
        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("Resolusi Lebar", f"{lebar} px")
        col_info2.metric("Resolusi Tinggi", f"{tinggi} px")
        col_info3.metric("Metode Aktif", metode.split(" ")[0])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Area Tombol dan Proses
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            proses_btn = st.button("🚀 MULAI PROSES KONVERSI", use_container_width=True, type="primary")
        
        if proses_btn:
            img_gray = np.zeros((tinggi, lebar))
            
            with st.spinner(f'Mengalkulasi piksel dengan algoritma {metode}...'):
                
                # --- ALGORITMA UTAMA (TIDAK ADA YANG DIUBAH) ---
                for i in range(tinggi):
                    for j in range(lebar):
                        R = float(img_array[i, j, 0])
                        G = float(img_array[i, j, 1])
                        B = float(img_array[i, j, 2])
                        
                        if metode == "Averaging (Perataan)":
                            img_gray[i, j] = (R + G + B) / 3.0
                        elif metode == "Weighting (Luma BT.709)":
                            img_gray[i, j] = (0.2126 * R) + (0.7152 * G) + (0.0722 * B)
                        elif metode == "Desaturation":
                            img_gray[i, j] = (max(R, G, B) + min(R, G, B)) / 2.0
                        elif metode == "Decomposition (Max)":
                            img_gray[i, j] = max(R, G, B)
                        elif metode == "Decomposition (Min)":
                            img_gray[i, j] = min(R, G, B)
                        elif metode == "Single Channel (Green)":
                            img_gray[i, j] = G
                
                # --- TAMPILAN HASIL ---
                st.toast('Selesai! Gambar berhasil dikonversi.', icon='🎉')
                img_gray_display = np.clip(img_gray, 0, 255).astype(np.uint8)
                
                st.divider()
                
                col_img1, col_img2 = st.columns(2)
                with col_img1:
                    st.markdown("<h4 style='text-align: center;'>Gambar Asli (RGB)</h4>", unsafe_allow_html=True)
                    st.image(image, use_container_width=True)
                    
                with col_img2:
                    st.markdown(f"<h4 style='text-align: center;'>Hasil: {metode}</h4>", unsafe_allow_html=True)
                    st.image(img_gray_display, use_container_width=True)
                
                # --- FITUR UNDUH ---
                # Mengubah array NumPy kembali menjadi gambar untuk bisa diunduh
                result_img = Image.fromarray(img_gray_display)
                buf = io.BytesIO()
                result_img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.markdown("<br>", unsafe_allow_html=True)
                col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                with col_dl2:
                    st.download_button(
                        label="📥 Unduh Gambar Hasil Konversi",
                        data=byte_im,
                        file_name=f"grayscale_{metode.split(' ')[0].lower()}.png",
                        mime="image/png",
                        use_container_width=True
                    )

    else:
        # Tampilan kosong/placeholder yang rapi
        st.info("👋 Selamat datang! Silakan unggah gambar pada panel di sebelah kiri untuk melihat keajaiban algoritma.")