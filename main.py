import pandas as pd
import matplotlib.pylab as plt
from pandas.plotting import register_matplotlib_converters
import os

def main():

    fieldname = 'new_cases'
    movingaverageupper = 28
    movingaveragelower = 7
    location = 'United Kingdom'
    populationminimum = 20000000
    groupbyfield = 'iso_subregion'

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
    df['mortality'] = df['total_deaths'] / df['total_cases']
    
    #join regional fields to iso_code
    df = pd.merge(df, dfiso, how='right', on='iso_code')
    df = df.dropna(axis=0, subset=['location'])

    register_matplotlib_converters()
    pd.options.mode.chained_assignment = None

    movingaveragebarchartcomparison(location, movingaveragelower, movingaverageupper, fieldname, df, 
        False, populationminimum, True, groupbyfield)


#bar chart or relative moving averages
def movingaveragebarchartcomparison(location, movingaveragelower, movingaverageupper, fieldname, df, 
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
        exportfile = 'c:\\temp\\covid19output1.csv'
        df2.to_csv(exportfile)


#line chart of two country comparison
def linechartcomparison(location, location2, fieldname, df,exporttocsv):

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
        exportfile = 'c:\\temp\\covid19output2.csv'
        df2.to_csv(exportfile)


#line chart of relative moving averages
def movingaveragelinechartcomparison(location, movingaveragelower, movingaverageupper, fieldname,
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
        exportfile = 'c:\\temp\\covid19output3.csv'
        df2.to_csv(exportfile)


if __name__ == '__main__':

    main()

        #example implementations
        #movingaveragebarchartcomparison(location, movingaveragelower, movingaverageupper, fieldname, df, 
        #   False, populationminimum, True, groupbyfield)
        #movingaveragelinechartcomparison(location, movingaveragelower, movingaverageupper, fieldname, df, False)
        #linechartcomparison(location, 'World', fieldname, df, False)

        #data fields available in file
        #iso_code
        #location
        #date
        #total_cases
        #new_cases
        #total_deaths
        #new_deaths
        #total_cases_per_million
        #new_cases_per_million
        #total_deaths_per_million
        #new_deaths_per_million
        #total_tests
        #new_tests
        #total_tests_per_thousand
        #new_tests_per_thousand
        #new_tests_smoothed
        #new_tests_smoothed_per_thousand
        #tests_units
        #stringency_index
        #population
        #population_density
        #median_age
        #aged_65_older
        #aged_70_older
        #gdp_per_capita
        #extreme_poverty
        #cvd_death_rate
        #diabetes_prevalence
        #female_smokers
        #male_smokers
        #handwashing_facilities
        #hospital_beds_per_100k