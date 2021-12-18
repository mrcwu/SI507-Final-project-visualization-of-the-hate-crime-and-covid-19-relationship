# SI507 Final project

## Project code
### Package Requirement:
There are two packages in this python file (Geojson, Geopandas) that need to be run in Anaconda virtual environment. Therefore, you have to install Anaconda first. After you finished, run this python file in PyCharm or Visual Studio Code, and set your virtual environment to Conda.
While inside Conda environment, you can use this command install the Geojson:
	conda install -c conda-forge geojson
To install Geopandas, you can use this command:
	conda install -c conda-forge geopandas
If you cannot import Geopandas successfully and the error code shows: “OSError: could not find or load spatialindex_c-64.dll” It means that your Rtree is corrupted (martinfleis, 2021, p. 8). You have to either try reinstalling it or using Pygeos instead.
  The other add-on packages I used are Pandas, Matplotlib, Requests, Scipy. They can be installed with “pip install packagename” directly.

List of all the packages I used:
 
1.	pandas
2.	geopandas
3.	matplotlib
4.	json
5.	geojson
6.	requests
7.	os
8.	scipy
 

### API setting:
Only the covid-19 data came from an API and you have to sign up for a key to use it. However, there is only one argument, the “apiKey”, you can put inside the API link to access the data. If you want to access a different kind of covid data, you have to switch to a different JSON file API link.
The API link is: https://api.covidactnow.org/v2/states.timeseries.json?apiKey=The_key_you_applied

## Brief instruction of using:
1.	After installing the required packages, putting the raw data files, and setting the Anaconda virtual environment. Run the main.py python file. It will take some time to build the main data structure and put the data into it.
2.	After the sub successfully ran, it will show the input of the first parameter. Select one of the months as starting month. You can either type exit to end this sub.
3.	The second parameter is an ending month. Just select one of the numbers that follow the rules.
4.	The third parameter asks you to tell the script what kind of covid data you want to use.
5.	The fourth parameter asks you to type in what kind of crime category or data you want to use. If you select the last one (type in 2). It will not ask you about the next parameter and show the plot directly.
6.	The fifth parameter asks you to put in the crime data you want to start the calculation with the covid data you chose. If you select victim types it will show you 9 options. If you select victim social groups, it will give you 34 options to choose from.


## Data Structure
Type: tree
Description:
The data structure for each record is just like below:

[[['AK', 'AK', 'Alaska'], '2020-01-01'], 
  {'covid': {'newCases': 0, 'newDeaths': 0}, 
   'crime': {'VICTIM_TYPES': {'Business': None, 
                              ...9 fields total...
                             'Unknown': None}, 
            'BIAS_DESC': {'Anti-American Indian or Alaska Native': None, 
                          ........ 34 fields total.........
                          'Anti-White': None}, 
            'VICTIM_COUNT': None}}]

Inside each record, there are two elements. The first one store states and date, the second one has crime and covid data. Inside the covid category, there are two data fields. Inside the crime category, there are two subcategories and one data field. One of the sub-categories called 'VICTIM_TYPES' contains 9 fields. The other sub-category called 'BIAS_DESC' contains 34 fields. Each record can be explained like: “At one specific date in one specific state, what’s the numbers are in each different category of crimes, and what’s the numbers of new covid cases and new covid deaths?”

