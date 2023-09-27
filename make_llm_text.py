from datetime import datetime
import pandas as pd
import argparse
import tqdm
import re
import os

DEFAULT_HEADER_STRING = """The following are descriptions of creatures in Pathfinder Second Edition."""
DEFAULT_REPEATED_DESC = """This creature uses it's parent family description: """
DEFAULT_FAMILY_HEADER = """These are creature families that represent common traits amongst all creatures of the same family"""
DEFAULT_MONSTER_HEADER = """The following are individual creature descriptions"""
DEFAULT_ENCOUNTER_RULES_TEXT = "./building_encounters_rules.txt"
DEFAULT_FAMDESC_CSV = "./creatures_all_rulebooks_comuncrar.familydesc.csv"
DEFAULT_CREDESC_CSV = "./creatures_all_rulebooks_comuncrar.creaturedesc.csv"
DEFAULT_CRESTAT_CSV = "./hyperlinkcreatures_all_rulebooks_comuncrar.txt"
DEFAULT_SOURCES = ['Bestiary 2',
 'Bestiary',
 'Bestiary 3',
 'Rage of Elements',
 'Gamemastery Guide',
 'Kingmaker Adventure Path',
 'Book of the Dead',
 'Kingmaker Companion Guide',
 'Core Rulebook']
DEFAULT_MAXCREATURES = 50
DEFAULT_STAT_COLS = ['Name_f','Family_f','Level_p','Trait_f','Sense_f']
DEFAULT_STAT_COL_MAP = {'Name_f': "Creature Name",
                        "Family_f": "Creature Family",
                        "Trait_f": "Traits",
                        "Level_p": "Creature level relative to party",
                        "Sense_f": "Creature senses"}

THREAT_MAP = {"trivial": 40,
            "low": 60,
            "moderate": 80,
            "severe": 120,
            "extreme": 160}
PARTY_ADJUSTMENT_MAP = {"trivial": 10,
                        "low": 15,
                        "moderate": 20,
                        "severe": 30,
                        "extreme": 40}
cleaner = re.compile('\[(.+?)\]')


def buildParser():
    
    parser = argparse.ArgumentParser()

    parser.add_argument("output_folder", type = str)
    parser.add_argument("apl", type = int, help = "Average party level")
    parser.add_argument("--party_size", type = int, default = 4,
                        help = """Number of party members""")
    parser.add_argument("--min_l", type = int, default = None, 
                        help = """Minimum creature level to consider. If not 
                        set will use apl - 3.""")
    parser.add_argument("--max_l", type = int, default = None,
                        help = """Maximum creature level to consider. If not set,
                        will use apl + 3.""")
    parser.add_argument("--family_description", type = str, default = DEFAULT_FAMDESC_CSV)
    parser.add_argument("--creature_description", type = str, default = DEFAULT_CREDESC_CSV)
    parser.add_argument("--creature_stats", type = str, default = DEFAULT_CRESTAT_CSV)
    parser.add_argument("--max_creatures", type = int, default = DEFAULT_MAXCREATURES)
    parser.add_argument("--max_sentences", type = int, default = 6) 
    parser.add_argument("--drop_rules", action = "store_true", default = False,
                        help = """Create rules or note """)
    parser.add_argument("--names_include_csv", type=str, default = "",
                        help = """CSV values of creature names to include""")
    parser.add_argument("--family_include_csv", type = str, default = "",
                        help = """CSV values of creature families names to include""")
    parser.add_argument("--trait_include_csv", type = str, default = "",
                        help = """CSV values of creature traits to include""")

    return parser

def AONFormat(x):
    f = re.search(cleaner, str(x))
    if f is None:
        return x
    else:
        return " ".join(f.groups())
    
def buildName(x):
    try:
        return x.split('[')[1].split(']')[0]
    except:
        return None

def prepDataFrame(dfCStats, APL):
    # Build formatted data
    dfCStats['Name_f']       = dfCStats['Name'].apply(AONFormat)
    dfCStats['Sense_f']      = dfCStats['Sense'].apply(AONFormat)
    dfCStats['Family_f']     = dfCStats['Creature family'].apply(buildName)
    dfCStats['Trait_f']      = dfCStats['Trait'].apply(AONFormat)
    dfCStats['Source_f']     = dfCStats['Source'].apply(AONFormat)
    dfCStats['Level']        = dfCStats['Level'].apply(lambda x: int(x))
    dfCStats['Level_p']      = dfCStats['Level'].apply(lambda x: x - APL)
    return dfCStats

def main(args):
    now = datetime.now() 
    output = now.strftime("%m_%d_%Y_%H_%M_%S.llm")
    output = os.path.join(args.output_folder, output)
    dfCStats = pd.read_csv(args.creature_stats, delimiter='|')
    dfCStats = dfCStats.loc[1:]
    dfCStats = prepDataFrame(dfCStats, args.apl)
    source_f = dfCStats['Source_f'].apply(lambda x: x in DEFAULT_SOURCES)
    dfCStats = dfCStats[source_f]

    il = dfCStats.shape[0]
    # Filter on input name CSV
    if args.names_include_csv != "":
        names_filt = args.names_include_csv.split(',')
        names_filt = [q.strip() for q in names_filt]
        f = dfCStats['Name_f'].apply(lambda x: x in names_filt)
        dfCStats = dfCStats[f].reset_index()
    if args.family_include_csv != "":
        fam_filt = args.family_include_csv.split(",")
        fam_filt = [q.strip() for q in fam_filt]
        print(fam_filt)
        f = dfCStats['Family_f'].apply(lambda x: x in fam_filt)
        dfCStats = dfCStats[f].reset_index()
    if args.trait_include_csv != "":
        trt_filt = args.trait_include_csv.split(",")
        trt_filt = [q.strip() for q in trt_filt]
        print(trt_filt)
        f = dfCStats['Trait_f'].apply(lambda x: x in trt_filt)
        dfCStats = dfCStats[f].reset_index()

    el = dfCStats.shape[0]
    if (il - el) > 0:
        print(f"After filtering there are {el} creatures")
    
    dfCDesc = pd.read_csv(args.creature_description)
    dfFam = pd.read_csv(args.family_description)

    # Filter by levels
    args.max_l = args.max_l or args.apl + 3
    args.min_l = args.min_l or args.apl - 3
    f1 = (dfCStats['Level'] <= args.max_l)
    print(sum(f1))
    f2 = (dfCStats['Level'] >= args.min_l)
    print(sum(f2))
    dfCStats = dfCStats[f1 & f2].reset_index()
        
    # Prep strings
    family_string = ""
    explained_families = []
    creature_string = ""
    print(f"Total number of creatures parsed: {len(dfCStats)}")
    
    if len(dfCStats) > args.max_creatures:
        print(f"Sampling {args.max_creatures} for output")
        dfCStats = dfCStats.sample(args.max_creatures)

    for ind, row in tqdm.tqdm(dfCStats.iterrows(), total = len(dfCStats)):
    # for ind, row in dfCStats.iterrows():
        if (ind + 1) == args.max_creatures:
            break

        name = row['Name_f']
        fam = row['Family_f']

        # Family update
        ffam = dfFam.loc[dfFam['name_family'] == fam]
        fam_sum = ""
        
        if len(ffam) == 1:
            fam_sum = ffam['family_summary'].iloc[0]
            if fam not in explained_families:
                explained_families.append(fam)
                if len(fam_sum.split('.')) > args.max_sentences:
                    fam_sum = '.'.join(fam_sum.split('.')[:args.max_sentences])
                family_string += f"{fam}\nSummary: {fam_sum}\n"

        # Gather creature summary
        creature_sum = dfCDesc[dfCDesc['name'] == name]
        if len(creature_sum) == 1:
            creature_sum = creature_sum['creature_summary'].iloc[0]
        else:
            creature_sum = None
            continue
        stat_sum = name + ' - Family: {Family_f} | Relative level: {Level_p}'.format(**row) + '\n'
        
        # Create creature string update
        if creature_sum is not None:
            if creature_sum != fam_sum:
                if len(creature_sum.split('.')) > args.max_sentences:
                    creature_sum = '.'.join(creature_sum.split('.')[:args.max_sentences])
                creature_string += stat_sum + creature_sum + '\n\n'
        else:
            creature_string += stat_sum + DEFAULT_REPEATED_DESC + fam + '\n\n'

    output_string = DEFAULT_HEADER_STRING + "\n\n" \
        + DEFAULT_MONSTER_HEADER + "\n" + creature_string + "\n" 

    # Create rule text file specific to party size.
    if not args.drop_rules:
        with open(DEFAULT_ENCOUNTER_RULES_TEXT, 'r') as fid:
            rules = ''.join(fid.readlines())

        # Adjust the threat values based on party size
        threat_b = THREAT_MAP.copy()
        for ik, iv in threat_b.items():
            threat_b[ik] = iv + (PARTY_ADJUSTMENT_MAP[ik] * (args.party_size - 4))
        rules = rules.format(**threat_b)

        out_rul = output + '.rules.txt'
        with open(out_rul, 'w') as fid:
            fid.writelines(rules)

    with open(output + '.crtdsc.txt', 'w') as fid:
        fid.writelines(output_string)

    output_family_string = DEFAULT_FAMILY_HEADER + "\n" + family_string + "\n"
    out_fam = output +'.famdsc.txt'
    with open(out_fam, 'w') as fid:
        fid.writelines(output_family_string)

    # Write out the filtered stats as well
    out_stats = output +'.crtstats.csv'
    dfCStatsOut = dfCStats[DEFAULT_STAT_COLS]
    dfCStatsOut = dfCStatsOut.rename(columns = DEFAULT_STAT_COL_MAP)
    dfCStatsOut.to_csv(out_stats, index = False, sep = '|')
    with open(out_stats ,'r') as fid:
        creatures_csv_string = fid.readlines()
        creatures_csv_string = ''.join(creatures_csv_string)

    with open("./theme_desert.txt", 'r') as fid:
        theme_string = fid.readlines()
        theme_string = ''.join(theme_string)

    # Write the full prompt
    with open("./encounter_building_prompt.txt", 'r') as fid:
        encounter_building_prompt = fid.readlines()
        encounter_building_prompt = ''.join(encounter_building_prompt)

    dat = {'encounter_rules': rules,
           'creatures_csv_table': creatures_csv_string,
            'thematic_elements': theme_string,
            "encounter_difficulty": "moderate"}
    encounter_prompt = encounter_building_prompt.format(**dat)
    with open(output +'.llmprompt.txt' ,'w') as fid:
        fid.writelines(encounter_prompt)

    return

if __name__ == '__main__':
    parser = buildParser()
    args = parser.parse_args()

    main(args)