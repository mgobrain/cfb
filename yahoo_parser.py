import pandas as pd
import glob as glob

# SET: directory of HTML files
target = '/home'

# store weekly results in a dictionary
week_dict = {}

# loop through HTML files in target directory
for f in glob.glob(target+'.html'):
    t = pd.read_html(f)[0]
    t.index = t[0]
    t.index.name = ''
    t.drop(columns=t.columns[-3:], axis=1, inplace=True)
    t.drop('Team Name', axis=0, inplace=True)
    t.drop(0, axis=1, inplace=True)
    week_dict[f.split('/')[-1].split('.')[0]] = t

# scrape users
og_users = t.index
users = og_users.copy()
u_dict = {'consensus': []}
for u in users:
    u_dict[u] = pd.Series([])

# loop through weeks and grab picks from each user
for w in week_dict.keys():
    for u in users:
        picks = week_dict[w].loc[u]
        u_dict[u] = pd.concat([u_dict[u],picks]).reset_index(drop=True)

# compare users head-to-head
diff_dict = {}
ties = 0

for g in u_dict[u].index:
    users = og_users.copy()
    group_pick = []
    for u in users:
        for v in users:
            if u == v:
                break
            if u_dict[u][g] == u_dict[v][g]:
                try:
                    diff_dict[u+'-'+v] += 1
                except KeyError:
                    diff_dict[u+'-'+v] = 1
        group_pick.append(u_dict[u][g])
        users.drop(u)
    group_pick  = [x for x in group_pick if type(x) == str]
    s = pd.Series(group_pick)
    s = s.value_counts()
    if [x for x in group_pick if s[x] < s.max()] == []:
        u_dict['consensus'].append('TIE')
        ties += 1
    else:
        u_dict['consensus'].append(s.idxmax())

diff_dict = {}
for g in u_dict[u].index:
    users = u_dict.keys()
    for u in users:
        for v in users:
            if u == v:
                break
            if u_dict[u][g] == u_dict[v][g]:
                try:
                    diff_dict[u+'-'+v] += 1
                except KeyError:
                    diff_dict[u+'-'+v] = 1

for k in diff_dict.keys():
    if 'consensus' in k:
        diff_dict[k] = diff_dict[k]/(len(u_dict[u])-ties)
    else:
        diff_dict[k] = diff_dict[k]/(len(u_dict[u]))

# inter-user agreement
corrs = pd.Series(diff_dict).sort_values()
print(corrs)
