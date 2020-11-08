# U.GG API Version 1.4.0
import os
import time
import json
import sys
from pathlib import Path

import requests
import urllib3


# warning hackathon code ahead


LEAGUE_PATH = Path(r'D:\Python\docker-temp-storage-because-idk-what-im-doing\rito\Riot Games\League of Legends')

# Poll every 3 seconds
POLL_WAIT = 3

aram_url = 'https://stats2.u.gg/lol/1.1/overview/10_22/normal_aram/%d/1.4.0.json'
ranked_url = 'https://stats2.u.gg/lol/1.1/overview/10_22/ranked_solo_5x5/%d/1.4.0.json'

regions = ('na', 'euw', 'kr', 'eune', 'br', 'las', 'lan', 'oce', 'ru', 'tr', 'jp', 'world')
ranks = ('challenger', 'master', 'diamond', 'platinum', 'gold', 'silver', 'bronze', 'overall', 'plat_plus', 'dia_plus')
lockfile = LEAGUE_PATH / 'lockfile'

urllib3.disable_warnings()

with open('champion.json', encoding='utf8') as f:
    champions = json.load(f)['data']


tree = {
    8000: [8005, 8008, 8021, 8010, 9101, 9111, 8009, 9104, 9105, 9103, 8014, 8017, 8299],
    8100: [8112, 8124, 8128, 9923, 8126, 8139, 8143, 8136, 8120, 8138, 8135, 8134, 8105, 8106],
    8200: [8214, 8229, 8230, 8224, 8226, 8275, 8210, 8234, 8233, 8237, 8232, 8236],
    8300: [8351, 8359, 8360, 8306, 8304, 8313, 8321, 8316, 8345, 8347, 8410, 8352],
    8400: [8437, 8439, 8465, 8446, 8463, 8401, 8429, 8444, 8473, 8451, 8453, 8242]
}
styles = tree.keys()

def sort_runes(runes, primary_style, sub_style):
    from functools import reduce, cmp_to_key

    indices = dict()

    def sort_fn(a, b): 
        return indices[a] - indices[b]

    def group_by(arr, fn):
        def red_fn(a, b):
            key = fn(b)
            if key not in a:
                a[key] = []
            a[key].append(b)
            return a
        return reduce(red_fn, arr, dict())

    def group_fn(rune):
        for style in styles:
            if rune in tree[style]:
                r_i = tree[style].index(rune)
                indices[rune] = r_i
                return style

    grouped = group_by(runes, group_fn)

    print(grouped)

    sort_fn = cmp_to_key(sort_fn)

    grouped[primary_style].sort(key=sort_fn)
    grouped[sub_style].sort(key=sort_fn)

    return [*grouped[primary_style], *grouped[sub_style]]


def wait_for_champ(window):
    # Check if League is open...
    while True:
        print('Polling for lockfile...')
        if lockfile.exists(): break
        print(f'Lockfile not found. Trying again in {POLL_WAIT} seconds...')
        time.sleep(POLL_WAIT)

    # If it is, fetch the LCU API's URL information 
    f = lockfile.open()
    _, _, port, password, protocol = f.read().split(':')
    f.close()

    base_url = f'{protocol}://127.0.0.1:{port}/'
    print(f'LCU API URL: {base_url}')

    auth = requests.auth.HTTPBasicAuth('riot', password)


    def build_url(route: str):
        return (base_url[:-1] if base_url[-1] == route[0] == '/' else base_url) + route


    def api_fetch(route: str):
        url = build_url(route)
        print(f'Sending request to {url}')
        return requests.get(url, auth=auth, verify=False).json()


    def get_champion(key: int):
        for champion in champions.values():
            if int(champion['key']) == key:
                return champion['id'], champion['name']
        return None


    # Summoner's region
    region = api_fetch('/riotclient/get_region_locale')['region']
    region = str(regions.index(region.lower()) + 1)

    # Recommended runes for current rank 
    rank = 'diamond'
    rank = str(ranks.index(rank) + 1)

    # sus
    summoner_id = api_fetch('/lol-chat/v1/me')['summonerId']
    print(f'Summoner ID: {summoner_id}')


    def update_champion(champion_id: int, is_aram: bool):
        url = (aram_url if is_aram else ranked_url) % champion_id
        data = requests.get(url).json()
        print(region, rank, is_aram)
        
        if is_aram:
            runes = data[region]['8']['6']
        else:
            runes = data[region][rank]['4'] 

        print(runes)

        main_style = runes[0][0][2]
        sub_style = runes[0][0][3]
        
        main_runes = runes[0][0][4]
        # main_runes = map(main_runes.__getitem__, (0, 5, 4, 1, 3, 2))
        main_runes = sort_runes(main_runes, main_style, sub_style)
        
        shards = runes[0][8][2]
        shards = map(int, shards)

        curr_page_id = api_fetch('/lol-perks/v1/currentpage')['id']
        del_url = build_url(f'/lol-perks/v1/pages/{curr_page_id}')
        create_url = build_url(f'/lol-perks/v1/pages/')
        print(f'Current page: {curr_page_id}')

        requests.delete(del_url, auth=auth, verify=False)
        print('Deleted current page.')

        runes = [*main_runes, *shards]
        champ_id, champ_name = get_champion(champion_id)
        page_name = champ_name + ' ' + ('ARAM' if is_aram else 'Ranked 5v5')
        requests.post(create_url, auth=auth, verify=False, json=dict(
            name=page_name,
            primaryStyleId=main_style,
            subStyleId=sub_style,
            selectedPerkIds=runes,
        ))

        print(f'Created page with name {page_name}. {runes}')

        display_runes = runes.copy()
        runes.insert(0, main_style)
        runes.insert(5, sub_style)
        window.evaluate_js(
            r'''
            updateChampion({
                id: "%s",
                pageName: "%s",
                runes: %s
            });
            ''' % (champ_id, page_name, runes)
        )


    run = True
    def stop():
        nonlocal run
        run = False
    window.closed += stop

    last_champ = None

    def champ_select():
        nonlocal last_champ
        # Wait until player is in champion select
        while run:
            session = api_fetch('/lol-champ-select/v1/session')
            if 'myTeam' in session.keys():
                team = session['myTeam']
                for member in team:
                    if member['summonerId'] == summoner_id:
                        champion = member['championId']
                        break
                if isinstance(champion, int) and champion > 0:
                    break

            print(f'Not in champ select, or no champion has been selected. Trying again in {POLL_WAIT} seconds...')
            time.sleep(POLL_WAIT)
        else:
            return

        if champion != last_champ:
            print(f'Fetching runes for champion with ID {champion}...')
            is_aram = api_fetch('/lol-champ-select/v1/session')['allowRerolling']
            update_champion(champion, is_aram)
            last_champ = champion

        time.sleep(1)
        champ_select()


    champ_select()