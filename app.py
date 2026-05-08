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
st.write("Sube tu audio o graba en vivo para generar la nota clínica avanzada.")
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
        with st.spinner("Procesando audio con lógica endocrinológica avanzada... ⏳"):
            try:
                fecha_hoy = datetime.now().strftime("%d de %B del %Y")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(audio_para_procesar)
                    ruta_temporal = tmp_file.name
                    
                archivo_gemini = genai.upload_file(ruta_temporal, mime_type=tipo_de_archivo)
                
                # INSTRUCCIÓN CLÍNICA REFINADA
                instruccion = f"""
                Eres un médico endocrinólogo e internista experto en Culiacán. La fecha de hoy es {fecha_hoy}.
                Escucha esta grabación y redacta una nota clínica SOAP profesional y ultra-compacta.
                
                REGLAS DE ORO (PROHIBICIONES ESTRICTAS):
                1. OMISIÓN SILENCIOSA: Si un dato (Signos vitales, USG, DEXA, RHP, Cáncer, FRAX) NO se menciona en el audio, NO lo menciones. PROHIBIDO usar frases como "No se refiere", "No hay datos" o "No cuenta con". Si no está, no existe en la nota.
                2. NO INVENTAR: Está estrictamente prohibido inventar cifras de tensión arterial, peso, frecuencia o cualquier dato clínico.
                3. PROHIBIDO VIÑETAS: No uses listas de bolitas ni números. Usa párrafos continuos.
                
                LÓGICA CLÍNICA:
                - Si el paciente toma LEVOTIROXINA: Incluye "Hipotiroidismo" en sus antecedentes (APP).
                - Lógica de Género: Si se mencionan AGO (FUM, embarazos, gestas), asume que es "Femenina" aunque no se diga el sexo explícitamente.
                
                ESTRUCTURA OBLIGATORIA:
                
                1. S: SUBJETIVO (Párrafo continuo): 
                   - Inicia: "Paciente [Femenina/Masculino] de [Edad] años. Motivo de envío: [Motivo]. Enviado por: [Especialidad]."
                   - APP (Antecedentes Personales Patológicos): Incluye diagnósticos y cirugías con su tiempo de evolución.
                   - APNP (Antecedentes Personales No Patológicos): Especificar Tabaquismo, Etilismo (tiempo y cantidad) y ALERGIAS (especificar a qué sustancia y reacción).
                   - AGO (Antecedentes Gineco-obstétricos): Solo en mujeres. Incluir Menarca, FUM, G, P, A, C y MPF en el orden dictado.
                   - Padecimiento actual: Evolución cronológica de síntomas.
                
                2. O: OBJETIVO (Párrafo continuo):
                   - Exploración física y signos vitales (SOLO los mencionados).
                   - Laboratorios y Cálculos (Lineal): Nombre y valor. Sin interpretaciones ("bajo/alto").
                   - Cálculos automáticos: Si hay datos, calcula TFG (CKD-EPI 2021), No-HDL, LDL y FRAX (México). Pon el cálculo entre paréntesis después del valor base.
                   - Imagen/DEXA/RHP: Solo si se dictan, en formato lineal separado por puntos y comas. USG con medidas de LTD, LTI, Istmo y Nódulos con ACR TI-RADS.
                
                3. A: ANÁLISIS (Párrafo continuo):
                   - Estratifica Riesgo CV (AACE 2025) y riesgo de fractura (AACE/Endocrine 2020).
                   - Diagnósticos integrados (Diabetes ADA 2026, Tiroides/Cáncer ATA 2025 con tipo de respuesta).
                
                4. P: PLAN (Separado por saltos de línea, SIN viñetas):
                   Estilo de vida: [Recomendaciones]
                   Tratamiento farmacológico: [Dosis, vía, frecuencia, recomendaciones de toma]
                   Seguimiento: [Cita y estudios solicitados]
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
