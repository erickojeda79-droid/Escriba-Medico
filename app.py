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
st.write("Escriba Inteligente: Endocrinología, Medicina Interna y Clínica de Obesidad.")
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
        with st.spinner("Generando nota clínica integral y avanzada... ⏳"):
            try:
                fecha_hoy = datetime.now().strftime("%d de %B del %Y")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(audio_para_procesar)
                    ruta_temporal = tmp_file.name
                    
                archivo_gemini = genai.upload_file(ruta_temporal, mime_type=tipo_de_archivo)
                
                # INSTRUCCIÓN CLÍNICA MAESTRA (CONSOLIDADA)
                instruccion = f"""
                Eres un médico endocrinólogo e internista experto. La fecha de hoy es {fecha_hoy}.
                Redacta una nota clínica SOAP ultra-compacta, lineal y profesional.
                
                REGLAS DE ORO (PROHIBICIONES):
                1. SÍNTESIS MÉDICA EXTREMA: Elimina anécdotas administrativas o personales.
                2. OMISIÓN SILENCIOSA: Si un dato no se menciona, NO lo mencIONES. PROHIBIDO "No se refiere".
                3. NO INVENTAR: Prohibido inventar signos vitales o laboratorios.
                
                REGLAS DE CÁLCULO Y DEDUCCIÓN (EL CEREBRO):
                - FECHAS: Convierte "ayer", "hace 2 días" a formato DD.MM.AAAA basándote en {fecha_hoy}.
                - DEDUCCIÓN: Levotiroxina = Hipotiroidismo en APP. Gestas/FUM = Paciente Femenina.
                - ANTROPOMETRÍA: Calcula automáticamente el IMC (Peso/Talla^2). Si hay datos, calcula el Estadio EOSS (0-4) y puntaje STOP-BANG para riesgo de SAHOS.
                - LABORATORIOS: Calcula TFG (CKD-EPI 2021), No-HDL (CT-HDL), LDL (Friedewald si TG <400) y FRAX (México). Pon los resultados entre paréntesis junto al valor original.
                - TI-RADS: Calcula automáticamente el nivel ACR TI-RADS según las características dictadas del nódulo.
                
                LÓGICA INSTITUCIONAL (ISSSTE):
                - Si el paciente es del ISSSTE/Instituto: Solo recomienda análogos de GLP-1 si tiene Diabetes Tipo 2. 
                - Si tiene Obesidad sin DM2 en el Instituto: Prioriza el análisis y envío a Cirugía Bariátrica (si IMC >35 o >30 con comorbilidades).
                
                ESTRUCTURA OBLIGATORIA:
                
                1. S: SUBJETIVO (Párrafo continuo): 
                   - Inicio: "Paciente [Femenina/Masculino] de [Edad] años. Motivo: [Motivo]. Enviado por: [Especialidad]."
                   - APP: Enfermedades, tiempo de diagnóstico, fármacos, dosis y apego. Incluye hospitalizaciones.
                   - APNP: Tabaquismo, Etilismo, Ocupación y ALERGIAS (agente y reacción).
                   - AGO (Mujeres): FUM, menarca, G, P, A, C, MPF.
                   - Padecimiento Actual: Resumen conciso de síntomas y evolución.
                
                2. O: OBJETIVO (Párrafo continuo y lineal):
                   - Antropometría: Peso, Talla, IMC calculado, PC.
                   - Signos vitales y EF (Solo mencionados).
                   - Laboratorios y Cálculos: Lineales con fecha DD.MM.AAAA.
                   - Imagen/DEXA/RHP: Lineales con TI-RADS, AJCC-8, TS, DMO y Nadir según aplique.
                
                3. A: ANÁLISIS (Párrafo continuo):
                   - OBESIDAD (AACE 2025): Clasifica ABCD e IMC. Define meta de pérdida de peso en % y beneficios esperados (metabólicos, mecánicos). Evalúa criterios para Cirugía Bariátrica.
                   - DIABETES: Control según ADA 2026 (Metas: Ayuno 70-130, HbA1c <7%). 
                   - TIROIDES/CÁNCER: Estado metabólico. Estadifica según AJCC-8 y ATA 2025 (Respuesta Excelente, Indeterminada, Bioquímica o Estructural Incompleta).
                   - RIESGO CV: Estratifica según AACE 2025 (PREVENT-ASCVD/GLOBO RISK).
                   - SALUD ÓSEA: Riesgo según AACE/Endocrine 2020.
                
                4. P: PLAN (Separado por saltos de línea, SIN viñetas):
                   Estilo de vida: Recomendaciones nutricionales y ejercicio.
                   Tratamiento farmacológico: [Un fármaco por renglón con dosis, vía y horario]. 
                   Seguimiento: Cita, estudios y envíos (Oftalmología, Cirugía Bariátrica, etc.).
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
