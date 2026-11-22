import streamlit as st
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Employee Management System", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .header-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .status-healthy {
        color: #09ab3b;
        font-size: 1.2em;
        font-weight: bold;
    }
    .status-error {
        color: #d62728;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="header-title">👨‍💼 Employee Management System</div>', unsafe_allow_html=True)
with col2:
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            st.markdown('<div class="status-healthy">✅ Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">❌ Offline</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="status-error">❌ Offline</div>', unsafe_allow_html=True)

st.divider()

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "👥 All Employees", "🔍 Search Employee", "➕ Add Employee", "🗑️ Delete Employee"])

# TAB 1: Dashboard
with tab1:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏠 Welcome")
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                st.markdown(f"**{data['message']}**")
        except:
            st.error("Cannot connect to backend")
    
    with col2:
        st.markdown("### ℹ️ System Info")
        st.markdown("""
        **Employee Management System**
        
        A REST API to manage employee records.
        """)
    
    with col3:
        st.markdown("### 🔧 Features")
        st.markdown("""
        - View all employees
        - Search by ID
        - Create records
        - Delete records
        """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Employee Count")
        try:
            response = requests.get(f"{BASE_URL}/employees")
            if response.status_code == 200:
                data = response.json()
                employees = data.get("employees", [])
                st.metric("Total Employees", len(employees))
        except:
            st.error("Cannot fetch data")
    
    with col2:
        st.markdown("### 🛠️ Backend Status")
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                st.metric("Status", "✅ Healthy")
        except:
            st.metric("Status", "❌ Offline")

# TAB 2: View All Employees
with tab2:
    st.markdown("### 👥 All Employees")
    
    if st.button("🔄 Refresh Data", key="refresh_employees"):
        st.rerun()
    
    try:
        response = requests.get(f"{BASE_URL}/employees")
        if response.status_code == 200:
            data = response.json()
            employees = data.get("employees", [])
            if employees:
                df_data = [{"ID": emp.get("id"), "Name": emp.get("name"), "Position": emp.get("position"), 
                           "Email": emp.get("email")} for emp in employees]
                st.dataframe(df_data, use_container_width=True, height=400)
                
                st.markdown(f"**Total: {len(employees)} employees**")
            else:
                st.info("📭 No employees found")
        else:
            st.error("Failed to fetch employees")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# TAB 3: Search Employee
with tab3:
    st.markdown("### 🔍 Search Employee by ID")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        employee_id = st.number_input("Enter Employee ID:", min_value=1, step=1, key="search_id")
    
    with col2:
        search_btn = st.button("🔎 Search", key="search_btn")
    
    if search_btn:
        try:
            response = requests.get(f"{BASE_URL}/employees/{employee_id}")
            if response.status_code == 200:
                data = response.json()
                employee = data.get("employee", {})
                
                st.success("Employee found!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **ID:** {employee.get('id')}
                    
                    **Name:** {employee.get('name')}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Position:** {employee.get('position')}
                    
                    **Email:** {employee.get('email')}
                    """)
            else:
                st.error(f"❌ {response.json().get('error', 'Employee not found')}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# TAB 4: Create Employee
with tab4:
    st.markdown("### ➕ Create New Employee")
    
    with st.form("create_employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("👤 Full Name", placeholder="John Doe")
        
        with col2:
            email = st.text_input("📧 Email", placeholder="john@example.com")
        
        position = st.text_input("💼 Position", placeholder="Software Engineer")
        
        st.divider()
        
        submitted = st.form_submit_button("✅ Create Employee", use_container_width=True)
        
        if submitted:
            if not all([name, position, email]):
                st.error("⚠️ All fields are required")
            else:
                try:
                    payload = {
                        "name": name,
                        "position": position,
                        "email": email
                    }
                    response = requests.post(f"{BASE_URL}/employees", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        employee = data.get("employee", {})
                        
                        st.success("✅ Employee created successfully!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                            **ID:** {employee.get('id')}
                            
                            **Name:** {employee.get('name')}
                            """)
                        
                        with col2:
                            st.markdown(f"""
                            **Position:** {employee.get('position')}
                            
                            **Email:** {employee.get('email')}
                            """)
                    else:
                        st.error("Failed to create employee")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# TAB 5: Delete Employee
with tab5:
    st.markdown("### 🗑️ Delete Employee")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        employee_id = st.number_input("Enter Employee ID to delete:", min_value=1, step=1, key="delete_id")
    
    with col2:
        st.markdown("###")
        delete_btn = st.button("🗑️ Delete", type="secondary", use_container_width=True, key="delete_btn")
    
    if delete_btn:
        try:
            response = requests.delete(f"{BASE_URL}/employees/{employee_id}")
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ {data.get('message', 'Employee deleted successfully')}")
            else:
                error_data = response.json()
                st.error(f"❌ {error_data.get('error', 'Failed to delete employee')}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.divider()
st.markdown("**Built with:** FastAPI Backend • Streamlit Frontend")
