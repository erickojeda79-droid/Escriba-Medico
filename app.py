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
st.write("Escriba Inteligente: Endocrinología, Medicina Interna y Obesidad.")
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
        with st.spinner("Redactando nota integral con juicio clínico avanzado... ⏳"):
            try:
                fecha_hoy = datetime.now().strftime("%d de %B del %Y")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(audio_para_procesar)
                    ruta_temporal = tmp_file.name
                    
                archivo_gemini = genai.upload_file(ruta_temporal, mime_type=tipo_de_archivo)
                
                # INSTRUCCIÓN CLÍNICA MAESTRA (INTEGRACIÓN TOTAL DE TODAS LAS GUÍAS)
                instruccion = f"""
                Eres un médico endocrinólogo e internista experto. La fecha de hoy es {fecha_hoy}.
                Redacta una nota clínica SOAP ultra-compacta, lineal y con tono narrativo profesional.
                
                REGLAS DE ORO (FORMATO Y SÍNTESIS):
                1. SÍNTESIS MÉDICA EXTREMA: Filtra anécdotas administrativas o personales.
                2. OMISIÓN SILENCIOSA: Si un dato no se menciona, NO lo menciones. PROHIBIDO "No se refiere".
                3. FECHAS: Convierte "ayer", "hace X días" a formato DD.MM.AAAA basándote en la fecha de hoy ({fecha_hoy}).
                
                S: SUBJETIVO - ORDEN JERÁRQUICO ESTRICTO: 
                   I. APP: Enfermedad + tiempo de diagnóstico + manejo con [Fármaco] [Dosis] [Frecuencia] [Vía] + apego. (PROHIBIDO paréntesis). Incluye hospitalizaciones y cirugías. Si toma Levotiroxina, incluye Hipotiroidismo Primario.
                   II. APNP: Tabaquismo, Etilismo, Ocupación y ALERGIAS (agente y reacción).
                   III. AHF: Solo lo relevante.
                   IV. AGO (Solo mujeres): Menarca, FUM, G, P, A, C, Menopausia. (Si no se dicta, OMITE).
                   V. PA (Padecimiento Actual): Resumen conciso centrado ÚNICAMENTE en la cronología de síntomas actuales y motivo de consulta.
                
                O: OBJETIVO (Lineal): 
                   Antropometría (Peso, Talla, IMC calculado, PC). Signos Vitales (Solo mencionados). 
                   Laboratorios: Lineales con fecha DD.MM.AAAA. Calcula TFG (CKD-EPI 2021), No-HDL, LDL y FRAX (solo si hay DEXA).
                   Imagen/DEXA: Lineal con TI-RADS automático (si aplica).
                
                A: ANÁLISIS (Tono humano y narrativo):
                   - Inicia: "Paciente de la [X] década de la vida con antecedente de...". 
                   - OBESIDAD (AACE 2025): Clasifica ABCD e IMC. Define estadio EOSS (0-4) y riesgo STOP-BANG. Establece metas de pérdida de peso (%) y beneficios.
                   - DIABETES: Control según ADA 2026 (Metas: Ayuno 70-130, HbA1c <7%). 
                   - TIROIDES/CÁNCER: Estado metabólico. Estadifica según AJCC-8 y ATA 2025 (Respuesta Excelente, Indeterminada, Bioquímica o Estructural Incompleta).
                   - RIESGO CV: Estratifica según AACE 2025 (PREVENT-ASCVD/GLOBO RISK). Si hay DM2 + ERC Etapa 3, clasifica como "Riesgo Extremo".
                   - SALUD ÓSEA: Riesgo según AACE/Endocrine 2020. Solo menciona FRAX si hay DEXA.
                
                P: PLAN (Separado por saltos de línea):
                   Estilo de vida. 
                   Tratamiento farmacológico: [Un fármaco por renglón con dosis y horario]. 
                   ADVERTENCIAS: Indica separación de 4h entre Levotiroxina y Cationes (Magnesio/Calcio/Hierro) o Eltrombopag y Lácteos si aplica.
                   Seguimiento: Cita, estudios y envíos (Cirugía Bariátrica, Oftalmología, etc.).
                
                REGLAS DE SEGURIDAD:
                - METFORMINA: Si TFG < 45, limitar dosis a 1000mg/día.
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
