import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import seaborn as sns
import os
import numpy as np
import math
from datetime import datetime, timedelta

location = 'United Kingdom'
fieldname = 'new_cases'
movingaverageupper = 28
movingaveragelower = 7    
location2 = 'United States'
populationminimum = 10000000
groupbyfield = 'location'
xVariable = 'total_tests_per_thousand'
yVariable = 'total_cases_per_million'
thirdVariable = 'continent'
chartbtype = 4
booLog = False
exportfile = 'c:\\temp\\covid19output.csv'

correlationfields = ['total_cases_per_million', 'total_deaths_per_million', 'total_tests_per_thousand',
        'mortality_rate', 'total_vaccinations_per_hundred', 'population_density', 
        'median_age', 'gdp_per_capita', 'hospital_beds_per_thousand', 
        'life_expectancy']

def main():

    datastream = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
    df = pd.read_csv(datastream, error_bad_lines=False)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['location'] != 'International']

    isofile = str(os.path.dirname(os.path.realpath(__file__))) + '\\iso.csv'
    if os.path.exists(isofile) == False:
        print ('ISO File not found')
        return

    dfiso = pd.read_csv(isofile)
    df.iso_code = df.iso_code.astype(str)
    df.iso_code = df.iso_code.str.strip()
    df['mortality_rate'] = df['total_deaths_per_million'] / df['total_cases_per_million']
    
    #join regional fields to iso_code
    df = pd.merge(df, dfiso, how='right', on='iso_code')
    df = df.dropna(axis=0, subset=['location'])

    register_matplotlib_converters()
    pd.options.mode.chained_assignment = None

    ChartProcess(chartbtype, df)


#to determine what chart type is run
def ChartProcess(bType, df):

    if bType == 1:
        MovingAverageBarChartComparison(location, movingaveragelower, movingaverageupper, 
        fieldname, df, False, populationminimum, True, groupbyfield)
    elif bType == 2:
        MovingAverageLineChartcomparison(location, movingaveragelower, movingaverageupper, 
        fieldname, df, False)
    elif bType == 3:
         LineChartComparison(location, location2, fieldname, df, False)
    elif bType == 4:
         ScatterChart(xVariable, yVariable, thirdVariable, 
         populationminimum, groupbyfield, df, True, booLog)
    elif bType == 5:
        CorrelationHeatMap(populationminimum, correlationfields, df, True)
    else:
        print ('Invalid Selection!')


#scatter plot of two variables colour coded by third variable
def ScatterChart(xVariable, yVariable, thirdVariable, populationminimum, groupbyfield, 
    df, exporttocsv, booLog):

    maxdate = (df['date']).max() - timedelta(days = 1)
    maxdate = maxdate.strftime('%Y%m%d')
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y%m%d')
    df2 = df[(df['date'] == maxdate) & (df['population'] > populationminimum)]

    if booLog:
        df2[xVariable] = np.log(df2[xVariable])
        df2[yVariable] = np.log(df2[yVariable])
    
    sns.relplot(x=xVariable, y=yVariable, hue=thirdVariable, data=df2)
    plt.show()

    if exporttocsv:
        df2.to_csv(exportfile)


#correlation heatmap of multiple variables
def CorrelationHeatMap(populationminimum, fields, df, exporttocsv):

    maxdate = (df['date']).max() - timedelta(days = 1)
    maxdate = maxdate.strftime('%Y%m%d')
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y%m%d')
    df2 = df[(df['date'] == maxdate) & (df['population'] > populationminimum)]

    df3 = df2[fields]
    heatmap = sns.heatmap(df3.corr(), vmin=-1, vmax=1, annot=True, cmap='YlGnBu', cbar=True)
    heatmap.set_yticklabels(heatmap.get_yticklabels(), rotation = 0, fontsize = 9)
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation = 0, fontsize = 7)
    
    ChartTitle = 'Covid-19 Correlation Heatmap (country populations > ' + str(populationminimum) + ')'
    heatmap.set_title(ChartTitle, fontdict={'fontsize':14}, pad=12)

    plt.xticks(rotation = 25)
    plt.show()

    if exporttocsv:
        df3.to_csv(exportfile)


#bar chart of relative moving averages
def MovingAverageBarChartComparison(location, movingaveragelower, movingaverageupper, fieldname, df, 
    exporttocsv, populationminimum, byPerMillion, groupbyfield):

    maxdate = (df['date']).max()
    maxdate = maxdate.strftime('%Y%m%d')
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y%m%d')

    df2 = df.groupby([groupbyfield,'date'])['population', fieldname].sum().reset_index()
    df2[fieldname+'_MAL'] = df2[fieldname].transform(lambda x: x.rolling(movingaveragelower, 1).mean())
    df2[fieldname+'_MAU'] = df2[fieldname].transform(lambda x: x.rolling(movingaverageupper, 1).mean())

    if byPerMillion:
        df2[fieldname + '_MAD'] = (df2[fieldname + '_MAL'] - df2[fieldname + '_MAU']) / (df2['population']) * 1000000
        chartstring = ' per million'
    else:
        df2[fieldname + '_MAD'] = (df2[fieldname + '_MAL'] - df2[fieldname + '_MAU'])
        chartstring = ''

    df3=df2[(df2['date'] == maxdate) & (df2['population'] > populationminimum) & (df2[groupbyfield] != 'World')]
    dfworld = df2[(df2['date'] == maxdate) & (df2[groupbyfield] == 'World')]

    df3.sort_values(fieldname + '_MAD', inplace=True, ascending=False)

    if groupbyfield == 'location':
        df3 = pd.concat([df3.tail(7), df3.head(7)])
    else:
        count = df3[fieldname + '_MAD'].count()
        seriesobj = df3[fieldname + '_MAD'] <= 0
        countnegative = len(seriesobj[seriesobj == True].index)
        df3 = pd.concat([df3.tail(countnegative), df3.head(count-countnegative)])

    plt.figure(figsize=(9,7)) 
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    ax.tick_params(axis='x', which='major', labelsize=6)
    ax.tick_params(axis='x', which='minor', labelsize=6)
    ax.set_xticklabels(pd.concat([df3[groupbyfield],dfworld[groupbyfield]]), rotation = 50, ha="right")

    plt.bar(df3[groupbyfield],df3[fieldname + '_MAD'], color = (df3[fieldname + '_MAD'] > 0)
        .map({True: 'grey',False: 'slategrey'}))
    plt.bar(dfworld[groupbyfield],dfworld[fieldname + '_MAD'], color = 'black')
    charttitle = 'Covid19 ' + fieldname + chartstring +  ', ' + str(movingaveragelower) + ' day minus ' \
        + str(movingaverageupper) + ' day average, ' + maxdate
    plt.title(charttitle)
    plt.show()

    if exporttocsv:
        df2.to_csv(exportfile)


#line chart of two country comparison
def LineChartComparison(location, location2, fieldname, df, exporttocsv):

    df['date'] = pd.to_datetime(df['date'])
    df2 = df[df['location'] == location]
    df3 = df[df['location'] == location2]

    plt.figure(figsize=(10,6)) 
    plt.plot(df2['date'], df2[fieldname], color = 'slategrey', label = location)
    plt.plot(df3['date'], df3[fieldname], color = 'black', label = location2)
    plt.title('Covid19 ' + fieldname)
    plt.legend(loc="upper left")
    plt.show()

    if exporttocsv:
        df2.to_csv(exportfile)


#line chart of relative moving averages
def MovingAverageLineChartcomparison(location, movingaveragelower, movingaverageupper, fieldname,
     df, exporttocsv):

    df2 = df[df['location'] == location]
    df2[fieldname + '_MAL'] = df2[fieldname].transform(lambda x: x.rolling(movingaveragelower, 1).mean())
    df2[fieldname + '_MAU'] = df2[fieldname].transform(lambda x: x.rolling(movingaverageupper, 1).mean())
    df2[fieldname + '_MAD'] = df2[fieldname + '_MAL'] - df2[fieldname + '_MAU']

    plt.figure(figsize=(10,6)) 
    plt.plot(df2['date'], df2[fieldname + '_MAD'], color = 'slategrey', label = 'ma')
    charttitle ='Covid19 ' + location + ' ' +  fieldname + ' - ' + str(movingaveragelower) \
        + ' day minus ' + str(movingaverageupper) + ' day average'
    plt.title(charttitle)
    plt.show()

    if exporttocsv:
        df2.to_csv(exportfile)


if __name__ == '__main__':

    main()

    #data fields available in file
    #iso_code	continent	location	date	total_cases	new_cases	new_cases_smoothed	
    # total_deaths	new_deaths	new_deaths_smoothed	total_cases_per_million	new_cases_per_million	
    # new_cases_smoothed_per_million	total_deaths_per_million	new_deaths_per_million	
    # new_deaths_smoothed_per_million	reproduction_rate	icu_patients	icu_patients_per_million	
    # hosp_patients	hosp_patients_per_million	weekly_icu_admissions	weekly_icu_admissions_per_million	
    # weekly_hosp_admissions	weekly_hosp_admissions_per_million	new_tests	total_tests	total_tests_per_thousand	
    # new_tests_per_thousand	new_tests_smoothed	new_tests_smoothed_per_thousand	positive_rate	tests_per_case	
    # tests_units	total_vaccinations	people_vaccinated	people_fully_vaccinated	new_vaccinations	
    # new_vaccinations_smoothed	total_vaccinations_per_hundred	people_vaccinated_per_hundred	
    # people_fully_vaccinated_per_hundred	new_vaccinations_smoothed_per_million	stringency_index	
    # population	population_density	median_age	aged_65_older	aged_70_older	gdp_per_capita	
    # extreme_poverty	cardiovasc_death_rate	diabetes_prevalence	female_smokers	male_smokers	
    # handwashing_facilities	hospital_beds_per_thousand	life_expectancy	human_development_index


