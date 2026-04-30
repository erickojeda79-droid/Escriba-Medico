import streamlit as st
import google.generativeai as genai
from datetime import datetime
import tempfile
import os

# 1. LA LLAVE MÁGICA: Ahora la busca en la caja fuerte de Streamlit
API_KEY = st.secrets["GOOGLE_API_KEY"] 
genai.configure(api_key=API_KEY)
modelo = genai.GenerativeModel('gemini-2.5-flash')

# 2. DISEÑO DEL CONSULTORIO
st.title("Mi Escriba Médico AI 🩺🎙️")
st.write("Sube una nota de voz de tu celular o graba en vivo para crear tu nota clínica.")
st.divider()

modo = st.radio("¿Cómo quieres ingresar el audio?", ["Subir archivo desde mi computadora", "Grabar en vivo con el micrófono"])

audio_para_procesar = None
tipo_de_archivo = "audio/wav"
extension = ".wav"

if modo == "Subir archivo desde mi computadora":
    archivo_subido = st.file_uploader("Selecciona tu archivo de audio", type=['mp3', 'wav', 'm4a', 'ogg'])
    if archivo_subido is not None:
        st.audio(archivo_subido)
        audio_para_procesar = archivo_subido.getvalue()
        tipo_de_archivo = archivo_subido.type
        extension = "." + archivo_subido.name.split('.')[-1]
else:
    audio_grabado = st.audio_input("Haz clic en el micrófono para empezar a grabar:")
    if audio_grabado is not None:
        audio_para_procesar = audio_grabado.getvalue()
        tipo_de_archivo = "audio/wav"
        extension = ".wav"

st.divider()

# 3. EL BOTÓN MÁGICO ACTUALIZADO PARA AUDIOS LARGOS
if st.button("Generar Nota Clínica"):
    if audio_para_procesar is not None:
        with st.spinner("Subiendo audio al servidor y redactando la nota... Esto puede tomar un minuto para audios largos ⏳"):
            try:
                fecha_hoy = datetime.now().strftime("%d de %B del %Y")
                
                # A) CÓDIGO NUEVO PARA AUDIOS PESADOS: Crear un archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(audio_para_procesar)
                    ruta_temporal = tmp_file.name
                    
                # B) Subir usando el sistema de Archivos Grandes de Google
                archivo_gemini = genai.upload_file(ruta_temporal, mime_type=tipo_de_archivo)
                
                # C) Instrucción clínica
                instruccion = f"""
                Eres un médico especialista experto. La fecha de hoy es {fecha_hoy}.
                Escucha esta grabación de voz con los apuntes de una consulta médica.
                Estructura la información en una nota clínica SOAP (Subjetivo, Objetivo, Análisis, Plan).
                
                Reglas estrictas:
                1. Usa siempre la fecha de hoy ({fecha_hoy}) en el encabezado.
                2. Basa la redacción del "Análisis y Plan" en estándares médicos internacionales y guías actuales.
                3. Usa terminología médica formal. 
                4. NO inventes datos ni medicamentos que no se mencionen en el audio.
                """
                
                # D) Analizar y generar respuesta
                respuesta = modelo.generate_content([instruccion, archivo_gemini])
                
                st.success("¡Nota generada con éxito!")
                st.markdown("### Resultado:")
                st.write(respuesta.text)
                
                # E) Limpiar la memoria borrando el archivo temporal
                os.remove(ruta_temporal)
                genai.delete_file(archivo_gemini.name)
                
            except Exception as e:
                st.error(f"Hubo un error al procesar el audio. Detalles: {e}")
    else:
        st.warning("⚠️ Primero sube o graba un audio.")
