import streamlit as st
from PIL import Image
import io
import numpy as np
import cv2
import base64
from io import BytesIO
from pydub import AudioSegment

# Fungsi untuk meresize gambar
def resize_image(image, target_size):
    # Resize gambar sesuai dengan target_size
    resized_image = image.resize(target_size)
    return resized_image

def compress_image(image, quality):
    # Konversi gambar PIL ke array numpy
    img_np = np.array(image)
    
    # Konversi dari BGR (OpenCV) ke RGB (matplotlib)
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
    
    # Kompresi gambar dengan kualitas tertentu
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, buffer = cv2.imencode('.jpg', img_rgb, encode_param)
    
    # Konversi kembali dari array byte ke gambar PIL
    img_compressed = Image.open(io.BytesIO(buffer))
    return img_compressed

# Fungsi untuk melakukan kompresi audio
def compress_audio(audio_bytes, bitrate='64k'):
    audio = AudioSegment.from_file(BytesIO(audio_bytes))
    compressed_audio = audio.export(format="mp3", bitrate=bitrate)
    return compressed_audio

def convert_audio_format(audio_bytes, target_format='mp3'):
    audio = AudioSegment.from_file(BytesIO(audio_bytes))
    output_buffer = BytesIO()
    audio.export(output_buffer, format=target_format)
    converted_audio_bytes = output_buffer.getvalue()
    return converted_audio_bytes


def main():
    st.title("Media Processing")

    # Sidebar untuk memilih opsi
    selected = st.sidebar.selectbox("Media Processing", ["Resize Image", "Compress Audio", "Convert Audio Format"])

    # Page Resize Gambar
    if selected == "Resize Image":
        st.header("Resize Image")

        uploaded_image = st.file_uploader("Upload Gambar", type=["png", "jpg", "jpeg"])
        if uploaded_image is not None:
            # Baca gambar yang diunggah
            image = Image.open(uploaded_image)

            st.subheader("Gambar Asli")
            st.image(image, caption="Gambar Asli", use_column_width=True)

            # Tampilkan opsi untuk meresize gambar
            new_width = st.number_input("Masukkan Lebar Gambar (px)", value=image.width)
            new_height = st.number_input("Masukkan Tinggi Gambar (px)", value=image.height)
            target_size = (new_width, new_height)

            # Resize gambar
            resized_image = resize_image(image, target_size)

            st.subheader("Gambar Setelah Resize")
            st.image(resized_image, caption=f"Ukuran: {target_size}", use_column_width=True)

            # Tampilkan slider untuk memilih kualitas kompresi
            compress_quality = st.slider("Pilih Kualitas Kompresi (0 = Terburuk, 100 = Terbaik)", 0, 100, 50)

            # Kompresi gambar
            compressed_image = compress_image(resized_image, compress_quality)

            st.subheader("Gambar Setelah Kompresi")
            st.image(compressed_image, caption=f"Kualitas Kompresi: {compress_quality}", use_column_width=True)

            # Tambahkan tombol untuk mengunduh gambar hasil
            if st.button("Unduh Gambar Hasil"):
                # Simpan gambar ke buffer byte
                img_byte_arr = io.BytesIO()
                compressed_image.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)

                # Encoding ke base64 dan tampilkan link untuk mengunduh gambar
                img_str = base64.b64encode(img_byte_arr.read()).decode()
                original_filename = uploaded_image.name  # Nama asli file yang diunggah
                download_filename = f"compressed_{original_filename}"  # Nama file hasil dengan awalan 'compressed_'
                href = f'<a href="data:image/jpg;base64,{img_str}" download="{download_filename}">Unduh Gambar</a>'
                st.markdown(href, unsafe_allow_html=True)
    # Page Convert Audio Format
    if selected == "Convert Audio Format":
        st.header("Convert Audio Format")

        uploaded_audio = st.file_uploader("Upload Audio File", type=["mp3", "wav"])
        if uploaded_audio is not None:
            st.write('Uploaded Audio File:', uploaded_audio.name)

            target_format = st.radio("Pilih Format Tujuan", ["mp3", "wav"])
            if st.button('Convert Audio'):
                converted_audio_bytes = convert_audio_format(uploaded_audio.getvalue(), target_format)

                st.audio(converted_audio_bytes, format=f'audio/{target_format}', start_time=0)

                st.download_button(
                    label=f"Download Converted Audio ({target_format.upper()})",
                    data=converted_audio_bytes,
                    file_name=f"converted_audio.{target_format}",
                    mime=f"audio/{target_format}"
                )
                st.success("Audio converted successfully!")
    # Page Compress Audio
    elif selected == "Compress Audio":
        st.header("Compress Audio")

        uploaded_audio = st.file_uploader("Upload Audio File", type=["mp3", "wav"])
        if uploaded_audio is not None:
            st.write('Uploaded Audio File:', uploaded_audio.name)

            if st.button('Compress Audio'):
                compressed_audio = compress_audio(uploaded_audio.getvalue())
                compressed_audio_bytes = compressed_audio.read()

                st.audio(compressed_audio_bytes, format='audio/mp3', start_time=0)

                st.download_button(
                    label="Download Compressed Audio",
                    data=compressed_audio_bytes,
                    file_name="compressed_audio.mp3",
                    mime="audio/mp3"
                )
                st.success("Audio compressed successfully!")

if __name__ == '__main__':
    main()
