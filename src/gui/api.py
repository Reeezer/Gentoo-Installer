import requests
import xml.etree.ElementTree as ET


class Region:
    def __init__(self, name):
        self.name = name
        self.countries = []
    def addCountry(self, root: ET):
        self.countries.append(Country(root))

class Country:
    def __init__(self, root: ET):
        self.name = root.attrib["countryname"]
        self.mirrors = []
        for mirror_ET in root:
            self.mirrors.append(Mirror(mirror_ET))

class Mirror:
    def __init__(self, root:ET):
        self.name = root[0].text
        self.uris = []
        for uri_ET in root.iter("uri"):
            self.uris.append(uri_ET.text)


def get_mirrors():

    r = requests.get('https://api.gentoo.org/mirrors/distfiles.xml')
    root = ET.fromstring(r.content)
    regions = {}
    for country_ET in root:
        region_name = country_ET.attrib["region"]
        if region_name not in regions:
            regions[region_name] = Region(region_name)
        else:
            regions[region_name].addCountry(country_ET)
    return regions.values()


if __name__ == '__main__':
    for region in get_mirrors():
        print(region.name)
        for country in region.countries:
            print("\t"+country.name)
            for mirror in country.mirrors:
                print("\t\t" + mirror.name)
                for uri in mirror.uris:
                    print("\t\t\t" + uri)