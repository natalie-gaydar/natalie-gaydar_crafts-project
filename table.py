import pandas as pd
from IPython.display import HTML, display as ipython_display

def display_table(top_viewed: pd.DataFrame):
    clickable_titles = []

    # Create a copy of the filtered data for display
    display_data = top_viewed[['Project-Title', 'Instructables-link', 'Views', 'Favorites', 'Subcategory']].copy()

    # Create clickable HTML links
    for index, row in display_data.iterrows():
        project_name = row['Project-Title']
        project_url = f"https://www.instructables.com{row['Instructables-link']}"
        html_link = f'<a href="{project_url}" target="_blank">{project_name}</a>'
        clickable_titles.append(html_link)

    # Replace the Project-Title column with clickable version
    display_data['Clickable Project Title'] = clickable_titles

    # Create final table without the original Project-Title and Instructables-link columns
    final_table = display_data[['Clickable Project Title', 'Views', 'Favorites', 'Subcategory']]

    # Display as HTML table
    ipython_display(HTML(final_table.to_html(escape=False, index=False)))