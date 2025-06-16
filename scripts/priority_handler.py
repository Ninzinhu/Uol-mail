import re
import logging

logging.basicConfig(filename='../logs/priority.log', level=logging.INFO)

def classify_priority(subject, body, is_emergency=False):
    
    try:
        content = f"{subject} {body}".lower()
        
        if is_emergency:
            return 'high'
            
        # Palavras-chave para alta prioridade
        high_priority_words = ['urgente', 'urgência', 'prioridade', 'importante', 
                              'socorro', 'ajuda', 'imediato', 'critico']
        if any(word in content for word in high_priority_words):
            return 'high'
            
        # Palavras-chave para média prioridade
        medium_priority_words = ['solicit', 'pedido', 'necessário', 'preciso', 
                                'problema', 'dificuldade']
        if any(word in content for word in medium_priority_words):
            return 'medium'
            
        return 'low'
        
    except Exception as e:
        logging.error(f"Erro ao classificar prioridade: {str(e)}")
        return 'medium'