from google import genai
from google.genai import types
from app.config import settings
from app.models.job_analysis import JobAnalysisSchema

class AIEngineService:
    def __init__(self):
        # Initializes using GEMINI_API_KEY from environment configurations safely
        self.client = genai.Client()

    def analyze_job_description(self, raw_text: str) -> JobAnalysisSchema:
        """Parses raw text data to output clean validated structured schema objects."""
        prompt = f"Analyze the following job description text and extract structured criteria metadata:\n\n{raw_text}"
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JobAnalysisSchema,
                temperature=0.1 # Low variance ensures reliable rule matching
            ),
        )
        # Parse result directly into validation schema tracking contract
        return JobAnalysisSchema.model_validate_json(response.text)

    def generate_text_embedding(self, text: str) -> list[float]:
        """Generates standard dense vector arrays representing semantic contextual intent."""
        # Clean text layout slightly to prevent sparse array anomalies
        sanitized_text = text.replace("\n", " ").strip()
        
        response = self.client.models.embed_content(
            model='gemini-embedding-2',
            contents=sanitized_text,
            config=types.EmbedContentConfig(
                output_dimensionality=1536
            )
        )
        # Access vector float values returned by Gemini API matrix
        return response.embeddings[0].values