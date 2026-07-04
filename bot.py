import requests
from datetime import datetime
import pytz
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ===== CONFIGURACIÓN =====
TELEGRAM_TOKEN = os.environ.get("8650824122:AAHx6VBLmgD2w63bXwZtWtAsvXLrGpcqT00")
API_FOOTBALL_KEY = os.environ.get("52398562f6973bad35a0020660360e11")
ZONA_HORARIA = pytz.timezone("America/Mexico_City")

# ===== FUNCIÓN PARA OBTENER PARTIDOS =====
def obtener_partidos():
    hoy = datetime.now(ZONA_HORARIA).strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "x-rapidapi-key": API_FOOTBALL_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    params = {
        "date": hoy,
        "timezone": "America/Mexico_City"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if data["response"]:
            mensaje = f"⚽ PARTIDOS DE HOY ({hoy})\n\n"
            for partido in data["response"]:
                local = partido["teams"]["home"]["name"]
                visitante = partido["teams"]["away"]["name"]
                hora = partido["fixture"]["date"]
                hora_dt = datetime.fromisoformat(hora.replace("Z", "+00:00"))
                hora_local = hora_dt.astimezone(ZONA_HORARIA).strftime("%H:%M")
                liga = partido["league"]["name"]
                
                mensaje += f"🕐 {hora_local} | {liga}\n"
                mensaje += f"🏠 {local} vs {visitante}\n\n"
            return mensaje
        else:
            return "📭 No hay partidos programados para hoy."
    
    except Exception as e:
        return f"❌ Error al obtener partidos: {str(e)}"

# ===== COMANDOS DEL BOT =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Mensaje de bienvenida"""
    await update.message.reply_text(
        "¡Hola! Soy tu bot de partidos de fútbol ⚽\n\n"
        "Usa /partidos para ver los partidos de hoy\n"
        "Usa /partidos_manana para ver los de mañana\n"
        "Usa /liga [nombre] para buscar partidos de una liga específica"
    )

async def partidos_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /partidos - Muestra los partidos de hoy"""
    mensaje = obtener_partidos()
    await update.message.reply_text(mensaje)

async def partidos_manana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /partidos_manana - Muestra los partidos de mañana"""
    manana = datetime.now(ZONA_HORARIA) + timedelta(days=1)
    fecha = manana.strftime("%Y-%m-%d")
    
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-rapidapi-key": API_FOOTBALL_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
    params = {"date": fecha, "timezone": "America/Mexico_City"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if data["response"]:
            mensaje = f"⚽ PARTIDOS DE MAÑANA ({fecha})\n\n"
            for partido in data["response"]:
                local = partido["teams"]["home"]["name"]
                visitante = partido["teams"]["away"]["name"]
                hora = partido["fixture"]["date"]
                hora_dt = datetime.fromisoformat(hora.replace("Z", "+00:00"))
                hora_local = hora_dt.astimezone(ZONA_HORARIA).strftime("%H:%M")
                liga = partido["league"]["name"]
                
                mensaje += f"🕐 {hora_local} | {liga}\n"
                mensaje += f"🏠 {local} vs {visitante}\n\n"
            await update.message.reply_text(mensaje)
        else:
            await update.message.reply_text("📭 No hay partidos programados para mañana.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def liga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /liga [nombre] - Busca partidos de una liga específica"""
    if not context.args:
        await update.message.reply_text(
            "❌ Por favor especifica el nombre de la liga.\n"
            "Ejemplo: /liga Liga MX\n"
            "Ejemplo: /liga Premier League"
        )
        return
    
    nombre_liga = " ".join(context.args)
    hoy = datetime.now(ZONA_HORARIA).strftime("%Y-%m-%d")
    
    # Primero buscamos el ID de la liga
    url_liga = "https://v3.football.api-sports.io/leagues"
    headers = {"x-rapidapi-key": API_FOOTBALL_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
    params_liga = {"name": nombre_liga}
    
    try:
        response_liga = requests.get(url_liga, headers=headers, params=params_liga)
        data_liga = response_liga.json()
        
        if not data_liga["response"]:
            await update.message.reply_text(f"❌ No encontré la liga: {nombre_liga}")
            return
        
        league_id = data_liga["response"][0]["league"]["id"]
        league_name = data_liga["response"][0]["league"]["name"]
        
        # Buscamos partidos de esa liga
        url_partidos = "https://v3.football.api-sports.io/fixtures"
        params_partidos = {
            "date": hoy,
            "league": league_id,
            "timezone": "America/Mexico_City"
        }
        
        response_partidos = requests.get(url_partidos, headers=headers, params=params_partidos)
        data_partidos = response_partidos.json()
        
        if data_partidos["response"]:
            mensaje = f"⚽ PARTIDOS DE {league_name.upper()} ({hoy})\n\n"
            for partido in data_partidos["response"]:
                local = partido["teams"]["home"]["name"]
                visitante = partido["teams"]["away"]["name"]
                hora = partido["fixture"]["date"]
                hora_dt = datetime.fromisoformat(hora.replace("Z", "+00:00"))
                hora_local = hora_dt.astimezone(ZONA_HORARIA).strftime("%H:%M")
                
                mensaje += f"🕐 {hora_local} | {local} vs {visitante}\n"
            
            await update.message.reply_text(mensaje)
        else:
            await update.message.reply_text(f"📭 No hay partidos de {league_name} para hoy.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ===== MAIN =====
def main():
    """Inicia el bot"""
    # Crear la aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("partidos", partidos_hoy))
    application.add_handler(CommandHandler("partidos_manana", partidos_manana))
    application.add_handler(CommandHandler("liga", liga))
    
    # Iniciar el bot (con polling)
    print("🤖 Bot iniciado... Esperando comandos")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()