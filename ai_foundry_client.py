"""
Microsoft AI Foundry Client
Provides LLM capabilities using Azure AI Foundry endpoint with function calling support
"""
import os
import json
import requests
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class Message:
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class AIFoundryClient:
    def __init__(
        self,
        endpoint: str = None,
        api_key: str = None,
        deployment: str = "gpt-4o",
        api_version: str = "2024-08-01-preview"
    ):
        """Initialize AI Foundry client with endpoint and authentication"""
        self.endpoint = endpoint or os.getenv("AIFOUNDRY_ENDPOINT", "https://af-sdlc-dev.services.ai.azure.com")
        self.api_key = (
            api_key
            or os.getenv("AIFOUNDRY_API_KEY")
            or os.getenv("AZURE_OPENAI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        self.deployment = deployment
        self.api_version = api_version
        self.api_versions = [self.api_version, "2024-02-01-preview", "2024-02-15-preview"]
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Set AIFOUNDRY_API_KEY (or AZURE_OPENAI_API_KEY / OPENAI_API_KEY)."
            )
        self.api_key = self.api_key.strip().strip('"').strip("'")
        
        # Normalize endpoint to base host in case a path was provided.
        parsed = urlparse(self.endpoint)
        if parsed.scheme and parsed.netloc:
            self.endpoint = f"{parsed.scheme}://{parsed.netloc}"
        self.endpoint = self.endpoint.rstrip('/')
        
        # Build base URL
        self.base_url = f"{self.endpoint}/openai/deployments/{self.deployment}"
        
        # Set up headers
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
    
    def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send a chat completion request with optional function calling
        
        Args:
            messages: List of message dictionaries with role and content
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            tools: List of tool definitions for function calling
            tool_choice: Controls which tool to call ("auto", "none", or specific tool)
        
        Returns:
            Response dictionary containing choices, usage, and tool calls if any
        """
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Add tool/function calling if provided
        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice
        
        try:
            last_response = None
            for ver in self.api_versions:
                url = f"{self.base_url}/chat/completions?api-version={ver}"
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                if response.status_code == 200:
                    return response.json()
                last_response = response
                # 401/403 are auth issues and retrying versions will not help.
                if response.status_code in (401, 403):
                    break

            if last_response is not None:
                last_response.raise_for_status()
            raise Exception("AI Foundry request failed without a response")

        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if e.response else str(e)
            if e.response is not None and e.response.status_code == 401:
                raise Exception(
                    "AI Foundry API error: 401 - Invalid API key or endpoint mismatch. "
                    "Confirm AIFOUNDRY_ENDPOINT and rotate AIFOUNDRY_API_KEY. "
                    f"Details: {error_detail}"
                )
            raise Exception(f"AI Foundry API error: {e.response.status_code} - {error_detail}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def chat_with_functions(
        self,
        messages: List[Dict[str, Any]],
        functions: Dict[str, Any],
        max_iterations: int = 5,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Run a multi-turn conversation with automatic function execution
        
        Args:
            messages: Initial message list
            functions: Dictionary mapping function names to callable functions
            max_iterations: Maximum number of function call iterations
            temperature: Sampling temperature
        
        Returns:
            Final response with complete conversation history
        """
        # Convert functions to tool format
        tools = self._functions_to_tools(functions)
        
        conversation_history = messages.copy()
        iterations = 0
        
        while iterations < max_iterations:
            # Get AI response
            response = self.chat(
                messages=conversation_history,
                temperature=temperature,
                tools=tools,
                tool_choice="auto"
            )
            
            choice = response['choices'][0]
            message = choice['message']
            
            # Add assistant's response to history
            conversation_history.append({
                "role": "assistant",
                "content": message.get("content", ""),
                "tool_calls": message.get("tool_calls")
            })
            
            # Check if AI wants to call functions
            if choice.get('finish_reason') == 'tool_calls' and message.get('tool_calls'):
                # Execute each tool call
                for tool_call in message['tool_calls']:
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    tool_call_id = tool_call['id']
                    
                    print(f"🔧 AI calling function: {function_name}({function_args})")
                    
                    # Execute the function
                    if function_name in functions:
                        try:
                            result = functions[function_name](**function_args)
                            result_str = json.dumps(result) if not isinstance(result, str) else result
                        except Exception as e:
                            result_str = json.dumps({"error": str(e)})
                            print(f"❌ Function execution error: {e}")
                    else:
                        result_str = json.dumps({"error": f"Function {function_name} not found"})
                    
                    # Add function result to conversation
                    conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": result_str
                    })
                
                iterations += 1
            else:
                # No more function calls, conversation complete
                return {
                    "response": message.get("content", ""),
                    "conversation_history": conversation_history,
                    "iterations": iterations,
                    "usage": response.get("usage", {})
                }
        
        # Max iterations reached
        return {
            "response": "Maximum iterations reached",
            "conversation_history": conversation_history,
            "iterations": iterations,
            "max_iterations_reached": True
        }
    
    def _functions_to_tools(self, functions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert function dictionary to OpenAI tools format"""
        tools = []
        for func_name, func_obj in functions.items():
            # If function has __tool_schema__ attribute, use it
            if hasattr(func_obj, '__tool_schema__'):
                tools.append(func_obj.__tool_schema__)
            else:
                # Try to extract from docstring and type hints
                tools.append({
                    "type": "function",
                    "function": {
                        "name": func_name,
                        "description": func_obj.__doc__ or f"Execute {func_name}",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                })
        return tools


def tool_schema(schema: Dict[str, Any]):
    """Decorator to attach tool schema to a function"""
    def decorator(func):
        func.__tool_schema__ = {
            "type": "function",
            "function": schema
        }
        return func
    return decorator
