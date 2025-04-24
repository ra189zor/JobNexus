# agents/baseline_threshold_agent.py
import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Instantiate ChatOpenAI ---
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.5,
    model_kwargs={"max_concurrency": 5} # Corrected placement
)

# --- Load Prompt (Still needed for the LLM call later) ---
try:
    with open('./prompts/baseline_prompt.txt', 'r') as f:
        baseline_prompt_template = f.read()
except FileNotFoundError:
    print("ERROR: Baseline prompt file not found.")
    baseline_prompt_template = "Estimate baseline proficiency (0-100) for skills based on role {role} and provided context {context}. Output JSON." # Fallback

# --- Create Agent ---
baseline_threshold_agent = Agent(
    role='Skill Proficiency Baseline Estimator',
    # --- THIS IS THE KEY CHANGE ---
    # Goal is now a static description, not the prompt template itself.
    goal='Estimate standard baseline proficiency levels (0-100) for skills relevant to a specific tech role, based on a provided skill definition text.',
    # -----------------------------
    backstory=(
        "You are an analytical AI assistant with deep knowledge of tech skill requirements. "
        "Given a tech role and a detailed text defining its required skills (provided as context), "
        "your function is to parse that text, identify the skills, estimate the standard baseline "
        "proficiency level (0-100) for each skill for someone competent in that role, "
        "and provide the output as a structured JSON object."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
    # The agent will use the full prompt template internally when executing the task
)

# --- Test Function (Optional) ---
if __name__ == '__main__':
    test_role = "Frontend Developer"
    # Note: The goal is now static, no formatting needed here
    print(f"Baseline Threshold Agent for '{test_role}' initialized.")
    print("Static Goal:", baseline_threshold_agent.goal)
    # The prompt template is still loaded and available if needed for testing internals
    # print("Prompt Template Snippet:", baseline_prompt_template[:100])