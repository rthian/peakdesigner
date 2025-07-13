import streamlit as st
import json
import os
from datetime import datetime

# Define roles, criteria, and ToMo questions (same as before)
ROLES = [
    "Associate Product Designer",
    "Product Designer",
    "Lead Product Designer",
    "Principal Product Designer",
    "Design Manager",
    "Senior Design Manager",
    "Head of Design"
]

CRITERIA = {
    # Copy all criteria dictionaries from the enhanced script (omitted for brevity)
    "Associate Product Designer": [
        ("Design Craft", "Basic skills in wireframing, mockups, and UI tools."),
        ("Research and User Understanding", "Assisting in user needs analysis and simple user journeys."),
        ("Collaboration and Communication", "Working effectively in teams and communicating ideas clearly."),
        ("Leadership and Mentoring", "Seeking feedback and learning from others."),
        ("Strategic Thinking and Impact", "Contributing to meeting business goals at a basic level.")
    ],
    "Product Designer": [
        ("Design Craft", "Proficient in prototyping, visual design, and design systems."),
        ("Research and User Understanding", "Conducting user tests and gathering feedback independently."),
        ("Collaboration and Communication", "Collaborating across teams on specs and features."),
        ("Leadership and Mentoring", "Driving consistency in processes."),
        ("Strategic Thinking and Impact", "Using data to shape work and evolve products based on feedback.")
    ],
    "Lead Product Designer": [
        ("Design Craft", "Advanced prototyping and guiding aesthetic direction."),
        ("Research and User Understanding", "Evaluating trends and complex UX patterns."),
        ("Collaboration and Communication", "Reviewing goals with PMs and providing accurate timelines."),
        ("Leadership and Mentoring", "Mentoring juniors and initiating product ideas."),
        ("Strategic Thinking and Impact", "Prioritizing work for efficiency and business impact.")
    ],
    "Principal Product Designer": [
        ("Design Craft", "Expert in complex components and user journeys."),
        ("Research and User Understanding", "Leading strategic user research and roadmap creation."),
        ("Collaboration and Communication", "Managing stakeholder expectations across projects."),
        ("Leadership and Mentoring", "Improving team work through critique and leading by example."),
        ("Strategic Thinking and Impact", "Demonstrating business thinking and high-impact delivery.")
    ],
    "Design Manager": [
        ("Design Craft", "Overseeing design quality and systems across teams."),
        ("Research and User Understanding", "Aligning research with product vision."),
        ("Collaboration and Communication", "Facilitating cross-functional collaboration."),
        ("Leadership and Mentoring", "Managing team development and career growth."),
        ("Strategic Thinking and Impact", "Budget management and ensuring project success.")
    ],
    "Senior Design Manager": [
        ("Design Craft", "Setting organization-wide design standards."),
        ("Research and User Understanding", "Integrating insights into long-term strategies."),
        ("Collaboration and Communication", "Building partnerships at senior levels."),
        ("Leadership and Mentoring", "Coaching managers and scaling teams."),
        ("Strategic Thinking and Impact", "Driving revenue-generating initiatives.")
    ],
    "Head of Design": [
        ("Design Craft", "Defining the overall design philosophy."),
        ("Research and User Understanding", "Championing user-centric culture."),
        ("Collaboration and Communication", "Influencing executive decisions."),
        ("Leadership and Mentoring", "Building and leading high-performing design org."),
        ("Strategic Thinking and Impact", "Aligning design with company vision and growth.")
    ]
}

TOMO_QUESTIONS = [
    ("I continue to work in my role because the work itself is enjoyable, interesting, and stimulating. (Play)", "play"),
    ("I continue to work in my role because I value the impact and outcomes of my work. (Purpose)", "purpose"),
    ("I continue to work in my role because it connects to my personal growth and future goals. (Potential)", "potential"),
    ("I continue to work in my role because I feel guilty, anxious, or ashamed if I don't. (Emotional Pressure)", "emotional"),
    ("I continue to work in my role to gain rewards or avoid financial punishment. (Economic Pressure)", "economic"),
    ("I continue to work in my role simply because it's routine and I don't think about why. (Inertia)", "inertia")
]

DATA_FILE = "assessments.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

st.title("Enhanced Peak Product Designer Scorecard")

tab1, tab2 = st.tabs(["New Assessment", "View Data"])

with tab1:
    name = st.text_input("Enter your name:")
    role = st.selectbox("Select your role:", ROLES)
    if role:
        criteria_list = CRITERIA[role]

        # Self Assessment
        st.subheader("Self Assessment")
        self_scores = {}
        for crit, desc in criteria_list:
            self_scores[crit] = st.slider(f"{crit}: {desc}", 1, 5, 3)

        # Manager Assessment
        has_manager = st.checkbox("Include Manager Assessment")
        manager_scores = None
        if has_manager:
            st.subheader("Manager Assessment")
            manager_scores = {}
            for crit, desc in criteria_list:
                manager_scores[crit] = st.slider(f"{crit}: {desc} (Manager)", 1, 5, 3)

        # Peer Assessments
        num_peers = st.number_input("Number of Peers", 0, 10, 0)
        peer_scores_list = []
        if num_peers > 0:
            for i in range(num_peers):
                st.subheader(f"Peer {i+1} Assessment")
                peer_scores = {}
                for crit, desc in criteria_list:
                    peer_scores[crit] = st.slider(f"{crit}: {desc} (Peer {i+1})", 1, 5, 3)
                peer_scores_list.append(peer_scores)

        # ToMo Survey
        st.subheader("Total Motivation (ToMo) Survey")
        tomo_scores = {}
        for question, key in TOMO_QUESTIONS:
            tomo_scores[key] = st.slider(question, 1, 7, 4)
        tomo = (tomo_scores["play"] + tomo_scores["purpose"] + tomo_scores["potential"]) - \
               (tomo_scores["emotional"] + tomo_scores["economic"] + tomo_scores["inertia"])

        if st.button("Submit Assessment"):
            def compute_averages(self_scores, manager_scores, peer_scores_list):
                criteria = list(self_scores.keys())
                averages = {}
                for crit in criteria:
                    scores = [self_scores[crit]]
                    if manager_scores:
                        scores.append(manager_scores[crit])
                    if peer_scores_list:
                        peer_avg = sum(p[crit] for p in peer_scores_list) / len(peer_scores_list)
                        scores.append(peer_avg)
                    averages[crit] = sum(scores) / len(scores)
                overall_avg = sum(averages.values()) / len(averages)
                return averages, overall_avg

            averages, overall_avg = compute_averages(self_scores, manager_scores, peer_scores_list)

            data = load_data()
            timestamp = datetime.now().isoformat()
            assessment = {
                "role": role,
                "self_scores": self_scores,
                "manager_scores": manager_scores,
                "peer_scores": peer_scores_list,
                "averages": averages,
                "overall_average": overall_avg,
                "tomo": tomo,
                "tomo_scores": tomo_scores,
                "timestamp": timestamp
            }
            if name not in data:
                data[name] = []
            data[name].append(assessment)
            save_data(data)
            st.success("Assessment saved!")
            st.write(f"Overall Average: {overall_avg:.2f}/5")
            st.write(f"ToMo Score: {tomo}")
            if tomo > 9:
                st.write("Adaptive Performer")
            elif tomo > 0:
                st.write("Balanced Performer")
            else:
                st.write("Tactical Performer")

with tab2:
    data = load_data()
    if data:
        selected_name = st.selectbox("Select user to view:", list(data.keys()))
        if selected_name:
            for i, assess in enumerate(data[selected_name]):
                with st.expander(f"Assessment {i+1} ({assess['timestamp']}) - Role: {assess['role']}"):
                    st.write(f"Overall Average: {assess['overall_average']:.2f}/5")
                    st.write(f"ToMo: {assess['tomo']}")
                    st.write("Averages per criterion:")
                    for crit, avg in assess['averages'].items():
                        st.write(f"- {crit}: {avg:.2f}")
    else:
        st.write("No assessments yet.")