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

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = f"{sender_name} <{smtp_user}>"
    msg['To'] = email_destinatario
    msg['Subject'] = f"Confirmación de Inscripción: Difusión TMERT V3 - {curso_id}"

    # Plantilla HTML
    html_template = f"""
    <html>
    <head>
        <style>
            .container {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; color: #333; }}
            .header {{ background-color: #004A99; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ padding: 30px; border: 1px solid #ddd; border-top: none; background-color: #f9f9f9; }}
            .details {{ background-color: white; padding: 20px; border-radius: 5px; margin-top: 20px; border-left: 5px solid #004A99; }}
            .footer {{ text-align: center; font-size: 12px; color: #777; margin-top: 20px; }}
            .highlight {{ color: #004A99; font-weight: bold; }}
            .btn {{ display: inline-block; padding: 10px 20px; background-color: #004A99; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Confirmación de Inscripción</h2>
                <p>Protocolo de Vigilancia TMERT V3</p>
            </div>
            <div class="content">
                <p>Estimado/a <span class="highlight">{nombre_completo}</span>,</p>
                <p>Le confirmamos que su inscripción para la jornada de difusión ha sido procesada con éxito.</p>
                
                <div class="details">
                    <p><strong>Curso:</strong> {curso_id}</p>
                    <p><strong>Fecha de la Jornada:</strong> {fecha_jornada}</p>
                    <p><strong>Horario:</strong> 09:00 AM</p>
                    <p><strong>Modalidad:</strong> Online</p>
                </div>
                
                <p>Próximamente recibirá el enlace de conexión a través de este mismo medio.</p>
                
                <p>Por favor, considere:</p>
                <ul>
                    <li>Conectarse 5 minutos antes del inicio.</li>
                    <li>Asegurarse de contar con una buena conexión a internet.</li>
                    <li>Tener su RUT a mano para el registro de asistencia.</li>
                </ul>
                
                <p>Atentamente,<br><strong>Equipo de Difusión IST</strong></p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no lo responda.</p>
                <p>&copy; {datetime.now().year} IST - Especialidades Técnicas</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_template, 'html'))

    try:
        # Conexión al servidor (SSL para puerto 465) con timeout de 10s
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(smtp_server, int(smtp_port), timeout=10)
        else:
            server = smtplib.SMTP(smtp_server, int(smtp_port), timeout=10)
            server.starttls()
            
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False
