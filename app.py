# =============================================================
#  AL DATO  (nombre provisorio)
#  Test interactivo: ¿cuánto sabés de economía y de tu plata?
#  TP Programación para Economistas — Vera Matzkin
# =============================================================
#  Cómo está organizado este archivo:
#   1. Configuración y estilo
#   2. Datos reales (las respuestas correctas)
#   3. Las preguntas
#   4. Funciones: puntajes, perfil, gráficos, guardar, IA
#   5. Pantallas: inicio → perfil → preguntas → resultado
# =============================================================

import random
import urllib.parse
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

NOMBRE_APP = "Al Dato"   # ← cambiar acá el nombre cuando lo elijas

# -------------------------------------------------------------
# 1. CONFIGURACIÓN Y ESTILO
# -------------------------------------------------------------
st.set_page_config(page_title=NOMBRE_APP, page_icon="📊", layout="centered")

AZUL, DORADO, VERDE, ROJO, GRIS = "#1F3A5F", "#C9A227", "#2E7D5B", "#B5473A", "#8A8A8A"

st.markdown(
    f"""
    <style>
    .block-container {{max-width: 720px; padding-top: 4rem;}}
    h1, h2, h3 {{letter-spacing: -0.02em;}}
    .etiqueta {{font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: #8A6D3B; font-weight: 700;}}
    .pregunta {{font-size: 1.4rem; font-weight: 700; line-height: 1.3; margin: 0.3rem 0 0.6rem 0;}}
    .ayuda {{color: #6B6B6B; font-size: 0.95rem;}}
    .grande {{font-size: 3.2rem; font-weight: 800; line-height: 1;}}
    .veredicto-ok {{color: {VERDE}; font-size: 1.3rem; font-weight: 800;}}
    .veredicto-mal {{color: {ROJO}; font-size: 1.3rem; font-weight: 800;}}
    .dato {{border-left: 4px solid {DORADO}; padding: 0.3rem 0 0.3rem 0.9rem; margin: 0.6rem 0 1rem 0;}}
    .perfil {{font-size: 2rem; font-weight: 800; margin: 0.2rem 0;}}
    div.stButton > button, div.stFormSubmitButton > button, a[data-testid="stLinkButton"] {{border-radius: 999px; font-weight: 700;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 2. DATOS REALES — verificar en las fuentes antes de entregar
# -------------------------------------------------------------
DATOS_REALES = {
    "pobreza":      {"valor": 32.3, "fuente": "INDEC, 1er semestre 2026"},
    "inflacion":    {"valor": 33.4, "fuente": "INDEC, interanual a septiembre 2026"},
    "desempleo":    {"valor": 7.9,  "fuente": "INDEC, 2do trimestre 2026"},
    "informalidad": {"valor": 45.0, "fuente": "INDEC, 2do trimestre 2026"},
    "extranjeros":  {"valor": 4.2,  "fuente": "Censo 2022"},
    "jubilaciones": {"valor": 42.6, "fuente": "IIEP-UBA con datos del Ministerio de Economía, julio 2026"},
    "empleo_nacion": {"valor": 21.0, "fuente": "Chequeado con datos oficiales, 2023"},
    "rinde_bono":   {"valor": 5.0,  "fuente": "Bono del Tesoro de EE.UU. a 10 años, octubre 2026"},
}

# Error a partir del cual la pregunta suma 0 puntos (en puntos porcentuales).
# Ejemplo: en pobreza, errarle por 0 = 100% del puntaje; por 12,5 = 50%; por 25 o más = 0%.
ERROR_MAXIMO = {"pobreza": 25, "inflacion": 30, "desempleo": 15, "informalidad": 30,
                "extranjeros": 15, "jubilaciones": 30, "empleo_nacion": 30, "rinde_bono": 10}

# -------------------------------------------------------------
# 3. LAS PREGUNTAS
#    tipo "numero": estima un %  ·  tipo "opcion": elige una respuesta
#    area "eco": suma a la nota de economía  ·  area "fin": suma a la nota de finanzas
# -------------------------------------------------------------
PREGUNTAS = [
    # ---- Economía argentina ----
    {"id": "pobreza", "area": "eco", "bloque": "El país", "tipo": "numero", "max": 100,
     "texto": "¿Qué porcentaje de las personas en Argentina es pobre?",
     "explica": "Para el INDEC, sos pobre si los ingresos de tu hogar no alcanzan para la canasta básica total: comida, transporte, salud, ropa. Son casi 10 millones de personas."},
    {"id": "inflacion", "area": "eco", "bloque": "El país", "tipo": "numero", "max": 150,
     "texto": "¿Cuánto subieron los precios en los últimos 12 meses?",
     "explica": "Algo que hace un año costaba $1.000, hoy cuesta en promedio $1.334."},
    {"id": "desempleo", "area": "eco", "bloque": "El país", "tipo": "numero", "max": 50,
     "texto": "De las personas que buscan trabajo, ¿qué porcentaje no lo consigue?",
     "explica": "Es la tasa de desocupación. Parece baja porque cuenta como \"ocupado\" a quien trabaja aunque sea pocas horas o en negro."},
    {"id": "informalidad", "area": "eco", "bloque": "El país", "tipo": "numero", "max": 100,
     "texto": "¿Qué porcentaje de los trabajadores es informal (\"en negro\")?",
     "explica": "Casi 1 de cada 2 trabajadores no tiene aportes jubilatorios, obra social ni vacaciones pagas."},
    {"id": "extranjeros", "area": "eco", "bloque": "El país", "tipo": "numero", "max": 50,
     "texto": "¿Qué porcentaje de la población argentina nació en otro país?",
     "explica": "Son 1,9 millones de personas: el 4,2%. Casi todo el mundo cree que son muchas más."},

    # ---- El Estado ----
    {"id": "jubilaciones", "area": "eco", "bloque": "El Estado", "tipo": "numero", "max": 100,
     "texto": "De cada $100 que gasta el gobierno nacional (sin contar intereses de deuda), ¿cuántos van a jubilaciones y pensiones?",
     "explica": "Es, lejos, el gasto más grande del Estado nacional: más de 4 de cada 10 pesos. Sumando otras ayudas sociales, se llega a 6 de cada 10."},
    {"id": "empleo_nacion", "area": "eco", "bloque": "El Estado", "tipo": "numero", "max": 100,
     "texto": "De todos los empleados públicos del país, ¿qué porcentaje trabaja para el gobierno nacional? (el resto trabaja en provincias y municipios)",
     "explica": "Solo 1 de cada 5. De 3,3 millones de empleados públicos, 2 de cada 3 trabajan para las provincias: docentes, policías, médicos de hospitales provinciales."},

    # ---- Finanzas personales ----
    {"id": "cual_segura", "area": "fin", "bloque": "Tu plata", "tipo": "opcion",
     "texto": "¿Cuál es la inversión considerada la más segura del mundo?",
     "opciones": ["Oro", "Dólares en efectivo", "Bonos del Tesoro de EE.UU.", "Plazo fijo", "Bitcoin", "No sé"],
     "correcta": "Bonos del Tesoro de EE.UU.",
     "explica": "El gobierno de EE.UU. es el deudor con menos chances de no pagar. Por eso en finanzas su bono se usa como la inversión \"libre de riesgo\"."},
    {"id": "rinde_bono", "area": "fin", "bloque": "Tu plata", "tipo": "numero", "max": 30,
     "texto": "¿Y cuánto creés que rinde por año ese bono, en dólares?",
     "explica": "Alrededor de 5% anual. Poco, pero casi sin riesgo. Regla de oro: si te prometen mucho más, hay mucho más riesgo."},
    {"id": "costo_oportunidad", "area": "fin", "bloque": "Tu plata", "tipo": "opcion",
     "texto": "Tenés $1.000.000 parado en la cuenta en vez de invertirlo. ¿Qué estás perdiendo?",
     "opciones": ["Nada, la plata sigue ahí", "Lo que podría haber ganado invirtiéndolo",
                  "Solo pierdo si el banco me cobra comisión", "No sé"],
     "correcta": "Lo que podría haber ganado invirtiéndolo",
     "explica": "Eso es el costo de oportunidad: lo que dejás de ganar por elegir una opción y no otra. La plata quieta también te cuesta."},
    {"id": "plazo_fijo", "area": "fin", "bloque": "Tu plata", "tipo": "opcion",
     "texto": "Hoy, ¿un plazo fijo le gana a la inflación?",
     "opciones": ["Sí", "No", "No sé"], "correcta": "No",
     "explica": "Los bancos grandes pagan entre 16% y 21% por año, y la inflación anual es 33,4%. Hoy, con un plazo fijo perdés poder de compra."},
    {"id": "interes", "area": "fin", "bloque": "Tu plata", "tipo": "opcion",
     "texto": "Ponés $100 en una cuenta que paga 2% por año. Sin sacar nada, a los 5 años tenés...",
     "opciones": ["Más de $102", "Exactamente $102", "Menos de $102", "No sé"], "correcta": "Más de $102",
     "explica": "Interés compuesto: cada año ganás intereses también sobre los intereses anteriores. A los 5 años tenés unos $110."},
    {"id": "tasa_real", "area": "fin", "bloque": "Tu plata", "tipo": "opcion",
     "texto": "Tu plata rinde 1% por año y la inflación es 2% por año. Dentro de un año, con esa plata podés comprar...",
     "opciones": ["Más que hoy", "Lo mismo que hoy", "Menos que hoy", "No sé"], "correcta": "Menos que hoy",
     "explica": "Si los precios suben más rápido que tu plata, perdés. Lo que importa es la tasa real: lo que rinde menos la inflación."},
    {"id": "diversificacion", "area": "fin", "bloque": "Tu plata", "tipo": "opcion",
     "texto": "\"Comprar acciones de una sola empresa es más seguro que comprar un fondo con muchas acciones.\"",
     "opciones": ["Verdadero", "Falso", "No sé"], "correcta": "Falso",
     "explica": "No pongas todos los huevos en la misma canasta: si una empresa se hunde, en un fondo con muchas el golpe es chico."},
]

# Los 4 perfiles (nombres provisorios). Se decide por las dos notas: economía y finanzas.
PERFILES = {
    ("alto", "alto"): {"nombre": "La Calculadora", "emoji": "🧮",
                       "texto": "Sabés cómo está el país y lo aplicás a tu plata. Sos de las pocas personas que no se dejan llevar por lo que \"se dice\"."},
    ("alto", "bajo"): {"nombre": "El Opinólogo", "emoji": "🎙️",
                       "texto": "Tenés los datos del país bastante claros, pero a la hora de manejar tu plata, te falta calle. Saber no alcanza: hay que aplicarlo."},
    ("bajo", "alto"): {"nombre": "El Ahorrista Intuitivo", "emoji": "🐷",
                       "texto": "No seguís mucho las noticias, pero con tu plata sos vivo/a. Si te informás un poco más, sos imparable."},
    ("bajo", "bajo"): {"nombre": "El Despistado", "emoji": "🤷",
                       "texto": "Opinás de economía con datos que no son, y tu plata está a la deriva. Tranqui: es lo más común, y se arregla rápido."},
}

# -------------------------------------------------------------
# 4. FUNCIONES
# -------------------------------------------------------------
def secreto(nombre):
    """Lee una clave de los Secrets de Streamlit. Si no existe, devuelve None."""
    try:
        return st.secrets[nombre]
    except Exception:
        return None


def puntaje_pregunta(p, respuesta):
    """Devuelve de 0 a 1 qué tan bien respondió.
    Números: cuanto más cerca del dato real, más puntos. Opciones: 1 si es correcta, 0 si no."""
    if p["tipo"] == "numero":
        error = abs(respuesta - DATOS_REALES[p["id"]]["valor"])
        return max(0.0, 1 - error / ERROR_MAXIMO[p["id"]])
    return 1.0 if respuesta == p["correcta"] else 0.0


def calcular_notas(resp):
    """Nota de economía y nota de finanzas, de 0 a 100."""
    notas = {}
    for area in ["eco", "fin"]:
        preguntas = [p for p in PREGUNTAS if p["area"] == area]
        notas[area] = round(100 * sum(puntaje_pregunta(p, resp[p["id"]]) for p in preguntas) / len(preguntas))
    return notas


def elegir_perfil(notas):
    nivel = lambda n: "alto" if n >= 50 else "bajo"
    return PERFILES[(nivel(notas["eco"]), nivel(notas["fin"]))]


def formato(numero):
    """32.3 → '32,3'  ·  45.0 → '45'"""
    texto = f"{numero:.1f}".replace(".", ",")
    return texto[:-2] if texto.endswith(",0") else texto


def grafico_linea(respuesta, real, maximo):
    """Una línea del 0 al máximo con dos marcas: tu respuesta y el dato real."""
    fig = go.Figure()
    fig.add_shape(type="line", x0=0, x1=maximo, y0=0, y1=0, line=dict(color="#DDD6C8", width=8))
    fig.add_shape(type="line", x0=min(respuesta, real), x1=max(respuesta, real), y0=0, y1=0,
                  line=dict(color=ROJO, width=8))
    fig.add_trace(go.Scatter(x=[respuesta], y=[0], mode="markers+text", text=[f"Vos: {formato(respuesta)}%"],
                             textposition="top center", marker=dict(size=22, color=DORADO, line=dict(color="white", width=2)),
                             textfont=dict(size=15, color="#1F1F1F"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[real], y=[0], mode="markers+text", text=[f"Real: {formato(real)}%"],
                             textposition="bottom center", marker=dict(size=22, color=AZUL, line=dict(color="white", width=2)),
                             textfont=dict(size=15, color=AZUL), hoverinfo="skip"))
    fig.update_layout(height=130, showlegend=False, margin=dict(l=10, r=10, t=0, b=0),
                      xaxis=dict(range=[-maximo * 0.06, maximo * 1.06], showgrid=False, zeroline=False,
                                 tickvals=[0, maximo / 2, maximo], ticktext=["0%", f"{maximo // 2}%", f"{maximo}%"]),
                      yaxis=dict(range=[-1.2, 1.2], visible=False), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def grafico_cuadrado(notas):
    """El cuadrado tipo Political Compass: finanzas (horizontal) × economía (vertical), con tu punto."""
    fig = go.Figure()
    zonas = [(0, 50, 50, 100, "#E9EEF5", ("alto", "bajo")), (50, 100, 50, 100, "#E6F2EC", ("alto", "alto")),
             (0, 50, 0, 50, "#F6E9E7", ("bajo", "bajo")), (50, 100, 0, 50, "#FBF3DE", ("bajo", "alto"))]
    for x0, x1, y0, y1, color, clave in zonas:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1, fillcolor=color, line=dict(width=0), layer="below")
        perfil = PERFILES[clave]
        fig.add_annotation(x=x0 + 3, y=y1 - 3, xanchor="left", yanchor="top", align="left",
                           text=f"{perfil['emoji']} {perfil['nombre']}", showarrow=False,
                           font=dict(size=12, color="#5A5A5A"))
    fig.add_shape(type="line", x0=50, x1=50, y0=0, y1=100, line=dict(color="#BBB", width=1))
    fig.add_shape(type="line", x0=0, x1=100, y0=50, y1=50, line=dict(color="#BBB", width=1))
    fig.add_trace(go.Scatter(x=[notas["fin"]], y=[notas["eco"]], mode="markers+text", text=["  VOS"],
                             textposition="middle right", textfont=dict(size=15, color="#1F1F1F"),
                             marker=dict(size=24, color=ROJO, line=dict(color="white", width=3)), hoverinfo="skip"))
    fig.update_layout(height=430, showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis=dict(range=[0, 100], title="💰 Finanzas personales →", showgrid=False, zeroline=False,
                                 tickvals=[0, 50, 100]),
                      yaxis=dict(range=[0, 100], title="📊 Economía del país →", showgrid=False, zeroline=False,
                                 tickvals=[0, 50, 100], scaleanchor="x"),
                      plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def grafico_barras(resp):
    """Lo que creías vs. el dato real, para todas las preguntas de números."""
    nombres = {"pobreza": "Pobreza", "inflacion": "Inflación", "desempleo": "Desempleo",
               "informalidad": "Informalidad", "extranjeros": "Extranjeros",
               "jubilaciones": "Gasto en jubilaciones", "empleo_nacion": "Empleados de Nación"}
    ids = list(nombres)
    fig = go.Figure()
    fig.add_bar(name="Lo que creías", y=[nombres[i] for i in ids], x=[resp[i] for i in ids],
                orientation="h", marker_color=DORADO)
    fig.add_bar(name="Dato real", y=[nombres[i] for i in ids], x=[DATOS_REALES[i]["valor"] for i in ids],
                orientation="h", marker_color=AZUL)
    fig.update_layout(barmode="group", height=480, margin=dict(l=10, r=10, t=30, b=10),
                      xaxis_title="%", legend=dict(orientation="h", y=1.08), yaxis=dict(autorange="reversed"),
                      plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def guardar_respuesta(fila):
    """Guarda una fila en Google Sheets. Si no está configurado, la guarda en un CSV local (para pruebas)."""
    try:
        if secreto("gcp_service_account") and secreto("sheet_url"):
            import gspread
            cliente = gspread.service_account_from_dict(dict(secreto("gcp_service_account")))
            hoja = cliente.open_by_url(secreto("sheet_url")).sheet1
            if not hoja.row_values(1):              # hoja vacía → escribimos los encabezados
                hoja.append_row(list(fila.keys()))
            hoja.append_row([str(v) for v in fila.values()])
            return
    except Exception:
        pass
    archivo = Path("respuestas.csv")
    pd.DataFrame([fila]).to_csv(archivo, mode="a", header=not archivo.exists(), index=False)


def resumen_para_ia(resp, notas, perfil):
    lineas = [f"Nota de economía: {notas['eco']}/100. Nota de finanzas: {notas['fin']}/100. Perfil: {perfil['nombre']}.",
              f"Edad: {resp['edad']}. Qué hace con la plata que le sobra: {resp['que_hace_con_la_plata']}."]
    for p in PREGUNTAS:
        r = resp[p["id"]]
        if p["tipo"] == "numero":
            lineas.append(f"- {p['texto']} Respondió {r}%. Dato real: {DATOS_REALES[p['id']]['valor']}%.")
        else:
            estado = "BIEN" if r == p["correcta"] else f"MAL (la correcta era: {p['correcta']})"
            lineas.append(f"- {p['texto']} Respondió \"{r}\": {estado}.")
    return "\n".join(lineas)


def devolucion_ia(resp, notas, perfil):
    """Le pide a Claude una devolución personalizada. Si algo falla, devuelve None."""
    clave = secreto("ANTHROPIC_API_KEY")
    if not clave:
        return None
    prompt = f"""Sos una educadora financiera argentina: canchera, directa, con humor, pero nunca cruel.
Una persona que NO estudió economía acaba de hacer un test. Estos son sus resultados:

{resumen_para_ia(resp, notas, perfil)}

Escribile una devolución personalizada en español rioplatense (voseo), de 150 a 200 palabras:
1. Una primera frase con gancho sobre cómo le fue.
2. Sus 2 errores más llamativos y por qué le importan en su vida diaria (usá los datos reales).
3. Dos consejos concretos para su plata, que pueda aplicar esta semana, teniendo en cuenta qué hace hoy con la plata que le sobra.
4. Un cierre que la desafíe a aprender más.
Sin títulos. Podés usar **negrita** para 2 o 3 ideas clave. No recomiendes productos financieros específicos."""
    try:
        import anthropic
        cliente = anthropic.Anthropic(api_key=clave)
        for modelo in [secreto("CLAUDE_MODEL") or "claude-haiku-5-5", "claude-sonnet-5-5"]:
            try:
                mensaje = cliente.messages.create(model=modelo, max_tokens=600,
                                                  messages=[{"role": "user", "content": prompt}])
                return mensaje.content[0].text
            except Exception:
                continue
    except Exception:
        pass
    return None


def devolucion_sin_ia(notas, perfil):
    """Texto de respaldo si la IA no está disponible."""
    flojo = "economía del país" if notas["eco"] < notas["fin"] else "finanzas personales"
    return (f"**{perfil['texto']}** Donde más tenés para mejorar es en **{flojo}**. "
            "Abajo tenés cada pregunta con su explicación: leelas, que en 2 minutos sabés más que la mayoría.")

# -------------------------------------------------------------
# 5. PANTALLAS
# -------------------------------------------------------------
if "paso" not in st.session_state:
    st.session_state.paso = "inicio"     # inicio → perfil → preguntas → resultado
    st.session_state.resp = {}
    st.session_state.i = 0               # número de pregunta actual
    st.session_state.revelar = False     # False: está respondiendo · True: le mostramos si acertó
    st.session_state.guardado = False


def ir_a(paso):
    st.session_state.paso = paso
    st.rerun()


# ---------- INICIO ----------
if st.session_state.paso == "inicio":
    st.markdown("<div class='etiqueta'>14 preguntas · 4 minutos</div>", unsafe_allow_html=True)
    st.title("¿Te animás a ver cuánto sabés de verdad?")
    st.markdown(
        "Todos opinamos de economía: en la mesa del domingo, en el laburo, en redes. "
        "Y todos creemos que manejamos bien nuestra plata.\n\n"
        "**Este test te muestra si es posta.** Vas a ver al instante cuánto le erraste a cada dato, "
        "y al final te decimos qué tipo de persona sos con la economía y con tu plata."
    )
    st.markdown("<div class='ayuda'>Es anónimo. Y no vale googlear: lo que importa es lo que vos creés.</div>",
                unsafe_allow_html=True)
    st.write("")
    if st.button("Arrancar →", type="primary"):
        ir_a("perfil")

# ---------- PERFIL ----------
elif st.session_state.paso == "perfil":
    st.markdown("<div class='etiqueta'>Antes de arrancar</div>", unsafe_allow_html=True)
    st.subheader("Contanos un poco de vos")
    with st.form("perfil"):
        edad = st.number_input("Edad", min_value=14, max_value=100, value=30)
        educacion = st.selectbox("Nivel educativo máximo",
                                 ["Secundario incompleto", "Secundario completo",
                                  "Terciario o universitario en curso", "Terciario o universitario completo", "Posgrado"])
        fuente = st.selectbox("¿Por dónde te informás principalmente?",
                              ["Redes sociales", "TV", "Diarios o portales", "Radio o streaming", "Casi no me informo"])
        plata = st.selectbox("¿Qué hacés con la plata que te sobra a fin de mes?",
                             ["No me sobra", "La gasto", "La dejo en la cuenta o billetera virtual",
                              "Plazo fijo", "Compro dólares", "La invierto (acciones, bonos, FCI, cripto)"])
        if st.form_submit_button("Empezar el test →", type="primary"):
            st.session_state.resp.update({"edad": edad, "educacion": educacion, "fuente_info": fuente,
                                          "que_hace_con_la_plata": plata})
            ir_a("preguntas")

# ---------- PREGUNTAS (una por pantalla, con devolución inmediata) ----------
elif st.session_state.paso == "preguntas":
    i = st.session_state.i
    p = PREGUNTAS[i]
    st.progress((i + 1) / len(PREGUNTAS), text=f"Pregunta {i + 1} de {len(PREGUNTAS)}")
    st.markdown(f"<div class='etiqueta'>{p['bloque']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pregunta'>{p['texto']}</div>", unsafe_allow_html=True)

    if not st.session_state.revelar:
        # --- Fase 1: responder ---
        with st.form(f"q_{p['id']}"):
            if p["tipo"] == "numero":
                # Sin valor inicial a propósito: un número precargado "sopla" la respuesta (sesgo de anclaje)
                valor = st.number_input("Tu estimación (%)", min_value=0.0, max_value=float(p["max"]), value=None,
                                        step=1.0, format="%g", placeholder="Escribí un número")
            else:
                valor = st.radio("Respuesta", p["opciones"], index=None, label_visibility="collapsed")
            if st.form_submit_button("Responder", type="primary"):
                if valor is None:
                    st.error("Respondé para seguir.")
                else:
                    st.session_state.resp[p["id"]] = valor
                    st.session_state.revelar = True
                    st.rerun()
    else:
        # --- Fase 2: le mostramos cómo le fue ---
        r = st.session_state.resp[p["id"]]
        if p["tipo"] == "numero":
            real = DATOS_REALES[p["id"]]["valor"]
            error = abs(r - real)
            if puntaje_pregunta(p, r) >= 0.8:
                st.markdown(f"<div class='veredicto-ok'>¡Al dato! Le erraste por solo {formato(error)} puntos</div>",
                            unsafe_allow_html=True)
            else:
                lado = "Te pasaste" if r > real else "Te quedaste corto/a"
                st.markdown(f"<div class='veredicto-mal'>{lado} por {formato(error)} puntos</div>",
                            unsafe_allow_html=True)
            st.plotly_chart(grafico_linea(r, real, p["max"]), use_container_width=True,
                            config={"displayModeBar": False, "staticPlot": True})
            st.caption(f"Fuente: {DATOS_REALES[p['id']]['fuente']}")
        else:
            if r == p["correcta"]:
                st.markdown("<div class='veredicto-ok'>¡Bien ahí! ✅</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='veredicto-mal'>Nop ❌ La correcta es: {p['correcta']}</div>",
                            unsafe_allow_html=True)
        st.markdown(f"<div class='dato'>{p['explica']}</div>", unsafe_allow_html=True)

        ultima = i == len(PREGUNTAS) - 1
        if st.button("Ver mi resultado →" if ultima else "Siguiente →", type="primary"):
            st.session_state.revelar = False
            if ultima:
                ir_a("resultado")
            st.session_state.i += 1
            st.rerun()

# ---------- RESULTADO ----------
elif st.session_state.paso == "resultado":
    resp = st.session_state.resp
    notas = calcular_notas(resp)
    perfil = elegir_perfil(notas)

    # Guardamos la respuesta UNA sola vez
    if not st.session_state.guardado:
        guardar_respuesta({"fecha": datetime.now().isoformat(timespec="seconds"), **resp,
                           "nota_economia": notas["eco"], "nota_finanzas": notas["fin"],
                           "perfil": perfil["nombre"]})
        st.session_state.guardado = True

    st.markdown("<div class='etiqueta'>Tu resultado</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='perfil'>{perfil['emoji']} Sos {perfil['nombre']}</div>", unsafe_allow_html=True)
    st.markdown(perfil["texto"])

    c1, c2 = st.columns(2)
    c1.markdown(f"📊 Economía del país<div class='grande'>{notas['eco']}<span style='font-size:1.2rem'>/100</span></div>",
                unsafe_allow_html=True)
    c2.markdown(f"💰 Tus finanzas<div class='grande'>{notas['fin']}<span style='font-size:1.2rem'>/100</span></div>",
                unsafe_allow_html=True)

    st.markdown("### Dónde estás parado/a")
    st.plotly_chart(grafico_cuadrado(notas), use_container_width=True,
                    config={"displayModeBar": False, "staticPlot": True})

    st.markdown("### Tu devolución")
    if "devolucion" not in st.session_state:
        with st.spinner("Analizando tus respuestas..."):
            st.session_state.devolucion = devolucion_ia(resp, notas, perfil) or devolucion_sin_ia(notas, perfil)
    with st.container(border=True):
        st.markdown(st.session_state.devolucion)

    st.markdown("### Lo que creías vs. la realidad")
    st.plotly_chart(grafico_barras(resp), use_container_width=True,
                    config={"displayModeBar": False, "staticPlot": True})

    # Compartir por WhatsApp
    st.divider()
    st.markdown("### ¿Te animás a desafiar a alguien?")
    link_app = secreto("APP_URL") or ""
    mensaje = (f"Hice el test \"{NOMBRE_APP}\" y me salió {perfil['emoji']} *{perfil['nombre']}* "
               f"(economía {notas['eco']}/100, finanzas {notas['fin']}/100). ¿A que no me ganás? {link_app}")
    st.link_button("📲 Compartir por WhatsApp", "https://wa.me/?text=" + urllib.parse.quote(mensaje), type="primary")
