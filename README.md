#Covid19 Data Visualisation in Python

ourworldindata.org kindly offers an updated csv file which can easily be extracted for analysis on this subject. 

It seems that the common pattern of this pandemic within countries is to see new cases grow rapidly (almost exponentially in some cases) in the early stages before levelling off and eventually falling.

Using Python, this tool looks at the relative moving average of key Covid19 fields such as New Cases, New Deaths etc at a point in time to hopefully give some insight into the stages countries, regions and subregions are currently at.  The charts below are looking at the 7 to 28 day moving average window of new cases as an example.  It seems that there is some daily seasonality associated with the release of new data with some countries seemingly releasing multiple days of data in a single day, therefore a minimum moving average term of 7 days is probably the lowest bound that should be considered.  

![](Figure_Country.png)
![](Figure_SubRegion.png)
![](Figure_Region.png)

