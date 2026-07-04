import requests
from datetime import datetime, timedelta
import pytz
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ===== CONFIGURACIÓN =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
ZONA_HORARIA = pytz.timezone("America/Mexico_City")

print("=" * 50)
print("🤖 INICIANDO BOT DE FÚTBOL")
print("=" * 50)

if not TELEGRAM_TOKEN:
    print("❌ ERROR: TELEGRAM_TOKEN no está configurado")
    exit(1)
else:
    print(f"✅ TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10]}... (configurado)")

if not API_FOOTBALL_KEY:
    print("⚠️ ADVERTENCIA: API_FOOTBALL_KEY no está configurado")
else:
    print(f"✅ API_FOOTBALL_KEY: {API_FOOTBALL_KEY[:10]}... (configurado)")

def obtener_partidos():
    if not API_FOOTBALL_KEY:
        return "❌ API Key no configurada."
    
    hoy = datetime.now(ZONA_HORARIA).strftime("%Y-%m-%d")
    print(f"📅 Buscando partidos para: {hoy}")
    
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
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"📡 Respuesta API: {response.status_code}")
        
        if response.status_code != 200:
            return f"❌ Error en API: Código {response.status_code}"
        
        data = response.json()
        
        if not data.get("response"):
            return "📭 No hay partidos programados para hoy."
        
        mensaje = f"⚽ PARTIDOS DE HOY ({hoy})\n\n"
        
        for partido in data["response"][:10]:
            local = partido["teams"]["home"]["name"]
            visitante = partido["teams"]["away"]["name"]
            fecha_str = partido["fixture"]["date"]
            fecha_dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
            hora = fecha_dt.astimezone(ZONA_HORARIA).strftime("%H:%M")
            liga = partido["league"]["name"]
            mensaje += f"🕐 {hora} | {liga}\n🏠 {local} vs {visitante}\n\n"
        
        return mensaje
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return f"❌ Error: {str(e)}"

# ===== COMANDOS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ ¡Hola! Soy tu bot de partidos de fútbol.\n\n"
        "Comandos:\n"
        "/partidos - Ver partidos de hoy\n"
        "/manana - Ver partidos de mañana\n"
        "/test - Verificar que el bot funciona"
    )

async def partidos_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📨 Comando /partidos de {update.effective_user.username or update.effective_user.id}")
    mensaje = obtener_partidos()
    await update.message.reply_text(mensaje)
    print("✅ Mensaje enviado")

async def partidos_manana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not API_FOOTBALL_KEY:
        await update.message.reply_text("❌ API Key no configurada")
        return
    
    manana = datetime.now(ZONA_HORARIA) + timedelta(days=1)
    fecha = manana.strftime("%Y-%m-%d")
    
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "x-rapidapi-key": API_FOOTBALL_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    params = {"date": fecha, "timezone": "America/Mexico_City"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        
        if data.get("response"):
            mensaje = f"⚽ PARTIDOS DE MAÑANA ({fecha})\n\n"
            for partido in data["response"][:10]:
                local = partido["teams"]["home"]["name"]
                visitante = partido["teams"]["away"]["name"]
                fecha_str = partido["fixture"]["date"]
                fecha_dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
                hora = fecha_dt.astimezone(ZONA_HORARIA).strftime("%H:%M")
                liga = partido["league"]["name"]
                mensaje += f"🕐 {hora} | {liga}\n🏠 {local} vs {visitante}\n\n"
            await update.message.reply_text(mensaje)
        else:
            await update.message.reply_text("📭 No hay partidos programados para mañana.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ ¡El bot funciona!\n\n"
        f"📅 {datetime.now(ZONA_HORARIA).strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"🔑 API Key: {'✅' if API_FOOTBALL_KEY else '❌'}"
    )

# ===== MAIN =====
def main():
    print("🚀 Inicializando aplicación...")
    
    try:
        # Crear la aplicación
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Registrar comandos
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("partidos", partidos_hoy))
        application.add_handler(CommandHandler("manana", partidos_manana))
        application.add_handler(CommandHandler("test", test))
        
        print("✅ Bot configurado correctamente")
        print("🤖 Bot iniciado. Esperando comandos...")
        print("=" * 50)
        
        # Iniciar el bot con polling
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
