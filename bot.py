import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
import subprocess
from dotenv import load_dotenv
import asyncio
from aiohttp import web

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PORT = int(os.getenv('PORT', 8080))

# Define intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

async def health_check(request):
    return web.Response(text="OK", status=200)

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Web server running on port {PORT}")

class ProfileView(View):
    def __init__(self, environment):

        super().__init__(timeout=None)
        self.environment = environment

    @discord.ui.button(label="Agente", style=discord.ButtonStyle.primary, custom_id="profile_agente")
    async def agent_button(self, interaction: discord.Interaction, button: Button):
        await self.run_test(interaction, "agente")

    @discord.ui.button(label="Supervisor", style=discord.ButtonStyle.secondary, custom_id="profile_supervisor")
    async def supervisor_button(self, interaction: discord.Interaction, button: Button):
        await self.run_test(interaction, "supervisor")

    @discord.ui.button(label="Bot", style=discord.ButtonStyle.secondary, custom_id="profile_bot")
    async def bot_button(self, interaction: discord.Interaction, button: Button):
        await self.run_test(interaction, "bot")

    async def run_test(self, interaction: discord.Interaction, profile):
        # Defer the response because pytest may take a while (prevents interaction timeout)
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=False)
        logging.info("Botón de perfil %s presionado en ambiente %s", profile, self.environment)
        await interaction.followup.send(f"🚀 Iniciando pruebas para perfil **{profile}** en **{self.environment}**. Esto puede tardar unos segundos...", ephemeral=False)
        logging.info("Running pytest for profile %s in environment %s", profile, self.environment)
        
        # Build the pytest command
        # Generate JSON report for custom HTML generation
        json_report_file = "report.json"
        
        # Clean previous results
        if os.path.exists(json_report_file):
            os.remove(json_report_file)
            
        command = f"python3 -m pytest tests/{profile} --env={self.environment} --json-report --json-report-file={json_report_file}"
        logging.info("Ejecutando comando de pruebas: %s", command)
        
        try:
            # Use asyncio.create_subprocess_shell for non-blocking execution
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            try:
                # Wait for the process with a timeout
                # Increased timeout to 1800s (30 min) to accommodate growing test suite
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=1800)
                stdout = stdout.decode()
                stderr = stderr.decode()
                returncode = process.returncode
                
                logging.info("Resultado de pytest: returncode=%s", returncode)
                
                # Initialize stats
                passed = 0
                failed = 0
                total = 0
                duration = 0

                # Generate Custom HTML Report
                report_file = "index.html"
                try:
                    import json
                    from datetime import datetime
                    
                    if os.path.exists(json_report_file):
                        with open(json_report_file, 'r') as f:
                            data = json.load(f)
                        
                        passed = data['summary'].get('passed', 0)
                        failed = data['summary'].get('failed', 0)
                        total = data['summary'].get('total', 0)
                        
                        # Calculate total duration as the sum of all test durations (setup + call + teardown)
                        # This ensures it matches exactly what the user sees in the list
                        for test in data['tests']:
                            test_duration = test.get('call', {}).get('duration', 0) + \
                                          test.get('setup', {}).get('duration', 0) + \
                                          test.get('teardown', {}).get('duration', 0)
                            duration += test_duration
                            # Store it in the test object for later use in the loop
                            test['full_duration'] = test_duration
                        
                        # Generate HTML content
                        html_content = f"""
                        <!DOCTYPE html>
                        <html lang="es">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Reporte de Pruebas - {profile.capitalize()} [{self.environment}]</title>
                            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                            <style>
                                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e0e0e0; margin: 0; padding: 20px; }}
                                .container {{ max-width: 1200px; margin: 0 auto; background-color: #2d2d2d; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); display: flex; flex-wrap: wrap; gap: 30px; }}
                                h1 {{ width: 100%; text-align: center; color: #ffffff; margin-bottom: 20px; border-bottom: 2px solid #444; padding-bottom: 10px; }}
                                
                                .left-panel {{ flex: 1; min-width: 300px; display: flex; flex-direction: column; align-items: center; }}
                                .right-panel {{ flex: 2; min-width: 400px; }}
                                
                                .chart-container {{ width: 100%; max-width: 400px; height: 300px; position: relative; margin-bottom: 20px; }}
                                .stats {{ width: 100%; font-size: 1.1em; background: #333; padding: 20px; border-radius: 8px; box-sizing: border-box; }}
                                .stat-item {{ margin: 10px 0; display: flex; justify-content: space-between; }}
                                .stat-value {{ font-weight: bold; }}
                                .passed {{ color: #4caf50; }}
                                .failed {{ color: #f44336; }}
                                
                                .test-list {{ height: 600px; overflow-y: auto; padding-right: 10px; }}
                                .test-list::-webkit-scrollbar {{ width: 8px; }}
                                .test-list::-webkit-scrollbar-track {{ background: #333; }}
                                .test-list::-webkit-scrollbar-thumb {{ background: #555; border-radius: 4px; }}
                                .test-list::-webkit-scrollbar-thumb:hover {{ background: #777; }}
                                
                                .test-item {{ background-color: #333; padding: 12px; margin-bottom: 8px; border-radius: 5px; border-left: 5px solid #777; transition: transform 0.2s; cursor: pointer; }}
                                .test-item:hover {{ background-color: #3a3a3a; }}
                                .test-item.passed {{ border-left-color: #4caf50; }}
                                .test-item.failed {{ border-left-color: #f44336; }}
                                .test-header {{ display: flex; justify-content: space-between; align-items: center; }}
                                .test-name {{ font-weight: bold; font-size: 1em; }}
                                .test-duration {{ font-size: 0.85em; color: #aaa; }}
                                .error-details {{ background-color: #1e1e1e; padding: 10px; margin-top: 10px; border-radius: 4px; font-family: monospace; font-size: 0.9em; color: #ff8a80; white-space: pre-wrap; display: none; }}
                                .footer {{ width: 100%; text-align: center; margin-top: 20px; color: #777; font-size: 0.8em; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1>Reporte de Ejecución: {profile.capitalize()} [{self.environment}]</h1>
                                
                                <div class="left-panel">
                                    <div class="chart-container">
                                        <canvas id="resultsChart"></canvas>
                                    </div>
                                    <div class="stats">
                                        <div class="stat-item"><span>Total:</span> <span class="stat-value">{total}</span></div>
                                        <div class="stat-item"><span class="passed">Pasados:</span> <span class="stat-value passed">{passed}</span></div>
                                        <div class="stat-item"><span class="failed">Fallados:</span> <span class="stat-value failed">{failed}</span></div>
                                        <div class="stat-item"><span>Duración Total:</span> <span class="stat-value">{duration:.2f}s</span></div>
                                    </div>
                                </div>
                                
                                <div class="right-panel">
                                    <h2>Detalle de Pruebas ({total})</h2>
                                    <div class="test-list">
                        """
                        
                        # Advanced Grouping: File -> Class -> Test
                        grouped_tests = {}
                        for test in data['tests']:
                            nodeid = test['nodeid']
                            parts = nodeid.split("::")
                            file_path = parts[0]
                            class_name = parts[1] if len(parts) > 2 else "Sin Clase"
                            test_name = parts[-1]
                            
                            if file_path not in grouped_tests:
                                grouped_tests[file_path] = {}
                            if class_name not in grouped_tests[file_path]:
                                grouped_tests[file_path][class_name] = []
                            
                            # Store test data with extracted name
                            # Translate test names if mapping exists
                            test_name_mapping = {
                                "test_valid_login": "Login del Agente exitoso",
                                "test_logout_agente": "Cierre de sesión del Agente",
                                "test_agent_status_timer": "Contador de estado Online",
                                "test_agent_status_break": "Activacion de estado descanso",
                                "test_receive_email": "recibo de mail -agente",
                                "test_chat_closure": "Cierre chat mail",
                                "test_outbound_bienvenida_rapida": "bienvenida_rapida",
                                "test_outbound_document": "qa_documento",
                                "test_outbound_image": "qa_imagen",
                                "test_outbound_document_url": "qa_documento_url",
                                "test_outbound_image_url": "qa_imagen_url",
                                "test_outbound_video_url": "qa_video_url",
                                "test_outbound_qa_header_boton": "qa_header_boton",
                                "test_outbound_qa_asterisco_inicio": "qa_asterisco_inicio",
                                "test_outbound_qa_plantilla_portugues": "qa_plantilla_portugues",
                                "test_outbound_qa_plantila_ingles": "qa_plantila_ingles",
                                "test_outbound_qa_boton_llamar": "qa_boton_llamar"
                            }
                            
                            test['short_name'] = test_name_mapping.get(test_name, test_name)
                            grouped_tests[file_path][class_name].append(test)
                            
                        for file_path, classes in grouped_tests.items():
                            test_counter = 1
                            
                            # Custom file name mapping
                            file_name_mapping = {
                                "tests/agente/test_inbound_email.py": "Chat - Mail",
                                "tests/agente/test_outbound_agente.py": "Outbound - Envio HSM",
                                "tests/agente/test_agent_status.py": "Agente"
                            }
                            
                            display_name = file_name_mapping.get(file_path)
                            
                            if not display_name:
                                # Format file path to friendly name
                                # e.g., tests/agente/test_login_agente.py -> Login
                                display_name = file_path.split("/")[-1] # test_login_agente.py
                                display_name = display_name.replace("test_", "").replace(".py", "") # login_agente
                                # Remove common suffixes if present (optional, based on pattern)
                                if "_" in display_name:
                                    display_name = display_name.split("_")[0] # login
                                display_name = display_name.capitalize() # Login
                            
                            html_content += f"""
                            <details style="margin-bottom: 15px; border: 1px solid #444; border-radius: 5px; overflow: hidden;">
                                <summary style="background: #252525; padding: 10px; cursor: pointer; font-weight: bold; color: #ddd;">📂 {display_name}</summary>
                                <div style="padding: 10px; background: #2d2d2d;">
                            """
                            
                            for class_name, tests in classes.items():
                                if class_name != "Sin Clase":
                                    html_content += f"""
                                    <details style="margin-bottom: 10px; margin-left: 10px; border-left: 2px solid #555;">
                                        <summary style="padding: 5px 10px; cursor: pointer; font-weight: bold; color: #aaa;">📦 {class_name}</summary>
                                        <div style="padding-left: 15px;">
                                    """
                                else:
                                    html_content += '<div style="margin-left: 10px;">'

                                for test in tests:
                                    status = test['outcome']
                                    nodeid = test['nodeid']
                                    name = test['short_name']
                                    # Use the pre-calculated full duration
                                    duration_test = test.get('full_duration', 0)
                                    
                                    # Logs
                                    logs = ""
                                    if 'log' in test.get('call', {}):
                                        logs = test['call']['log']
                                    
                                        # Error message
                                    error_msg = ""
                                    if status == 'failed':
                                        error_msg = test['call'].get('longrepr', 'Error desconocido')
                                        
                                    # Screenshot (Now for ALL tests)
                                    screenshot_html = ""
                                    safe_name = nodeid.replace("::", "_").replace("/", "_").replace(".py", "")
                                    screenshot_path = f"screenshots/{safe_name}.png"
                                    if os.path.exists(screenshot_path):
                                        import base64
                                        with open(screenshot_path, "rb") as image_file:
                                            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                                            screenshot_html = f'''
                                            <details style="margin-top: 5px; border: 1px solid #444; border-radius: 4px; padding: 5px;">
                                                <summary style="cursor: pointer; color: #aaa;">📸 Captura de Pantalla</summary>
                                                <div style="margin-top: 10px; text-align: center;">
                                                    <img src="data:image/png;base64,{encoded_string}" style="max-width: 100%; border: 1px solid #555; border-radius: 4px;">
                                                </div>
                                            </details>
                                            '''
                                    
                                    html_content += f"""
                                            <div class="test-item {status}">
                                                <div class="test-header" onclick="this.parentElement.querySelector('.details-container').style.display = this.parentElement.querySelector('.details-container').style.display === 'block' ? 'none' : 'block'">
                                                    <span class="test-name">#{test_counter} {name}</span>
                                                    <span class="test-duration">{duration_test:.2f}s</span>
                                                </div>
                                                <div class="details-container" style="display: none; margin-top: 10px;">
                                                    {f'<div style="color: #ff8a80; margin-bottom: 10px; padding: 10px; background: #2a1a1a; border-radius: 4px;"><strong>Error:</strong><br>{error_msg}</div>' if error_msg else ''}
                                                    
                                                    {f'''
                                                    <details style="margin-top: 5px; border: 1px solid #444; border-radius: 4px; padding: 5px;">
                                                        <summary style="cursor: pointer; color: #aaa;">📄 Logs de Ejecución</summary>
                                                        <pre style="background: #111; padding: 10px; overflow-x: auto; color: #ccc; margin-top: 5px; white-space: pre-wrap;">{logs}</pre>
                                                    </details>
                                                    ''' if logs else '<div style="color: #555; font-style: italic; margin-top: 5px;">No logs captured</div>'}
                                                    
                                                    {screenshot_html}
                                                </div>
                                            </div>
                                    """
                                    test_counter += 1
                                
                                if class_name != "Sin Clase":
                                    html_content += "</div></details>"
                                else:
                                    html_content += "</div>"
                            
                            html_content += "</div></details>"
                        
                        html_content += f"""
                                    </div>
                                </div>
                                <div class="footer">Generado el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</div>
                            </div>
                            
                            <script>
                                const ctx = document.getElementById('resultsChart').getContext('2d');
                                
                                // Plugin to draw text in center
                                const centerTextPlugin = {{
                                    id: 'centerText',
                                    beforeDraw: function(chart) {{
                                        var width = chart.chartArea.width,
                                            height = chart.chartArea.height,
                                            ctx = chart.ctx;
                                            
                                        ctx.restore();
                                        var fontSize = (height / 114).toFixed(2);
                                        ctx.font = fontSize + "em sans-serif";
                                        ctx.textBaseline = "middle";
                                        ctx.fillStyle = "#ffffff";
                                        
                                        var text = "{total}",
                                            textX = Math.round((width - ctx.measureText(text).width) / 2) + chart.chartArea.left,
                                            textY = (height / 2) + chart.chartArea.top;
                                            
                                        ctx.fillText(text, textX, textY);
                                        ctx.save();
                                    }}
                                }};
                                
                                new Chart(ctx, {{
                                    type: 'doughnut',
                                    data: {{
                                        labels: ['Pasados', 'Fallados'],
                                        datasets: [{{
                                            data: [{passed}, {failed}],
                                            backgroundColor: ['#4caf50', '#f44336'],
                                            borderWidth: 0
                                        }}]
                                    }},
                                    options: {{
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        plugins: {{
                                            legend: {{ position: 'bottom', labels: {{ color: '#fff' }} }}
                                        }}
                                    }},
                                    plugins: [centerTextPlugin]
                                }});
                            </script>
                        </body>
                        </html>
                        """
                        
                        with open(report_file, "w") as f:
                            f.write(html_content)
                        logging.info("Reporte HTML personalizado generado exitosamente.")

                except Exception as e:
                    logging.error("Error generando reporte HTML: %s", e)

                # Upload report to GCS
                report_url = "https://console.cloud.google.com/run" # Fallback
                try:
                    from google.cloud import storage
                    from datetime import datetime
                    
                    if os.path.exists(report_file):
                        bucket_name = "qa-allure-automation-chattigo-reports"
                        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                        destination_blob_name = f"{self.environment}/{profile}/{timestamp}/report/index.html"
                        
                        storage_client = storage.Client()
                        bucket = storage_client.bucket(bucket_name)
                        blob = bucket.blob(destination_blob_name)
                        blob.upload_from_filename(report_file)
                        
                        # User requested specific format:
                        report_url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name.replace(' ', '%20')}"
                        logging.info("Reporte subido a: %s", report_url)
                except Exception as e:
                    logging.error("Error subiendo reporte a GCS: %s", e)
                    await interaction.followup.send(f"⚠️ Error subiendo reporte a GCS: {e}")

                # Build embed with results
                # Use stats from JSON report (already calculated above)
                
                # Fallback if total is 0 (should not happen if JSON loaded correctly)
                if total == 0:
                     if returncode == 0:
                         passed = 1
                         total = 1
                     else:
                         failed = 1
                         total = 1

                percentage = int((passed / total) * 100) if total > 0 else 0
                
                # Create progress bar (15 chars long)
                bar_length = 15
                filled_length = int(bar_length * percentage // 100)
                # Use green squares for filled, white squares for empty
                bar = '🟩' * filled_length + '⬜' * (bar_length - filled_length)
                
                # Build formatted embed matching user request
                embed = discord.Embed(
                    title=f"[{profile}][{self.environment}]: {percentage} % -",
                    description=f"El cohete ha llegado a destino! 🪐 Click [acá]({report_url}) para ver el Reporte!\n-\nPasados : {passed}\nFallados : {failed}\nTotal : {total}\n[{bar}]",
                    color=0x00ff00 if returncode == 0 else 0xff0000,
                )
                
                # Add timestamp footer
                from datetime import datetime
                embed.set_footer(text=datetime.now().strftime("%d/%m/%y, %H:%M"))
                
                # Send message without error details or screenshots (as requested)
                await interaction.followup.send(embed=embed)
                
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except:
                    pass
                logging.error("Timeout al ejecutar pytest")
                await interaction.followup.send("⚠️ Timeout al ejecutar las pruebas. Por favor, verifica que los tests no requieran interacción manual.")
                
        except Exception as e:
            logging.error("Error al ejecutar pytest: %s", e, exc_info=True)
            try:
                await interaction.followup.send(f"⚠️ Error al ejecutar el comando: {e}")
            except:
                pass

class EnvironmentView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Pantera", style=discord.ButtonStyle.success, custom_id="env_pantera")
    async def pantera_button(self, interaction: discord.Interaction, button: Button):
        logging.info("Botón Pantera presionado por %s", interaction.user)
        await self.ask_profile(interaction, "pantera")

    @discord.ui.button(label="Bugs", style=discord.ButtonStyle.danger, custom_id="env_bugs")
    async def bugs_button(self, interaction: discord.Interaction, button: Button):
        await self.ask_profile(interaction, "bugs")

    @discord.ui.button(label="Support Bugs", style=discord.ButtonStyle.primary, custom_id="env_support_bugs")
    async def support_bugs_button(self, interaction: discord.Interaction, button: Button):
        await self.ask_profile(interaction, "support-bugs")

    @discord.ui.button(label="Leones", style=discord.ButtonStyle.secondary, custom_id="env_leones")
    async def leones_button(self, interaction: discord.Interaction, button: Button):
        await self.ask_profile(interaction, "leones")

    async def ask_profile(self, interaction: discord.Interaction, environment):
        try:
            # Deferimos la interacción antes de enviar cualquier mensaje
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=False)
            view = ProfileView(environment)
            logging.info("Ambiente %s seleccionado, mostrando botones de perfil", environment)
            await interaction.followup.send(
                f"Has seleccionado **{environment}**. ¿Qué perfil deseas probar?",
                view=view,
                ephemeral=False,  # Cambiado a False para evitar confusión si el usuario pierde el mensaje
            )
            logging.info("Mensaje de selección de perfil enviado correctamente")
        except Exception as e:
            logging.error("Error en ask_profile: %s", e)
            try:
                await interaction.followup.send(f"⚠️ Error al procesar la selección: {e}", ephemeral=True)
            except:
                pass

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    try:
        # Register persistent views
        bot.add_view(EnvironmentView())
        print("Vista EnvironmentView registrada.")
        
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos.")
    except Exception as e:
        print(e)

@bot.tree.command(name="auto", description="Inicia el flujo de pruebas automatizadas")
async def auto(interaction: discord.Interaction):
    logging.info("/auto command invoked by user")
    # Deferimos la respuesta para evitar timeouts (error 10062)
    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=False)
    view = EnvironmentView()
    await interaction.followup.send("Selecciona el ambiente para las pruebas:", view=view)

async def main():
    if not TOKEN:
        print("Error: DISCORD_TOKEN no encontrado en variables de entorno.")
        return
    
    # Start web server and bot concurrently
    await asyncio.gather(
        start_web_server(),
        bot.start(TOKEN)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle graceful shutdown if needed
        pass
