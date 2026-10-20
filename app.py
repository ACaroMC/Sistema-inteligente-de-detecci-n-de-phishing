
import re
from urllib.parse import urlparse

import streamlit as st

st.set_page_config(
    page_title="PhishingGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- DISEÑO VISUAL ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(145deg, #071426 0%, #0b1d36 100%);
    color: #e8f1ff;
}
[data-testid="stSidebar"] {
    background: #08172b;
    border-right: 1px solid #1b3557;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}
h1, h2, h3 { color: #f0f6ff !important; }
p, label, .stMarkdown { color: #c8d9ef; }
div[data-testid="stMetric"] {
    background: #102744;
    border: 1px solid #21466e;
    padding: 18px;
    border-radius: 14px;
}
div[data-testid="stMetricLabel"] { color: #9db9dd; }
div[data-testid="stMetricValue"] { color: #ffffff; }
.stTextArea textarea, .stTextInput input {
    background: #091a30 !important;
    color: #f0f6ff !important;
    border: 1px solid #244b76 !important;
    border-radius: 10px !important;
}
.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(90deg, #1478f8, #2865e8);
    color: white;
    border: none;
    border-radius: 10px;
    min-height: 44px;
    font-weight: 600;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    border: 1px solid #6cb4ff;
    color: white;
}
.panel {
    background: rgba(16, 39, 68, 0.88);
    border: 1px solid #21466e;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 16px;
}
.small-muted { color: #8eadd4; font-size: 0.9rem; }
.risk {
    border-radius: 12px;
    padding: 16px;
    font-weight: 600;
    margin: 10px 0;
}
.low { background: #103d37; border: 1px solid #20a783; color: #6ce6bd; }
.medium { background: #493719; border: 1px solid #c9952e; color: #ffd477; }
.high { background: #481f32; border: 1px solid #ed526d; color: #ff8a9a; }
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #1478f8, #ff526d);
}
hr { border-color: #21466e; }
</style>
""", unsafe_allow_html=True)

# ---------- EJEMPLOS ----------
EXAMPLES = {
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
            "los avances del proyecto y las tareas pendientes. Gracias."
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

if "correo" not in st.session_state:
    st.session_state.correo = ""
if "url" not in st.session_state:
    st.session_state.url = ""
if "resultado" not in st.session_state:
    st.session_state.resultado = None

# ---------- FUNCIONES DE ANÁLISIS ----------
PALABRAS = [
    "urgente", "contraseña", "verifique", "suspendida",
    "premio", "inicie sesión", "confirmar cuenta",
    "inmediatamente", "bloqueo", "validar cuenta",
]

def analizar(correo, url):
    texto = correo.lower()
    puntos_texto = 0
    puntos_url = 0
    razones_texto = []
    razones_url = []

    encontradas = [p for p in PALABRAS if p in texto]
    if encontradas:
        puntos_texto += min(50, len(encontradas) * 10)
        razones_texto.append(
            "Palabras de alerta: " + ", ".join(encontradas)
        )

    if re.search(r"https?://", texto):
        puntos_texto += 10
        razones_texto.append("El texto contiene una dirección web.")

    if len(correo) > 0 and len(correo) < 25:
        razones_texto.append(
            "Hay poco contenido para realizar una evaluación completa."
        )

    if url.strip():
        direccion = url.strip()
        candidata = (
            direccion if "://" in direccion
            else "https://" + direccion
        )
        parsed = urlparse(candidata)
        dominio = parsed.hostname or ""

        if not dominio:
            puntos_url += 40
            razones_url.append("No se pudo reconocer el dominio.")
        else:
            if parsed.scheme != "https":
                puntos_url += 20
                razones_url.append("La URL no utiliza HTTPS.")

            if "@" in direccion:
                puntos_url += 25
                razones_url.append("La URL contiene el carácter @.")

            if dominio.startswith("xn--") or ".xn--" in dominio:
                puntos_url += 20
                razones_url.append(
                    "El dominio utiliza codificación internacional."
                )

            if len(direccion) > 100:
                puntos_url += 10
                razones_url.append("La URL es inusualmente larga.")

            if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", dominio):
                puntos_url += 25
                razones_url.append(
                    "La URL utiliza una dirección IP como dominio."
                )

            if dominio.count(".") >= 4:
                puntos_url += 10
                razones_url.append(
                    "El dominio tiene varios subdominios."
                )

    puntos_texto = min(100, puntos_texto)
    puntos_url = min(100, puntos_url)

    # Puntuación demostrativa: combina las señales de ambas fuentes.
    if url.strip():
        total = round(puntos_texto * 0.5 + puntos_url * 0.5)
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

# ---------- BARRA LATERAL ----------
with st.sidebar:
    st.markdown("# 🛡️ PhishingGuard AI")
    st.caption("Ciberseguridad corporativa")
    st.divider()

    pagina = st.radio(
        "NAVEGACIÓN",
        ["Inicio", "Analizar correo", "Acerca del proyecto"],
        label_visibility="visible",
    )

    st.divider()
    st.markdown("### Estado del sistema")
    st.success("Aplicación disponible")
    st.caption("Prototipo académico")
    st.markdown("---")
    st.caption("Más seguridad, menos riesgos.")

# ---------- ENCABEZADO ----------
st.markdown(
    "<div class='small-muted'>PLATAFORMA DE CIBERSEGURIDAD / ANÁLISIS INTELIGENTE</div>",
    unsafe_allow_html=True,
)
st.title("Sistema de detección de phishing")
st.markdown(
    "Evaluación de correos electrónicos corporativos mediante "
    "**análisis del texto y de las URL**."
)

if pagina == "Acerca del proyecto":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🎯 Objetivo del proyecto")
    st.write(
        "Desarrollar un sistema multimodal basado en Machine Learning "
        "para detectar y evaluar el riesgo de phishing en correos "
        "electrónicos corporativos."
    )
    st.write("**Tecnologías:** Python, Streamlit y GitHub.")
    st.write(
        "**Estado actual:** prototipo con reglas heurísticas. "
        "El modelo entrenado de Machine Learning se incorporará "
        "en una siguiente etapa."
    )
    st.markdown("</div>", unsafe_allow_html=True)

elif pagina in ["Inicio", "Analizar correo"]:

    # Métricas iniciales
    resultado = st.session_state.resultado

    c1, c2, c3 = st.columns(3)
    c1.metric("🛡️ Módulos de análisis", "02", "Texto + URL")
    c2.metric(
        "📊 Última puntuación",
        f"{resultado['total']}/100" if resultado else "—",
        resultado["nivel"] if resultado else "Esperando análisis",
    )
    c3.metric(
        "🔎 Señales identificadas",
        str(
            len(resultado["razones_texto"])
            + len(resultado["razones_url"])
        ) if resultado else "—",
        "En último análisis" if resultado else "Sin resultados",
    )

    st.divider()
    entrada, salida = st.columns([1, 1], gap="large")

    with entrada:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("✉️ Analizar correo electrónico")
        st.caption(
            "Introduce el mensaje y, si existe, la URL que deseas evaluar."
        )

        ejemplo = st.selectbox(
            "Cargar un ejemplo de prueba",
            ["Selecciona un ejemplo"] + list(EXAMPLES.keys()),
        )

        if st.button("📥 Cargar ejemplo", key="cargar"):
            if ejemplo in EXAMPLES:
                st.session_state.correo = EXAMPLES[ejemplo]["correo"]
                st.session_state.url = EXAMPLES[ejemplo]["url"]
                st.rerun()
            else:
                st.info("Selecciona un ejemplo de la lista.")

        with st.form("form_analisis"):
            correo = st.text_area(
                "Contenido del correo",
                key="correo",
                height=220,
                placeholder="Pega aquí el asunto y el contenido del correo...",
            )
            url = st.text_input(
                "URL incluida en el correo (opcional)",
                key="url",
                placeholder="https://ejemplo.com",
            )
            enviar = st.form_submit_button(
                "🔍 Analizar riesgo de phishing",
                use_container_width=True,
            )

        if enviar:
            if not correo.strip() and not url.strip():
                st.warning("Introduce un correo o una URL.")
            else:
                st.session_state.resultado = analizar(correo, url)
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with salida:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("📊 Resultados del análisis")

        if resultado is None:
            st.info(
                "Los resultados aparecerán aquí después de analizar "
                "un correo o una URL."
            )
            st.markdown("#### ¿Qué se evalúa?")
            st.write("📝 Palabras y expresiones sospechosas.")
            st.write("🔗 Características básicas de las URL.")
            st.write("📈 Puntuación heurística combinada.")
        else:
            st.markdown(
                f"<div class='risk {resultado['clase']}'>"
                f"RIESGO {resultado['nivel'].upper()} — "
                f"{resultado['total']}/100"
                "</div>",
                unsafe_allow_html=True,
            )
            st.progress(resultado["total"] / 100)

            a, b = st.columns(2)
            a.metric("Análisis textual", f"{resultado['texto']}/100")
            b.metric("Análisis de URL", f"{resultado['url']}/100")

            st.markdown("#### Indicadores del texto")
            if resultado["razones_texto"]:
                for razon in resultado["razones_texto"]:
                    st.write(f"⚠️ {razon}")
            else:
                st.write("No se detectaron señales textuales definidas.")

            st.markdown("#### Indicadores de la URL")
            if resultado["razones_url"]:
                for razon in resultado["razones_url"]:
                    st.write(f"⚠️ {razon}")
            else:
                st.write(
                    "No se detectaron señales de URL o no se proporcionó una."
                )

            if resultado["nivel"] == "Alto":
                st.error(
                    "Precaución: evita abrir enlaces o compartir "
                    "credenciales hasta verificar el mensaje."
                )
            elif resultado["nivel"] == "Medio":
                st.warning(
                    "Revisa el remitente y verifica el enlace por "
                    "un canal confiable."
                )
            else:
                st.success(
                    "Pocas señales detectadas por las reglas actuales. "
                    "Esto no garantiza que el correo sea seguro."
                )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("## 🧪 Pruebas rápidas")
    st.caption("Selecciona un ejemplo en el panel de análisis para cargarlo.")

    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### 🚨 Correo sospechoso")
        st.caption("Urgencia, solicitud de contraseña y enlace.")
        st.markdown("</div>", unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### ✉️ Correo informativo")
        st.caption("Mensaje de reunión sin URL.")
        st.markdown("</div>", unsafe_allow_html=True)
    with p3:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### 🔗 Análisis de URL")
        st.caption("Dirección IP y conexión HTTP.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.caption(
        "Aviso académico: las puntuaciones son heurísticas de demostración, "
        "no probabilidades calibradas. Esta versión no utiliza un modelo "
        "entrenado y no verifica la reputación real de los dominios."
    )
