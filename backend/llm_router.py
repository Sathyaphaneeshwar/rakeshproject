# backend/llm_router.py
import re

class LLMRouter:
    """Router that uses pattern matching to detect audio links"""
    
    def __init__(self):
        pass
    
    def extract_audio_link(self, text):
        """Extract audio link using regex patterns"""
        if not text:
            return None
        
        # Patterns to match audio URLs
        patterns = [
            r'https?://[^\s<>"]+\.mp3',
            r'https?://[^\s<>"]+\.wav',
            r'https?://[^\s<>"]+\.m4a',
            r'https?://[^\s<>"]+\.aac',
            r'https?://[^\s<>"]+[/]audio[^\s<>"]+',
            r'https?://[^\s<>"]+recording[^\s<>"]+',
            r'https?://[^\s<>"]+earnings[_-]?call[^\s<>"]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(0)
                # Clean up URL (remove trailing characters)
                url = re.sub(r'[,;.\)]$', '', url)
                return url
        
        return None
    
    def route_announcement(self, announcement, pdf_text):
        """Route announcement based on audio link detection"""
        
        print(f"  → Searching for audio links (pattern matching)...")
        
        # Combine all text sources
        combined_text = " ".join([
            announcement.get('title', ''),
            announcement.get('description', ''),
            pdf_text[:5000] if pdf_text else ''
        ])
        
        # Extract audio link
        audio_link = self.extract_audio_link(combined_text)
        
        if audio_link:
            print(f"    ✓ Audio link found: {audio_link[:80]}...")
            return {
                "transcript_detected": True,
                "transcript_link": audio_link,
                "process": True,
                "headline": "Audio recording detected for transcription"
            }
        else:
            print(f"    ✗ No audio link detected")
            return {
                "transcript_detected": False,
                "transcript_link": None,
                "process": False,
                "headline": "Standard document announcement"
            }

if __name__ == "__main__":
    router = LLMRouter()
    
    # Test with Indegene example
    test = {
        "title": "Q1 Earnings Call",
        "description": "Recording available"
    }
    pdf = "Audio recording: https://bm.indegene.com/Audio+Recording+of+the+Q1FY26+earnings+call.mp3"
    
    print("Testing audio link detection:")
    print("="*60)
    result = router.route_announcement(test, pdf)
    print(f"\nResult: {result}")