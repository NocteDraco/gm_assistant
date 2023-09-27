"""
Web scraper for gathering information from Archives of Nethys creatures. Requires
a copy of the linked names to function.
"""

from bs4 import BeautifulSoup
import pandas as pd
import argparse
import requests
import tqdm
import time
import os
import re


DEFAULT_HEADER_STRING = """The following are descriptions of creatures all of a single level in Pathfinder Second Edition."""
DEFAULT_REPEATED_DESC = """This creature uses it's parent family description: """
DEFAULT_FAMILY_HEADER = """These are creature families that represent common traits amongst all creatures of the same family"""
DEFAULT_MONSTER_HEADER = """These are individual creature descriptions for the relevant monsters"""
re_clean = re.compile('<.*?>')


def _getDescText(link):
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'html.parser')
    # Parse out the meta content description
    summary = soup.head.find(name = 'meta', content = True, attrs = {"name": "description"})
    try:
        sum_text = summary['content']
        sum_text = re.sub(re_clean, '', sum_text)
    except TypeError:
        return None
    return sum_text

def buildMonsterSummary(x):
    if x["Name_f"] == None:
        return None
    name = x['Name_f']
    link = x['link']
    sum_text = _getDescText(link)
    return (name, sum_text)

def buildMonsterFamilySummary(x, clean = re_clean):
    if x["Family_f"] == None:
        return None
    name = x['Family_f']
    link = x['link_family']
    sum_text = _getDescText(link)
    return (name, sum_text)

def buildLink(x):
    try:
        a = x.split('](')
        b = a[1]
        c = b.split(')')
        d = c[0]
        return d
    except:
        return None

def buildName(x):
    try:
        return x.split('[')[1].split(']')[0]
    except:
        return None

def buildParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('text', type = str)
    return parser

def main(args):
    print("Loading data")
    df = pd.read_csv(args.text, delimiter='|')
    print("Data prep")
    df['Name_f'] = df["Name"].apply(buildName)
    df["link"] = df['Name'].apply(buildLink)
    df['Family_f'] = df["Creature family"].apply(buildName)
    df["link_family"] = df["Creature family"].apply(buildLink)
    print("Gathering descriptions")
    
    

    # Query individual monster descriptions
    dfFamily = pd.DataFrame(columns = ['name_family', 'family_summary'])
    dfCreature = pd.DataFrame()

    print("Gathering individual monster descriptions")
    for i, row in tqdm.tqdm(df.loc[1:].iterrows()):
        
        # Query monster family descriptions if not present
        mons_fam = row['Family_f']
        if (row['Family_f'] is not None) and (row['Family_f'] not in dfFamily['name_family'].values):            
            name, family_summary = buildMonsterFamilySummary(row)
            if family_summary is not None:
                # family_string += name + '\n' + family_summary + '\n\n'
                # exp_mons_fam[row['Family_f']] = family_summary
                dat = {'name_family': name, 'family_summary':family_summary}
                dfFamily = pd.concat([dfFamily, pd.DataFrame([dat])], ignore_index = True)

        name, monster_sum = buildMonsterSummary(row)
        if monster_sum is not None:
            dat = {'name': name, 
                'creature_summary': monster_sum, 
                "name_family": mons_fam,
                "level": row['Level']}

            dfCreature = pd.concat([dfCreature, pd.DataFrame([dat])], ignore_index = True)

        # Prevent DDOS'ing
        time.sleep(0.25)
        if (i+1)%200 == 0:
            outpath = os.path.splitext(args.text)[0] + ".creaturedesc.csv"
            outpath_family = os.path.splitext(args.text)[0] + ".familydesc.csv"
            dfCreature.to_csv(outpath, index = False)
            dfFamily.to_csv(outpath_family, index = False)

    outpath = os.path.splitext(args.text)[0] + ".creaturedesc.csv"
    outpath_family = os.path.splitext(args.text)[0] + ".familydesc.csv"
    dfCreature.to_csv(outpath, index = False)
    dfFamily.to_csv(outpath_family, index = False)


if __name__ == '__main__':
    parser = buildParser()
    args = parser.parse_args()
    main(args)