import pytest
from scripts.firebase_db import FirebaseManager

@pytest.fixture
def firebase():
    return FirebaseManager()

def test_firebase_connection(firebase):
    # Teste de escrita
    test_data = {
        'test': 'connection',
        'timestamp': '2023-01-01T00:00:00'
    }
    ticket_id = firebase.ref.push().key
    firebase.ref.child(ticket_id).set(test_data)
    
    # Teste de leitura
    result = firebase.ref.child(ticket_id).get()
    assert result == test_data, "Os dados lidos não correspondem aos dados escritos"
    
    # Limpeza
    firebase.ref.child(ticket_id).delete()