from twilio.rest import Client
import json
import logging
from typing import Optional

# Configurar logging
logging.basicConfig(filename='../logs/whatsapp.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class WhatsAppSender:
    def __init__(self):
        try:
            with open('../config/config.json') as config_file:
                self.config = json.load(config_file)['whatsapp']
            self.client = Client(self.config['account_sid'], self.config['auth_token'])
        except Exception as e:
            logging.error(f"Erro ao inicializar WhatsAppSender: {str(e)}")
            raise

    def send_message(self, message: str, to_group: bool = True) -> Optional[str]:
        """Envia mensagem para número individual ou grupo"""
        try:
            if not message or not isinstance(message, str):
                raise ValueError("Mensagem inválida ou vazia")

            destination = self.config['group_id'] if to_group else self.config['to_number']
            
            if not destination:
                logging.error("Destino não configurado")
                return None

            message = self.client.messages.create(
                body=message,
                from_=self.config['from_number'],
                to=destination
            )
            logging.info(f"Mensagem enviada para {'grupo' if to_group else 'individual'}. SID: {message.sid}")
            return message.sid
        except Exception as e:
            logging.error(f"Erro ao enviar WhatsApp: {str(e)}")
            return None

def send_whatsapp_notification(message: str, to_group: bool = True) -> Optional[str]:
    """Função pública para envio de notificações"""
    try:
        if not message:
            logging.warning("Tentativa de enviar mensagem vazia")
            return None
            
        sender = WhatsAppSender()
        return sender.send_message(message, to_group)
    except Exception as e:
        logging.error(f"Erro em send_whatsapp_notification: {str(e)}")
        return None