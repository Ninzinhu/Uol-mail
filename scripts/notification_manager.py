from scripts.whatsapp_sender import send_whatsapp_notification
from scripts.log_sender import send_via_log
from scripts.firebase_db import FirebaseManager
import logging

class NotificationManager:
    def __init__(self):
        self.firebase = FirebaseManager()

    def format_notification(self, ticket_data: dict) -> str:
        
        try:
            emoji = "🚨" if ticket_data.get('is_emergency', False) else "📌"
            priority = ticket_data.get('priority', 'medium').upper()
            
            return (
                f"{emoji} *Novo Chamado - {priority}*\n\n"
                f"👤 *De:* {ticket_data.get('sender', 'Remetente desconhecido')}\n"
                f"📌 *Assunto:* {ticket_data.get('subject', 'Sem assunto')}\n\n"
                f"📝 *Mensagem:*\n{ticket_data.get('body', 'Sem conteúdo')[:300]}\n\n"
                f"🆔 *ID:* {ticket_data.get('id', 'N/A')}"
            )
        except Exception as e:
            logging.error(f"Erro ao formatar notificação: {str(e)}")
            return "Novo chamado recebido (formato inválido)"

    def send_new_tickets_notifications(self):
        """Envia notificações para novos chamados"""
        try:
            tickets = self.firebase.ref.order_by_child('processed').equal_to(False).get()
            
            if not tickets:
                logging.info("Nenhum novo chamado para processar")
                return

            for ticket_id, ticket_data in tickets.items():
                # Adiciona o ID aos dados do ticket
                ticket_data['id'] = ticket_id
                
                # Formata a mensagem
                message = self.format_notification(ticket_data)
                
                if not message:
                    continue
                
                # Envia para o grupo
                send_whatsapp_notification(message=message, to_group=True)
                
                # Se for emergência, envia também para individual
                if ticket_data.get('is_emergency', False):
                    emergency_msg = f"🚨 URGENTE: {message}"
                    send_whatsapp_notification(message=emergency_msg, to_group=False)
                
                # Marca como processado
                self.firebase.update_ticket_status(ticket_id, {'processed': True})
                
        except Exception as e:
            logging.error(f"Erro no gerenciador de notificações: {str(e)}")