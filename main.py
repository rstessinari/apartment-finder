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


train_stations_nearby_bristol_dict = {
    # 'Severn Beach' : 'BS35 4PL',
    # 'St Andrews Road' : 'BS11 9BT',
    # 'Avonmouth' : 'BS11 9JB',
    # 'Shirehampton' : 'BS11 9XB',
    # 'Sea Mills' : 'BS9 1FF',
    'Clifton Down' : 'BS8 2PN',
    # 'Redland' : 'BS6 6QP',
    # 'Montpelier' : 'BS6 5HA',
    # 'Stapleton Road' : 'BS5 0ND',
    # 'Lawrence Hill' : 'BS5 0AF',
    # 'Temple Meads' : 'BS1 6QF',
    # 'Bedminster' : 'BS3 4DN',
    # 'Parson Street' : 'BS3 5PU'
    # 'Nailsea & Backwell' : 'BS48 3LE'
}


def get_distance_to_location(starting_postcode,ending_postcode):
    my_api_key = 'AIzaSyBgSRvBvVsKl5qqEHVPdsl1aaZRJlW0-kw'
    gmaps = googlemaps.Client(key=my_api_key)

    distance_value = -1.0
    distance_txt = 'NaN'
    try:
        directions_result = gmaps.directions(starting_postcode, ending_postcode,
                                             mode='bicycling',
                                            #  mode='transit',
                                            #  mode='walking'
                                             units='imperial',
                                            #  units='metric',
                                            )
        distance_value = float(directions_result[0]['legs'][0]['distance']['value'])
        distance_txt = directions_result[0]['legs'][0]['distance']['text']
    except:
        print('It was not possible to retrieve distance from gmaps.')
    
    return (distance_value,distance_txt)


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

    # print('The closest station from',target_postcode,'is ',closest_station,'(',station_postcode,'):', closest_station_distance_in_miles)
    return (closest_station,closest_station_distance_in_miles)

import re
import googlemaps

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
    ratio = ''
    closest_train_station_name = ''
    closest_train_station_distance = ''

    def set_soup(self,soup):
        self.soup = soup

    def set_info(self):
        self.set_title()
        self.set_id()
        self.set_postal_code()
        self.set_gmaps_link()
        self.set_route_to_lab()
        self.set_distance_to_lab()
        self.set_rent()
        self.set_rooms()
        self.set_zoopla_link()
        self.set_ratio()
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
        result = result + 'The ratio is: %s\n' % self.get_ratio()
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
    
    def set_id(self):
        pattern = re.compile('\"id\":\s(\d+),')
        script = self.soup.find('script', text=pattern)
        if script:
            match = pattern.search(script.text)
            if match:
                self.prop_id = match.group(1)
    
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
    
    def set_ratio(self):
        ratio = self.distance_value/1000/1.6 * float(self.rent_pcm) / float(self.num_beds)
        self.ratio = '%.1f' % ratio
    
    def get_ratio(self):
        return self.ratio
    
    def print_zoopla_link(self):
        print('Zoopla Link: %s' % self.get_zoopla_link())
    
    def send_property_by_email(self):
        title = 'New interesting property: '+self.title
        msg = self.get_info()
        send_email('zeibzon2@gmail.com','Z7YSEw0@EufxDhl9',['rodrigostange@gmail.com','rsc.segatto@gmail.com'],title,msg)

    def isWorthy(self, value):
        if float(self.get_ratio()) < (value):
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


if __name__ == "__main__":
    # result = find_closest_train_station('BS3 5LY')
    # print(result[0])
    # print(result[1])
    import requests
    from bs4 import BeautifulSoup
    res = requests.get('https://www.zoopla.co.uk/to-rent/details/51602204')
    bs = BeautifulSoup(res.text, 'lxml')
    # print(bs.prettify())

    prop = Property()
    prop.set_soup(bs)
    prop.set_info()
    prop.print_info()