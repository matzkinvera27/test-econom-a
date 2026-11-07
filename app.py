# =============================================================
#  AL DATO  (nombre provisorio)
#  Test interactivo: ¿cuánto sabés de economía y qué hacés con tu dinero?
#  TP Programación para Economistas — Vera Matzkin
# =============================================================
#  Cómo está organizado este archivo:
#   1. Configuración y estilo
#   2. Datos reales (las respuestas correctas)
#   3. Las preguntas ("sabés") y los hábitos ("hacés")
#   4. Funciones: notas, perfil, gráficos, guardar, IA
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
# 1. CONFIGURACIÓN Y ESTILO
# -------------------------------------------------------------
st.set_page_config(page_title=NOMBRE_APP, page_icon="📊", layout="centered")

AZUL, DORADO, VERDE, ROJO = "#1F3A5F", "#C9A227", "#2E7D5B", "#B5473A"

st.markdown(
    f"""
    <style>
    .block-container {{max-width: 720px; padding-top: 3.5rem;}}
    h1, h2, h3 {{letter-spacing: -0.02em;}}
    .hero {{background: {AZUL}; color: white; border-radius: 22px; padding: 2.4rem 1.8rem 2rem 1.8rem; margin-bottom: 1.2rem;}}
    .hero h1 {{color: white; font-size: 2.1rem; line-height: 1.15; font-weight: 900; margin: 0 0 1rem 0; padding: 0;}}
    .hero p {{color: #E8ECF2; font-size: 1.08rem; margin: 0.3rem 0;}}
    .hero .oro {{color: {DORADO}; font-weight: 800; font-size: 1.2rem; margin-top: 0.8rem;}}
    .chips {{margin-top: 1.2rem;}}
    .chip {{display: inline-block; background: rgba(255,255,255,0.12); color: white; border-radius: 999px;
            padding: 0.3rem 0.8rem; margin: 0.2rem 0.3rem 0.2rem 0; font-size: 0.9rem;}}
    .etiqueta {{font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: #8A6D3B; font-weight: 700;}}
    .pregunta {{font-size: 1.4rem; font-weight: 700; line-height: 1.3; margin: 0.3rem 0 0.6rem 0;}}
    .ayuda {{color: #6B6B6B; font-size: 0.95rem;}}
    .grande {{font-size: 3.2rem; font-weight: 800; line-height: 1;}}
    .ok {{color: {VERDE}; font-size: 1.3rem; font-weight: 800;}}
    .mal {{color: {ROJO}; font-size: 1.3rem; font-weight: 800;}}
    .escena {{background: #F4F1EA; border-radius: 16px; padding: 1.1rem 1.3rem; margin: 0.8rem 0 1.2rem 0; line-height: 1.6;}}
    .personas {{font-size: 2rem; letter-spacing: 0.15rem; line-height: 1.4;}}
    .perfil {{font-size: 2rem; font-weight: 800; margin: 0.2rem 0;}}
    div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primaryFormSubmit"],
    a[data-testid="stBaseLinkButton-primary"] {{
        background: {DORADO}; color: #1F1F1F; border: none; border-radius: 999px; font-weight: 800;}}
    div.stButton > button, div.stFormSubmitButton > button, a[data-testid="stLinkButton"] {{border-radius: 999px; font-weight: 700;}}
    .st-key-boton_gigante button {{min-height: 4rem;}} .st-key-boton_gigante button p {{font-size: 1.35rem !important; font-weight: 900; letter-spacing: 0.05em;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 2. DATOS REALES — verificar en las fuentes antes de lanzar
# -------------------------------------------------------------
DATOS_REALES = {
    "bono":      {"valor": 5.0,  "unidad": "%",       "fuente": "Bono del Tesoro de EE.UU. a 10 años, octubre 2026"},
    "en_blanco": {"valor": 5.0,  "unidad": " de 10",  "fuente": "Cálculo con datos del INDEC, 2do trimestre 2026"},
    "impuestos": {"valor": 56.0, "unidad": " de $100", "fuente": "Unión Industrial Argentina (UIA), julio 2026"},
}
# Error a partir del cual la pregunta numérica suma 0 puntos
ERROR_MAXIMO = {"bono": 10, "en_blanco": 5, "impuestos": 40}

# -------------------------------------------------------------
# 3. PREGUNTAS ("SABÉS")  —  la "escena" es lo que aprende la persona después de responder
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

    {"id": "bono", "bloque": "Tu dinero", "tipo": "numero", "max": 30, "paso": 0.5, "sufijo": "%",
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

    {"id": "en_blanco", "bloque": "El país", "tipo": "numero", "max": 10, "paso": 1.0, "sufijo": " de 10",
     "texto": "De cada 10 personas que trabajan o buscan trabajo en Argentina, ¿cuántas tienen un trabajo en blanco (con aportes y obra social)?",
     "escena": """🔥 <b>Imaginate un asado con 10 personas que trabajan o buscan laburo:</b><br>
<div class='personas'>🧑‍💼🧑‍💼🧑‍💼🧑‍💼🧑‍💼</div><b>5 tienen recibo de sueldo</b><br>
<div class='personas'>🤫🤫🤫🤫</div><b>4 laburan en negro</b><br>
<div class='personas'>🔍</div><b>1 está buscando trabajo</b><br><br>
🤔 Solo 5 de cada 10 aportan… <b>¿Los números cierran?</b> Guardate esta pregunta: la retomamos al final. 😉"""},

    {"id": "impuestos", "bloque": "El país", "tipo": "numero", "max": 100, "paso": 1.0, "sufijo": "",
     "prefijo": "$",
     "texto": "Una empresa en blanco en Argentina, de cada $100 que gana, ¿cuántos se le van en impuestos?",
     "escena": """🥇 <b>Argentina sale 1ª de 30 países</b> en impuestos sobre las empresas en blanco. Un campeonato que nadie quiere ganar.<br><br>
🤔 <b>Pero en presión fiscal total, somos 12º.</b> ¿Cómo puede ser? Acordate del asado: solo 5 de cada 10 trabajan en blanco.<br>
<b>Pagan pocos, y los que pagan, pagan por todos.</b>"""},
]

# HÁBITOS ("HACÉS"): cuántos puntos suma cada respuesta (None = no cuenta para la nota)
HABITOS = {
    "dinero_que_sobra": {"No me sobra": None, "Lo gasto": 0, "Lo dejo en la cuenta o billetera virtual": 25,
                         "Plazo fijo": 50, "Compro dólares": 50, "Lo invierto (acciones, bonos, FCI, cripto)": 100},
    "fondo_emergencia": {"Sí": 100, "Más o menos": 50, "No": 0},
    "ahorro_jubilacion": {"Sí": 100, "Todavía no, pero quiero": 25, "No lo había pensado": 0},
}

# Los 4 perfiles (nombres provisorios): (nivel en "sabés", nivel en "hacés")
PERFILES = {
    ("alto", "alto"): {"nombre": "El Estratega", "emoji": "🧮",
                       "texto": "Sabés cómo funciona el dinero y lo aplicás. Sos de los pocos que no se dejan llevar por lo que \"se dice\"."},
    ("alto", "bajo"): {"nombre": "El Teórico", "emoji": "📚",
                       "texto": "Tenés los conceptos claros, pero tu dinero está quieto. Saber no alcanza: hay que pasar a la acción."},
    ("bajo", "alto"): {"nombre": "El Intuitivo", "emoji": "🐷",
                       "texto": "Hacés las cosas bastante bien con tu dinero, aunque no siempre sepas por qué. Con un poco más de información, sos imparable."},
    ("bajo", "bajo"): {"nombre": "El Despistado", "emoji": "🤷",
                       "texto": "Ni los datos ni los hábitos te acompañan todavía. Tranqui: es lo más común, y es lo más fácil de cambiar."},
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


def formato(numero):
    """32.3 → '32,3'  ·  45.0 → '45'"""
    texto = f"{numero:.1f}".replace(".", ",")
    return texto[:-2] if texto.endswith(",0") else texto


def con_unidad(pid, valor):
    p = next(q for q in PREGUNTAS if q["id"] == pid)
    return f"{p.get('prefijo', '')}{formato(valor)}{p['sufijo']}"


def puntaje_pregunta(p, respuesta):
    """De 0 a 1. Números: cuanto más cerca del dato real, más puntos. Opciones: 1 si es correcta."""
    if p["tipo"] == "numero":
        error = abs(respuesta - DATOS_REALES[p["id"]]["valor"])
        return max(0.0, 1 - error / ERROR_MAXIMO[p["id"]])
    return 1.0 if respuesta == p["correcta"] else 0.0


def calcular_notas(resp):
    sabes = 100 * sum(puntaje_pregunta(p, resp[p["id"]]) for p in PREGUNTAS) / len(PREGUNTAS)
    puntos = [HABITOS[h][resp[h]] for h in HABITOS if HABITOS[h][resp[h]] is not None]
    haces = sum(puntos) / len(puntos)
    return {"sabes": round(sabes), "haces": round(haces)}


def elegir_perfil(notas):
    nivel = lambda n: "alto" if n >= 50 else "bajo"
    return PERFILES[(nivel(notas["sabes"]), nivel(notas["haces"]))]


def grafico_linea(respuesta, real, maximo, unidad_txt):
    """Una línea del 0 al máximo con dos marcas: tu respuesta y el dato real."""
    fig = go.Figure()
    fig.add_shape(type="line", x0=0, x1=maximo, y0=0, y1=0, line=dict(color="#DDD6C8", width=8))
    fig.add_shape(type="line", x0=min(respuesta, real), x1=max(respuesta, real), y0=0, y1=0, line=dict(color=ROJO, width=8))
    fig.add_trace(go.Scatter(x=[respuesta], y=[0], mode="markers+text", text=[f"Vos: {unidad_txt(respuesta)}"],
                             textposition="top center", marker=dict(size=22, color=DORADO, line=dict(color="white", width=2)),
                             textfont=dict(size=15, color="#1F1F1F"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[real], y=[0], mode="markers+text", text=[f"Real: {unidad_txt(real)}"],
                             textposition="bottom center", marker=dict(size=22, color=AZUL, line=dict(color="white", width=2)),
                             textfont=dict(size=15, color=AZUL), hoverinfo="skip"))
    fig.update_layout(height=130, showlegend=False, margin=dict(l=10, r=10, t=0, b=0),
                      xaxis=dict(range=[-maximo * 0.08, maximo * 1.08], visible=False),
                      yaxis=dict(range=[-1.3, 1.3], visible=False),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def grafico_bola_de_nieve():
    """Interés compuesto vs. interés simple, $100 al 10% anual durante 30 años."""
    anios = list(range(0, 31))
    fig = go.Figure()
    fig.add_scatter(x=anios, y=[100 + 10 * a for a in anios], name="Sin bola de nieve", line=dict(color="#AAA", width=3, dash="dot"))
    fig.add_scatter(x=anios, y=[100 * 1.1 ** a for a in anios], name="Con bola de nieve ⛄", line=dict(color=DORADO, width=4))
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.15),
                      xaxis_title="Años", yaxis_title="$", plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def grafico_cuadrado(notas):
    """El cuadrado tipo Political Compass: hacés (horizontal) × sabés (vertical), con tu punto."""
    fig = go.Figure()
    zonas = [(0, 50, 50, 100, "#E9EEF5", ("alto", "bajo")), (50, 100, 50, 100, "#E6F2EC", ("alto", "alto")),
             (0, 50, 0, 50, "#F6E9E7", ("bajo", "bajo")), (50, 100, 0, 50, "#FBF3DE", ("bajo", "alto"))]
    for x0, x1, y0, y1, color, clave in zonas:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1, fillcolor=color, line=dict(width=0), layer="below")
        perfil = PERFILES[clave]
        fig.add_annotation(x=x0 + 3, y=y1 - 3, xanchor="left", yanchor="top", text=f"{perfil['emoji']} {perfil['nombre']}",
                           showarrow=False, font=dict(size=12, color="#5A5A5A"))
    fig.add_shape(type="line", x0=50, x1=50, y0=0, y1=100, line=dict(color="#BBB", width=1))
    fig.add_shape(type="line", x0=0, x1=100, y0=50, y1=50, line=dict(color="#BBB", width=1))
    fig.add_trace(go.Scatter(x=[notas["haces"]], y=[notas["sabes"]], mode="markers+text", text=["  VOS"],
                             textposition="middle right", textfont=dict(size=15, color="#1F1F1F"),
                             marker=dict(size=24, color=ROJO, line=dict(color="white", width=3)), hoverinfo="skip"))
    fig.update_layout(height=430, showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis=dict(range=[0, 100], title="💪 Lo que hacés con tu dinero →", showgrid=False, zeroline=False, tickvals=[0, 50, 100]),
                      yaxis=dict(range=[0, 100], title="🧠 Lo que sabés →", showgrid=False, zeroline=False, tickvals=[0, 50, 100], scaleanchor="x"),
                      plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def grafico_barras(resp):
    """Lo que creías vs. el dato real (llevado a %, para poder comparar en un mismo gráfico)."""
    filas = [("Bono del Tesoro (% anual)", resp["bono"], 5.0),
             ("Trabajan en blanco (de cada 100)", resp["en_blanco"] * 10, 50.0),
             ("Impuestos (de cada $100)", resp["impuestos"], 56.0)]
    fig = go.Figure()
    fig.add_bar(name="Lo que creías", y=[f[0] for f in filas], x=[f[1] for f in filas], orientation="h", marker_color=DORADO)
    fig.add_bar(name="Dato real", y=[f[0] for f in filas], x=[f[2] for f in filas], orientation="h", marker_color=AZUL)
    fig.update_layout(barmode="group", height=300, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.15),
                      yaxis=dict(autorange="reversed"), plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
    return fig


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


def devolucion(resp, notas, perfil):
    lineas = [f"Nota SABÉS: {notas['sabes']}/100. Nota HACÉS: {notas['haces']}/100. Perfil: {perfil['nombre']}. Edad: {resp['edad']}.",
              f"Qué hace con el dinero que le sobra: {resp['dinero_que_sobra']}. Fondo de emergencia: {resp['fondo_emergencia']}. "
              f"Ahorra para la jubilación: {resp['ahorro_jubilacion']}."]
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
Sin títulos. Podés usar **negrita** para 2 o 3 ideas clave. Usá "dinero", no "plata".
No recomiendes productos, bancos ni empresas específicas. No opines de política."""
    respuesta = preguntar_a_claude(prompt)
    if respuesta:
        return respuesta
    flojo = "lo que sabés" if notas["sabes"] < notas["haces"] else "lo que hacés con tu dinero"
    return (f"**{perfil['texto']}** Donde más margen tenés para mejorar es en **{flojo}**. "
            "Repasá las explicaciones de cada pregunta: en 2 minutos sabés más que la mayoría.")

# -------------------------------------------------------------
# 5. PANTALLAS
# -------------------------------------------------------------
if "paso" not in st.session_state:
    st.session_state.paso = "inicio"     # inicio → sobre_vos → preguntas → jubilacion → resultado
    st.session_state.resp = {}
    st.session_state.i = 0
    st.session_state.revelar = False
    st.session_state.guardado = False
    st.session_state.consultas = 0


def ir_a(paso):
    st.session_state.paso = paso
    st.rerun()


# ---------- INICIO ----------
if st.session_state.paso == "inicio":
    st.markdown(
        """<div class='hero'>
        <h1>¿Te animás a descubrir cuánto sabés realmente de economía?</h1>
        <p>Todos opinamos de economía. Todos creemos que manejamos bien nuestro dinero.</p>
        <p class='oro'>En 4 minutos vas a saber si es cierto.</p>
        <div class='chips'><span class='chip'>⏱ 4 minutos</span><span class='chip'>🔒 Anónimo</span><span class='chip'>🚫 Sin Google</span></div>
        </div>""", unsafe_allow_html=True)
    with st.container(key="boton_gigante"):
        if st.button("EMPEZAR EL TEST →", type="primary", use_container_width=True):
            ir_a("sobre_vos")

# ---------- SOBRE VOS ----------
elif st.session_state.paso == "sobre_vos":
    st.markdown("<div class='etiqueta'>Antes de arrancar</div>", unsafe_allow_html=True)
    st.subheader("Contanos un poco de vos")
    with st.form("sobre_vos"):
        edad = st.number_input("Edad", min_value=14, max_value=100, value=None, placeholder="Escribí tu edad")
        educacion = st.selectbox("Nivel educativo máximo", ["Secundario incompleto", "Secundario completo",
                                 "Terciario o universitario en curso", "Terciario o universitario completo", "Posgrado"], index=None,
                                 placeholder="Elegí una opción")
        fuente = st.selectbox("¿Por dónde te informás principalmente?", ["Redes sociales", "TV", "Diarios o portales",
                              "Radio o streaming", "Casi no me informo"], index=None, placeholder="Elegí una opción")
        sobra = st.selectbox("¿Qué hacés con el dinero que te sobra a fin de mes?", list(HABITOS["dinero_que_sobra"]),
                             index=None, placeholder="Elegí una opción")
        emergencia = st.radio("¿Tenés un ahorro para emergencias de al menos 3 meses de gastos?",
                              list(HABITOS["fondo_emergencia"]), index=None, horizontal=True)
        if st.form_submit_button("Seguir →", type="primary", use_container_width=True):
            if None in (edad, educacion, fuente, sobra, emergencia):
                st.error("Completá todo para seguir.")
            else:
                st.session_state.resp.update({"edad": edad, "educacion": educacion, "fuente_info": fuente,
                                              "dinero_que_sobra": sobra, "fondo_emergencia": emergencia})
                ir_a("preguntas")

# ---------- PREGUNTAS (una por pantalla, con devolución inmediata) ----------
elif st.session_state.paso == "preguntas":
    i = st.session_state.i
    p = PREGUNTAS[i]
    st.progress((i + 1) / (len(PREGUNTAS) + 1), text=f"Pregunta {i + 1} de {len(PREGUNTAS) + 1}")
    st.markdown(f"<div class='etiqueta'>{p['bloque']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pregunta'>{p['texto']}</div>", unsafe_allow_html=True)

    if not st.session_state.revelar:
        with st.form(f"q_{p['id']}"):
            if p["tipo"] == "numero":
                # Sin valor inicial a propósito: un número precargado "sopla" la respuesta (sesgo de anclaje)
                valor = st.number_input(f"Tu respuesta ({p.get('prefijo', '')}{p['sufijo'].strip() or 'número'})",
                                        min_value=0.0, max_value=float(p["max"]), value=None, step=p["paso"],
                                        format="%g", placeholder="Escribí un número")
            else:
                valor = st.radio("Respuesta", p["opciones"], index=None, label_visibility="collapsed")
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
            error = abs(r - real)
            if puntaje_pregunta(p, r) >= 0.8:
                st.markdown(f"<div class='ok'>¡Muy cerca! ✅</div>", unsafe_allow_html=True)
            else:
                lado = "Te pasaste" if r > real else "Te quedaste corto/a"
                st.markdown(f"<div class='mal'>{lado} ❌</div>", unsafe_allow_html=True)
            st.plotly_chart(grafico_linea(r, real, p["max"], lambda v, pid=p["id"]: con_unidad(pid, v)),
                            use_container_width=True, config={"displayModeBar": False, "staticPlot": True})
            st.caption(f"Fuente: {DATOS_REALES[p['id']]['fuente']}")
        else:
            if r == p["correcta"]:
                st.markdown("<div class='ok'>¡Bien ahí! ✅</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='mal'>Nop ❌</div>La correcta es: <b>{p['correcta']}</b>", unsafe_allow_html=True)
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
        valor = st.radio("Respuesta", list(HABITOS["ahorro_jubilacion"]), index=None, label_visibility="collapsed")
        if st.form_submit_button("Ver mi resultado →", type="primary", use_container_width=True):
            if valor is None:
                st.error("Respondé para seguir.")
            else:
                st.session_state.resp["ahorro_jubilacion"] = valor
                ir_a("resultado")

# ---------- RESULTADO ----------
elif st.session_state.paso == "resultado":
    resp = st.session_state.resp
    notas = calcular_notas(resp)
    perfil = elegir_perfil(notas)

    if not st.session_state.guardado:
        guardar({"fecha": datetime.now().isoformat(timespec="seconds"), **resp,
                 "nota_sabes": notas["sabes"], "nota_haces": notas["haces"], "perfil": perfil["nombre"]})
        st.session_state.guardado = True

    st.markdown("<div class='etiqueta'>Tu resultado</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='perfil'>{perfil['emoji']} Sos {perfil['nombre']}</div>", unsafe_allow_html=True)
    st.markdown(perfil["texto"])
    c1, c2 = st.columns(2)
    c1.markdown(f"🧠 Lo que sabés<div class='grande'>{notas['sabes']}<span style='font-size:1.2rem'>/100</span></div>", unsafe_allow_html=True)
    c2.markdown(f"💪 Lo que hacés<div class='grande'>{notas['haces']}<span style='font-size:1.2rem'>/100</span></div>", unsafe_allow_html=True)

    st.markdown("### Dónde estás parado/a")
    st.plotly_chart(grafico_cuadrado(notas), use_container_width=True, config={"displayModeBar": False, "staticPlot": True})

    st.markdown("### Tu devolución")
    if "devolucion" not in st.session_state:
        with st.spinner("Analizando tus respuestas..."):
            st.session_state.devolucion = devolucion(resp, notas, perfil)
    with st.container(border=True):
        st.markdown(st.session_state.devolucion)

    st.markdown("### Lo que creías vs. la realidad")
    st.plotly_chart(grafico_barras(resp), use_container_width=True, config={"displayModeBar": False, "staticPlot": True})

    # ----- Cierre según la edad: los números no cierran + calculadora -----
    st.divider()
    edad = resp["edad"]
    st.markdown("### 🔥 ¿Te acordás del asado?")
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
        por_mes = st.select_slider("🎚️ ¿Cuánto podrías ahorrar por mes? (en dólares)", options=[10, 20, 30, 50, 75, 100, 150, 200], value=50)
        hoy = ahorro_a_futuro(por_mes, anios)
        tarde = ahorro_a_futuro(por_mes, max(anios - 10, 0))
        c1, c2 = st.columns(2)
        c1.metric("Si empezás hoy", f"USD {hoy:,.0f}".replace(",", "."))
        c2.metric("Si esperás 10 años", f"USD {tarde:,.0f}".replace(",", "."))
        st.caption(f"Ahorrando USD {por_mes} por mes hasta los 65, con un rendimiento supuesto de 7% anual en dólares.")
    st.markdown("💡 **No hace falta mucho:** empezar con el 5 o 10% de tu sueldo ya hace la diferencia. "
                "Informate, preguntale a alguien que sepa, investigá. **Lo importante es arrancar.**")

    # ----- Compartir -----
    st.divider()
    st.markdown("### ¿Te animás a desafiar a alguien?")
    mensaje = (f"Hice el test \"{NOMBRE_APP}\" y me salió {perfil['emoji']} *{perfil['nombre']}* "
               f"(sé {notas['sabes']}/100, hago {notas['haces']}/100). ¿A que no me ganás? {secreto('APP_URL') or ''}")
    st.link_button("📲 Desafiá a alguien por WhatsApp", "https://wa.me/?text=" + urllib.parse.quote(mensaje),
                   type="primary", use_container_width=True)

    # ----- Dejá tu pregunta -----
    st.divider()
    st.markdown("### 💬 Dejá tu pregunta")
    st.markdown("¿Te quedó alguna duda sobre economía o sobre tu dinero? Escribila y te respondemos al instante.")
    with st.form("consulta", clear_on_submit=True):
        consulta = st.text_area("Tu pregunta", placeholder="Ej: ¿Qué es un fondo común de inversión?", max_chars=300,
                                label_visibility="collapsed")
        enviar = st.form_submit_button("Preguntar", type="primary", use_container_width=True)
    if enviar and consulta.strip():
        if st.session_state.consultas >= 3:
            st.info("Llegaste al máximo de 3 preguntas. ¡Gracias por participar!")
        else:
            st.session_state.consultas += 1
            guardar({"fecha": datetime.now().isoformat(timespec="seconds"), "edad": edad, "perfil": perfil["nombre"],
                     "pregunta": consulta.strip()}, hoja_nombre="preguntas")
            with st.spinner("Pensando..."):
                respuesta = preguntar_a_claude(
                    f"""Respondé esta pregunta de una persona que no estudió economía, en español rioplatense (voseo),
en 80 a 150 palabras, claro y con un ejemplo cotidiano. Usá "dinero", no "plata".
Educativo y neutral: no recomiendes productos, bancos ni empresas específicas, no opines de política,
y si la pregunta pide un consejo personal de inversión, explicá los conceptos y sugerí consultar a un asesor.
Pregunta: {consulta.strip()}""", max_tokens=400)
            with st.container(border=True):
                st.markdown(f"**Tu pregunta:** {consulta.strip()}")
                st.markdown(respuesta or "¡Gracias! Guardamos tu pregunta. Muy pronto esta sección va a responder al instante. 🙌")
