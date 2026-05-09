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
st.write("Escriba Inteligente para Endocrinología y Medicina Interna.")
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
        with st.spinner("Redactando nota integral y avanzada... ⏳"):
            try:
                fecha_hoy = datetime.now().strftime("%d de %B del %Y")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(audio_para_procesar)
                    ruta_temporal = tmp_file.name
                    
                archivo_gemini = genai.upload_file(ruta_temporal, mime_type=tipo_de_archivo)
                
                # INSTRUCCIÓN CLÍNICA DEFINITIVA (MANTIENE TODO LO CONSTRUIDO)
                instruccion = f"""
                Eres un médico endocrinólogo e internista experto. La fecha de hoy es {fecha_hoy}.
                Escucha esta grabación y redacta una nota clínica SOAP ultra-compacta y profesional.
                
                REGLAS DE ORO (PROHIBICIONES):
                1. SÍNTESIS EXTREMA: Filtra anécdotas, problemas de farmacia, IMSS o referencias. Quédate solo con lo médicamente relevante.
                2. OMISIÓN SILENCIOSA: Si un dato, estudio (DEXA, USG), cálculo (FRAX) o enfermedad NO se menciona en el audio, OMÍTELO POR COMPLETO. PROHIBIDO escribir frases de relleno como "No se cuenta con...", "No refiere...".
                3. NO INVENTAR: No inventes cifras de TA, peso o laboratorios.
                4. TERMINOLOGÍA: Usa "Diabetes Tipo 2" o "DT2".
                
                ESTRUCTURA OBLIGATORIA:
                
                1. S: SUBJETIVO (Párrafo continuo): 
                   - Inicia: "Paciente [Femenina/Masculino] de [Edad] años. Motivo: [Motivo]. Enviado por: [Especialidad]."
                   - APP: Incluye enfermedades, tiempo de diagnóstico, medicamentos actuales con dosis y apego. Menciona hospitalizaciones previas. NO hagas lista aparte de medicamentos. Lógica: Si toma levotiroxina, asume hipotiroidismo.
                   - APNP: Tabaquismo, Etilismo (tiempo/cantidad) y ALERGIAS (sustancia y reacción).
                   - AGO (Solo mujeres): FUM, menarca, G, P, A, C. (Asume femenina si hay FUM o gestas).
                   - Padecimiento Actual: Resumen conciso, síntomas, evolución, mejora/empeora.
                
                2. O: OBJETIVO (Párrafo continuo y lineal):
                   - EF y Signos vitales (Solo los mencionados).
                   - Laboratorios y Cálculos: Formato lineal. Nombre y valor (Sin "alto/bajo"). Calcula TFG (CKD-EPI 2021), No-HDL, LDL y FRAX (México) si hay datos, ponlo entre paréntesis junto al valor.
                   - Imagen/DEXA/RHP: Solo si se dictan. Formato lineal. USG con medidas y ACR TI-RADS. DEXA con TS, DMO, segmento y NADIR. RM/TAC/RHP de corrido.
                
                3. A: ANÁLISIS (Párrafo continuo):
                   - No repitas género/edad literal. Usa "Paciente de la X década...". Integra diagnósticos.
                   - DIABETES Y RIESGO CV: Estado de control según ADA 2026 (Metas: Ayuno 70-130, HbA1c <7%). Estratifica Riesgo CV (AACE 2025 usando PREVENT-ASCVD/GLOBO RISK) y justifica manejo.
                   - TIROIDES Y CÁNCER: Define estado (eutiroideo/hipo/hiper). Estadifica cáncer usando AJCC-8 y guías ATA 2025 (Respuesta Excelente, Indeterminada, Bioquímica o Estructural Incompleta).
                   - SALUD ÓSEA: Riesgo de fractura según guías AACE/Endocrine Society 2020.
                
                4. P: PLAN (Separado por saltos de línea, SIN viñetas):
                   Estilo de vida: Educación, dieta, ejercicio.
                   Tratamiento farmacológico: [Un medicamento por renglón con dosis, vía y horario].
                   Seguimiento: Cita y estudios solicitados.
                """
                
                respuesta = modelo.generate_content([instruccion, archivo_gemini])
                
                st.success("¡Nota generada con éxito!")
                st.markdown("### Resultado:")
                st.write(respuesta.text)
                
                # Limpieza de memoria
                os.remove(ruta_temporal)
                genai.delete_file(archivo_gemini.name)
                
            except Exception as e:
                st.error(f"Hubo un error al procesar el audio. Detalles: {e}")
    else:
        st.warning("⚠️ Primero sube o graba un audio.")
