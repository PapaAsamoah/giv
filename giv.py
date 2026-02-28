import os
import json
import re
from google import genai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

# Load environment variables
load_dotenv('/Users/noahangus/Comservice/.env')

app = Flask(__name__)

# API key setup
api_key = os.environ.get("GEMINI_API_KEY")
print(f"API Key loaded: {api_key[:20]}...")

client = genai.Client(api_key=api_key)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask_ai():
    user_question = request.json.get('question', '').strip()
    
    if not user_question:
        return jsonify({'success': False, 'error': 'No question provided.'})

    formatted_prompt = f"""
Find community service opportunities near the user related to: {user_question}

Return at least 3 opportunities if possible.

Return ONLY valid JSON. Do NOT include markdown, backticks, or extra text.
Use this exact format:
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
"""
    try:
        # Call Gemini API
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=formatted_prompt
        )
        response_text = response.text.strip()

        # Attempt to extract JSON from response
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        cleaned_json = match.group(0) if match else response_text

        try:
            # Parse JSON safely
            data = json.loads(cleaned_json)
            return jsonify({'success': True, 'data': data})
        except json.JSONDecodeError:
            # Return raw text if JSON parsing fails
            return jsonify({'success': True, 'answer': response_text, 'parse_error': True})

    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
