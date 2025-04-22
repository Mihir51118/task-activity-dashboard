import streamlit as st
import os
import re
import pandas as pd
import numpy as np
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from mailer import send_summary_email
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from mailer import send_summary_email  # ✅ REAL sender
# Set the page configuration FIRST
st.set_page_config(
    page_title="Task Activity Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Now you can use other Streamlit commands
st.title("Startup World")

# Define custom colors
CUSTOM_COLORS = px.colors.qualitative.Plotly

# Function to fetch data from the API
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_data(from_date, to_date):
    try:
        url = f"http://startupworld.in/Version1/get_task_activity.php?from_date={from_date}&to_date={to_date}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Exception occurred: {e}")
        return None

# Function to process data into a pandas DataFrame
def process_data(data):
    if "data" in data:
        df = pd.json_normalize(data["data"])
        
        # Convert date fields to datetime
        date_columns = ["created_date", "updated_date"]
        for col in date_columns:
            if col in df.columns:
               df[col] = pd.to_datetime(df[col], format='%d-%m-%Y', errors='coerce')

        
        # Convert time_spent to minutes for easier analysis
        if "time_spent" in df.columns:
            df["time_spent_minutes"] = df["time_spent"].apply(lambda x: convert_time_to_minutes(x) if pd.notnull(x) else 0)
        
        # Clean up nullable fields and ensure 'college' column is string
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].replace(["null", "NULL", "None", ""], np.nan)

        if 'college' in df.columns:
            # Convert 'college' column to string type to avoid TypeError
            df['college'] = df['college'].astype(str)
        
        return df
    else:
        st.error("No data field found in API response")
        return pd.DataFrame()

# Function to convert time strings like "4:30" to minutes
def convert_time_to_minutes(time_str):
    try:
        if pd.isnull(time_str) or time_str == "":
            return 0
        
        parts = time_str.split(":")
        if len(parts) == 2:
            hours = int(parts[0])
            minutes = int(parts[1])
            return hours * 60 + minutes
        else:
            return 0
    except:
        return 0

# Title and description
st.title("📊 Task Activity Dashboard")
st.markdown("""
This dashboard provides insights into task activities based on data from the StartupWorld API.
Use the filters in the sidebar to customize your view and explore the data.
""")

# Sidebar filters
st.sidebar.header("Filters")

# Date range picker
today = datetime.now().date()
yesterday = today - timedelta(days=1)
default_from_date = yesterday.strftime("%Y-%m-%d")
default_to_date = today.strftime("%Y-%m-%d")

from_date = st.sidebar.date_input("From Date", value=datetime.strptime(default_from_date, "%Y-%m-%d").date())
to_date = st.sidebar.date_input("To Date", value=datetime.strptime(default_to_date, "%Y-%m-%d").date())

# Format dates for API
from_date_str = from_date.strftime("%Y-%m-%d")
to_date_str = to_date.strftime("%Y-%m-%d")

# Fetch and process data
with st.spinner("Fetching data..."):
    raw_data = fetch_data(from_date_str, to_date_str)
    if raw_data:
        df = process_data(raw_data)
        if not df.empty:
            st.success(f"Successfully loaded {len(df)} task activities.")
        else:
            st.warning("No task activities found for the selected date range.")
    else:
        st.error("Failed to fetch data from API.")
        st.stop()

# Additional filters based on the data we have
if 'activity_status' in df.columns:
    status_options = ["All"] + sorted(df['activity_status'].unique().tolist())
    selected_status = st.sidebar.selectbox("Activity Status", status_options)

if 'project' in df.columns:
    project_options = ["All"] + sorted(df['project'].unique().tolist())
    selected_project = st.sidebar.selectbox("Project", project_options)

if 'college' in df.columns:
    # Ensure all values in 'college' are strings before sorting
    df['college'] = df['college'].astype(str)
    college_options = ["All"] + sorted(df['college'].unique().tolist())
    selected_college = st.sidebar.selectbox("College", college_options)

if 'task_title' in df.columns:
    task_options = ["All"] + sorted(df['task_title'].unique().tolist())
    selected_task = st.sidebar.selectbox("Task Type", task_options)

# Apply filters
filtered_df = df.copy()
if 'activity_status' in filtered_df.columns and selected_status != "All":
    filtered_df = filtered_df[filtered_df['activity_status'] == selected_status]
if 'project' in filtered_df.columns and selected_project != "All":
    filtered_df = filtered_df[filtered_df['project'] == selected_project]
if 'college' in filtered_df.columns and selected_college != "All":
    filtered_df = filtered_df[filtered_df['college'] == selected_college]
if 'task_title' in filtered_df.columns and selected_task != "All":
    filtered_df = filtered_df[filtered_df['task_title'] == selected_task]

# First row - Key metrics
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_tasks = len(filtered_df)
    st.metric("Total Tasks", total_tasks)

with col2:
    if 'activity_status' in filtered_df.columns:
        completed_tasks = filtered_df[filtered_df['activity_status'] == 'Completed'].shape[0]
        completion_rate = f"{completed_tasks / total_tasks * 100:.1f}%" if total_tasks > 0 else "0%"
        st.metric("Completed Tasks", completed_tasks, completion_rate)
    else:
        st.metric("Completed Tasks", "N/A")

with col3:
    if 'time_spent_minutes' in filtered_df.columns:
        total_time = filtered_df['time_spent_minutes'].sum()
        hours = int(total_time // 60)
        minutes = int(total_time % 60)
        st.metric("Total Time Spent", f"{hours}h {minutes}m")
    else:
        st.metric("Total Time Spent", "N/A")

with col4:
    if 'college' in filtered_df.columns:
        unique_colleges = filtered_df['college'].nunique()
        st.metric("Unique Colleges", unique_colleges)
    else:
        st.metric("Unique Colleges", "N/A")

# Second row - Task status breakdown
st.header("Task Status Distribution")
col1, col2 = st.columns(2)

with col1:
    if 'activity_status' in filtered_df.columns:
        status_counts = filtered_df['activity_status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        fig = px.pie(status_counts, values='Count', names='Status', 
                    title='Task Status Distribution',
                    color_discrete_sequence=CUSTOM_COLORS,
                    hole=0.4)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Activity status data not available")

with col2:
    if 'time_spent_minutes' in filtered_df.columns and 'activity_status' in filtered_df.columns:
        time_by_status = filtered_df.groupby('activity_status')['time_spent_minutes'].sum().reset_index()
        time_by_status.columns = ['Status', 'Minutes']
        
        fig = px.bar(time_by_status, x='Status', y='Minutes', 
                    title='Time Spent by Task Status',
                    color='Status',
                    color_discrete_sequence=CUSTOM_COLORS)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Time spent or activity status data not available")

# Third row - College analysis
st.header("College Activity Analysis")
col1, col2 = st.columns(2)

with col1:
    if 'college' in filtered_df.columns:
        college_task_counts = filtered_df.groupby('college').size().sort_values(ascending=False).head(10).reset_index()
        college_task_counts.columns = ['College', 'Task Count']
        
        fig = px.bar(college_task_counts, x='Task Count', y='College', 
                    title='Top 10 Colleges by Task Count',
                    color='Task Count',
                    color_continuous_scale=px.colors.sequential.Viridis,
                    orientation='h')
        fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("College data not available")

with col2:
    if 'time_spent_minutes' in filtered_df.columns and 'college' in filtered_df.columns:
        time_by_college = filtered_df.groupby('college')['time_spent_minutes'].sum().sort_values(ascending=False).head(10).reset_index()
        time_by_college.columns = ['College', 'Minutes']
        time_by_college['Hours'] = round(time_by_college['Minutes'] / 60, 2)
        
        fig = px.bar(time_by_college, x='Hours', y='College', 
                    title='Top 10 Colleges by Time Spent (Hours)',
                    color='Hours',
                    color_continuous_scale=px.colors.sequential.Plasma,
                    orientation='h')
        fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Time spent or college data not available")

# User activity analysis
st.header("User Activity Analysis")
col1, col2 = st.columns(2)

with col1:
    if 'uname' in filtered_df.columns:
        user_counts = filtered_df.groupby('uname').size().sort_values(ascending=False).head(10).reset_index()
        user_counts.columns = ['User', 'Task Count']
        
        fig = px.bar(user_counts, x='Task Count', y='User', 
                    title='Top 10 Users by Task Count',
                    color='Task Count',
                    color_continuous_scale=px.colors.sequential.Viridis,
                    orientation='h')
        fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("User name data not available")

with col2:
    if 'time_spent_minutes' in filtered_df.columns and 'uname' in filtered_df.columns:
        time_by_user = filtered_df.groupby('uname')['time_spent_minutes'].sum().sort_values(ascending=False).head(10).reset_index()
        time_by_user.columns = ['User', 'Minutes']
        time_by_user['Hours'] = round(time_by_user['Minutes'] / 60, 2)
        
        fig = px.bar(time_by_user, x='Hours', y='User', 
                    title='Top 10 Users by Time Spent (Hours)',
                    color='Hours',
                    color_continuous_scale=px.colors.sequential.Plasma,
                    orientation='h')
        fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Time spent or user name data not available")

# Task Type analysis
st.header("Task Type Analysis")
col1, col2 = st.columns(2)

with col1:
    if 'task_title' in filtered_df.columns:
        task_counts = filtered_df['task_title'].value_counts().head(10).reset_index()
        task_counts.columns = ['Task Type', 'Count']
        
        fig = px.bar(task_counts, x='Count', y='Task Type', 
                    title='Top 10 Task Types',
                    color='Count',
                    color_continuous_scale=px.colors.sequential.Viridis,
                    orientation='h')
        fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Task title data not available")

with col2:
    if 'time_spent_minutes' in filtered_df.columns and 'task_title' in filtered_df.columns:
        time_by_task = filtered_df.groupby('task_title')['time_spent_minutes'].sum().sort_values(ascending=False).head(10).reset_index()
        time_by_task.columns = ['Task Type', 'Minutes']
        time_by_task['Hours'] = round(time_by_task['Minutes'] / 60, 2)
        
        fig = px.bar(time_by_task, x='Hours', y='Task Type', 
                    title='Top 10 Task Types by Time Spent (Hours)',
                    color='Hours',
                    color_continuous_scale=px.colors.sequential.Plasma,
                    orientation='h')
        fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Time spent or task title data not available")



# Project analysis
# st.header("Project Performance")

# if 'project' in filtered_df.columns:
#     project_counts = filtered_df.groupby('project').agg({
#         'id': 'count',
#         'time_spent_minutes': 'sum'
#     }).reset_index()
#     project_counts.columns = ['Project', 'Task Count', 'Total Minutes']
#     project_counts['Hours'] = round(project_counts['Total Minutes'] / 60, 2)
#     project_counts = project_counts.sort_values('Task Count', ascending=False)
    
#     fig = px.scatter(project_counts, x='Task Count', y='Hours', 
#                      text='Project',
#                      size='Task Count',
#                      color='Hours',
#                      title='Projects by Task Count and Time Spent',
#                      color_continuous_scale=px.colors.sequential.Viridis)
#     fig.update_traces(textposition='top center')
#     fig.update_layout(height=600)
#     st.plotly_chart(fig, use_container_width=True)
# else:
#     st.info("Project data not available")

# Detailed task view
st.header("Detailed Task View")

# Add a text search box
search_term = st.text_input("Search tasks by title or remark")

# Filter by search term if provided
if search_term:
    search_columns = []
    for col in ['task_title', 'remark', 'current_task','uname','college','email']:
        if col in filtered_df.columns:
            search_columns.append(col)
    
    if search_columns:
        search_filter = filtered_df[search_columns[0]].str.contains(search_term, case=False, na=False)
        for col in search_columns[1:]:
            search_filter = search_filter | filtered_df[col].str.contains(search_term, case=False, na=False)
        searched_df = filtered_df[search_filter]
    else:
        searched_df = filtered_df
else:
    searched_df = filtered_df

# Show data table with the most relevant columns
if not searched_df.empty:
    # Select relevant columns for display
    display_cols = []
    for col in ['id','email', 'task_title', 'activity_status', 'remark', 'current_task', 'time_spent', 'created_date', 'college', 'uname']:
        if col in searched_df.columns:
            display_cols.append(col)
    
    if display_cols:
        st.dataframe(searched_df[display_cols], use_container_width=True)
    else:
        st.dataframe(searched_df, use_container_width=True)
else:
    st.info("No tasks match your search criteria.")

# Download option
st.header("Download Data")
st.markdown("Download the filtered data as a CSV file")

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(filtered_df)
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name=f"task_activities_{from_date_str}_to_{to_date_str}.csv",
    mime="text/csv",
)

# Footer
st.markdown("---")
st.markdown("Task Activity Dashboard | Created with Streamlit | Data source: StartupWorld API")

def fetch_data(from_date, to_date):
    return [
        {"task": "Task A", "activity_status": "Completed", "time_spent_minutes": 90},
        {"task": "Task B", "activity_status": "Pending", "time_spent_minutes": 45},
    ]

def process_data(data):
    return pd.DataFrame(data)

# 1️⃣ Dummy fetch/process placeholders
def fetch_data(from_date, to_date):
    return [
        {"task": "Task A", "activity_status": "Completed", "time_spent_minutes": 90},
        {"task": "Task B", "activity_status": "Pending", "time_spent_minutes": 45},
    ]

def process_data(data):
    return pd.DataFrame(data)

# 2️⃣ Generate and send report
def generate_email_report(recipients, detailed_df, date_for_report):
    csv_path = f"detailed_task_view_{date_for_report}.csv"
    detailed_df.to_csv(csv_path, index=False)
    subject = f"Startup World Report — {date_for_report}"
    total = len(detailed_df)
    done = detailed_df[detailed_df['activity_status'] == 'Completed'].shape[0] if 'activity_status' in detailed_df.columns else 0
    hours = round(detailed_df['time_spent'].apply(lambda x: convert_time_to_minutes(x) if pd.notnull(x) else 0).sum() / 60, 2) if 'time_spent' in detailed_df.columns else 0

    html_body = f"""
    <h2>📊 Detailed Task View</h2>
    <ul>
      <li><b>Total Tasks:</b> {total}</li>
      <li><b>Completed Tasks:</b> {done}</li>
      <li><b>Total Time Spent:</b> {hours} hours</li>
    </ul>
    """

    send_summary_email(recipients, subject, html_body, csv_path)
    print("✅ Detailed Task View report email sent!")


# 3️⃣ Config helpers
def save_email_time(time_obj):
    os.makedirs("config", exist_ok=True)
    with open("config/email_time.json", "w") as f:
        json.dump({"hour": time_obj.hour, "minute": time_obj.minute}, f)

def load_email_time():
    try:
        with open("config/email_time.json", "r") as f:
            data = json.load(f)
            return data.get("hour", 18), data.get("minute", 0)
    except:
        return 18, 0

def get_saved_time_str():
    hour, minute = load_email_time()
    return f"{hour:02d}:{minute:02d}"

def validate_emails(input_str):
    emails = [e.strip() for e in input_str.split(",")]
    valid_email_pattern = r"[^@]+@[^@]+\.[^@]+"
    return [e for e in emails if re.match(valid_email_pattern, e)][:10]

# 4️⃣ Streamlit UI
st.sidebar.markdown("### 📬 Email Schedule")

# Email input
email_input = st.sidebar.text_area(
    "Enter up to 10 recipient emails (comma separated):",
    placeholder="example1@gmail.com, example2@gmail.com"
)
valid_recipients = validate_emails(email_input)

# Time picker
email_time = st.sidebar.time_input(
    "Select time to send daily report",
    value=datetime.strptime("18:00", "%H:%M").time()
)

if st.sidebar.button("💾 Save Email Time"):
    save_email_time(email_time)
    st.sidebar.success(f"Email time saved: {email_time.strftime('%H:%M')}")

st.sidebar.markdown(f"⏱️ **Current Scheduled Time:** {get_saved_time_str()}")

# 📤 Manual Send
if st.button("📤 Send Email Now"):
    if valid_recipients:
        date_for_report = to_date_str
        if 'display_cols' in locals() and display_cols:
            detailed_df = searched_df[display_cols]
        else:
            detailed_df = searched_df
        generate_email_report(valid_recipients, detailed_df, date_for_report)
        st.success("✅ Email sent immediately!")
    else:
        st.error("⚠️ Please enter valid email addresses.")

# 🕒 Auto Scheduler
scheduler = BackgroundScheduler()

def schedule_email():
    if valid_recipients:
        generate_email_report(valid_recipients)
    else:
        print("⚠️ No valid recipients to send email to.")

def start_scheduled_job():
    hour, minute = load_email_time()
    scheduler.add_job(schedule_email, "cron", hour=hour, minute=minute, id="daily_email", replace_existing=True)
    scheduler.start()
    st.success(f"✅ Email will now be sent daily at {hour:02d}:{minute:02d}")

if st.button("🕒 Start Scheduled Email"):
    start_scheduled_job()