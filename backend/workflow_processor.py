# backend/workflow_processor.py
from database import get_db
from pdf_text_extractor import get_pdf_text_for_announcement
from llm_router import LLMRouter
from transcription_service import TranscriptionService
from rate_limited_llm import groq_client
import os
import json
from dotenv import load_dotenv


load_dotenv()

class WorkflowProcessor:
    """Orchestrates the agentic workflow for announcement processing"""
    
    def __init__(self):
        self.router = LLMRouter()
        self.transcription_service = TranscriptionService()
        self.groq_client = groq_client
    
    def update_announcement(self, ann_id, updates):
        """Update announcement in database"""
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [ann_id]
            
            cursor.execute(f"""
                UPDATE announcements 
                SET {set_clause}
                WHERE id = %s
            """, values)
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"    ✗ Update error: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def transcription_workflow(self, announcement, transcript_link):
        """Workflow for announcements with audio transcripts"""
        
        print(f"  📻 TRANSCRIPTION WORKFLOW")
        print(f"  Audio URL: {transcript_link[:80]}...")
        
        # Step 1: Transcribe audio
        diarized_transcript = self.transcription_service.transcribe_from_url(transcript_link)
        
        if not diarized_transcript:
            print(f"    ✗ Transcription failed")
            return False
        
        print(f"    ✓ Transcribed: {diarized_transcript['metadata']['total_speakers']} speakers detected")
        
        # Step 2: Generate LLM summary from transcript
        print(f"  → Generating summary from transcript...")
        summary = self.summarize_transcript(announcement, diarized_transcript)
        
        if not summary:
            print(f"    ✗ Summary generation failed")
            return False
        
        print(f"    ✓ Summary generated ({len(summary)} chars)")
        
        # Step 3: Save to database
        updates = {
            'transcript_link': transcript_link,
            'transcript_diarized': json.dumps(diarized_transcript),
            'llm_summary': summary,
            'workflow_type': 'transcription',
            'processed': True
        }
        
        return self.update_announcement(announcement['id'], updates)
    
    def simple_summary_workflow(self, announcement, pdf_text, headline):
        """Workflow for announcements without audio"""
        
        print(f"  📄 SIMPLE SUMMARY WORKFLOW")
        
        # Generate summary from PDF text and description
        summary = self.generate_simple_summary(announcement, pdf_text, headline)
        
        if not summary:
            print(f"    ✗ Summary generation failed")
            return False
        
        print(f"    ✓ Summary generated ({len(summary)} chars)")
        
        # Save to database
        updates = {
            'llm_summary': summary,
            'workflow_type': 'simple_summary',
            'processed': True
        }
        
        return self.update_announcement(announcement['id'], updates)
    
    def summarize_transcript(self, announcement, diarized_transcript):
        """Generate summary from diarized transcript"""
        
        # Convert diarized transcript to text for LLM
        transcript_text = "\n\n".join([
            f"{speaker['speaker']} ({speaker['timestamp']}): {speaker['text']}"
            for speaker in diarized_transcript['speakers'][:100]
        ])
        
        prompt = f"""Analyze this earnings call transcript:

                    Stock: {announcement.get('stock_code')}
                    Title: {announcement.get('title')}
                    Date: {announcement.get('announcement_date')}

                    Transcript (with speakers):
                    {transcript_text[:8000]}

                    Provide a comprehensive summary including:
                    1. Key Financial Highlights
                    2. Management Commentary
                    3. Q&A Key Points
                    4. Overall Sentiment (Positive/Negative/Neutral)

                    Be concise but thorough."""
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a financial analyst."},
                    {"role": "user", "content": prompt}
                ],
                model="openai/gpt-oss-20b",
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"    ✗ LLM error: {e}")
            return None
    
    def generate_simple_summary(self, announcement, pdf_text, headline):
        """Generate summary from PDF text (no transcript)"""
        
        prompt = f"""Summarize this corporate announcement:

Stock: {announcement.get('stock_code')}
Title: {announcement.get('title')}
Category: {announcement.get('category')}
Description: {announcement.get('description')}
Headline: {headline}

PDF Content:
{pdf_text[:3000] if pdf_text else 'Not available'}
    
Provide a concise summary (3-5 sentences) focusing on key points for investors."""
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a financial analyst."},
                    {"role": "user", "content": prompt}
                ],
                model="openai/gpt-oss-20b",
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"    ✗ LLM error: {e}")
            return None
    
    def process_announcement(self, announcement_id):
        """Main processing pipeline"""
        
        # Get announcement
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, stock_code, title, description, category, 
                   announcement_date, pdf_downloaded
            FROM announcements
            WHERE id = %s
        """, (announcement_id,))
        
        ann = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not ann:
            print(f"✗ Announcement {announcement_id} not found")
            return False
        
        print(f"\n{'='*80}")
        print(f"🔄 Processing: {ann['stock_code']} - {ann['title'][:60]}")
        print(f"{'='*80}")
        
        # Extract PDF text
        print(f"  → Extracting PDF text...")
        pdf_text = get_pdf_text_for_announcement(ann['id'])
        
        if pdf_text:
            print(f"    ✓ Extracted {len(pdf_text)} characters")
        else:
            print(f"    ⚠ No PDF text available")
        
        # Route using LLM
        print(f"  → Routing announcement...")
        routing_decision = self.router.route_announcement(ann, pdf_text)
        
        # Execute appropriate workflow
        if routing_decision['transcript_detected'] and routing_decision['process']:
            return self.transcription_workflow(ann, routing_decision['transcript_link'])
        else:
            headline = routing_decision.get('headline', 'Standard announcement')
            return self.simple_summary_workflow(ann, pdf_text, headline)
        

def __init__(self):
    self.router = LLMRouter()
    self.transcription_service = TranscriptionService()
    self.groq_client = groq_client  # Use rate-limited client

if __name__ == "__main__":
    processor = WorkflowProcessor()
    processor.process_announcement(2)  # Test with ID 2
