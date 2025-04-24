import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Instantiate ChatOpenAI ---
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo", # Good balance for creative generation
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.8, # Higher temperature for more varied job descriptions
    model_kwargs={"max_concurrency":5}
)

# --- Load Prompt ---
try:
    with open('./prompts/job_match_prompt.txt', 'r') as f:
        job_match_prompt = f.read()
except FileNotFoundError:
    print("ERROR: Job match prompt file not found.")
    job_match_prompt = "Generate a realistic mock job posting for role: {role}." # Fallback

# --- Create Agent ---
job_match_generator_agent = Agent(
    role='Mock Job Posting Creator',
    goal=job_match_prompt,
    backstory=(
        "You are a creative AI assistant skilled at generating realistic-looking "
        "mock job postings for the tech industry. Given a specific role, you craft "
        "a plausible job title, company name, location, salary range, description, "
        "responsibilities, and qualifications, mimicking the style of real job boards."
        "You can subtly tailor postings if provided with user skill context."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# --- Test Function (Optional) ---
if __name__ == '__main__':
    test_role = "DevOps Engineer"
    # Example with no user skills summary
    formatted_goal = job_match_generator_agent.goal.format(role=test_role, user_skills_summary="")
    print(f"Job Match Generator Agent for '{test_role}' initialized.")
    print("Formatted Goal Example (No User Skills):", formatted_goal)

    # Example with user skills summary
    test_summary = "Strong in AWS, Kubernetes, Terraform. Intermediate Python scripting."
    formatted_goal_with_skills = job_match_generator_agent.goal.format(role=test_role, user_skills_summary=test_summary)
    print("\nFormatted Goal Example (With User Skills):", formatted_goal_with_skills)