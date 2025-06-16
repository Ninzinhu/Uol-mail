import schedule
import time
from scripts.email_monitor import check_emails
import logging

def job():
    logging.info("Executando verificação de emails...")
    check_emails()

# Agendar verificação a cada 5 minutos
schedule.every(5).minutes.do(job)

if __name__ == "__main__":
    logging.info("Serviço de monitoramento iniciado")
    while True:
        schedule.run_pending()
        time.sleep(1)