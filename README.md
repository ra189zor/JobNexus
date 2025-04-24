# JobNexus: AI Career Advisor

## 🚀 Overview
**JobNexus** is an intelligent, user-friendly AI-powered career advisor and job matching platform for tech and digital professionals. It analyzes your skills, recommends actionable learning resources, and matches you to relevant job opportunities—all with a beautiful, interactive dashboard.

---

## ✨ Features
- **Skill Radar Visualization:**
  - Interactive radar chart comparing your self-assessed skills to industry baselines.
- **Personalized Learning Path:**
  - Actionable, curated learning resources for your skill gaps—never generic or empty!
- **Smart Job Matching:**
  - AI-powered job postings tailored to your skills and goals, with robust fallback logic.
- **Boss Agent Feedback:**
  - Consistency check and skill gap summary, so you know exactly where to improve.
- **Robust Skill Mapping:**
  - Fuzzy matching and synonym handling for all tech skills, so you’re never penalized for how you phrase things.
- **Modern UI:**
  - Clean, dark-themed Streamlit interface with collapsible sections and beautiful charts.

---

## 🛠️ Tech Stack
- **Frontend:** [Streamlit](https://streamlit.io/) (Python)
- **AI/Agents:** [CrewAI](https://github.com/joaomdmoura/crewAI), OpenAI (LLM), Custom Agents
- **Visualization:** [Plotly](https://plotly.com/python/)
- **Fuzzy Matching:** [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy), [python-Levenshtein](https://github.com/ztane/python-Levenshtein)

---

## 📦 Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/jobnexus.git
   cd jobnexus
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   - Create a `.env` file with your OpenAI API key:
     ```env
     OPENAI_API_KEY=your-openai-key
     ```
4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

---

## 🖥️ Usage
1. **Enter your target career role** (e.g., "Software Engineer").
2. **List your current skills** (comma-separated or one per line).
3. **Rate your proficiency** for each skill (0–100).
4. **Explore:**
   - **Skill Radar:** Visualize your strengths and gaps.
   - **Learning Path:** Get actionable resources for your gaps.
   - **Job Matches:** See tailored job postings.
   - **Agent Feedback:** Review consistency and missing skills.

---

## 💡 How It Works
- **Skill Mapping:**
  - Synonym dictionary + fuzzy string matching ensures your skills are always recognized—even with typos or alternate names.
- **Fallback Handling:**
  - If the AI can’t find a resource or job, you’ll always see a helpful fallback (never an empty or useless message).
- **Consistent Feedback:**
  - The Boss Agent validates all outputs for consistency and accuracy.

---

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

---

## 📄 License
This project is licensed under the MIT License. See [LICENSSE](./LICENSSE) for details.

---

## 🙏 Acknowledgements
- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/python/)
- [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy)
- [python-Levenshtein](https://github.com/ztane/python-Levenshtein)

---

> Made with ❤️ by AB
