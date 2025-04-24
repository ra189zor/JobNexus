import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Instantiate ChatOpenAI ---
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo", # A capable and cost-effective model
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.6, # Balance creativity and relevance for finding resources
    model_kwargs={"max_concurrency":5}
)

# --- Load Prompt ---
try:
    with open('./prompts/course_prompt.txt', 'r') as f:
        course_prompt = f.read()
except FileNotFoundError:
    print("ERROR: Course prompt file not found.")
    course_prompt = "Find free online learning resources (Beginner, Intermediate, Advanced) for skill: {skill}." # Fallback

# --- Create Agent ---
learning_resource_agent = Agent(
    role='Free Learning Resource Finder',
    goal=course_prompt,
    backstory=(
        "You are an AI assistant dedicated to helping users learn and grow. "
        "Your specialty is finding high-quality, free, online learning resources "
        "(courses, tutorials, documentation) for specific technical skills. "
        "You categorize resources by difficulty (Beginner, Intermediate, Advanced) "
        "and provide direct URLs."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# --- Test Function (Optional) ---
if __name__ == '__main__':
    test_skill = "React Hooks"
    formatted_goal = learning_resource_agent.goal.format(skill=test_skill)
    print(f"Learning Resource Agent for '{test_skill}' initialized.")
    print("Formatted Goal Example:", formatted_goal)