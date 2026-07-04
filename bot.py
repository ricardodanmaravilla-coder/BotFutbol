# -*- coding: utf-8 -*-
import requests
from datetime import datetime, timedelta
import pytz
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ===== CONFIGURACION =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
ZONA_HORARIA = pytz.timezone("America/Mexico_City")

# IDs de las 5 grandes ligas + Mundial
LIGAS_PERMITIDAS = {
    39: "[ING] Premier League",
    140: "[ESP] LaLiga",
    135: "[ITA] Serie A",
    78: "[GER] Bundesliga",
    61: "[FRA] Ligue 1",
    1: "[MUNDIAL] World Cup"
}

print("=" * 50)
print("INICIANDO BOT DE FUTBOL - 5 GRANDES LIGAS")
print("=" * 50)

if not TELEGRAM_TOKEN:
    print("ERROR: TELEGRAM_TOKEN no esta configurado")
    exit(1)
else:
    print(f"TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10]}... (configurado)")

if not API_FOOTBALL_KEY:
    print("ADVERTENCIA: API_FOOTBALL_KEY no esta configurado")
else:
    print(f"API_FOOTBALL_KEY: {API_FOOTBALL_KEY[:10]}... (configurado)")

print(f"Ligas configuradas: {len(LIGAS_PERMITIDAS)}")
for nombre in LIGAS_PERMITIDAS.values():
    print(f"   - {nombre}")

def obtener_partidos_filtrados(fecha=None, liga_id=None):
    """Obtiene partidos de las 5 grandes ligas + Mundial"""
    if not API_FOOTBALL_KEY:
        return "ERROR: API Key no configurada."
    
    if fecha is None:
        fecha = datetime.now(ZONA_HORARIA).strftime("%Y-%m-%d")
    
    print(f"Buscando partidos para: {fecha}")
    
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "x-rapidapi-key": API_FOOTBALL_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    
    mensaje = ""
    total_partidos = 0
    
    ligas_a_buscar = [liga_id] if liga_id else LIGAS_PERMITIDAS.keys()
    
    for lid in ligas_a_buscar:
        if lid not in LIGAS_PERMITIDAS:
            continue
            
        nombre_liga = LIGAS_PERMITIDAS[lid]
        
        params = {
            "date": fecha,
            "league": lid,
            "timezone": "America/Mexico_City"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("response"):
                    if not mensaje:
                        mensaje = f"PARTIDOS DE {fecha}\n"
                        mensaje += "=" * 40 + "\n\n"
                    
                    mensaje += f"LIGA: {nombre_liga}\n"
                    mensaje += "-" * 30 + "\n"
                    
                    for partido in data["response"]:
                        local = partido["teams"]["home"]["name"]
                        visitante = partido["teams"]["away"]["name"]
                        
                        fecha_str = partido["fixture"]["date"]
                        fecha_dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
                        hora = fecha_dt.astimezone(ZONA_HORARIA).strftime("%H:%M")
                        
                        mensaje += f"{hora} | {local} vs {visitante}\n"
                        total_partidos += 1
                    
                    mensaje += "\n"
                    
        except Exception as e:
            print(f"Error en liga {lid}: {e}")
    
    if not mensaje:
        return f"No hay partidos de las 5 grandes ligas ni Mundial para {fecha}."
    
    mensaje += f"Total: {total_partidos} partidos"
    return mensaje

# ===== COMANDOS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola! Soy tu bot de las 5 grandes ligas.\n\n"
        "Ligas disponibles:\n"
        "- Premier League\n"
        "- LaLiga\n"
        "- Serie A\n"
        "- Bundesliga\n"
        "- Ligue 1\n"
        "- Mundial / World Cup\n\n"
        "Comandos:\n"
        "/partidos - Ver partidos de hoy\n"
        "/manana - Ver partidos de manana\n"
        "/liga [nombre] - Ver partidos de una liga especifica\n"
        "/test - Verificar que el bot funciona\n\n"
        "Ejemplos:\n"
        "/liga Premier League\n"
        "/liga LaLiga"
    )

async def partidos_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Comando /partidos de {update.effective_user.username or update.effective_user.id}")
    mensaje = obtener_partidos_filtrados()
    await update.message.reply_text(mensaje)
    print("Mensaje enviado")

async def partidos_manana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Comando /manana de {update.effective_user.username or update.effective_user.id}")
    manana = datetime.now(ZONA_HORARIA) + timedelta(days=1)
    fecha = manana.strftime("%Y-%m-%d")
    mensaje = obtener_partidos_filtrados(fecha)
    await update.message.reply_text(mensaje)
    print("Mensaje enviado")

async def liga_especifica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /liga [nombre] - Busca partidos de una liga especifica"""
    if not context.args:
        await update.message.reply_text(
            "Por favor especifica el nombre de la liga.\n\n"
            "Opciones disponibles:\n"
            "- Premier League\n"
            "- LaLiga\n"
            "- Serie A\n"
            "- Bundesliga\n"
            "- Ligue 1\n"
            "- Mundial\n\n"
            "Ejemplo: /liga Premier League"
        )
        return
    
    nombre_busqueda = " ".join(context.args).lower()
    
    map_nombres = {
        "premier": 39,
        "premier league": 39,
        "inglaterra": 39,
        "laliga": 140,
        "la liga": 140,
        "espana": 140,
        "serie a": 135,
        "serie": 135,
        "italia": 135,
        "bundesliga": 78,
        "alemania": 78,
        "ligue 1": 61,
        "ligue": 61,
        "francia": 61,
        "mundial": 1,
        "world cup": 1,
        "copa del mundo": 1
    }
    
    liga_id = None
    for key, value in map_nombres.items():
        if key in nombre_busqueda:
            liga_id = value
            break
    
    if not liga_id:
        await update.message.reply_text(
            f"No encontre la liga: {nombre_busqueda}\n\n"
            "Opciones disponibles:\n"
            "- Premier League\n"
            "- LaLiga\n"
            "- Serie A\n"
            "- Bundesliga\n"
            "- Ligue 1\n"
            "- Mundial"
        )
        return
    
    hoy = datetime.now(ZONA_HORARIA).strftime("%Y-%m-%d")
    mensaje = obtener_partidos_filtrados(hoy, liga_id)
    await update.message.reply_text(mensaje)

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "El bot funciona correctamente!\n\n"
        f"Fecha: {datetime.now(ZONA_HORARIA).strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"API Key: {'Configurada' if API_FOOTBALL_KEY else 'No configurada'}\n"
        f"Ligas configuradas: {len(LIGAS_PERMITIDAS)}"
    )

# ===== MAIN =====
def main():
    print("Inicializando aplicacion...")
    
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("partidos", partidos_hoy))
        application.add_handler(CommandHandler("manana", partidos_manana))
        application.add_handler(CommandHandler("liga", liga_especifica))
        application.add_handler(CommandHandler("test", test))
        
        print("Bot configurado correctamente")
        print("Bot iniciado. Esperando comandos...")
        print("=" * 50)
        
        application.run_polling()
        
    except Exception as e:
        print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
