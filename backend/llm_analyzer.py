# backend/llm_analyzer.py
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMAnalyzer:
    """Handles LLM analysis using Groq"""
    
    def __init__(self, api_key=None):
        """Initialize with API key and system prompt"""
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment or parameter")
        
        self.client = Groq(api_key=self.api_key)
        
        # System prompt
        self.system_prompt = """
You are a financial analyst specializing in Indian stock market corporate announcements. 
Your role is to analyze BSE (Bombay Stock Exchange) announcements and provide clear, 
actionable insights for investors.

Key responsibilities:
- Extract critical information from corporate announcements
- Assess potential impact on stock price and investor sentiment
- Identify material events (mergers, acquisitions, financial results, regulatory changes)
- Provide concise, professional summaries
- Avoid speculation - focus on factual analysis
- Use simple language suitable for both retail and institutional investors

Your analysis should help investors quickly understand:
1. What happened?
2. Why does it matter?
3. What's the likely impact?
"""
    
    def prepare_prompt(self, announcement, pdf_text=None):
        """Prepare the prompt for LLM"""
        prompt = f"""
Analyze this corporate announcement and provide a concise summary.

Stock Code: {announcement.get('stock_code')} 
Title: {announcement.get('title')}
Category: {announcement.get('category')}
Description: {announcement.get('description', 'N/A')}
Date: {announcement.get('announcement_date')}
Submission Time: {announcement.get('submission_time')}

"""
        
        # Add PDF text if available (limit to 5000 chars)
        if pdf_text and len(pdf_text.strip()) > 50:
            prompt += f"\nPDF Content:\n{pdf_text[:5000]}\n"
        
        prompt += """
Please provide:
1. Key Points (2-3 bullet points)
2. Impact Assessment (Positive/Negative/Neutral with brief reason)
3. Brief Summary (2-3 sentences)

Keep it concise and focused on actionable insights for investors.
"""
        return prompt
    
    def analyze_announcement(self, announcement, pdf_text=None):
        """Analyze announcement with optional PDF text"""
        try:
            prompt = self.prepare_prompt(announcement, pdf_text)
            
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="openai/gpt-oss-20b",
                temperature=0.3,
                max_tokens=1000
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            print(f"    ✗ LLM error: {e}")
            return f"Error analyzing: {str(e)}"
    
    def test_connection(self):
        """Test if API key works"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": "Say 'API is working'"
                    }
                ],
                model="openai/gpt-oss-20b"
            )
            print(f"✓ API Response: {chat_completion.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"✗ API test failed: {e}")
            return False

if __name__ == "__main__":
    analyzer = LLMAnalyzer()
    analyzer.test_connection()