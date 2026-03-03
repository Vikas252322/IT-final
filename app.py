import streamlit as st
import pandas as pd
from datetime import date
from database import *

create_tables()

st.set_page_config(page_title="Enterprise Workforce Dashboard", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
h1, h2, h3 { color: #00FFD1; }
.stButton>button {
    background: linear-gradient(90deg, #00FFD1, #00C6FF);
    color: black;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -------- SESSION --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# -------- LOGIN PAGE --------
def login_page():
    st.title("🔐 Enterprise Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = connect()
        user = pd.read_sql(
            "SELECT * FROM users WHERE username=? AND password=?",
            conn,
            params=(username, password)
        )
        conn.close()

        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.role = user["role"].values[0]
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# -------- MAIN APP --------
if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.write(f"👤 Logged in as: {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    st.sidebar.title("Navigation")

    menu = st.sidebar.selectbox("Go to",[
        "Dashboard",
        "Manage Branch",
        "Add Employee",
        "Manage Skills",
        "Employee Skills",
        "Apply Leave",
        "Payroll",
        "Search & Compare by Skill"
    ])

    level_map = {"Beginner":1,"Intermediate":2,"Expert":3}
    reverse_map = {1:"Beginner",2:"Intermediate",3:"Expert"}

    # -------- DASHBOARD --------
    if menu == "Dashboard":
        st.title("🏢 Enterprise Dashboard")

        conn = connect()
        total_emp = pd.read_sql("SELECT COUNT(*) as c FROM employees",conn)["c"][0]
        total_branch = pd.read_sql("SELECT COUNT(*) as c FROM branches",conn)["c"][0]
        total_salary = pd.read_sql("SELECT SUM(net_salary) as s FROM payroll",conn)["s"][0]
        conn.close()

        col1,col2,col3 = st.columns(3)
        col1.metric("Total Employees", total_emp)
        col2.metric("Total Branches", total_branch)
        col3.metric("Total Salary Paid", total_salary if total_salary else 0)

    # -------- BRANCH --------
    elif menu == "Manage Branch":
        st.title("🏢 Add Branch")
        branch = st.text_input("Branch Name")

        if st.button("Add Branch"):
            conn = connect()
            try:
                conn.execute("INSERT INTO branches(branch_name) VALUES(?)",(branch,))
                conn.commit()
                st.success("Branch Added")
            except:
                st.warning("Branch already exists")
            conn.close()

    # -------- ADD EMPLOYEE --------
    elif menu == "Add Employee":
        st.title("👤 Add Employee")

        name = st.text_input("Name")
        role = st.text_input("Role")
        salary = st.number_input("Monthly Salary",min_value=0.0)

        conn = connect()
        branches = pd.read_sql("SELECT * FROM branches",conn)
        conn.close()

        if not branches.empty:
            branch = st.selectbox("Branch",branches["branch_name"])
            branch_id = branches[branches["branch_name"]==branch]["id"].values[0]

            if st.button("Save Employee"):
                conn = connect()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO employees(name,branch_id,role,salary) VALUES(?,?,?,?)",
                    (name,branch_id,role,salary)
                )
                emp_id = cursor.lastrowid
                cursor.execute("INSERT OR IGNORE INTO leave_balance(employee_id) VALUES(?)",(emp_id,))
                conn.commit()
                conn.close()
                st.success("Employee Added")

    # -------- MANAGE SKILLS --------
    elif menu == "Manage Skills":
        st.title("🛠 Add Skill")
        skill = st.text_input("Skill Name")

        if st.button("Add Skill"):
            conn = connect()
            try:
                conn.execute("INSERT INTO skills(skill_name) VALUES(?)",(skill,))
                conn.commit()
                st.success("Skill Added")
            except:
                st.warning("Skill exists")
            conn.close()

    # -------- SEARCH & COMPARE --------
    elif menu == "Search & Compare by Skill":
        st.title("🔎 Search & Compare Employees by Skill")

        conn = connect()
        skills = pd.read_sql("SELECT * FROM skills",conn)
        conn.close()

        if not skills.empty:
            skill = st.selectbox("Select Skill",skills["skill_name"])

            if st.button("Search"):
                conn = connect()
                result = pd.read_sql("""
                    SELECT employees.name, employees.salary,
                           employee_skills.level
                    FROM employee_skills
                    JOIN employees ON employees.id=employee_skills.employee_id
                    JOIN skills ON skills.id=employee_skills.skill_id
                    WHERE skills.skill_name=?
                    ORDER BY employee_skills.level DESC
                """,conn,params=(skill,))
                conn.close()

                if result.empty:
                    st.warning("No employee has this skill")
                else:
                    result["Level"] = result["level"].map(reverse_map)
                    st.dataframe(result[["name","salary","Level"]])

                    selected = st.multiselect("Select Employees to Compare",
                                              result["name"])

                    if selected:
                        conn = connect()
                        query = f"""
                            SELECT employees.name, salary,
                                   paid_left, casual_left, sick_left
                            FROM employees
                            JOIN leave_balance ON employees.id=leave_balance.employee_id
                            WHERE employees.name IN ({','.join(['?']*len(selected))})
                        """
                        compare_data = pd.read_sql(query,conn,params=selected)
                        conn.close()

                        st.subheader("Comparison Result")
                        st.dataframe(compare_data)
