import streamlit as st
import json
import os
from datetime import datetime
import hashlib
import pandas as pd

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

def pre_populate_users():
    users = load_data(USERS_FILE)
    if not users:
        # Add superadmin
        users['sadmin'] = {"password": "12345", "role": "Superadmin"}
        # Add 14 users
        for i in range(1, 15):
            num = f"{i:03d}"
            username = f"Potato-{num}"
            password = f"p{num}"
            users[username] = {
                "password": password,
                "role": "User",
                "title": "Product Designer",  # Default title
                "team": [] if "Manager" in "Product Designer" else None
            }
        save_data(users, USERS_FILE)
    return users

def is_superadmin(username):
    return username == 'sadmin'

def is_manager(role):
    return role == "Manager"

def get_masked_id(name):
    m = hashlib.md5()
    m.update(name.encode('utf-8'))
    return m.hexdigest()[:6].upper()

def add_manager():
    st.session_state["show_assign_form"] = True
    st.session_state["selected_manager"] = None

def edit_manager(manager):
    st.session_state["show_assign_form"] = True
    st.session_state["selected_manager"] = manager

# Login function
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_data(USERS_FILE)
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = users[username].get("role", "User")
            st.session_state["title"] = users[username].get("title", "")
            st.session_state["team"] = users[username].get("team", [])
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")

pre_populate_users()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    username = st.session_state["username"]
    role = st.session_state["role"]
    title = st.session_state["title"]
    team = st.session_state["team"]

    # Logout button for all dashboards
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    if is_superadmin(username):
        # Superadmin view
        st.title("Superadmin Dashboard")
        data = load_data(DATA_FILE)
        users = load_data(USERS_FILE)

        # Submission Stats
        st.subheader("Submission Stats")
        total_submissions = sum(len(data.get(u, [])) for u in users if u != 'sadmin')
        total_approved = sum(len([a for a in data.get(u, []) if a.get('status', 'Approved') == 'Approved']) for u in users if u != 'sadmin')
        total_pending = sum(len([a for a in data.get(u, []) if a.get('status') == 'Pending Approval']) for u in users if u != 'sadmin')
        total_rejected = sum(len([a for a in data.get(u, []) if a.get('status') == 'Rejected']) for u in users if u != 'sadmin')
        st.write(f"Total Submissions: {total_submissions}")
        st.write(f"Approved: {total_approved}")
        st.write(f"Pending: {total_pending}")
        st.write(f"Rejected: {total_rejected}")

        # List of user scores and stats
        st.subheader("User Assessment Overview")
        pending_count = 0
        for u in users:
            if u == 'sadmin': continue
            u_assess = data.get(u, [])
            approved = len([a for a in u_assess if a.get('status', 'Approved') == 'Approved'])
            pending = len([a for a in u_assess if a.get('status') == 'Pending Approval'])
            rejected = len([a for a in u_assess if a.get('status') == 'Rejected'])
            if pending > 0:
                pending_count += pending
            st.write(f"{u} ({users[u]['title']}): Approved={approved}, Pending={pending}, Rejected={rejected}")

        if pending_count > 0:
            if st.button("Go to Approval Section"):
                st.session_state["show_manage"] = True

        if st.session_state.get("show_manage", False):
            st.subheader("Manage Assessments")
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
                                if assess['assessor'] == "Self":
                                    data[uname] = [a for a in data[uname] if not (a['assessor'] == "Self" and a.get('status', 'Approved') == 'Approved')]
                                assess['status'] = "Approved"
                                data[uname].append(assess) if assess['assessor'] == "Self" else None
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

        # User management
        st.subheader("User Management")
        if st.button("Add Manager"):
            add_manager()

        if st.session_state.get("show_assign_form", False):
            if st.session_state.get("selected_manager") is None:
                selected_user = st.selectbox("Select User to Assign as Manager", [u for u in users if u != 'sadmin' and users[u]["role"] != "Manager"])
            else:
                selected_user = st.session_state["selected_manager"]
            if selected_user:
                team_members = st.multiselect("Assign Team Members", [u for u in users if u != 'sadmin' and u != selected_user], default=users.get(selected_user, {}).get("team", []))
                if st.button("Confirm Changes"):
                    if st.session_state.get("confirm_changes", False):
                        users[selected_user]["role"] = "Manager"
                        users[selected_user]["team"] = team_members
                        save_data(users, USERS_FILE)
                        st.success("Manager assigned/updated!")
                        st.session_state["show_assign_form"] = False
                        st.session_state["confirm_changes"] = False
                        st.session_state["selected_manager"] = None
                    else:
                        st.warning("Are you sure? Click 'Confirm Changes' again to save.")
                        st.session_state["confirm_changes"] = True

        # List of managers
        st.subheader("List of Managers")
        managers = [u for u in users if users[u]["role"] == "Manager"]
        if managers:
            for manager in managers:
                team_size = len(users[manager].get("team", []))
                col1, col2 = st.columns([4, 1])
                col1.write(f"{manager} - Team Size: {team_size}")
                if col2.button("Edit", key=f"edit_{manager}", on_click=edit_manager, args=(manager,)):
                    pass
        else:
            st.write("No managers assigned yet.")

    else:
        # User or Manager view
        st.title("Dashboard")
        st.write(f"Welcome, {username} ({title})")

        data = load_data(DATA_FILE)
        user_assessments = data.get(username, [])
        approved_self = [a for a in user_assessments if a['assessor'] == "Self" and a.get('status', 'Approved') == 'Approved']
        has_self = len(approved_self) > 0

        tabs = ["Self Assessment"]
        if role == "Manager":
            tabs.append("Team Management")
        tab_objects = st.tabs(tabs)

        with tab_objects[0]:
            if has_self:
                if st.button("Submit Assessment"):
                    st.session_state["show_survey"] = True
            else:
                st.session_state["show_survey"] = True

            if st.session_state.get("show_survey", False) or not has_self:
                st.subheader("Self Assessment")
                criteria_list = CRITERIA[title]

                pending = has_self  # If has approved, new is pending

                if pending:
                    st.warning("This submission will require manager approval to replace the existing one.")

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
                        "role": title,
                        "scores": self_scores,
                        "tomo": tomo,
                        "tomo_scores": tomo_scores,
                        "timestamp": timestamp,
                        "status": "Pending Approval" if pending else "Approved"
                    }
                    if username not in data:
                        data[username] = []
                    data[username].append(assessment)
                    save_data(data, DATA_FILE)
                    st.success("Self Assessment submitted!" + (" (Pending Approval)" if pending else ""))
                    st.session_state["show_survey"] = False

            if has_self:
                # Display averages and bar chart
                assessments = [a for a in user_assessments if a.get('status', 'Approved') == 'Approved']
                all_scores = {}
                for assess in assessments:
                    for crit, score in assess['scores'].items():
                        if crit not in all_scores:
                            all_scores[crit] = []
                        all_scores[crit].append(score)
                averages = {crit: sum(scores)/len(scores) for crit, scores in all_scores.items()}
                overall_avg = sum(averages.values()) / len(averages)

                self_count = len([a for a in assessments if a['assessor'] == "Self"])
                peer_count = len([a for a in assessments if a['assessor'] == "Peer"])
                manager_count = len([a for a in assessments if a['assessor'] == "Manager"])

                st.subheader("Overall Average Score")
                st.write(f"{overall_avg:.2f}/5")
                st.write(f"Assessors: Self = {self_count}, Peer = {peer_count}, Manager = {manager_count}")

                # Tabulated scores
                st.table(averages)

                # Bar chart visualization
                st.subheader("Score Diagram")
                df = pd.DataFrame.from_dict(averages, orient='index', columns=['Average Score'])
                st.bar_chart(df)

        if role == "Manager":
            with tab_objects[1]:
                st.subheader("Team Management")
                for team_member in team:
                    st.write(f"**{team_member}**")
                    member_assess = data.get(team_member, [])
                    # Similar to user view, show averages, bar chart if approved
                    approved_assess = [a for a in member_assess if a.get('status', 'Approved') == 'Approved']
                    if approved_assess:
                        all_scores = {}
                        for assess in approved_assess:
                            for crit, score in assess['scores'].items():
                                if crit not in all_scores:
                                    all_scores[crit] = []
                                all_scores[crit].append(score)
                        averages = {crit: sum(scores)/len(scores) for crit, scores in all_scores.items()}
                        overall_avg = sum(averages.values()) / len(averages)

                        self_count = len([a for a in approved_assess if a['assessor'] == "Self"])
                        peer_count = len([a for a in approved_assess if a['assessor'] == "Peer"])
                        manager_count = len([a for a in approved_assess if a['assessor'] == "Manager"])

                        st.write(f"Overall Average: {overall_avg:.2f}/5")
                        st.write(f"Assessors: Self = {self_count}, Peer = {peer_count}, Manager = {manager_count}")
                        st.table(averages)

                        # Bar chart
                        df = pd.DataFrame.from_dict(averages, orient='index', columns=['Average Score'])
                        st.bar_chart(df)

                    # Pending approvals
                    pending_assess = [ (idx, a) for idx, a in enumerate(member_assess) if a.get('status') == 'Pending Approval' ]
                    if pending_assess:
                        st.write("Pending Assessments")
                        for idx, assess in pending_assess:
                            with st.expander(f"Assessment {idx+1} ({assess['timestamp']}) - {assess['assessor']}"):
                                avg_score = sum(assess['scores'].values()) / len(assess['scores'])
                                st.write(f"Average Score: {avg_score:.2f}/5")
                                for crit, score in assess['scores'].items():
                                    st.write(f"- {crit}: {score}")
                                if 'tomo' in assess:
                                    st.write(f"ToMo: {assess['tomo']}")

                                col1, col2 = st.columns(2)
                                if col1.button("Approve", key=f"team_approve_{team_member}_{idx}"):
                                    if assess['assessor'] == "Self":
                                        data[team_member] = [a for a in data[team_member] if not (a['assessor'] == "Self" and a.get('status', 'Approved') == 'Approved')]
                                    assess['status'] = "Approved"
                                    data[team_member].append(assess)
                                    save_data(data, DATA_FILE)
                                    st.success("Approved!")
                                if col2.button("Reject", key=f"team_reject_{team_member}_{idx}"):
                                    assess['status'] = "Rejected"
                                    save_data(data, DATA_FILE)
                                    st.success("Rejected!")