from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import urllib.parse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Google Sheets setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "projekty-434020-04c49456444d.json"  # Place your credentials file in the project root
with open("psssst.json", "r", encoding="utf-8") as file:
    secrets = json.load(file)

# Assign the value to a variable
SHEET_NAME = secrets.get("SHEET_NAME")
def get_tournaments():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_NAME).worksheet("Turnaje")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def get_matches():
    # Similar to your get_tournaments, but for matches
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_NAME).worksheet("Zápasy")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def get_tournament_info(selected_turnaj):
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_NAME).worksheet("Turnaje")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    ttt = df[df['Nazov_turnaj'] == selected_turnaj]
    if not ttt.empty:
        return {
            "hala": ttt['Hala'].values[0],
            "miesto": ttt['Miesto'].values[0],
            "nazov_neoficialny": ttt['Nazov_neoficialny'].values[0]
        }
    return {}

def convert_list_string_to_string(value):
    if isinstance(value, str) and '[' in value and ']' in value:
        value = value[1:-1]
        elements = value.split(',')
        return [elem.strip().strip("'\"") for elem in elements]
    return [value]

def df_to_html_table(df):
    fighter_columns_style = "width: 15%; text-align: center;"
    narrow_columns_style = "width: 7%; text-align: center;"
    column_styles = {
        'Fighter 1': fighter_columns_style,
        'Fighter 2': fighter_columns_style,
        'Method': narrow_columns_style,
        'Round': narrow_columns_style,
        'Time': narrow_columns_style,
        'Disciplina': narrow_columns_style,
        'Vaha': narrow_columns_style
    }
    html = "<table border='1' style='border-collapse: collapse;'>"
    html += "<thead><tr>"
    for column in df.columns:
        if column not in ['Winner', 'Loser']:
            html += f"<th style='{column_styles.get(column, narrow_columns_style)}'>{column}</th>"
    html += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        fighter_1_list = convert_list_string_to_string(row['Fighter 1'])
        fighter_2_list = convert_list_string_to_string(row['Fighter 2'])
        winner_list = convert_list_string_to_string(row['Winner'])
        loser_list = convert_list_string_to_string(row['Loser'])
        if 'DRAW' in winner_list:
            result_type = 'DRAW'
        elif 'CANCELLED' in winner_list or 'NC' in winner_list:
            result_type = 'CANCELLED'
        else:
            result_type = None
        fighter_1_colored = []
        fighter_2_colored = []
        for fighter in fighter_1_list:
            color = 'black'
            if result_type == 'DRAW':
                color = 'yellow'
            elif result_type in ['CANCELLED', 'NC']:
                color = 'grey'
            elif fighter in winner_list:
                color = 'green'
            elif fighter in loser_list:
                color = 'red'
            fighter_url = f"/fighters/{urllib.parse.quote(fighter)}"
            fighter_1_colored.append(f"<a href='{fighter_url}' style='color: {color}; text-decoration: none;'>{fighter}</a>")
        for fighter in fighter_2_list:
            color = 'black'
            if result_type == 'DRAW':
                color = 'yellow'
            elif result_type in ['CANCELLED', 'NC']:
                color = 'grey'
            elif fighter in winner_list:
                color = 'green'
            elif fighter in loser_list:
                color = 'red'
            fighter_url = f"/fighters/{urllib.parse.quote(fighter)}"
            fighter_2_colored.append(f"<a href='{fighter_url}' style='color: {color}; text-decoration: none;'>{fighter}</a>")
        if ' and ' in ' '.join(fighter_1_list) and ' and ' in ' '.join(fighter_2_list):
            fighters = list(set(fighter_1_list + fighter_2_list))
            winners = set(winner_list)
            losers = set(loser_list)
            fighter_1_colored = []
            fighter_2_colored = []
            for fighter in fighters:
                color = 'black'
                if fighter in winners:
                    color = 'green'
                elif fighter in losers:
                    color = 'red'
                fighter_url = f"/fighters/{urllib.parse.quote(fighter)}"
                fighter_1_colored.append(f"<a href='{fighter_url}' style='color: {color}; text-decoration: none;'>{fighter}</a>")
                fighter_2_colored.append(f"<a href='{fighter_url}' style='color: {color}; text-decoration: none;'>{fighter}</a>")
            fighter_1 = ' and '.join(fighter_1_colored)
            fighter_2 = ' and '.join(fighter_2_colored)
        else:
            fighter_1 = ' and '.join(fighter_1_colored)
            fighter_2 = ' and '.join(fighter_2_colored)
        try:
            rr = int(row['Round'])
        except:
            rr = None
        html += "<tr>"
        html += f"<td style='{fighter_columns_style}'>{fighter_1}</td>"
        html += f"<td style='{fighter_columns_style}'>{fighter_2}</td>"
        html += f"<td style='{narrow_columns_style}'>{row['Method']}</td>"
        html += f"<td style='{narrow_columns_style}'>{rr}</td>"
        html += f"<td style='{narrow_columns_style}'>{row['Time']}</td>"
        html += f"<td style='{narrow_columns_style}'>{row['Disciplina']}</td>"
        html += f"<td style='{narrow_columns_style}'>{row['Vaha']}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html

@router.get(
    "/tournaments",
    summary="Tournaments Page",
    description="This endpoint returns information about tournaments.",
    response_class=HTMLResponse
)
async def tournaments(request: Request):
    df = get_tournaments()
    tournaments = df["Nazov_turnaj"].tolist()
    # Pass tournaments to template for button rendering
    return templates.TemplateResponse(
        "tournaments.html",
        {"request": request, "tournaments": tournaments}
    )

@router.get("/tournaments/{tournament_name}", response_class=HTMLResponse)
async def tournament_detail(request: Request, tournament_name: str):
    df_matches = get_matches()
    # Filter matches for this tournament
    df_filtered = df_matches[df_matches['Nazov_turnaj'] == tournament_name]
    if df_filtered.empty:
        html_table = "<p>No matches found for this tournament.</p>"
    else:
        # Process data to handle edge cases
        def process_fight_result(row):
            if row['DRAW'] == 1:
                return 'DRAW', 'DRAW'
            elif row['CANCELLED'] == 1:
                return 'CANCELLED', 'CANCELLED'
            elif row['NO_CONTEST'] == 1:
                return 'NC', 'NC'
            else:
                return row['W'], row['L']
        df_filtered[['Winner', 'Loser']] = df_filtered.apply(
            lambda row: pd.Series(process_fight_result(row)), axis=1
        )
        result_table = pd.DataFrame({
            'Fighter 1': df_filtered['Zapasnik1'],
            'Fighter 2': df_filtered['Zapasnik2'],
            'Winner': df_filtered['Winner'],
            'Loser': df_filtered['Loser'],
            'Method': df_filtered['Metoda'],
            'Round': df_filtered['Kolo'],
            'Time': df_filtered['Čas'],
            'Disciplina': df_filtered['Disciplina'],
            'Vaha': df_filtered['Vaha']
        })
        html_table = df_to_html_table(result_table)
    info = get_tournament_info(tournament_name)
    return templates.TemplateResponse(
        "tournament_detail.html",
        {
            "request": request,
            "tournament_name": tournament_name,
            "hala": info.get("hala", ""),
            "miesto": info.get("miesto", ""),
            "nazov_neoficialny": info.get("nazov_neoficialny", ""),
            "html_table": html_table
        }
    )