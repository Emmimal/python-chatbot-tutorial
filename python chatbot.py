# API-Integrated Chatbot with Multiple Services
import requests
import json
import os
from datetime import datetime
import random

class APIChatbot:
    def __init__(self):
        # API keys (in production, use environment variables)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        
        # API endpoints
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.weather_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Conversation history for context
        self.conversation_history = []
        
        # Intent patterns
        self.intent_patterns = {
            'weather': ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy'],
            'time': ['time', 'date', 'what time', 'current time'],
            'ai_chat': ['tell me', 'explain', 'what do you think', 'opinion', 'advice'],
            'calculation': ['calculate', 'math', 'plus', 'minus', 'multiply', 'divide']
        }
    
    def detect_intent(self, user_input):
        """
        Determine what kind of request the user is making
        """
        user_input_lower = user_input.lower()
        
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return intent
        
        return 'general_chat'
    
    def get_weather_info(self, city="London"):
        """
        Get current weather information
        """
        if not self.weather_api_key:
            return "I'd love to check the weather, but I need a weather API key to access current data."
        
        try:
            params = {
                'q': city,
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.weather_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                weather = data['weather'][0]['description']
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                
                return f"Weather in {city}: {weather.capitalize()}, {temp}°C (feels like {feels_like}°C), humidity {humidity}%"
            else:
                return f"Sorry, I couldn't get weather data for {city}. Please check the city name."
        
        except Exception as e:
            return f"Weather service is currently unavailable: {str(e)}"
    
    def get_current_time(self):
        """
        Get current date and time
        """
        now = datetime.now()
        return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def calculate_expression(self, expression):
        """
        Safely evaluate mathematical expressions
        """
        try:
            # Remove spaces and validate input
            expression = expression.replace(' ', '')
            
            # Basic security: only allow numbers and basic operators
            allowed_chars = set('0123456789+-*/.()= ')
            if not all(c in allowed_chars for c in expression):
                return "I can only handle basic math operations (+, -, *, /, parentheses)"
            
            # Remove 'calculate' and similar words
            expression = expression.lower()
            for word in ['calculate', 'what is', 'what\'s', '=']:
                expression = expression.replace(word, '')
            
            result = eval(expression)
            return f"The answer is: {result}"
        
        except Exception as e:
            return "I couldn't calculate that. Please use a format like '2 + 3' or '10 * 5'"
    
    def chat_with_openai(self, user_input):
        """
        Get intelligent responses from OpenAI's API
        """
        if not self.openai_api_key:
            # Fallback responses when OpenAI is not available
            fallback_responses = [
                "That's a thoughtful question! I'd need access to advanced AI models to give you a comprehensive answer.",
                "Interesting topic! For detailed analysis like this, I'd typically use more advanced language models.",
                "Great question! This is the kind of complex query that benefits from larger AI models with extensive training.",
                "I find that fascinating! For in-depth responses like this, I'd normally leverage more sophisticated AI systems."
            ]
            return random.choice(fallback_responses)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            # Build conversation context
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant integrated into a Python chatbot. Be concise but informative."}
            ]
            
            # Add recent conversation history
            for exchange in self.conversation_history[-3:]:  # Last 3 exchanges for context
                messages.append({"role": "user", "content": exchange['user']})
                messages.append({"role": "assistant", "content": exchange['bot']})
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            response = requests.post(self.openai_url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                return f"AI service temporarily unavailable (Status: {response.status_code})"
        
        except Exception as e:
            return f"AI service error: {str(e)}"
    
    def get_response(self, user_input):
        """
        Route user input to appropriate service based on intent
        """
        intent = self.detect_intent(user_input)
        
        if intent == 'weather':
            # Extract city name if mentioned
            words = user_input.split()
            city = "London"  # Default city
            # Simple city extraction (in production, use NER)
            for i, word in enumerate(words):
                if word.lower() in ['in', 'at', 'for'] and i + 1 < len(words):
                    city = words[i + 1]
                    break
            return self.get_weather_info(city)
        
        elif intent == 'time':
            return self.get_current_time()
        
        elif intent == 'calculation':
            return self.calculate_expression(user_input)
        
        elif intent == 'ai_chat':
            return self.chat_with_openai(user_input)
        
        else:
            # For general chat, try OpenAI first, fallback to simple responses
            if self.openai_api_key:
                return self.chat_with_openai(user_input)
            else:
                simple_responses = [
                    "That's interesting! Tell me more about what you're thinking.",
                    "I'd love to hear more about that topic from your perspective.",
                    "Great point! What led you to think about this?",
                    "That's a fascinating subject! What aspects interest you most?"
                ]
                return random.choice(simple_responses)
    
    def chat(self):
        """
        Start interactive API-powered conversation
        """
        print("🌐 API Chatbot: Hello! I'm connected to various online services.")
        print("I can check weather, tell time, do calculations, and have intelligent conversations!")
        print("Try asking: 'What's the weather in Paris?' or 'What time is it?' or 'Calculate 15 * 23'")
        print("Type 'quit' to exit.")
        print("-" * 80)
        
        # Show available services
        available_services = []
        if self.weather_api_key:
            available_services.append("Weather")
        if self.openai_api_key:
            available_services.append("AI Chat")
        available_services.extend(["Time/Date", "Calculator"])
        
        print(f"Available services: {', '.join(available_services)}")
        print("-" * 80)
        
        while True:
            user_input = input("You: ")
            
            if user_input.lower() in ['quit', 'exit', 'goodbye']:
                print("🌐 API Chatbot: Thanks for chatting! Stay connected!")
                break
            
            if not user_input.strip():
                continue
            
            # Get response
            response = self.get_response(user_input)
            print(f"🌐 API Chatbot: {response}")
            
            # Store conversation
            self.conversation_history.append({
                'user': user_input,
                'bot': response,
                'timestamp': datetime.now()
            })

# Usage example and setup instructions
if __name__ == "__main__":
    print("Setting up API Chatbot...")
    print("For full functionality, set these environment variables:")
    print("- OPENAI_API_KEY: Get from https://platform.openai.com/")
    print("- WEATHER_API_KEY: Get from https://openweathermap.org/api")
    print()
    
    bot = APIChatbot()
    bot.chat()
