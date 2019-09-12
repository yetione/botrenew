import json
import sys
import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError

config = json.load(open('./config.json'))
supported_zones = ['mobiumapps.com', 'mobium.pro']
domain = str(sys.argv[1])
new_key = str(sys.argv[2])
try:
    searchable_zone = supported_zones[supported_zones.index('.'.join(domain.split('.')[-2:]))]
except ValueError:
    exit(1)
cf = CloudFlare.CloudFlare(email=config['username'], token=config['api_key'])

try:
    zone = cf.zones.get(params={'name':searchable_zone})
except CloudFlareAPIError as e:
    exit('/zones.get %d %s - api call failed' % (e, e))
except Exception as e:
    exit('/zones.get - %s - api call failed' % (e))
zone = zone[0]
try:
    dns = cf.zones.dns_records.get(zone['id'], params={'type':'TXT', 'per_page':100})
except CloudFlareAPIError as e:
    exit('/zones/dns_records.get %d %s - api call failed' % (e, e))
except Exception as e:
    exit('/zones/dns_records.get - %s - api call failed' % (e))
acme_record = None
record_name = '_acme-challenge.'+str(domain)
for record in dns:
    if record['name'] == record_name:
        acme_record = record
        break
if acme_record is None:
    try:
        res = cf.zones.dns_records.post(zone['id'], data={
            'type': 'TXT',
            'name': record_name,
            'content': new_key,
            'proxied': False,
        })
    except CloudFlareAPIError as e:
        exit('/zones/dns_records.post %d %s - api call failed' % (e, e))
    except Exception as e:
        exit('/zones/dns_records.post - %s - api call failed' % (e))
else:
    try:
        res = cf.zones.dns_records.put(zone['id'], acme_record['id'], data={
            'type': 'TXT',
            'name': record_name,
            'content': new_key,
            'proxied': False,
        })
    except CloudFlareAPIError as e:
        exit('/zones/dns_records.put %d %s - api call failed' % (e, e))
    except Exception as e:
        exit('/zones/dns_records.put - %s - api call failed' % (e))
exit(0)

# sudo certbot renew --preferred-challenges=dns --cert-name panel.pre.mobiumapps.com --force-renew --manual-auth-hook ./authentificator.sh --manual-public-ip-logging-ok