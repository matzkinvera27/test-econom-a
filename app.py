# =============================================================
#  ECONOMÍA EN 4 MINUTOS
#  Test interactivo: ¿cuánto sabés realmente de economía?
#  TP Programación para Economistas — Vera Matzkin
# =============================================================
#  Cómo está organizado este archivo:
#   1. Configuración y diseño (colores, letras, estilo)
#   2. Datos reales (las respuestas correctas)
#   3. Las preguntas y los perfiles
#   4. Funciones: puntaje, gráficos, guardar respuestas, IA
#   5. Pantallas: inicio → sobre vos → preguntas → jubilación → percepción → resultado
# =============================================================

import random
import urllib.parse
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

NOMBRE_APP = "Economía en 4 Minutos"   # ← cambiar acá el nombre

# -------------------------------------------------------------
# 1. CONFIGURACIÓN Y DISEÑO — paleta "chocolate y crema"
# -------------------------------------------------------------
st.set_page_config(page_title=NOMBRE_APP, page_icon="🪙", layout="wide", initial_sidebar_state="collapsed")

ESPRESSO, CHOCOLATE, CARAMELO, CREMA, ARENA = "#2B1D14", "#4A2F22", "#C08552", "#F5EDE3", "#E8DCCB"
VERDE, ROJO, WHATSAPP = "#4E7A55", "#A3472F", "#25D366"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {background: CREMA; color: ESPRESSO; font-family: 'Inter', sans-serif;}
header[data-testid="stHeader"], #MainMenu, footer {display: none !important;}
.block-container {max-width: 880px; padding: 2.5rem 1.4rem 4rem 1.4rem;}
body {overflow-x: hidden;}
h1, h2, h3, .titulo {font-family: 'Space Grotesk', sans-serif !important; color: ESPRESSO; letter-spacing: -0.03em;}
p, li, label, .stMarkdown {font-size: 1.08rem;}

/* --- Portada: fondo oscuro de borde a borde (arriba, el botón y abajo) --- */
.hero-arriba, .hero-abajo {background: ESPRESSO; color: CREMA; width: 100vw; margin-left: calc(-50vw + 50%);}
.hero-arriba {margin-top: -3rem; margin-bottom: -3px; padding: 4.5rem 1.4rem 1.6rem 1.4rem;}
.hero-abajo {padding: 0.5rem 1.6rem 3rem 1.6rem; margin-top: -1rem;}
.hero-grilla {max-width: 880px; margin: 0 auto; display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; align-items: center;}
.hero-texto {max-width: 640px;}
.hero-arriba .kicker {font-size: 0.85rem; letter-spacing: 0.22em; text-transform: uppercase; color: CARAMELO; font-weight: 600;}
.hero-arriba h1 {font-family: 'Space Grotesk', sans-serif; color: CREMA !important; font-size: clamp(2.2rem, 5.6vw, 3.9rem);
                 line-height: 1.02; font-weight: 700; margin: 0.6rem 0 1.2rem 0; padding: 0; letter-spacing: -0.035em;}
.hero-arriba p {color: #D9CBBB; font-size: 1.12rem; margin: 0.3rem 0;}
.hero-arriba .oro {color: CARAMELO; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 1.4rem; margin-top: 0.9rem;}
.chips {margin-top: 1.2rem;}
.chip {display: inline-block; border: 1px solid rgba(245,237,227,0.25); color: CREMA; border-radius: 999px;
       padding: 0.35rem 0.95rem; margin: 0.25rem 0.35rem 0.25rem 0; font-size: 0.92rem;}
.ilus svg {width: 100%; height: auto;}
.ilus-celu {display: none; max-width: 420px; margin: 0 auto;}
@media (max-width: 760px) {
  .hero-grilla {grid-template-columns: 1fr;}
  .ilus-compu {display: none;}
  .ilus-celu {display: block;}
}
/* El botón de empezar queda dentro del fondo oscuro */
.st-key-boton_gigante {background: ESPRESSO; box-shadow: 0 0 0 100vmax ESPRESSO; clip-path: inset(0 -100vmax); padding: 0.4rem 0 1.4rem 0;}
.st-key-boton_gigante {margin-top: -2px;}
.st-key-boton_gigante button {min-height: 4.4rem !important; max-width: 560px;}
.st-key-boton_gigante button p {font-size: 1.35rem !important; font-weight: 800 !important; letter-spacing: 0.08em;}

/* --- Textos de las pantallas --- */
.etiqueta {font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.2em; color: CARAMELO; font-weight: 700; margin-top: 1rem;}
.pregunta {font-family: 'Space Grotesk', sans-serif; font-size: clamp(1.6rem, 4.4vw, 2.3rem); font-weight: 700; line-height: 1.15;
           margin: 0.5rem 0 1.4rem 0; color: ESPRESSO; letter-spacing: -0.03em;}
.ok {color: VERDE; font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700;}
.mal {color: ROJO; font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700;}
.escena {background: ARENA; border-radius: 22px; padding: 1.6rem 1.7rem; margin: 1rem 0 1.6rem 0; line-height: 1.75; font-size: 1.08rem;}
.personas {font-size: 2.1rem; letter-spacing: 0.2rem; line-height: 1.4;}
.puntaje {font-family: 'Space Grotesk', sans-serif; font-size: clamp(3.5rem, 12vw, 6rem); font-weight: 700; line-height: 1; color: ESPRESSO; letter-spacing: -0.04em;}
.perfil {font-family: 'Space Grotesk', sans-serif; font-size: clamp(1.8rem, 5vw, 2.6rem); font-weight: 700; margin: 0.6rem 0 0.3rem 0; letter-spacing: -0.03em;}
.seccion {font-family: 'Space Grotesk', sans-serif; font-size: 1.9rem; font-weight: 700; margin: 2.6rem 0 0.6rem 0; color: ESPRESSO; letter-spacing: -0.03em;}
.letra-chica {color: #7A6656; font-size: 0.9rem;}
.titulo-preg {display: inline-block; background: ARENA; color: CHOCOLATE; border-radius: 999px; padding: 0.3rem 0.9rem; font-weight: 600; font-size: 0.98rem; margin-top: 0.6rem;}
.destacado {font-size: 1.28rem; line-height: 1.6; margin: 0.4rem 0 0.8rem 0;}
.emoji-calc {font-size: 2.3rem; line-height: 1; margin-bottom: 0.2rem;}
.neutro {color: CHOCOLATE; font-family: 'Space Grotesk', sans-serif; font-size: 1.9rem; font-weight: 700;}
.fila-emoji {display: flex; align-items: center; gap: 0.8rem; flex-wrap: nowrap; margin: 0.35rem 0;}
.fila-emoji b {flex: 1; line-height: 1.3;}
.fila-emoji .personas {font-size: clamp(1.25rem, 5.2vw, 2rem); letter-spacing: 0.1rem; line-height: 1.2; white-space: nowrap;}
.racha {font-size: 1.05rem; letter-spacing: 0.15rem; margin: -0.4rem 0 0.2rem 0;}
.racha-fuego {color: ROJO; font-weight: 700; letter-spacing: 0; margin-left: 0.4rem;}
.puntos {font-size: 1.5rem; letter-spacing: 0.2rem; color: CARAMELO;}
.pista {background: ARENA; border-radius: 14px; padding: 0.7rem 1rem; margin: 0.4rem 0 1rem 0; font-weight: 600;}
/* Transiciones suaves: cada pantalla aparece con un fundido y un leve deslizamiento */
@keyframes aparecer {from {opacity: 0; transform: translateY(14px);} to {opacity: 1; transform: none;}}
.etiqueta, .titulo-preg, .pregunta, .escena, .ok, .mal, .neutro, .puntaje, .perfil, .notas, .racha,
div[role="radiogroup"], [data-testid="stNumberInput"] {animation: aparecer 0.5s ease-out both;}
/* Latido de las barritas de la calculadora, hasta que la persona las toca */
@keyframes latido {0%, 100% {box-shadow: 0 0 0 0 rgba(192,133,82,0.55);} 50% {box-shadow: 0 0 0 12px rgba(192,133,82,0);}}
[data-testid="stSlider"] [role="slider"] {animation: latido 1.6s ease-in-out infinite; transform: scale(1.35);}
[data-testid="stSlider"] [role="slider"]:focus, [data-testid="stSlider"] [role="slider"]:active {animation: none;}
.notas {display: flex; gap: 1rem; flex-wrap: wrap; margin: 0.8rem 0;}
.nota {background: white; border-radius: 16px; padding: 0.8rem 1.2rem; min-width: 160px;}
.nota b {font-family: 'Space Grotesk', sans-serif; font-size: 2rem;}
.frase {background: ESPRESSO; color: CREMA; border-radius: 22px; padding: 2rem 1.8rem; margin: 2.6rem 0 0 0;
        font-family: 'Space Grotesk', sans-serif; font-size: clamp(1.25rem, 3.4vw, 1.6rem); line-height: 1.35; font-weight: 500;}
.frase span {color: CARAMELO;}
.billete svg {width: 100%; max-width: 520px; height: auto; display: block; margin: 0.8rem auto 1.2rem auto;}
.boton-wa {display: flex; align-items: center; justify-content: center; gap: 0.7rem; background: WHATSAPP; color: white !important;
           text-decoration: none !important; border-radius: 999px; min-height: 3.6rem; font-weight: 700; font-size: 1.1rem;}
.boton-wa:hover {filter: brightness(0.95);}
.boton-wa svg {flex-shrink: 0;}

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
div[role="radiogroup"][aria-orientation="horizontal"] label {width: auto;}

/* --- Botones --- */
div.stButton > button, div.stFormSubmitButton > button {border-radius: 999px; font-weight: 700; min-height: 3.3rem; font-size: 1.05rem;}
div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primaryFormSubmit"] {
    background: CARAMELO !important; color: ESPRESSO !important; border: none !important;}
div.stButton > button[kind="secondary"] {background: transparent; border: 1.5px solid CHOCOLATE; color: CHOCOLATE;}
[data-testid="stProgress"] > div > div > div > div {background: CARAMELO !important;}
[data-testid="stMetricValue"] {font-family: 'Space Grotesk', sans-serif; font-weight: 700;}
</style>
"""
for nombre, valor in {"ESPRESSO": ESPRESSO, "CHOCOLATE": CHOCOLATE, "CARAMELO": CARAMELO, "CREMA": CREMA,
                      "ARENA": ARENA, "VERDE": VERDE, "ROJO": ROJO, "WHATSAPP": WHATSAPP}.items():
    CSS = CSS.replace(nombre, valor)
st.markdown(CSS, unsafe_allow_html=True)


# Ilustración de la portada: monedas que crecen cuesta abajo (la bola de nieve del interés compuesto)
def moneda(cx, cy, r):
    return (f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{CARAMELO}'/>"
            f"<circle cx='{cx}' cy='{cy}' r='{r * 0.78:.1f}' fill='none' stroke='{ESPRESSO}' stroke-opacity='0.35' stroke-width='{max(r * 0.07, 1):.1f}'/>"
            f"<text x='{cx}' y='{cy + r * 0.36:.1f}' text-anchor='middle' font-family='Space Grotesk, sans-serif' font-weight='700' "
            f"font-size='{r * 1.05:.1f}' fill='{ESPRESSO}' fill-opacity='0.55'>$</text>")


MONEDAS = [(40, 52, 7), (110, 78, 10), (200, 112, 15), (315, 156, 22), (465, 214, 34)]
ILUSTRACION = (
    "<svg viewBox='0 0 560 270' xmlns='http://www.w3.org/2000/svg' role='img' aria-label='Monedas que crecen cuesta abajo'>"
    f"<path d='M0 40 L560 255' stroke='{CREMA}' stroke-opacity='0.25' stroke-width='2' stroke-dasharray='2 8'/>"
    + "".join(f"<path d='M{cx - r - 34} {cy - 6 - r * 0.2} h22' stroke='{CREMA}' stroke-opacity='0.2' stroke-width='2' stroke-linecap='round'/>"
              for cx, cy, r in MONEDAS[1:])
    + "".join(moneda(cx, cy - r * 0.55, r) for cx, cy, r in MONEDAS)
    + "</svg>"
)

# Billete de 1 dólar (ilustración propia, estilizada) para la calculadora de inversión
BILLETE = f"""<svg viewBox='0 0 520 230' xmlns='http://www.w3.org/2000/svg' role='img' aria-label='Billete de un dólar'>
<rect x='4' y='4' width='512' height='222' rx='14' fill='#DCE5CF' stroke='#5E7A4E' stroke-width='3'/>
<rect x='18' y='18' width='484' height='194' rx='8' fill='none' stroke='#5E7A4E' stroke-width='1.5' stroke-dasharray='5 4'/>
<circle cx='260' cy='115' r='62' fill='#C9D6B8' stroke='#5E7A4E' stroke-width='2'/>
<text x='260' y='145' text-anchor='middle' font-family='Space Grotesk, sans-serif' font-weight='700' font-size='92' fill='#3F5A33'>$</text>
<text x='48' y='72' font-family='Space Grotesk, sans-serif' font-weight='700' font-size='54' fill='#3F5A33'>1</text>
<text x='472' y='72' text-anchor='end' font-family='Space Grotesk, sans-serif' font-weight='700' font-size='54' fill='#3F5A33'>1</text>
<text x='48' y='192' font-family='Space Grotesk, sans-serif' font-weight='700' font-size='54' fill='#3F5A33'>1</text>
<text x='472' y='192' text-anchor='end' font-family='Space Grotesk, sans-serif' font-weight='700' font-size='54' fill='#3F5A33'>1</text>
<text x='260' y='40' text-anchor='middle' font-family='Inter, sans-serif' font-weight='600' font-size='14' letter-spacing='4' fill='#3F5A33'>UN DÓLAR</text>
<text x='260' y='205' text-anchor='middle' font-family='Inter, sans-serif' font-weight='600' font-size='13' letter-spacing='3' fill='#3F5A33'>EL PRIMERO DE TU BOLA DE NIEVE</text>
</svg>"""

# -------------------------------------------------------------
# 2. DATOS REALES — verificar en las fuentes antes de lanzar
# -------------------------------------------------------------
DATOS_REALES = {
    "en_blanco": {"valor": 5.0,  "fuente": "Cálculo con datos del INDEC, 2do trimestre 2026"},
    "impuestos": {"valor": 56.0, "fuente": "Unión Industrial Argentina (UIA), julio 2026"},
}
# Error a partir del cual la pregunta numérica suma 0 puntos
ERROR_MAXIMO = {"en_blanco": 5, "impuestos": 40}

# -------------------------------------------------------------
# 3. LAS PREGUNTAS — area "fin" (tu dinero) o "eco" (el país); "escena" = lo que aprende después de responder
# -------------------------------------------------------------
PREGUNTAS = [
    # ---------- 💰 TU DINERO ----------
    {"id": "interes_compuesto", "titulo": "💰 Tu primera inversión", "area": "fin", "bloque": "Tu dinero", "tipo": "opcion",
     "texto": "Ponés USD 1.000 en una inversión que rinde 10% por año y no retirás nada. El primer año ganás USD 100. ¿Y el segundo año?",
     "opciones": ["Gano USD 100 de nuevo", "Gano un poco más que USD 100", "Gano menos que USD 100"],
     "correcta": "Gano un poco más que USD 100",
     "escena": """<b>El secreto: cada año ganás intereses sobre los intereses que ya ganaste.</b><br><br>
⚪ <b>Año 1:</b> ganás USD 100 → tenés USD 1.100<br>
⚪ <b>Año 2:</b> ganás USD 110 → tenés USD 1.210<br>
⚪ <b>Año 3:</b> ganás USD 121 → tenés USD 1.331<br><br>
Tu dinero genera dinero solo, como una bola de nieve que rueda cuesta abajo y cada vuelta junta más nieve. ⛄<br><br>
📈 A los 10 años: <b>USD 2.594</b> (no 2.000). 🚀 A los 30 años: <b>USD 17.449</b>.<br><br>
📚 <b>Esto tiene nombre: se llama interés compuesto.</b> Es ganar intereses sobre los intereses que ya ganaste.
Acordate de esta palabra, porque es la base de cualquier inversión.<br><br>
<b>Lo que importa no es cuánto ponés, sino cuánto tiempo dejás rodar la bola.</b>"""},

    {"id": "la_vara", "titulo": "🛡️ A prueba de todo", "area": "fin", "bloque": "Tu dinero", "tipo": "opcion",
     "texto": "¿Cuál de estas inversiones se considera la más segura del mundo?",
     "opciones": ["Oro", "Dólares en el colchón", "Bonos del Tesoro de EE.UU.", "Bitcoin"],
     "correcta": "Bonos del Tesoro de EE.UU.",
     "escena": """🇺🇸 Se considera que el gobierno de EE.UU. es el deudor con menos chances de no pagar.<br><br>
📏 <b>Paga alrededor de 5% por año en dólares, casi sin riesgo y sin hacer nada.</b> Eso es <b>"la vara"</b>:
cualquier inversión o negocio tiene que ganarle.<br><br>
Guardate este número, que lo vas a necesitar en la próxima pregunta. 😉"""},

    {"id": "franquicia", "titulo": "🍔 La propuesta de un amigo", "area": "fin", "bloque": "Tu dinero", "tipo": "opcion",
     "texto": "Un amigo te ofrece entrar en su franquicia: por cada USD 100 que ponés, ganás USD 4 por año. ¿Es buen negocio?",
     "opciones": ["Sí, porque gano dinero todos los años", "Sí, porque 4% por año es un buen rendimiento",
                  "No, porque gana menos que una inversión sin riesgo", "Depende de dónde esté el local"],
     "correcta": "No, porque gana menos que una inversión sin riesgo",
     "escena": """📏 <b>La vara: 5% en dólares, sin riesgo y sin hacer nada.</b> Cualquier negocio tiene que ganarle, y <b>por bastante</b>: vos ponés riesgo, tiempo y laburo.<br><br>
🍔 <b>Franquicia al 4%:</b> arriesgás tu dinero para ganar <i>menos</i> que alguien que no hizo nada.<br>
🏢 <b>Departamento en alquiler:</b> si te deja 3 o 4% en dólares después de gastos, pasa lo mismo.<br><br>
🚀 Siempre preguntate: <b>¿mi negocio le gana a la vara por lo suficiente?</b> Si no, hay que exprimirlo más.
Eso es el <b>costo de oportunidad</b>: lo que dejás de ganar por elegir una opción y no otra.<br><br>
🧮 <b>¿Cómo lo mido?</b> Ganancia de un año ÷ dinero que pusiste: $4 ÷ $100 = <b>4%</b>."""},

    {"id": "tasa_real", "titulo": "📉 ¿Ganaste o perdiste?", "area": "fin", "bloque": "Tu dinero", "tipo": "opcion",
     "texto": "Ponés $100.000 en algo que rinde 40% en el año, pero la inflación de ese año es 50%. Al final del año, ¿cuántas cosas podés comprar con tu dinero?",
     "opciones": ["Un 40% más que antes", "Un poco más que antes", "Menos que antes", "Lo mismo que antes"],
     "correcta": "Menos que antes",
     "escena": """🛒 Tus $100.000 se hicieron <b>$140.000</b>. ¡Bien! 🕺🍾<br>
Pero el changuito que antes costaba $100.000, ahora cuesta <b>$150.000</b>. 😬<br>
Con tus $140.000 no te alcanza: <b>te faltan $10.000</b>.<br><br>
<b>Tenés más billetes, pero podés comprar menos.</b> Lo que importa no es cuánto rinde tu dinero,
sino si rinde <b>más que la inflación</b>. Eso se llama <b>tasa real</b>."""},


    {"id": "colchon", "titulo": "🛏️ El colchón", "area": "fin", "bloque": "Tu dinero", "tipo": "opcion",
     "texto": "Una persona guarda todos sus ahorros en dólares durante varios años, sin invertirlos. ¿Qué pasa con ese dinero?",
     "opciones": ["No pierde valor: el dólar es una moneda fuerte", "Pierde poder de compra de a poco, por la inflación de EE.UU.",
                  "Gana valor solo, con el paso del tiempo", "Rinde más que cualquier inversión en pesos"],
     "correcta": "Pierde poder de compra de a poco, por la inflación de EE.UU.",
     "escena": """🛏️ <b>El dólar te cuida de la devaluación del peso… pero no de la inflación de EE.UU.</b> Allá los precios también suben, en promedio un 3% por año.<br><br>
💵 Tus <b>USD 100</b> del colchón, en 10 años, compran lo mismo que hoy compran <b>unos USD 74</b>. No ves menos billetes, pero alcanzan para menos.<br><br>
📏 <b>Acordate de la vara:</b> esos mismos USD 100 en un bono del Tesoro, a 5% por año, en 10 años serían <b>USD 163</b>.<br>
<b>El dólar quieto también pierde. El dólar invertido, crece.</b>"""},

    # ---------- 🇦🇷 EL PAÍS ----------
    {"id": "en_blanco", "titulo": "🥩 El asado", "area": "eco", "bloque": "El país", "tipo": "numero", "max": 10, "paso": 1.0, "prefijo": "", "sufijo": " de 10",
     "texto": "De cada 10 personas que trabajan o buscan trabajo en Argentina, ¿cuántas tienen un trabajo en blanco (con aportes y obra social)?",
     "escena": """🥩 <b>Imaginate un asado con 10 personas que trabajan o buscan laburo:</b><br>
<div class='fila-emoji'><span class='personas'>🧑‍💼🧑‍💼🧑‍💼🧑‍💼🧑‍💼</span><b>5 tienen recibo de sueldo</b></div>
<div class='fila-emoji'><span class='personas'>🤫🤫🤫🤫</span><b>4 laburan en negro</b></div>
<div class='fila-emoji'><span class='personas'>🔍</span><b>1 está buscando trabajo</b></div><br>
🤔 Solo 5 de cada 10 aportan… <b>¿Los números cierran?</b> Guardate esta pregunta: la retomamos al final. 😉"""},

    {"id": "impuestos", "titulo": "🏭 Los impuestos", "area": "eco", "bloque": "El país", "tipo": "numero", "max": 100, "paso": 1.0, "prefijo": "$", "sufijo": "",
     "texto": "Una empresa en blanco en Argentina, de cada $100 que gana, ¿cuántos se le van en impuestos?",
     "escena": """🥇 <b>Argentina sale 1ª de 30 países</b> en impuestos sobre las empresas en blanco. Un campeonato que nadie quiere ganar.<br><br>
🤔 <b>Pero en presión fiscal total, somos 12º.</b> ¿Cómo puede ser? Acordate del asado: solo 5 de cada 10 trabajan en blanco.<br>
<b>Pagan pocos, y los que pagan, pagan por todos.</b>"""},

    {"id": "banco_central", "titulo": "🏦 El Banco Central", "area": "eco", "bloque": "El país", "tipo": "opcion",
     "texto": "El Banco Central sube fuerte la tasa de interés. ¿Qué busca lograr?",
     "opciones": ["Que sea más barato endeudarse y se consuma más",
                  "Encarecer el crédito para frenar el consumo y la inflación", "Que suban los sueldos"],
     "correcta": "Encarecer el crédito para frenar el consumo y la inflación",
     "escena": """🏦 La tasa de interés es el <b>"precio" del dinero</b>. Cuando el Banco Central la sube:<br><br>
💳 Pedir un préstamo o comprar en cuotas sale <b>más caro</b> → la gente compra menos.<br>
🐷 Ahorrar en pesos <b>rinde más</b> → la gente guarda en vez de gastar.<br><br>
Menos gente gastando = <b>los precios suben más despacio</b>. Es como pisar el freno del auto 🚗:
frena la inflación… pero también frena la economía."""},

    {"id": "emision", "titulo": "🖨️ La maquinita", "area": "eco", "bloque": "El país", "tipo": "opcion",
     "texto": "Un país imprime muchos más billetes, pero produce la misma cantidad de bienes y servicios. ¿Qué pasa?",
     "opciones": ["Hay más riqueza para todos", "Suben los precios", "No pasa nada, el dinero es solo papel"],
     "correcta": "Suben los precios",
     "escena": """🍕 Imaginá <b>una pizza de 8 porciones</b>, y cada porción se canjea con un ticket.<br>
Si de golpe se imprimen el doble de tickets, pero la pizza sigue siendo una sola…<br>
<b>cada ticket alcanza para media porción.</b> 🤏<br><br>
Con el dinero pasa lo mismo: si hay el doble de billetes pero los mismos bienes y servicios para comprar,
<b>cada billete compra menos</b>. Eso es la inflación."""},
    {"id": "dolar", "titulo": "💵 La obsesión nacional", "area": "eco", "bloque": "El país", "tipo": "opcion",
     "texto": "Si el dólar pasa de $1.000 a $1.500, ¿cuál de estas afirmaciones describe mejor lo que sucede en la economía?",
     "opciones": ["El peso pierde valor frente al dólar, y los productos importados podrían encarecerse",
                  "El peso gana valor frente al dólar, porque ahora se necesitan más pesos para comprarlo",
                  "Todos los precios de la economía aumentan automáticamente un 50%",
                  "El cambio solo afecta a quienes compran dólares, sin impacto en el resto de la economía"],
     "correcta": "El peso pierde valor frente al dólar, y los productos importados podrían encarecerse",
     "escena": """💸 <b>Que el dólar suba significa que el peso vale menos.</b> Antes, con $1.000 comprabas un dólar; ahora necesitás $1.500. Eso es una <b>devaluación</b>.<br><br>
📱 <b>Lo directo:</b> un celular importado de USD 100 pasa de $100.000 a $150.000.<br><br>
🍞 <b>Lo indirecto:</b> ¿y el pan, que no tiene nada que ver con el dólar? Mirá la cadena:<br>
⛽ Sube el combustible (su precio va atado al dólar)<br>
→ 🚚 sube el flete que lleva el trigo al molino<br>
→ 🌾 sube la harina<br>
→ 🥖 sube el pan<br><br>
Por eso, <b>cuando sube el dólar en Argentina, primero suben las cosas atadas al dólar, y después ese aumento se va contagiando</b>
hasta productos que no tienen nada que ver. Y por eso todos miramos el dólar todo el tiempo. 👀"""},
]

# Lo que se aprende en cada pregunta, en punteo (va en la página 2 del informe PDF)
APRENDIZAJES = {
    "interes_compuesto": ("Interés compuesto", [
        "Cada año ganás intereses sobre los intereses que ya ganaste: USD 1.000 al 10% anual se hacen USD 1.100, después USD 1.210, después USD 1.331.",
        "A los 10 años son USD 2.594 (no 2.000) y a los 30 años, USD 17.449, sin poner un peso más.",
        "Lo que más pesa no es cuánto ponés, sino cuánto tiempo lo dejás crecer: conviene empezar cuanto antes."]),
    "en_blanco": ("Trabajo en blanco", [
        "De cada 10 personas que trabajan o buscan trabajo en Argentina, solo 5 tienen un empleo en blanco: 4 trabajan en negro y 1 busca trabajo.",
        "Con los aportes de esos 5 se financian, entre otras cosas, las jubilaciones. Con tan pocos aportando, los números no cierran."]),
    "impuestos": ("Presión fiscal", [
        "Una empresa en blanco paga unos $56 de impuestos por cada $100 que gana (UIA, 2026): Argentina es 1ª de 30 países en ese ranking.",
        "En presión fiscal total, Argentina está 12ª. Como muchos trabajan en negro, pagan pocos, y los que pagan, pagan por todos."]),
    "la_vara": ("La vara: la inversión más segura", [
        "Los bonos del Tesoro de EE.UU. se consideran la inversión más segura del mundo.",
        "Pagan alrededor de 5% por año en dólares, casi sin riesgo. Esa es \"la vara\": cualquier inversión o negocio tiene que ganarle."]),
    "franquicia": ("Costo de oportunidad", [
        "Un negocio que rinde 4% en dólares gana menos que la vara del 5%, y encima tiene riesgo y requiere trabajo.",
        "El costo de oportunidad es lo que dejás de ganar por elegir una opción y no otra.",
        "Para medir un negocio: ganancia de un año ÷ dinero invertido. Si no le gana a la vara por bastante, hay que exprimirlo más."]),
    "emision": ("Emisión e inflación", [
        "Si un país imprime muchos más billetes pero produce los mismos bienes y servicios, cada billete compra menos: suben los precios.",
        "Como una pizza de 8 porciones: si se imprimen el doble de tickets para canjearla, cada ticket alcanza para media porción."]),
    "tasa_real": ("Tasa real", [
        "Si tus $100.000 rinden 40% pero la inflación es 50%, tenés $140.000… pero el changuito que costaba $100.000 ahora cuesta $150.000.",
        "Tener más pesos no significa poder comprar más. Lo que importa es la tasa real: si tu dinero rinde más que la inflación."]),
    "banco_central": ("La tasa de interés del Banco Central", [
        "La tasa de interés es el \"precio\" del dinero. Cuando el Banco Central la sube, endeudarse sale más caro y ahorrar rinde más.",
        "La gente gasta menos y los precios suben más despacio: es un freno a la inflación, pero también a la economía."]),
    "dolar": ("Devaluación", [
        "Si el dólar pasa de $1.000 a $1.500, el peso pierde valor: eso es una devaluación.",
        "Suben primero los productos importados y lo atado al dólar, como el combustible.",
        "Después el aumento se contagia: combustible → flete → harina → pan. Por eso en Argentina todos miramos el dólar."]),
    "colchon": ("El dólar en el colchón", [
        "El dólar te protege de la devaluación del peso, pero no de la inflación de EE.UU. (en promedio, 3% por año).",
        "USD 100 guardados 10 años compran lo mismo que hoy USD 74. Invertidos al 5%, serían USD 163.",
        "El dólar quieto también pierde. El dólar invertido, crece."]),
}

# Orden en que aparecen: intercaladas, respetando las que se nombran entre sí
# (la vara → franquicia, asado → impuestos, la vara → colchón)
ORDEN = ["interes_compuesto", "en_blanco", "impuestos", "la_vara", "franquicia",
         "emision", "tasa_real", "banco_central", "dolar", "colchon"]
PREGUNTAS = [next(p for p in PREGUNTAS if p["id"] == pid) for pid in ORDEN]

# Los 4 perfiles (nombres provisorios): (nivel en "El país", nivel en "Tu dinero")
PERFILES = {
    ("alto", "alto"): {"nombre": "La Calculadora", "emoji": "🧮",
                       "texto": "Entendés cómo funciona el país y lo aplicás a tu dinero. Sos de los pocos que no se dejan llevar por lo que \"se dice\"."},
    ("alto", "bajo"): {"nombre": "El Opinólogo", "emoji": "🎙️",
                       "texto": "Tenés bastante claro cómo funciona la economía del país, pero a la hora de manejar tu dinero, te falta calle."},
    ("bajo", "alto"): {"nombre": "El Ahorrista Intuitivo", "emoji": "🐷",
                       "texto": "Con tu dinero sos vivo/a, aunque la economía del país te queda un poco lejos. Si te informás un poco más, sos imparable."},
    ("bajo", "bajo"): {"nombre": "El Despistado", "emoji": "🤷",
                       "texto": "Todavía te faltan datos clave del país y de tu dinero. Tranqui: es lo más común, y es lo más fácil de cambiar."},
}

PERCEPCION = ["Más de lo que pensaba", "Lo que pensaba", "Menos de lo que pensaba",
              "Me di cuenta de que hay un montón de cosas que nunca me había preguntado"]

SUGERENCIAS = ["¿Qué es un plazo fijo UVA?", "¿Cómo empiezo a invertir con poco?", "¿Por qué hay tanta inflación en Argentina?"]

LINK_APP = "https://test-economia.streamlit.app"
# Logo de WhatsApp (Simple Icons, licencia CC0), dibujado en blanco
ICONO_WHATSAPP = "<svg viewBox='0 0 24 24' width='28' height='28' fill='white' xmlns='http://www.w3.org/2000/svg'><path d='M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z'/></svg>"

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


def miles(numero):
    """163806.4 → '163.806'"""
    return f"{numero:,.0f}".replace(",", ".")


def con_unidad(p, valor):
    return f"{p['prefijo']}{formato(valor)}{p['sufijo']}"


def opciones_mezcladas(p):
    """Mezcla el orden de las opciones (una vez por persona) para que la correcta no caiga siempre en el mismo lugar.
    'No sé' va siempre al final."""
    clave = f"orden_{p['id']}"
    if clave not in st.session_state:
        orden = p["opciones"][:]
        random.shuffle(orden)
        st.session_state[clave] = orden + ["No sé"]
    return st.session_state[clave]


def puntaje_pregunta(p, respuesta):
    """De 0 a 1. Números: cuanto más cerca del dato real, más puntos. Opciones: 1 si es correcta."""
    if p["tipo"] == "numero":
        error = abs(respuesta - DATOS_REALES[p["id"]]["valor"])
        return max(0.0, 1 - error / ERROR_MAXIMO[p["id"]])
    return 1.0 if respuesta == p["correcta"] else 0.0


def acerto(p, respuesta):
    """Cuenta como acierto si la opción es correcta o si el número quedó muy cerca (80% del puntaje o más)."""
    return puntaje_pregunta(p, respuesta) >= 0.8


POR_AREA = 5   # preguntas de cada área


def calcular_notas(resp):
    """Aciertos en 'El país' (eco) y en 'Tu dinero' (fin), de 0 a 5."""
    return {area: sum(acerto(p, resp[p["id"]]) for p in PREGUNTAS if p["area"] == area) for area in ["eco", "fin"]}


def elegir_perfil(notas):
    nivel = lambda n: "alto" if n >= 3 else "bajo"   # 3 de 5 o más = mitad alta
    return PERFILES[(nivel(notas["eco"]), nivel(notas["fin"]))]


def puntitos(n, total=POR_AREA):
    return "●" * n + "○" * (total - n)


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
                             textfont=dict(size=16, color=ESPRESSO), hoverinfo="skip", cliponaxis=False))
    fig.add_trace(go.Scatter(x=[real], y=[0], mode="markers+text", text=[f"Real: {con_unidad(p, real)}"],
                             textposition="bottom center", marker=dict(size=26, color=CHOCOLATE, line=dict(color="white", width=3)),
                             textfont=dict(size=16, color=CHOCOLATE), hoverinfo="skip", cliponaxis=False))
    fig.update_layout(showlegend=False, xaxis=dict(range=[-maximo * 0.08, maximo * 1.08], visible=False),
                      yaxis=dict(range=[-1.3, 1.3], visible=False))
    return layout_base(fig, 140)


def grafico_bola_de_nieve():
    """Interés compuesto vs. interés simple: USD 1.000 al 10% anual durante 30 años."""
    anios = list(range(0, 31))
    fig = go.Figure()
    fig.add_scatter(x=anios, y=[1000 + 100 * a for a in anios], name="Sin bola de nieve", line=dict(color="#B9A797", width=3, dash="dot"))
    fig.add_scatter(x=anios, y=[1000 * 1.1 ** a for a in anios], name="Con bola de nieve ⛄", line=dict(color=CARAMELO, width=5))
    fig.update_layout(legend=dict(orientation="h", y=1.15), xaxis=dict(title="Años", gridcolor=ARENA),
                      yaxis=dict(title="USD", gridcolor=ARENA))
    return layout_base(fig, 280)


def grafico_cuadrado(notas):
    """El cuadrado tipo zodíaco: 'Tu dinero' (horizontal) × 'El país' (vertical), con tu punto."""
    fig = go.Figure()
    zonas = [(0, 50, 50, 100, "#EADCCB", ("alto", "bajo")), (50, 100, 50, 100, "#D9BC98", ("alto", "alto")),
             (0, 50, 0, 50, "#F3EAE0", ("bajo", "bajo")), (50, 100, 0, 50, "#E4CCAE", ("bajo", "alto"))]
    for x0, x1, y0, y1, color, clave in zonas:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1, fillcolor=color, line=dict(width=0), layer="below")
        perfil = PERFILES[clave]
        fig.add_annotation(x=x0 + 3, y=y1 - 3, xanchor="left", yanchor="top", text=f"{perfil['emoji']} {perfil['nombre']}",
                           showarrow=False, font=dict(size=12, color=CHOCOLATE))
    fig.add_shape(type="line", x0=50, x1=50, y0=0, y1=100, line=dict(color="#B9A797", width=1))
    fig.add_shape(type="line", x0=0, x1=100, y0=50, y1=50, line=dict(color="#B9A797", width=1))
    # El punto se ubica según los aciertos de cada área (0 a 5 → 0 a 100)
    x = min(max(notas["fin"] / POR_AREA * 100, 4), 96)
    y = min(max(notas["eco"] / POR_AREA * 100, 4), 90)
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers+text", text=["  VOS"], textposition="middle right",
                             textfont=dict(size=16, color=ESPRESSO, family="Space Grotesk"), cliponaxis=False,
                             marker=dict(size=26, color=ESPRESSO, line=dict(color="white", width=4)), hoverinfo="skip"))
    fig.update_layout(showlegend=False,
                      xaxis=dict(range=[0, 100], title="💰 Tu dinero →", showgrid=False, zeroline=False, tickvals=[0, 50, 100]),
                      yaxis=dict(range=[0, 100], title="🇦🇷 El país →", showgrid=False, zeroline=False, tickvals=[0, 50, 100]))
    return layout_base(fig, 460)


def grafico_barras(resp):
    """Lo que creías vs. el dato real (llevado a la misma escala para comparar)."""
    filas = [("Trabajan en blanco<br>(de cada 100)", resp["en_blanco"] * 10, 50.0),
             ("Impuestos de una empresa<br>(de cada $100)", resp["impuestos"], 56.0)]
    fig = go.Figure()
    fig.add_bar(name="Lo que creías", y=[f[0] for f in filas], x=[f[1] for f in filas], orientation="h", marker_color=CARAMELO)
    fig.add_bar(name="Dato real", y=[f[0] for f in filas], x=[f[2] for f in filas], orientation="h", marker_color=CHOCOLATE)
    fig.update_layout(barmode="group", legend=dict(orientation="h", y=1.2), yaxis=dict(autorange="reversed"),
                      xaxis=dict(gridcolor=ARENA, range=[0, 100]))
    return layout_base(fig, 260)


def simular_ahorro(por_mes, anios, tasa_anual):
    """Año por año: cuánto pusiste vos y cuánto generó el interés compuesto (aportes mensuales)."""
    r = tasa_anual / 12
    saldo, filas = 0.0, []
    for mes in range(1, int(anios * 12) + 1):
        saldo = saldo * (1 + r) + por_mes
        if mes % 12 == 0:
            aportado = por_mes * mes
            filas.append({"anio": mes // 12, "aportado": aportado, "intereses": saldo - aportado, "total": saldo})
    return pd.DataFrame(filas)


def grafico_crecimiento(tabla):
    """Barras anuales apiladas: lo que pusiste vos + lo que puso la bola de nieve."""
    fig = go.Figure()
    fig.add_bar(x=tabla["anio"], y=tabla["aportado"], name="Lo que pusiste vos", marker_color=CHOCOLATE)
    fig.add_bar(x=tabla["anio"], y=tabla["intereses"], name="Lo que puso la bola de nieve ⛄", marker_color=CARAMELO)
    fig.update_layout(barmode="stack", bargap=0.15, legend=dict(orientation="h", y=1.15),
                      xaxis=dict(title="Años", gridcolor=ARENA), yaxis=dict(title="USD", gridcolor=ARENA))
    return layout_base(fig, 340)


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


MODELOS_CLAUDE = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-haiku-4-5", "claude-sonnet-4-5", "claude-3-5-haiku-latest"]
DEBUG = st.query_params.get("debug") == "1"   # entrar con ?debug=1 muestra los errores de la IA (solo para Vera)


def preguntar_a_claude(prompt, max_tokens=600):
    """Le manda un pedido a Claude. Si no está configurado o falla, devuelve None (y en modo debug muestra por qué)."""
    clave = secreto("ANTHROPIC_API_KEY")
    errores = []
    if not clave:
        errores.append("No encontré ANTHROPIC_API_KEY en los Secrets de Streamlit.")
    else:
        try:
            import anthropic
            cliente = anthropic.Anthropic(api_key=str(clave).strip())
            modelos = ([secreto("CLAUDE_MODEL")] if secreto("CLAUDE_MODEL") else []) + MODELOS_CLAUDE
            for modelo in modelos:
                try:
                    msj = cliente.messages.create(model=modelo, max_tokens=max_tokens,
                                                  messages=[{"role": "user", "content": prompt}])
                    return msj.content[0].text
                except Exception as e:
                    errores.append(f"{modelo}: {type(e).__name__}: {e}")
        except Exception as e:
            errores.append(f"No se pudo usar la librería anthropic: {type(e).__name__}: {e}")
    if DEBUG:
        st.error("🔧 Diagnóstico de la IA:\n\n" + "\n\n".join(errores))
    return None


def devolucion(resp, notas, perfil, aciertos):
    lineas = [f"Aciertos: {aciertos} de {len(PREGUNTAS)}. El país: {notas['eco']} de 5. Tu dinero: {notas['fin']} de 5. "
              f"Perfil: {perfil['nombre']}. Edad: {resp['edad']}.",
              f"Qué hace con el dinero que le sobra: {resp['dinero_que_sobra']}. Ahorra para la jubilación: {resp['ahorro_jubilacion']}. "
              f"Después del test siente que sabe: {resp['percepcion']}."]
    for p in PREGUNTAS:
        r = resp[p["id"]]
        if p["tipo"] == "numero":
            lineas.append(f"- {p['texto']} Respondió {r}. Dato real: {DATOS_REALES[p['id']]['valor']}.")
        else:
            lineas.append(f"- {p['texto']} Respondió \"{r}\": {'BIEN' if r == p['correcta'] else 'MAL'}.")
    prompt = f"""Sos una educadora financiera argentina: directa, desafiante y con algo de humor, nunca cruel.
Una persona acaba de hacer un test de economía y finanzas personales. Resultados:
{chr(10).join(lineas)}

Escribile una devolución personalizada en español rioplatense (voseo), de 100 a 130 palabras como máximo,
en 3 o 4 párrafos MUY cortos (de 1 a 3 líneas cada uno), porque se lee en el celular.
Hablale directo a ESA persona, como una amiga que sabe del tema: usá sus datos (su edad, qué hace con el dinero que le sobra,
si ahorra para la jubilación y cómo se sintió al terminar el test) para que sienta que el texto es sobre ella, no genérico.
1. Una primera frase con gancho que conecte su perfil con algo de su vida.
2. Lo más importante que se le escapó y por qué le importa, en una o dos frases.
3. Una acción concreta para esta semana, según lo que hoy hace con su dinero.
4. Un cierre cálido y corto que la deje con ganas de informarse más.
Ortografía: el nombre del país se escribe siempre con mayúscula (Argentina).
Sin títulos. Podés usar **negrita** para 2 o 3 ideas clave. Usá "dinero", no "plata".
No recomiendes productos, bancos ni empresas específicas. No opines de política."""
    respuesta = preguntar_a_claude(prompt)
    if respuesta:
        return respuesta
    # Respaldo sin IA: igual lo armamos con los datos de la persona
    flojo = "la economía del país" if notas["eco"] < notas["fin"] else "el manejo de tu dinero"
    fuerte = "el manejo de tu dinero" if flojo == "la economía del país" else "la economía del país"
    sobra = resp["dinero_que_sobra"].lower()
    texto = (f"Con {resp['edad']} años, acertaste {aciertos} de {len(PREGUNTAS)}: **te defendés mejor en {fuerte}**, "
             f"y donde más margen tenés es en **{flojo}**. ")
    if resp["percepcion"] != "Más de lo que pensaba":
        texto += ("Si terminaste sintiendo que sabés menos de lo que creías, ¡buenísimo!: es el primer paso, "
                  "y la mayoría ni se lo pregunta. ")
    texto += (f"Contaste que con el dinero que te sobra: *{sobra}*. Esta semana, hacé una sola cosa: fijate cuánto le rindió "
              "a ese dinero en el último año y comparalo con la inflación y con la vara del 5% en dólares. ")
    if resp["ahorro_jubilacion"] != "Sí":
        texto += "Y si todavía no ahorrás para tu jubilación, mirá la calculadora de abajo: empezar con poco hoy vale más que mucho mañana. "
    texto += "Repasá las explicaciones de cada pregunta: en 2 minutos sabés más que la mayoría. 🙌"
    return texto


def tarjeta_resultado(aciertos, notas, perfil):
    """Arma una imagen PNG con el resultado, para descargar."""
    import io
    import textwrap
    from PIL import Image, ImageDraw, ImageFont

    def fuente(tam, negrita=False):
        # Letra Inter (licencia libre OFL), guardada en la carpeta fonts/ para que se vean los acentos
        archivo = Path(__file__).parent / "fonts" / ("Inter-Bold.otf" if negrita else "Inter-Regular.otf")
        try:
            return ImageFont.truetype(str(archivo), tam)
        except Exception:
            return ImageFont.load_default()

    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), ESPRESSO)
    d = ImageDraw.Draw(img)
    x = 90
    d.text((x, 110), "ECONOMÍA EN 4 MINUTOS", font=fuente(34, True), fill=CARAMELO)
    d.text((x, 200), "Acerté", font=fuente(60), fill=CREMA)
    d.text((x, 270), f"{aciertos} de {len(PREGUNTAS)}", font=fuente(190, True), fill=CREMA)
    d.text((x, 520), f"Soy {perfil['nombre']}", font=fuente(68, True), fill=CARAMELO)
    y = 620
    for linea in textwrap.wrap(perfil["texto"], width=42):
        d.text((x, y), linea, font=fuente(38), fill="#D9CBBB")
        y += 52
    y += 50
    for etiqueta, n in [("El país", notas["eco"]), ("Tu dinero", notas["fin"])]:
        d.text((x, y), etiqueta, font=fuente(44), fill=CREMA)
        for k in range(POR_AREA):
            cx = x + 330 + k * 70
            d.ellipse((cx, y + 4, cx + 46, y + 50), fill=CARAMELO if k < n else None, outline=CARAMELO, width=4)
        d.text((x + 700, y), f"{n} de {POR_AREA}", font=fuente(44), fill=CREMA)
        y += 100
    d.line((x, 1130, W - x, 1130), fill="#5A4636", width=2)
    d.text((x, 1170), "¿Te animás a descubrir cuánto sabés?", font=fuente(40, True), fill=CREMA)
    d.text((x, 1230), LINK_APP.replace("https://", ""), font=fuente(40), fill=CARAMELO)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def sin_emojis(texto):
    """Las letras del PDF no tienen emojis: los sacamos (y también la negrita de markdown)."""
    import re
    texto = re.sub(r"[\U00010000-\U0010FFFF\u2600-\u27BF\uFE0F\u200D\u2B50\u2B06\u2194]", "", texto)
    return texto.replace("**", "").replace("*", "").replace("  ", " ").strip()


def imagen_cuadrado(notas):
    """Dibuja el cuadrado de perfiles con el punto de la persona (como imagen, para el PDF)."""
    import io
    from PIL import Image, ImageDraw, ImageFont
    fuente = lambda t: ImageFont.truetype(str(Path(__file__).parent / "fonts" / "DejaVuSans.ttf"), t)
    W = 800
    img = Image.new("RGB", (W, W), CREMA)
    d = ImageDraw.Draw(img)
    m, lado = 70, W - 110
    mitad = lado // 2
    zonas = [((0, 0), "#EADCCB", ("alto", "bajo")), ((1, 0), "#D9BC98", ("alto", "alto")),
             ((0, 1), "#F3EAE0", ("bajo", "bajo")), ((1, 1), "#E4CCAE", ("bajo", "alto"))]
    for (cx, cy), color, clave in zonas:
        x0, y0 = m + cx * mitad, 20 + cy * mitad
        d.rectangle((x0, y0, x0 + mitad, y0 + mitad), fill=color)
        d.text((x0 + 14, y0 + 12), PERFILES[clave]["nombre"], font=fuente(24), fill=CHOCOLATE)
    px = m + notas["fin"] / POR_AREA * lado
    py = 20 + lado - notas["eco"] / POR_AREA * lado
    px, py = min(max(px, m + 22), m + lado - 22), min(max(py, 42), 20 + lado - 22)
    d.ellipse((px - 18, py - 18, px + 18, py + 18), fill=ESPRESSO, outline="white", width=5)
    d.text((px + 26, py - 16), "VOS", font=fuente(28), fill=ESPRESSO)
    d.text((m + lado // 2 - 70, 20 + lado + 18), "Tu dinero →", font=fuente(26), fill=CHOCOLATE)
    eje = Image.new("RGBA", (220, 40), (0, 0, 0, 0))
    ImageDraw.Draw(eje).text((0, 0), "El país →", font=fuente(26), fill=CHOCOLATE)
    img.paste(eje.rotate(90, expand=True), (16, 20 + lado // 2 - 110), eje.rotate(90, expand=True))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def informe_pdf(resp, aciertos, notas, perfil, devolucion_texto, calculo):
    """Arma el informe en PDF: página 1 = tu resultado; página 2 = lo que aprendiste."""
    from fpdf import FPDF
    carpeta = Path(__file__).parent / "fonts"
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(True, margin=10)
    pdf.add_font("DejaVu", "", str(carpeta / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(carpeta / "DejaVuSans-Bold.ttf"))
    rgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    ancho = 180

    def titulo_seccion(texto):
        pdf.ln(4)
        pdf.set_font("DejaVu", "B", 13)
        pdf.set_text_color(*rgb(CARAMELO))
        pdf.cell(0, 8, texto.upper(), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*rgb(ESPRESSO))

    # ---------- Página 1: tu resultado ----------
    pdf.add_page()
    pdf.set_fill_color(*rgb(ESPRESSO))
    pdf.rect(0, 0, 210, 52, style="F")
    pdf.set_xy(15, 12)
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(*rgb(CARAMELO))
    pdf.cell(0, 6, f"ECONOMÍA EN 4 MINUTOS  ·  {datetime.now().strftime('%d/%m/%Y')}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(15)
    pdf.set_font("DejaVu", "B", 30)
    pdf.set_text_color(*rgb(CREMA))
    pdf.cell(0, 16, f"Acertaste {aciertos} de {len(PREGUNTAS)}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(15)
    pdf.set_font("DejaVu", "B", 16)
    pdf.set_text_color(*rgb(CARAMELO))
    pdf.cell(0, 10, f"Sos {perfil['nombre']}", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(60)
    pdf.set_text_color(*rgb(ESPRESSO))
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(ancho, 6, perfil["texto"])
    pdf.ln(2)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 7, f"Economía del país: {puntitos(notas['eco'])}  {notas['eco']} de {POR_AREA}      "
                   f"Tu dinero: {puntitos(notas['fin'])}  {notas['fin']} de {POR_AREA}", new_x="LMARGIN", new_y="NEXT")

    y_cuadrado = pdf.get_y() + 3
    pdf.image(imagen_cuadrado(notas), x=15, y=y_cuadrado, w=85)
    # Sobre vos, al lado del cuadrado
    pdf.set_xy(108, y_cuadrado)
    pdf.set_font("DejaVu", "B", 13)
    pdf.set_text_color(*rgb(CARAMELO))
    pdf.cell(0, 8, "SOBRE VOS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*rgb(ESPRESSO))
    datos = [("Edad", f"{resp['edad']} años"), ("Estudios", resp["educacion"]), ("Te informás por", resp["fuente_info"]),
             ("Con el dinero que te sobra", resp["dinero_que_sobra"]), ("¿Ahorrás para tu jubilación?", resp["ahorro_jubilacion"]),
             ("Al terminar, sentiste que sabés", resp["percepcion"])]
    for etiqueta, valor in datos:
        pdf.set_x(108)
        pdf.set_font("DejaVu", "B", 9)
        pdf.cell(0, 5, etiqueta, new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(108)
        pdf.set_font("DejaVu", "", 10)
        pdf.multi_cell(87, 5, valor)
        pdf.ln(1.5)

    pdf.set_y(max(pdf.get_y(), y_cuadrado + 88))
    titulo_seccion("Tu devolución")
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(ancho, 6, sin_emojis(devolucion_texto))
    titulo_seccion("Tu calculadora")
    pdf.set_font("DejaVu", "", 10.5)
    pdf.multi_cell(ancho, 5.6, f"Ahorrando USD {calculo['por_mes']} por mes al {calculo['tasa']}% anual, en {calculo['anios']} años "
                               f"tendrías USD {miles(calculo['total'])}: vos pondrías USD {miles(calculo['aportado'])} y la bola "
                               f"de nieve, USD {miles(calculo['intereses'])}.")
    pdf.ln(4)
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(*rgb(CHOCOLATE))
    pdf.multi_cell(ancho, 6, "No necesitás estudiar Economía para que la economía importe en tu vida. Pero sí necesitás "
                             "entenderla para que tus decisiones no dependan de la suerte.")
    pdf.ln(2)
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(*rgb(CARAMELO))
    pdf.cell(0, 6, f"¿Te animás a descubrir cuánto sabés? {LINK_APP}", new_x="LMARGIN", new_y="NEXT")

    # ---------- Página 2: lo que aprendiste ----------
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 22)
    pdf.set_text_color(*rgb(ESPRESSO))
    pdf.cell(0, 12, "Lo que aprendiste", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(*rgb("#7A6656"))
    pdf.cell(0, 6, "Los 10 conceptos del test, para releer cuando quieras.", new_x="LMARGIN", new_y="NEXT")
    for numero, p in enumerate(PREGUNTAS, start=1):
        concepto, puntos = APRENDIZAJES[p["id"]]
        pdf.ln(1.3)
        pdf.set_font("DejaVu", "B", 11)
        pdf.set_text_color(*rgb(CHOCOLATE))
        pdf.cell(0, 5.6, f"{numero}. {concepto}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*rgb(ESPRESSO))
        pdf.set_font("DejaVu", "", 9.5)
        for punto in puntos:
            pdf.set_x(18)
            pdf.cell(5, 4.5, "•")
            pdf.multi_cell(ancho - 8, 4.5, punto, align="L", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


def responder_consulta(texto, edad, aciertos):
    guardar({"fecha": datetime.now().isoformat(timespec="seconds"), "edad": edad, "aciertos": aciertos,
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
TOTAL_PANTALLAS = len(PREGUNTAS) + 2   # + jubilación + percepción

if "paso" not in st.session_state:
    st.session_state.paso = "inicio"     # inicio → sobre_vos → preguntas → jubilacion → percepcion → resultado
    st.session_state.resp = {}
    st.session_state.i = 0
    st.session_state.revelar = False
    st.session_state.guardado = False
    st.session_state.consultas = []
    st.session_state.historial = []   # aciertos de cada pregunta respondida, para la racha


def ir_a(paso):
    st.session_state.paso = paso
    st.rerun()


def pregunta_simple(numero, etiqueta, texto, opciones, clave, siguiente, boton):
    """Pantalla de una pregunta sin puntaje (jubilación y percepción)."""
    st.progress(numero / TOTAL_PANTALLAS, text=f"Pregunta {numero} de {TOTAL_PANTALLAS}")
    st.markdown(f"<div class='etiqueta'>{etiqueta}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pregunta'>{texto}</div>", unsafe_allow_html=True)
    with st.form(clave):
        valor = st.radio("Respuesta", opciones, index=None, label_visibility="collapsed")
        st.write("")
        if st.form_submit_button(boton, type="primary", use_container_width=True):
            if valor is None:
                st.error("Respondé para seguir.")
            else:
                st.session_state.resp[clave] = valor
                ir_a(siguiente)


# ---------- INICIO ----------
if st.session_state.paso == "inicio":
    st.markdown(f"""<div class='hero-arriba'><div class='hero-grilla'>
        <div class='hero-texto'>
          <div class='kicker'>Economía en 4 minutos</div>
          <h1>¿Te animás a descubrir cuánto sabés realmente de economía?</h1>
          <p>Todos opinamos de economía. Todos creemos que manejamos bien nuestro dinero.</p>
          <p class='oro'>En 4 minutos vas a saber si es cierto.</p>
          <div class='chips'><span class='chip'>⏱ 4 minutos</span><span class='chip'>🔒 Anónimo</span><span class='chip'>🚫 Sin Google</span></div>
        </div>
        <div class='ilus ilus-compu'>{ILUSTRACION}</div>
        </div></div>""", unsafe_allow_html=True)
    with st.container(key="boton_gigante"):
        if st.button("EMPEZAR EL TEST →", type="primary", use_container_width=True):
            ir_a("sobre_vos")
    st.markdown(f"<div class='hero-abajo'><div class='ilus ilus-celu'>{ILUSTRACION}</div></div>", unsafe_allow_html=True)

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
    st.progress((i + 1) / TOTAL_PANTALLAS, text=f"Pregunta {i + 1} de {TOTAL_PANTALLAS}")
    # La racha: ✅/❌ de lo respondido y ○ de lo que falta; si van 3 o más seguidas bien, se festeja
    historial = st.session_state.historial
    marcas = "".join("✅" if ok else "❌" for ok in historial) + "○" * (len(PREGUNTAS) - len(historial))
    seguidas = 0
    for ok in reversed(historial):
        if not ok:
            break
        seguidas += 1
    fuego = f"<span class='racha-fuego'>🔥 ¡{seguidas} seguidas!</span>" if seguidas >= 3 else ""
    st.markdown(f"<div class='racha'>{marcas}{fuego}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='etiqueta'>{p['bloque']}</div><div class='titulo-preg'>{p['titulo']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pregunta'>{p['texto']}</div>", unsafe_allow_html=True)

    if not st.session_state.revelar:
        with st.form(f"q_{p['id']}"):
            if p["tipo"] == "numero":
                # Sin valor inicial a propósito: un número precargado "sopla" la respuesta (sesgo de anclaje)
                unidad = (p["prefijo"] + p["sufijo"]).strip()
                valor = st.number_input(f"Tu respuesta ({unidad})", min_value=0.0, max_value=float(p["max"]), value=None,
                                        step=p["paso"], format="%g", placeholder="Escribí un número")
            else:
                valor = st.radio("Respuesta", opciones_mezcladas(p), index=None, label_visibility="collapsed")
            st.write("")
            if st.form_submit_button("Responder", type="primary", use_container_width=True):
                if valor is None:
                    st.error("Respondé para seguir.")
                else:
                    st.session_state.resp[p["id"]] = valor
                    st.session_state.historial.append(acerto(p, valor))
                    st.session_state.revelar = True
                    st.rerun()
    else:
        r = st.session_state.resp[p["id"]]
        if p["tipo"] == "numero":
            real = DATOS_REALES[p["id"]]["valor"]
            if r == real:
                st.markdown("<div class='ok'>¡Exacto! 🎯</div>", unsafe_allow_html=True)
            elif acerto(p, r):
                st.markdown("<div class='ok'>¡Muy cerca! ✅</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='mal'>{'Te pasaste' if r > real else 'Te quedaste corto/a'} ❌</div>", unsafe_allow_html=True)
            st.plotly_chart(grafico_linea(p, r, real), use_container_width=True, config={"displayModeBar": False, "staticPlot": True})
            st.markdown(f"<div class='letra-chica'>Fuente: {DATOS_REALES[p['id']]['fuente']}</div>", unsafe_allow_html=True)
        else:
            if r == p["correcta"]:
                st.markdown("<div class='ok'>¡Bien ahí! ✅</div>", unsafe_allow_html=True)
            elif r == "No sé":
                st.markdown(f"<div class='neutro'>¡Jajaja, gracias por la honestidad! 🙌</div><p>Acá te lo explico. "
                            f"La respuesta es: <b>{p['correcta']}</b></p>", unsafe_allow_html=True)
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

# ---------- SIN PUNTAJE: JUBILACIÓN Y PERCEPCIÓN ----------
elif st.session_state.paso == "jubilacion":
    pregunta_simple(len(PREGUNTAS) + 1, "Casi terminamos", "¿Estás ahorrando por tu cuenta para cuando te jubiles?",
                    ["Sí", "Todavía no, pero quiero", "No lo había pensado"], "ahorro_jubilacion", "percepcion", "Seguir →")

elif st.session_state.paso == "percepcion":
    pregunta_simple(TOTAL_PANTALLAS, "Última", "Después de hacer este test, ¿cuánto sentís que sabés realmente de economía y finanzas?",
                    PERCEPCION, "percepcion", "resultado", "Ver mi resultado →")

# ---------- RESULTADO ----------
elif st.session_state.paso == "resultado":
    resp = st.session_state.resp
    notas = calcular_notas(resp)
    perfil = elegir_perfil(notas)
    aciertos = sum(acerto(p, resp[p["id"]]) for p in PREGUNTAS)

    if not st.session_state.guardado:
        guardar({"fecha": datetime.now().isoformat(timespec="seconds"), **resp, "aciertos": aciertos,
                 "nota_pais": notas["eco"], "nota_dinero": notas["fin"], "perfil": perfil["nombre"]})
        st.session_state.guardado = True

    st.markdown("<div class='etiqueta'>Tu resultado</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='puntaje'>{aciertos} de {len(PREGUNTAS)}</div>", unsafe_allow_html=True)
    st.markdown("<div class='letra-chica'>respuestas acertadas</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='perfil'>{perfil['emoji']} Sos {perfil['nombre']}</div>", unsafe_allow_html=True)
    st.markdown(perfil["texto"])
    st.markdown(f"""<div class='notas'>
        <div class='nota'>🇦🇷 Economía del país<br><span class='puntos'>{puntitos(notas['eco'])}</span> <b>{notas['eco']}</b> de {POR_AREA}</div>
        <div class='nota'>💰 Tu dinero<br><span class='puntos'>{puntitos(notas['fin'])}</span> <b>{notas['fin']}</b> de {POR_AREA}</div></div>""",
                unsafe_allow_html=True)

    st.markdown("<div class='seccion'>Dónde estás parado/a</div>", unsafe_allow_html=True)
    st.plotly_chart(grafico_cuadrado(notas), use_container_width=True, config={"displayModeBar": False, "staticPlot": True})

    if "devolucion" not in st.session_state:
        with st.spinner("Analizando tus respuestas..."):
            st.session_state.devolucion = devolucion(resp, notas, perfil, aciertos)
    st.markdown("<div class='seccion'>Tu devolución</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(st.session_state.devolucion)


    # ----- Cierre: los números no cierran + calculadora de inversión -----
    edad = resp["edad"]
    st.markdown("<div class='seccion'>🥩 ¿Te acordás del asado?</div>", unsafe_allow_html=True)
    st.markdown("<div class='destacado'>Solo 5 de cada 10 aportan. Y además, cada vez hay menos trabajadores por cada jubilado. "
                "<b>Los números no cierran.</b> ¿Quién va a pagar tu jubilación?</div>", unsafe_allow_html=True)
    if edad < 30:
        cierre = "⛄ <b>La buena noticia:</b> tenés a tu favor lo que más pesa en la bola de nieve, que es <b>el tiempo</b>."
    elif edad < 50:
        cierre = "⛄ <b>Nunca es tarde, pero cada año cuenta.</b> La bola de nieve necesita tiempo para crecer."
    else:
        cierre = "⛄ <b>Es momento de ordenar y proteger lo que ahorraste,</b> y de que cada peso que sumes trabaje para vos."
    st.markdown(f"<div class='destacado'>{cierre}</div>", unsafe_allow_html=True)

    st.markdown("<div class='seccion'>🧮 Calculadora de inversión</div>", unsafe_allow_html=True)
    st.markdown("<div class='pista'>👉 Mové las barritas ← → y mirá cómo crece tu dinero</div>", unsafe_allow_html=True)
    anios = max(65 - edad, 10)   # hasta los 65; si falta poco, mostramos 10 años
    c1, c2 = st.columns(2)
    c1.markdown("<div class='emoji-calc'>💵</div>", unsafe_allow_html=True)
    por_mes = c1.slider("¿Cuánto podrías ahorrar por mes? (USD)", min_value=5, max_value=500, value=50, step=5)
    c2.markdown("<div class='emoji-calc'>📈</div>", unsafe_allow_html=True)
    tasa = c2.slider("¿A qué tasa anual en dólares?", min_value=2, max_value=8, value=5, step=1, format="%d%%")
    st.markdown("<div class='letra-chica'>5% ≈ la vara (bono del Tesoro de EE.UU.) · 7% ≈ lo que rindió históricamente "
                "la bolsa de EE.UU. después de la inflación, con más riesgo.</div>", unsafe_allow_html=True)
    tabla = simular_ahorro(por_mes, anios, tasa / 100)
    final = tabla.iloc[-1]
    m1, m2 = st.columns(2)
    m1.metric(f"En {anios} años tendrías", f"USD {miles(final['total'])}")
    if anios >= 20:
        m2.metric("Si esperás 10 años para empezar", f"USD {miles(simular_ahorro(por_mes, anios - 10, tasa / 100).iloc[-1]['total'])}")
    st.markdown(f"Vos pusiste **USD {miles(final['aportado'])}**. La bola de nieve puso **USD {miles(final['intereses'])}**. ⛄")
    st.plotly_chart(grafico_crecimiento(tabla), use_container_width=True, config={"displayModeBar": False, "staticPlot": True})
    calculo = {"por_mes": por_mes, "tasa": tasa, "anios": anios, "total": final["total"],
               "aportado": final["aportado"], "intereses": final["intereses"]}
    st.markdown("💡 **No hace falta mucho:** empezar con el 5 o 10% de tu sueldo ya hace la diferencia. "
                "Informate, preguntale a alguien que sepa, investigá. **Lo importante es arrancar.**")

    st.markdown("<div class='frase'>No necesitás estudiar Economía para que la economía importe en tu vida. "
                "<span>Pero sí necesitás entenderla para que tus decisiones no dependan de la suerte.</span></div>",
                unsafe_allow_html=True)

    # ----- Descargas: informe completo (PDF) y tarjeta para compartir (imagen) -----
    st.markdown("<div class='seccion'>📥 Llevate tu resultado</div>", unsafe_allow_html=True)
    st.markdown("Un informe con tu resultado, tu devolución y **todo lo que aprendiste**, para releer cuando quieras.")
    d1, d2 = st.columns(2)
    d1.download_button("📄 Informe completo (PDF)", data=informe_pdf(resp, aciertos, notas, perfil, st.session_state.devolucion, calculo),
                       file_name="mi-informe-economia-en-4-minutos.pdf", mime="application/pdf", use_container_width=True, type="primary")
    d2.download_button("🖼️ Tarjeta para compartir", data=tarjeta_resultado(aciertos, notas, perfil),
                       file_name="mi-resultado-economia-en-4-minutos.png", mime="image/png", use_container_width=True)

    # ----- Compartir por WhatsApp -----
    st.markdown("<div class='seccion'>¿Te animás a desafiar a alguien?</div>", unsafe_allow_html=True)
    mensaje = ("¿Te animás a descubrir cuánto sabés realmente de economía? Yo ya lo hice y me dejó pensando. "
               f"Son 4 minutos: {LINK_APP}")
    enlace = "https://wa.me/?text=" + urllib.parse.quote(mensaje)
    st.markdown(f"<a class='boton-wa' href='{enlace}' target='_blank'>{ICONO_WHATSAPP}"
                "Desafiá a alguien por WhatsApp</a>", unsafe_allow_html=True)

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
                responder_consulta(sugerencia, edad, aciertos)
                st.rerun()
        with st.form("consulta", clear_on_submit=True):
            consulta = st.text_area("Tu pregunta", placeholder="Escribí tu pregunta acá...", max_chars=300,
                                    label_visibility="collapsed")
            if st.form_submit_button("Preguntar", type="primary", use_container_width=True) and consulta.strip():
                responder_consulta(consulta.strip(), edad, aciertos)
                st.rerun()
    else:
        st.info("Llegaste al máximo de 3 preguntas. ¡Gracias por participar!")

    for pregunta, respuesta in reversed(st.session_state.consultas):
        with st.container(border=True):
            st.markdown(f"**Tu pregunta:** {pregunta}")
            st.markdown(respuesta)

    st.markdown("<div class='letra-chica'>Podés hacer hasta 3 preguntas. Las respuestas son educativas: para decisiones "
                "importantes con tu dinero, consultá con un profesional.</div>", unsafe_allow_html=True)
