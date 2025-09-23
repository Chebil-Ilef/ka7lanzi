
feedback_store = {}

def store_feedback(dataset_name: str, question: str, feedback: str):
    """
    Stocke le feedback utilisateur pour améliorer les réponses futures
    """
    if dataset_name not in feedback_store:
        feedback_store[dataset_name] = []
    feedback_store[dataset_name].append({"question": question, "feedback": feedback})