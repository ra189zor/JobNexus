# agents/skill_gap_analyzer.py

class SkillGapAnalyzerAgent:
    """
    Analyzes the gap between user's self-assessed skills and the
    baseline proficiency levels defined for a target role. CASE-INSENSITIVE matching.
    """
    def __init__(self):
        print("Skill Gap Analyzer Agent initialized (Computational).")

    def analyze_gaps(self, user_skills_lower, baseline_skills_original):
        """
        Compares user skills proficiency against baseline proficiency (Case-Insensitive Keys).
        Uses robust fuzzy_skill_match to ensure a baseline is only missing if no mapped user skill covers it.

        Args:
            user_skills_lower (dict): {skill_name_lower: proficiency} - From user input.
            baseline_skills_original (dict): {Skill_Name_Original_Case: proficiency} - From AI.

        Returns:
            dict: {'missing': [Skill_Name_Original_Case],
                   'weak': [{'skill': Skill_Name_Original_Case, 'user': N, 'baseline': N, 'gap': N}]}
                   Returns None if inputs are invalid. Returns empty lists if no gaps.
        """
        if not isinstance(user_skills_lower, dict) or not isinstance(baseline_skills_original, dict):
            print("ERROR: Invalid input format for skill gap analysis.")
            return {'missing': [], 'weak': [], 'error': 'Invalid input format'}

        # Handle empty baseline case
        if not baseline_skills_original:
             print("WARNING: Baseline skills dictionary is empty. Cannot perform gap analysis.")
             return {'missing': [], 'weak': [], 'info': 'Baseline skills unavailable'}

        # --- Robust mapping: Use fuzzy_skill_match to map user skills to baseline ---
        from utils.agent_helpers import fuzzy_skill_match, normalize_text
        user_skill_names = list(user_skills_lower.keys())
        baseline_names = list(baseline_skills_original.keys())
        mapping = fuzzy_skill_match(user_skill_names, baseline_names, threshold=80)
        # mapping: {baseline_skill: user_skill or None}

        # Build reverse: for each baseline, did any user skill map to it?
        covered_baselines = set()
        user_skill_to_level = {normalize_text(k): v for k, v in user_skills_lower.items()}
        for baseline_skill, user_skill in mapping.items():
            if user_skill is not None:
                covered_baselines.add(normalize_text(baseline_skill))

        # Lowercase mapping for baseline
        baseline_lower_map = {normalize_text(k): k for k in baseline_skills_original.keys()}
        gaps = {'missing': [], 'weak': []}

        # Find missing skills (those not covered by any mapped user skill)
        for baseline_norm, original_baseline in baseline_lower_map.items():
            if baseline_norm not in covered_baselines:
                gaps['missing'].append(original_baseline)

        # Find weak skills (present in both, check levels)
        for baseline_norm, original_baseline in baseline_lower_map.items():
            if baseline_norm in covered_baselines:
                # Find which user skill mapped to this baseline
                mapped_user_skill = mapping.get(original_baseline)
                if mapped_user_skill is not None:
                    user_level = user_skills_lower.get(mapped_user_skill.lower(), user_skills_lower.get(normalize_text(mapped_user_skill), 0))
                    baseline_level = baseline_skills_original[original_baseline]
                    try:
                        user_level_num = int(user_level)
                        baseline_level_num = int(baseline_level)
                        if user_level_num < baseline_level_num:
                            gaps['weak'].append({
                                'skill': original_baseline, # Use original case for display
                                'user': user_level_num,
                                'baseline': baseline_level_num,
                                'gap': baseline_level_num - user_level_num
                            })
                    except (ValueError, TypeError) as e:
                         print(f"WARNING: Could not compare levels for skill '{original_baseline}'. User: {user_level}, Baseline: {baseline_level}. Error: {e}")
                         # Optionally add this as an issue?

        print(f"Skill Gap Analysis complete. Missing: {len(gaps['missing'])}, Weak: {len(gaps['weak'])}")
        return gaps