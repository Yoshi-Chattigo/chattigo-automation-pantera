import os
import json
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord.ext import commands
from discord import app_commands

from google.cloud.devtools import cloudbuild_v1
from google.oauth2 import service_account
from google.cloud import storage

from datetime import datetime

# ===============================
# CONFIG (ENV VARS PARA CLOUD RUN)
# ===============================

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

PROJECT_ID = "automation-chattigo"
BUCKET = "qa-allure-report-storage-automation"

# Service Account desde archivo incluido en el contenedor
credentials = service_account.Credentials.from_service_account_file(
    "service-account.json"
)

storage_client = storage.Client(
    project=PROJECT_ID,
    credentials=credentials
)

# ===============================
# DISCORD BOT
# ===============================

intents = discord.Intents.default()
intents.message_content = True  # necesario para slash commands

bot = commands.Bot(command_prefix="/", intents=intents)


# ===============================
# EMBED FINAL
# ===============================

async def enviar_resultado_embed(ambiente, perfil, passed, failed, porcentaje, fecha, public_url):

    color = 0x2ecc71 if failed == 0 else 0xe74c3c

    embed = discord.Embed(
        title=f"📊 Pruebas finalizadas — {ambiente} / {perfil}",
        description=(
            f"🟢 **Pasadas:** {passed}\n"
            f"🔴 **Fallidas:** {failed}\n"
            f"📈 **Éxito:** {porcentaje:.2f}%\n"
            f"📅 **Fecha:** {fecha}"
        ),
        color=color
    )

    embed.set_footer(text="Chattigo QA Automation")

    class ReporteButton(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Ver Reporte Allure",
            style=discord.ButtonStyle.link,
            url=public_url
        )
        async def reporte(self, interaction, button):
            pass

    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(embed=embed, view=ReporteButton())


# ===============================
# READ SUMMARY.JSON
# ===============================

def leer_resultados_allure(ambiente, perfil):

    ruta = f"{ambiente}/{perfil}/summary.json"
    bucket = storage_client.bucket(BUCKET)
    blob = bucket.blob(ruta)

    if not blob.exists():
        print("⚠ summary.json NO encontrado:", ruta)
        return 0, 0, 0

    data = json.loads(blob.download_as_text())

    passed = data["statistic"]["passed"]
    failed = data["statistic"]["failed"]
    total = passed + failed
    porcentaje = (passed / total * 100) if total > 0 else 0

    return passed, failed, porcentaje


# ===============================
# CLOUD BUILD EXECUTION
# ===============================

async def ejecutar_en_cloud_build(ambiente, perfil):

    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(f"🏗️ Enviando ejecución a Cloud Build para `{ambiente}` / `{perfil}`...")

    client = cloudbuild_v1.CloudBuildClient(credentials=credentials)

    build = cloudbuild_v1.Build(
        substitutions={
            "_ENV": ambiente,
            "_PROFILE": perfil
        }
    )

    op = client.create_build(project_id=PROJECT_ID, build=build)

    status_msg = await channel.send("⏳ Ejecutando pruebas en Cloud Build...")

    while not op.done():
        await asyncio.sleep(6)
        await status_msg.edit(content="⏳ Cloud Build sigue ejecutando...")

    _ = op.result()

    public_url = (
        f"https://storage.googleapis.com/{BUCKET}/"
        f"{ambiente}/{perfil}/allure-report/index.html"
    )

    passed, failed, porcentaje = leer_resultados_allure(ambiente, perfil)

    fecha = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    await enviar_resultado_embed(
        ambiente, perfil, passed, failed, porcentaje, fecha, public_url
    )


# ===============================
# BUTTON PERFILES
# ===============================

class PerfilView(discord.ui.View):
    def __init__(self, ambiente):
        super().__init__(timeout=120)
        self.ambiente = ambiente

    @discord.ui.button(label="agente", style=discord.ButtonStyle.success)
    async def agente(self, interaction, button):
        await interaction.response.send_message(f"Ejecutando agente en {self.ambiente}…", ephemeral=True)
        await ejecutar_en_cloud_build(self.ambiente, "agente")

    @discord.ui.button(label="bot", style=discord.ButtonStyle.primary)
    async def bot(self, interaction, button):
        await interaction.response.send_message(f"Ejecutando bot en {self.ambiente}…", ephemeral=True)
        await ejecutar_en_cloud_build(self.ambiente, "bot")

    @discord.ui.button(label="supervisor", style=discord.ButtonStyle.secondary)
    async def supervisor(self, interaction, button):
        await interaction.response.send_message(f"Ejecutando supervisor en {self.ambiente}…", ephemeral=True)
        await ejecutar_en_cloud_build(self.ambiente, "supervisor")


async def mostrar_selector_perfil(interaction, ambiente):
    await interaction.response.send_message(
        f"🌍 Ambiente seleccionado: `{ambiente}`\nSelecciona el perfil:",
        view=PerfilView(ambiente)
    )


# ===============================
# BUTTON AMBIENTES
# ===============================

class AmbienteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="pantera", style=discord.ButtonStyle.primary)
    async def pantera(self, interaction, button):
        await mostrar_selector_perfil(interaction, "pantera")

    @discord.ui.button(label="leones", style=discord.ButtonStyle.primary)
    async def leones(self, interaction, button):
        await mostrar_selector_perfil(interaction, "leones")

    @discord.ui.button(label="bugs", style=discord.ButtonStyle.danger)
    async def bugs(self, interaction, button):
        await mostrar_selector_perfil(interaction, "bugs")

    @discord.ui.button(label="support-bugs", style=discord.ButtonStyle.secondary)
    async def support_bugs(self, interaction, button):
        await mostrar_selector_perfil(interaction, "support-bugs")


# ===============================
# /auto COMMAND
# ===============================

@bot.tree.command(name="auto", description="Ejecuta pruebas automáticas")
async def auto(interaction: discord.Interaction):
    await interaction.response.send_message("🌍 Selecciona el ambiente:", view=AmbienteView())


# ===============================
# READY
# ===============================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot conectado como {bot.user}")


# ===============================
# HTTP HEALTH SERVER (para Cloud Run)
# ===============================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        # Evita spam de logs
        return


def start_health_server():
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health server escuchando en puerto {port}")
    server.serve_forever()


# ===============================
# RUN
# ===============================

if __name__ == "__main__":
    # Levantar servidor HTTP en background para satisfacer a Cloud Run
    t = threading.Thread(target=start_health_server, daemon=True)
    t.start()

    # Ejecutar el bot de Discord (hilo principal)
    bot.run(DISCORD_BOT_TOKEN)
