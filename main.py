import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
from st_social_media_links import SocialMediaIcons
import random

# Cargar el logo SVG desde un archivo
with open("data/logo.svg", "r") as svg_file:
    svg_logo = svg_file.read()

# Incrustar el logo SVG usando HTML
st.markdown(f'<div style="text-align:center">{svg_logo}</div>', unsafe_allow_html=True)
st.subheader("Descubre contra qué Digimon pelearía tu gato")

# Función para recortar y redimensionar la imagen
def recortar_y_redimensionar(imagen, tamaño=(255, 255)):
    imagen = imagen.convert("RGBA")
    ancho, alto = imagen.size
    nuevo_tamaño = min(ancho, alto)
    izquierda = (ancho - nuevo_tamaño) / 2
    superior = (alto - nuevo_tamaño) / 2
    derecha = (ancho + nuevo_tamaño) / 2
    inferior = (alto + nuevo_tamaño) / 2
    imagen_recortada = imagen.crop((izquierda, superior, derecha, inferior))
    imagen_redimensionada = imagen_recortada.resize(tamaño, Image.LANCZOS)
    return imagen_redimensionada

# Subir imagen
uploaded_image = st.file_uploader("Sube una imagen de tu gato", type=["jpg", "jpeg", "png"])

# Mostrar la imagen del gato si ha sido cargada
if uploaded_image is not None:
    st.image(uploaded_image, caption="Imagen de tu gato")

# Input para el nombre del gato
nombre_gato = st.text_input("Introduce el nombre de tu gato", "Garfield")

# Botón para buscar contrincante Digimon (desactivado hasta que se suba una imagen)
if st.button("Buscar contrincante Digimon", disabled=uploaded_image is None):
    # Obtener datos de Digimon desde la API
    response = requests.get("https://digi-api.com/api/v1/digimon")
    digimon_data = response.json()

    # Imprimir los datos para depuración
    #st.write(digimon_data)

    # Asegurarnos de que la clave 'content' está presente en la respuesta
    if 'content' in digimon_data:
        # Seleccionar un Digimon aleatorio
        digimon_mas_cercano = random.choice(digimon_data['content'])

        # Mostrar los resultados
        if digimon_mas_cercano:
            st.write(f"¡El contrincante perfecto es **{digimon_mas_cercano['name']}**!")

            # Cargar la plantilla y fuentes
            plantilla = Image.open("data/plantilla.png").convert("RGBA")
            try:
                font_path = "fonts/pokemon_classic.ttf"
                font_nombre = ImageFont.truetype(font_path, 45)
                font_peso = ImageFont.truetype(font_path, 30)
            except IOError:
                font_nombre = ImageFont.load_default()
                font_peso = ImageFont.load_default()

            # Crear un objeto para dibujar sobre la imagen
            draw = ImageDraw.Draw(plantilla)

            # Cargar y procesar la imagen del gato y Digimon
            imagen_gato = Image.open(uploaded_image)
            imagen_gato = recortar_y_redimensionar(imagen_gato)

            digimon_image_url = digimon_mas_cercano['image']
            imagen_digimon = Image.open(requests.get(digimon_image_url, stream=True).raw).convert("RGBA").resize((255, 255))

            # Posiciones hardcodeadas para los elementos
            posiciones = {
                "nombre_gato": (300, 490),
                "imagen_gato": (167, 226),
                "nombre_digimon": (990, 490),
                "imagen_digimon": (855, 232),
            }

            # Calcular ancho de los nombres para centrar
            bbox_nombre_gato = draw.textbbox((0, 0), nombre_gato, font=font_nombre)
            bbox_nombre_digimon = draw.textbbox((0, 0), digimon_mas_cercano['name'], font=font_nombre)

            ancho_nombre_gato = bbox_nombre_gato[2] - bbox_nombre_gato[0]
            ancho_nombre_digimon = bbox_nombre_digimon[2] - bbox_nombre_digimon[0]

            # Calcular la nueva posición X para centrar los nombres
            posicion_centrada_gato = (posiciones["nombre_gato"][0] - ancho_nombre_gato // 2, posiciones["nombre_gato"][1])
            posicion_centrada_digimon = (posiciones["nombre_digimon"][0] - ancho_nombre_digimon // 2, posiciones["nombre_digimon"][1])

            # Dibujar los textos (nombre) en la plantilla
            draw.text(posicion_centrada_gato, nombre_gato, font=font_nombre, fill="white")
            draw.text(posicion_centrada_digimon, digimon_mas_cercano['name'], font=font_nombre, fill="white")

            # Pegar las imágenes sobre la plantilla en las posiciones correspondientes
            plantilla.paste(imagen_gato, posiciones["imagen_gato"], imagen_gato)
            plantilla.paste(imagen_digimon, posiciones["imagen_digimon"], imagen_digimon)

            # Convertir la imagen final a RGB
            plantilla_final = plantilla.convert("RGB")

            # Mostrar la imagen resultante
            st.image(plantilla_final)

            # Crear un archivo para la imagen final
            buffer = io.BytesIO()
            plantilla_final.save(buffer, format="PNG")
            buffer.seek(0)

            # Botón para descargar la imagen
            st.download_button(
                label="Descargar imagen",
                data=buffer,
                file_name="resultado_digimon_vs_gato.png",
                mime="image/png"
            )

            # Crear enlaces de redes sociales con st-social-media-links
            social_media_links = [
                "https://x.com/intent/tweet?text=¡Mira%20el%20resultado%20del%20enfrentamiento%20entre%20mi%20gato%20y%20un%20Digimon!%20%23GatoVsDigimon&url=https://gatovsdigimon.streamlit.app",
                "https://www.tiktok.com/@izanhacecosas",
                "https://youtube.com/@quarto.es",
                "https://www.instagram.com/izanhacecosas/"
            ]

            social_media_icons = SocialMediaIcons(social_media_links)
            social_media_icons.render()
    else:
        st.error("No se pudo obtener información de Digimon. Por favor, inténtalo de nuevo más tarde.")
