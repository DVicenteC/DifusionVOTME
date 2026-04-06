import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def enviar_confirmacion(datos_participante, curso_info):
    """
    Envía un correo de confirmación al participante tras su inscripción.
    
    Args:
        datos_participante (dict): Datos del formulario (nombres, email, rut, etc.)
        curso_info (dict): Datos del curso seleccionado (id, jornada, etc.)
        
    Returns:
        bool: True si el envío fue exitoso, False en caso contrario.
    """
    
    # Verificar si las credenciales están configuradas
    try:
        email_config = st.secrets.get("email", {})
        if not email_config:
            return False
            
        smtp_server = email_config.get("smtp_server")
        smtp_port = email_config.get("smtp_port")
        smtp_user = email_config.get("smtp_user")
        smtp_password = email_config.get("smtp_password")
        sender_name = email_config.get("sender_name", "Difusión TMERT V3")
        
        if not all([smtp_server, smtp_port, smtp_user, smtp_password]):
            return False
            
    except Exception:
        # Silenciosamente fallamos si no hay secretos configurados
        return False

    # Datos para el correo
    nombre_completo = f"{datos_participante.get('nombres', '')} {datos_participante.get('apellido_paterno', '')}".title()
    email_destinatario = datos_participante.get('email')
    curso_id = curso_info.get('curso_id', 'TMERT-N/A')
    fecha_jornada = curso_info.get('fecha_jornada', 'Pendiente')
    
    if not email_destinatario:
        return False

    # Crear el mensaje (Multipart/Alternative para mejor compatibilidad)
    msg = MIMEMultipart('alternative')
    # Simplificar el From: algunos servidores corporativos rechazan el formato "Nombre <email>"
    msg['From'] = smtp_user 
    msg['To'] = email_destinatario
    msg['Subject'] = f"Confirmación de Inscripción: Difusión TMERT V3 - {curso_id}"
    
    # Versión en Texto Plano (para evitar filtros de spam)
    text_version = f"""
    Estimado/a {nombre_completo},
    
    Le confirmamos que su inscripción para la jornada de difusión ha sido procesada con éxito.
    
    DETALLES:
    - Curso: {curso_id}
    - Fecha: {fecha_jornada}
    - Horario: 09:00 AM
    - Modalidad: Online
    
    Próximamente recibirá el enlace de conexión.
    Atentamente, equipo de Difusión IST.
    """

    # Plantilla HTML
    html_template = f"""
    <html>
    <head>
        <style>
            .container {{ font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333; }}
            .header {{ background-color: #004A99; color: white; padding: 15px; text-align: center; }}
            .content {{ padding: 20px; border: 1px solid #ddd; }}
            .footer {{ text-align: center; font-size: 11px; color: #999; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Inscripción Confirmada</h2>
            </div>
            <div class="content">
                <p>Hola <strong>{nombre_completo}</strong>,</p>
                <p>Tu inscripción para <strong>{curso_id}</strong> ha sido registrada.</p>
                <ul>
                    <li><strong>Fecha:</strong> {fecha_jornada}</li>
                    <li><strong>Hora:</strong> 09:00 AM</li>
                    <li><strong>Modalidad:</strong> Online</li>
                </ul>
                <p>Nos vemos en la jornada.</p>
            </div>
            <div class="footer">
                <p>IST - Especialidades Técnicas</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(text_version, 'plain'))
    msg.attach(MIMEText(html_template, 'html'))

    try:
        # Activar debug si es necesario
        debug_level = 1 if __name__ == "__main__" else 0
        
        # Conexión al servidor (SSL para puerto 465)
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(smtp_server, int(smtp_port), timeout=15)
        else:
            server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=15)
            server.set_debuglevel(debug_level)
            server.starttls()
            
        server.set_debuglevel(debug_level)
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False

# Bloque de prueba local
if __name__ == "__main__":
    print("🧪 Iniciando prueba local de envío de correos...")
    
    # Intentar cargar secretos manualmente para la prueba local
    import os
    import re
    
    class MockSecrets:
        def __init__(self):
            self.data = {"email": {}}
            try:
                # Buscar secrets.toml relativo a la ubicación del script
                base_dir = os.path.dirname(os.path.abspath(__file__))
                secrets_path = os.path.join(base_dir, ".streamlit", "secrets.toml")
                
                if os.path.exists(secrets_path):
                    with open(secrets_path, "r") as f:
                        content = f.read()
                        # Simple regex para capturar campos de [email]
                        for key in ["smtp_server", "smtp_port", "smtp_user", "smtp_password", "sender_name"]:
                            # Buscar con comillas simples o dobles
                            match = re.search(rf'{key}\s*=\s*["\'](.*?)["\']', content)
                            if not match: # Caso para números (port)
                                match = re.search(rf'{key}\s*=\s*(\d+)', content)
                            
                            if match:
                                self.data["email"][key] = match.group(1)
                else:
                    print(f"⚠️ Archivo no encontrado en: {secrets_path}")
            except Exception as e:
                print(f"⚠️ No se pudo leer secrets.toml: {e}")

        def get(self, key, default=None):
            return self.data.get(key, default)

    # Reemplazar st.secrets temporalmente para la prueba
    original_secrets = st.secrets
    st.secrets = MockSecrets()
    
    # Simular datos de entrada
    test_participante = {
        'nombres': 'DIEGO (TEST)',
        'apellido_paterno': 'VICENTE',
        'email': 'diergo.vicente@gmail.com' # Verifica que este correo sea el correcto para recibir
    }
    
    test_curso = {
        'curso_id': 'TEST-LOCAL-IST',
        'fecha_jornada': '16-04-2026'
    }
    
    # Intentar enviar con captura de error detallada
    try:
        print(f"Connecting to {st.secrets.get('email').get('smtp_server')}...")
        resultado = enviar_confirmacion(test_participante, test_curso)
        
        if resultado:
            print("\n✅ ¡ÉXITO! El correo fue aceptado por el servidor.")
        else:
            print("\n❌ FALLÓ el envío.")
            print("Posibles causas:")
            print("1. Credenciales incorrectas en secrets.toml")
            print("2. El servidor mail.ist.cl NO acepta conexiones desde esta IP")
            print("3. Firewall bloqueando el puerto 465")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
    finally:
        st.secrets = original_secrets
