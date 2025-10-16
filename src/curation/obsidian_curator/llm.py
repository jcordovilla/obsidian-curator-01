"""
LLM interface supporting both OpenAI and Ollama providers.
Defaults to OpenAI for better accuracy with JSON schemas and multilingual content.
"""
import json
import os
from typing import Optional, Dict, Any, List
from openai import OpenAI
from pathlib import Path

# Initialize OpenAI client (reads from .env file or environment)
_openai_client = None

def _load_env():
    """Load environment variables from .env file if it exists."""
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    os.environ[key.strip()] = value

def _get_openai_client():
    """Lazy initialization of OpenAI client."""
    global _openai_client
    if _openai_client is None:
        # Load from .env file if present
        _load_env()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. "
                "Add it to .env file: OPENAI_API_KEY=your-key-here"
            )
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client

def chat_text(model: str, system: str, user: str, tokens: int = 512, temp: float = 0.2, provider: str = "openai", max_retries: int = 2) -> str:
    """
    Get text response from LLM.
    
    Args:
        model: Model identifier (e.g., 'gpt-5-2025-08-07', 'gpt-5-mini-2025-08-07')
        system: System prompt
        user: User prompt
        tokens: Maximum tokens to generate (up to 128K for GPT-5)
        temp: Temperature (0-2 for GPT-5)
        provider: 'openai' or 'ollama'
    
    Returns:
        Response text
    """
    if provider == "openai":
        client = _get_openai_client()
        
        # GPT-5/O3/O4 use reasoning tokens - need higher token limits
        is_reasoning_model = model.startswith("gpt-5") or model.startswith("o3") or model.startswith("o4")
        effective_tokens = tokens * 4 if is_reasoning_model else tokens
        
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "max_completion_tokens": effective_tokens
        }
        # Only add temperature for non-reasoning models
        if not is_reasoning_model:
            kwargs["temperature"] = temp
        
        # Retry logic for transient failures
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                
                # Check for empty response
                if not content or not content.strip():
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.5)
                        continue
                    else:
                        return ""
                
                return content
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(0.5)
                    continue
                else:
                    raise e
    
    elif provider == "ollama":
        # Fallback to Ollama for local models
        import requests
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "options": {
                "temperature": temp,
                "num_predict": tokens
            },
            "stream": False
        }
        r = requests.post("http://localhost:11434/api/chat", json=payload)
        r.raise_for_status()
        return r.json()["message"]["content"]
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def chat_json(
    model: str, 
    system: str, 
    user: str, 
    tokens: int = 512, 
    temp: float = 0.2,
    provider: str = "openai",
    json_schema: Optional[Dict[str, Any]] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Get JSON response from LLM with optional schema validation and retry logic.
    
    Args:
        model: Model identifier
        system: System prompt
        user: User prompt
        tokens: Maximum tokens to generate (up to 128K for GPT-5)
        temp: Temperature (0-2 for GPT-5)
        provider: 'openai' or 'ollama'
        json_schema: Optional JSON schema for validation
        max_retries: Maximum retry attempts for empty/invalid responses (GPT-5 bug mitigation)
    
    Returns:
        Parsed JSON response
    """
    if provider == "openai":
        client = _get_openai_client()
        
        # Build request kwargs
        # GPT-5/O3/O4 use reasoning tokens internally - need much higher token limits
        is_reasoning_model = model.startswith("gpt-5") or model.startswith("o3") or model.startswith("o4")
        effective_tokens = tokens * 4 if is_reasoning_model else tokens  # 4x for reasoning models
        
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system + "\n\nCRITICAL: Return ONLY valid JSON. No other text."},
                {"role": "user", "content": user}
            ],
            "max_completion_tokens": effective_tokens
        }
        
        # GPT-5/O3/O4: Don't use response_format (causes empty), fixed temperature
        if is_reasoning_model:
            # Reasoning models: No json_object format, no custom temperature
            pass
        else:
            # Standard models: Use json_object and custom temperature
            kwargs["response_format"] = {"type": "json_object"}
            kwargs["temperature"] = temp
        
        # Debug: Log request details
        if os.getenv("DEBUG_LLM"):
            print(f"DEBUG: Calling {model} with {len(kwargs['messages'])} messages")
            print(f"DEBUG: max_completion_tokens={kwargs.get('max_completion_tokens')}")
            print(f"DEBUG: has response_format={('response_format' in kwargs)}")
            print(f"DEBUG: has temperature={('temperature' in kwargs)}")
        
        # Make API call with retry logic for transient failures
        last_error = None
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(**kwargs)
                text = response.choices[0].message.content
                
                # Validate response is not empty
                if not text or not text.strip():
                    last_error = f"Empty response (attempt {attempt + 1}/{max_retries})"
                    print(f"Warning: {last_error}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        print(f"Warning: All {max_retries} attempts returned empty responses")
                        return _get_safe_default_response()
                
                # Clean up reasoning artifacts (GPT-5/O3 sometimes add these)
                if text.strip().startswith("Reasoning:"):
                    lines = text.split('\n')
                    text = '\n'.join(line for line in lines if not line.strip().startswith("Reasoning:"))
                
                # Successfully got non-empty response
                break
                
            except Exception as e:
                last_error = str(e)
                print(f"Warning: API error on attempt {attempt + 1}/{max_retries}: {str(e)[:100]}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    print(f"Warning: All attempts failed with errors")
                    return _get_safe_default_response()
        
        # Parse JSON response
        try:
            parsed = json.loads(text)
            
            # Validate parsed JSON is not empty/trivial
            if not parsed or parsed == {}:
                print(f"Warning: Parsed JSON is empty")
                return _get_safe_default_response()
            
            # Optional: validate against schema using Pydantic if provided
            if json_schema:
                from pydantic import TypeAdapter
                validator = TypeAdapter(json_schema)
                return validator.validate_python(parsed)
            
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"Warning: JSON decode failed: {e}")
            print(f"Response text: {text[:200]}")
            
            # Try to extract JSON from response (handle artifacts)
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    extracted = json.loads(text[start:end+1])
                    if extracted and extracted != {}:
                        return extracted
                except json.JSONDecodeError:
                    pass
            
            # All parsing attempts failed, return safe default
            return _get_safe_default_response()
    
    elif provider == "ollama":
        text = chat_text(model, system, user + "\n\nReturn ONLY strict JSON.", tokens, temp, provider="ollama")
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Try to extract JSON
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start:end+1])
                except json.JSONDecodeError:
                    pass
            print(f"Warning: Could not parse JSON from LLM response: {e}")
            return _get_safe_default_response()
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def embed_text(text: str, model: str, provider: str = "openai") -> Optional[List[float]]:
    """
    Generate embedding for text.
    
    Args:
        text: Text to embed
        model: Model identifier (e.g., 'text-embedding-3-small', 'nomic-embed-text')
        provider: 'openai' or 'ollama'
    
    Returns:
        Embedding vector or None on failure
    """
    if not text or not text.strip():
        return None
    
    if provider == "openai":
        client = _get_openai_client()
        # Truncate text if too long (8191 token limit for embedding models)
        # For GPT-5 context: 400K tokens, but embeddings use separate models
        if len(text) > 8000:
            text = text[:8000]
        
        response = client.embeddings.create(
            model=model,
            input=text,
            encoding_format="float"  # Explicit format for latest API
        )
        return response.data[0].embedding
    
    elif provider == "ollama":
        import requests
        r = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": model, "prompt": text}
        )
        r.raise_for_status()
        return r.json().get("embedding")
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def _get_safe_default_response() -> Dict[str, Any]:
    """Return safe default response when JSON parsing fails."""
    return {
        "categories": ["Unknown"],
        "tags": ["unknown"],
        "entities": {
            "organizations": [],
            "projects": [],
            "technologies": [],
            "locations": []
        },
        "usefulness": 0.3,
        "reasoning": "JSON parsing failed, using default",
        "publication_readiness": 0.3
    }
