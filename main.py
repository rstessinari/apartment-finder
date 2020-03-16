
#!/usr/bin/python3

from bs4 import BeautifulSoup
from click import command, option
from os import makedirs
from os.path import exists, join
from time import sleep
import googlemaps
import pandas as pd
import re
import requests


ANALYZED_DATAFRAME = 'analyzed_properties.xlsx'
FORCE_REFRESH = False
DATA_FOLDER = 'properties'
KNOWN_PROPERTIES = join(DATA_FOLDER, '_known_properties.txt')
WATCH_MODE = False
ZOOPLA_IDS_MAIN_PAGE_MATCH = '\"id\": \"([0-9]*)\",'


class Property:
    prop_id = ''
    title = ''
    details_tag = ''
    soup = ''
    postalcode = ''
    incode = ''
    outcode = ''
    url_route_to_lab = ''
    distance_txt = ''
    distance_value = -1.0
    gmaps_link = ''
    rent_pcm = ''
    num_beds = ''
    num_baths = ''
    num_recepts = ''
    zoopla_link = ''
    score = ''
    closest_train_station_name = ''
    closest_train_station_distance = ''
    pets_allowed = ''

    def __init__(self, id):
        self.prop_id = id

    def set_soup(self,soup):
        self.soup = soup

    def set_info(self):
        self.set_title()
        self.set_postal_code()
        self.set_gmaps_link()
        self.set_route_to_lab()
        self.set_distance_to_lab()
        self.set_rent()
        self.set_rooms()
        self.set_zoopla_link()
        self.set_score()
        self.set_closest_train_station()

    def get_info(self):
        result = 'Title: %s\n' % self.get_title()
        result = result + 'Id: %s\n' % self.get_id() 
        result = result + 'Postal Code: %s\n' % self.get_postal_code()
        result = result + 'Distance to the Lab: %s\n' % self.get_distance_to_lab()
        result = result + 'Rent (pcm): %s\n' % self.get_rent()
        result = result + 'Rooms: %s\n' % self.get_rooms()
        result = result + 'Google maps link: %s\n' % self.get_gmaps_link()
        result = result + 'Routes to Lab link: %s\n' % self.get_route_to_lab()
        result = result + 'Zoopla Link: %s\n' % self.get_zoopla_link()
        result = result + 'The closest train station is: %s, %s away\n' % (self.get_closest_train_station(), self.get_cloest_train_station_distance())
        result = result + 'The score is: %s\n' % self.get_score()
        return result

    def print_info(self):
        self.print_title()
        self.print_id()
        self.print_postal_code()
        self.print_distance_to_lab()
        self.print_rent()
        self.print_rooms()
        self.print_gmaps_link()
        self.print_route_to_lab()
        self.print_zoopla_link()
        
    def set_title(self):
        self.title = self.soup.title.text
    
    def get_title(self):
        return self.title
    
    def print_title(self):
        print('Title: %s' % self.get_title())

    def set_tag(self):
        tags = self.soup.find_all('script')
        for i in range(len(tags)):
            if 'ZPG.trackData.taxonomy' in str(tags[i]):
                self.details_tag = tags[i]
                break
    def get_tag(self):
        return self.details_tag
    
    def print_tag(self):
        print(self.get_tag())
    
    def get_id(self):
        return self.prop_id
    
    def print_id(self):
        print('Id: %s' % self.get_id())

    def set_postal_code(self):
        pattern = re.compile('incode:\s\"(\w+)\",')
        script = self.soup.find('script', text=pattern)
        if script:
            match = pattern.search(script.text)
            if match:
                self.incode = match.group(1)
        pattern = re.compile('outcode:\s\"(\w+)\",')
        script = self.soup.find('script', text=pattern)
        if script:
            match = pattern.search(script.text)
            if match:
                self.outcode = match.group(1)
        self.postalcode = self.outcode + ' ' + self.incode
    
    def get_postal_code(self):
        return self.postalcode

    def print_postal_code(self):
        print('Postal Code: %s' % self.get_postal_code())
    
    def set_gmaps_link(self):
        if self.set_postal_code == '':
            self.set_postal_code()
        self.gmaps_link = 'https://www.google.com/maps/place/Bristol+'+self.outcode+'+'+self.incode
    
    def get_gmaps_link(self):
        return self.gmaps_link

    def print_gmaps_link(self):
        if self.set_postal_code == '':
            self.set_postal_code()
        print('Google maps link: %s' % self.get_gmaps_link())

    def set_route_to_lab(self):
        self.url_route_to_lab = 'https://www.google.com/maps/dir/'+self.outcode+'+'+self.incode+',+Bristol,+UK/BS8+1UB,+Bristol,+UK'
    
    def get_route_to_lab(self):
        return self.url_route_to_lab

    def print_route_to_lab(self):
        print('Routes to Lab link: %s' % self.get_route_to_lab())

    def set_distance_to_lab(self):
        work_postcode = 'BS8 1UB'
        starting_postcode = self.outcode+' '+self.incode
        try:
            result = get_distance_to_location(starting_postcode,work_postcode)
            self.distance_value = result[0]
            self.distance_txt = result[1]
        except:
            print('It was not possible to retrieve distance from gmaps.')

    def get_distance_to_lab(self):
        return self.distance_txt
    
    def print_distance_to_lab(self):
        print('Distance to the Lab: %s' % self.get_distance_to_lab())

    def set_rent(self):
        pattern = re.compile('price_actual:\s(\d+),')
        script = self.soup.find('script', text=pattern)
        if script:
            match = pattern.search(script.text)
            if match:
                self.rent_pcm = match.group(1)
    def get_rent(self):
        return self.rent_pcm

    def print_rent(self):
        print('Rent (pcm): %s' % self.get_rent())

    def set_rooms(self):
        pattern = re.compile('num_beds:\s(\d+),')
        script = self.soup.find('script', text=pattern)
        if script:
            match = pattern.search(script.text)
            if match:
                self.num_beds = match.group(1)

        pattern = re.compile('num_baths:\s(\d+),')
        script = self.soup.find('script', text=pattern)
        if script:
            match = pattern.search(script.text)
            if match:
                self.num_baths = match.group(1)

        pattern = re.compile('num_recepts:\s(\d+),')
        script = self.soup.find('script', text=pattern)
        if script:
            match = pattern.search(script.text)
            if match:
                self.num_recepts = match.group(1)

        if self.num_beds == '':
            self.num_beds = '?'
        if self.num_baths == '':
            self.num_baths = '?'
        if self.num_recepts == '':
            self.num_recepts = '?'

        self.rooms = '%s bedrooms / %s receptions / %s bathrooms' % (self.num_beds, self.num_recepts, self.num_baths)
        # print(self.rooms)

    def get_rooms(self):
        return self.rooms
    
    def print_rooms(self):
        print('Rooms: %s' % self.rooms)

    def set_zoopla_link(self):
        self.zoopla_link = 'https://www.zoopla.co.uk/to-rent/details/%s' % self.prop_id
    
    def get_zoopla_link(self):
        return self.zoopla_link
    
    def set_score(self):
        score = self.distance_value/1000/1.6 * float(self.rent_pcm) / float(self.num_beds)
        self.score = '%.1f' % score
    
    def get_score(self):
        return self.score
    
    def print_zoopla_link(self):
        print('Zoopla Link: %s' % self.get_zoopla_link())
    
    def send_property_by_email(self):
        title = 'New interesting property: '+self.title
        msg = self.get_info()
        send_email('zeibzon2@gmail.com','Z7YSEw0@EufxDhl9',['rodrigostange@gmail.com','rsc.segatto@gmail.com'],title,msg)

    def isWorthy(self, value):
        if float(self.get_score()) < (value):
            return True
        else:
            return False

    def set_closest_train_station(self):
        result = find_closest_train_station(self.postalcode)
        self.closest_train_station_name = result[0]
        self.closest_train_station_distance = result[1]

    def get_closest_train_station(self):
        return self.closest_train_station_name
    
    def get_cloest_train_station_distance(self):
        return self.closest_train_station_distance
        
    def print_closest_train_station(self):
        print('The closest station is',self.closest_train_station_name,'. ',closest_station_distance_in_miles,'away.')


train_stations_nearby_bristol_dict = {
    # 'Severn Beach' : 'BS35 4PL',
    'St Andrews Road' : 'BS11 9BT',
    'Avonmouth' : 'BS11 9JB',
    'Shirehampton' : 'BS11 9XB',
    'Sea Mills' : 'BS9 1FF',
    'Clifton Down' : 'BS8 2PN',
    'Redland' : 'BS6 6QP',
    'Montpelier' : 'BS6 5HA',
    'Stapleton Road' : 'BS5 0ND',
    'Lawrence Hill' : 'BS5 0AF',
    'Temple Meads' : 'BS1 6QF',
    'Bedminster' : 'BS3 4DN',
    'Parson Street' : 'BS3 5PU'
    # 'Nailsea & Backwell' : 'BS48 3LE'
}


def send_email(user, pwd, recipient, subject, body):
    import smtplib

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        return 'successfully sent the mail'
    except:
        return 'failed to send mail'

    # usage
    # title = 'New interesting property: '
    # msg = 'testing'
    # send_email('zeibzon2@gmail.com','Z7YSEw0@EufxDhl9',['rodrigostange@gmail.com'],title,msg)


def find_closest_train_station(starting_postcode):
    min_distance_value = 99999.9 # in meters
    closest_station = ''
    closest_station_distance_in_miles = ''

    for station in train_stations_nearby_bristol_dict:
        station_postcode = train_stations_nearby_bristol_dict[station]
        result = get_distance_to_location(starting_postcode,station_postcode)
        if result[0] < min_distance_value:
            min_distance_value = result[0]
            closest_station = station
            closest_station_distance_in_miles = result[1]
        sleep(0.1)

    # print('The closest station from',target_postcode,'is ',closest_station,'(',station_postcode,'):', closest_station_distance_in_miles)
    return (closest_station,closest_station_distance_in_miles)


def get_distance_to_location(starting_postcode,ending_postcode):
    my_api_key = open('google_api_key', 'r').read()
    gmaps = googlemaps.Client(key=my_api_key)

    distance_value = -1.0
    distance_txt = 'NaN'
    try:
        directions_result = gmaps.directions(starting_postcode, ending_postcode,
                                            #  mode='bicycling',
                                            #  mode='transit',
                                             mode='walking',
                                             units='imperial'
                                            #  units='metric',
                                            )
        distance_value = float(directions_result[0]['legs'][0]['distance']['value'])
        distance_txt = directions_result[0]['legs'][0]['distance']['text']
    except:
        print('It was not possible to retrieve distance from gmaps.')
    
    return (distance_value,distance_txt)


def get_ids_from_zoopla_main_page(text):
    matchObj = re.findall(ZOOPLA_IDS_MAIN_PAGE_MATCH, text)
    return matchObj


def create_link(city, beds_max, beds_min, pets_allowed, price_max, price_min, radius, pn):
    link = "https://www.zoopla.co.uk/to-rent/property/{}/?beds_max={}&beds_min={}&pets_allowed={}&price_frequency=per_month&price_max={}&price_min={}&q={}&radius={}&results_sort=newest_listings&page_size=100&pn={}&search_source=facets".format(
    city, beds_max, beds_min, pets_allowed, price_max, price_min, city, radius, pn)
    return link


def scavenge_zoopla(city = "Bristol", beds_max = 4, beds_min = 2, pets_allowed = True, price_max = 1400, price_min = 800, radius = 0):
    print("Looking for properties to rent on Zoopla with the following parameters:\n\tCity: {}\n\tBedrooms: {} - {}\n\tPrice range: £{} - £{}\n\tOther: Pets? {}".format(
          city, beds_min, beds_max, price_min, price_max, pets_allowed))
    pn = 1
    link = create_link(city, beds_max, beds_min, pets_allowed, price_max, price_min, radius, pn)
    print("\tSearch link: {}".format(link), flush=True)
    res = requests.get(link)
    id_lst = get_ids_from_zoopla_main_page(res.text)

    if "Pages:" in res.text:
        pn = pn + 1
        while ">Next</a>" in res.text:
            link = create_link(city, beds_max, beds_min, pets_allowed, price_max, price_min, radius, pn)
            print("\tNext Page: {}".format(link), flush=True)
            res = requests.get(link)
            id_lst = id_lst + get_ids_from_zoopla_main_page(res.text)
            pn = pn + 1
    
    return list(set(id_lst))





def check_and_create_folder(folder):
    if not exists(folder):
        makedirs(folder)





def test_train_station_distance(postcode):
    result = find_closest_train_station(postcode)
    print(result[0])
    print(result[1])


def test_property_list_scrapping(id_lst, data_folder):
    for id in id_lst:
        print("\n--- property {} ---".format(id))
        with open(join(data_folder,"{}.html".format(id)), "r") as file:
            data = file.read()
            bs = BeautifulSoup(data, 'lxml')
            prop = Property(id)
            prop.set_soup(bs)
            prop.set_info()
            print(prop.get_info())


def filter_new_ids(id_lst, known_prop_filename):
    print("\nFiltering new properties only. Reading file \"{}\".".format(known_prop_filename), flush=True)
    try:
        with open(known_prop_filename, "r") as file:
            data = file.read()
            known_ids = data.split(';')
            print(known_ids)
            print("Found {} properties already saved.".format(len(known_ids)-1))
    except: # noqa
        print("Cannot open file \"{}\". No properties saved.".format(known_prop_filename))
        known_ids = []

    new_ids = list(set(id_lst) - set(known_ids))
    print("Found {} new properties.".format(len(new_ids)))
    return new_ids


def add_property_to_dataframe(property, df):
    property = Property(12)
    prop_dict = {"id": property.prop_id,
                 "postcode": property.postalcode,
                 "distance to lab": property.distance_value,
                 "rent (pcm)": property.rent_pcm,
                 "bedrooms": property.num_beds,
                 "receptions": property.num_recepts,
                 "bathrooms": property.num_baths,
                 "closest train station": property.closest_train_station_distance,
                 "score": property.score,
                 "link gmaps": property.gmaps_link,
                 "link routes": property.url_route_to_lab,
                 "link ad": property.zoopla_link,
                 "title": property.title
                }
    print(prop_dict)
    df.append(prop_dict, ignore_index=True)
    print(df, flush=True)
    return df
    # sys.exit()


# def analyze_properties_known(data_folder, known_prop_filename):
#     print("Retrieving known properties list from \"{}\"".format(known_prop_filename), flush=True)
#     try:
#         with open(known_prop_filename, "r") as file:
#             data = file.read()
#             known_ids = data.split(';')
#     except: # noqa
#         print("Cannot open file \"{}\". No properties can be analyzed.".format(known_prop_filename))
#         return False

#     print("Analyzing {} properties".format(len(known_ids)-1))
#     # df = pd.read_excel(ANALYZED_DATAFRAME)
#     for id in known_ids:
#         if id == '':
#             continue
#         else:
#             analize_property(id, data_folder)
            # def analize_property(data_folder, id):
            #     # print("--- Analyzing property {} ---".format(id))
            #     # try:
            #     #     with open(join(data_folder,"{}.html".format(id)), "r") as file:
            #     #         data = file.read()
            #     #         # bs = BeautifulSoup(data, 'lxml')
            #     #         # get_ids_from_zoopla_soup(bs)
            #     #         get_ids_from_zoopla_main_page(data)
            #     # except: # noqa
            #     #     print("Cannot open id {} in folder \"{}\"".format(id, data_folder))

            #     print("\n--- property {} ---".format(id))
            #     with open(join(data_folder,"{}.html".format(id)), "r") as file:
            #         data = file.read()
            #         bs = BeautifulSoup(data, 'lxml')
            #         prop = Property(id)
            #         prop.set_soup(bs)
            #         prop.set_info()
            #         print(prop.get_info())
            #         # df = add_property_to_dataframe(prop,df)
            #         # print(df)
            #         # preciso salvar as propriedades em algum lugar. Dataframe provavelmente

            #     # df.to_excel("output.xlsx")


def run(data_folder, known_prop_filename):
    # test_train_station_distance('BS3 5LY')
    # test_property_list_scrapping([49627231, 50896995], data_folder)

    city = "Bristol"
    beds_min = 3
    beds_max = 3
    pets_allowed = True
    price_min = 800
    price_max = 1150
    radius = 0 # 0 means no restriction

    id_lst = scavenge_zoopla(city, beds_max, beds_min, pets_allowed, price_max, price_min, radius)
    print("\n** Found {} properties **".format(len(id_lst)))

    ids_to_download = filter_new_ids(id_lst, known_prop_filename)

    # # create a list of already downloaded ids.
    # known_prop_lst = 

    # downloads data from new not-saved properties
    if ids_to_download != []:
        download_data_zoopla(ids_to_download, data_folder, known_prop_filename)

    # analyse files
    analyze_properties_known(data_folder, known_prop_filename)

    print("Job done.")


    # 30704703


def find_prop_in_database(known_prop_filename, id_lst):
    # check list against ids in the file ^
    # return only the non-existing
    return id_lst


def download_data_zoopla(data_folder, known_prop_filename, ids_to_download):
    check_and_create_folder(data_folder)
    print("Saving them in {}".format(data_folder))

    for id in ids_to_download:
        print("--- property {} ---".format(id))
        res = requests.get('https://www.zoopla.co.uk/to-rent/details/{}'.format(id))
        if res.ok:
            with open(join(data_folder,"{}.html".format(id)), "w") as file:
                file.write(res.text)
                file.close()

        # add id to known_list:
        with open(known_prop_filename, "a") as file:
            file.write("{};".format(id))
            file.close()


def show_properties(data_folder, id_lst):
    for id in id_lst:
        print("--- Analysing property {} ---".format(id))
        try:
            with open(join(data_folder,"{}.html".format(id)), "r") as file:
                data = file.read()
                bs = BeautifulSoup(data, 'lxml')
                prop = Property(id)
                prop.set_soup(bs)
                prop.set_info()
                print(prop.get_info())
        except: # noqa
            print("Cannot open property {} in folder \"{}\"".format(id, data_folder))


def analise_properties(data_folder, known_prop_filename, id_lst, refresh):
    print("Analysing {} properties".format(len(id_lst)))
    if refresh:
        ids_to_download = id_lst
    else:
        # check if id exists in the known_prop_filename. gets back only the new ones
        ids_to_download = find_prop_in_database(known_prop_filename, id_lst)
    
    download_data_zoopla(data_folder, known_prop_filename, ids_to_download)
    show_properties(data_folder, id_lst)


@command()
@option(
    "-f",
    "--find",
    default=0,
    help="Find one especific property from zoopla.",
)
@option(
    "-r",
    "--refresh",
    default=FORCE_REFRESH,
    help="If True, forces the download the property even if it already exists in the database.",
)
# @option(
#     "-w",
#     "--watch",
#     default=WATCH_MODE,
#     help="",
# )
def main(
    find=0,
    refresh=FORCE_REFRESH,
):
    """It should find a nice home for you ;)
    """
    data_folder = DATA_FOLDER
    known_prop_filename = KNOWN_PROPERTIES
    if find != 0:
        id_lst = [find]
        analise_properties(data_folder, known_prop_filename, id_lst, refresh)

    else:
        run(data_folder, known_prop_filename)


if __name__ == "__main__":
    main()
