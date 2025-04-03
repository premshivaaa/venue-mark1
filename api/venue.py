from http.server import BaseHTTPRequestHandler
from google.generativeai import GenerativeModel, configure
import json
import os

# Configure Gemini with error handling
try:
    configure(api_key=os.environ.get("GEMINI_API_KEY"))
    gemini = GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Gemini initialization error: {str(e)}")

SYSTEM_PROMPT = """You are VenueBot. Provide 3 venue suggestions with:
1. Name
2. Type
3. General location
4. 1-sentence description
For off-topic queries, respond: "I only provide venue suggestions.""""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get and parse request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            query = data.get('query', '').strip()
            
            # Handle empty query
            if not query:
                response = "Please enter a valid query."
            # Handle off-topic queries
            elif any(kw in query.lower() for kw in ['weather', 'news', 'joke']):
                response = "I only provide venue suggestions."
            else:
                # Generate content with safety checks
                result = gemini.generate_content(f"{SYSTEM_PROMPT}\nQuery: {query}")
                
                # Check if response was blocked
                if hasattr(result, 'prompt_feedback') and result.prompt_feedback.block_reason:
                    response = "My response was blocked for safety reasons. Please try a different query."
                # Handle successful response
                elif hasattr(result, 'text'):
                    response = result.text
                elif hasattr(result, 'candidates') and result.candidates:
                    response = result.candidates[0].content.parts[0].text
                else:
                    response = "Sorry, I couldn't process that request."
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": response}).encode())
            
        except Exception as e:
            # Enhanced error handling
            error_msg = f"Error processing request: {str(e)}"
            print(error_msg)  # For server-side logging
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Could not get response",
                "details": error_msg
            }).encode())
