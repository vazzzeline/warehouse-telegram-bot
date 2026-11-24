import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Загрузка данных из CSV
df = pd.read_csv('warehouse_data.csv')
df['date'] = pd.to_datetime(df['date'])

# Инициализация приложения
app = dash.Dash(__name__)

# Стили
colors = {
    'background': '#f0f2f5',
    'text': '#1a1a2e',
    'card': '#ffffff'
}

# Макет дашборда
app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '20px', 'fontFamily': 'Arial'}, children=[
    
    # Заголовок
    html.H1("Дашборд склада", style={'textAlign': 'center', 'color': colors['text']}),
    html.P("Анализ ключевых показателей: выручка, расходы, прибыль", 
           style={'textAlign': 'center', 'color': '#666'}),
    
    # Выпадающий список для выбора периода
    html.Div([
        html.Label("Выберите период анализа:"),
        dcc.Dropdown(
            id='period-dropdown',
            options=[
                {'label': 'Все данные', 'value': 'all'},
                {'label': 'Январь 2026', 'value': '2026-01'},
            ],
            value='all',
            style={'width': '300px'}
        )
    ], style={'margin': '20px 0'}),
    
    # Индикаторы (полоски состояния)
    html.Div(id='kpi-indicators', style={'display': 'flex', 'gap': '20px', 'margin': '20px 0'}),
    
    # График временного ряда
    html.Div([
        html.H3("Динамика доходов и расходов"),
        dcc.Graph(id='time-series')
    ], style={'backgroundColor': colors['card'], 'padding': '20px', 'borderRadius': '10px', 'margin': '20px 0'}),
    
    # Круговая диаграмма
    html.Div([
        html.H3("Структура расходов по категориям"),
        dcc.Graph(id='pie-chart')
    ], style={'backgroundColor': colors['card'], 'padding': '20px', 'borderRadius': '10px', 'margin': '20px 0'}),
    
    # Гистограмма
    html.Div([
        html.H3("Прибыль по категориям"),
        dcc.Graph(id='bar-chart')
    ], style={'backgroundColor': colors['card'], 'padding': '20px', 'borderRadius': '10px', 'margin': '20px 0'}),
    
    # Таблица
    html.Div([
        html.H3("Ключевые показатели"),
        dash_table.DataTable(
            id='data-table',
            columns=[
                {'name': 'Дата', 'id': 'date'},
                {'name': 'Операция', 'id': 'operation'},
                {'name': 'Категория', 'id': 'category'},
                {'name': 'Выручка', 'id': 'revenue'},
                {'name': 'Расходы', 'id': 'expenses'},
                {'name': 'Прибыль', 'id': 'profit'},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#1a1a2e', 'color': 'white', 'fontWeight': 'bold'},
        )
    ], style={'backgroundColor': colors['card'], 'padding': '20px', 'borderRadius': '10px', 'margin': '20px 0'}),
    
    # График рассеяния
    html.Div([
        html.H3("Корреляция прибыли и выручки"),
        dcc.Graph(id='scatter-plot')
    ], style={'backgroundColor': colors['card'], 'padding': '20px', 'borderRadius': '10px', 'margin': '20px 0'}),
])

# Колбэки для интерактивности
@app.callback(
    [Output('time-series', 'figure'),
     Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('data-table', 'data'),
     Output('scatter-plot', 'figure'),
     Output('kpi-indicators', 'children')],
    [Input('period-dropdown', 'value')]
)
def update_dashboard(period):
    # Фильтрация данных
    if period == 'all':
        filtered_df = df
    else:
        filtered_df = df[df['date'].dt.strftime('%Y-%m') == period]
    
    # График временного ряда
    fig1 = px.line(filtered_df, x='date', y=['revenue', 'expenses'], 
                   title='Динамика доходов и расходов',
                   labels={'value': 'Сумма (руб.)', 'date': 'Дата'})
    
    # Круговая диаграмма
    fig2 = px.pie(filtered_df, values='expenses', names='category', 
                  title='Структура расходов по категориям')
    
    # Гистограмма
    fig3 = px.bar(filtered_df, x='category', y='profit', 
                  title='Прибыль по категориям', color='category')
    
    # Таблица
    table_data = filtered_df.to_dict('records')
    
    # График рассеяния
    fig4 = px.scatter(filtered_df, x='revenue', y='profit', color='category',
                      title='Корреляция прибыли и выручки',
                      labels={'revenue': 'Выручка', 'profit': 'Прибыль'})
    
    # Индикаторы
    total_revenue = filtered_df['revenue'].sum()
    total_expenses = filtered_df['expenses'].sum()
    total_profit = filtered_df['profit'].sum()
    
    indicators = [
        html.Div([
            html.H4("Выручка"),
            html.H2(f"{total_revenue:,.0f} ₽", style={'color': '#2ecc71'})
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'flex': '1', 'textAlign': 'center'}),
        html.Div([
            html.H4("Расходы"),
            html.H2(f"{total_expenses:,.0f} ₽", style={'color': '#e74c3c'})
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'flex': '1', 'textAlign': 'center'}),
        html.Div([
            html.H4("Прибыль"),
            html.H2(f"{total_profit:,.0f} ₽", style={'color': '#3498db'})
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'flex': '1', 'textAlign': 'center'}),
    ]
    
    return fig1, fig2, fig3, table_data, fig4, indicators

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)