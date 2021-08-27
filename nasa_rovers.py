import requests
import json
from datetime import datetime, date, timedelta
import os

class NASARoverAPI:
    """ Custom made API that interfaces NASA's API for getting photos from Mars rovers

    Methods
    -------
    queryIsCached - checks './cache' folder to see if there are JSON files which contain cached NASA API response
    cacheQuery - saves NASA API response in a JSON file in './cache' folder
    getPhotos - main function of the class which returns JSON-like output of "date": [list_of_photos] pairs
    """

    @staticmethod
    def queryIsCached(rover_name, camera, date):
        """ Searches './cache' folder for cached JSON file based on input parameters """
        # If there is no ./cache folder, than certainly no cached files have been saved
        if not os.path.isdir('./cache'):
            return False

        cached_files = os.listdir("./cache")
        # Files are saved in the following format: "rovername_cameraname_YYYY-MM-DD.json"
        for file in cached_files:
            # Split file names and check if rover name, camera name and dates match
            l = file.split("_") 
            n, c, d = l[0], l[1], l[2].split(".")[0]
            if n == rover_name and c == camera and d == date:
                return True

        # No cached data for these parameters
        return False


    @staticmethod
    def cacheQuery(rover_name, camera, date, response):
        """ Saves NASA API response in a JSON file in './cache' folder """
        # Create a ./cache folder if one does not exist
        if not os.path.isdir('./cache'):
            os.mkdir('./cache')

        # Files are saved in the following format: "rovername_cameraname_YYYY-MM-DD.json"
        f = open(f"./cache/{rover_name}_{camera}_{date}.json", "w")
        # Prettify JSON-like string
        f.write(json.dumps(response, indent=4, sort_keys=True))
        f.close()


    def getPhotos(self, rover_name='curiosity', camera='navcam', ending_date=str(date.today()), num_of_days=10, max_photos=3):
        """ Main function of the class which returns JSON-like output of "date": [list_of_photos] pairs

        Search for photos is conducted for num_of_days days, starting with ending_date and counting backwards.
        For each date, function checks if a request with the same rover name, camera name and date has been cached,
        and if so, retreives the cached JSON object from a file. If the request has never been made before, function
        sends a GET request to NASA's API, receives a response and caches it in a JSON file.
        For each request, a JSON object is returned which contains list of photos.
        Each photo in the list is an object that looks like the following
        {
            "camera" :  {
                ...
            },
            "earh_date": "yyyy-mm-dd",
            "id": 123456,
            "img src": "http://...JPG",
            "rover": {
                ...
            },
            "sol": 123
        }

        A bunch of inormation can be extracted from there, but we are only interested in the image source link.
        Since JSON objects naturally map to Python dicts, response is treated as a dict and parsed as one.
        An entry is created for each date of interest in the output dict, and with it an empty list. This list
        is then filled with image source links. At the end of the execution, function prints a prettyfied JSON string

        Parameters
        ----------
        rover_name - string containing the name of the rover. One of the following: curiosity, opportunity, spirit
        camera - name of the rover camera. The following are allowed: fhaz, rhaz, mast, chemcam, mahli, mardi, navcam, pancam, minites
        ending_date - string containing ending date of interest in format 'YYYY-MM-DD'
        num_of_days - number of days functions returns to the past to get photos from
        max_photos - how many photos should be returned for each date (it might happen that there are actually less photos than this)

        Returns
        -------
        None - prints out prettyfied JSON string
        """
        # Create a dict in which the output will be saved in "date": [list_of_photos] pairs
        output = {}
        # Getting photos for the last num_of_days days
        for i in range(num_of_days):
            # Calculate the exact date, starting from ending_date and going back day by day
            # through iterations, and convert it to a string
            day = str(datetime.strptime(ending_date, "%Y-%m-%d").date() - timedelta(days = i))

            # If we already queried this exact rover, camera and date, they are cached in
            # a JSON file
            if self.queryIsCached(rover_name, camera, day):
                f = open(f"./cache/{rover_name}_{camera}_{day}.json")
                response = json.load(f)
                f.close()
            else:
                # if not, send a GET request to NASA's API and cache the results
                query_string = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover_name}/photos?earth_date={day}&camera={camera}&api_key=DEMO_KEY"
                response = requests.get(query_string).json()
                # Cache just non-error responses
                if 'error' not in response.keys():
                    self.cacheQuery(rover_name, camera, day, response)

            # Create an entry for this date in the dict
            output[day] = []

            # Go through photos in the list (if any) and append their links
            # to the list of photos for this date, and do this for min(max_photos, len(r["photos"])) photos.
            # If an error response occurs, indicate it.
            if 'error' in response.keys():
                output[day].append(response["error"]["code"])
            elif len(response["photos"]) > 0:
                for j in range(min(max_photos, len(response["photos"]))):
                    output[day].append(response["photos"][j]["img_src"])

        print(f"\nOutput for the past *{num_of_days}* days ending on *{ending_date}* for *{camera}* camera from *{rover_name}* rover\n")
        print(json.dumps(output, indent=4, sort_keys=True))


# Create a rover object and execute the search for photos
rover = NASARoverAPI()
rover.getPhotos()
