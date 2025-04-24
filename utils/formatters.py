# utils/formatters.py
import plotly.graph_objects as go
import re

# --- COLOR_SCALE remains the same ---
COLOR_SCALE = { "strong": "#34d399", # Emerald-400 (adjusted for dark mode)
                "mid": "#facc15",      # Yellow-400 (adjusted for dark mode)
                "weak": "#f87171",     # Red-400 (adjusted for dark mode)
                "baseline": "#9ca3af", # Gray-400 (also used for lines/grid)
                "user": "#818cf8",      # Indigo-400
                "text": "#e5e7eb",      # Gray-200 (for labels if needed)
                "text-secondary": "#9ca3af" # Gray-400
               }

def create_radar_chart(user_skills_lower, baseline_skills_original, skill_gaps):
    """ Creates Plotly radar chart. Assumes lowercase user keys, original baseline keys. """
    if not baseline_skills_original: return None

    labels = list(baseline_skills_original.keys())
    baseline_values = list(baseline_skills_original.values())
    user_values = [user_skills_lower.get(label.lower(), 0) for label in labels]

    # Determine point colors based on gaps (using original case keys from gaps dict)
    point_colors = []
    weak_gap_map = {item['skill']: item['gap'] for item in skill_gaps.get('weak', [])}
    missing_set = set(skill_gaps.get('missing', []))

    for skill_original_case in labels:
        baseline_level = baseline_skills_original.get(skill_original_case, 0)
        if skill_original_case in missing_set: point_colors.append(COLOR_SCALE['weak'])
        elif skill_original_case in weak_gap_map:
             gap = weak_gap_map[skill_original_case]
             try:
                 gap_percentage = (gap / int(baseline_level)) * 100 if int(baseline_level) > 0 else 100
                 if gap_percentage > 40: point_colors.append(COLOR_SCALE['weak'])
                 else: point_colors.append(COLOR_SCALE['mid'])
             except (ValueError, TypeError): point_colors.append(COLOR_SCALE['mid'])
        else: point_colors.append(COLOR_SCALE['strong'])

    # --- Plotly Figure Creation ---
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=baseline_values, theta=labels, fill='toself', name='Baseline Proficiency',
        line=dict(color=COLOR_SCALE['baseline'], dash='dot'), fillcolor='rgba(156, 163, 175, 0.1)'
    ))
    fig.add_trace(go.Scatterpolar(
        r=user_values, theta=labels, fill='toself', name='Your Proficiency',
        line=dict(color=COLOR_SCALE['user']), marker=dict(color=point_colors, size=8), fillcolor='rgba(129, 140, 248, 0.2)'
    ))

    # --- FIX IS HERE ---
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 100], tickvals=[0, 25, 50, 75, 100], angle=90,
                tickfont=dict(size=10, color=COLOR_SCALE['text-secondary']), # Use text-secondary for ticks
                gridcolor=COLOR_SCALE['baseline'], # Use baseline color for grid
                linecolor=COLOR_SCALE['baseline']  # Use baseline color for axis lines
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color=COLOR_SCALE['text-secondary']), # Use text-secondary for labels
                direction="clockwise",
                linecolor=COLOR_SCALE['baseline'] # Use baseline color for axis lines
            )
        ),
        # --- END FIX ---
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color=COLOR_SCALE['text-secondary'])),
        margin=dict(l=60, r=60, t=40, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color=COLOR_SCALE['text']) # Use main text color
    )
    return fig

# --- format_learning_path function remains the same ---
def format_learning_path(learning_resources, skill_gaps):
    # ... (Keep existing logic) ...
    if not skill_gaps: return "<p>Skill gap data not available.</p>"
    html = "<div>" # ... rest of function ...
    skills_to_learn = []
    if skill_gaps and not skill_gaps.get('error'):
        skills_to_learn.extend(skill_gaps.get('missing', []))
        skills_to_learn.extend([item['skill'] for item in skill_gaps.get('weak', [])])
    # ... rest of function ...
    return html


# --- format_job_card function remains the same ---
def format_job_card(job_posting_text):
    # ... (Keep existing logic) ...
    return """ ... """ 