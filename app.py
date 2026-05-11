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
st.write("Escriba Inteligente: Endocrinología, Medicina Interna y Obesidad (Protocolo Avanzado).")
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
        with st.spinner("Generando nota con juicio clínico avanzado y seguridad renal... ⏳"):
            try:
                fecha_hoy = datetime.now().strftime("%d de %B del %Y")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(audio_para_procesar)
                    ruta_temporal = tmp_file.name
                    
                archivo_gemini = genai.upload_file(ruta_temporal, mime_type=tipo_de_archivo)
                
                # INSTRUCCIÓN CLÍNICA MAESTRA (EVOLUCIONADA)
                instruccion = f"""
                Eres un médico endocrinólogo e internista experto. La fecha de hoy es {fecha_hoy}.
                Redacta una nota clínica SOAP ultra-compacta, lineal y con tono profesional humano.
                
                REGLAS DE ORO (PROHIBICIONES):
                1. SÍNTESIS MÉDICA EXTREMA: Elimina anécdotas administrativas.
                2. OMISIÓN SILENCIOSA: Si un dato no se menciona, NO lo menciones.
                3. FRAX CONDICIONAL: Calcula y muestra el FRAX Score ÚNICAMENTE si se menciona una Densitometría Ósea (DEXA) en el audio. Si no hay DEXA, omite el FRAX por completo.
                
                REGLAS DE SEGURIDAD Y CÁLCULO:
                - METFORMINA Y RIÑÓN: Si la TFG calculada (CKD-EPI 2021) es < 45 mL/min, la dosis de Metformina NO debe exceder los 1000 mg diarios. Advierte esto en el análisis.
                - RIESGO EXTREMO (AACE 2025): Clasifica como "Riesgo Extremo" si el paciente tiene DM2 + ERC Etapa 3 o enfermedad cardiovascular establecida.
                - ANTROPOMETRÍA: Calcula IMC, Estadio EOSS (0-4) y puntaje STOP-BANG (Riesgo de SAHOS).
                - TI-RADS: Calcula nivel ACR TI-RADS según características dictadas.
                
                TONO DEL ANÁLISIS (ESTILO HUMANO-CLÍNICO):
                - Evita listas de puntos en el Análisis. Redacta en prosa profesional.
                - Inicia con: "Paciente de la [X] década de la vida con antecedente de [Enfermedades principales]..."
                - Describe la situación actual integrando los hallazgos: "Se encuentra actualmente en descontrol glucémico y metabólico, exacerbado por..."
                - Justifica las decisiones: "Dada la presencia de obesidad grado III y el riesgo cardiovascular extremo, se opta por intensificar con..."
                
                ESTRUCTURA OBLIGATORIA:
                
                1. S: SUBJETIVO (Párrafo continuo): 
                   - Inicio: "Paciente [Femenina/Masculino] de [Edad] años. Motivo: [Motivo]. Enviado por: [Especialidad]."
                   - APP: Enfermedades, fármacos (Levotiroxina = Hipotiroidismo) y apego.
                   - APNP: Tabaquismo, Etilismo, Ocupación y ALERGIAS.
                   - AGO (Mujeres): FUM, menarca, G, P, A, C, MPF.
                
                2. O: OBJETIVO (Párrafo continuo y lineal):
                   - Antropometría: Peso, Talla, IMC, PC.
                   - Laboratorios: Lineales (DD.MM.AAAA). Incluye TFG, No-HDL, LDL y FRAX (solo si hay DEXA).
                   - Imagen/DEXA/RHP: Lineales con TI-RADS.
                
                3. A: ANÁLISIS (Narrativa profesional en prosa):
                   - Clasifica Obesidad (ABCD), metas de pérdida de peso (%) y beneficios.
                   - Analiza Diabetes (ADA 2026), Tiroides/Cáncer (ATA 2025) y Riesgo CV (AACE 2025). 
                   - Si hay ERC, ajusta la lógica de fármacos.
                
                4. P: PLAN (Separado por saltos de línea, SIN viñetas):
                   Estilo de vida: Recomendaciones nutricionales y ejercicio.
                   Tratamiento farmacológico: [Un fármaco por renglón con dosis y horario]. 
                   Seguimiento: Cita, estudios y envíos específicos.
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
