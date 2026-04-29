import streamlit as st
import google.generativeai as genai

# 1. PON TU LLAVE SECRETA AQUÍ ADENTRO DE LAS COMILLAS
API_KEY = "AIzaSyB5cxkIAbd9qV5BCzNbjqdLo7nQC3eKJS4" 

genai.configure(api_key=API_KEY)
modelo = genai.GenerativeModel('gemini-2.5-flash')

# 2. DISEÑO DEL CONSULTORIO ACTUALIZADO
st.title("Mi Escriba Médico AI 🩺🎙️")
st.write("Sube una nota de voz de tu celular o graba en vivo para crear tu nota clínica estructurada.")

st.divider() # Una línea visual separadora

# 3. EL SELECTOR DE MODO
modo = st.radio("¿Cómo quieres ingresar el audio?", ["Subir archivo desde mi computadora", "Grabar en vivo con el micrófono"])

audio_para_procesar = None
tipo_de_archivo = "audio/wav"

if modo == "Subir archivo desde mi computadora":
    # El nuevo botón para subir archivos
    archivo_subido = st.file_uploader("Selecciona tu archivo de audio (Formatos: MP3, WAV, M4A, OGG)", type=['mp3', 'wav', 'm4a', 'ogg'])
    if archivo_subido is not None:
        st.audio(archivo_subido) # Te muestra un reproductor para confirmar qué audio subiste
        audio_para_procesar = archivo_subido.getvalue()
        tipo_de_archivo = archivo_subido.type
else:
    # El micrófono que ya tenías
    audio_grabado = st.audio_input("Haz clic en el micrófono para empezar a grabar:")
    if audio_grabado is not None:
        audio_para_procesar = audio_grabado.getvalue()
        tipo_de_archivo = "audio/wav"

st.divider()

# 4. EL BOTÓN MÁGICO
if st.button("Generar Nota Clínica"):
    if audio_para_procesar is not None:
        with st.spinner("Escuchando el audio, analizando y redactando la nota... ⏳"):
            try:
                datos_audio = {
                    "mime_type": tipo_de_archivo,
                    "data": audio_para_procesar
                }
                
                # Tu instrucción médica (puedes modificar este texto después si quieres cambiar el formato)
                instruccion = """
                Eres un médico especialista experto. Escucha esta grabación de voz con los apuntes rápidos de una consulta médica.
                Extrae la información y estructúrala en una nota clínica profesional usando el formato SOAP (Subjetivo, Objetivo, Análisis, Plan).
                Usa terminología médica formal. No inventes datos que no se mencionen en el audio.
                """
                
                respuesta = modelo.generate_content([instruccion, datos_audio])
                
                st.success("¡Nota generada con éxito!")
                st.markdown("### Resultado:")
                st.write(respuesta.text)
                
                st.warning("⚠️ **Recordatorio Profesional:** La IA no toma decisiones clínicas. Por favor, revisa esta nota antes de anexarla a tu expediente oficial.")
            except Exception as e:
                st.error("Hubo un error al procesar el audio. Verifica tu conexión a internet o el formato del archivo.")
    else:
        st.warning("⚠️ Primero sube o graba un audio antes de presionar el botón de generar.")
        