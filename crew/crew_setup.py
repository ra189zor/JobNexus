# crew/crew_setup.py # Version 5
import os
import json
import re # Import regex for better parsing
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
# Import CrewOutput if it's a specific type, otherwise handle AttributeError
# from crewai.outputs import CrewOutput # Example, adjust if needed

# Import Agent definitions
from agents.role_definition_agent import role_definition_agent
from agents.baseline_threshold_agent import baseline_threshold_agent
from agents.learning_resource_agent import learning_resource_agent
from agents.job_match_generator_agent import job_match_generator_agent

# Import the computational analyzer and boss validation logic
from agents.skill_gap_analyzer import SkillGapAnalyzerAgent
from agents.boss_agent import validate_outputs

# Import Helper functions
# We'll refine parse_json_output right here for clarity
from utils.agent_helpers import format_user_skills_summary

load_dotenv()

# --- Refined JSON Parser ---
def parse_json_output_robust(llm_output):
    """
    Safely parses a JSON string potentially embedded in LLM output or CrewOutput object.
    Handles potential markdown code blocks and extracts JSON from text.
    """
    raw_text = None
    if isinstance(llm_output, str):
        raw_text = llm_output
    # Add checks for known CrewAI output objects if necessary
    # Example (adjust based on actual object structure):
    elif hasattr(llm_output, 'raw_output') and isinstance(llm_output.raw_output, str):
         raw_text = llm_output.raw_output
    elif hasattr(llm_output, 'result') and isinstance(llm_output.result, str):
         raw_text = llm_output.result
    elif hasattr(llm_output, '__str__'): # Fallback to string representation
         raw_text = str(llm_output)
    else:
        print(f"Warning: Unexpected output type for JSON parsing: {type(llm_output)}")
        return None

    if not raw_text:
        return None

    # Use regex to find JSON block ```json ... ``` or just { ... }
    # Regex to find JSON object starting with { and ending with }
    # It handles nested braces. It's not perfect but often works for simple cases.
    match = re.search(r'\{[\s\S]*\}', raw_text)

    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse extracted JSON string: {e}\nString was: {json_str}")
            return None # Indicate parsing failure
    else:
        # Fallback if no clear JSON object is found (maybe the whole string is JSON?)
        try:
             # Try parsing the whole cleaned text
             cleaned_text = raw_text.strip()
             if cleaned_text.startswith("```json"):
                  cleaned_text = cleaned_text[7:-3].strip()
             elif cleaned_text.startswith("```"):
                  cleaned_text = cleaned_text[3:-3].strip()
             return json.loads(cleaned_text)
        except json.JSONDecodeError:
             print(f"Warning: Could not parse raw LLM output as JSON. Output:\n{raw_text}")
             return None


# --- Initialize Computational Agents/Validators ---
skill_gap_analyzer = SkillGapAnalyzerAgent()

# --- In-Memory Cache ---
session_cache = {}

# --- Define Tasks (Ensure baseline_threshold_agent has static goal) ---
# Task 1: Define Skills for the Role
task_define_role_skills = Task(
    description="Analyze the tech role: **{role}**. Identify and list its core technical skills, secondary technical skills/tools, and key soft skills. Use the prompt instructions precisely. Output should be structured text.",
    expected_output="A clearly structured text output listing Core Technical Skills, Secondary Technical Skills/Tools, and Soft Skills for the role: {role}.",
    agent=role_definition_agent,
)

# Task 2: Define Baseline Proficiency Levels
task_define_baseline_thresholds = Task(
    description="CONTEXT PROVIDED: The output from the previous 'Role Skill Definer' task.\nYOUR TASK: Based *only* on the skill definition text provided in the context, estimate the standard baseline proficiency level (0-100) for each skill relevant to the role: **{role}**. Follow the detailed instructions in your internal prompt (baseline_prompt.txt) to parse the context and generate the JSON output.",
    expected_output="A single JSON object mapping each relevant skill identified from the context to its estimated baseline proficiency level (e.g., {{\"Skill A\": 75, \"Skill B\": 80, ...}}). Output ONLY the JSON.",
    agent=baseline_threshold_agent,
    context=[task_define_role_skills]
)

# Task 3: Generate Mock Job Postings (Template Task)
task_template_generate_job_match = Task(
    description="Generate a realistic mock job posting for the tech role: **{role}**. Incorporate sections like Job Title, Company, Location, Salary Range, Description, Responsibilities, and Qualifications. Use the prompt instructions precisely. If provided, consider the user's skill summary: {user_skills_summary}",
    expected_output="A well-formatted block of text representing a realistic job posting.",
    agent=job_match_generator_agent
)

# Task 4: Find Learning Resources (Template Task)
task_template_find_learning_resources = Task(
    description="Find high-quality, free, online learning resources (courses, tutorials, documentation) for the specific technical skill: **{skill}**. Categorize them by difficulty (Beginner, Intermediate, Advanced) and provide direct URLs. Use the prompt instructions.",
    expected_output="A structured text output listing free learning resources with URLs.",
    agent=learning_resource_agent
)


# --- Crew Definition ---
initial_crew = Crew(
    agents=[role_definition_agent, baseline_threshold_agent],
    tasks=[task_define_role_skills, task_define_baseline_thresholds],
    process=Process.sequential,
    verbose=True
)

# --- Main Orchestration Function ---
def run_tech_advisor_crew(role: str, user_skills: dict):
    """ Orchestrates the CrewAI agents to generate career advice. """
    print(f"\n--- Running Tech Advisor Crew for Role: {role} ---")
    results = {'role_skills_definition': "Processing...", 'baseline_thresholds': {}, 'skill_gaps': None, 'learning_resources': {}, 'job_posting': None, 'validation': {}}
    validation_issues = []
    final_confidence = 1.0

    cache_key_role_def = f"role_def_{role}" # We won't retrieve role_def directly, but keep key for potential future use
    cache_key_baseline = f"baseline_{role}"

    try:
        # --- Step 1 & 2: Get Role Skills and Baselines ---
        baseline_output_json = None

        if cache_key_baseline in session_cache:
             print(f"CACHE HIT: Using cached baseline thresholds for '{role}'")
             baseline_output_json = session_cache[cache_key_baseline]
             # Can't reliably get role_def from cache if not stored separately
             results['role_skills_definition'] = "Retrieved from cache (content not stored separately)."
        else:
            print(f"CACHE MISS: Running initial crew (Role Def -> Baseline) for '{role}'...")
            crew_inputs = {'role': role}
            crew_result_object = initial_crew.kickoff(inputs=crew_inputs) # Get the result object

            if not crew_result_object:
                 print(f"WARNING: Initial crew returned an empty or None result for '{role}'.")
                 validation_issues.append(f"Initial crew (Role Def->Baseline) returned no output for role '{role}'.")
                 final_confidence -= 0.5
                 baseline_output_json = {} # Assume failure
                 results['role_skills_definition'] = "Initial crew failed to produce output."
            else:
                # Try parsing baseline from the result object using the robust parser
                print("Parsing baseline thresholds from crew output...")
                baseline_output_json = parse_json_output_robust(crew_result_object) # Use robust parser

                if not baseline_output_json:
                    print(f"WARNING: Failed to parse baseline JSON from crew output for '{role}'.")
                    validation_issues.append(f"Failed to parse baseline proficiency JSON for role '{role}'.")
                    final_confidence -= 0.4
                    baseline_output_json = {} # Use empty dict
                    # Store raw output for debugging if possible
                    raw_output_for_debug = str(crew_result_object) if crew_result_object else "N/A"
                    results['role_skills_definition'] = f"Baseline parsing failed. Raw crew output: {raw_output_for_debug[:200]}..." # Store snippet
                else:
                    print(f"Caching baseline thresholds for role '{role}'")
                    session_cache[cache_key_baseline] = baseline_output_json
                    # We don't have the intermediate role def easily, set placeholder
                    results['role_skills_definition'] = "Role definition processed (output used for baseline)."

        # --- Assign results ---
        results['baseline_thresholds'] = baseline_output_json

        # --- Step 3: Analyze Skill Gaps ---
        print("Analyzing skill gaps...")
        skill_gaps = None # <<<< INITIALIZE skill_gaps before the if/else
        if results.get('baseline_thresholds'): # Check if baseline dict is not empty
            try:
                skill_gaps = skill_gap_analyzer.analyze_gaps(user_skills, results['baseline_thresholds'])
                results['skill_gaps'] = skill_gaps # Store the result
            except Exception as gap_e:
                 print(f"ERROR during skill gap analysis: {gap_e}")
                 results['skill_gaps'] = {'error': f'Error during gap analysis: {gap_e}'}
                 validation_issues.append("Skill gap analysis failed internally.")
                 final_confidence -= 0.1
        else:
            # Baseline was empty or missing
            results['skill_gaps'] = {'error': 'Baseline thresholds not available for gap analysis.'}
            print("Skipping skill gap analysis as baseline is missing or invalid.")
            # Validation issue/confidence penalty already applied during baseline step


        # --- Step 4: Find Learning Resources ---
        print("Finding learning resources...")
        learning_resources = {}
        skills_to_learn = []
        # Use results['skill_gaps'] which is guaranteed to exist now
        current_gaps = results.get('skill_gaps')
        if current_gaps and not current_gaps.get('error'):
             skills_to_learn.extend(current_gaps.get('missing', []))
             skills_to_learn.extend([item['skill'] for item in current_gaps.get('weak', [])])

        # (Rest of Step 4 remains the same, using task.execute() with fallback)
        if skills_to_learn:
            from utils.agent_helpers import is_fallback_or_template_output, generic_learning_resource_fallback
            unique_skills_to_learn = sorted(list(set(skills_to_learn)))
            print(f"Skills needing resources: {unique_skills_to_learn}")
            MAX_SKILLS_FOR_RESOURCES = 5
            skills_to_fetch = unique_skills_to_learn[:MAX_SKILLS_FOR_RESOURCES]

            for skill in skills_to_fetch:
                try:
                    temp_task_desc = task_template_find_learning_resources.description.format(skill=skill.strip())
                    temp_task = Task(description=temp_task_desc, expected_output=task_template_find_learning_resources.expected_output, agent=learning_resource_agent)
                    resource_output = temp_task.execute() # Try task.execute()
                except AttributeError:
                    try:
                        print(f"  >> Fallback: Using agent.execute_task() for learning resource: {skill}")
                        resource_output = learning_resource_agent.execute_task(task=temp_task)
                    except Exception as fallback_e:
                        print(f"  - Error during agent.execute_task() fallback for {skill}: {fallback_e}")
                        resource_output = f"Error retrieving resources (fallback failed): {fallback_e}"
                        validation_issues.append(f"Failed to get learning resources for '{skill}' (fallback).")
                        final_confidence -= 0.05
                except Exception as e:
                    print(f"  - Error finding resources for {skill}: {e}")
                    resource_output = f"Error retrieving resources: {e}"
                    validation_issues.append(f"Failed to get learning resources for '{skill}'.")
                    final_confidence -= 0.05
                # Robust fallback/template detection
                if is_fallback_or_template_output(resource_output):
                    resource_output = generic_learning_resource_fallback(skill)
                learning_resources[skill] = resource_output

            if len(unique_skills_to_learn) > MAX_SKILLS_FOR_RESOURCES:
                learning_resources["INFO"] = f"Resource search limited to top {MAX_SKILLS_FOR_RESOURCES} skills."
        else:
            print("No actionable skill gaps identified requiring learning resources.")
        results['learning_resources'] = learning_resources

        # --- Step 5: Generate Mock Job Posting ---
        # (Remains the same, using task.execute() with fallback)
        print("Generating mock job posting...")
        try:
            from utils.agent_helpers import is_fallback_or_template_output, generic_job_posting_fallback
            user_summary = format_user_skills_summary(user_skills)
            temp_task_desc = task_template_generate_job_match.description.format(role=role, user_skills_summary=user_summary)
            temp_task = Task(description=temp_task_desc, expected_output=task_template_generate_job_match.expected_output, agent=job_match_generator_agent)
            job_output = temp_task.execute() # Try task.execute()
        except AttributeError:
            try:
                print("  >> Fallback: Using agent.execute_task() for job match.")
                job_output = job_match_generator_agent.execute_task(task=temp_task)
            except Exception as fallback_e:
                print(f"  - Error during agent.execute_task() fallback for job match: {fallback_e}")
                job_output = f"Error generating job posting (fallback failed): {fallback_e}"
                validation_issues.append("Failed to generate mock job posting (fallback).")
                final_confidence -= 0.15
        except Exception as e:
            print(f"Error generating job posting: {e}")
            job_output = f"Error generating job posting: {e}"
            validation_issues.append("Failed to generate mock job posting.")
            final_confidence -= 0.15
        # Robust fallback/template detection
        if is_fallback_or_template_output(job_output):
            job_output = generic_job_posting_fallback(role)
        results['job_posting'] = job_output


        # --- Step 6: Boss Agent Validation ---
        print("Performing final validation...")
        # (Remains the same)
        validation_input = { # Prepare dict for validation function
            'role_skills': results.get('role_skills_definition'), # Might be placeholder text
            'baseline': results.get('baseline_thresholds'),
            'gaps': results.get('skill_gaps'),
            'resources': results.get('learning_resources'),
            'job_postings': [results.get('job_posting')] if results.get('job_posting') and not results.get('job_posting').startswith("Error") else []
        }
        # Ensure validate_outputs handles potential None values gracefully
        is_valid, boss_issues, boss_confidence = validate_outputs(validation_input)

        all_issues = sorted(list(set(validation_issues + boss_issues)))
        final_confidence = min(final_confidence, boss_confidence)
        final_confidence = max(0.0, final_confidence)

        results['validation'] = {
            'is_valid': is_valid and not validation_issues, # Consider programmatic issues too
            'issues': all_issues,
            'confidence_score': final_confidence
        }
        print(f"Final Validation: Valid={results['validation']['is_valid']}, Issues Found={len(results['validation']['issues'])}, Confidence={results['validation']['confidence_score']:.2f}")


    except Exception as e:
        print(f"ERROR: An exception occurred during crew execution: {e}")
        import traceback
        traceback.print_exc()
        if 'results' not in locals(): results = {}
        results['error'] = f"An unexpected error occurred during orchestration: {e}"
        results['validation'] = {
             'is_valid': False,
             'issues': validation_issues + [f"Orchestration Error: {e}"],
             'confidence_score': 0.0
         }
        for key in ['role_skills_definition', 'baseline_thresholds', 'skill_gaps', 'learning_resources', 'job_posting']:
             if key not in results: results[key] = None
        return results

    print("--- Tech Advisor Crew Run Finished ---")
    return results


# --- Test Execution Block ---
if __name__ == '__main__':
    # test_role = "UI/UX Designer"
    # test_user_skills = { "Figma": 70, "User Research": 50, "Communication": 85 }
    test_role = "Data Scientist"
    test_user_skills = {"Python": 60, "SQL": 75, "Communication": 85}


    session_cache.pop(f"role_def_{test_role}", None)
    session_cache.pop(f"baseline_{test_role}", None)

    final_results = run_tech_advisor_crew(test_role, test_user_skills)

    print("\n\n--- FINAL CREW RESULTS ---")
    print(json.dumps(final_results, indent=2))