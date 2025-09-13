#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
data = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
)

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Automobile Statistics Dashboard"

# Dropdown options and years list
dropdown_options = [
    {"label": "Yearly Statistics", "value": "Yearly Statistics"},
    {"label": "Recession Period Statistics", "value": "Recession Period Statistics"},
]
year_list = [i for i in range(1980, 2024)]

# App layout
app.layout = html.Div(
    [
        # TASK 2.1 Add title to the dashboard
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 24},
        ),
        # TASK 2.2: two dropdowns
        html.Div(
            [
                html.Label("Select Statistics:"),
                dcc.Dropdown(
                    id="dropdown-statistics",
                    options=dropdown_options,
                    placeholder="Select a report type",
                    style={"width": "80%", "padding": 3, "font-size": 20, "text-align-last": "center"},
                ),
            ]
        ),
        html.Div(
            dcc.Dropdown(
                id="select-year",
                options=[{"label": str(y), "value": y} for y in year_list],
                placeholder="Select year",
                disabled=True,  # initially disabled; toggled by callback
            )
        ),
        # TASK 2.3: output container (fixed style; removed undefined 'flex' name)
        html.Div(html.Div(id="output-container", className="chart-grid"), style={"padding": 10}),
    ]
)


# TASK 2.4: disable/enable year selector depending on statistics type
@app.callback(Output("select-year", "disabled"), Input("dropdown-statistics", "value"))
def update_input_container(selected_statistics):
    # enable the year dropdown only when Yearly Statistics is chosen
    if selected_statistics == "Yearly Statistics":
        return False
    return True


# Callback for plotting (all plotting code must be INSIDE this function)
@app.callback(
    Output("output-container", "children"),
    [Input("dropdown-statistics", "value"), Input("select-year", "value")],
)
def update_output_container(report_type, selected_year):
    # If user chooses Recession Period Statistics
    if report_type == "Recession Period Statistics":
        recession_data = data[data["Recession"] == 1]

        # Plot 1: Average automobile sales over recession years (line)
        yearly_rec = recession_data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, x="Year", y="Automobile_Sales", title="Average Automobile Sales (Recession Years)")
        )

        # Plot 2: Average number of vehicles sold by vehicle type (bar)
        average_sales = recession_data.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales, x="Vehicle_Type", y="Automobile_Sales", title="Average Sales by Vehicle Type (Recession)")
        )

        # Plot 3: Advertising expenditure share by vehicle type (pie)
        exp_rec = recession_data.groupby("Vehicle_Type")["Advertising_Expenditure"].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, names="Vehicle_Type", values="Advertising_Expenditure", title="Advertising Expenditure Share (Recession)")
        )

        # Plot 4: Effect of unemployment rate on vehicle type and sales (grouped bar)
        # (group by unemployment rate and vehicle type, take mean sales)
        unemp_data = (
            recession_data.groupby(["unemployment_rate", "Vehicle_Type"])["Automobile_Sales"]
            .mean()
            .reset_index()
        )
        R_chart4 = dcc.Graph(
            figure=px.bar(
                unemp_data,
                x="unemployment_rate",
                y="Automobile_Sales",
                color="Vehicle_Type",
                labels={"unemployment_rate": "Unemployment Rate", "Automobile_Sales": "Average Automobile Sales"},
                title="Effect of Unemployment Rate on Vehicle Type and Sales (Recession)",
            )
        )

        return [
            html.Div(
                className="chart-item",
                children=[html.Div(children=R_chart1), html.Div(children=R_chart2)],
                style={"display": "flex", "gap": "10px"},
            ),
            html.Div(
                className="chart-item",
                children=[html.Div(children=R_chart3), html.Div(children=R_chart4)],
                style={"display": "flex", "gap": "10px"},
            ),
        ]

    # TASK 2.6: Yearly Report Statistics
    elif report_type == "Yearly Statistics":
        if not selected_year:
            # ask the user to select a year if none chosen
            return html.Div("Please select a year from the dropdown to see Yearly Statistics.", style={"margin": 20})

        # ensure year is integer (dropdown gives numeric values)
        try:
            year = int(selected_year)
        except Exception:
            year = selected_year

        yearly_data = data[data["Year"] == year]

        if yearly_data.empty:
            return html.Div(f"No data available for year {year}.", style={"margin": 20})

        # Plot 1: Average automobile sales across all years (line)
        yas = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas, x="Year", y="Automobile_Sales", title="Average Automobile Sales Over the Years")
        )

        # Plot 2: Total monthly automobile sales for the selected year (line)
        mas = yearly_data.groupby("Month")["Automobile_Sales"].sum().reset_index().sort_values("Month")
        Y_chart2 = dcc.Graph(
            figure=px.line(mas, x="Month", y="Automobile_Sales", title=f"Total Monthly Automobile Sales in {year}")
        )

        # Plot 3: Average vehicles sold by vehicle type in the selected year (bar)
        avr_vdata = yearly_data.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata, x="Vehicle_Type", y="Automobile_Sales", title=f"Average Vehicles Sold by Type in {year}")
        )

        # Plot 4: Advertising expenditure by vehicle type in the selected year (pie)
        exp_data = yearly_data.groupby("Vehicle_Type")["Advertising_Expenditure"].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data, names="Vehicle_Type", values="Advertising_Expenditure", title=f"Advertising Expenditure by Type in {year}")
        )

        return [
            html.Div(
                className="chart-item",
                children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)],
                style={"display": "flex", "gap": "10px"},
            ),
            html.Div(
                className="chart-item",
                children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)],
                style={"display": "flex", "gap": "10px"},
            ),
        ]

    # default: nothing selected yet
    return html.Div("Choose a report type to view charts.", style={"margin": 20})


# Run the Dash app
if __name__ == "__main__":
    app.run(debug=True)
