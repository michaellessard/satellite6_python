#!/usr/bin/env python

# example taken from : https://access.redhat.com/documentation/en-us/red_hat_security_data_api/0.1/html-single/red_hat_security_data_api/#example_script

from __future__ import print_function
import sys
import requests
from datetime import datetime, timedelta

API_HOST = 'https://access.redhat.com/labs/securitydataapi'


def get_data(query):

    full_query = API_HOST + query
    r = requests.get(full_query)

    if r.status_code != 200:
        print('ERROR: Invalid request; returned {} for the following '
              'query:\n{}'.format(r.status_code, full_query))
        sys.exit(1)

    if not r.json():
        print('No data returned with the following query:')
        print(full_query)
        sys.exit(0)

    return r.json()


# Get a list of issues and their impacts for RHSA-2016:1847
endpoint = '/cve.json'
params = 'advisory=RHSA-2016:1847'

data = get_data(endpoint + '?' + params)

for cve in data:
    print(cve['CVE'], cve['severity'])


print('-----')
# Get a list of kernel advisories for the last 30 days and display the
# packages that they provided.
endpoint = '/cvrf.json'
date = datetime.now() - timedelta(days=30)
params = 'package=kernel&after=' + str(date.date())

data = get_data(endpoint + '?' + params)

kernel_advisories = []
for advisory in data:
    print(advisory['RHSA'], advisory['severity'], advisory['released_on'])
    print('-', '\n- '.join(advisory['released_packages']))
    kernel_advisories.append(advisory['RHSA'])


print('-----')
# From the list of advisories saved in the previous example (as
# `kernel_advisories`), get a list of affected products for each advisory.
endpoint = '/cvrf/'

for advisory in kernel_advisories:
    data = get_data(endpoint + advisory + '.json')
    print(advisory)

    product_branch = data['cvrfdoc']['product_tree']['branch']
    for product_branch in data['cvrfdoc']['product_tree']['branch']:

        if product_branch['type'] == 'Product Family':

            if type(product_branch['branch']) is dict:
                print('-', product_branch['branch']['full_product_name'])

            else:
                print('-', '\n- '.join(pr['full_product_name'] for
                                       pr in product_branch['branch']))
