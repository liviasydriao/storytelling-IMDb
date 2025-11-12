import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

# --- Carrega o dataset ---
df = pd.read_csv('data/imdb.csv')
df = df.dropna(subset=['Genre', 'IMDb Rating', 'Year'])
df['Year'] = df['Year'].astype(int)

# --- Define o ano mínimo de dados válidos (1957) ---
MIN_YEAR = 1957
df = df[df['Year'] >= MIN_YEAR]

# --- Inicializa o app ---
app = Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css'])
app.title = "IMDb Storytelling Dashboard"

# --- Layout ---
app.layout = html.Div([
    html.Div([
        html.H1("🎬 IMDb Storytelling Dashboard", className="text-center mt-3 mb-2 fw-bold"),
        html.P("Explore tendências, notas e popularidade dos filmes ao longo dos anos.", className="text-center mb-4"),
        html.Div([
            html.Button("🌞/🌙 Modo Claro/Escuro", id="theme-toggle", n_clicks=0, className="btn btn-outline-dark")
        ], className="text-center mb-4")
    ], className="container"),

    html.Div([
        html.Div([
            html.Label("Selecione o gênero:"),
            dcc.Dropdown(
                options=[{'label': g, 'value': g} for g in sorted(df['Genre'].unique())],
                value='Action',
                id='genre-dropdown',
                clearable=False
            )
        ], className="col-md-4"),

        html.Div([
            html.Label("Selecione o intervalo de anos:"),
            dcc.RangeSlider(
                min=df['Year'].min(),
                max=df['Year'].max(),
                step=1,
                value=[2010, 2024],
                marks={y: str(y) for y in range(df['Year'].min(), df['Year'].max()+1, 5)},
                id='year-slider'
            )
        ], className="col-md-8")
    ], className="row container mb-4"),

    html.Div(id='summary-container', className="text-center mb-4 fw-semibold"),

    dcc.Loading([
        html.Div([
            dcc.Graph(id='rating-distribution', className="col-md-6"),
            dcc.Graph(id='meta-over-time', className="col-md-6")
        ], className="row container"),

        html.Div([
            dcc.Graph(id='top-movies', className="col-md-12 mt-4"),
            dcc.Graph(id='movies-per-year', className="col-md-12 mt-4")
        ], className="row container mb-5")
    ])
])

# --- Callbacks ---
@app.callback(
    [Output('rating-distribution', 'figure'),
     Output('meta-over-time', 'figure'),
     Output('top-movies', 'figure'),
     Output('movies-per-year', 'figure'),
     Output('summary-container', 'children')],
    [Input('genre-dropdown', 'value'),
     Input('year-slider', 'value'),
     Input('theme-toggle', 'n_clicks')]
)
def update_charts(selected_genre, selected_years, n_clicks):
    start, end = selected_years
    theme = "plotly_dark" if n_clicks % 2 else "plotly_white"
    filtered_df = df[(df['Genre'] == selected_genre) & (df['Year'].between(start, end))]

    avg_rating = filtered_df['IMDb Rating'].mean()
    avg_meta = filtered_df['MetaScore'].mean()

    summary = f"Média IMDb Rating: {avg_rating:.2f} | Média MetaScore: {avg_meta:.2f}"

    fig1 = px.histogram(filtered_df, x='IMDb Rating', nbins=20,
                        title=f"Distribuição das notas ({selected_genre})", template=theme)
    fig2 = px.line(filtered_df.groupby('Year')['MetaScore'].mean().reset_index(),
                   x='Year', y='MetaScore', title=f"Média de MetaScore ao longo dos anos ({selected_genre})",
                   markers=True, template=theme)
    top = filtered_df.nlargest(10, 'IMDb Rating')
    fig3 = px.bar(top, x='Title', y='IMDb Rating', title=f"Top 10 filmes ({selected_genre})",
                  color='IMDb Rating', color_continuous_scale='Blues', template=theme)
    fig3.update_layout(xaxis={'categoryorder': 'total ascending'})

    per_year = filtered_df.groupby('Year').size().reset_index(name='Count')
    fig4 = px.area(per_year, x='Year', y='Count', title=f"Quantidade de filmes lançados ({selected_genre})", template=theme)

    return fig1, fig2, fig3, fig4, summary


# --- Executa o servidor ---
if __name__ == '__main__':
    app.run(debug=False)
