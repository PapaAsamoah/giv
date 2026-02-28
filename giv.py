import os
import json
import re
from google import genai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

load_dotenv('/Users/noahangus/Comservice/.env')

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
print(f"✅ API Key loaded: {api_key[:20]}...")

client = genai.Client(api_key=api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_ai():
    user_question = request.json.get('question')
    
    # Prompt Gemini to return JSON
    formatted_prompt = f"""
Find community service opportunities related to: {user_question}

Return at least 3 opportunities if possible.

Return ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "opportunities": [
    {{
      "company_name": "Name of organization",
      "location": ["City", "State"],
      "signup_process": ["Step 1", "Step 2"],
      "contact_info": ["Phone", "Email", "Website"],
      "additional_info": ["Details"]
    }}
  ]
}}

Only return JSON, nothing else.
"""

    
    try:
        # Get response from Gemini
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=formatted_prompt
        )
        
        # Clean up the response text
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if '```json' in response_text:
            response_text = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if response_text:
                response_text = response_text.group(1)
        elif '```' in response_text:
            response_text = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if response_text:
                response_text = response_text.group(1)
        
        # Parse JSON
        try:
            data = json.loads(response_text)
            
            print("✅ Successfully parsed JSON:")
            print(json.dumps(data, indent=2))
            
            return jsonify({
                'success': True,
                'data': data
            })
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Response was: {response_text[:200]}")
            
            # Fallback: return raw text
            return jsonify({
                'success': True,
                'answer': response.text,
                'parse_error': True
            })
    
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
