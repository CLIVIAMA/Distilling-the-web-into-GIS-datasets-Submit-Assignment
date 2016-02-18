"""
In this project, I scrape the information about top 100 largest libraries of the United
States from wikipedia, using geopy api to get the location of these libraries, create the 
shapefile and the geojson file that shows the location of these largest libraries
on the map and other information such as the volumes, name and whether they are academic
or public. From the shapefile and geojson file, we can easily see the largest libraries
distribution on the map.

The first challenge I encountered to get the table information from web. Through the referenced
page http://www.gregreda.com/2013/03/03/web-scraping-101-with-python/ I know that BeautifulSoup 
can help do this task. It can get information of particular html tag. And from search, I know 
that html table row tag is 'tr', at this step, I can get all the rows of the table of the web,
the rest is to filter the content I want.

The second challenge is to get the latitude and longitude of the libraries. By learning the geopy 
example code, I can get the location by look up the library name using its api.

The third challenge is to insert the html table to shapefile table. I use insert cursor to do the job,
but I found that it only can insert to an existing shapefile, so I have to find way to create an empty
shapefile first. First, I want to create it thorugh arcpy, But through much research there seem no way
to do it through arcpy. So then I decide to create the empty shapefile using the Arcmap software, fortunately
I found a YouTube video(https://www.youtube.com/watch?v=pUnUrTzP2dw) to teach it.

I implement this project on my own. But I borrowed example codes of geopy(https://github.com/geopy/geopy) 
to get the latitude and longitude from address. And also I have learned the codes from 
http://www.gregreda.com/2013/03/03/web-scraping-101-with-python/ to use BeautifulSoup.

I estimated I have spent 23 hours to do this project.

"""


def scrapeTable():
	"""
	this function get the table information from the url using BeautifulSoup
	"""
	from bs4 import BeautifulSoup
	from urllib2 import urlopen

	url = "https://en.wikipedia.org/wiki/List_of_the_largest_libraries_in_the_United_States"

	# read the html content
	html = urlopen(url).read()

	# create BeautifulSoup from html
	table = BeautifulSoup(html)

	# find all table row elements
	rows = table.findAll('tr')

	arr = []
	for tr in rows:

		# find all columns
		cols = tr.findAll('td')

		# column text
		x = [c.text for c in cols]

		# filter the content
		if len(x)!=0:
			try:
				int(x[0])
			except Exception, e:
				break

			arr.append(x)

	return arr



from geopy.geocoders import Nominatim

geolocator = Nominatim()

def getLatAndLong(addr):
	"""
	get the latitude and longitude through address using geopy
	"""
	try:
		location = geolocator.geocode(addr, timeout = 2)

		print (location.latitude, location.longitude)
		return (location.latitude, location.longitude)
	except Exception, e:
		print e
		return None
	

def getAllLocation(table):
	"""
	get all the location of the libraries in the table
	"""
	locs = []

	num = len(table)

	for i in range(num):
		# first field is the name
		loc = getLatAndLong(table[i][1])

		locs.append(loc)

	return locs


outputDirectory = r"C:/Python27/distill_web_output/"

# before run the program, create an empty shapefile on this path
outShape = outputDirectory + "libraries.shp"

outGeojson = outputDirectory + "libraries.geojson"


def addToShapeFile(table, locs):
    import arcpy

    insertCursor = arcpy.InsertCursor(outShape)

    for i in range(len(table)):
        if locs[i] != None:

            row = insertCursor.newRow()

            point = arcpy.CreateObject("Point")

            # The X field  is longitude and the Y field is latitude
            point.Y, point.X = locs[i][0], locs[i][1]
            
            row.shape = point

            # library name
            row.Name = table[i][1]

            # process the volumes number, 
            noco = table[i][2].replace(",","")

            t = noco.find('[')

            if t != -1:
                noco = noco[:t]

            row.Id = i
            # volumns
            row.Volumes = int(noco)
            # types such as public or academic
            row.Type = table[i][3]
            # administration
            row.Admin = table[i][4]
            # state
            row.State = table[i][5]

            # insert the row
            insertCursor.insertRow(row)


def transform():
	"""
	transform shapefile to geojson using ogr2ogr
	"""
    from subprocess import call
    import os

    exePath = r'C:\Python27\ArcGIS10.2\release-1700-gdal-1-11-3-mapserver-6-4-2\bin\ogr2ogr'

    call([exePath, '-f','GeoJSON',
        outGeojson,
        outShape])


def main():

	# scrape table information from wiki
	table = scrapeTable()

	# find the locations of these libraries
	locs = getAllLocation(table)

	# insert table to shapefile
	addToShapeFile(table, locs)

	# transform to geojson file
	transform()

if __name__ == '__main__':
	main()






