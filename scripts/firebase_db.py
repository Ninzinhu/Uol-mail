import firebase_admin
from firebase_admin import credentials, db
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(filename='../logs/db.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class FirebaseManager:
    def __init__(self, config_path='../config/firebase_config.json'):
        try:
            # Carregar configuração do Firebase
            with open(config_path) as config_file:
                firebase_config = json.load(config_file)
            
            # Inicializar o Firebase
            if not firebase_admin._apps:
                cred = credentials.Certificate(firebase_config["serviceAccount"])
                firebase_admin.initialize_app(cred, {
                    'databaseURL': firebase_config["databaseURL"]
                })
            
            self.ref = db.reference('/chamados')
            logging.info("Firebase inicializado com sucesso")
        except Exception as e:
            logging.error(f"Erro ao inicializar Firebase: {str(e)}")
            raise

    def save_ticket(self, ticket_data):
        """Salva um novo chamado no Firebase"""
        try:
            # Adicionar metadados
            ticket_data['timestamp'] = datetime.now().isoformat()
            ticket_data['status'] = 'pendente'
            
            # Salvar no Firebase
            new_ticket_ref = self.ref.push()
            new_ticket_ref.set(ticket_data)
            ticket_id = new_ticket_ref.key
            
            logging.info(f"Chamado salvo no Firebase. ID: {ticket_id}")
            return ticket_id
        except Exception as e:
            logging.error(f"Erro ao salvar chamado: {str(e)}")
            return None

    def update_ticket_status(self, ticket_id, status):
        """Atualiza o status de um chamado"""
        try:
            self.ref.child(ticket_id).update({'status': status})
            logging.info(f"Status do chamado {ticket_id} atualizado para {status}")
            return True
        except Exception as e:
            logging.error(f"Erro ao atualizar chamado: {str(e)}")
            return False

    def get_pending_tickets(self):
        """Retorna todos os chamados pendentes"""
        try:
            tickets = self.ref.order_by_child('status').equal_to('pendente').get()
            return tickets if tickets else {}
        except Exception as e:
            logging.error(f"Erro ao buscar chamados pendentes: {str(e)}")
            return {}

    def check_ticket_exists(self, email_id):
        """Verifica se um email já foi processado"""
        try:
            tickets = self.ref.order_by_child('email_id').equal_to(email_id).get()
            return bool(tickets)
        except Exception as e:
            logging.error(f"Erro ao verificar chamado existente: {str(e)}")
            return True  