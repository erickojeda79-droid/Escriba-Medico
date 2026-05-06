import streamlit as st
import google.generativeai as genai
from datetime import datetime
import tempfile
import os

# LA LLAVE MÁGICA: Ahora la busca en la caja fuerte de Streamlit
API_KEY = st.secrets["GOOGLE_API_KEY"] 
genai.configure(api_key=API_KEY)
modelo = genai.GenerativeModel('gemini-2.5-flash')

# DISEÑO DEL CONSULTORIO
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

if st.button("Generar Nota Clínica"):
    if audio_para_procesar is not None:
        with st.spinner("Subiendo audio y redactando la nota con criterios FRAX y AACE... ⏳"):
            try:
                fecha_hoy = datetime.now().strftime("%d de %B del %Y")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(audio_para_procesar)
                    ruta_temporal = tmp_file.name
                    
                archivo_gemini = genai.upload_file(ruta_temporal, mime_type=tipo_de_archivo)
                
                # INSTRUCCIÓN CLÍNICA ENDOCRINOLÓGICA INTEGRAL
                instruccion = f"""
                Eres un médico endocrinólogo experto. La fecha de hoy es {fecha_hoy}.
                Escucha esta grabación de voz y redacta una nota clínica SOAP profesional.
                
                Aplica ESTRICTAMENTE las siguientes reglas:
                
                1. S: SUBJETIVO:
                   - Formato: Paciente [Femenina/Masculino] de [Edad] años. Motivo de envío: [Motivo]. Enviado por: [Médico/Especialidad].
                   - Antecedentes en orden: APP, APNP, AHF y AGO (G, P, A, C, FUM, MPF si aplica).
                   - Padecimiento actual: Evolución, síntomas, localización, atenuantes y agravantes.
                
                2. O: OBJETIVO (Formato LINEAL y Párrafo Continuo):
                   - Exploración física y signos vitales.
                   - Laboratorios: Lineales, por fecha (DD.MM.AAAA), sin interpretaciones ("elevado/bajo") salvo rangos de referencia dictados.
                   - Densitometría Ósea (DEXA): Fecha, T-Score (TS), Densidad Mineral Ósea (DMO), segmento (ej. L1-L4) y NADIR (TS y DMO de la vértebra más afectada). 
                   - FRAX Score: Calcula la probabilidad a 10 años de fractura mayor y de cadera para población MEXICANA. Usa edad, peso, talla, padres con fractura de cadera y glucocorticoides (si no se mencionan, asume negativo).
                   - Imagen y Gabinetes: USG (LTD, LTI, ITSMO, Nódulos A, B, C con ACR TI-RADS), RM/TAC (Simple/Contrastada, medidas, masas, vía visual, Knosp/Hardy), RHP (Folio, médico, descripción).
                
                3. A: ANÁLISIS:
                   - Diabetes: Control según ADA 2026.
                   - Tiroides y Cáncer: Eutiroideo/Hipotiroideo/Hipertiroideo. Estadifica AJCC-8 y ATA 2025 (Respuesta Excelente, Indeterminada, Bioquímica o Estructural Incompleta).
                   - Osteoporosis/Salud Ósea: Si se menciona densitometría, usa guías AACE/ACE 2020 y Endocrine Society 2020. Define si el riesgo es "Alto" o "Muy Alto" y justifica la elección farmacológica.
                
                4. P: PLAN:
                   - Estilo de vida y dieta.
                   - Medicamentos: Nombre, dosis, vía y recomendaciones.
                   - Envíos y estudios solicitados para la siguiente cita.
                   
                NO inventes datos. Si no se habla de salud ósea, omite esa sección.
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
