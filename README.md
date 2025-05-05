# CORDIS Horizon Europe Explorer (2021–2027)

This Streamlit-based web app allows users to explore data from the CORDIS Horizon Europe (2021–2027) programme, focusing on projects and their related publications.

## Features

- Download and process CORDIS Horizon Europe project and publication data.
- Search projects by acronym, organization, or project ID.
- View project details and associated publications in a user-friendly interface.
- Lightweight and runs entirely in the browser (via Streamlit).

## Data Sources

- [CORDIS Horizon Projects CSV (ZIP)](https://cordis.europa.eu/data/cordis-HORIZONprojects-csv.zip)
- [CORDIS Horizon Publications CSV (ZIP)](https://cordis.europa.eu/data/cordis-HORIZONprojectPublications-csv.zip)

## Installation

1. Clone this repository or download the script.
2. Install dependencies:
   ```bash
   pip install streamlit pandas requests
   ```

3. Run the app:
   ```bash
   streamlit run cordis_explorer.py
   ```

## Notes

- The script uses Streamlit's caching to speed up repeated data loads.
- Input CSVs are loaded directly from the official CORDIS EU data portal.

## License

This project is provided "as is" without warranty of any kind.

---

© 2025
