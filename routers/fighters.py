import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import unicodedata
import json
import os
import urllib.parse
import ast
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "projekty-434020-04c49456444d.json"
with open("psssst.json", "r", encoding="utf-8") as file:
    secrets = json.load(file)
SHEET_ID = secrets.get("SHEET_NAME")

def format_fighter_name(row):
    if pd.notna(row['Prezývka']) and row['Prezývka'].strip():
        return f"{row['Meno']} \"{row['Prezývka']}\" {row['Priezvisko']}"
    else:
        return f"{row['Meno']} {row['Priezvisko']}"

def get_fighter_names_and_images():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_ID).worksheet("Fighters")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(how='all')
    df['Fighter_Display_Name'] = df.apply(format_fighter_name, axis=1)
    # Prepare a tuple: (display_name, image_filename)
    fighters = []
    for _, row in df.iterrows():
        meno = str(row['Meno']).strip()
        priezvisko = str(row['Priezvisko']).strip()
        base_filename = f"{meno} {priezvisko}"
        image_filename = None
        for ext in ['jpg', 'png', 'webp']:
            candidate = f"{base_filename}.{ext}"
            if os.path.exists(os.path.join("images", "fighters", candidate)):
                image_filename = candidate
                break
        if not image_filename:
            image_filename = "default.jpg"  # fallback image
        fighters.append({"display_name": row['Fighter_Display_Name'], "image_filename": image_filename})
    return fighters

@router.get(
    "/fighters",
    summary="Fighters Page",
    description="This endpoint returns information about fighters."
)
async def fighters(request: Request):
    fighters = get_fighter_names_and_images()
    return templates.TemplateResponse(
        "fighters.html",
        {"request": request, "fighters": fighters}
    )

def normalize_string(s):
    normalized = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii').strip()
    return normalized

def extract_name_without_prezivka(fighter_name):
    parts = fighter_name.split('"')
    meno, priezvisko = parts[0].strip(), parts[-1].strip()
    return meno + ' ' + priezvisko

@router.get("/fighters/{fighter_name}")
async def fighter_detail(request: Request, fighter_name: str):
    import urllib.parse
    fighter_name = urllib.parse.unquote(fighter_name)

    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_ID).worksheet("Fighters")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(how='all')
    df['Fighter_Display_Name'] = df.apply(format_fighter_name, axis=1)



    # Normalize for matching
    def get_normalized_name(name):
        return normalize_string(name).lower()

    normalized_target = get_normalized_name(fighter_name)

    # Try to match full display name first
    df['Normalized_Display_Name'] = df['Fighter_Display_Name'].apply(get_normalized_name)
    selected_row = df[df['Normalized_Display_Name'] == normalized_target]

    # If not found, try matching just Meno + Priezvisko (no nickname)
    if selected_row.empty:
        df['Normalized_Meno_Priezvisko'] = (df['Meno'] + ' ' + df['Priezvisko']).apply(get_normalized_name)
        selected_row = df[df['Normalized_Meno_Priezvisko'] == normalized_target]

    if selected_row.empty:
        return templates.TemplateResponse("fighter_detail.html", {
            "request": request,
            "fighter_name": fighter_name,
            "not_found": True
        })

    selected_row = selected_row.iloc[0]
    # Stats
    wins = int(selected_row['W'])
    losses = int(selected_row['L'])
    draws = int(selected_row['D'])
    no_contests = int(selected_row['NO_CONTEST'])
    cancelled = int(selected_row['CANCEL'])
    win_ko_tko = int(selected_row['W_KO/TKO'])
    win_sub = int(selected_row['W_SUB'])
    win_dec = int(selected_row['W_DEC'])
    win_other = int(selected_row['W_OTHER'])
    loss_ko_tko = int(selected_row['L_KO/TKO'])
    loss_sub = int(selected_row['L_SUB'])
    loss_dec = int(selected_row['L_DEC'])
    loss_other = int(selected_row['L_OTHER'])

    total_wins = win_ko_tko + win_sub + win_dec + win_other
    total_losses = loss_ko_tko + loss_sub + loss_dec + loss_other

    win_ko_tko_perc = int((win_ko_tko / total_wins * 100) if total_wins > 0 else 0)
    win_sub_perc = int((win_sub / total_wins * 100) if total_wins > 0 else 0)
    win_dec_perc = int((win_dec / total_wins * 100) if total_wins > 0 else 0)
    win_other_perc = int((win_other / total_wins * 100) if total_wins > 0 else 0)
    loss_ko_tko_perc = int((loss_ko_tko / total_losses * 100) if total_losses > 0 else 0)
    loss_sub_perc = int((loss_sub / total_losses * 100) if total_losses > 0 else 0)
    loss_dec_perc = int((loss_dec / total_losses * 100) if total_losses > 0 else 0)
    loss_other_perc = int((loss_other / total_losses * 100) if total_losses > 0 else 0)

    # Find photo (use your convention)
    meno = str(selected_row['Meno']).strip()
    priezvisko = str(selected_row['Priezvisko']).strip()
    photo_url = None
    for ext in ['jpg', 'png', 'webp']:
        candidate = f"/images/fighters/{meno} {priezvisko}.{ext}"
        if os.path.exists(f"images/fighters/{meno} {priezvisko}.{ext}"):
            photo_url = candidate
            break
    if not photo_url:
        photo_url = "/images/fighters/default.jpg"

    # Load fights data
    sheet_fights = gc.open_by_key(SHEET_ID).worksheet("Zápasy")
    data_fights = sheet_fights.get_all_records()
    df_fights = pd.DataFrame(data_fights)
    df_fights = df_fights.loc[:, ~df_fights.columns.str.contains('^Unnamed')]
    df_fights = df_fights.dropna(how='all')

    # Filter fights for this fighter
    fighter_is_winner = df_fights['W'].astype(str).str.contains(fighter_name, na=False)
    fighter_is_loser = df_fights['L'].astype(str).str.contains(fighter_name, na=False)
    relevant_fights = df_fights[fighter_is_winner | fighter_is_loser]

    display_name = selected_row['Fighter_Display_Name']

    def make_fighter_link(name):
        url = "/fighters/" + urllib.parse.quote(name)
        return f'<a class="fighter-link" href="{url}">{name}</a>'

    # Prepare fights for table
    fight_results = []
    for _, row in relevant_fights.iterrows():
        if row['NO_CONTEST'] == 1:
            result = 'NO_CONTEST'
        elif row['CANCELLED'] == 1:
            result = 'CANCELLED'
        elif row['DRAW'] == 1:
            result = 'DRAW'
        elif fighter_name in row['W']:
            result = 'W'
        elif fighter_name in row['L']:
            result = 'L'
        else:
            result = ''
        opponent = row['L'] if display_name in row['W'] else row['W']

        # If opponent is a string that looks like a list, convert it
        if isinstance(opponent, str) and opponent.startswith("[") and opponent.endswith("]"):
            try:
                names = ast.literal_eval(opponent)
                if isinstance(names, list):
                    opponent_links = " and ".join(make_fighter_link(n.strip()) for n in names)
                else:
                    opponent_links = make_fighter_link(opponent)
            except Exception:
                opponent_links = make_fighter_link(opponent)
        elif isinstance(opponent, list):
            opponent_links = " and ".join(make_fighter_link(n.strip()) for n in opponent)
        else:
            opponent_links = make_fighter_link(opponent)

        # Make tournament a link
        tournament_url = "/tournaments/" + urllib.parse.quote(str(row['Nazov_turnaj']))
        tournament_html = f'<a class="tournament-link" href="{tournament_url}">{row["Nazov_turnaj"]}</a>'

        fight_results.append({
            "Result": result,
            "Opponent": opponent_links,
            "Event": tournament_html,
            "Method": row['Metoda'],
            "Round": row['Kolo'],
            "Time": row['Čas'],
            "Style": row['Disciplina']
        })

    return templates.TemplateResponse("fighter_detail.html", {
        "request": request,
        "fighter_name": fighter_name,
        "photo_url": photo_url,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "no_contests": no_contests,
        "cancelled": cancelled,
        "win_ko_tko": win_ko_tko,
        "win_sub": win_sub,
        "win_dec": win_dec,
        "win_other": win_other,
        "loss_ko_tko": loss_ko_tko,
        "loss_sub": loss_sub,
        "loss_dec": loss_dec,
        "loss_other": loss_other,
        "win_ko_tko_perc": win_ko_tko_perc,
        "win_sub_perc": win_sub_perc,
        "win_dec_perc": win_dec_perc,
        "win_other_perc": win_other_perc,
        "loss_ko_tko_perc": loss_ko_tko_perc,
        "loss_sub_perc": loss_sub_perc,
        "loss_dec_perc": loss_dec_perc,
        "loss_other_perc": loss_other_perc,
        "fight_results": fight_results,
        "not_found": False
    })

import ast
import urllib.parse

def make_fighter_links(cell):
    # Convert string representation of list to actual list if needed
    if isinstance(cell, str) and cell.startswith("[") and cell.endswith("]"):
        try:
            names = ast.literal_eval(cell)
        except Exception:
            names = [cell]
    elif isinstance(cell, list):
        names = cell
    else:
        names = [cell]
    # Create links for each name
    links = [
        f'<a href="/fighters/{urllib.parse.quote(str(name))}" class="fighter-link">{name}</a>'
        for name in names
    ]
    return " and ".join(links)