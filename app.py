
import re
from urllib.parse import urlparse

import streamlit as st

# =====================================================
# CONFIGURACIÓN
# =====================================================
st.set_page_config(
    page_title="PhishingGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# ESTILOS: DISEÑO RESPONSIVE
# =====================================================
st.markdown("""
<style>
/* Fondo y colores */
.stApp {
    background: linear-gradient(145deg, #071426 0%, #0b1d36 100%);
    color: #e8f1ff;
}

[data-testid="stSidebar"] {
    background: #08172b;
    border-right: 1px solid #1b3557;
}

[data-testid="stMainBlockContainer"],
.block-container {
    width: 100%;
    max-width: 1500px;
    box-sizing: border-box;
    padding: clamp(12px, 3vw, 36px);
}

/* Tipografía adaptable */
h1, h2, h3 {
    color: #f0f6ff !important;
    overflow-wrap: anywhere;
}

h1 {
    font-size: clamp(1.65rem, 4vw, 2.5rem) !important;
    line-height: 1.2 !important;
}

h2 {
    font-size: clamp(1.3rem, 3vw, 1.8rem) !important;
}

p, label, .stMarkdown {
    color: #c8d9ef;
}

/* Paneles */
.panel {
    background: rgba(16, 39, 68, 0.88);
    border: 1px solid #21466e;
    border-radius: 16px;
    padding: clamp(12px, 2vw, 22px);
    margin-bottom: 16px;
    box-sizing: border-box;
    min-width: 0;
    overflow-wrap: anywhere;
}

.small-muted {
    color: #8eadd4;
    font-size: 0.88rem;
}

/* Indicadores */
div[data-testid="stMetric"] {
    background: #102744;
    border: 1px solid #21466e;
    padding: clamp(10px, 2vw, 18px);
    border-radius: 14px;
    min-width: 0;
    overflow-wrap: anywhere;
}

div[data-testid="stMetricLabel"] {
    color: #9db9dd;
}

div[data-testid="stMetricValue"] {
    color: #ffffff;
    font-size: clamp(1.1rem, 2.5vw, 1.8rem);
}

/* Campos */
.stTextArea textarea,
.stTextInput input {
    background: #091a30 !important;
    color: #f0f6ff !important;
    border: 1px solid #244b76 !important;
    border-radius: 10px !important;
    box-sizing: border-box;
    width: 100%;
    font-size: 16px !important;
}

/* Botones accesibles */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #1478f8, #2865e8);
    color: white;
    border: none;
    border-radius: 10px;
    min-height: 44px;
    font-weight: 600;
    width: 100%;
    white-space: normal;
    overflow-wrap: anywhere;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    border: 1px solid #6cb4ff;
    color: white;
}

/* Indicador de progreso */
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #1478f8, #ff526d);
}

hr {
    border-color: #21466e;
}

/* Resultado de riesgo */
.risk {
    border-radius: 12px;
    padding: 16px;
    font-weight: 700;
    margin: 12px 0;
    overflow-wrap: anywhere;
}

.low {
    background: #103d37;
    border: 1px solid #20a783;
    color: #6ce6bd;
}

.medium {
    background: #493719;
    border: 1px solid #c9952e;
    color: #ffd477;
}

.high {
    background: #481f32;
    border: 1px solid #ed526d;
    color: #ff8a9a;
}

/* Imágenes, tablas y gráficos */
img, canvas, iframe,
[data-testid="stImage"],
[data-testid="stPlotlyChart"] {
    max-width: 100%;
}

/* Tablet y celular */
@media screen and (max-width: 768px) {
    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding: 14px 12px !important;
    }

    .panel {
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 12px;
    }

    div[data-testid="stMetric"] {
        padding: 10px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.78rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.15rem;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 46px;
    }
}

/* Celulares pequeños */
@media screen and (max-width: 480px) {
    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding: 10px 8px !important;
    }

    h1 {
        font-size: 1.5rem !important;
    }

    h2 {
        font-size: 1.25rem !important;
    }

    .panel {
        padding: 11px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# EJEMPLOS DE PRUEBA
# =====================================================
EJEMPLOS = {
    "Correo sospechoso": {
        "correo": (
            "Asunto: URGENTE - Cuenta corporativa suspendida\n\n"
            "Estimado usuario: su cuenta corporativa será suspendida. "
            "Verifique su contraseña e inicie sesión inmediatamente "
            "para evitar el bloqueo. Confirme cuenta ahora."
        ),
        "url": "http://192.0.2.10/login",
    },
    "Correo informativo": {
        "correo": (
            "Asunto: Reunión semanal del equipo\n\n"
            "Buenos días, equipo. Les recuerdo que nuestra reunión "
            "semanal será el jueves a las 10:00 a. m. Revisaremos "
            "los avances del proyecto y las tareas pendientes. "
            "Gracias por su participación."
        ),
        "url": "",
    },
    "URL para evaluar": {
        "correo": (
            "Hola, revisa el siguiente enlace para consultar "
            "la información solicitada."
        ),
        "url": "http://192.0.2.10/verificacion",
    },
}


# =====================================================
# ANÁLISIS HEURÍSTICO DE TEXTO Y URL
# =====================================================
PALABRAS_SOSPECHOSAS = [
    "urgente",
    "contraseña",
    "verifique",
    "suspendida",
    "premio",
    "inicie sesión",
    "confirmar cuenta",
    "inmediatamente",
    "bloqueo",
    "validar cuenta",
]


def analizar_correo(correo, url):
    texto = correo.lower()

    puntos_texto = 0
    puntos_url = 0

    razones_texto = []
    razones_url = []

    # -------- Análisis textual --------
    encontradas = [
        palabra
        for palabra in PALABRAS_SOSPECHOSAS
        if palabra in texto
    ]

    if encontradas:
        puntos_texto += min(50, len(encontradas) * 10)
        razones_texto.append(
            "Palabras de alerta: " + ", ".join(encontradas)
        )

    if re.search(r"https?://", texto):
        puntos_texto += 10
        razones_texto.append(
            "El cuerpo del correo contiene una dirección web."
        )

    if len(correo.strip()) < 25 and correo.strip():
        razones_texto.append(
            "El mensaje es corto; hay poca información para evaluarlo."
        )

    # -------- Análisis de URL --------
    if url.strip():
        direccion = url.strip()

        candidata = (
            direccion
            if "://" in direccion
            else "https://" + direccion
        )

        parsed = urlparse(candidata)
        dominio = parsed.hostname or ""

        if not dominio:
            puntos_url += 40
            razones_url.append(
                "No se pudo reconocer un dominio válido."
            )

        else:
            if parsed.scheme.lower() != "https":
                puntos_url += 20
                razones_url.append(
                    "La dirección no utiliza HTTPS."
                )

            if "@" in direccion:
                puntos_url += 25
                razones_url.append(
                    "La dirección contiene el carácter @."
                )

            if (
                dominio.startswith("xn--")
                or ".xn--" in dominio
            ):
                puntos_url += 20
                razones_url.append(
                    "El dominio utiliza codificación internacional."
                )

            if len(direccion) > 100:
                puntos_url += 10
                razones_url.append(
                    "La URL es inusualmente larga."
                )

            if re.fullmatch(
                r"(?:\d{1,3}\.){3}\d{1,3}",
                dominio,
            ):
                puntos_url += 25
                razones_url.append(
                    "La URL utiliza una dirección IP como dominio."
                )

            if dominio.count(".") >= 4:
                puntos_url += 10
                razones_url.append(
                    "El dominio contiene varios subdominios."
                )

    puntos_texto = min(100, puntos_texto)
    puntos_url = min(100, puntos_url)

    # -------- Puntuación combinada --------
    # Fórmula ilustrativa, pendiente de validación experimental.
    if url.strip():
        total = round(
            puntos_texto * 0.6
            + puntos_url * 0.8
        )
    else:
        total = puntos_texto

    total = min(100, total)

    if total >= 50:
        nivel = "Alto"
        clase = "high"
    elif total >= 25:
        nivel = "Medio"
        clase = "medium"
    else:
        nivel = "Bajo"
        clase = "low"

    return {
        "total": total,
        "nivel": nivel,
        "clase": clase,
        "texto": puntos_texto,
        "url": puntos_url,
        "razones_texto": razones_texto,
        "razones_url": razones_url,
    }


# =====================================================
# ESTADO DE LA APLICACIÓN
# =====================================================
if "correo" not in st.session_state:
    st.session_state.correo = ""

if "url" not in st.session_state:
    st.session_state.url = ""

if "resultado" not in st.session_state:
    st.session_state.resultado = None


def cargar_ejemplo():
    nombre = st.session_state.selector_ejemplo

    if nombre in EJEMPLOS:
        st.session_state.correo = EJEMPLOS[nombre]["correo"]
        st.session_state.url = EJEMPLOS[nombre]["url"]
        st.session_state.resultado = None


# =====================================================
# BARRA LATERAL
# =====================================================
with st.sidebar:
    st.markdown("# 🛡️ PhishingGuard AI")
    st.caption("Ciberseguridad corporativa")
    st.divider()

    pagina = st.radio(
        "NAVEGACIÓN",
        [
            "Inicio",
            "Analizar correo",
            "Acerca del proyecto",
        ],
    )

    st.divider()

    st.markdown("### Estado del sistema")
    st.success("Aplicación disponible")
    st.caption("Prototipo académico")

    st.markdown("---")
    st.caption("Más seguridad, menos riesgos.")


# =====================================================
# ENCABEZADO PRINCIPAL
# =====================================================
st.markdown(
    "<div class='small-muted'>"
    "PLATAFORMA DE CIBERSEGURIDAD / ANÁLISIS INTELIGENTE"
    "</div>",
    unsafe_allow_html=True,
)

st.title("🛡️ Sistema de detección de phishing")

st.markdown(
    "Evaluación de correos electrónicos corporativos mediante "
    "**análisis del texto y de las URL**."
)


# =====================================================
# PÁGINA: ACERCA DEL PROYECTO
# =====================================================
if pagina == "Acerca del proyecto":

    st.markdown(
        "<div class='panel'>",
        unsafe_allow_html=True,
    )

    st.subheader("🎯 Objetivo del proyecto")

    st.write(
        "Sistema multimodal basado en Machine Learning para la "
        "detección y evaluación del riesgo de phishing en correos "
        "electrónicos corporativos mediante análisis de texto y URL."
    )

    st.markdown("#### Tecnologías utilizadas")
    st.write("🐍 Python")
    st.write("📊 Streamlit")
    st.write("🐙 GitHub")

    st.markdown("#### Estado del desarrollo")
    st.info(
        "Esta versión es un prototipo con reglas heurísticas. "
        "El modelo entrenado de Machine Learning se incorporará "
        "en una siguiente etapa."
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =====================================================
# PÁGINAS: INICIO Y ANÁLISIS
# =====================================================
else:

    resultado = st.session_state.resultado

    # Indicadores superiores
    c1, c2, c3 = st.columns(
        [1, 1, 1],
        gap="small",
    )

    with c1:
        st.metric(
            "🛡️ Módulos",
            "02",
            "Texto + URL",
        )

    with c2:
        st.metric(
            "📊 Última puntuación",
            f"{resultado['total']}/100"
            if resultado else "—",
            resultado["nivel"]
            if resultado else "Sin análisis",
        )

    with c3:
        cantidad = (
            len(resultado["razones_texto"])
            + len(resultado["razones_url"])
            if resultado else 0
        )

        st.metric(
            "🔎 Señales detectadas",
            str(cantidad) if resultado else "—",
            "Último análisis" if resultado else "Pendiente",
        )

    st.divider()

    # Columnas principales: Streamlit las adapta según el espacio.
    entrada, salida = st.columns(
        [1, 1],
        gap="medium",
    )

    # -------- PANEL DE ENTRADA --------
    with entrada:

        st.markdown(
            "<div class='panel'>",
            unsafe_allow_html=True,
        )

        st.subheader("✉️ Analizar correo electrónico")

        st.caption(
            "Ingresa el contenido del mensaje y, opcionalmente, "
            "una URL que quieras evaluar."
        )

        st.selectbox(
            "Cargar un ejemplo de prueba",
            [
                "Selecciona un ejemplo",
                *EJEMPLOS.keys(),
            ],
            key="selector_ejemplo",
        )

        st.button(
            "📥 Cargar ejemplo",
            on_click=cargar_ejemplo,
            use_container_width=True,
        )

        with st.form("formulario_analisis"):

            st.text_area(
                "Contenido del correo",
                key="correo",
                height=220,
                placeholder=(
                    "Pega aquí el asunto y el contenido "
                    "del correo electrónico..."
                ),
            )

            st.text_input(
                "URL incluida en el correo (opcional)",
                key="url",
                placeholder="https://ejemplo.com",
            )

            enviar = st.form_submit_button(
                "🔍 Analizar riesgo de phishing",
                use_container_width=True,
            )

        if enviar:
            if (
                not st.session_state.correo.strip()
                and not st.session_state.url.strip()
            ):
                st.warning(
                    "Introduce un correo electrónico o una URL."
                )
            else:
                st.session_state.resultado = analizar_correo(
                    st.session_state.correo,
                    st.session_state.url,
                )
                st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    # -------- PANEL DE RESULTADOS --------
    with salida:

        st.markdown(
            "<div class='panel'>",
            unsafe_allow_html=True,
        )

        st.subheader("📊 Resultados del análisis")

        resultado = st.session_state.resultado

        if resultado is None:

            st.info(
                "Los resultados aparecerán aquí después "
                "de analizar el correo."
            )

            st.markdown("#### ¿Qué se evalúa?")
            st.write("📝 Palabras y expresiones sospechosas.")
            st.write("🔗 Características básicas de las URL.")
            st.write("📈 Puntuación heurística combinada.")

        else:

            st.markdown(
                f"<div class='risk {resultado['clase']}'>"
                f"RIESGO {resultado['nivel'].upper()} · "
                f"{resultado['total']}/100"
                "</div>",
                unsafe_allow_html=True,
            )

            st.progress(resultado["total"] / 100)

            a, b = st.columns(2, gap="small")

            with a:
                st.metric(
                    "Análisis textual",
                    f"{resultado['texto']}/100",
                )

            with b:
                st.metric(
                    "Análisis de URL",
                    f"{resultado['url']}/100",
                )

            st.markdown("#### 📝 Indicadores del texto")

            if resultado["razones_texto"]:
                for razon in resultado["razones_texto"]:
                    st.write(f"⚠️ {razon}")
            else:
                st.write(
                    "No se detectaron señales textuales "
                    "definidas en las reglas actuales."
                )

            st.markdown("#### 🔗 Indicadores de la URL")

            if resultado["razones_url"]:
                for razon in resultado["razones_url"]:
                    st.write(f"⚠️ {razon}")
            else:
                st.write(
                    "No se detectaron señales de URL "
                    "o no se proporcionó una."
                )

            if resultado["nivel"] == "Alto":
                st.error(
                    "Precaución: evita abrir enlaces o compartir "
                    "credenciales hasta verificar el mensaje."
                )

            elif resultado["nivel"] == "Medio":
                st.warning(
                    "Verifica el remitente y la dirección web "
                    "por un canal confiable."
                )

            else:
                st.success(
                    "Las reglas detectaron pocas señales. "
                    "Esto no garantiza que el correo sea seguro."
                )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    # -------- EJEMPLOS VISUALES --------
    st.markdown("## 🧪 Ejemplos de prueba")

    st.caption(
        "Selecciona un ejemplo en el panel de análisis "
        "y pulsa 'Cargar ejemplo'."
    )

    p1, p2, p3 = st.columns(
        [1, 1, 1],
        gap="small",
    )

    with p1:
        st.markdown(
            "<div class='panel'>"
            "<h3>🚨 Correo sospechoso</h3>"
            "<p>Urgencia y solicitud de contraseña.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            "<div class='panel'>"
            "<h3>✉️ Correo informativo</h3>"
            "<p>Mensaje de reunión sin URL.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    with p3:
        st.markdown(
            "<div class='panel'>"
            "<h3>🔗 Evaluación de URL</h3>"
            "<p>Dirección IP y conexión HTTP.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    st.caption(
        "Aviso académico: esta versión utiliza reglas heurísticas "
        "de demostración. No contiene un modelo entrenado de Machine "
        "Learning, no calcula probabilidades calibradas y no verifica "
        "la reputación real de los dominios."
    )
