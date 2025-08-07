import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AIService:
    """
    Configurable AI service that can use either Groq or Gemini based on availability.
    """
    
    def __init__(self, preferred_service: str = "auto"):
        """
        Initialize AI service.
        
        Args:
            preferred_service (str): "groq", "gemini", or "auto" (default)
        """
        self.preferred_service = preferred_service
        self.service = None
        self.service_name = None
        
        # Try to initialize the preferred service
        if preferred_service == "auto":
            self._initialize_auto()
        elif preferred_service == "groq":
            self._initialize_groq()
        elif preferred_service == "gemini":
            self._initialize_gemini()
        else:
            raise ValueError("preferred_service must be 'groq', 'gemini', or 'auto'")
    
    def _initialize_auto(self):
        """Automatically choose the best available service."""
        # Try Groq first (faster, but has rate limits)
        if self._try_groq():
            return
        
        # Try Gemini as fallback
        if self._try_gemini():
            return
        
        raise Exception("No AI service available. Please check your API keys for GROQ_API_KEY or GEMINI_API_KEY")
    
    def _initialize_groq(self):
        """Initialize Groq service."""
        if not self._try_groq():
            raise Exception("Groq service not available. Please check your GROQ_API_KEY")
    
    def _initialize_gemini(self):
        """Initialize Gemini service."""
        if not self._try_gemini():
            raise Exception("Gemini service not available. Please check your GEMINI_API_KEY")
    
    def _try_groq(self) -> bool:
        """Try to initialize Groq service."""
        try:
            from groq_service import GroqService
            if GroqService.is_available():
                self.service = GroqService()
                self.service_name = "groq"
                print(f"✅ Using Groq service")
                return True
        except Exception as e:
            print(f"⚠️ Groq not available: {e}")
        return False
    
    def _try_gemini(self) -> bool:
        """Try to initialize Gemini service."""
        try:
            from gemini_service import GeminiService
            if GeminiService.is_available():
                self.service = GeminiService()
                self.service_name = "gemini"
                print(f"✅ Using Gemini service")
                return True
        except Exception as e:
            print(f"⚠️ Gemini not available: {e}")
        return False
    
    async def generate_content(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate content using the configured AI service.
        
        Args:
            prompt (str): The prompt to send to the model
            system_prompt (Optional[str]): System prompt to guide the model's behavior
            
        Returns:
            str: The generated content
        """
        if not self.service:
            raise Exception("No AI service available")
        
        return await self.service.generate_content(prompt, system_prompt)
    
    def get_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        top_p: float = 1,
        stream: bool = False
    ) -> str:
        """
        Get a completion from the configured AI service.
        
        Args:
            prompt (str): The user prompt
            system_prompt (Optional[str]): System prompt to guide the model's behavior
            model (Optional[str]): Model to use. If None, uses default model
            temperature (float): Sampling temperature
            max_tokens (int): Maximum number of tokens to generate
            top_p (float): Nucleus sampling parameter
            stream (bool): Whether to stream the response
            
        Returns:
            str: The completion text
        """
        if not self.service:
            raise Exception("No AI service available")
        
        return self.service.get_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=stream
        )
    
    def get_embeddings(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        """
        Get embeddings using the configured AI service.
        
        Args:
            texts (List[str]): List of texts to get embeddings for
            model (Optional[str]): Embedding model to use
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not self.service:
            raise Exception("No AI service available")
        
        return self.service.get_embeddings(texts, model)
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for a text.
        
        Args:
            text (str): Text to estimate tokens for
            
        Returns:
            int: Estimated token count
        """
        if not self.service:
            raise Exception("No AI service available")
        
        return self.service.estimate_tokens(text)
    
    def check_content_size(self, prompt: str, system_prompt: str = "", max_tokens: int = 4000) -> Dict[str, Any]:
        """
        Check if content size is within limits.
        
        Args:
            prompt (str): User prompt
            system_prompt (str): System prompt
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            Dict[str, Any]: Size information and recommendations
        """
        if not self.service:
            raise Exception("No AI service available")
        
        return self.service.check_content_size(prompt, system_prompt, max_tokens)
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the current service.
        
        Returns:
            Dict[str, Any]: Service information
        """
        return {
            "service_name": self.service_name,
            "preferred_service": self.preferred_service,
            "available": self.service is not None
        }
    
    @staticmethod
    def get_available_services() -> List[str]:
        """
        Get list of available AI services.
        
        Returns:
            List[str]: List of available service names
        """
        available = []
        
        # Check Groq
        try:
            from .groq_service import GroqService
            if GroqService.is_available():
                available.append("groq")
        except:
            pass
        
        # Check Gemini
        try:
            from .gemini_service import GeminiService
            if GeminiService.is_available():
                available.append("gemini")
        except:
            pass
        
        return available 