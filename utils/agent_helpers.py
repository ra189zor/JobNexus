# utils/agent_helpers.py
import json
import difflib
import re
from fuzzywuzzy import fuzz

def parse_json_output(llm_output: str):
    """
    Safely parses a JSON string potentially embedded in LLM output.
    Handles potential markdown code blocks ```json ... ```
    """
    try:
        # Check for markdown code block
        if llm_output.strip().startswith("```json"):
            # Extract content within the code block
            json_str = llm_output.strip()[7:-3].strip() # Remove ```json and ```
        elif llm_output.strip().startswith("```"):
             json_str = llm_output.strip()[3:-3].strip() # Remove ``` and ```
        else:
            json_str = llm_output.strip()

        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"Warning: Could not parse LLM output as JSON: {llm_output}")
        return None # Indicate parsing failure
    except Exception as e:
        print(f"Error parsing JSON output: {e}\nOutput was: {llm_output}")
        return None

def format_user_skills_summary(user_skills: dict) -> str:
    """ Formats user skills dictionary into a simple string summary. """
    if not user_skills:
        return "No specific skills provided."
    summary = "User has skills in: "
    summary += ", ".join([f"{skill} (Proficiency: {level}/100)" for skill, level in user_skills.items()])
    return summary

def normalize_text(text):
    # Lowercase, remove punctuation, and extra spaces
    return re.sub(r'[^a-z0-9 ]+', '', text.lower().strip())

def fuzzy_skill_match(user_skills, baseline_skills, threshold=80):
    """
    Maps user-entered skills to closest baseline skills using synonym mapping and fuzzywuzzy matching (Levenshtein ratio).
    Returns a dict: {baseline_skill: user_skill or None}
    """
    from fuzzywuzzy import fuzz
    skill_synonyms = {
        'java': 'Programming Languages',
        'c++': 'Programming Languages',
        'python': 'Programming Languages',
        'javascript': 'Programming Languages',
        'data structures': 'Algorithms and Data Structures',
        'algorithms': 'Algorithms and Data Structures',
        'problem solving': 'Problem-Solving',
        'oop': 'Object-Oriented Design',
        'object oriented programming': 'Object-Oriented Design',
        'object-oriented programming': 'Object-Oriented Design',
        'version control': 'Version Control',
        'git': 'Version Control',
        'sql': 'Database Management',
        'database': 'Database Management',
        'testing': 'Testing',
        'debugging': 'Debugging',
        'web': 'Web Development',
        'web dev': 'Web Development',
        'software dev': 'Software Development',
        'software development': 'Software Development',
    }
    mapping = {}
    baseline_norm = {normalize_text(b): b for b in baseline_skills}
    for user_skill in user_skills:
        skill_key = normalize_text(user_skill)
        # Try direct synonym mapping first
        if skill_key in skill_synonyms:
            target = normalize_text(skill_synonyms[skill_key])
            if target in baseline_norm:
                mapping[baseline_norm[target]] = user_skill
                continue
        # FuzzyWuzzy best match
        best_score = 0
        best_baseline = None
        for base_norm, base_orig in baseline_norm.items():
            score = fuzz.ratio(skill_key, base_norm)
            if score > best_score:
                best_score = score
                best_baseline = base_orig
        if best_score >= threshold:
            mapping[best_baseline] = user_skill
        else:
            mapping[user_skill] = None
    return mapping

def is_fallback_or_template_output(output):
    """Detects if agent output is fallback/template (not actionable). Add more patterns as needed."""
    if not output:
        return True
    output_str = str(output).lower()
    fallback_phrases = [
        'provide only the structured list',
        'i now can give a great answer',
        'no specific free resources',
        'no actionable mock job posting',
        'must be the great and the most complete',
        'your final answer must',
        'no actionable resources found',
        'no actionable mock job posting was generated',
        'no actionable',
        'no job posting',
        'no resources found',
        'no results',
        'no suitable',
        'no relevant',
        'no real',
        'template',
        'fallback',
        'cannot provide',
        'not available',
        'not found',
        'no data',
        'n/a',
        'error',
        'must be outcome described',
        'must be outcome described',
        'no job',
        'no posting',
        'no opportunities',
        'no learning resource',
        'no learning path',
    ]
    for phrase in fallback_phrases:
        if phrase in output_str:
            return True
    return False

def generic_learning_resource_fallback(skill):
    """Returns a generic fallback learning resource for a skill."""
    return f"No specific resources found for **{skill}**. Try searching on Coursera, edX, or YouTube for high-quality free courses."

def generic_job_posting_fallback(role):
    """Returns a generic fallback job posting for a role."""
    return f"No actionable job posting found for **{role}**. Try checking LinkedIn, Indeed, or Glassdoor for real-world postings."

# Add more helpers as needed, e.g., for retry logic with tenacity