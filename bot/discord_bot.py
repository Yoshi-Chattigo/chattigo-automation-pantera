import discord
from discord.ext import commands
from discord import app_commands

from google.cloud.devtools import cloudbuild_v1
from google.oauth2 import service_account
from google.cloud import storage

from datetime import datetime
import json
import asyncio

# ===============================
# CONFIG LOCAL (TOKEN + CHANNEL)
# ===============================
from local_config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID

PROJECT_ID = "automation-chattigo"
BUCKET = "qa-allure-report-storage-automation"

# Service account
credentials = service_account.Credentials.from_service_account_file(
    "bot/service-account.json"
)

storage_client = storage.Client(
    project=PROJECT_ID,
    credentials=credentials
)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

CHANNEL_ID = DISCORD_CHANNEL_ID  # canal oficial donde se reporta todo


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
        await ejecutar_en_cloud_build(self.ambiente, "agente")

    @discord.ui.button(label="bot", style=discord.ButtonStyle.primary)
    async def bot(self, interaction, button):
        await ejecutar_en_cloud_build(self.ambiente, "bot")

    @discord.ui.button(label="supervisor", style=discord.ButtonStyle.secondary)
    async def supervisor(self, interaction, button):
        await ejecutar_en_cloud_build(self.ambiente, "supervisor")


async def mostrar_selector_perfil(interaction, ambiente):
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(
        f"🌍 Ambiente seleccionado: `{ambiente}`\n"
        "Ahora selecciona el perfil:",
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
# /auto
# ===============================

@bot.tree.command(name="auto", description="Ejecuta pruebas automáticas")
async def auto(interaction: discord.Interaction):
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("🌍 Selecciona el ambiente:", view=AmbienteView())


# ===============================
# READY
# ===============================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot conectado como {bot.user}")


# ===============================
# RUN
# ===============================

bot.run(DISCORD_BOT_TOKEN)
