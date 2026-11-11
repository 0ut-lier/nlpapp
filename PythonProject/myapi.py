import requests

class API:

    def __init__(self):

        self.api_key = "YOUR_API_KEY"  # Replace with your actual API key
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "liquid/lfm-3-1.7b:free"
        self.system_message = None
        self.text = None

    
    def api_call(self):

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": f"{self.system_message} {self.text}"
                }
            ]
        }

        response = requests.post(
            self.url,
            headers=headers,
            json=payload
        )

        return response.json()["choices"][0]["message"]["content"]
    
    
    def sentiment_analysis(self, text, system_message):
        self.system_message = system_message
        self.text = text
        return self.api_call()
    

    def nlp_task(self, task, text):

        if task == "sentiment-analysis":
            system_message = "Perform sentiment analysis of this sentence in one word:"
        elif task == "ner":
            system_message = "Perform named entity recognition on this sentence and classify the entities into categories like person, organization, location, etc. Return the entities in this way `entity` -> `category` and write each of them in new line:"
        elif task == "emotion-detection":
            system_message = "Perform emotion detection on this sentence and return the most closely related emotion from the following list: happy, sad, angry, surprised, disgusted, fearful. Return only the emotion and nothing else:"

        self.system_message = system_message
        self.text = text
        return self.api_call()