import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from supabase import create_client, Client
from app.config import settings
from app.services.ai_engine import AIEngineService

def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def pipeline_processor():
    supabase = get_supabase()
    ai_engine = AIEngineService()

    print("Checking database for unprocessed raw job listings...")
    # Fetch job listings where embedding vectors have not yet been evaluated
    raw_jobs = supabase.table("jobs").select("*").is_("embedding", "null").limit(5).execute()

    if not raw_jobs.data:
        print("No new jobs to process.")
        return

    # Grab active resume to apply evaluation mappings against (Selects first active record)
    resume_query = supabase.table("resumes").select("*").limit(1).execute()
    if not resume_query.data:
        print("CRITICAL: Pipeline halted. Please upload at least one target baseline resume first.")
        return
    
    active_resume = resume_query.data[0]
    resume_embedding = active_resume.get("embedding")

    for job in raw_jobs.data:
        try:
            print(f"Analyzing listing: {job['title']} at {job['company']}...")
            
            # Step 1: Structural Extraction via Gemini Flash
            analysis = ai_engine.analyze_job_description(job['description'])
            
            # Step 2: Generate Context Vector Embedding via Gemini Embedding Engine
            job_vector = ai_engine.generate_text_embedding(job['description'])

            # Step 3: Update processed jobs target model table record
            supabase.table("jobs").update({
                "embedding": job_vector,
                "is_remote": True if analysis.remote_policy == "remote" else False,
                "salary_min": analysis.salary_min,
                "salary_max": analysis.salary_max,
                "currency": analysis.currency
            }).eq("id", job["id"]).execute()

            # Step 4: Run mathematical similarity matching via Supabase RPC calculations
            if resume_embedding:
                # Call stored procedure matching engine
                match_rpc = supabase.rpc("match_jobs_to_resume", {
                    "query_embedding": resume_embedding,
                    "match_threshold": 0.3, # Filters extreme anomalies
                    "match_count": 1
                }).execute()

                if match_rpc.data:
                    similarity_score = match_rpc.data[0]["similarity"]
                    
                    # Convert to aggregate standard 100 percentage layout bounds
                    final_score = round(similarity_score * 100, 2)
                    
                    # Route statuses dynamically depending on target matching boundaries
                    status_route = "pending"
                    if final_score >= 95:
                        status_route = "approved" # Pipeline flag auto-apply loop criteria
                    elif final_score < 85:
                        status_route = "ignored"

                    supabase.table("job_matches").insert({
                        "job_id": job["id"],
                        "resume_id": active_resume["id"],
                        "semantic_score": final_score,
                        "aggregate_score": final_score, # We will enhance this with extra heuristics in subsequent phases
                        "status": status_route
                    }).execute()
                    
                    print(f"--> Match processing complete. Calculated Score: {final_score}% -> Route: {status_route}")

        except Exception as e:
            print(f"Error processing matching cycle pipeline run on job {job['id']}: {e}")
            continue

if __name__ == "__main__":
    pipeline_processor()