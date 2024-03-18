from bs4 import BeautifulSoup
import cloudscraper
from time import sleep, time
import pandas as pd


# Define a custom function to convert market value strings to float values
def convert_market_value(value):
    if isinstance(value, str):
        print("Original value:", value)  # Debug print
        value = value.replace('€', '')  # Remove euro sign
        if value.endswith('k'):
            value = int(value[:-1]) * 1000  # Convert thousands to float
        elif value.endswith('m'):
            value = int(value[:-1]) * 1e6  # Convert millions to float
        else:
            try:
                value = int(value)
            except ValueError:
                value = 0  # Debug print
    return value



def scrape_transfermarkt_data():


    urls = ['https://www.transfermarkt.com/st-patricks-athletic/kader/verein/1189/saison_id/2023/plus/1',
            'https://www.transfermarkt.com/shamrock-rovers/kader/verein/3258/saison_id/2023/plus/1',
            'https://www.transfermarkt.com/bohemian-football-club/kader/verein/9211/saison_id/2023/plus/1',
            'https://www.transfermarkt.com/derry-city/kader/verein/920/saison_id/2023/plus/1',
            'https://www.transfermarkt.com/dundalk-fc/kader/verein/6066/saison_id/2023/plus/1',
            'https://www.transfermarkt.com/sligo-rovers/kader/verein/8780/saison_id/2023/plus/1',
            'https://www.transfermarkt.com/shelbourne-fc/kader/verein/3909/saison_id/2023/plus/1',
            'https://www.transfermarkt.com/waterford-fc/kader/verein/7609/saison_id/2023/plus/1',
            'https://www.transfermarkt.com/galway-united-fc/kader/verein/42394/saison_id/2023/plus/1',
            'https://www.transfermarkt.com/drogheda-united-fc/kader/verein/4277/saison_id/2023/plus/1']

    scraper = cloudscraper.create_scraper()

    all_players = []

    for url in urls:

        info = scraper.get(url)
        # player market values
        soup = BeautifulSoup(info.text, "html.parser")
        # Find all <td> elements with class 'rechts hauptlink'
        td_elements = soup.select('td.rechts')

        # Extract text values and insert null where not present
        player_market_values = []

        for td in td_elements:
            if td.a:  # Check if <a> tag exists
                value = td.a.get_text(strip=True)
            else:
                value = 'null'
            player_market_values.append(value)

        # team name

        team_name = soup.select('div[class="data-header__headline-container"]')
        squad_name = [td.get_text(strip=True) if td is not None else 'null' for td in team_name]

        # player names

        player_elements = soup.select('td.hauptlink:not(.rechts)')

        player_names = []
        for td in player_elements:
            if td.a:  # Check if <a> tag exists
                value = td.a.get_text(strip=True)
            else:
                value = 'null'
            player_names.append(value)

        # positions

        positions = soup.select('table[class="inline-table"]')
        posititon_values = [p.find_all('td')[-1].get_text(strip=True) for p in positions]

        # player info

        player_info_stats = soup.select('td.zentriert:not(.rueckennummer)')

        player_data = [td.get_text(strip=True) if td is not None else 'null' for td in player_info_stats]

        # last club

        player_signed_from = soup.select('td.zentriert img[class!=flaggenrahmen]')

        player_previous_clubs = [td['title'] if td is not None else 'null' for td in player_signed_from]

        # Create a list to store player information
        players = []

        # Iterate through the data in chunks of 8 (assuming each player has 8 pieces of information)
        for i in range(0, len(player_data), 7):
            player_info = player_data[i:i + 7]  # Get data for a single player
            player_dict = {
                'name': None,
                'position': None,
                'club': None,
                'birthdate': player_info[0] if player_info[0] else None,
                'height': player_info[2] if player_info[2] else None,
                'foot': player_info[3] if player_info[3] else 'Unknown',
                'joined': player_info[4] if player_info[4] else None,
                'signed_from': player_info[5] if player_info[5] else None,
                'contract': player_info[6] if player_info[6] else None,
                'market_value': None
            }
            players.append(player_dict)

        player_market_values = soup.select('td.rechts:not(.rueckennummer)')

        player_data_market_values = [td.get_text(strip=True) if td is not None else 'null' for td in player_market_values]

        # Iterate through player_data and player_data_market_values simultaneously
        for player_info, market_value_info in zip(players, player_data_market_values):
            # Update player_info dictionary with market_value
            player_info['market_value'] = market_value_info

        for player_info, club_info in zip(players, player_previous_clubs):
            player_info['signed_from'] = club_info

        for player_info, name_info in zip(players, player_names):
            player_info['name'] = name_info

        for player_info, position_info in zip(players, posititon_values):
            player_info['position'] = position_info

        for player_info, team_name in zip(players, [squad_name] * len(players)):
            club_name = team_name[0] if team_name else 'Unknown Club'
            player_info['club'] = club_name

        # add current url players to the all players list
        all_players.extend(players)

        sleep(5)


    return pd.DataFrame(all_players)
