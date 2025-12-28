import os
import json
import google.generativeai as genai
from google.generativeai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GEMINI_API_KEY not found in environment variables. API calls will fail.")

def create_hrj_gemini_prompt(signal_message: str) -> str:
    """
    Creates a prompt for Gemini to parse an HRJ-style trade signal.
    """
    prompt = f"""Given the following plain text message:
---
{signal_message}
---
Determine if this message is a trade signal. If it is, output the message as a single, minified JSON object using the following Django models as a schema. If it is not a signal message, you MUST respond with the single word: false.

**MODELS (SCHEMA):**
```python
class HRJDiscordSignals(models.Model):
    asset = models.CharField(max_length=255)
    trade_type = models.CharField(max_length=5, choices=[('long', 'short')])
    leverage = models.IntegerField(default=1)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    entry_price = models.DecimalField(max_digits=20, decimal_places=10)
    entry_order_type = models.CharField(max_length=6, choices=[('market', 'limit')])
    stop_loss = models.DecimalField(max_digits=20, decimal_places=10)

class HRJTakeProfitTrades(models.Model):
    signal = models.ForeignKey(HRJDiscordSignals, on_delete=models.CASCADE)
    series_num = models.IntegerField(default=1)
    tp_price = models.DecimalField(max_digits=20, decimal_places=10)
```

**RULES:**
1. Your entire response must be ONLY the JSON object or the word `false`.
2. Do NOT include any explanations, comments, or markdown formatting (like ```json).
3. Extract numerical values only (e.g., `5` from `5X`, `3` from `3% of capital`).
4. The `trade_type` and `entry_order_type` must be lowercase.
5. The final JSON must have a root key "HRJDiscordSignals" and a nested key "HRJTakeProfitTrades".

**EXAMPLE 1 (VALID SIGNAL):**
*Message:*
LINK/USDT (LONG)
Leverage: 5X 
Balance: 3% of capital
Entry: 12.32 - (limit order)
TP1: 14.92
TP2: 18.73
SL: 9.89

*Your Output:*
{{"HRJDiscordSignals":{{"asset":"LINK/USDT","trade_type":"long","leverage":5,"balance":3.00,"entry_price":12.32,"entry_order_type":"limit","stop_loss":9.89}},"HRJTakeProfitTrades":[{{"series_num":1,"tp_price":14.92}},{{"series_num":2,"tp_price":18.73}}]}}

**EXAMPLE 2 (INVALID SIGNAL):**
*Message:*
✅ The first target of this BTC/USDT was reached @Brigade ⚔️

*Your Output:*
false
"""
    return prompt

def create_fj_gemini_prompt(signal_message: str) -> str:
    """
    Creates a prompt for Gemini to parse an FJ-style trade signal.
    """
    prompt = f"""Given the following plain text message:
---
{signal_message}
---
Determine if this message is a trade signal. If it is, output the message as a single, minified JSON object using the following Django models as a schema. If it is not a signal message, you MUST respond with the single word: false.

**MODELS (SCHEMA):**
```python
class FJDiscordSignals(models.Model):
    asset = models.CharField(max_length=255)
    trade_type = models.CharField(max_length=5, choices=[('long', 'short')])
    entry_price = models.DecimalField(max_digits=20, decimal_places=10)
    entry_order_type = models.CharField(max_length=6, choices=[('market', 'limit')])
    stop_loss = models.DecimalField(max_digits=20, decimal_places=10)

class FJTakeProfitTrades(models.Model):
    signal = models.ForeignKey(FJDiscordSignals, on_delete=models.CASCADE)
    series_num = models.IntegerField()
    tp_price = models.DecimalField(max_digits=20, decimal_places=10)
```

**RULES:**
1. Your entire response must be ONLY the JSON object or the word `false`.
2. Do NOT include any explanations, comments, or markdown formatting (like ```json).
3. Replace commas with periods for decimal numbers (e.g., `81,97` -> `81.97`).
4. The `trade_type` and `entry_order_type` must be lowercase.
5. The final JSON must have a root key "FJDiscordSignals" and a nested key "FJTakeProfitTrades".

**EXAMPLE 1 (VALID SIGNAL):**
*Message:*
LTC/USDT (long) 1D chart
Entry: 81,97 - (market)
TP1: 87,93
TP2: 95,40
SL: 72,03

*Your Output:*
{{"FJDiscordSignals":{{"asset":"LTC/USDT","trade_type":"long","entry_price":81.97,"entry_order_type":"market","stop_loss":72.03}},"FJTakeProfitTrades":[{{"series_num":1,"tp_price":87.93}},{{"series_num":2,"tp_price":95.40}}]}}

**EXAMPLE 2 (INVALID SIGNAL):**
*Message:*
TP 1 was reached @Brigade ⚔️

*Your Output:*
false
"""
    return prompt

def call_gemini_api(prompt: str) -> str:
    """
    Calls the Gemini API with a given prompt and returns the cleaned response.

    Args:
        prompt: The prompt to send to the Gemini API.

    Returns:
        A string containing the JSON response, 'false', or an error message.
    """
    if not api_key:
        return "Error: GEMINI_API_KEY not found. Please set it in your environment."

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Clean up potential markdown fences that the LLM might add despite instructions
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
             response_text = response_text[3:-3].strip()

        return response_text

    except types.generation_types.BlockedPromptError as e:
        return f"API call blocked due to a prompt safety issue: {e}"
    except Exception as e:
        return f"An unexpected error occurred while calling the Gemini API: {e}"

if __name__ == "__main__":
    # --- HRJ Example ---
    hrj_valid_signal = """LINK/USDT (LONG)
Leverage: 5X 
Balance: 3% of capital
Entry: 12.32 - (limit order)
TP1: 14.92
TP2: 18.73
SL: 9.89
R:R: 8"""
    hrj_invalid_signal = "✅ The first target of this BTC/USDT was reached @Brigade ⚔️"

    print("--- GENERATING HRJ PROMPT (VALID) ---")
    hrj_prompt_valid = create_hrj_gemini_prompt(hrj_valid_signal)
    # print(hrj_prompt_valid) # Uncomment to see the full prompt
    print("\n--- CALLING GEMINI FOR HRJ (VALID) ---")
    hrj_response_valid = call_gemini_api(hrj_prompt_valid)
    print(hrj_response_valid)

    print("\n--- GENERATING HRJ PROMPT (INVALID) ---")
    hrj_prompt_invalid = create_hrj_gemini_prompt(hrj_invalid_signal)
    print("\n--- CALLING GEMINI FOR HRJ (INVALID) ---")
    hrj_response_invalid = call_gemini_api(hrj_prompt_invalid)
    print(hrj_response_invalid)

    # --- FJ Example ---
    fj_valid_signal = """LTC/USDT (long) 1D chart 
Entry: 81,97 - (market)
TP1: 87,93
TP2: 95,40
SL: 72,03
R:R: 8,58"""
    fj_invalid_signal = "TP 1 was reached @Brigade ⚔️"

    print("\n\n--- GENERATING FJ PROMPT (VALID) ---")
    fj_prompt_valid = create_fj_gemini_prompt(fj_valid_signal)
    # print(fj_prompt_valid) # Uncomment to see the full prompt
    print("\n--- CALLING GEMINI FOR FJ (VALID) ---")
    fj_response_valid = call_gemini_api(fj_prompt_valid)
    print(fj_response_valid)

    print("\n--- GENERATING FJ PROMPT (INVALID) ---")
    fj_prompt_invalid = create_fj_gemini_prompt(fj_invalid_signal)
    print("\n--- CALLING GEMINI FOR FJ (INVALID) ---")
    fj_response_invalid = call_gemini_api(fj_prompt_invalid)
    print(fj_response_invalid)