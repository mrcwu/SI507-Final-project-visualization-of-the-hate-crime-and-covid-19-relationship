# Step 0: required packages
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import json
import requests
from geojson import Feature, FeatureCollection #conda install -c conda-forge geojson
from os.path import exists
from scipy import stats

# Step.1 building data structure: final_df

# 1.1 put state_list in the script
with open('states.csv', 'r') as s:
    next(s)
    s_data = s.read()
    s_list = s_data.split('\n')
    s_list = s_list[:-1]
    f_s_list = []
    for text in s_list:
        list_text = text.split(',')
        f_s_list.append(list_text)


# 1.2 build final_df
# 1.2.1 build the pk

date_list = pd.date_range(start = '1/1/2020', end = '12/31/2020').unique()
date_list = date_list.astype(str).tolist()

final_df = []
for state in f_s_list:
    for date in date_list:
        final_df.append([(state, date)])


# 1.2.2 append covid and crime sections
# 1.2.2.1 build the list gonna used
crime_cat_VICTIM_TYPES = [
            'Business',
            'Financial Institution',
            'Government',
            'Individual',
            'Law Enforcement Officer',
            'Other',
            'Religious Organization',
            'Society/Public',
            'Unknown']

crime_cat_BIAS_DESC = [
            'Anti-American Indian or Alaska Native',
            'Anti-Arab',
            'Anti-Asian',
            'Anti-Atheism/Agnosticism',
            'Anti-Bisexual',
            'Anti-Black or African American',
            'Anti-Buddhist',
            'Anti-Catholic',
            'Anti-Eastern Orthodox (Russian, Greek, Other)',
            'Anti-Female',
            'Anti-Gay (Male)',
            'Anti-Gender Non-Conforming',
            'Anti-Heterosexual',
            'Anti-Hindu',
            'Anti-Hispanic or Latino',
            'Anti-Islamic (Muslim)',
            "Anti-Jehovah's Witness",
            'Anti-Jewish',
            'Anti-Lesbian (Female)',
            'Anti-Lesbian, Gay, Bisexual, or Transgender (Mixed Group)',
            'Anti-Male',
            'Anti-Mental Disability',
            'Anti-Mormon',
            'Anti-Multiple Races, Group',
            'Anti-Multiple Religions, Group',
            'Anti-Native Hawaiian or Other Pacific Islander',
            'Anti-Other Christian',
            'Anti-Other Race/Ethnicity/Ancestry',
            'Anti-Other Religion',
            'Anti-Physical Disability',
            'Anti-Protestant',
            'Anti-Sikh',
            'Anti-Transgender',
            'Anti-White']

VICTIM_TYPES = {}
BIAS_DESC = {}
for n in crime_cat_VICTIM_TYPES:
    VICTIM_TYPES[n] = None
for i in crime_cat_BIAS_DESC:
    BIAS_DESC[i] = None

crime = {'VICTIM_TYPES':VICTIM_TYPES, 'BIAS_DESC':BIAS_DESC, 'VICTIM_COUNT':None}
covid = {'newCases':0, 'newDeaths':0}

# 1.2.2.2 append process
for item in final_df:
    item.append({'covid':covid,'crime':crime})

# 1.2.3 covert the final_df into json type

json_final_df = json.dumps(final_df)
final_df = json.loads(json_final_df)



# step 2: put in the crime data (first data) into the final_df
# 2.1 read the crime csv files
df = pd.read_csv("hate_crime_2020.csv", low_memory=False)
df['INCIDENT_DATE'] = pd.to_datetime(df['INCIDENT_DATE'])
df['INCIDENT_DATE'] = df['INCIDENT_DATE'].astype(str)
crime_data = df.values.tolist()

# 2.2 put in the data
for item in final_df:
    for crime in crime_data:
        # state equal and date equal, the first state abbr (item[0][0][0]) is the abbr used in crime data
        if item[0][0][0] == crime[6] and item[0][1] == crime[12]:
            # put in victim type
            vic_type_col = 29
            for vic_type in crime_cat_VICTIM_TYPES:
                # put in the victim type
                if item[1]['crime']['VICTIM_TYPES'][str(vic_type)] == None:
                    item[1]['crime']['VICTIM_TYPES'][str(vic_type)] = int(crime[vic_type_col])
                else:
                    item[1]['crime']['VICTIM_TYPES'][str(vic_type)] += int(crime[vic_type_col])

                vic_type_col += 1

            # put in victim group
            vic_col = 43
            for vic in crime_cat_BIAS_DESC:
                if item[1]['crime']['BIAS_DESC'][str(vic)] == None:
                    item[1]['crime']['BIAS_DESC'][str(vic)] = int(crime[vic_col])
                else:
                    item[1]['crime']['BIAS_DESC'][str(vic)] += int(crime[vic_col])

                vic_col += 1

            vic_count_col = 20
            # put in victim count
            if item[1]['crime']['VICTIM_COUNT'] == None:
                item[1]['crime']['VICTIM_COUNT'] = int(crime[vic_count_col])
            else:
                item[1]['crime']['VICTIM_COUNT'] += int(crime[vic_count_col])

        else:
            pass



# step 3: download the covid data (second data) and put in the final_df
# 3.1 download files and save to json DB
# 3.1.1 data capture with api. If the file already exists, it will not download.
if not exists('covid_data.json'):
    response_covid = requests.get("https://api.covidactnow.org/v2/states.timeseries.json?apiKey=ca6fedd93a5f4a20921a178c231aecbf")
    covid_data = json.loads(response_covid.text)

    # save to json file
    with open('covid_data.json', 'w', encoding='utf-8') as f:
        json.dump(covid_data, f)
# 3.1.2 load the data
covid_data_download = json.load(open('covid_data.json','r'))


# 3.2 put in the data
for item in final_df:
        for covid_s_total in covid_data_download:
            # the second state abbr is the abbr used in covid data, that why use "item[0][0][1]"
            if covid_s_total["state"] == item[0][0][1]:
                for covid_s_time in covid_s_total["actualsTimeseries"]:
                    if covid_s_time["date"] == item[0][1]:
                        item[1]['covid']['newCases'] = covid_s_time["newCases"]
                        item[1]['covid']['newDeaths'] = covid_s_time["newDeaths"]

# save data structure
with open('main_data_structure.json', 'w', encoding='utf-8') as f:
    json.dump(final_df, f)

# Calculation function
def calculation(f_s_list, crime_cat_VICTIM_TYPES, crime_cat_BIAS_DESC, from_month, to_month, covid_input, crime_input_1, crime_input_2):

    # 1 build the first level data structure for calculation:
    month_list = pd.date_range(start=from_month+'/1/2020', end=to_month+'/15/2020').to_period('M').unique()
    month_list = month_list.astype(str).tolist()

    cal_df_1 = []
    meta = {'covid_count': 0, 'crime_count': 0}
    for state in f_s_list:
        for date in month_list:
            cal_df_1.append([(state, date), meta])

    json_cal_df_1 = json.dumps(cal_df_1)
    cal_df_1 = json.loads(json_cal_df_1)

    # 2 put the data into the first level calculation df
    for f_s_date in final_df:
        for c_s_date in cal_df_1:
            if f_s_date[0][0] == c_s_date[0][0] and f_s_date[0][1][:7] == c_s_date[0][1]:
                if crime_input_1 == 0:
                    value = f_s_date[1]['crime']['VICTIM_TYPES'][crime_cat_VICTIM_TYPES[crime_input_2]]
                    if value != None:
                        c_s_date[1]['crime_count'] += value

                elif crime_input_1 == 1:
                    value = f_s_date[1]['crime']['BIAS_DESC'][crime_cat_BIAS_DESC[crime_input_2]]
                    if value != None:
                        c_s_date[1]['crime_count'] += value

                elif crime_input_1 == 2:
                    value = f_s_date[1]['crime']['VICTIM_COUNT']
                    if value != None:
                        c_s_date[1]['crime_count'] += value

                if covid_input == 0:
                    cv = f_s_date[1]['covid']['newCases']
                    if cv != None:
                        c_s_date[1]['covid_count'] += cv

                elif covid_input == 1:
                    cv = f_s_date[1]['covid']['newDeaths']
                    if cv != None:
                        c_s_date[1]['covid_count'] += cv

    # 3 Calculate the correlation for each state
    # f_cor_state_list is the second level of calculation
    f_cor_state_list = []
    for u in range(len(f_s_list)):
        f_cor_state_list.append([f_s_list[u]])

    for st in f_cor_state_list:
        x = []
        y = []
        for c_s_date in cal_df_1:

            if st[0] == c_s_date[0][0]:

                x.append(c_s_date[1]['crime_count'])
                y.append(c_s_date[1]['covid_count'])

        try:
            r = stats.pearsonr(x, y)[0]
            fr = float(r)

        except:
            fr = 0

        st.append(fr)

    return(f_cor_state_list)



# Plotting function
# 1 setup
usa_map = 'https://github.com/kjhealy/us-county/raw/master/data/geojson/gz_2010_us_040_00_500k.json'
file_name = "usa_json.json"

def plotting(usa_map, file_name, f_s_list, f_cor_state_list):
    if not exists(file_name):
        us_json = requests.get(usa_map).json()
        with open(file_name, 'w') as file:
             file.write(json.dumps(us_json))

    data = json.load(open(file_name,'r'))


    # 2 building the plotting geojson
    # 2.1 setup
    f_s_list_name = [item[0][2] for item in f_cor_state_list]
    alaska = []
    hawaii = []
    main_usa = []

    f_cor_state_dict = {}
    for each_st in f_cor_state_list:
        f_cor_state_dict[each_st[0][2]] = each_st[1]


    for state in data["features"]:
        if state["properties"]["NAME"] in f_s_list_name:
            if state["properties"]["NAME"] == 'Alaska':
                alaska.append(Feature(geometry=(state["geometry"]),
                                        properties={"state_name": state["properties"]["NAME"],
                                                    "corelation": f_cor_state_dict[state["properties"]["NAME"]],
                                                    "color":'lightgray'}))

            elif state["properties"]["NAME"] == 'Hawaii':
                hawaii.append(Feature(geometry=(state["geometry"]),
                                        properties={"state_name": state["properties"]["NAME"],
                                                    "corelation": f_cor_state_dict[state["properties"]["NAME"]],
                                                    "color":'lightgray'}))

            else:
                main_usa.append(Feature(geometry=(state["geometry"]),
                                        properties={"state_name": state["properties"]["NAME"],
                                                    "corelation": f_cor_state_dict[state["properties"]["NAME"]],
                                                    "color":'lightgray'}))


    # 2.2.2 making geojson objects
    alaska_collection = FeatureCollection(alaska)
    hawaii_collection = FeatureCollection(hawaii)
    main_usa_collection = FeatureCollection(main_usa)

    # 2.3 convert geojson objects into geopanda dataframe
    m_usa_p = geopandas.GeoDataFrame.from_features(main_usa_collection, crs = 'EPSG:4269')
    alaska_p = geopandas.GeoDataFrame.from_features(alaska_collection, crs = 'EPSG:4269')
    hawaii_p = geopandas.GeoDataFrame.from_features(hawaii_collection, crs = 'EPSG:4269')

    # 2.4 making a plot with insert plots (Hawaii and Alaska)
    fig, ax_m = plt.subplots()
    left_1, bottom_1, width_1, height_1 = [.10, 0.80, 0.15, 0.15]
    ax_1 = fig.add_axes([left_1, bottom_1, width_1, height_1])
    ax_1.axis([-178, -135, 46, 73])

    left_2, bottom_2, width_2, height_2 = [.25, 0.80, 0.15, 0.15]
    ax_2 = fig.add_axes([left_2, bottom_2, width_2, height_2])
    ax_2.axis([-162, -152, 15, 25])


    # 2.5 final output
    m_usa_p.plot(ax=ax_m, column = "corelation", legend=True, missing_kwds={"color": "lightgrey","edgecolor": "red", "hatch": "///", "label": "Missing values"})
    alaska_p.plot(ax=ax_1, column = "corelation", missing_kwds={"color": "lightgrey","edgecolor": "red", "hatch": "///", "label": "Missing values"})
    hawaii_p.plot(ax=ax_2,  column = "corelation", missing_kwds={"color": "lightgrey","edgecolor": "red", "hatch": "///", "label": "Missing values"})

    plt.show()

# Final part: User's input
if __name__ == "__main__":
    print("Welcome! This is my final project in SI507.")
    print("This program will firstly ask you put in 4-5 parameters (calculation starting date, calculation ending date, covid data going to use, crime category (if applicable) and crime data going to use).")
    print("Then, it will calculate the correlation coefficient between these two data and plot them on the US map.")
    print("Let's get started!")

    term = input('Please choose a starting month (1 to 10), or type exit to end this sub')
    check = lambda term: int(term) if term.isnumeric() else -99
    while str(term) != 'exit':

        while (check(term) not in range(1,11)):
            print('please put in a valid month. Also, starting month must smaller than 11.')
            term = input('Please choose a starting month (1 to 10)')

        from_month = term

        term = input('Please choose an ending month (3 to 12, it must be at least twice greater than the first input.)')
        while ((check(term) not in range(3,13)) or (check(term) - int(from_month) < 2)):
            print('please put in a valid month. Also, ending month must greater than 2.')
            term = input('Please choose an ending month (3 to 12, it must be at least twice greater than the first input.)')
        to_month = term

        print('covid data:')
        print('0: cases, 1: death')
        term = input('Please select which covid data you want to compare (type in the number)')
        while check(term) not in range(0,2):
            print('please put in a valid number')
            term = input('Please select which covid data you want to compare (type in the number)')
        covid_input = term

        print('crime_data:')
        print("0: victim types, 1: victim social groups, 2: all of the victim")
        term = input('Please select which crime category/data you want to compare with covid data (type in the number)')
        while (check(term) not in range(0,3)):
            print('please put in a valid number')
            term = input('Please select which crime category/data you want to compare with covid data (type in the number)')
        crime_input_1 = term

        if int(crime_input_1) != 2:
            if int(crime_input_1) == 1:
                for i in range(len(crime_cat_BIAS_DESC)):
                    print(str(i)+':'+str(crime_cat_BIAS_DESC[i]))
                    i += 1
                term = input('Please select which crime data you want to compare with covid data (type in the number)')
                while (check(term) not in range(len(crime_cat_BIAS_DESC))):
                    print('please put in a valid number')
                    term = input('Please select which crime data you want to compare with covid data (type in the number)')
                crime_input_2 = term

            elif int(crime_input_1) == 0:
                for i in range(len(crime_cat_VICTIM_TYPES)):
                    print(str(i)+':'+str(crime_cat_VICTIM_TYPES[i]))
                    i += 1
                term = input('Please select which crime data you want to compare with covid data (type in the number)')
                while (check(term) not in range(len(crime_cat_VICTIM_TYPES))):
                    print('please put in a valid number')
                    term = input('Please select which crime data you want to compare with covid data (type in the number)')
                crime_input_2 = term
        else:
            crime_input_2 = 0


        from_month = str(from_month)
        to_month = str(to_month)
        covid_input = int(covid_input)
        crime_input_1 = int(crime_input_1)
        crime_input_2 = int(crime_input_2)

        cor_list = calculation(f_s_list, crime_cat_VICTIM_TYPES, crime_cat_BIAS_DESC, from_month, to_month, covid_input, crime_input_1, crime_input_2)
        plotting(usa_map, file_name, f_s_list, cor_list)

        term = input('Please choose a starting month (1 to 10), or type exit to end this sub')
        if term == 'exit':
            break




    if term == 'exit':
        print('Bye!')


