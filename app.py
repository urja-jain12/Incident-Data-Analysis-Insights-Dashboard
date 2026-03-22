import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

MAIN = "#4E79A7"
SECONDARY = "#59A14F"

st.sidebar.title("Upload Dataset")
upload_file = st.sidebar.file_uploader("Choose a CSV File", type="csv")

if upload_file is not None:
    df = pd.read_csv(upload_file)

    # ---------------- DATA CLEANING ----------------
    df = df.drop_duplicates()

    df['age'] = df['age'].fillna(df['age'].median())
    df['gender'] = df['gender'].fillna("Unknown")
    df['type_of_injury'] = df['type_of_injury'].fillna("Unknown")

    df['gender'] = df['gender'].str.title()
    df['event_location_region'] = df['event_location_region'].str.title()

    df['date_of_event'] = pd.to_datetime(df['date_of_event'], errors='coerce')

    # ---------------- FILTERS ----------------
    st.sidebar.header("Filters")

    region_filter = st.sidebar.multiselect(
        "Select Region",
        options=df['event_location_region'].dropna().unique(),
        default=df['event_location_region'].dropna().unique()
    )

    injury_filter = st.sidebar.multiselect(
        "Select Injury Type",
        options=df['type_of_injury'].dropna().unique(),
        default=df['type_of_injury'].dropna().unique()
    )

    gender_filter = st.sidebar.multiselect(
        "Select Gender",
        options=df['gender'].dropna().unique(),
        default=df['gender'].dropna().unique()
    )

    df = df[
        (df['event_location_region'].isin(region_filter)) &
        (df['type_of_injury'].isin(injury_filter)) &
        (df['gender'].isin(gender_filter))
    ]

    # ---------------- DASHBOARD ----------------
    st.title('Incident Data Analysis & Insights Dashboard')
    st.write('Dataset Sample')

    # Sidebar stats
    no_event = len(df)
    citizenship_counts = df['citizenship'].value_counts()
    event_location_region = df['event_location_region'].value_counts()
    hostilities_count = df[df['took_part_in_the_hostilities'] == 'Yes']['citizenship'].value_counts()
    no_hostilities_count = df[df['took_part_in_the_hostilities'] == 'No']['citizenship'].value_counts()

    st.sidebar.write("Number of Events : ", no_event)

    col1, col2 = st.sidebar.columns(2)
    col3, col4 = st.sidebar.columns(2)

    with col1:
        st.subheader("Citizenship Counts")
        st.write(citizenship_counts)

    with col2:
        st.subheader("Region Count")
        st.write(event_location_region)

    with col3:
        st.subheader("Hostilities Count")
        st.write(hostilities_count)

    with col4:
        st.subheader("No Hostilities Count")
        st.write(no_hostilities_count)

    weapons_counts = df['ammunition'].value_counts()
    st.sidebar.write("Number of Weapons : ", weapons_counts)

    # ---------------- KPI ----------------
    col1, col2, col3 = st.columns(3)

    total_incidents = len(df)
    most_affected_region = df['event_location_region'].mode()[0] if not df.empty else "N/A"
    dominant_injury = df['type_of_injury'].mode()[0] if not df.empty else "N/A"

    col1.metric("Total Incidents", total_incidents)
    col2.metric("Most Affected Region", most_affected_region)
    col3.metric("Dominant Injury Type", dominant_injury)

    # ---------------- TIME ANALYSIS ----------------
    yearly = df['date_of_event'].dt.year.value_counts().sort_index()

    st.subheader("Incidents Over Time (Yearly Trend)")
    st.line_chart(yearly)

    # ---------------- INJURY + GENDER ----------------
    col1, col2 = st.columns(2)

    top_injuries = df['type_of_injury'].value_counts().nlargest(5)
    others = df['type_of_injury'].value_counts()[5:].sum()
    top_injuries['Others'] = others

    with col1:
        st.subheader("Top Injury Types")
        st.bar_chart(top_injuries)

    with col2:
        st.subheader("Incident Count by Gender")
        MFcounts = df['gender'].value_counts()
        st.bar_chart(MFcounts)

    # ---------------- HOSTILITY ----------------
    hostility = df['took_part_in_the_hostilities'].value_counts()
    st.subheader("Involvement in Hostilities")
    st.bar_chart(hostility)

    # ---------------- AGE + REGION ----------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Age Summary")
        st.write(df['age'].describe())

        bins = [0, 18, 30, 50, 80]
        labels = ['Children', 'Young Adults', 'Adults', 'Older']
        df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels)

        age_group_counts = df['age_group'].value_counts()
        st.subheader("Incidents by Age Group")
        st.bar_chart(age_group_counts)

    with col2:
        st.subheader("Incident Counts by Region")
        reg = df['event_location_region'].value_counts()
        st.bar_chart(reg)

    # ---------------- AMMUNITION ----------------
    ammo = df['ammunition'].value_counts().head(5)
    st.subheader("Top Ammunition Types Used")
    st.bar_chart(ammo)

    # ---------------- PIE CHARTS ----------------
    col1, col2 = st.columns(2)

    with col1:
        residencecountbyreg = df.groupby('event_location_region')['place_of_residence'].nunique()
        st.subheader("Residence Distribution by Region (%)")
        fig, ax = plt.subplots()
        ax.pie(
            residencecountbyreg,
            labels=residencecountbyreg.index,
            autopct='%1.1f%%',
            startangle=90
        )
        ax.axis("equal")
        st.pyplot(fig)

    with col2:
        injurytype = df['type_of_injury'].value_counts()
        st.subheader("Injury Type Distribution")
        fig, ax = plt.subplots()

        wedges, texts, autotexts = ax.pie(
            injurytype,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.75
        )

        ax.legend(
            wedges,
            injurytype.index,
            title="Injury Type",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )

        ax.axis("equal")
        st.pyplot(fig)

    # ---------------- AVG AGE ----------------
    avg_age_by_region = df.groupby('event_location_region')['age'].mean()
    st.subheader("Average Age by Region")
    st.bar_chart(avg_age_by_region)

    # ---------------- DISTRICT ----------------
    col1, col2 = st.columns(2)

    with col1:
        Incident_byreg = df.groupby('event_location_region').size()
        st.subheader("Total Incidents by Region")
        st.bar_chart(Incident_byreg)

    district = df['event_location_district'].value_counts().head(10)
    st.subheader("Top Affected Districts")
    st.bar_chart(district)

    # ---------------- DATA CLEANING INFO ----------------
    st.markdown("## 🧹 Data Cleaning & Preprocessing")

    st.write("""
    - Removed duplicate records  
    - Handled missing values using median and default categories  
    - Standardized categorical values for consistency  
    - Converted date column to datetime format for time analysis  
    """)