import json
from litellm import completion

def call_llm(model_cfg, prompt, system_prompt=None):
    """通用 LLM 呼叫封裝"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = completion(
            model=model_cfg['model'],
            messages=messages,
            api_base=model_cfg.get('api_base'),
            max_tokens=model_cfg.get('max_tokens', 500),
            temperature=model_cfg.get('temperature', 0.3)
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return None

def call_llm_json(model_cfg, prompt, system_prompt="You are a helpful assistant that outputs JSON."):
    """呼叫 LLM 並嘗試解析 JSON"""
    content = call_llm(model_cfg, prompt, system_prompt)
    if not content:
        return None
    
    try:
        # 移除 Markdown Code Blocks
        clean_content = content.strip()
        if clean_content.startswith("```"):
            clean_content = clean_content.strip("`").strip()
            if clean_content.startswith("json"):
                clean_content = clean_content[4:].strip()
        return json.loads(clean_content)
    except Exception as e:
        print(f"Failed to parse JSON from LLM: {e}. Content: {content}")
        return None
