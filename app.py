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
st.write("Sube tu audio o graba en vivo para generar la nota clínica con cálculos automáticos (TFG, Lípidos, FRAX).")
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
        with st.spinner("Procesando audio y realizando cálculos clínicos avanzados... ⏳"):
            try:
                fecha_hoy = datetime.now().strftime("%d de %B del %Y")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(audio_para_procesar)
                    ruta_temporal = tmp_file.name
                    
                archivo_gemini = genai.upload_file(ruta_temporal, mime_type=tipo_de_archivo)
                
                # INSTRUCCIÓN CLÍNICA ENDOCRINOLÓGICA INTEGRAL
                instruccion = f"""
                Eres un médico endocrinólogo e internista experto. La fecha de hoy es {fecha_hoy}.
                Escucha esta grabación y redacta una nota clínica SOAP altamente profesional.
                
                REGLAS DE CÁLCULO Y CONTENIDO:
                
                1. S: SUBJETIVO:
                   - Inicia: Paciente [Femenina/Masculino] de [Edad] años. Motivo de envío: [Motivo]. Enviado por: [Especialidad].
                   - Antecedentes en orden: APP, APNP, AHF y AGO (G, P, A, C, FUM, MPF).
                   - Padecimiento actual: Evolución, síntomas, localización, atenuantes y agravantes.
                
                2. O: OBJETIVO (Formato LINEAL y Continuo):
                   - Exploración física y signos vitales.
                   - Laboratorios con Cálculos Automáticos: 
                     a) Si se menciona CREATININA, calcula la Tasa de Filtrado Glomerular (TFG) usando CKD-EPI 2021 (sin raza).
                     b) Perfil Lipídico: Calcula Colesterol NO-HDL (Total - HDL). Calcula LDL (Friedewald: CT - HDL - TG/5) solo si los datos están presentes y TG < 400. Si el LDL ya fue dictado, prioriza el dictado.
                     c) Anota los resultados lineales por fecha (DD.MM.AAAA).
                   - DEXA y FRAX: Fecha, TS, DMO, segmento, NADIR. Calcula FRAX (Población Mexicana) a 10 años para fractura mayor y cadera.
                   - Imagen/Gabinetes: USG (LTD, LTI, ISTMO, Nódulos A, B, C con ACR TI-RADS), RM/TAC (Simple/Contrastada, medidas, masas, vía visual, Knosp/Hardy), RHP (Folio, médico, descripción). TODO LINEAL.
                
                3. A: ANÁLISIS:
                   - Riesgo Cardiovascular (AACE 2025): Utiliza las herramientas PREVENT-ASCVD o GLOBO RISK para estimar el riesgo. Estratifica al paciente en categorías de riesgo (Bajo, Moderado, Alto, Muy Alto o Extremo) según la Guía AACE 2025 para el manejo farmacológico de dislipidemia.
                   - Diabetes/Tiroides/Cáncer: Control según ADA 2026. Estadifica AJCC-8 y ATA 2025 (Respuesta Excelente, Indeterminada, Bioquímica o Estructural Incompleta).
                   - Salud Ósea: Riesgo según AACE/ACE 2020.
                
                4. P: PLAN:
                   - Manejo NO Farmacológico: Dieta y estilo de vida basados en el riesgo calculado.
                   - Manejo Farmacológico: Sugerencias de tratamiento según las guías AACE 2025 y metas de control.
                   - Medicamentos: Nombre, dosis, vía y recomendaciones.
                   - Envíos y estudios solicitados.
                   
                IMPORTANTE: Si no tienes datos para un cálculo (ej. falta el peso para FRAX o el HDL para No-HDL), NO menciones el cálculo.
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
