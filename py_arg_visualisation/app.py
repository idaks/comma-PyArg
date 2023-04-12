from dash import Dash, html
import dash_bootstrap_components as dbc
import dash


# Create a Dash app using an external stylesheet.
app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.YETI])

# Navigation bar.
navbar = dbc.Navbar(dbc.Container([dbc.Row(
    [dbc.Col(dbc.NavItem(dbc.NavLink(page['name'], href=page['relative_path'])))
     for page in dash.page_registry.values()] +
    [dbc.Col(html.Img(src=app.get_asset_url('UU_logo_2021_EN_RGB.png')))], align='center', className='g-0')]))

# Specification of the layout, consisting of a navigation bar and the page container.
app.layout = html.Div([navbar, dbc.Col(html.Div([dash.page_container]), width={'size': 10, 'offset': 1})])

# Running the app.
if __name__ == '__main__':
    app.run_server(debug=True)
