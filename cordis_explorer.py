import streamlit as st
import pandas as pd
import zipfile
import io
import requests
import datetime

# URLs
PROJECTS_ZIP_URL = "https://cordis.europa.eu/data/cordis-HORIZONprojects-csv.zip"
PUBLICATIONS_ZIP_URL = "https://cordis.europa.eu/data/cordis-HORIZONprojectPublications-csv.zip"

st.set_page_config(layout="wide")

@st.cache_data(show_spinner=False)
def download_and_extract_csv(url):
    response = requests.get(url)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        for file in z.namelist():
            if file.endswith('.csv'):
                with z.open(file) as f:
                    df = pd.read_csv(f, sep=';', low_memory=False, on_bad_lines='skip')
                return df
    return None

st.title("CORDIS Horizon Europe Explorer (2021-2027)")
st.markdown("""
This lightweight tool allows you to explore links between **EU Horizon Europe projects (2021–2027)** and their **related publications**. 
Search by project acronym, organization, or project ID — and export results as needed.


Source: Publications Office. (2022). CORDIS - EU research projects under HORIZON EUROPE (2021-2027) [Data set](https://doi.org/10.2906/112117098108/20)

CORDIS datasets are updated monthly.
""")

st.header("🔎 Explore Links Between Projects and Publications")
# Initialize session_state to hold loaded data
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'projects_df' not in st.session_state:
    st.session_state.projects_df = None
if 'publications_df' not in st.session_state:
    st.session_state.publications_df = None
if 'selected_acronym' not in st.session_state:
    st.session_state.selected_acronym = "All"
if 'selected_org' not in st.session_state:
    st.session_state.selected_org = "All"
if 'search_project_id' not in st.session_state:
    st.session_state.search_project_id = ""

# Reset mechanism
if st.session_state.get("reset_triggered"):
    st.session_state.selected_acronym = "All"
    st.session_state.selected_org = "All"
    st.session_state.search_project_id = ""
    st.session_state.reset_triggered = False

# Add manual force refresh
refresh = st.sidebar.checkbox("Force fresh download", value=False)

# Display last fetch time if available
if 'last_fetch_time' in st.session_state:
    st.sidebar.caption(f"Last updated: {st.session_state.last_fetch_time.strftime('%Y-%m-%d %H:%M:%S')}")

if st.sidebar.button("Fetch Projects and Publications"):
    if refresh:
        download_and_extract_csv.clear()
    with st.spinner("Downloading and extracting data..."):
        st.session_state.projects_df = download_and_extract_csv(PROJECTS_ZIP_URL)
        st.session_state.publications_df = download_and_extract_csv(PUBLICATIONS_ZIP_URL)
        st.session_state.data_loaded = True
        st.session_state.last_fetch_time = datetime.datetime.now()
    st.success("Data loaded successfully!")

if st.session_state.data_loaded:
    projects_df = st.session_state.projects_df
    publications_df = st.session_state.publications_df
    # Deduplicate projects: one row per project
    if 'projectID' in projects_df.columns and 'name' in projects_df.columns:
        orgs_per_project = projects_df.groupby('projectID')['name'].apply(lambda x: "; ".join(sorted(set(x.dropna())))).reset_index()
        first_rows = projects_df.drop_duplicates(subset='projectID', keep='first')
        projects_df = pd.merge(first_rows, orgs_per_project, on='projectID', suffixes=('', '_combined'))
        projects_df['Organizations'] = projects_df['name_combined']

    if 'projectID' in publications_df.columns and 'projectID' in projects_df.columns:
        publications_df['projectID'] = publications_df['projectID'].astype(str)
        projects_df['projectID'] = projects_df['projectID'].astype(str)
        merged_df = publications_df.merge(
            projects_df,
            on='projectID',
            suffixes=('_pub', '_proj')
        )

        # Combine all organization names per publication ID
        if 'id' in merged_df.columns and 'Organizations' in merged_df.columns:
            merged_df['Organizations'] = merged_df.groupby('id')['Organizations'].transform(lambda x: "; ".join(sorted(set(x.dropna()))))
            combined_df = merged_df.drop_duplicates(subset='id').copy()
        else:
            combined_df = merged_df.copy()

        # Dropdown for project acronym
        acronym_options = ['All'] + sorted(combined_df['projectAcronym_proj'].dropna().unique().tolist())
        selected_acronym = st.selectbox("Filter by Project Acronym:", acronym_options, key="selected_acronym")

        # Dropdown for organization name
        org_names = set()
        for orgs in combined_df['Organizations'].dropna().unique():
            org_names.update([o.strip() for o in orgs.split(';')])
        org_options = ['All'] + sorted(org_names)
        selected_org = st.selectbox("Filter by Organization Name:", org_options, key="selected_org")

        # Search box for project ID
        search_project_id = st.text_input("Search by Project ID:", key="search_project_id")

        # Reset filters button
        if st.button("🔄 Reset Filters"):
            st.session_state.reset_triggered = True
            st.rerun()

        # Filtering logic
        filtered_df = combined_df.copy()
        if selected_acronym != "All":
            filtered_df = filtered_df[filtered_df['projectAcronym_proj'] == selected_acronym]
        if selected_org != "All":
            filtered_df = filtered_df[filtered_df['Organizations'].str.contains(selected_org)]
        if search_project_id:
            filtered_df = filtered_df[filtered_df['projectID'].str.strip() == search_project_id.strip()]

        st.write(f"Showing {len(filtered_df)} matching publications")
        st.dataframe(filtered_df.head(500))

        # Export filtered results
        csv_export = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇ Download Results as CSV",
            data=csv_export,
            file_name='cordis_filtered_results.csv',
            mime='text/csv',
        )
        
    else:
        st.error("Could not find 'projectID' columns to merge datasets.")
    
    # Display Projects and Publications datasets as collapsibles at the bottom of the page
    with st.expander("Projects Dataset"):
        st.dataframe(projects_df)

    with st.expander("Publications Dataset"):
        st.dataframe(publications_df)

else:
    st.info("Click the button in the sidebar to fetch and load the data.")

# Add spacer to push creator info down
st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

# Creator info block
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Created by:**<br>"
    "Søren Vidmar<br>"
    "🔗 <a href='https://orcid.org/0000-0003-3055-6053'>ORCID</a><br>"
    "🏫 Aalborg University<br>"
    "📧 <a href='mailto:sv@aub.aau.dk'>sv@aub.aau.dk</a><br>"
    "📦 <a href='https://github.com/svidmar'>GitHub</a>",
    unsafe_allow_html=True
)
