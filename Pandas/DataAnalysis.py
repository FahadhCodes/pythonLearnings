import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("std_performance.csv")
# Mentionaning Necessary fields to clean null data contained recode
necessary_clm = ['StudyHoursPerWeek', 'PreviousGrade', 'ParentalSupport',
                 'FinalGrade', 'Study Hours', 'Attendance (%)', 'Online Classes Taken']
selected_fileds = [
    'StudyHoursPerWeek', 'PreviousGrade',
    'ExtracurricularActivities', 'ParentalSupport',
    'FinalGrade', 'Study Hours', 'Attendance (%)',
    'Online Classes Taken']


def cleaning(df, necessary_clm, selected_fileds):
    df = df.dropna(subset=necessary_clm)
    # Selecting fields
    df = df[selected_fileds]
    bdf = df.isna()
    # rechecking null
    for x in selected_fileds:
        print(f"_"*5, f"{x}", f"_"*5)
        for p, q in bdf[x].items():
            if q:
                message = "empty Available"
                print(f"{x}:{p, q, df.loc[p, x]}")
                if x == "ExtracurricularActivities":
                    df.fillna({x: 0}, inplace=True)
    return df


df = cleaning(df, necessary_clm, selected_fileds)
# other datatypes to numbers
df["ParentalSupport"] = df["ParentalSupport"].map({
    "High": 3,
    "Medium": 2,
    "Low": 1
})

df["Online Classes Taken"] = df["Online Classes Taken"].map({
    True: 1,
    False: 0
})


req = "Study Hours"
for x, y in df[req].items():
    if y < 0:
        df.loc[x, req] *= -1

print('''
info\t:1\n
describe\t:2\n
correlation\t:3\n
plotes\t:4\n
''')


def analytic():
    cho = int(input("Enter analytic type: "))
    if cho == 1:
        print(df.info())
    elif cho == 2:
        print(df.describe())
    elif cho == 3:
        print(df.corr())
    elif cho == 4:
        for column in selected_fileds:
            df.plot(kind="scatter", x=column, y="FinalGrade")
            plt.show()


analytic()
