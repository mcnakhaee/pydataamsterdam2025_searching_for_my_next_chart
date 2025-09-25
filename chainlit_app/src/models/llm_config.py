class LLMConfig:
    def __init__(self):
        self.model_name = "gpt-3.5-turbo"
        self.temperature = 0.7
        self.max_tokens = 150
        self.top_p = 1.0
        self.frequency_penalty = 0.0
        self.presence_penalty = 0.0

    def to_dict(self):
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }