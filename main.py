import requests
import json
import sys
import time
config = json.load(open('./config.json'))
supported_zones = ['mobiumapps.com', 'mobium.pro']
domain = str(sys.argv[1])
new_key = str(sys.argv[2])
try:
    searchable_zone = supported_zones[supported_zones.index('.'.join(domain.split('.')[-2:]))]
except ValueError:
    exit(1)


class CloudFlareAPI:

    def __init__(self, email, api_key):
        self.headers = {
            'Content-Type': 'application/json',
            'X-Auth-Email': email,
            'X-Auth-key': api_key
        }

    def find_zone(self, zone_name):
        """

        :type zone_name: str
        """
        response = requests.get('https://api.cloudflare.com/client/v4/zones', headers=self.headers,
                                params={'name': zone_name})
        data = response.json()
        for zone in data['result']:  # type: object
            if zone['name'] == zone_name:
                return zone
        return None

    def get_zone_dns(self, zone, domain):
        params = {
            'type': 'TXT',
            'per_page': 100
        }
        response = requests.get('https://api.cloudflare.com/client/v4/zones/' + str(zone['id']) + '/dns_records',
                           headers=self.headers, params=params)
        data = response.json()
        for dns in data['result']:
            if dns['name'] == '_acme-challenge.'+str(domain):
                return dns
        return None

    def create_dns_recod(self, zone, domain, value):
        params = {
            'type':'TXT',
            'name':'_acme-challenge.'+str(domain),
            'content':value,
            'proxied': False,
        }
        response = requests.post('https://api.cloudflare.com/client/v4/zones/'+str(zone['id'])+'/dns_records', json=params, headers=self.headers)
        data = response.json()
        return data

    def update_dns_record(self, zone, dns, domain, value):
        params = {
            'type': 'TXT',
            'name': '_acme-challenge.' + str(domain),
            'content': value,
            'proxied': False,
        }
        response = requests.put('https://api.cloudflare.com/client/v4/zones/' + str(zone['id']) + '/dns_records/'+str(dns['id']),
                                 json=params, headers=self.headers)
        data = response.json()
        return  data


api = CloudFlareAPI(config['username'], config['api_key'])
zone = api.find_zone(searchable_zone)
if (zone is not None):
    dns = api.get_zone_dns(zone, domain)
    if dns is not None:
        api.update_dns_record(zone, dns, domain, new_key)
    else:
        api.create_dns_recod(zone, domain, new_key)
    time.sleep(10)
# sudo certbot renew --preferred-challenges=dns --cert-name panel.pre.mobiumapps.com --force-renew --manual-auth-hook ./authentificator.sh --manual-public-ip-logging-ok