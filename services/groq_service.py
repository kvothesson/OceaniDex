from typing import List, Dict, Any, Optional
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not found in environment variables")
            
        self.client = Groq(api_key=self.api_key)
        self.default_model = "llama-3.3-70b-versatile"
        self.rate_limit_info = {}

    async def generate_content(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate content using Groq (async wrapper for compatibility).
        
        Args:
            prompt (str): The prompt to send to the model
            system_prompt (Optional[str]): System prompt to guide the model's behavior
            
        Returns:
            str: The generated content
        """
        return self.get_completion(prompt, system_prompt)

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
        Get a completion from Groq.
        
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
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=stream
            )
            
            # Extract rate limit info from headers if available
            if hasattr(response, 'headers'):
                self.rate_limit_info = {
                    'x-ratelimit-remaining': response.headers.get('x-ratelimit-remaining'),
                    'x-ratelimit-limit': response.headers.get('x-ratelimit-limit'),
                    'x-ratelimit-reset': response.headers.get('x-ratelimit-reset')
                }
                print(f"📊 Rate limit info: {self.rate_limit_info}")
            
            if stream:
                return response
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            if "413" in error_msg or "too large" in error_msg.lower():
                print("⚠️ Request too large. Consider reducing content size or using chunked processing.")
                # Estimate token count (rough approximation)
                estimated_tokens = len(prompt.split()) * 1.3  # Rough token estimation
                print(f"📊 Estimated tokens: {estimated_tokens:.0f}")
                print("💡 Suggestions:")
                print("   - Reduce max_tokens parameter")
                print("   - Split content into smaller chunks")
                print("   - Use a different model with higher limits")
            elif "rate_limit" in error_msg.lower():
                print("⚠️ Rate limit exceeded. Check rate limit info in headers.")
                print(f"📊 Current rate limit info: {self.rate_limit_info}")
            raise Exception(f"Error getting completion from Groq: {error_msg}")

    def get_embeddings(self, texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
        """
        Get embeddings for a list of texts.
        
        Args:
            texts (List[str]): List of texts to get embeddings for
            model (str): Embedding model to use
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            raise Exception(f"Error getting embeddings from Groq: {str(e)}")
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of token count for a text.
        
        Args:
            text (str): Text to estimate tokens for
            
        Returns:
            int: Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters for English/Spanish
        return len(text) // 4
    
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
        total_text = system_prompt + " " + prompt
        estimated_input_tokens = self.estimate_tokens(total_text)
        total_estimated_tokens = estimated_input_tokens + max_tokens
        
        # Groq limits (approximate)
        model_limits = {
            "llama-3.3-70b-versatile": 6000,  # TPM limit
            "llama-3.1-8b-instant": 8000,
            "llama-3.1-70b-versatile": 6000,
            "mixtral-8x7b-32768": 32000
        }
        
        model_limit = model_limits.get(self.default_model, 6000)
        
        return {
            "estimated_input_tokens": estimated_input_tokens,
            "max_output_tokens": max_tokens,
            "total_estimated_tokens": total_estimated_tokens,
            "model_limit": model_limit,
            "within_limits": total_estimated_tokens <= model_limit,
            "recommendations": []
        }

    @staticmethod
    def is_available():
        return bool(os.getenv("GROQ_API_KEY")) 