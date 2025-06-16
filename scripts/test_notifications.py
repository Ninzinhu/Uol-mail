from scripts.notification_manager import NotificationManager

def test_notification_system():
    print("Testando sistema de notificações...")
    manager = NotificationManager()
    
    # Teste com dados simulados
    test_ticket = {
        "sender": "Teste Sistema",
        "subject": "Mensagem de Teste",
        "body": "Esta é uma mensagem de teste do sistema de notificações",
        "priority": "high",
        "is_emergency": True,
        "processed": False
    }
    
    # Simular salvamento no Firebase
    from scripts.firebase_db import FirebaseManager
    fb = FirebaseManager()
    ticket_id = fb.ref.push().key
    fb.ref.child(ticket_id).set(test_ticket)
    
    # Testar envio
    manager.send_new_tickets_notifications()
    print(f"Teste completo. Verifique o grupo WhatsApp e o número individual.")

if __name__ == "__main__":
    test_notification_system()