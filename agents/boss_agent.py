import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo", # Use a capable model if LLM validation is needed
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.3, # Low temperature for analytical tasks
    model_kwargs={"max_concurrency":3} # Lower concurrency might be fine
)

boss_agent = Agent(
    role='Chief Validation Officer',
    goal=(
        "Oversee the outputs of other AI agents in the career advisor system. "
        "Validate outputs for completeness (no empty fields), basic consistency "
        "(e.g., skills match the role domain), and detect potential issues like "
        "hallucinated or nonsensical content. Provide a final confidence score or flag errors."
    ),
    backstory=(
        "You are the final checkpoint in the AI-powered Tech Career Advisor. "
        "With meticulous attention to detail, you review the work of other agents "
        "(like skill definitions, learning resources, job postings) before presenting "
        "it to the user. Your primary function is quality control, ensuring accuracy, "
        "relevance, and preventing errors or nonsensical outputs. You don't generate "
        "content yourself, but you critically evaluate it."
    ),
    verbose=True,
    allow_delegation=False, # Does not delegate, only reviews
    # llm=llm # Assign LLM if needed for advanced validation tasks later
)

# Placeholder for validation logic (to be implemented in Phase 2/3)
def validate_outputs(agent_outputs):
    """
    Placeholder function for the Boss Agent's validation logic.
    Checks for empty fields, basic consistency, etc.

    Args:
        agent_outputs (dict): A dictionary containing outputs from various agents.
                              e.g., {'role_skills': {...}, 'baseline': {...}, ...}

    Returns:
        tuple: (is_valid (bool), issues (list), confidence_score (float))
    """
    print("Boss Agent: Performing validation (Placeholder)...")
    issues = []
    confidence = 1.0 # Start with perfect confidence

    # --- Example Checks (Implement fully later) ---
    if not agent_outputs.get('role_skills'):
        issues.append("Role skills definition is missing.")
        confidence -= 0.3
    if not agent_outputs.get('baseline'):
        issues.append("Baseline proficiency levels are missing.")
        confidence -= 0.3
    if not agent_outputs.get('job_postings'):
        issues.append("Job postings are missing.")
        confidence -= 0.2
    # Add more sophisticated checks:
    # - Check if skills in baseline match skills defined for the role
    # - Check if course links look like valid URLs
    # - Potentially use LLM to check if job description sounds plausible

    is_valid = len(issues) == 0
    final_confidence = max(0.0, confidence) # Ensure confidence doesn't go below 0

    print(f"Boss Agent: Validation complete. Valid: {is_valid}, Issues: {issues}, Confidence: {final_confidence:.2f}")
    return is_valid, issues, final_confidence


# --- Test Function (Optional) ---
if __name__ == '__main__':
    print("Boss Agent initialized.")
    # Example test call to the placeholder validation function
    test_output_ok = {
        'role_skills': {'Core': ['Python'], 'Secondary': ['Git']},
        'baseline': {'Python': 80, 'Git': 60},
        'job_postings': [{'title': 'Python Dev', 'company': 'TestCo'}]
    }
    test_output_bad = {
        'role_skills': None, # Missing output
        'baseline': {'Python': 80},
        'job_postings': [] # Empty list
    }
    print("\n--- Testing Validation (OK case) ---")
    validate_outputs(test_output_ok)
    print("\n--- Testing Validation (Bad case) ---")
    validate_outputs(test_output_bad)