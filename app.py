import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

# Carrega o dataset 
df = pd.read_csv('data/imdb.csv')

# Limpeza leve 
df = df.dropna(subset=['Genre', 'IMDb Rating', 'Year'])
df['Year'] = df['Year'].astype(int)

# Inicializa o app 
app = Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css'])
app.title = "IMDb Storytelling Dashboard"

# Layout 
app.layout = html.Div([
    html.Div([
        html.H1("🎬 IMDb Storytelling Dashboard", className="text-center mt-3 mb-4"),
        html.P("Explore tendências, notas e popularidade dos filmes ao longo dos anos.", className="text-center")
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
    ], className="row container mb-5"),

    html.Div([
        dcc.Graph(id='rating-distribution', className="col-md-6"),
        dcc.Graph(id='meta-over-time', className="col-md-6")
    ], className="row container"),

    html.Div([
        dcc.Graph(id='top-movies', className="col-md-12 mt-4")
    ], className="row container mb-5")
])

# Callbacks (interatividade) 
@app.callback(
    [Output('rating-distribution', 'figure'),
     Output('meta-over-time', 'figure'),
     Output('top-movies', 'figure')],
    [Input('genre-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_charts(selected_genre, selected_years):
    start, end = selected_years
    filtered_df = df[
        (df['Genre'] == selected_genre) &
        (df['Year'].between(start, end))
    ]

    # Distribuição das notas
    fig1 = px.histogram(
        filtered_df,
        x='IMDb Rating',
        nbins=20,
        title=f"Distribuição das notas ({selected_genre})",
        color_discrete_sequence=['#F4C430']
    )

    # Média de MetaScore por ano
    yearly = filtered_df.groupby('Year')['MetaScore'].mean().reset_index()
    fig2 = px.line(
        yearly,
        x='Year',
        y='MetaScore',
        title=f"Média de MetaScore ao longo dos anos ({selected_genre})",
        markers=True,
        color_discrete_sequence=['#1F77B4']
    )

    # Top 10 filmes mais bem avaliados
    top = filtered_df.nlargest(10, 'IMDb Rating')
    fig3 = px.bar(
        top,
        x='Title',
        y='IMDb Rating',
        title=f"Top 10 filmes ({selected_genre})",
        color='IMDb Rating',
        color_continuous_scale='Blues'
    )
    fig3.update_layout(xaxis={'categoryorder': 'total ascending'})

    return fig1, fig2, fig3


# --- Executa o servidor ---
if __name__ == '__main__':
    app.run(debug=False)
