#!/usr/bin/env python3
from ebaysdk.finding import Connection

if __name__ == '__main__':
    api = Connection(domain='svcs.sandbox.ebay.com', config_file='test_yaml.yaml', debug=True, siteid="EBAY-US", https=True)

    request = {
        'keywords': 'basketball',
        'itemFilter': [
            {'name': 'condition', 'value': 'new'}
        ],
        'paginationInput': {
            'entriesPerPage': 10,
            'pageNumber': 1
        },
        'sortOrder': 'PricePlusShippingLowest'
    }

    response = api.execute('findItemsByKeywords', request)
    print(response.dict())