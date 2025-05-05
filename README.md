# CORDIS Horizon Europe Explorer (2021–2027)

This Streamlit-based web app allows users to explore data from the CORDIS Horizon Europe (2021–2027) programme, focusing on projects and their related publications.

## Features

- Download and process CORDIS Horizon Europe project and publication data.
- Search projects by acronym, organization, or project ID.
- View project details and associated publications
- Lightweight and runs entirely in the browser (via Streamlit).

## Data Sources

- Source: Publications Office. (2022). CORDIS - EU research projects under HORIZON EUROPE (2021-2027) [Data set](https://doi.org/10.2906/112117098108/20)

## Notes

- The script uses Streamlit's caching to speed up repeated data loads.
- Input CSVs are loaded directly from the official CORDIS EU data portal.