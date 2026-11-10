from transformers import pipeline

class API:

    def __init__(self):
        self.task = None
        self.model = None
        self.tokenizer = None

    def sentiment_analysis(self, text):
        self.task = "sentiment-analysis"
        self.model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.tokenizer = "cardiffnlp/twitter-roberta-base-sentiment-latest"

        sentiment_task = pipeline(task = self.task, model = self.model, tokenizer = self.tokenizer)
        response = sentiment_task(text)
        return response
