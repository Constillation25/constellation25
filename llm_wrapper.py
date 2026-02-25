#!/usr/bin/env python3
"""
LLM Wrapper — Unified interface for multiple LLM providers.
Supports: Claude (Anthropic), GPT (OpenAI), Grok (xAI), Qwen, Local models
"""
import os, sys, json, time, subprocess

class LLMWrapper:
    """
    Unified LLM interface with automatic provider detection and fallback.
    FRAMEWORK PILLAR: Adaptive Execution (provider failover)
    """
    
    def __init__(self):
        self.providers = self._detect_available_providers()
        self.default_provider = self.providers[0] if self.providers else None
    
    def _detect_available_providers(self):
        """Detect which LLM providers are configured."""
        available = []
        if os.getenv("ANTHROPIC_API_KEY"):
            available.append("anthropic")
        if os.getenv("OPENAI_API_KEY"):
            available.append("openai")
        if os.getenv("XAI_API_KEY"):
            available.append("xai")
        if self._check_ollama():
            available.append("ollama")
        return available
    
    def _check_ollama(self):
        """Check if Ollama is running locally."""
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/tags"],
                capture_output=True, timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def call(self, prompt, provider=None, model=None, max_tokens=1024, temperature=0.7):
        """
        Make an LLM call with automatic provider selection and retry.
        FRAMEWORK PILLAR: Adaptive Execution (retry with fallback)
        """
        start_time = time.time()
        provider = provider or self.default_provider
        
        if not provider:
            return {
                "success": False,
                "error": "No LLM providers available. Set API keys or install Ollama.",
                "response": None
            }
        
        # Try primary provider
        result = self._call_provider(provider, prompt, model, max_tokens, temperature)
        
        # Fallback to other providers if primary fails
        if not result["success"] and len(self.providers) > 1:
            for fallback in self.providers:
                if fallback != provider:
                    result = self._call_provider(fallback, prompt, model, max_tokens, temperature)
                    if result["success"]:
                        break
        
        result["latency_ms"] = int((time.time() - start_time) * 1000)
        return result
    
    def _call_provider(self, provider, prompt, model, max_tokens, temperature):
        """Call specific LLM provider."""
        try:
            if provider == "anthropic":
                return self._call_anthropic(prompt, model or "claude-sonnet-4-20250514", max_tokens, temperature)
            elif provider == "openai":
                return self._call_openai(prompt, model or "gpt-4", max_tokens, temperature)
            elif provider == "xai":
                return self._call_xai(prompt, model or "grok-beta", max_tokens, temperature)
            elif provider == "ollama":
                return self._call_ollama(prompt, model or "qwen2.5:7b", max_tokens, temperature)
            else:
                return {"success": False, "error": f"Unknown provider: {provider}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _call_anthropic(self, prompt, model, max_tokens, temperature):
        """Call Anthropic Claude API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "success": True,
                "provider": "anthropic",
                "model": model,
                "response": message.content[0].text,
                "tokens": message.usage.input_tokens + message.usage.output_tokens
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "anthropic"}
    
    def _call_openai(self, prompt, model, max_tokens, temperature):
        """Call OpenAI GPT API."""
        try:
            import openai
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "success": True,
                "provider": "openai",
                "model": model,
                "response": response.choices[0].message.content,
                "tokens": response.usage.total_tokens
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "openai"}
    
    def _call_xai(self, prompt, model, max_tokens, temperature):
        """Call xAI Grok API."""
        try:
            import openai
            client = openai.OpenAI(
                api_key=os.getenv("XAI_API_KEY"),
                base_url="https://api.x.ai/v1"
            )
            response = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "success": True,
                "provider": "xai",
                "model": model,
                "response": response.choices[0].message.content,
                "tokens": response.usage.total_tokens
            }
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "xai"}
    
    def _call_ollama(self, prompt, model, max_tokens, temperature):
        """Call local Ollama API."""
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/generate", 
                 "-d", json.dumps({
                     "model": model,
                     "prompt": prompt,
                     "stream": False,
                     "options": {
                         "num_predict": max_tokens,
                         "temperature": temperature
                     }
                 })],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "success": True,
                    "provider": "ollama",
                    "model": model,
                    "response": data.get("response", ""),
                    "tokens": 0  # Ollama doesn't return token count
                }
            else:
                return {"success": False, "error": "Ollama request failed", "provider": "ollama"}
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "ollama"}

# Function calling support
class FunctionRegistry:
    """
    Registry for tool/function calls that agents can invoke.
    FRAMEWORK PILLAR: Dynamic Assessment (capability discovery)
    """
    
    def __init__(self):
        self.functions = {}
    
    def register(self, name, func, description, parameters):
        """Register a callable function with metadata."""
        self.functions[name] = {
            "callable": func,
            "description": description,
            "parameters": parameters
        }
    
    def call(self, name, **kwargs):
        """Execute a registered function with parameters."""
        if name not in self.functions:
            return {"success": False, "error": f"Function '{name}' not found"}
        
        try:
            func = self.functions[name]["callable"]
            result = func(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_functions(self):
        """Return list of available functions for LLM context."""
        return [
            {
                "name": name,
                "description": meta["description"],
                "parameters": meta["parameters"]
            }
            for name, meta in self.functions.items()
        ]

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: llm_wrapper.py <prompt> [provider] [model]")
        print("Providers: anthropic, openai, xai, ollama")
        print("Set API keys: ANTHROPIC_API_KEY, OPENAI_API_KEY, XAI_API_KEY")
        sys.exit(1)
    
    prompt = sys.argv[1]
    provider = sys.argv[2] if len(sys.argv) > 2 else None
    model = sys.argv[3] if len(sys.argv) > 3 else None
    
    wrapper = LLMWrapper()
    print(f"Available providers: {wrapper.providers}", file=sys.stderr)
    
    result = wrapper.call(prompt, provider=provider, model=model)
    
    if result["success"]:
        print(json.dumps({
            "response": result["response"],
            "provider": result["provider"],
            "model": result["model"],
            "tokens": result.get("tokens", 0),
            "latency_ms": result["latency_ms"]
        }, indent=2))
    else:
        print(json.dumps({"error": result["error"]}, indent=2), file=sys.stderr)
        sys.exit(1)
