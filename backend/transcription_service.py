# backend/transcription_service.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TranscriptionService:
    """Handles audio transcription with Deepgram (with diarization)"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('DEEPGRAM_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY not found in .env file")
    
    def transcribe_from_url(self, audio_url):
        """
        Transcribe audio directly from URL with speaker diarization using REST API
        """
        try:
            print(f"    → Transcribing from URL: {audio_url[:60]}...")
            
            # Deepgram API endpoint
            url = "https://api.deepgram.com/v1/listen"
            
            # Parameters
            params = {
                "model": "nova-2",
                "language": "en",
                "diarize": "true",
                "punctuate": "true",
                "paragraphs": "true",
                "smart_format": "true"
            }
            
            # Headers
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Payload with URL
            payload = {
                "url": audio_url
            }
            
            # Make request
            response = requests.post(url, params=params, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            
            print(f"    ✓ Transcription complete")
            return self.format_diarized_output(result)
            
        except Exception as e:
            print(f"    ✗ Transcription error: {e}")
            return None
    
    def format_diarized_output(self, deepgram_result):
        """Format Deepgram response into clean speaker-separated structure"""
        
        try:
            # Get words with speaker info
            results = deepgram_result.get('results', {})
            channels = results.get('channels', [])
            
            if not channels:
                return None
            
            words = channels[0].get('alternatives', [{}])[0].get('words', [])
            
            # Group by speaker
            formatted = {
                "speakers": [],
                "metadata": {
                    "duration": deepgram_result.get('metadata', {}).get('duration', 0)
                }
            }
            
            current_speaker = None
            current_text = []
            current_start = None
            
            for word in words:
                speaker = word.get('speaker', 0)
                
                if speaker != current_speaker:
                    # Save previous speaker's text
                    if current_text:
                        formatted["speakers"].append({
                            "speaker": f"Speaker {current_speaker}",
                            "timestamp": f"{current_start:.2f}s",
                            "text": " ".join(current_text)
                        })
                    
                    # Start new speaker
                    current_speaker = speaker
                    current_text = [word.get('word', '')]
                    current_start = word.get('start', 0)
                else:
                    current_text.append(word.get('word', ''))
            
            # Add last speaker
            if current_text:
                formatted["speakers"].append({
                    "speaker": f"Speaker {current_speaker}",
                    "timestamp": f"{current_start:.2f}s",
                    "text": " ".join(current_text)
                })
            
            formatted["metadata"]["total_speakers"] = len(set(
                s["speaker"] for s in formatted["speakers"]
            ))
            
            return formatted
            
        except Exception as e:
            print(f"    ✗ Formatting error: {e}")
            return None

if __name__ == "__main__":
    service = TranscriptionService()
    
    # Test with Deepgram's sample audio
    test_url = "https://static.deepgram.com/examples/Bueller-Life-moves-pretty-fast.wav"
    result = service.transcribe_from_url(test_url)
    
    if result:
        print("\n✓ Transcription Result:")
        print(f"Speakers detected: {result['metadata']['total_speakers']}")
        print(f"Total utterances: {len(result['speakers'])}")
        print(f"\nFirst 3 utterances:")
        for i, utterance in enumerate(result['speakers'][:3]):
            print(f"{i+1}. {utterance['speaker']} ({utterance['timestamp']}): {utterance['text'][:100]}")