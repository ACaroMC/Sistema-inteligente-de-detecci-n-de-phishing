
import streamlit as st
from urllib.parse import urlparse
import re

st.set_page_config(
    page_title="PhishingGuard AI",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ PhishingGuard AI")
st.subheader("Sistema inteligente de análisis de phishing")
st.write(
    "Evalúa posibles señales de phishing mediante "
    "el análisis del texto del correo y sus URL."
)

st.info(
    "Prototipo académico: los resultados son indicativos "
    "y no sustituyen un modelo de Machine Learning validado."
)

correo = st.text_area(
    "Contenido del correo electrónico",
    placeholder="Pega aquí el contenido del correo..."
)

url = st.text_input(
    "URL incluida en el correo",
    placeholder="https://ejemplo.com"
)

if st.button("Analizar correo", type="primary"):

    if not correo.strip() and not url.strip():
        st.warning("Introduce el correo o una URL para analizar.")
    else:
        texto = correo.lower()
        puntuacion = 0
        razones = []

        palabras = [
            "urgente", "contraseña", "verifique",
            "suspendida", "premio", "inicie sesión",
            "confirmar cuenta", "inmediatamente"
        ]

        encontradas = [
            palabra for palabra in palabras
            if palabra in texto
        ]

        if encontradas:
            puntuacion += min(30, len(encontradas) * 10)
            razones.append(
                "Palabras sospechosas: "
                + ", ".join(encontradas)
            )

        if re.search(r"https?://", texto):
            razones.append(
                "El cuerpo del correo contiene enlaces."
            )
            puntuacion += 10

        if url.strip():
            direccion = url.strip()
            url_valida = urlparse(
                direccion if "://" in direccion
                else "https://" + direccion
            )

            if not url_valida.hostname:
                puntuacion += 30
                razones.append("La URL no tiene un dominio válido.")

            else:
                dominio = url_valida.hostname.lower()

                if url_valida.scheme != "https":
                    puntuacion += 20
                    razones.append("La URL no utiliza HTTPS.")

                if "@" in direccion:
                    puntuacion += 25
                    razones.append(
                        "La URL contiene el carácter @."
                    )

                if dominio.startswith("xn--") or ".xn--" in dominio:
                    puntuacion += 20
                    razones.append(
                        "El dominio utiliza codificación internacional."
                    )

                if len(direccion) > 100:
                    puntuacion += 10
                    razones.append("La URL es inusualmente larga.")

                if re.search(r"\d+\.\d+\.\d+\.\d+", dominio):
                    puntuacion += 25
                    razones.append(
                        "La dirección utiliza una IP como dominio."
                    )

        puntuacion = min(puntuacion, 100)

        st.divider()
        st.subheader("Resultados del análisis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Puntuación de riesgo", f"{puntuacion}/100")

        with col2:
            if puntuacion >= 50:
                st.error("Riesgo alto")
            elif puntuacion >= 25:
                st.warning("Riesgo medio")
            else:
                st.success("Riesgo bajo según las reglas aplicadas")

        st.progress(puntuacion / 100)

        st.subheader("Indicadores detectados")

        if razones:
            for razon in razones:
                st.write(f"- {razon}")
        else:
            st.write(
                "No se detectaron indicadores sospechosos "
                "según las reglas implementadas."
            )

        st.caption(
            "Una puntuación baja no garantiza que el correo sea seguro. "
            "Esta versión utiliza reglas heurísticas, no un modelo "
            "entrenado de Machine Learning."
        )
