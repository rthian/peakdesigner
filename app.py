import streamlit as st
import json
import os
from datetime import datetime
import hashlib

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

SELF_TOMO_QUESTIONS = [
    ("I continue to work in my role because the work itself is enjoyable, interesting, and stimulating. (Play)", "play"),
    ("I continue to work in my role because I value the impact and outcomes of my work. (Purpose)", "purpose"),
    ("I continue to work in my role because it connects to my personal growth and future goals. (Potential)", "potential"),
    ("I continue to work in my role because I feel guilty, anxious, or ashamed if I don't. (Emotional Pressure)", "emotional"),
    ("I continue to work in my role to gain rewards or avoid financial punishment. (Economic Pressure)", "economic"),
    ("I continue to work in my role simply because it's routine and I don't think about why. (Inertia)", "inertia")
]

OTHER_TOMO_QUESTIONS = [
    ("The person continues to work in their role because the work itself is enjoyable, interesting, and stimulating to them. (Play)", "play"),
    ("The person continues to work in their role because they value the impact and outcomes of their work. (Purpose)", "purpose"),
    ("The person continues to work in their role because it connects to their personal growth and future goals. (Potential)", "potential"),
    ("The person continues to work in their role because they feel guilty, anxious, or ashamed if they don't. (Emotional Pressure)", "emotional"),
    ("The person continues to work in their role to gain rewards or avoid financial punishment. (Economic Pressure)", "economic"),
    ("The person continues to work in their role simply because it's routine and they don't think about why. (Inertia)", "inertia")
]

DATA_FILE = "assessments.json"
USERS_FILE = "users.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return {}

def save_data(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def is_manager(title):
    return "Manager" in title or "Head" in title

def get_masked_id(name):
    m = hashlib.md5()
    m.update(name.encode('utf-8'))
    return m.hexdigest()[:6].upper()

# Login function
def login():
    st.title("Login")
    name = st.text_input("Name")
    title = st.selectbox("Title", ROLES)
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_data(USERS_FILE)
        default_pass = name.replace(" ", "")
        if name in users and users[name]["password"] == password and users[name]["title"] == title:
            st.session_state["logged_in"] = True
            st.session_state["user_name"] = name
            st.session_state["user_title"] = title
            st.success("Logged in successfully!")
        else:
            # Register if not exists
            users[name] = {"title": title, "password": default_pass}
            save_data(users, USERS_FILE)
            st.session_state["logged_in"] = True
            st.session_state["user_name"] = name
            st.session_state["user_title"] = title
            st.success("Registered and logged in! Your password is " + default_pass)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    st.title("Enhanced Peak Product Designer Scorecard")
    user_name = st.session_state["user_name"]
    user_title = st.session_state["user_title"]
    st.write(f"Welcome, {user_name} ({user_title})")

    tabs = ["Self Assessment", "Manager/Peer Assessment", "View Data"]
    if is_manager(user_title):
        tabs.append("Manage Assessments")
    tab_objects = st.tabs(tabs)

    tab1 = tab_objects[0]
    tab2 = tab_objects[1]
    tab3 = tab_objects[2]
    if is_manager(user_title):
        tab4 = tab_objects[3]

    with tab1:
        st.subheader("Self Assessment")
        criteria_list = CRITERIA[user_title]

        data = load_data(DATA_FILE)
        user_assessments = data.get(user_name, [])
        approved_self = [a for a in user_assessments if a['assessor'] == "Self" and a.get('status', 'Approved') == 'Approved']

        if len(approved_self) >= 1:
            st.warning("You already have an approved self-assessment. This submission will require manager approval to replace the existing one.")
            pending = True
        else:
            pending = False

        self_scores = {}
        for crit, desc in criteria_list:
            self_scores[crit] = st.slider(f"{crit}: {desc}", 1, 5, 3, key=f"self_{crit.replace(' ', '_')}")

        st.subheader("Total Motivation (ToMo) Survey")
        tomo_scores = {}
        for question, key in SELF_TOMO_QUESTIONS:
            tomo_scores[key] = st.slider(question, 1, 7, 4, key=f"tomo_{key}")
        tomo = (tomo_scores["play"] + tomo_scores["purpose"] + tomo_scores["potential"]) - \
               (tomo_scores["emotional"] + tomo_scores["economic"] + tomo_scores["inertia"])

        if st.button("Submit Self Assessment"):
            timestamp = datetime.now().isoformat()
            assessment = {
                "assessor": "Self",
                "role": user_title,
                "scores": self_scores,
                "tomo": tomo,
                "tomo_scores": tomo_scores,
                "timestamp": timestamp,
                "status": "Pending Approval" if pending else "Approved"
            }
            if user_name not in data:
                data[user_name] = []
            data[user_name].append(assessment)
            save_data(data, DATA_FILE)
            st.success("Self Assessment submitted!" + (" (Pending Approval)" if pending else ""))

    with tab2:
        st.subheader("Manager/Peer Assessment")
        assessor_role = st.selectbox("Your Role in this Assessment", ["Manager", "Peer"])
        users = load_data(USERS_FILE)
        assessee_name = st.selectbox("Select User to Assess", list(users.keys()))
        if assessee_name:
            assessee_title = users[assessee_name]["title"]
            criteria_list = CRITERIA[assessee_title]

            scores = {}
            for crit, desc in criteria_list:
                scores[crit] = st.slider(f"{crit}: {desc}", 1, 5, 3, key=f"{assessor_role.lower()}_{crit.replace(' ', '_')}_{assessee_name.replace(' ', '_')}")

            st.subheader("Total Motivation (ToMo) Survey (Observer Perspective)")
            tomo_scores = {}
            for question, key in OTHER_TOMO_QUESTIONS:
                tomo_scores[key] = st.slider(question, 1, 7, 4, key=f"other_tomo_{key}_{assessee_name.replace(' ', '_')}")
            tomo = (tomo_scores["play"] + tomo_scores["purpose"] + tomo_scores["potential"]) - \
                   (tomo_scores["emotional"] + tomo_scores["economic"] + tomo_scores["inertia"])

            if st.button("Submit Assessment"):
                data = load_data(DATA_FILE)
                timestamp = datetime.now().isoformat()
                assessment = {
                    "assessor": assessor_role,
                    "assessor_name": user_name,
                    "role": assessee_title,
                    "scores": scores,
                    "tomo": tomo,
                    "tomo_scores": tomo_scores,
                    "timestamp": timestamp,
                    "status": "Approved"  # Manager/Peer always approved
                }
                if assessee_name not in data:
                    data[assessee_name] = []
                data[assessee_name].append(assessment)
                save_data(data, DATA_FILE)
                st.success(f"{assessor_role} Assessment for {assessee_name} saved!")

    with tab3:
        data = load_data(DATA_FILE)
        if user_name in data:
            assessments = data[user_name]
            if assessments:
                st.subheader("Your Assessments")
                for i, assess in enumerate(assessments):
                    masked_origin = "Self" if assess['assessor'] == "Self" else f"{assess['assessor']} ({get_masked_id(assess.get('assessor_name', ''))})"
                    status = assess.get('status', 'Approved')
                    with st.expander(f"Assessment {i+1} ({assess['timestamp']}) - Origin: {masked_origin} - Status: {status}"):
                        if 'scores' in assess:
                            avg_score = sum(assess['scores'].values()) / len(assess['scores'])
                            st.write(f"Average Score: {avg_score:.2f}/5")
                            for crit, score in assess['scores'].items():
                                st.write(f"- {crit}: {score}")
                        if 'tomo' in assess:
                            st.write(f"ToMo: {assess['tomo']}")
            else:
                st.write("No assessments yet.")
        else:
            st.write("No assessments yet.")

        if st.button("Compute Overall Averages"):
            if user_name in data:
                assessments = [a for a in data[user_name] if a.get('status', 'Approved') == 'Approved']
                all_scores = {}
                tomo_list = []
                for assess in assessments:
                    if 'scores' in assess:
                        for crit, score in assess['scores'].items():
                            if crit not in all_scores:
                                all_scores[crit] = []
                            all_scores[crit].append(score)
                    if 'tomo' in assess:
                        tomo_list.append(assess['tomo'])
                if all_scores:
                    averages = {crit: sum(scores)/len(scores) if scores else 0 for crit, scores in all_scores.items()}
                    overall_avg = sum(averages.values()) / len(averages) if averages else 0
                    st.write(f"Overall Average Score: {overall_avg:.2f}/5")
                    for crit, avg in averages.items():
                        st.write(f"- {crit}: {avg:.2f}")
                if tomo_list:
                    avg_tomo = sum(tomo_list) / len(tomo_list)
                    st.write(f"Average ToMo: {avg_tomo:.2f}")
            else:
                st.write("No data to compute.")

    if is_manager(user_title):
        with tab4:
            st.subheader("Manage Assessments")
            data = load_data(DATA_FILE)
            all_assessments = []
            for uname, uassess in data.items():
                for idx, assess in enumerate(uassess):
                    all_assessments.append((uname, idx, assess))

            if all_assessments:
                for uname, idx, assess in all_assessments:
                    status = assess.get('status', 'Approved')
                    masked_origin = "Self" if assess['assessor'] == "Self" else f"{assess['assessor']} ({get_masked_id(assess.get('assessor_name', ''))})"
                    with st.expander(f"User: {uname} - Assessment {idx+1} ({assess['timestamp']}) - Origin: {masked_origin} - Status: {status}"):
                        if 'scores' in assess:
                            avg_score = sum(assess['scores'].values()) / len(assess['scores'])
                            st.write(f"Average Score: {avg_score:.2f}/5")
                            for crit, score in assess['scores'].items():
                                st.write(f"- {crit}: {score}")
                        if 'tomo' in assess:
                            st.write(f"ToMo: {assess['tomo']}")

                        col1, col2, col3 = st.columns(3)
                        if status == "Pending Approval":
                            if col1.button("Approve", key=f"approve_{uname}_{idx}"):
                                # If self, remove previous approved self
                                if assess['assessor'] == "Self":
                                    data[uname] = [a for a in data[uname] if not (a['assessor'] == "Self" and a.get('status', 'Approved') == 'Approved')]
                                assess['status'] = "Approved"
                                data[uname].append(assess) if assess['assessor'] == "Self" else None  # Re-add if removed
                                save_data(data, DATA_FILE)
                                st.success("Approved and replaced if applicable!")
                        if status == "Pending Approval" and col2.button("Reject", key=f"reject_{uname}_{idx}"):
                            assess['status'] = "Rejected"
                            save_data(data, DATA_FILE)
                            st.success("Rejected!")
                        if col3.button("Delete", key=f"delete_{uname}_{idx}"):
                            del data[uname][idx]
                            if not data[uname]:
                                del data[uname]
                            save_data(data, DATA_FILE)
                            st.success("Deleted!")
            else:
                st.write("No assessments to manage.")