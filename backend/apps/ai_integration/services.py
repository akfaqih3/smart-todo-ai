
import requests
import json
from django.conf import settings # To access Django settings (e.g., AI_MODEL_API_URL)
from django.utils import timezone
from datetime import timedelta
import re

class AIService:
    """
    A service class to interact with the local AI model (LM Studio).
    Encapsulates all AI-related functionalities.
    """
    def __init__(self, api_url=None, model_name=None):
        """
        Initializes the AI Service with the API URL and model name.
        """
        self.api_url = api_url or getattr(settings, 'AI_MODEL_API_URL', 'http://localhost:1234/v1/chat/completions' )
        self.model_name = model_name or getattr(settings, 'AI_MODEL_NAME', 'local-model') # Default model name for LM Studio

        # Basic headers for the API request
        self.headers = {
            "Content-Type": "application/json",
        }

    def _make_request(self, messages, max_tokens=150, temperature=0.7):
        """
        Internal method to send a request to the AI model API.
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            # "stream": False # Set to True if you want streaming responses
        }
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with AI model: {e}")
            return None

    def _extract_content(self, response):
        """
        Extracts the content from the AI model's response.
        """
        if response and 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content'].strip()
        return None

    def analyze_context(self, context_text):
        """
        Analyzes a given context text to extract insights like keywords, sentiment, etc.
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant that analyzes text and extracts key information."},
            {"role": "user", "content": f"Analyze the following text and extract key entities, keywords, and a general sentiment (positive, negative, neutral). Format the output as a JSON object with keys 'entities', 'keywords', 'sentiment'. Text: '{context_text}'"}
        ]
        response = self._make_request(messages, max_tokens=300, temperature=0.5)
        if response:
            content = self._extract_content(response)
            try:
                # Attempt to parse the content as JSON
                return json.loads(content)
            except json.JSONDecodeError:
                print(f"AI response was not valid JSON: {content}")
                return {"error": "AI response format error", "raw_response": content}
        return None

    def get_task_priority_score(self, task_title, task_description, context_insights=None):
        """
        Generates an AI-powered priority score for a task based on its details and context.
        Score should be between 0 and 100.
        """
        context_info = ""
        if context_insights:
            context_info = f"Relevant context insights: {json.dumps(context_insights)}. "

        messages = [
            {"role": "system", "content": "You are an AI assistant that helps prioritize tasks. Assign a priority score from 0 to 100, where 100 is most urgent. ONLY output the score as a number, nothing else. For example: 75"},
            {"role": "user", "content": f"Task: '{task_title}'. Description: '{task_description}'. {context_info}What is the priority score (0-100)? ONLY the number:"}
        ]
        response = self._make_request(messages, max_tokens=10, temperature=0.2) # Low temperature for consistent scores
        if response:
            content = self._extract_content(response)
            # Clean the content: extract only numbers
            numbers = re.findall(r'\d+\.?\d*', content) # Find all numbers (integers or floats)
            if numbers:
                try:
                    score = float(numbers[0]) # Take the first number found
                    return max(0, min(100, score))
                except ValueError:
                    print(f"AI response for priority could not be converted to number after cleaning: {content}")
            else:
                print(f"AI response for priority contained no numbers: {content}")
        return 0.0

    def suggest_deadline(self, task_title, task_description, current_date, context_insights=None):
        """
        Suggests a realistic deadline for a task.
        """
        context_info = ""
        if context_insights:
            context_info = f"Relevant context insights: {json.dumps(context_insights)}. "

        messages = [
            {"role": "system", "content": "You are an AI assistant that suggests realistic deadlines. Output the suggested deadline in 'YYYY-MM-DD' format. ONLY output the date, nothing else. Example: User: 'Task: Buy groceries'. Current date: 2025-07-06. AI: 2025-07-07"},
            {"role": "user", "content": f"Task: '{task_title}'. Description: '{task_description}'. Current date: {current_date.strftime('%Y-%m-%d')}. ONLY the date (YYYY-MM-DD):"}
        ]
        response = self._make_request(messages, max_tokens=20, temperature=0.7)
        if response:
            content = self._extract_content(response)
            # Try to extract a date-like string first
            # This regex looks for YYYY-MM-DD pattern
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', content)
            if date_match:
                date_string = date_match.group(0)
                try:
                    # Convert date object to datetime object at the start of the day
                    return timezone.make_aware(timezone.datetime.strptime(date_string, '%Y-%m-%d')) # <--- CHANGE HERE
                except ValueError:
                    print(f"AI response for deadline was not a valid date after cleaning: {content}")
            else:
                print(f"AI response for deadline did not contain a YYYY-MM-DD pattern: {content}")
        # Fallback: suggest 7 days from now if AI fails
        # Convert date object to datetime object at the start of the day
        return timezone.make_aware(timezone.datetime.combine(current_date + timedelta(days=7), timezone.datetime.min.time())) # <--- CHANGE HERE
        
    def suggest_categories_and_tags(self, task_title, task_description, existing_categories=None):
        """
        Suggests categories and tags for a task.
        """
        existing_cats_info = ""
        if existing_categories:
            existing_cats_info = f"Existing categories: {', '.join(existing_categories)}. "

        messages = [
            {"role": "system", "content": "You are an AI assistant that suggests categories and tags for tasks. Output a comma-separated list of categories/tags. ONLY output the comma-separated list, nothing else. For example: 'Marketing, Social Media, Campaign'"},
        {"role": "user", "content": f"Task: '{task_title}'. Description: '{task_description}'. {existing_cats_info}Suggest categories and tags for this task (comma-separated, ONLY the list):"}
        ]
        response = self._make_request(messages, max_tokens=50, temperature=0.7)
        if response:
            content = self._extract_content(response)
            # Clean the content: remove numbers, newlines, and split by comma
            cleaned_content = content.replace('\n', ',').replace('.', '').strip() # Remove newlines and periods
            # Split by comma, strip whitespace, and filter out empty strings
            return [tag.strip() for tag in cleaned_content.split(',') if tag.strip()]
        return []

    def enhance_task_description(self, task_title, task_description, context_insights=None):
        """
        Enhances a task description with more details based on context.
        """
        context_info = ""
        if context_insights:
            context_info = f"Relevant context insights: {json.dumps(context_insights)}. "

        messages = [
            {"role": "system", "content": "You are an AI assistant that enhances task descriptions. Expand on the provided task description, making it more detailed and actionable, especially considering any provided context. Keep it concise but informative."},
            {"role": "user", "content": f"Task: '{task_title}'. Original Description: '{task_description}'. {context_info}Enhanced Description:"}
        ]
        response = self._make_request(messages, max_tokens=200, temperature=0.8)
        if response:
            return self._extract_content(response)
        return task_description # Return original if AI fails

