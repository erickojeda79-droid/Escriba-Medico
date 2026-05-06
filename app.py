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
        with st.spinner("Subiendo audio y redactando la nota... Esto puede tomar un minuto para audios largos ⏳"):
            try:
                fecha_hoy = datetime.now().strftime("%d de %B del %Y")
                
                # CÓDIGO NUEVO PARA AUDIOS PESADOS
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                    tmp_file.write(audio_para_procesar)
                    ruta_temporal = tmp_file.name
                    
                archivo_gemini = genai.upload_file(ruta_temporal, mime_type=tipo_de_archivo)
                
                # INSTRUCCIÓN CLÍNICA AVANZADA Y LINEAL
                instruccion = f"""
                Eres un médico endocrinólogo experto. La fecha de hoy es {fecha_hoy}.
                Escucha esta grabación de voz y redacta una nota clínica SOAP altamente estructurada y profesional.
                
                Aplica ESTRICTAMENTE las siguientes reglas de formato y contenido:
                
                1. S: SUBJETIVO:
                   - Inicia OBLIGATORIAMENTE con el siguiente formato: Paciente [Femenina/Masculino] de [Edad] años. Motivo de envío: [Motivo]. Enviado por: [Médico/Especialidad].
                   - Sigue este orden exacto para los antecedentes: 
                     a) Antecedentes Personales Patológicos (APP).
                     b) Antecedentes Personales No Patológicos (APNP).
                     c) Antecedentes Heredofamiliares (AHF).
                     d) Antecedentes Gineco-obstétricos (AGO): Menarca, FUM, G, P, A, C, MPF (solo en mujeres y si se mencionan).
                   - Padecimiento actual: Describe de forma estructurada las molestias o signos iniciales, tiempo de evolución, localización, características, síntomas acompañantes, atenuantes y agravantes.
                
                2. O: OBJETIVO:
                   - Exploración física y signos vitales.
                   - Laboratorios: Formato ESTRICTAMENTE LINEAL y en párrafo continuo. Agrúpalos por fecha completa (DD.MM.AAAA). REGLA ESTRICTA: NO interpretes los resultados (prohibido usar términos como elevado, disminuido o normal) a menos que el médico haya dictado explícitamente los rangos de referencia, en cuyo caso pon los rangos entre paréntesis junto al valor.
                   - Gabinetes e Imagen y Reportes Histopatológicos: Formato ESTRICTAMENTE LINEAL y en párrafo continuo. NO uses saltos de línea, viñetas ni listas hacia abajo. Escribe todo de corrido, separado solo por puntos y comas.
                     - USG Tiroides/Cuello: Fecha (DD.MM.AAAA) y región. Describir medidas de LTD, LTI e ISTMO. Si hay nódulos, numéralos con letras (ej. Nódulo A). Por cada nódulo detalla: medida, composición, ecogenicidad, forma, márgenes y focos ecogénicos. Calcula y anota el ACR TI-RADS.
                     - TAC/RM: Fecha (DD.MM.AAAA), región, si es simple o contrastada, medidas, masas, afección de vía visual y escalas (Knosp/Hardy).
                     - Reporte Histopatológico (RHP): Abreviarlo como RHP, incluir fecha, folio, médico que realizó y descripción de forma lineal.
                     - Otros estudios (gammagrama, rastreo, etc.): Fecha y descripción dictada.
                
                3. A: ANÁLISIS:
                   - Integra los datos según el motivo de envío y guías clínicas actualizadas.
                   - Diabetes: Define si hay excelente control o descontrol glucémico usando metas ADA 2026. Ajusta a metas de tercera edad o embarazo si aplica.
                   - Tiroides: Define si el paciente está clínica y bioquímicamente eutiroideo, hipotiroideo o hipertiroideo.
                   - Cáncer de Tiroides: Estadifica usando AJCC-8 y guías ATA 2025. Especifica claramente el tipo de respuesta: Excelente, Indeterminada, Bioquímica incompleta o Estructural incompleta.
                   - Otras comorbilidades: Indica si está en metas y sugiere seguimiento o valoración basada en guías si no se especifica.
                
                4. P: PLAN:
                   - Recomendaciones de estilo de vida y alimenticias.
                   - Medicamentos: Nombre, dosis, vía de administración y recomendaciones.
                   - Envíos o interconsultas.
                   - Estudios a solicitar.
                   
                NO inventes datos, medidas ni medicamentos que no se mencionen en el audio. Si falta información para algún apartado, omítelo sin inventar relleno.
                """
                
                respuesta = modelo.generate_content([instruccion, archivo_gemini])
                
                st.success("¡Nota generada con éxito!")
                st.markdown("### Resultado:")
                st.write(respuesta.text)
                
                # Limpiar la memoria
                os.remove(ruta_temporal)
                genai.delete_file(archivo_gemini.name)
                
            except Exception as e:
                st.error(f"Hubo un error al procesar el audio. Detalles: {e}")
    else:
        st.warning("⚠️ Primero sube o graba un audio.")
