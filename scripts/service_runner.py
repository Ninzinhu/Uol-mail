import schedule
import time
from scripts.email_monitor import EmailMonitor
from scripts.notification_manager import NotificationManager
import logging

logging.basicConfig(filename='../logs/service.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ServiceRunner:
    def __init__(self):
        self.email_monitor = EmailMonitor()
        self.notification_manager = NotificationManager()

    def check_emails_job(self):
        logging.info("Executando verificação de emails...")
        self.email_monitor.check_emails()

    def send_notifications_job(self):
        logging.info("Verificando notificações pendentes...")
        self.notification_manager.send_new_tickets_notifications()

    def run(self):
        # Agendar jobs
        schedule.every(5).minutes.do(self.check_emails_job)
        schedule.every(10).minutes.do(self.send_notifications_job)

        logging.info("Serviço iniciado com sucesso")
        
        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    service = ServiceRunner()
    service.run()