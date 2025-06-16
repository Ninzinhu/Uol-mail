import logging
from typing import Optional
from datetime import datetime
import json
from pathlib import Path

class LogSender:
    def __init__(self, log_file: str = '../logs/message_logs.log'):
        self.log_file = Path(log_file)
        self._setup_logger()

    def _setup_logger(self):
        """Configura o logger para mensagens"""
        self.logger = logging.getLogger('message_logger')
        self.logger.setLevel(logging.INFO)
        
        # Evitar handlers duplicados
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(file_handler)

    def send_log_message(self, message: str, metadata: dict = None) -> bool:
        """Registra mensagem no log com metadados"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'metadata': metadata or {}
            }
            
            self.logger.info(json.dumps(log_entry, ensure_ascii=False))
            return True
        except Exception as e:
            logging.error(f"Erro ao registrar mensagem no log: {str(e)}")
            return False

def send_via_log(message: str, metadata: dict = None) -> bool:
    """Função pública para envio via log"""
    sender = LogSender()
    return sender.send_log_message(message, metadata)