"""
Agente Revisore: analizza e critica strategie di trading generate.
"""

class ReviewerAgent:
    def __init__(self):
        pass

    def review_strategy(self, strategy_code: str) -> dict[str, str | bool]:
        """
        Analizza la strategia e restituisce un dizionario con feedback, approvazione e suggerimento su Hyperopt.
        """
        # TODO: Integrare con LLM locale e parsing JSON
        return {
            "approved": True,
            "feedback": "La strategia è promettente ma migliorabile. Consiglio Hyperopt.",
            "suggest_hyperopt": True
        }
