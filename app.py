# =============================================================
#  AL DATO  (nombre provisorio)
#  Test interactivo: ¿cuánto sabés realmente de economía?
#  TP Programación para Economistas — Vera Matzkin
# =============================================================
#  Cómo está organizado este archivo:
#   1. Configuración y diseño (colores, letras, estilo)
#   2. Datos reales (las respuestas correctas)
#   3. Las preguntas
#   4. Funciones: puntaje, gráficos, guardar respuestas, IA
#   5. Pantallas: inicio → sobre vos → preguntas → jubilación → resultado
# =============================================================

import urllib.parse
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

NOMBRE_APP = "Al Dato"   # ← cambiar acá el nombre cuando lo elijas

# -------------------------------------------------------------
# 1. CONFIGURACIÓN Y DISEÑO — paleta "chocolate y crema"
# -------------------------------------------------------------
st.set_page_config(page_title=NOMBRE_APP, page_icon="🪙", layout="wide", initial_sidebar_state="collapsed")

ESPRESSO, CHOCOLATE, CARAMELO, CREMA, ARENA = "#2B1D14", "#4A2F22", "#C08552", "#F5EDE3", "#E8DCCB"
VERDE, ROJO = "#4E7A55", "#A3472F"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700;9..144,900&family=Inter:wght@400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {background: CREMA; color: ESPRESSO; font-family: 'Inter', sans-serif;}
header[data-testid="stHeader"], #MainMenu, footer {display: none !important;}
.block-container {max-width: 860px; padding: 2.5rem 1.4rem 4rem 1.4rem;}
body {overflow-x: hidden;}
h1, h2, h3, .serif {font-family: 'Fraunces', serif !important; color: ESPRESSO; letter-spacing: -0.02em;}
p, li, label, .stMarkdown {font-size: 1.08rem;}

/* --- Portada a pantalla completa --- */
.hero {background: ESPRESSO; color: CREMA; margin: -3rem calc(-50vw + 50%) 0 calc(-50vw + 50%);
       width: 100vw; min-height: 88vh; display: flex; align-items: center; justify-content: center; padding: 3rem 1.6rem;}
.hero-in {max-width: 860px; width: 100%;}
.hero .kicker {font-size: 0.85rem; letter-spacing: 0.22em; text-transform: uppercase; color: CARAMELO; font-weight: 600;}
.hero h1 {color: CREMA !important; font-size: clamp(2.3rem, 7vw, 4.4rem); line-height: 1.02; font-weight: 900; margin: 0.6rem 0 1.4rem 0; padding: 0;}
.hero p {color: #D9CBBB; font-size: 1.15rem; max-width: 560px; margin: 0.3rem 0;}
.hero .oro {color: CARAMELO; font-family: 'Fraunces', serif; font-style: italic; font-size: 1.45rem; margin-top: 1rem;}
.hero svg {width: 100%; max-width: 560px; height: auto; margin: 1.2rem 0 0.4rem -0.4rem;}
.chips {margin-top: 1.4rem;}
.chip {display: inline-block; border: 1px solid rgba(245,237,227,0.25); color: CREMA; border-radius: 999px;
       padding: 0.35rem 0.95rem; margin: 0.25rem 0.35rem 0.25rem 0; font-size: 0.92rem;}

/* --- Textos de las pantallas --- */
.etiqueta {font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.2em; color: CARAMELO; font-weight: 700; margin-top: 1rem;}
.pregunta {font-family: 'Fraunces', serif; font-size: clamp(1.6rem, 4.6vw, 2.4rem); font-weight: 700; line-height: 1.18; margin: 0.5rem 0 1.4rem 0; color: ESPRESSO;}
.ok {color: VERDE; font-family: 'Fraunces', serif; font-size: 2rem; font-weight: 900;}
.mal {color: ROJO; font-family: 'Fraunces', serif; font-size: 2rem; font-weight: 900;}
.escena {background: ARENA; border-radius: 22px; padding: 1.6rem 1.7rem; margin: 1rem 0 1.6rem 0; line-height: 1.75; font-size: 1.08rem;}
.personas {font-size: 2.1rem; letter-spacing: 0.2rem; line-height: 1.4;}
.puntaje {font-family: 'Fraunces', serif; font-size: clamp(3.5rem, 12vw, 6rem); font-weight: 900; line-height: 1; color: ESPRESSO;}
.seccion {font-family: 'Fraunces', serif; font-size: 1.9rem; font-weight: 700; margin: 2.4rem 0 0.6rem 0; color: ESPRESSO;}
.letra-chica {color: #7A6656; font-size: 0.9rem;}

/* --- Formularios sin "cajita" --- */
[data-testid="stForm"] {border: none !important; padding: 0 !important;}
.stTextInput input, .stNumberInput input, .stTextArea textarea {font-size: 1.2rem !important; background: white !important; border-radius: 14px !important;}
[data-baseweb="select"] > div {background: white !important; border-radius: 14px !important; min-height: 3.1rem;}

/* --- Opciones como tarjetas grandes --- */
div[role="radiogroup"] {gap: 0.7rem;}
div[role="radiogroup"] label {background: white; border: 1.5px solid ARENA; border-radius: 16px; padding: 1rem 1.2rem;
                              width: 100%; margin: 0 !important; transition: all .15s;}
div[role="radiogroup"] label:hover {border-color: CARAMELO;}
div[role="radiogroup"] label:has(input:checked) {border-color: CARAMELO; background: #FBF4EC; box-shadow: 0 0 0 2px CARAMELO inset;}
div[role="radiogroup"] label p {font-size: 1.12rem !important; font-weight: 500;}

/* --- Botones --- */
div.stButton > button, div.stFormSubmitButton > button, a[data-testid^="stBaseLinkButton"] {
    border-radius: 999px; font-weight: 700; min-height: 3.3rem; font-size: 1.05rem;}
div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primaryFormSubmit"], a[data-testid="stBaseLinkButton-primary"] {
    background: CARAMELO !important; color: ESPRESSO !important; border: none !important;}
div.stButton > button[kind="secondary"] {background: transparent; border: 1.5px solid CHOCOLATE; color: CHOCOLATE;}
.st-key-boton_gigante {margin-top: -5.5rem; position: relative; z-index: 2; max-width: 560px;}
.st-key-boton_gigante button {min-height: 4.4rem !important;}
.st-key-boton_gigante button p {font-size: 1.35rem !important; font-weight: 900 !important; letter-spacing: 0.08em;}
[data-testid="stProgress"] > div > div > div > div {background: CARAMELO !important;}
</style>
"""
for nombre, valor in {"ESPRESSO": ESPRESSO, "CHOCOLATE": CHOCOLATE, "CARAMELO": CARAMELO, "CREMA": CREMA,
                      "ARENA": ARENA, "VERDE": VERDE, "ROJO": ROJO}.items():
    CSS = CSS.replace(nombre, valor)
st.markdown(CSS, unsafe_allow_html=True)


# Ilustración de la portada: una bola de monedas que crece cuesta abajo (el interés compuesto)
def moneda(cx, cy, r):
    return (f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{CARAMELO}'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r * 0.78:.1f}' fill='none' stroke='{ESPRESSO}' stroke-opacity='0.35' stroke-width='{max(r * 0.07, 1):.1f}'/>"
            f"<text x='{cx}' y='{cy + r * 0.36:.1f}' text-anchor='middle' font-family='Fraunces, serif' font-weight='900' "
            f"font-size='{r * 1.05:.1f}' fill='{ESPRESSO}' fill-opacity='0.55'>$</text>")


MONEDAS = [(40, 52, 7), (110, 78, 10), (200, 112, 15), (315, 156, 22), (465, 214, 34)]
ILUSTRACION = (
    "<svg viewBox='0 0 560 270' xmlns='http://www.w3.org/2000/svg' role='img' aria-label='Una bola de monedas que crece cuesta abajo'>"
    f"<path d='M0 40 L560 255' stroke='{CREMA}' stroke-opacity='0.25' stroke-width='2' stroke-dasharray='2 8'/>"
    + "".join(f"<path d='M{cx - r - 34} {cy - 6 - r * 0.2} h22' stroke='{CREMA}' stroke-opacity='0.2' stroke-width='2' stroke-linecap='round'/>"
              for cx, cy, r in MONEDAS[1:])
    + "".join(moneda(cx, cy - r * 0.55, r) for cx, cy, r in MONEDAS)
    + "</svg>"
)

# -------------------------------------------------------------
# 2. DATOS REALES — verificar en las fuentes antes de lanzar
# -------------------------------------------------------------
DATOS_REALES = {
    "bono":      {"valor": 5.0,  "fuente": "Bono del Tesoro de EE.UU. a 10 años, octubre 2026"},
    "en_blanco": {"valor": 5.0,  "fuente": "Cálculo con datos del INDEC, 2do trimestre 2026"},
    "impuestos": {"valor": 56.0, "fuente": "Unión Industrial Argentina (UIA), julio 2026"},
}
# Error a partir del cual la pregunta numérica suma 0 puntos
ERROR_MAXIMO = {"bono": 10, "en_blanco": 5, "impuestos": 40}

# -------------------------------------------------------------
# 3. LAS PREGUNTAS — "escena" es lo que aprende la persona después de responder
# -------------------------------------------------------------
PREGUNTAS = [
    {"id": "interes_compuesto", "bloque": "Tu dinero", "tipo": "opcion",
     "texto": "Ponés $100 y cada año te pagan un 10% de lo que tenés. El primer año ganás $10. ¿Y el segundo año?",
     "opciones": ["Gano $10 de nuevo", "Gano un poco más que $10", "Gano menos que $10", "No sé"],
     "correcta": "Gano un poco más que $10",
     "escena": """<b>El secreto: cada año ganás intereses sobre los intereses que ya ganaste.</b><br><br>
⚪ <b>Año 1:</b> ganás $10 → tenés $110<br>
⚪ <b>Año 2:</b> ganás $11 → tenés $121<br>
⚪ <b>Año 3:</b> ganás $12 → tenés $133<br><br>
Tu dinero genera dinero solo, como una bola de nieve que rueda cuesta abajo y cada vuelta junta más nieve. ⛄<br><br>
📈 A los 10 años: <b>$259</b> (no $200). 🚀 A los 30 años: <b>$1.745</b>.<br><br>
<b>Lo que importa no es cuánto ponés, sino cuánto tiempo dejás rodar la bola.</b>"""},

    {"id": "bono", "bloque": "Tu dinero", "tipo": "numero", "max": 30, "paso": 0.5, "prefijo": "", "sufijo": "%",
     "texto": "La inversión considerada la más segura del mundo es el bono del Tesoro de EE.UU. ¿Cuánto creés que paga por año, en dólares?",
     "escena": """📏 <b>Esta es "la vara":</b> lo que podés ganar en dólares <b>casi sin riesgo y sin hacer nada.</b><br><br>
Guardate este número, que lo vas a necesitar en la próxima pregunta. 😉"""},

    {"id": "franquicia", "bloque": "Tu dinero", "tipo": "opcion",
     "texto": "Un amigo te ofrece entrar en su franquicia: por cada USD 100 que ponés, ganás USD 4 por año. ¿Es buen negocio?",
     "opciones": ["Sí, gano dinero todos los años",
                  "No: rinde menos que una inversión sin riesgo, y encima yo pongo el riesgo",
                  "Depende de dónde esté el local", "No sé"],
     "correcta": "No: rinde menos que una inversión sin riesgo, y encima yo pongo el riesgo",
     "escena": """📏 <b>La vara: 5% en dólares, sin riesgo y sin hacer nada.</b> Cualquier negocio tiene que ganarle, y <b>por bastante</b>: vos ponés riesgo, tiempo y laburo.<br><br>
🍔 <b>Franquicia al 4%:</b> arriesgás tu dinero para ganar <i>menos</i> que alguien que no hizo nada.<br>
🏢 <b>Departamento en alquiler:</b> si te deja 3 o 4% en dólares después de gastos, pasa lo mismo.<br><br>
🚀 Siempre preguntate: <b>¿mi negocio le gana a la vara por lo suficiente?</b> Si no, hay que exprimirlo más.<br><br>
Esto se llama <b>costo de oportunidad</b>: lo que dejás de ganar por elegir una opción y no otra.<br><br>
🧮 <b>¿Y cómo lo mido?</b> Ganancia de un año ÷ dinero que pusiste. Ganás $4 por cada $100 → <b>4%</b>."""},

    {"id": "en_blanco", "bloque": "El país", "tipo": "numero", "max": 10, "paso": 1.0, "prefijo": "", "sufijo": " de 10",
     "texto": "De cada 10 personas que trabajan o buscan trabajo en Argentina, ¿cuántas tienen un trabajo en blanco (con aportes y obra social)?",
     "escena": """🔥 <b>Imaginate un asado con 10 personas que trabajan o buscan laburo:</b><br>
<div class='personas'>🧑‍💼🧑‍💼🧑‍💼🧑‍💼🧑‍💼</div><b>5 tienen recibo de sueldo</b><br>
<div class='personas'>🤫🤫🤫🤫</div><b>4 laburan en negro</b><br>
<div class='personas'>🔍</div><b>1 está buscando trabajo</b><br><br>
🤔 Solo 5 de cada 10 aportan… <b>¿Los números cierran?</b> Guardate esta pregunta: la retomamos al final. 😉"""},

    {"id": "impuestos", "bloque": "El país", "tipo": "numero", "max": 100, "paso": 1.0, "prefijo": "$", "sufijo": "",
     "texto": "Una empresa en blanco en Argentina, de cada $100 que gana, ¿cuántos se le van en impuestos?",
     "escena": """🥇 <b>Argentina sale 1ª de 30 países</b> en impuestos sobre las empresas en blanco. Un campeonato que nadie quiere ganar.<br><br>
🤔 <b>Pero en presión fiscal total, somos 12º.</b> ¿Cómo puede ser? Acordate del asado: solo 5 de cada 10 trabajan en blanco.<br>
<b>Pagan pocos, y los que pagan, pagan por todos.</b>"""},
]

# Niveles del termómetro final
NIVELES = [(0, 25, "🌱 Recién arrancás"), (25, 50, "📖 En camino"), (50, 75, "🎯 Bien informado"), (75, 101, "🏆 Crack")]

SUGERENCIAS = ["¿Qué es un plazo fijo UVA?", "¿Cómo empiezo a invertir con poco?", "¿Por qué hay tanta inflación en Argentina?"]

# -------------------------------------------------------------
# 4. FUNCIONES
# -------------------------------------------------------------
def secreto(nombre):
    """Lee una clave de los Secrets de Streamlit. Si no existe, devuelve None."""
    try:
        return st.secrets[nombre]
    except Exception:
        return None


def formato(numero):
    """32.3 → '32,3'  ·  45.0 → '45'"""
    texto = f"{numero:.1f}".replace(".", ",")
    return texto[:-2] if texto.endswith(",0") else texto


def con_unidad(p, valor):
    return f"{p['prefijo']}{formato(valor)}{p['sufijo']}"


def puntaje_pregunta(p, respuesta):
    """De 0 a 1. Números: cuanto más cerca del dato real, más puntos. Opciones: 1 si es correcta."""
    if p["tipo"] == "numero":
        error = abs(respuesta - DATOS_REALES[p["id"]]["valor"])
        return max(0.0, 1 - error / ERROR_MAXIMO[p["id"]])
    return 1.0 if respuesta == p["correcta"] else 0.0


def acerto(p, respuesta):
    """Cuenta como acierto si la opción es correcta o si el número quedó muy cerca (80% del puntaje o más)."""
    return puntaje_pregunta(p, respuesta) >= 0.8


def nivel(puntaje):
    return next(nombre for desde, hasta, nombre in NIVELES if desde <= puntaje < hasta)


def layout_base(fig, alto):
    fig.update_layout(height=alto, margin=dict(l=10, r=10, t=10, b=10), font=dict(family="Inter", color=ESPRESSO, size=14),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def grafico_linea(p, respuesta, real):
    """Una línea del 0 al máximo con dos marcas: tu respuesta y el dato real."""
    maximo = p["max"]
    fig = go.Figure()
    fig.add_shape(type="line", x0=0, x1=maximo, y0=0, y1=0, line=dict(color=ARENA, width=10))
    fig.add_shape(type="line", x0=min(respuesta, real), x1=max(respuesta, real), y0=0, y1=0, line=dict(color=ROJO, width=10))
    fig.add_trace(go.Scatter(x=[respuesta], y=[0], mode="markers+text", text=[f"Vos: {con_unidad(p, respuesta)}"],
                             textposition="top center", marker=dict(size=26, color=CARAMELO, line=dict(color="white", width=3)),
                             textfont=dict(size=16, color=ESPRESSO), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[real], y=[0], mode="markers+text", text=[f"Real: {con_unidad(p, real)}"],
                             textposition="bottom center", marker=dict(size=26, color=CHOCOLATE, line=dict(color="white", width=3)),
                             textfont=dict(size=16, color=CHOCOLATE), hoverinfo="skip"))
    fig.update_layout(showlegend=False, xaxis=dict(range=[-maximo * 0.08, maximo * 1.08], visible=False),
                      yaxis=dict(range=[-1.3, 1.3], visible=False))
    return layout_base(fig, 140)


def grafico_bola_de_nieve():
    """Interés compuesto vs. interés simple: $100 al 10% anual durante 30 años."""
    anios = list(range(0, 31))
    fig = go.Figure()
    fig.add_scatter(x=anios, y=[100 + 10 * a for a in anios], name="Sin bola de nieve", line=dict(color="#B9A797", width=3, dash="dot"))
    fig.add_scatter(x=anios, y=[100 * 1.1 ** a for a in anios], name="Con bola de nieve ⛄", line=dict(color=CARAMELO, width=5))
    fig.update_layout(legend=dict(orientation="h", y=1.15), xaxis=dict(title="Años", gridcolor=ARENA),
                      yaxis=dict(title="$", gridcolor=ARENA))
    return layout_base(fig, 280)


def grafico_termometro(puntaje):
    """Termómetro de 0 a 100 con 4 zonas y tu punto."""
    colores = ["#E9DCCB", "#DCC3A6", "#CFA77E", "#C08552"]
    fig = go.Figure()
    for (desde, hasta, nombre), color in zip(NIVELES, colores):
        fig.add_shape(type="rect", x0=desde, x1=min(hasta, 100), y0=-0.3, y1=0.3, fillcolor=color, line=dict(width=0), layer="below")
        fig.add_annotation(x=(desde + min(hasta, 100)) / 2, y=-0.75, text=nombre.replace(" ", "<br>", 1), showarrow=False,
                           font=dict(size=12, color=CHOCOLATE))
    fig.add_trace(go.Scatter(x=[min(max(puntaje, 4), 96)], y=[0], mode="markers+text", text=["VOS"], cliponaxis=False, textposition="top center",
                             marker=dict(size=34, color=ESPRESSO, line=dict(color="white", width=4)),
                             textfont=dict(size=16, color=ESPRESSO, family="Fraunces"), hoverinfo="skip"))
    fig.update_layout(showlegend=False, xaxis=dict(range=[-6, 106], visible=False), yaxis=dict(range=[-1.2, 1.4], visible=False))
    return layout_base(fig, 200)


def grafico_barras(resp):
    """Lo que creías vs. el dato real (llevado a la misma escala para comparar)."""
    filas = [("Bono del Tesoro<br>(% anual)", resp["bono"], 5.0),
             ("Trabajan en blanco<br>(de cada 100)", resp["en_blanco"] * 10, 50.0),
             ("Impuestos<br>(de cada $100)", resp["impuestos"], 56.0)]
    fig = go.Figure()
    fig.add_bar(name="Lo que creías", y=[f[0] for f in filas], x=[f[1] for f in filas], orientation="h", marker_color=CARAMELO)
    fig.add_bar(name="Dato real", y=[f[0] for f in filas], x=[f[2] for f in filas], orientation="h", marker_color=CHOCOLATE)
    fig.update_layout(barmode="group", legend=dict(orientation="h", y=1.18), yaxis=dict(autorange="reversed"),
                      xaxis=dict(gridcolor=ARENA))
    return layout_base(fig, 320)


def ahorro_a_futuro(por_mes, anios, tasa_anual=0.07):
    """Cuánto juntás ahorrando 'por_mes' durante 'anios', con interés compuesto mensual."""
    r = tasa_anual / 12
    meses = int(anios * 12)
    return por_mes * ((1 + r) ** meses - 1) / r if meses > 0 else 0


def guardar(fila, hoja_nombre="respuestas"):
    """Guarda una fila en Google Sheets (si está configurado) o en un CSV local (para pruebas)."""
    try:
        if secreto("gcp_service_account") and secreto("sheet_url"):
            import gspread
            cliente = gspread.service_account_from_dict(dict(secreto("gcp_service_account")))
            libro = cliente.open_by_url(secreto("sheet_url"))
            try:
                hoja = libro.worksheet(hoja_nombre)
            except Exception:
                hoja = libro.add_worksheet(title=hoja_nombre, rows=1000, cols=40)
            if not hoja.row_values(1):
                hoja.append_row(list(fila.keys()))
            hoja.append_row([str(v) for v in fila.values()])
            return
    except Exception:
        pass
    archivo = Path(f"{hoja_nombre}.csv")
    pd.DataFrame([fila]).to_csv(archivo, mode="a", header=not archivo.exists(), index=False)


def preguntar_a_claude(prompt, max_tokens=600):
    """Le manda un pedido a Claude. Si no está configurado o falla, devuelve None."""
    clave = secreto("ANTHROPIC_API_KEY")
    if not clave:
        return None
    try:
        import anthropic
        cliente = anthropic.Anthropic(api_key=clave)
        for modelo in [secreto("CLAUDE_MODEL") or "claude-haiku-5-5", "claude-sonnet-5-5"]:
            try:
                msj = cliente.messages.create(model=modelo, max_tokens=max_tokens,
                                              messages=[{"role": "user", "content": prompt}])
                return msj.content[0].text
            except Exception:
                continue
    except Exception:
        pass
    return None


def devolucion(resp, puntaje, aciertos):
    lineas = [f"Puntaje: {puntaje}/100 ({aciertos} de {len(PREGUNTAS)} aciertos). Nivel: {nivel(puntaje)}. Edad: {resp['edad']}.",
              f"Qué hace con el dinero que le sobra: {resp['dinero_que_sobra']}. Ahorra para la jubilación: {resp['ahorro_jubilacion']}."]
    for p in PREGUNTAS:
        r = resp[p["id"]]
        if p["tipo"] == "numero":
            lineas.append(f"- {p['texto']} Respondió {r}. Dato real: {DATOS_REALES[p['id']]['valor']}.")
        else:
            lineas.append(f"- {p['texto']} Respondió \"{r}\": {'BIEN' if r == p['correcta'] else 'MAL'}.")
    prompt = f"""Sos una educadora financiera argentina: directa, desafiante y con algo de humor, nunca cruel.
Una persona acaba de hacer un test de economía y finanzas personales. Resultados:
{chr(10).join(lineas)}

Escribile una devolución personalizada en español rioplatense (voseo), de 120 a 170 palabras:
1. Una primera frase con gancho sobre su resultado.
2. Lo más importante que se le escapó y por qué le importa en su vida.
3. Dos acciones concretas para esta semana, según lo que hoy hace con su dinero.
4. Un cierre que la deje con ganas de informarse más.
Sin títulos. Podés usar **negrita** para 2 o 3 ideas clave. Usá "dinero", no "plata".
No recomiendes productos, bancos ni empresas específicas. No opines de política."""
    respuesta = preguntar_a_claude(prompt)
    if respuesta:
        return respuesta
    if puntaje >= 75:
        return "**Estás mejor informado/a que la mayoría.** Igual, repasá dónde fallaste: siempre hay algo más para aprender."
    if puntaje >= 50:
        return "**Vas bien, pero hay datos clave que se te escapan.** Repasá las explicaciones: en 2 minutos sabés más que la mayoría."
    return "**Como a la mayoría, a vos también te faltan datos clave.** La buena noticia: se aprende rápido, y ya diste el primer paso."


def responder_consulta(texto, edad, puntaje):
    guardar({"fecha": datetime.now().isoformat(timespec="seconds"), "edad": edad, "puntaje": puntaje,
             "pregunta": texto}, hoja_nombre="preguntas")
    with st.spinner("Pensando..."):
        respuesta = preguntar_a_claude(
            f"""Respondé esta pregunta de una persona que no estudió economía, en español rioplatense (voseo),
en 80 a 150 palabras, claro y con un ejemplo cotidiano. Usá "dinero", no "plata".
Educativo y neutral: no recomiendes productos, bancos ni empresas específicas, no opines de política,
y si la pregunta pide un consejo personal de inversión, explicá los conceptos y sugerí consultar a un profesional.
Pregunta: {texto}""", max_tokens=400)
    st.session_state.consultas.append((texto, respuesta or
        "¡Gracias! Guardamos tu pregunta. Muy pronto esta sección va a responder al instante. 🙌"))

# -------------------------------------------------------------
# 5. PANTALLAS
# -------------------------------------------------------------
if "paso" not in st.session_state:
    st.session_state.paso = "inicio"     # inicio → sobre_vos → preguntas → jubilacion → resultado
    st.session_state.resp = {}
    st.session_state.i = 0
    st.session_state.revelar = False
    st.session_state.guardado = False
    st.session_state.consultas = []


def ir_a(paso):
    st.session_state.paso = paso
    st.rerun()


# ---------- INICIO ----------
if st.session_state.paso == "inicio":
    st.markdown(f"""<div class='hero'><div class='hero-in'>
        <div class='kicker'>Test de economía</div>
        <h1>¿Te animás a descubrir cuánto sabés realmente de economía?</h1>
        <p>Todos opinamos de economía. Todos creemos que manejamos bien nuestro dinero.</p>
        <p class='oro'>En 4 minutos vas a saber si es cierto.</p>
        <div class='chips'><span class='chip'>⏱ 4 minutos</span><span class='chip'>🔒 Anónimo</span><span class='chip'>🚫 Sin Google</span></div>
        {ILUSTRACION}
        <div style='height:5rem'></div>
        </div></div>""", unsafe_allow_html=True)
    with st.container(key="boton_gigante"):
        if st.button("EMPEZAR EL TEST →", type="primary", use_container_width=True):
            ir_a("sobre_vos")

# ---------- SOBRE VOS ----------
elif st.session_state.paso == "sobre_vos":
    st.markdown("<div class='etiqueta'>Antes de arrancar</div>", unsafe_allow_html=True)
    st.markdown("<div class='pregunta'>Contanos un poco de vos</div>", unsafe_allow_html=True)
    with st.form("sobre_vos"):
        edad = st.number_input("Edad", min_value=14, max_value=100, value=None, placeholder="Escribí tu edad")
        educacion = st.selectbox("Nivel educativo máximo", ["Secundario incompleto", "Secundario completo",
                                 "Terciario o universitario en curso", "Terciario o universitario completo", "Posgrado"],
                                 index=None, placeholder="Elegí una opción")
        fuente = st.selectbox("¿Por dónde te informás principalmente?", ["Redes sociales", "TV", "Diarios o portales",
                              "Radio o streaming", "Casi no me informo"], index=None, placeholder="Elegí una opción")
        sobra = st.selectbox("¿Qué hacés con el dinero que te sobra a fin de mes?",
                             ["No me sobra", "Lo gasto", "Lo dejo en la cuenta o billetera virtual", "Plazo fijo",
                              "Compro dólares", "Lo invierto (acciones, bonos, FCI, cripto)"],
                             index=None, placeholder="Elegí una opción")
        st.write("")
        if st.form_submit_button("Seguir →", type="primary", use_container_width=True):
            if None in (edad, educacion, fuente, sobra):
                st.error("Completá todo para seguir.")
            else:
                st.session_state.resp.update({"edad": edad, "educacion": educacion, "fuente_info": fuente,
                                              "dinero_que_sobra": sobra})
                ir_a("preguntas")

# ---------- PREGUNTAS (una por pantalla, con devolución inmediata) ----------
elif st.session_state.paso == "preguntas":
    i = st.session_state.i
    p = PREGUNTAS[i]
    total = len(PREGUNTAS) + 1
    st.progress((i + 1) / total, text=f"Pregunta {i + 1} de {total}")
    st.markdown(f"<div class='etiqueta'>{p['bloque']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pregunta'>{p['texto']}</div>", unsafe_allow_html=True)

    if not st.session_state.revelar:
        with st.form(f"q_{p['id']}"):
            if p["tipo"] == "numero":
                # Sin valor inicial a propósito: un número precargado "sopla" la respuesta (sesgo de anclaje)
                unidad = (p["prefijo"] + p["sufijo"]).strip()
                valor = st.number_input(f"Tu respuesta ({unidad})", min_value=0.0, max_value=float(p["max"]), value=None,
                                        step=p["paso"], format="%g", placeholder="Escribí un número")
            else:
                valor = st.radio("Respuesta", p["opciones"], index=None, label_visibility="collapsed")
            st.write("")
            if st.form_submit_button("Responder", type="primary", use_container_width=True):
                if valor is None:
                    st.error("Respondé para seguir.")
                else:
                    st.session_state.resp[p["id"]] = valor
                    st.session_state.revelar = True
                    st.rerun()
    else:
        r = st.session_state.resp[p["id"]]
        if p["tipo"] == "numero":
            real = DATOS_REALES[p["id"]]["valor"]
            if acerto(p, r):
                st.markdown("<div class='ok'>¡Muy cerca! ✅</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='mal'>{'Te pasaste' if r > real else 'Te quedaste corto/a'} ❌</div>", unsafe_allow_html=True)
            st.plotly_chart(grafico_linea(p, r, real), use_container_width=True, config={"displayModeBar": False, "staticPlot": True})
            st.markdown(f"<div class='letra-chica'>Fuente: {DATOS_REALES[p['id']]['fuente']}</div>", unsafe_allow_html=True)
        else:
            if r == p["correcta"]:
                st.markdown("<div class='ok'>¡Bien ahí! ✅</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='mal'>Nop ❌</div><p>La correcta es: <b>{p['correcta']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<div class='escena'>{p['escena']}</div>", unsafe_allow_html=True)
        if p["id"] == "interes_compuesto":
            st.plotly_chart(grafico_bola_de_nieve(), use_container_width=True, config={"displayModeBar": False, "staticPlot": True})

        if st.button("Siguiente →", type="primary", use_container_width=True):
            st.session_state.revelar = False
            if i == len(PREGUNTAS) - 1:
                ir_a("jubilacion")
            st.session_state.i += 1
            st.rerun()

# ---------- ÚLTIMA PREGUNTA ----------
elif st.session_state.paso == "jubilacion":
    total = len(PREGUNTAS) + 1
    st.progress(1.0, text=f"Pregunta {total} de {total}")
    st.markdown("<div class='etiqueta'>Última</div>", unsafe_allow_html=True)
    st.markdown("<div class='pregunta'>¿Estás ahorrando por tu cuenta para cuando te jubiles?</div>", unsafe_allow_html=True)
    with st.form("jubilacion"):
        valor = st.radio("Respuesta", ["Sí", "Todavía no, pero quiero", "No lo había pensado"], index=None,
                         label_visibility="collapsed")
        st.write("")
        if st.form_submit_button("Ver mi resultado →", type="primary", use_container_width=True):
            if valor is None:
                st.error("Respondé para seguir.")
            else:
                st.session_state.resp["ahorro_jubilacion"] = valor
                ir_a("resultado")

# ---------- RESULTADO ----------
elif st.session_state.paso == "resultado":
    resp = st.session_state.resp
    aciertos = sum(acerto(p, resp[p["id"]]) for p in PREGUNTAS)
    # El puntaje (0 a 100) sale de los aciertos, así el termómetro y el "X de 5" siempre coinciden
    puntaje = round(100 * aciertos / len(PREGUNTAS))

    if not st.session_state.guardado:
        guardar({"fecha": datetime.now().isoformat(timespec="seconds"), **resp, "puntaje": puntaje, "aciertos": aciertos})
        st.session_state.guardado = True

    st.markdown("<div class='etiqueta'>Tu resultado</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='puntaje'>{aciertos} de {len(PREGUNTAS)}</div>", unsafe_allow_html=True)
    st.markdown("<div class='letra-chica'>respuestas acertadas</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pregunta' style='margin-top:0.4rem'>{nivel(puntaje)}</div>", unsafe_allow_html=True)
    st.plotly_chart(grafico_termometro(puntaje), use_container_width=True, config={"displayModeBar": False, "staticPlot": True})

    if "devolucion" not in st.session_state:
        with st.spinner("Analizando tus respuestas..."):
            st.session_state.devolucion = devolucion(resp, puntaje, aciertos)
    st.markdown("<div class='seccion'>Tu devolución</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(st.session_state.devolucion)

    st.markdown("<div class='seccion'>Lo que creías vs. la realidad</div>", unsafe_allow_html=True)
    st.plotly_chart(grafico_barras(resp), use_container_width=True, config={"displayModeBar": False, "staticPlot": True})

    # ----- Cierre: los números no cierran + calculadora de jubilación -----
    edad = resp["edad"]
    st.markdown("<div class='seccion'>🔥 ¿Te acordás del asado?</div>", unsafe_allow_html=True)
    st.markdown("Solo 5 de cada 10 aportan. Y además, cada vez hay menos trabajadores por cada jubilado. "
                "**Los números no cierran.** ¿Quién va a pagar tu jubilación?")
    if edad < 30:
        st.markdown("⛄ **La buena noticia:** tenés a tu favor lo que más pesa en la bola de nieve, que es **el tiempo**.")
    elif edad < 50:
        st.markdown("⛄ **Nunca es tarde, pero cada año cuenta.** La bola de nieve necesita tiempo para crecer.")
    else:
        st.markdown("⛄ **Es momento de ordenar y proteger lo que ahorraste,** y de que cada peso que sumes trabaje para vos.")
    anios = max(65 - edad, 0)
    if anios >= 5:
        por_mes = st.select_slider("🎚️ ¿Cuánto podrías ahorrar por mes? (en dólares)",
                                   options=[10, 20, 30, 50, 75, 100, 150, 200], value=50)
        c1, c2 = st.columns(2)
        c1.metric("Si empezás hoy", f"USD {ahorro_a_futuro(por_mes, anios):,.0f}".replace(",", "."))
        c2.metric("Si esperás 10 años", f"USD {ahorro_a_futuro(por_mes, max(anios - 10, 0)):,.0f}".replace(",", "."))
        st.markdown(f"<div class='letra-chica'>Ahorrando USD {por_mes} por mes hasta los 65, con un rendimiento supuesto "
                    "de 7% anual en dólares.</div>", unsafe_allow_html=True)
    st.markdown("💡 **No hace falta mucho:** empezar con el 5 o 10% de tu sueldo ya hace la diferencia. "
                "Informate, preguntale a alguien que sepa, investigá. **Lo importante es arrancar.**")

    # ----- Compartir -----
    st.markdown("<div class='seccion'>¿Te animás a desafiar a alguien?</div>", unsafe_allow_html=True)
    mensaje = (f"Hice el test \"{NOMBRE_APP}\" y acerté {aciertos} de {len(PREGUNTAS)} ({nivel(puntaje)}). "
               f"¿A que no me ganás? {secreto('APP_URL') or ''}")
    st.link_button("📲 Desafiá a alguien por WhatsApp", "https://wa.me/?text=" + urllib.parse.quote(mensaje),
                   type="primary", use_container_width=True)

    # ----- Dejá tu pregunta -----
    st.markdown("<div class='seccion'>💬 ¿Te quedaste con dudas? ¡Esa es la idea!</div>", unsafe_allow_html=True)
    st.markdown("Si este test te dejó pensando, no te quedes con la duda. Escribí lo que quieras saber sobre economía o sobre tu "
                "dinero, desde *\"¿qué es la inflación?\"* hasta *\"¿cómo empiezo a invertir con poco?\"*, y una inteligencia "
                "artificial te lo explica al instante, en criollo y sin tecnicismos.")
    st.markdown("**No hay preguntas tontas:** las mejores conversaciones de economía empiezan con un *\"¿y esto por qué pasa?\"*.")

    if len(st.session_state.consultas) < 3:
        st.markdown("<div class='letra-chica'>Tocá una idea o escribí la tuya:</div>", unsafe_allow_html=True)
        for k, sugerencia in enumerate(SUGERENCIAS):
            if st.button(sugerencia, key=f"sug_{k}", use_container_width=True):
                responder_consulta(sugerencia, edad, puntaje)
                st.rerun()
        with st.form("consulta", clear_on_submit=True):
            consulta = st.text_area("Tu pregunta", placeholder="Escribí tu pregunta acá...", max_chars=300,
                                    label_visibility="collapsed")
            if st.form_submit_button("Preguntar", type="primary", use_container_width=True) and consulta.strip():
                responder_consulta(consulta.strip(), edad, puntaje)
                st.rerun()
    else:
        st.info("Llegaste al máximo de 3 preguntas. ¡Gracias por participar!")

    for pregunta, respuesta in reversed(st.session_state.consultas):
        with st.container(border=True):
            st.markdown(f"**Tu pregunta:** {pregunta}")
            st.markdown(respuesta)

    st.markdown("<div class='letra-chica'>Podés hacer hasta 3 preguntas. Las respuestas son educativas: para decisiones "
                "importantes con tu dinero, consultá con un profesional.</div>", unsafe_allow_html=True)
