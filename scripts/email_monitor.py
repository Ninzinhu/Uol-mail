import imaplib
import email
import json
import re
from email.header import decode_header
from scripts.whatsapp_sender import send_whatsapp_notification
import os
from dotenv import load_doteenv
import logging
from scripts.firebase_db import FirebaseManager
from scripts.priority_handler import classify_priority


class EmailMonitor:
    def __init__(self):
        self.firebase = FirebaseManager()
        self.keywords = self.load_keywords('../config/keywords.txt')
        self.emergency_keys = self.load_keywords('../config/emergency_keys.txt')

    def load_keywords(self, filepath):
        with open(filepath) as f:
            return [line.strip().lower() for line in f if line.strip()]

    def process_email(self, email_message, email_id):
        try:
            subject = self.decode_email_header(email_message.get('Subject', 'Sem assunto'))
            sender_name = self.get_sender_name(email_message)
            body = self.extract_email_body(email_message)
            
            
            is_emergency = self.check_emergency(subject, body)
            
            #
            priority = classify_priority(subject, body, is_emergency)
            
            
            ticket_data = {
                'email_id': email_id,
                'sender': sender_name,
                'subject': subject,
                'body': body[:2000],  
                'priority': priority,
                'is_emergency': is_emergency,
                'processed': False
            }
            
            # DB FIREBASE
            ticket_id = self.firebase.save_ticket(ticket_data)
            
            if ticket_id:
                return self.generate_notification(ticket_data, ticket_id)
            return None
            
        except Exception as e:
            logging.error(f"Erro ao processar email: {str(e)}")
            return None

    def generate_notification(self, ticket_data, ticket_id):
        emoji = "🚨" if ticket_data['is_emergency'] else "📌"
        priority_text = {
            'high': 'ALTA PRIORIDADE',
            'medium': 'Prioridade Média',
            'low': 'Prioridade Baixa'
        }.get(ticket_data['priority'], 'Prioridade Normal')
        
        return (
            f"{emoji} *Novo Chamado ({priority_text})* {emoji}\n\n"
            f"🆔 *ID:* {ticket_id}\n"
            f"👤 *Remetente:* {ticket_data['sender']}\n"
            f"📌 *Assunto:* {ticket_data['subject']}\n\n"
            f"📝 *Mensagem:*\n{ticket_data['body'][:500]}\n\n"
            f"⚠️ *Emergência:* {'Sim' if ticket_data['is_emergency'] else 'Não'}"
        )

   

# Logging
logging.basicConfig(filename='../logs/monitor.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


with open('../config/config.json') as config_file:
    config = json.load(config_file)


with open('../config/keywords.txt') as keywords_file:
    keywords = [line.strip() for line in keywords_file if line.strip()]

def decode_text(text):
    """Decodifica texto com encoding desconhecido"""
    if isinstance(text, bytes):
        try:
            return text.decode('utf-8')
        except UnicodeDecodeError:
            return text.decode('latin-1')
    return text

def get_sender_name(email_message):
    """Extrai o nome do remetente do email"""
    sender = email_message.get('From', '')
    decoded_sender = decode_header(sender)[0]
    sender_text = decode_text(decoded_sender[0])
    
    # Extrair nome do formato "Nome <email@dominio.com>"
    match = re.match(r'(.*?)\s*<[^>]+>', sender_text)
    if match:
        return match.group(1).strip('"\' ')
    return sender_text

def check_emails():
    
    try:
        # Conectar ao servidor IMAP
        mail = imaplib.IMAP4_SSL(config['email']['server'], config['email']['port'])
        mail.login(config['email']['username'], config['email']['password'])
        mail.select(config['email']['folder'])
        
        # Buscar emails não lidos
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK':
            logging.error("Erro ao buscar emails")
            return
        
        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                continue
                
            email_message = email.message_from_bytes(data[0][1])
            subject = decode_header(email_message.get('Subject', 'Sem assunto'))[0][0]
            subject = decode_text(subject)
            sender_name = get_sender_name(email_message)
            
            # Verificar corpo do email
            body = ""
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = decode_text(part.get_payload(decode=True))
                    break
            
            # Verificar se contém palavras-chave
            if any(keyword.lower() in (subject + body).lower() for keyword in keywords):
                # Preparar mensagem para WhatsApp
                message = (
                    f"🚨 *Novo Chamado Recebido* 🚨\n\n"
                    f"👤 *Nome:* {sender_name}\n"
                    f"📌 *Título:* {subject}\n\n"
                    f"📝 *Mensagem:*\n{body[:500]}"  # Limitar a 500 caracteres
                )
                
                # Enviar para WhatsApp
                send_whatsapp_notification(message)
                logging.info(f"Notificação enviada para WhatsApp - Assunto: {subject}")
                
    except Exception as e:
        logging.error(f"Erro ao verificar emails: {str(e)}")
    finally:
        try:
            mail.close()
            mail.logout()
        except:
            pass

if __name__ == "__main__":
    check_emails()