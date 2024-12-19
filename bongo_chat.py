from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
import cloudscraper
from http import HTTPStatus

@dataclass
class AIResponse:
    """
    Data class representing the response from an AI service.
    
    Attributes:
        content: The response text from the AI
        status_code: HTTP status code of the response
        error: Optional error message if the request failed
    """
    content: str
    status_code: int
    error: Optional[str] = None

class AIServiceError(Exception):
    """Base exception class for AI service errors."""
    pass

class InvalidPromptError(AIServiceError):
    """Exception raised when the prompt is invalid or empty."""
    pass

class ServiceConnectionError(AIServiceError):
    """Exception raised when connection to the AI service fails."""
    pass

class AIServiceBase(ABC):
    """
    Abstract base class defining the interface for AI service clients.
    
    This class provides a template for implementing different AI service clients
    with consistent error handling and response formatting.
    """
    
    @abstractmethod
    def generate_response(self, prompt: str) -> AIResponse:
        """
        Generate a response from the AI service.
        
        Args:
            prompt: Input text to send to the AI service
            
        Returns:
            AIResponse object containing the response and status
            
        Raises:
            InvalidPromptError: If the prompt is empty or invalid
            ServiceConnectionError: If connection to the service fails
            AIServiceError: For other AI service related errors
        """
        pass

    @abstractmethod
    def validate_prompt(self, prompt: str) -> None:
        """
        Validate the input prompt before sending to the service.
        
        Args:
            prompt: Input text to validate
            
        Raises:
            InvalidPromptError: If the prompt is invalid
        """
        pass

class BongoChatAI(AIServiceBase):
    """
    Implementation of AI service client for the Bongo Network Team API.
    
    This class handles communication with the API including headers management,
    request formatting, and error handling.
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the Bongo Chat AI client.
        
        Args:
            model: The model identifier to use for generation
        """
        self.model = model
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://darkness.ashlynn.workers.dev/chat/"
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.6',
            'origin': 'https://bongonetworkteambd.github.io',
            'priority': 'u=1, i',
            'referer': 'https://bongonetworkteambd.github.io/',
            'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }

    def validate_prompt(self, prompt: str) -> None:
        """
        Validate the input prompt.
        
        Args:
            prompt: The input text to validate
            
        Raises:
            InvalidPromptError: If prompt is empty or contains invalid characters
        """
        if not prompt or not isinstance(prompt, str):
            raise InvalidPromptError("Prompt cannot be empty and must be a string")
        if len(prompt.strip()) == 0:
            raise InvalidPromptError("Prompt cannot be whitespace only")

    def generate_response(self, prompt: str) -> AIResponse:
        """
        Generate a response from the AI service.
        
        Args:
            prompt: The input text to send to the AI
            
        Returns:
            AIResponse object containing the response and status
            
        Raises:
            InvalidPromptError: If prompt validation fails
            ServiceConnectionError: If connection to the service fails
            AIServiceError: For other service related errors
        """
        try:
            self.validate_prompt(prompt)
            
            params = {
                'prompt': prompt,
                'model': self.model
            }
            
            response = self.scraper.get(
                self.base_url,
                params=params,
                headers=self.headers
            )
            
            response_data = response.json()
            
            if response_data['status'] == HTTPStatus.OK:
                return AIResponse(
                    content=response_data['response'],
                    status_code=HTTPStatus.OK
                )
            else:
                return AIResponse(
                    content="",
                    status_code=response_data['status'],
                    error=response_data['type']
                )
                
        except InvalidPromptError as e:
            raise e
        except cloudscraper.exceptions.CloudflareChallengeError:
            raise ServiceConnectionError("Failed to bypass Cloudflare protection")
        except Exception as e:
            raise AIServiceError(f"Unexpected error: {str(e)}")

def main():
    """Main function to demonstrate usage of the BongoChatAI class."""
    try:
        ai_client = BongoChatAI()
        response = ai_client.generate_response("Hello")
        print(f"AI Response: {response.content}")
        
    except AIServiceError as e:
        print(f"Error occurred: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == '__main__':
    main()