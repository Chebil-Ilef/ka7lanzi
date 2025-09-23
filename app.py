from core.agent import DatasetAgent
from config import DATA_DIR

if __name__ == "__main__":

    agent = DatasetAgent(str(DATA_DIR))
    agent.build_index()

    question = "Quelle est la colonne ayant la plus forte corrélation avec math_score ?"
    answer = agent.query(question)
    print("Réponse de l'agent :", answer)