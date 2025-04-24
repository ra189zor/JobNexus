# utils/streamlit_helpers.py
import streamlit as st

def inject_custom_css():
    """Injects custom CSS into the Streamlit app for styling (Dark Mode)."""
    # Dark Mode Theme based on Tailwind CSS dark colors
    css = """
    <style>
        /* --- Base & Font --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
        }

        /* --- Dark Mode Colors --- */
        :root {
            --primary-color: #818cf8; /* Indigo-400 (Lighter for dark bg) */
            --secondary-color: #2dd4bf; /* Teal-400 (Lighter for dark bg) */
            --text-color: #e5e7eb; /* Gray-200 (Light text) */
            --text-secondary-color: #9ca3af; /* Gray-400 (Slightly dimmer text) */
            --bg-color: #111827; /* Gray-900 (Dark background) */
            --bg-secondary-color: #1f2937; /* Gray-800 (Slightly lighter dark bg) */
            --border-color: #374151; /* Gray-700 (Darker borders) */
            --success-color: #34d399; /* Emerald-400 */
            --warning-color: #facc15; /* Yellow-400 */
            --error-color: #f87171; /* Red-400 */
            --info-bg-color: #1e293b; /* Slate-800 */
            --info-border-color: #3b82f6; /* Blue-500 */
            --info-text-color: #bfdbfe; /* Blue-200 */
        }

        /* --- Basic Styling --- */
        .stApp {
            background-color: var(--bg-color);
            color: var(--text-color);
        }
        /* Ensure text inputs have dark background and light text */
        .stTextInput input, .stTextArea textarea {
            background-color: var(--bg-secondary-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }
        /* Ensure selectbox/multiselect dropdowns are dark */
        div[data-baseweb="select"] > div {
             background-color: var(--bg-secondary-color) !important;
             border: 1px solid var(--border-color) !important;
        }
         div[data-baseweb="popover"] { /* Dropdown panel */
              background-color: var(--bg-secondary-color) !important;
              border: 1px solid var(--border-color) !important;
         }
         li[role="option"] {
             color: var(--text-color) !important;
         }
         li[role="option"]:hover {
              background-color: var(--primary-color) !important;
              color: var(--bg-color) !important; /* High contrast hover */
         }


        /* --- Header/Footer --- */
         .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            font-size: 0.85em;
            color: var(--text-secondary-color);
         }
         .app-header {
             font-size: 1.6em;
             font-weight: 700;
             margin-bottom: 25px;
             display: flex;
             align-items: center;
             gap: 10px;
             color: var(--text-color); /* Ensure header text is light */
         }
         .app-header span {
             font-size: 0.7em;
             color: var(--text-secondary-color);
             font-weight: 500;
         }

        /* --- Tabs Styling --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 48px;
            background-color: transparent;
            border-radius: 6px 6px 0 0;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            padding: 0 16px;
            color: var(--text-secondary-color);
            transition: border-color 0.3s ease, color 0.3s ease;
            font-weight: 500;
        }
        .stTabs [data-baseweb="tab"]:hover {
             /* background-color: var(--bg-secondary-color); Slightly lighter dark bg */
             border-bottom-color: var(--primary-color);
             color: var(--primary-color);
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: transparent;
            border-bottom: 2px solid var(--primary-color);
            box-shadow: none;
            color: var(--primary-color);
            font-weight: 600;
        }

        /* --- Buttons --- */
        .stButton>button {
            border-radius: 8px;
            background-color: var(--primary-color);
            color: var(--bg-color); /* Dark text on light button */
            border: none;
            padding: 10px 24px;
            font-weight: 600;
            transition: background-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #a5b4fc; /* Lighter Indigo for hover */
            color: var(--bg-color);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stButton>button:focus {
             box-shadow: 0 0 0 3px var(--bg-color), 0 0 0 5px var(--primary-color); /* Focus ring */
             background-color: #a5b4fc;
             color: var(--bg-color);
             outline: none;
        }
        /* Reset button styling */
         button[data-testid="stButton"] span:contains("Reset Inputs") { /* Attempt to target by text */
              /* This is fragile - better if Streamlit adds classes/ids */
              /* background-color: var(--bg-secondary-color) !important; */
              /* color: var(--text-color) !important; */
         }


        /* --- Sliders --- */
        div[data-baseweb="slider"] > div:nth-child(2) > div { /* Thumb */
            background-color: var(--primary-color) !important;
            border: 2px solid var(--bg-secondary-color); /* Contrast border */
        }
        /* REMOVED the rule for the track background */ /* <-- My note indicating it's gone */

        /* Slider value label */
         div[data-testid="stSlider"] span[data-baseweb="tag"] {
             color: var(--text-color);
             background-color: var(--bg-secondary-color);
             border: 1px solid var(--border-color);
         }


        /* --- Info Box Contrast --- */
        .stAlert[data-testid="stInfo"] {
            background-color: var(--info-bg-color);
            border: 1px solid var(--info-border-color);
            border-radius: 8px;
        }
        .stAlert[data-testid="stInfo"] p, .stAlert[data-testid="stInfo"] li {
             color: var(--info-text-color) !important; /* Light text for dark info box */
             font-size: 0.95em;
        }
        .stAlert[data-testid="stInfo"] svg {
            fill: var(--info-text-color);
        }
        /* Similar styling for success/warning/error */
         .stAlert[data-testid="stSuccess"] { background-color: #052e16; border-color: var(--success-color); color: var(--success-color); }
         .stAlert[data-testid="stWarning"] { background-color: #422006; border-color: var(--warning-color); color: var(--warning-color); }
         .stAlert[data-testid="stError"] { background-color: #450a0a; border-color: var(--error-color); color: var(--error-color); }
         .stAlert p, .stAlert li { color: inherit !important; } /* Inherit color from parent alert */
         .stAlert svg { fill: currentColor !important; }


        /* --- Cards (using Markdown) --- */
        .job-card, .learning-card {
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 16px;
            background-color: var(--bg-secondary-color); /* Slightly lighter dark bg */
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .job-card:hover, .learning-card:hover {
             box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); /* More noticeable shadow */
             border-color: var(--primary-color);
        }
        .job-card h4, .learning-card h4 {
            margin-top: 0;
            margin-bottom: 8px;
            color: var(--text-color);
        }
        .job-card p, .learning-card p {
            color: var(--text-secondary-color);
            margin-bottom: 4px;
            font-size: 0.9em;
        }
        .job-card details summary {
            cursor: pointer;
            font-weight: 500;
            color: var(--primary-color);
            font-size: 0.9em;
        }
        .job-card details p {
             color: var(--text-secondary-color); /* Lighter text for details */
             font-size: 0.85em;
             line-height: 1.5;
        }
        /* Learning card button */
        .learning-card a.stButton {
             background-color: var(--secondary-color) !important;
             color: var(--bg-color) !important; /* Dark text on light button */
        }
        .learning-card a.stButton:hover {
             background-color: #5eead4 !important; /* Lighter teal hover */
        }


         /* --- Timeline Style (Example) --- */
        .timeline-item {
            position: relative;
            padding-left: 35px;
            margin-bottom: 25px;
            border-left: 2px solid var(--border-color);
        }
        .timeline-item::before { /* Dot */
            content: '';
            position: absolute;
            left: -9px;
            top: 2px;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background-color: var(--primary-color);
            border: 3px solid var(--bg-secondary-color); /* Use card bg for pop */
        }
         .timeline-item h4 {
             margin-bottom: 10px;
             font-weight: 600;
             color: var(--text-color);
         }
        .timeline-badge { /* Adjust badge colors for dark mode if needed */
             display: inline-block;
             padding: 3px 10px;
             font-size: 0.75em;
             border-radius: 12px;
             margin-left: 8px;
             font-weight: 500;
             vertical-align: middle;
        }
        /* Example: Keep light badges or make them dark */
        .badge-beginner { background-color: #052e16; color: #6ee7b7; } /* Dark Green */
        .badge-intermediate { background-color: #422006; color: #fbbf24; } /* Dark Orange */
        .badge-advanced { background-color: #450a0a; color: #fca5a5; } /* Dark Red */

        /* --- Checkbox Styling --- */
        .stCheckbox {
             padding: 4px 0;
        }
        .stCheckbox label span { /* Checkbox text color */
             color: var(--text-color) !important;
        }

        /* --- Expander Styling --- */
        .stExpander > div:first-child {
            padding: 10px 0;
        }
        .stExpander summary { /* Expander title */
             color: var(--text-color);
             font-weight: 500;
        }
        .stExpander > div:first-child > details > summary svg {
            fill: var(--primary-color); /* Arrow color */
        }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Skill Slider Rendering ---
def render_skill_sliders(entered_skills_lower, current_levels_lower):
    """
    Renders sliders for entered skills (lowercase) and returns updated levels (lowercase keys).
    """
    updated_levels_for_selected_skills = {}
    if not entered_skills_lower:
        st.caption("Enter skills in the text area above to rate them.")
        return updated_levels_for_selected_skills

    st.markdown("**Rate your proficiency (0=Novice, 100=Expert):**")
    num_columns = 2 if len(entered_skills_lower) > 3 else 1
    cols = st.columns(num_columns)
    col_index = 0
    skills_to_render = sorted(list(entered_skills_lower)) # Already lowercase

    for skill_lower in skills_to_render:
        with cols[col_index % num_columns]:
            current_value_from_state = current_levels_lower.get(skill_lower, 0)
            # --- Display lowercase skill name as the label ---
            new_value = st.slider(
                 f"**{skill_lower}**", # Use the lowercase skill name
                 min_value=0,
                 max_value=100,
                 value=current_value_from_state,
                 step=5,
                 key=f"slider_{skill_lower}" # Key is lowercase
             )
            # Store with lowercase key
            updated_levels_for_selected_skills[skill_lower] = new_value
        col_index += 1
    return updated_levels_for_selected_skills