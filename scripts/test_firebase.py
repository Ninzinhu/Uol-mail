from scripts.firebase_db import FirebaseManager

def test_firebase():
    print("Testando conexão com Firebase...")
    fb = FirebaseManager()
    test_data = {
        "teste": "Conexão estabelecida com sucesso",
        "timestamp": "2023-01-01T00:00:00"
    }
    result = fb.ref.push().set(test_data)
    print("Resultado do teste:", result)

if __name__ == "__main__":
    test_firebase()