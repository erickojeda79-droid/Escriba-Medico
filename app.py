import streamlit as st
import google.generativeai as genai
from datetime import datetime
import tempfile
import os

# CONFIGURACIÓN DE SEGURIDAD
API_KEY = st.secrets["GOOGLE_API_KEY"] 
genai.configure(api_key=API_KEY)
modelo = genai.GenerativeModel('gemini-2.5-flash')

# DISEÑO DE LA INTERFAZ
st.title("Mi Escriba Médico AI 🩺🎙️")
st.write("Sube tu audio o graba en vivo para generar la nota clínica compacta y lineal.")
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

if st.button("Generar Nota Clínica"):
    if audio_para_procesar is not None:
        with st.spinner("Procesando audio y redactando nota lineal... ⏳"):
            try:
                fecha_hoy = datetime.now().strftime("%d de %B del %Y")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(audio_para_procesar)
                    ruta_temporal = tmp_file.name
                    
                archivo_gemini = genai.upload_file(ruta_temporal, mime_type=tipo_de_archivo)
                
                # INSTRUCCIÓN CLÍNICA ULTRA-COMPACTA
                instruccion = f"""
                Eres un médico endocrinólogo e internista experto. La fecha de hoy es {fecha_hoy}.
                Escucha esta grabación y redacta una nota clínica SOAP profesional pero ULTRA-COMPACTA.
                
                REGLAS CRÍTICAS DE FORMATO (PROHIBIDO USAR LISTAS O VIÑETAS):
                
                1. S: SUBJETIVO: 
                   Todo en párrafos continuos. Inicia: "Paciente [Femenina/Masculino] de [Edad] años. Motivo de envío: [Motivo]. Enviado por: [Especialidad]." 
                   Sigue con antecedentes (APP, APNP, AHF, AGO) y padecimiento actual, todo sin viñetas.
                
                2. O: OBJETIVO (TODO EN UN SOLO BLOQUE DE TEXTO):
                   - Exploración física y signos vitales en un solo renglón.
                   - LABORATORIOS Y CÁLCULOS FUSIONADOS: Escribe los laboratorios de forma lineal. Si calculas algo (TFG CKD-EPI 2021, No-HDL, LDL, FRAX pobl. mexicana), ponlo INMEDIATAMENTE después del laboratorio que le dio origen, en el mismo renglón. 
                     Ejemplo: "Laboratorios 19.03.2026: Glucosa 105 mg/dL, Creatinina 0.8 mg/dL (TFG CKD-EPI 2021: 110 mL/min), Colesterol Total 200, HDL 50 (No-HDL: 150), HbA1c 10.9%."
                   - GABINETES E IMAGEN LINEALES: Todo en párrafo continuo, separado por puntos y comas. Incluye USG (LTD, LTI, Itsmo, Nódulos A/B/C con ACR TI-RADS), RM/TAC y RHP.
                   - DEXA: Fecha, TS, DMO y Nadir de corrido.
                
                3. A: ANÁLISIS (Párrafo continuo):
                   Estratifica el riesgo cardiovascular según AACE 2025 (PREVENT-ASCVD/GLOBO RISK) y riesgo de fractura según AACE/Endocrine Society.
                   Estadifica Cáncer de Tiroides (AJCC-8 y ATA 2025 con tipo de respuesta).
                
                4. P: PLAN (Párrafo continuo):
                   Manejo no farmacológico, medicamentos (dosis/vía/recomendación) y estudios solicitados.
                
                ESTRICTAMENTE PROHIBIDO:
                - No uses bolitas (viñetas) ni listas numeradas.
                - No uses el encabezado "Cálculos Automáticos" como sección separada; intégralos en los laboratorios.
                - No dejes espacios en blanco excesivos entre secciones.
                """
                
                respuesta = modelo.generate_content([instruccion, archivo_gemini])
                
                st.success("¡Nota generada con éxito!")
                st.markdown("### Resultado:")
                st.write(respuesta.text)
                
                os.remove(ruta_temporal)
                genai.delete_file(archivo_gemini.name)
                
            except Exception as e:
                st.error(f"Hubo un error al procesar el audio. Detalles: {e}")
    else:
        st.warning("⚠️ Primero sube o graba un audio.")
