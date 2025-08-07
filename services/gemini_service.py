import google.generativeai as genai
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.default_model = 'gemini-1.5-pro'

    async def generate_content(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate content using Gemini (async wrapper for compatibility).
        
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
        Get a completion from Gemini.
        
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
        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=top_p
                )
            )
            
            if stream:
                return response
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                print("⚠️ Rate limit or quota exceeded for Gemini.")
                print("💡 Suggestions:")
                print("   - Check your Gemini API quota")
                print("   - Reduce request frequency")
                print("   - Use a different model")
            elif "too large" in error_msg.lower():
                print("⚠️ Request too large for Gemini.")
                print("💡 Suggestions:")
                print("   - Reduce content size")
                print("   - Split into smaller chunks")
            raise Exception(f"Error getting completion from Gemini: {error_msg}")

    def get_embeddings(self, texts: List[str], model: str = "text-embedding-004") -> List[List[float]]:
        """
        Get embeddings for a list of texts using Gemini.
        
        Args:
            texts (List[str]): List of texts to get embeddings for
            model (str): Embedding model to use
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            embedding_model = genai.get_model(model)
            embeddings = []
            for text in texts:
                result = embedding_model.embed_content(text)
                embeddings.append(result['embedding'])
            return embeddings
        except Exception as e:
            raise Exception(f"Error getting embeddings from Gemini: {str(e)}")
    
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
        Check if content size is within Gemini limits.
        
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
        
        # Gemini limits (approximate)
        model_limits = {
            "gemini-1.5-pro": 1000000,  # Very high limit
            "gemini-1.5-flash": 1000000,
            "gemini-1.0-pro": 30000
        }
        
        model_limit = model_limits.get(self.default_model, 1000000)
        
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
        return bool(os.getenv("GEMINI_API_KEY")) 