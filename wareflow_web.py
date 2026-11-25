import os
from datetime import datetime
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output, State, ctx

DATA_FILE = "warehouse_data.csv"
BOT_LINK = "https://t.me"
DASH_URL = "http://127.0.0"

def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["date", "operation", "category", "revenue", "expenses", "profit", "quantity"])
        df.to_csv(DATA_FILE, index=False)
    return pd.read_csv(DATA_FILE)

app = Dash(__name__, title="WAREFLOW — Мобильный и веб-клиент WMS", suppress_callback_exceptions=True)

CARD = {
    "backgroundColor": "#FFFFFF",
    "borderRadius": "16px",
    "padding": "18px 20px",
    "boxShadow": "0 2px 12px rgba(15, 41, 47, 0.06)",
    "border": "1px solid #EAECEF"
}

def kpi_box(icon, bg_icon, color_icon, title, value, subtitle, val_color="#0F292F"):
    return html.Div(style={**CARD, "flex": "1", "minWidth": "210px"}, children=[
        html.Div(icon, style={
            "width": "38px", "height": "38px", "borderRadius": "10px",
            "backgroundColor": bg_icon, "color": color_icon,
            "display": "flex", "alignItems": "center", "justifyContent": "center",
            "fontSize": "18px", "fontWeight": "bold", "marginBottom": "14px"
        }),
        html.Div(title, style={"color": "#6C757D", "fontSize": "13px", "marginBottom": "4px"}),
        html.Div(value, style={"color": val_color, "fontSize": "26px", "fontWeight": "800", "lineHeight": "1.2"}),
        html.Div(subtitle, style={"color": "#9AA0A6", "fontSize": "12px", "marginTop": "4px"})
    ])

header_block = html.Div(style={"backgroundColor": "#0A2328", "color": "#FFF", "padding": "14px 28px"}, children=[
    html.Div(style={"maxWidth": "1160px", "margin": "0 auto", "display": "flex", "justifyContent": "space-between", "alignItems": "center", "flexWrap": "wrap", "gap": "12px"}, children=[
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "12px"}, children=[
            html.Div("W", style={"backgroundColor": "#1DB978", "color": "#FFF", "width": "34px", "height": "34px", "borderRadius": "9px", "display": "flex", "alignItems": "center", "justifyContent": "center", "fontWeight": "bold", "fontSize": "18px"}),
            html.Span("WAREFLOW", style={"fontSize": "19px", "fontWeight": "700", "letterSpacing": "1px"}),
            html.Span("08:00–20:00", style={"backgroundColor": "#14353C", "padding": "5px 12px", "borderRadius": "8px", "fontSize": "13px", "marginLeft": "8px"}),
            html.Span("● Всё по плану", style={"backgroundColor": "#E6F7EF", "color": "#169B62", "padding": "4px 12px", "borderRadius": "20px", "fontSize": "12px", "fontWeight": "600"})
        ]),
        html.Div(style={"display": "flex", "gap": "10px"}, children=[
            html.A("🤖 Telegram-бот", href=BOT_LINK, target="_blank", style={"backgroundColor": "#2481CC", "color": "#FFF", "padding": "8px 14px", "borderRadius": "10px", "textDecoration": "none", "fontSize": "13px", "fontWeight": "600"}),
            html.A("📊 Отдельный дашборд (ЛР №5)", href=DASH_URL, target="_blank", style={"backgroundColor": "#163B42", "color": "#FFF", "padding": "8px 14px", "borderRadius": "10px", "textDecoration": "none", "fontSize": "13px", "border": "1px solid #2A5760"})
        ])
    ])
])

NAV_ITEMS = [
    ("nav-home", "⊞ Главная"),
    ("nav-in", "📥 Приёмка"),
    ("nav-addr", "🗺 Адреса"),
    ("nav-pick", "📦 Сборка"),
    ("nav-out", "🚚 Отгрузка"),
    ("nav-inv", "📋 Учёт"),
]

footer_nav = html.Div(
    id="footer-bar",
    style={"position": "fixed", "bottom": "0", "left": "0", "right": "0", "backgroundColor": "#FFFFFF", "borderTop": "1px solid #E2E6EA", "padding": "8px 0", "display": "flex", "justifyContent": "center", "gap": "16px", "zIndex": "100"},
    children=[
        html.Button(label, id=btn_id, n_clicks=0, style={"border": "none", "background": "transparent", "fontSize": "14px", "fontWeight": "600", "cursor": "pointer", "padding": "6px 14px", "borderRadius": "8px", "color": "#6C757D"})
        for btn_id, label in NAV_ITEMS
    ]
)
def render_operation_form(default_op="Приёмка", title_text="➕ Регистрация операции в базе"):
    return html.Div(style=CARD, children=[
        html.Div(title_text, style={"fontSize": "16px", "fontWeight": "700", "color": "#0F292F", "marginBottom": "12px"}),
        dcc.Dropdown(id="op", options=["Приёмка", "Отгрузка", "Инвентаризация"], value=default_op, clearable=False, style={"marginBottom": "10px"}),
        dcc.Dropdown(id="cat", options=["Электроника", "Одежда", "Продукты"], value="Электроника", clearable=False, style={"marginBottom": "10px"}),
        html.Div(style={"display": "flex", "gap": "8px", "marginBottom": "12px"}, children=[
            dcc.Input(id="qty", type="number", value=10, placeholder="Кол-во", style={"width": "33%", "padding": "8px", "borderRadius": "8px", "border": "1px solid #DCE1E5"}),
            dcc.Input(id="rev", type="number", value=50000, placeholder="Выручка", style={"width": "33%", "padding": "8px", "borderRadius": "8px", "border": "1px solid #DCE1E5"}),
            dcc.Input(id="exp", type="number", value=20000, placeholder="Расходы", style={"width": "33%", "padding": "8px", "borderRadius": "8px", "border": "1px solid #DCE1E5"})
        ]),
        html.Button("Выполнить операцию", id="btn", n_clicks=0, style={"width": "100%", "padding": "11px", "backgroundColor": "#1DB978", "color": "#FFF", "border": "none", "borderRadius": "10px", "fontWeight": "700", "cursor": "pointer"}),
        html.Div(id="msg", style={"marginTop": "8px", "color": "#169B62", "fontSize": "13px", "fontWeight": "600"})
    ])

def render_addresses_tab():
    zones = [
        ("Зона A • Электроника", "Стеллаж A-01 → Ячейка 04", "Заполнено: 82% (FIFO)", "#EBF3FF", "#2481CC"),
        ("Зона B • Одежда и текстиль", "Стеллаж B-12 → Ячейка 09", "Заполнено: 64% (Свободно 14 мест)", "#E6F7EF", "#1DB978"),
        ("Зона C • Продукты (Терморежим)", "Стеллаж C-03 → Ячейка 01", "Заполнено: 91% (Контроль FEFO)", "#FFF3E0", "#E67E22"),
    ]
    return html.Div(style={"display": "flex", "flexDirection": "column", "gap": "16px"}, children=[
        html.H3("🗺 Топология адресного хранения склада (зона → стеллаж → ячейка)", style={"margin": "0", "color": "#0F292F"}),
        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={**CARD, "flex": "1", "minWidth": "280px"}, children=[
                html.Span("Активная ячейка", style={"backgroundColor": bg, "color": col, "padding": "4px 10px", "borderRadius": "8px", "fontSize": "12px", "fontWeight": "700"}),
                html.H4(title, style={"margin": "12px 0 6px", "color": "#0F292F"}),
                html.Div(loc, style={"fontSize": "14px", "fontWeight": "600", "color": "#495057", "marginBottom": "6px"}),
                html.Div(status, style={"fontSize": "13px", "color": "#6C757D"})
            ]) for title, loc, status, bg, col in zones
        ])
    ])

def render_picking_tab():
    orders = [
        ("Заказ МСК-1842", "Маршрут: A-01-04 → B-12-09", "Собрано 8 из 12 позиций", "В работе"),
        ("Заказ ХБР-0915", "Маршрут: C-03-01 → Зона упаковки", "Собрано 5 из 5 позиций", "Готов к отгрузке"),
        ("Заказ КМС-4410", "Маршрут: A-02-01 → A-04-03", "Ожидает назначения кладовщика", "В очереди"),
    ]
    return html.Div(style=CARD, children=[
        html.H3("📦 Маршрутные листы сборки заказов", style={"marginTop": "0", "color": "#0F292F"}),
        html.Div(style={"display": "flex", "flexDirection": "column", "gap": "12px"}, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "12px", "backgroundColor": "#F8F9FA", "borderRadius": "12px"}, children=[
                html.Div([
                    html.Div(oid, style={"fontWeight": "700", "fontSize": "15px", "color": "#0F292F"}),
                    html.Div(f"{route} • {prog}", style={"fontSize": "13px", "color": "#6C757D"})
                ]),
                html.Span(st, style={"backgroundColor": "#E6F7EF", "color": "#169B62", "padding": "5px 12px", "borderRadius": "12px", "fontSize": "12px", "fontWeight": "700"})
            ]) for oid, route, prog, st in orders
        ])
    ])
app.layout = html.Div(style={"backgroundColor": "#F5F7F8", "minHeight": "100vh", "fontFamily": "Segoe UI, Roboto, Arial, sans-serif", "paddingBottom": "75px"}, children=[
    dcc.Store(id="active-tab", data="nav-home"),
    dcc.Interval(id="timer", interval=3000, n_intervals=0),
    header_block,
    html.Div(id="page-content", style={"maxWidth": "1160px", "margin": "22px auto", "padding": "0 18px"}),
    footer_nav
])

@app.callback(
    [Output("active-tab", "data")] + [Output(btn_id, "style") for btn_id, _ in NAV_ITEMS],
    [Input(btn_id, "n_clicks") for btn_id, _ in NAV_ITEMS],
    State("active-tab", "data")
)
def switch_tab(*args):
    current = args[-1]
    triggered = ctx.triggered_id
    active = triggered if triggered in [b[0] for b in NAV_ITEMS] else current

    styles = []
    for btn_id, _ in NAV_ITEMS:
        if btn_id == active:
            styles.append({"border": "none", "background": "#E6F7EF", "fontSize": "14px", "fontWeight": "700", "cursor": "pointer", "padding": "6px 14px", "borderRadius": "8px", "color": "#169B62"})
        else:
            styles.append({"border": "none", "background": "transparent", "fontSize": "14px", "fontWeight": "600", "cursor": "pointer", "padding": "6px 14px", "borderRadius": "8px", "color": "#6C757D"})
    return [active] + styles

@app.callback(
    Output("page-content", "children"),
    [Input("active-tab", "data"), Input("timer", "n_intervals")]
)
def render_page(tab, n_intervals):
    df = load_data()
    total_ops = len(df)
    in_qty = int(df[df["operation"] == "Приёмка"]["quantity"].sum()) if not df.empty else 0
    out_qty = int(df[df["operation"] == "Отгрузка"]["quantity"].sum()) if not df.empty else 0
    prof = df["profit"].sum() if not df.empty else 0

    if tab == "nav-addr":
        return render_addresses_tab()
    if tab == "nav-pick":
        return render_picking_tab()

    if tab in ["nav-in", "nav-out", "nav-inv"]:
        op_map = {"nav-in": ("Приёмка", "📥 Приёмка товара по накладным (ТОРГ-12)"), "nav-out": ("Отгрузка", "🚚 Оформление отгрузки заказов"), "nav-inv": ("Инвентаризация", "📋 Учёт и сверка остатков (Инвентаризация)")}
        op_val, heading = op_map[tab]
        sub_df = df if tab == "nav-inv" else df[df["operation"] == op_val]
        return html.Div(style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "340px"}, children=[render_operation_form(op_val, heading)]),
            html.Div(style={**CARD, "flex": "1.6", "minWidth": "400px"}, children=[
                html.H4(f"Журнал раздела «{op_val}»", style={"marginTop": "0", "color": "#0F292F"}),
                dash_table.DataTable(data=sub_df.iloc[::-1].to_dict("records"), page_size=8, style_header={"backgroundColor": "#0A2328", "color": "#FFF"}, style_cell={"textAlign": "left", "padding": "8px", "fontSize": "13px"})
            ])
        ])

    # Главный экран (nav-home)
    cards = html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "22px"}, children=[
        kpi_box("📦", "#EBF3FF", "#2481CC", "Всего записей (SKU)", f"{total_ops}", "+синхронизация с ботом"),
        kpi_box("↓", "#E6F7EF", "#1DB978", "Поступило (Приёмка)", f"{in_qty} шт.", "оприходовано на склад"),
        kpi_box("↑", "#EBF3FF", "#2481CC", "Отгружено (Отгрузка)", f"{out_qty} шт.", "передано в доставку"),
        kpi_box("✓", "#FFF4E5", "#E67E22", "Чистая прибыль", f"{prof:,.0f} ₽".replace(",", " "), "Цель ≥ 99% точности", "#1DB978")
    ])

    fig = px.bar(df.groupby("category", as_index=False)["profit"].sum(), x="category", y="profit", color="category", color_discrete_sequence=["#0A2328", "#1DB978", "#2481CC"]) if not df.empty else px.bar()
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False, plot_bgcolor="#FFF")

    return html.Div([
        cards,
        html.Div(style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "340px"}, children=[render_operation_form("Приёмка", "➕ Быстрая операция")]),
            html.Div(style={"flex": "1.5", "minWidth": "400px", "display": "flex", "flexDirection": "column", "gap": "16px"}, children=[
                html.Div(style=CARD, children=[
                    html.Div("📊 Динамика прибыли по категориям ТМЦ", style={"fontSize": "16px", "fontWeight": "700", "color": "#0F292F", "marginBottom": "8px"}),
                    dcc.Graph(figure=fig, style={"height": "210px"}, config={"displayModeBar": False})
                ]),
                html.Div(style=CARD, children=[
                    html.Div("📋 Последние операции (синхронизировано с ботом)", style={"fontSize": "16px", "fontWeight": "700", "color": "#0F292F", "marginBottom": "8px"}),
                    dash_table.DataTable(data=df.iloc[::-1].to_dict("records"), page_size=5, style_header={"backgroundColor": "#0A2328", "color": "#FFF"}, style_cell={"textAlign": "left", "padding": "8px", "fontSize": "13px"})
                ])
            ])
        ])
    ])

@app.callback(
    Output("msg", "children"),
    Input("btn", "n_clicks"),
    [State("op", "value"), State("cat", "value"), State("qty", "value"), State("rev", "value"), State("exp", "value")],
    prevent_initial_call=True
)
def save_op(n_clicks, op, cat, qty, rev, exp):
    if not n_clicks:
        return ""
    df = load_data()
    q, r, e = int(qty or 1), float(rev or 0), float(exp or 0)
    row = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "operation": op, "category": cat, "revenue": r, "expenses": e, "profit": r - e, "quantity": q}])
    df = pd.concat([df, row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return f"✅ Операция «{op}» ({cat}, {q} шт.) записана!"

if __name__ == "__main__":
    print("Веб-приложение WAREFLOW запущено: http://127.0.0")
    app.run(debug=False, port=8051)
