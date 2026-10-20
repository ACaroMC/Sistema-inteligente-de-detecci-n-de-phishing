
import re
from urllib.parse import urlparse

import streamlit as st

# =========================================================
# 1. CONFIGURACIÓN
# =========================================================
st.set_page_config(
    page_title="PhishingGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 2. TEMA PERSONALIZADO
# =========================================================
if "tema_visual" not in st.session_state:
    st.session_state.tema_visual = "Oscuro"

# Paletas completas de la interfaz
TEMAS = {
    "Oscuro": {
        "scheme": "dark",
        "fondo": "#071426",
        "superficie": "#0B1D36",
        "tarjeta": "#102744",
        "borde": "#21466E",
        "texto": "#E8F1FF",
        "secundario": "#A9BED8",
        "campo": "#091A30",
        "boton": "#1769E8",
        "sombra": "rgba(0,0,0,0.18)",
        "bajo": "#103D37",
        "medio": "#493719",
        "alto": "#481F32",
        "texto_bajo": "#6CE6BD",
        "texto_medio": "#FFD477",
        "texto_alto": "#FF8A9A",
    },
    "Claro": {
        "scheme": "light",
        "fondo": "#F3F6FB",
        "superficie": "#FFFFFF",
        "tarjeta": "#FFFFFF",
        "borde": "#D4DEEA",
        "texto": "#172B46",
        "secundario": "#536780",
        "campo": "#FFFFFF",
        "boton": "#1769E8",
        "sombra": "rgba(24,49,82,0.07)",
        "bajo": "#DDF7EC",
        "medio": "#FFF1CF",
        "alto": "#FFE2E7",
        "texto_bajo": "#087657",
        "texto_medio": "#805400",
        "texto_alto": "#B42343",
    },
}

# Selector de apariencia
with st.sidebar:
    st.markdown("## 🛡️ PhishingGuard AI")
    st.caption("Ciberseguridad corporativa")
    st.divider()

    st.radio(
        "🎨 Apariencia",
        ["Oscuro", "Claro"],
        key="tema_visual",
        horizontal=True,
    )

tema = TEMAS[st.session_state.tema_visual]

# =========================================================
# 3. CSS GLOBAL Y RESPONSIVE
# =========================================================
css = """
<style>
:root {
    color-scheme: __SCHEME__;
    --fondo: __FONDO__;
    --superficie: __SUPERFICIE__;
    --tarjeta: __TARJETA__;
    --borde: __BORDE__;
    --texto: __TEXTO__;
    --secundario: __SECUNDARIO__;
    --campo: __CAMPO__;
    --boton: __BOTON__;
    --sombra: __SOMBRA__;
    --bajo: __BAJO__;
    --medio: __MEDIO__;
    --alto: __ALTO__;
    --texto-bajo: __TEXTO_BAJO__;
    --texto-medio: __TEXTO_MEDIO__;
    --texto-alto: __TEXTO_ALTO__;
}

/* Fondo general */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.stApp {
    background: var(--fondo) !important;
    color: var(--texto) !important;
}

.stApp {
    min-width: 0;
}

[data-testid="stMainBlockContainer"],
.block-container {
    width: 100%;
    max-width: 1500px;
    box-sizing: border-box;
    padding: clamp(12px, 3vw, 36px);
}

/* Barra lateral */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {
    background: var(--superficie) !important;
    color: var(--texto) !important;
}

[data-testid="stSidebar"] {
    border-right: 1px solid var(--borde);
}

/* Tipografía */
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp p,
.stApp label,
.stApp li,
.stApp .stMarkdown,
.stApp [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] * {
    color: var(--texto);
}

.stApp [data-testid="stCaptionContainer"] {
    color: var(--secundario) !important;
}

h1 {
    font-size: clamp(1.6rem, 4vw, 2.5rem) !important;
    line-height: 1.2 !important;
    overflow-wrap: anywhere;
}

h2 {
    font-size: clamp(1.25rem, 3vw, 1.8rem) !important;
}

.small-muted {
    color: var(--secundario) !important;
    font-size: 0.88rem;
}

/* Paneles y contenedores */
.panel {
    box-sizing: border-box;
    min-width: 0;
    overflow-wrap: anywhere;
    background: var(--tarjeta);
    color: var(--texto);
    border: 1px solid var(--borde);
    border-radius: 16px;
    padding: clamp(12px, 2vw, 22px);
    margin-bottom: 16px;
    box-shadow: 0 4px 16px var(--sombra);
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--tarjeta) !important;
    border-color: var(--borde) !important;
    border-radius: 16px;
}

/* Métricas */
[data-testid="stMetric"],
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: var(--texto) !important;
}

div[data-testid="stMetric"] {
    background: var(--tarjeta) !important;
    border: 1px solid var(--borde) !important;
    border-radius: 14px;
    padding: clamp(10px, 2vw, 18px);
    min-width: 0;
    overflow-wrap: anywhere;
    box-shadow: 0 3px 12px var(--sombra);
}

div[data-testid="stMetricLabel"] {
    color: var(--secundario) !important;
}

div[data-testid="stMetricValue"] {
    color: var(--texto) !important;
    font-size: clamp(1.05rem, 2.5vw, 1.8rem);
}

/* Campos de entrada */
.stTextArea textarea,
.stTextInput input,
.stNumberInput input,
[data-baseweb="input"] > div,
[data-baseweb="textarea"],
[data-baseweb="select"] > div {
    background: var(--campo) !important;
    color: var(--texto) !important;
    border-color: var(--borde) !important;
    border-radius: 10px !important;
    box-sizing: border-box;
    max-width: 100%;
    font-size: 16px !important;
}

/* Placeholder */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: var(--secundario) !important;
    opacity: 0.85;
}

/* Menús desplegables */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="select"] ul,
[data-baseweb="select"] li {
    background: var(--superficie) !important;
    color: var(--texto) !important;
}

/* Botones */
.stButton > button,
.stFormSubmitButton > button {
    background: var(--boton) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--boton) !important;
    border-radius: 10px;
    min-height: 44px;
    width: 100%;
    font-weight: 600;
    white-space: normal;
    overflow-wrap: anywhere;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    filter: brightness(1.12);
    border-color: var(--borde) !important;
}

/* Formularios y controles */
[data-testid="stForm"],
[data-testid="stRadio"],
[data-testid="stCheckbox"],
[data-testid="stSelectbox"],
[data-testid="stTextInput"],
[data-testid="stTextArea"] {
    color: var(--texto) !important;
}

/* Alertas nativas */
[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Barra de progreso */
[data-testid="stProgressBar"] {
    background: var(--borde) !important;
}

/* Separadores */
hr {
    border-color: var(--borde) !important;
}

/* Indicador de riesgo */
.risk {
    border-radius: 12px;
    padding: 16px;
    font-weight: 700;
    margin: 12px 0;
    overflow-wrap: anywhere;
}

.low {
    background: var(--bajo) !important;
    border: 1px solid #20A783;
    color: var(--texto-bajo) !important;
}

.medium {
    background: var(--medio) !important;
    border: 1px solid #C9952E;
    color: var(--texto-medio) !important;
}

.high {
    background: var(--alto) !important;
    border: 1px solid #ED526D;
    color: var(--texto-alto) !important;
}

/* Multimedia */
img, canvas, iframe, video,
[data-testid="stImage"],
[data-testid="stPlotlyChart"] {
    max-width: 100%;
}

/* Responsive para tablets y celulares */
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

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
    }

    div[data-testid="stMetric"] {
        padding: 10px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.78rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.1rem;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 46px;
    }
}

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
"""

reemplazos = {
    "__SCHEME__": tema["scheme"],
    "__FONDO__": tema["fondo"],
    "__SUPERFICIE__": tema["superficie"],
    "__TARJETA__": tema["tarjeta"],
    "__BORDE__": tema["borde"],
    "__TEXTO__": tema["texto"],
    "__SECUNDARIO__": tema["secundario"],
    "__CAMPO__": tema["campo"],
    "__BOTON__": tema["boton"],
    "__SOMBRA__": tema["sombra"],
    "__BAJO__": tema["bajo"],
    "__MEDIO__": tema["medio"],
    "__ALTO__": tema["alto"],
    "__TEXTO_BAJO__": tema["texto_bajo"],
    "__TEXTO_MEDIO__": tema["texto_medio"],
    "__TEXTO_ALTO__": tema["texto_alto"],
}

for clave, valor in reemplazos.items():
    css = css.replace(clave, valor)

st.markdown(css, unsafe_allow_html=True)


# =========================================================
# 4. EJEMPLOS DE PRUEBA
# =========================================================
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
    "Solicitud de contraseña": {
        "correo": (
            "Asunto: Verificación de acceso\n\n"
            "Estimado colaborador, necesitamos validar su cuenta. "
            "Por favor, confirme cuenta y contraseña para continuar "
            "con el acceso a los servicios internos."
        ),
        "url": "",
    },
    "Aviso con HTTPS": {
        "correo": (
            "Asunto: Actualización del calendario\n\n"
            "Hola, el calendario de actividades del equipo "
            "se encuentra actualizado. Puedes consultar los "
            "detalles en el enlace compartido."
        ),
        "url": "https://example.com/calendario",
    },
}


# =========================================================
# 5. MOTOR DE ANÁLISIS HEURÍSTICO
# =========================================================
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

    # Análisis de texto
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

    if correo.strip() and len(correo.strip()) < 25:
        razones_texto.append(
            "El mensaje es corto; hay poca información para evaluarlo."
        )

    # Análisis de URL
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

    # Puntuación ilustrativa, no probabilidad calibrada
    if url.strip():
        total = round(
            puntos_texto * 0.6 + puntos_url * 0.8
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


# =========================================================
# 6. ESTADO Y CARGA DE EJEMPLOS
# =========================================================
for clave, valor in {
    "correo": "",
    "url": "",
    "resultado": None,
    "selector_ejemplo": "Selecciona un ejemplo",
}.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor


def cargar_ejemplo():
    nombre = st.session_state.selector_ejemplo

    if nombre in EJEMPLOS:
        st.session_state.correo = EJEMPLOS[nombre]["correo"]
        st.session_state.url = EJEMPLOS[nombre]["url"]
        st.session_state.resultado = None


# =========================================================
# 7. NAVEGACIÓN LATERAL
# =========================================================
with st.sidebar:
    st.divider()

    pagina = st.radio(
        "NAVEGACIÓN",
        [
            "Inicio",
            "Analizar correo",
            "Acerca del proyecto",
        ],
        key="pagina",
    )

    st.divider()

    st.markdown("### Estado del sistema")
    st.success("Aplicación disponible")
    st.caption("Prototipo académico")
    st.markdown("---")
    st.caption("Más seguridad, menos riesgos.")


# =========================================================
# 8. ENCABEZADO
# =========================================================
st.markdown(
    "<div class='small-muted'>"
    "PLATAFORMA DE CIBERSEGURIDAD / ANÁLISIS INTELIGENTE"
    "</div>",
    unsafe_allow_html=True,
)

st.title("Sistema de detección de phishing")

st.markdown(
    "Evaluación de correos electrónicos corporativos mediante "
    "**análisis del texto y de las URL**."
)


# =========================================================
# 9. ACERCA DEL PROYECTO
# =========================================================
if pagina == "Acerca del proyecto":

    with st.container(border=True):
        st.subheader("🎯 Objetivo del proyecto")

        st.write(
            "Sistema multimodal basado en Machine Learning para "
            "la detección y evaluación del riesgo de phishing en "
            "correos electrónicos corporativos mediante análisis "
            "de texto y URL."
        )

        st.markdown("#### Tecnologías")
        st.write("🐍 Python")
        st.write("📊 Streamlit")
        st.write("🐙 GitHub")

        st.markdown("#### Estado actual")
        st.info(
            "Este prototipo utiliza reglas heurísticas. "
            "Todavía no incorpora un modelo de Machine Learning "
            "entrenado ni una evaluación experimental."
        )

# =========================================================
# 10. INICIO Y ANÁLISIS
# =========================================================
else:
    resultado = st.session_state.resultado

    # Indicadores
    c1, c2, c3 = st.columns(3, gap="small")

    with c1:
        st.metric("🛡️ Módulos", "02", "Texto + URL")

    with c2:
        st.metric(
            "📊 Última puntuación",
            f"{resultado['total']}/100" if resultado else "—",
            resultado["nivel"] if resultado else "Sin análisis",
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

    entrada, salida = st.columns([1, 1], gap="medium")

    # -----------------------------------------------------
    # PANEL DE ENTRADA
    # -----------------------------------------------------
    with entrada:
        with st.container(border=True):
            st.subheader("✉️ Analizar correo electrónico")

            st.caption(
                "Introduce el mensaje y, opcionalmente, "
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
                correo_actual = st.session_state.correo
                url_actual = st.session_state.url

                if not correo_actual.strip() and not url_actual.strip():
                    st.warning(
                        "Introduce un correo electrónico o una URL."
                    )
                else:
                    st.session_state.resultado = analizar_correo(
                        correo_actual,
                        url_actual,
                    )
                    st.rerun()

    # -----------------------------------------------------
    # PANEL DE RESULTADOS
    # -----------------------------------------------------
    with salida:
        with st.container(border=True):
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

    # =====================================================
    # 11. TARJETAS DE EJEMPLOS
    # =====================================================
    st.markdown("## 🧪 Ejemplos de prueba")

    st.caption(
        "Selecciona un ejemplo en el panel de análisis "
        "y pulsa 'Cargar ejemplo'."
    )

    p1, p2, p3 = st.columns(3, gap="small")

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
        "de demostración. No incorpora un modelo entrenado de "
        "Machine Learning, no calcula probabilidades calibradas "
        "y no verifica la reputación real de los dominios."
    )
