from http.server import BaseHTTPRequestHandler
from google.generativeai import GenerativeModel, configure
import json
import os  # For environment variables

# Configure Gemini (API key set in Vercel env)
configure(api_key=os.environ.get("GEMINI_API_KEY"))
gemini = GenerativeModel('gemini-pro')

SYSTEM_PROMPT = """You are VenueBot. Provide 3 venue suggestions with:
1. Name
2. Type
3. General location
4. 1-sentence description
For off-topic queries, respond: "I only provide venue suggestions.""""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            query = json.loads(post_data)['query']
            
            if any(kw in query.lower() for kw in ['weather', 'news', 'joke']):
                response = "I only provide venue suggestions."
            else:
                response = gemini.generate_content(
                    f"{SYSTEM_PROMPT}\nQuery: {query}"
                ).text
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": response}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())