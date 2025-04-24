import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Instantiate ChatOpenAI with Concurrency Limit ---
# You can customize the model_name and temperature
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo", # A capable and cost-effective model
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
    model_kwargs={"max_concurrency":5}
)

# --- Load Prompt ---
try:
    with open('./prompts/role_definition_prompt.txt', 'r') as f:
        role_definition_prompt = f.read()
except FileNotFoundError:
    print("ERROR: Role definition prompt file not found.")
    role_definition_prompt = "Define core, secondary, and soft skills for tech role: {role}. Structure the output." # Fallback prompt

# --- Create Agent ---
role_definition_agent = Agent(
    role='Tech Role Skill Definer',
    goal=role_definition_prompt, # Use the loaded prompt directly as the goal template
    backstory=(
        "You are an expert AI assistant specialized in understanding the tech industry "
        "and job requirements. Your task is to meticulously analyze a given tech role "
        "and identify the essential core technical skills, important secondary skills/tools, "
        "and relevant soft skills required for success in that role. You provide clear, structured output."
    ),
    verbose=True, # Enable verbose output for debugging
    allow_delegation=False, # This agent works independently
    llm=llm # Assign the specific LLM instance
)

# --- Test Function (Optional) ---
if __name__ == '__main__':
    # Example usage for testing this agent directly
    test_role = "Data Scientist"
    task_description = role_definition_prompt.format(role=test_role) # Format the prompt for a test task

    # Create a Task (not strictly needed for agent definition, but shows usage)
    from crewai import Task
    test_task = Task(
        description=f"Define the skills for the role: {test_role}",
        expected_output="A structured list of core, secondary, and soft skills.",
        agent=role_definition_agent
        # If using Crew framework, context/inputs would be passed differently
    )

    # To execute directly (requires Crew setup or manual execution)
    # result = role_definition_agent.execute_task(test_task) # Simplified example
    # print(f"\n--- Test Result for {test_role} ---")
    # print(result)
    print(f"Role Definition Agent for '{test_role}' initialized.")
    print("Goal:", role_definition_agent.goal.format(role=test_role)) # Show the formatted goal