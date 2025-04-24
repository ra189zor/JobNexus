# app.py (Lowercase Standardization Version)

import streamlit as st
import plotly.graph_objects as go
import time

# Import backend function
from crew.crew_setup import run_tech_advisor_crew # Assumes crew_setup expects lowercase keys if it uses them

# Import helpers and formatters
from utils.streamlit_helper import inject_custom_css, render_skill_sliders
from utils.formatters import create_radar_chart, format_learning_path, format_job_card # Will update create_radar_chart
from utils.agent_helpers import fuzzy_skill_match

# --- Page Configuration ---
st.set_page_config(page_title="JobNexus - AI Career Advisor", layout="wide")

# --- Apply Custom CSS ---
inject_custom_css()

# --- App Header ---
st.markdown("<div class='app-header'>JobNexus <span>AI Career Advisor</span></div>", unsafe_allow_html=True)

# --- Session State Initialization ---
# Keys in user_skills will now be lowercase
if 'user_skills' not in st.session_state: st.session_state.user_skills = {}
if 'results' not in st.session_state: st.session_state.results = None
if 'raw_skills_input' not in st.session_state: st.session_state.raw_skills_input = ""
# entered_skills will store unique lowercase skills
if 'entered_skills' not in st.session_state: st.session_state.entered_skills = []

# --- Sidebar ---
with st.sidebar:
    st.header("Your Profile")

    # 1. Career Goal Input
    career_goal = st.text_input(
        "🎯 Enter your target career role:",
        placeholder="e.g. Frontend Developer, AI Engineer...",
        key="career_goal_input"
    )

    # 2. Skill Input using Text Area
    st.markdown("🔥 **Enter your current skills:**")
    raw_skills = st.text_area(
        "List your skills (one per line or comma-separated):",
        value=st.session_state.raw_skills_input,
        placeholder="e.g.\nPython\nJavaScript, React\nSQL\nCommunication",
        height=150,
        key="skills_text_area"
    )
    st.session_state.raw_skills_input = raw_skills

    # 3. Parse Text Input into Lowercase Skill List
    parsed_skills_lower = []
    if raw_skills:
        lines = raw_skills.strip().split('\n')
        for line in lines:
            skills_on_line = line.split(',')
            for skill in skills_on_line:
                cleaned_skill = skill.strip()
                if cleaned_skill:
                    # --- STANDARDIZE TO LOWERCASE ---
                    standardized_skill = cleaned_skill.lower()
                    # --------------------------------
                    parsed_skills_lower.append(standardized_skill)

    # Update the list of entered skills (unique and sorted lowercase skills)
    st.session_state.entered_skills = sorted(list(set(parsed_skills_lower)))

    # 4. Render Sliders Dynamically based on Parsed (Lowercase) Skills
    # Keys used for sliders and stored in user_skills will now be lowercase
    st.session_state.user_skills = render_skill_sliders(st.session_state.entered_skills, st.session_state.user_skills)

    # 5. Generate Button & Reset Button (remain the same)
    st.divider()
    generate_button = st.button("🚀 Generate Career Advice", use_container_width=True)
    if st.button("Reset Inputs", key="reset_button", use_container_width=True):
        st.session_state.user_skills = {}
        st.session_state.raw_skills_input = ""
        st.session_state.entered_skills = []
        st.session_state.results = None
        st.rerun()

# --- Main Area ---
if generate_button:
    # Validation checks (remain the same)
    if not career_goal: st.error("⚠️ Please enter your target career role.")
    elif not st.session_state.entered_skills: st.warning("⚠️ Please enter at least one skill.")
    elif not st.session_state.user_skills or not any(skill in st.session_state.user_skills for skill in st.session_state.entered_skills): st.warning("⚠️ Please rate the skills you entered.")
    else:
        # Proceed with analysis
        with st.spinner("🧠 Your AI advisor crew is analyzing your profile..."):
            try:
                # Prepare skills_to_send - keys are already lowercase
                skills_to_send = {skill: level for skill, level in st.session_state.user_skills.items() if skill in st.session_state.entered_skills}
                if not skills_to_send:
                     st.warning("No valid skill ratings found.")
                     st.session_state.results = None
                else:
                     print(f"Running crew for role '{career_goal}' with skills: {skills_to_send}")
                     results = run_tech_advisor_crew(career_goal, skills_to_send) # Send lowercase keys
                     st.session_state.results = results
                     print("Crew run finished.")
            except Exception as e:
                st.error(f"❌ An error occurred during analysis: {e}")
                import traceback; traceback.print_exc()
                st.session_state.results = {'error': str(e)}

# --- Display Results ---
if st.session_state.results:
    results = st.session_state.results
    if results.get('error') and 'validation' not in results: st.error(f"❌ Failed to generate advice: {results['error']}")
    elif isinstance(results, dict):
        tab_titles = ["📊 Skill Radar", "📚 Learning Path", "💼 Job Matches", "🧐 Agent Feedback"]
        try: tab1, tab2, tab3, tab4 = st.tabs(tab_titles)
        except Exception as e: st.error(f"Error creating tabs: {e}."); tab1 = tab2 = tab3 = tab4 = st

        # Tab 1: Skill Radar (Filtered using lowercase)
        with tab1:
            st.subheader("Your Skill Proficiency Overview")
            st.caption("Comparing your self-assessed skills against the typical baseline for the skills you entered.")
            baseline = results.get('baseline_thresholds', {}) # Assumes original case keys from AI
            gaps = results.get('skill_gaps', {}) # Assumes original case keys in 'missing'/'weak' lists/dicts
            # user_rated_skills keys are lowercase
            user_rated_skills_lower = {skill: level for skill, level in st.session_state.user_skills.items() if skill in st.session_state.entered_skills}
            # Fuzzy map user skills to baseline
            if baseline and user_rated_skills_lower:
                mapping = fuzzy_skill_match(list(user_rated_skills_lower.keys()), list(baseline.keys()))
                # Build mapped user skills dict for radar/gap
                mapped_user_skills = {}
                for baseline_skill, user_skill in mapping.items():
                    if user_skill is not None and user_skill in user_rated_skills_lower:
                        mapped_user_skills[baseline_skill] = user_rated_skills_lower[user_skill]
                user_rated_skills_lower = {k.lower(): v for k, v in mapped_user_skills.items()}

            if baseline and user_rated_skills_lower:
                # Create lowercase mapping for baseline keys for filtering comparison
                baseline_lower_map = {k.lower(): k for k in baseline.keys()}

                # Filter baseline to include only keys matching user's lowercase keys
                filtered_baseline_original_case = {}
                for user_skill_lower in user_rated_skills_lower.keys():
                    if user_skill_lower in baseline_lower_map:
                        original_baseline_key = baseline_lower_map[user_skill_lower]
                        filtered_baseline_original_case[original_baseline_key] = baseline[original_baseline_key]

                if filtered_baseline_original_case:
                    print(f"Plotting radar for: {list(filtered_baseline_original_case.keys())}")
                    # Pass lowercase user skills, original case baseline (filtered), original case gaps
                    radar_fig = create_radar_chart(user_rated_skills_lower, filtered_baseline_original_case, gaps)
                    if radar_fig:
                        st.plotly_chart(radar_fig, use_container_width=True)
                    else:
                        st.warning("Could not generate skill radar chart.")
                else:
                    st.info("ℹ️ None of the skills you entered match the baseline skills identified for this role by the AI.")
                    if baseline:
                        st.markdown("**Baseline skills identified by AI:**")
                        for skill in baseline.keys():
                            st.markdown(f"- {skill}")
            elif not user_rated_skills_lower: st.warning("Please enter and rate your skills.")
            else: st.warning("Baseline skill data not available.")

        # Tab 2: Learning Path
        with tab2:
            st.subheader("Personalized Learning Roadmap")
            # Summary of missing skills
            gaps = results.get('skill_gaps', {})
            missing = gaps.get('missing', [])
            weak_items = gaps.get('weak', [])
            gap_skills = missing + [item['skill'] for item in weak_items]
            if not gap_skills:
                st.success("✅ Great news! Your skills meet or exceed the baseline.")
            else:
                top_skills = gap_skills[:5]
                st.markdown(f"**You’re missing {len(gap_skills)} key skill(s). Here are free courses to get you job‑ready in {', '.join(top_skills)}.**")
                resources = results.get('learning_resources', {})
                if resources:
                    skills = list(resources.keys())
                    main_skills = skills[:3]
                    extra_skills = skills[3:]
                    for skill in main_skills:
                        with st.expander(f"▶ {skill}"):
                            resource_output = resources.get(skill)
                            # Filter out agent fallback/template outputs
                            if not resource_output or any(x in str(resource_output).lower() for x in ["provide only the structured list", "i now can give a great answer", "no specific free resources"]):
                                st.info("No actionable resources found for this skill.")
                                continue
                            if isinstance(resource_output, str):
                                st.markdown(resource_output)
                            else:
                                st.markdown(str(resource_output))
                    if extra_skills:
                        with st.expander("Show More Skills"):
                            for skill in extra_skills:
                                st.markdown(f"**{skill}**")
                                resource_output = resources.get(skill)
                                # Filter out agent fallback/template outputs
                                if not resource_output or any(x in str(resource_output).lower() for x in ["provide only the structured list", "i now can give a great answer", "no specific free resources"]):
                                    st.info("No actionable resources found for this skill.")
                                    continue
                                if isinstance(resource_output, str):
                                    st.markdown(resource_output)
                                else:
                                    st.markdown(str(resource_output))
                else:
                    st.info("No learning resources available.")

        # Tab 3: Job Matches
        with tab3:
            st.subheader("Example Job Opportunities")
            st.caption("AI-generated mock job postings relevant to your goal.")
            job_posting = results.get('job_posting')
            if job_posting and not str(job_posting).startswith("Error") and not any(x in str(job_posting).lower() for x in ["i now can give a great answer"]):
                if isinstance(job_posting, str):
                    st.markdown(job_posting)
                else:
                    st.markdown(str(job_posting))
            else:
                st.warning("No actionable mock job posting was generated.")

        # Tab 4: Agent Feedback (Uses original case keys from gaps)
        with tab4:
            st.subheader("Analysis Quality & Feedback")
            validation = results.get('validation', {})
            gaps = results.get('skill_gaps', {})

            # Display Validation section
            if validation:
                # ... (Validation metric, progress, status - same as before) ...
                confidence = validation.get('confidence_score', 0.0); issues = validation.get('issues', []); is_valid = validation.get('is_valid', False)
                st.metric("Analysis Consistency Score", f"{confidence*100:.0f}%"); st.progress(confidence)
                if not issues and confidence > 0.8: st.success("✅ Analysis complete. Results look consistent.")
                elif issues or confidence <= 0.5: st.error(f"❌ Analysis completed with {len(issues)} issue(s).")
                else: st.warning(f"⚠️ Analysis complete, confidence moderate or minor issues ({len(issues)} issue(s)).")
                if issues: st.subheader("Detected Issues / Areas for Caution:"); [st.markdown(f"- {issue}") for issue in issues]; st.markdown("---")

            # Display Skill Gap Summary section
            st.subheader("Skill Gap Summary:")
            if gaps and isinstance(gaps, dict) and not gaps.get('error'):
                weak_skills = gaps.get('weak', []) # List of dicts with original case 'skill' key
                missing_skills = gaps.get('missing', []) # List of original case skill names

                # Display Weak Skills
                if weak_skills:
                    st.markdown("**Skills Below Baseline:**")
                    for item in sorted(weak_skills, key=lambda x: x['skill']): st.markdown(f"- Improve **{item['skill']}** by **{item['gap']}** points (Your score: {item['user']}, Baseline: {item['baseline']}).")
                else:
                    if not missing_skills: st.success("✅ Great news! Your listed skills meet or exceed the baseline requirements!")
                    else: st.markdown("**Skills Below Baseline:** None")
                st.markdown("---")

                # Display Missing Skills
                if missing_skills:
                    st.markdown("**Missing Baseline Skills:**"); st.markdown(f"Consider acquiring these skills relevant to a {career_goal or 'target role'}:")
                    num_missing_cols = 3 if len(missing_skills) > 5 else 2 if len(missing_skills) > 2 else 1; cols = st.columns(num_missing_cols); col_index = 0
                    for skill in sorted(missing_skills):
                        with cols[col_index % num_missing_cols]: st.markdown(f"- **{skill}**"); col_index += 1
                else:
                    if not weak_skills: pass
                    else: st.markdown("**Missing Baseline Skills:** None")
            elif gaps and gaps.get('error'): st.warning(f"Could not display skill gap summary: {gaps['error']}")
            else:
                if not validation or not validation.get('is_valid', True): st.warning("Skill gap summary unavailable due to analysis issues.")
                else: st.info("No skill gap data available.")

            if not validation:
                if results.get('error'): st.error(f"Validation could not be performed: {results['error']}")
                else: st.warning("Validation feedback not available.")
    else: st.warning("Received invalid results format.")
else: st.info("👈 Enter your career goal and skills in the sidebar to get started!")

# --- Footer ---
st.markdown("---")
st.markdown("<div class='footer'>Built by AB with ❤️ using Streamlit, CrewAI, and OpenAI</div>", unsafe_allow_html=True)