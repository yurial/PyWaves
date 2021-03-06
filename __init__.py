# Copyright (C) 2017 YuWaves Developers
#
# This file is part of YuWaves.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-bitcoinlib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

from __future__ import absolute_import, division, print_function, unicode_literals

DEFAULT_TX_FEE = 100000
DEFAULT_ASSET_FEE = 100000000
DEFAULT_MATCHER_FEE = 300000
DEFAULT_LEASE_FEE = 100000
DEFAULT_ALIAS_FEE = 100000
DEFAULT_SPONSOR_FEE = 100000000
DEFAULT_SCRIPT_FEE = 100000
DEFAULT_ASSET_SCRIPT_FEE = 100000000
VALID_TIMEFRAMES = (5, 15, 30, 60, 240, 1440)
MAX_WDF_REQUEST = 100

THROW_EXCEPTION_ON_ERROR = True

import requests

from .address import *
from .asset import *
from .order import *

OFFLINE = False
NODE = 'https://nodes.wavesnodes.com'

ADDRESS_VERSION = 1
ADDRESS_CHECKSUM_LENGTH = 4
ADDRESS_HASH_LENGTH = 20
ADDRESS_LENGTH = 1 + 1 + ADDRESS_CHECKSUM_LENGTH + ADDRESS_HASH_LENGTH

CHAIN = 'mainnet'
CHAIN_ID = 'W'
#MATCHER = 'https://nodes.wavesnodes.com'
MATCHER = 'http://matcher.wavesnodes.com'
MATCHER_PUBLICKEY = ''

DATAFEED = 'http://marketdata.wavesplatform.com'

logging.getLogger("requests").setLevel(logging.WARNING)
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class YuWavesException(ValueError):
    pass


def throw_error(msg):
    if THROW_EXCEPTION_ON_ERROR:
        raise YuWavesException(msg)


def setThrowOnError(throw=True):
    global THROW_EXCEPTION_ON_ERROR
    THROW_EXCEPTION_ON_ERROR = throw


def setOffline():
    global OFFLINE
    OFFLINE = True

def setOnline():
    global OFFLINE
    OFFLINE = False

def setChain(chain = CHAIN, chain_id = None):
    global CHAIN, CHAIN_ID

    if chain_id is not None:
        CHAIN = chain
        CHAIN_ID = chain_id
    else:
        if chain.lower()=='mainnet' or chain.lower()=='w':
            CHAIN = 'mainnet'
            CHAIN_ID = 'W'
        elif chain.lower()=='hacknet' or chain.lower()=='u':
            CHAIN = 'hacknet'
            CHAIN_ID = 'U'
        else:
            CHAIN = 'testnet'
            CHAIN_ID = 'T'

def getChain():
    return CHAIN

def setNode(node = NODE, chain = CHAIN, chain_id = None):
    global NODE, CHAIN, CHAIN_ID
    NODE = node
    setChain(chain, chain_id)

def getNode():
    return NODE

MATCHER_ASSET_PRIORITY = {}

def getMatcherSettings():
    return wrapper('/matcher/settings', host=MATCHER, headers={'Accept': 'application/json'})

def getAssetPriority(asseId):
    if asseId in MATCHER_ASSET_PRIORITY:
        return MATCHER_ASSET_PRIORITY[asseId]
    return 0

def setMatcher(node = MATCHER):
    global MATCHER, MATCHER_PUBLICKEY, MATCHER_ASSET_PRIORITY
    MATCHER_PUBLICKEY = wrapper('/matcher', host = node)
    MTCHER = node
    logging.info('Setting matcher %s %s' % (MATCHER, MATCHER_PUBLICKEY))
    priceAssets = getMatcherSettings()['priceAssets']
    priceAssets.reverse()
    for i, asset in enumerate(priceAssets):
        MATCHER_ASSET_PRIORITY[asset] = i+1
        if asset == 'WAVES':
            MATCHER_ASSET_PRIORITY[''] = MATCHER_ASSET_PRIORITY[asset]

def setDatafeed(wdf = DATAFEED):
    global DATAFEED
    DATAFEED = wdf
    logging.info('Setting datafeed %s ' % (DATAFEED))

def wrapper(api, postData='', host='', headers='', timeout=10):
    global OFFLINE
    if OFFLINE:
        offlineTx = {}
        offlineTx['api-type'] = 'POST' if postData else 'GET'
        offlineTx['api-endpoint'] = api
        offlineTx['api-data'] = postData
        return offlineTx
    if not host:
        host = NODE
    if postData:
        logging.debug('POST: {}'.format(postData))
        req = requests.post('%s%s' % (host, api), data=postData, headers={'content-type': 'application/json'}, timeout=timeout).json()
    else:
        req = requests.get('%s%s' % (host, api), headers=headers, timeout=timeout).json()
    return req

def height():
    return wrapper('/blocks/height')['height']

def lastblock():
    return wrapper('/blocks/last')

def block(n):
    return wrapper('/blocks/at/%d' % n)

def tx(id):
    return wrapper('/transactions/info/%s' % id)

def getOrderBook(assetPair):
    orderBook = assetPair.orderbook()
    try:
        bids = orderBook['bids']
        asks = orderBook['asks']
    except:
        bids = ''
        asks = ''
    return bids, asks

def symbols():
    return wrapper('/api/symbols', host=DATAFEED)

def markets():
    return wrapper('/api/markets', host=DATAFEED)

def validateAddress(address):
    addr = crypto.bytes2str(base58.b58decode(address))
    if addr[0] != chr(ADDRESS_VERSION):
        logging.error("Wrong address version")
    elif addr[1] != CHAIN_ID:
        logging.error("Wrong chain id")
    elif len(addr) != ADDRESS_LENGTH:
        logging.error("Wrong address length")
    elif addr[-ADDRESS_CHECKSUM_LENGTH:] != crypto.hashChain(crypto.str2bytes(addr[:-ADDRESS_CHECKSUM_LENGTH]))[:ADDRESS_CHECKSUM_LENGTH]:
        logging.error("Wrong address checksum")
    else:
        return True
    return False

WAVES = Asset('')
BTC = Asset('8LQW8f7P5d5PZM7GtZEBgaqRPGSzS3DfPuiXrURJ4AJS')
BCH = Asset('zMFqXuoyrn5w17PFurTqxB7GsS71fp9dfk6XFwxbPCy')
BSV = Asset('62LyMjcr2DtiyF5yVXFhoQ2q414VPPJXjsNYp72SuDCH')
LTC = Asset('HZk1mbfuJpmxU1Fs4AX5MWLVYtctsNcg6e2C6VKqK8zk')
ETH = Asset('474jTeYx2r2Va35794tCScAXWJG9hU2HcgxzMowaZUnu')
XMR = Asset('5WvPKSJXzVE2orvbkJ8wsQmmQKqTv9sGBPksV4adViw3')
DASH = Asset('B3uGHFRpSUuGEDWjqB9LWWxafQj8VTvpMucEyoxzws5H')
TRY = Asset('2mX5DzVKWrAJw8iwdJnV2qtoeVG9h5nTDpTqC1wb1WEN')
CNY = Asset('DEJbZipbKQjwEiRjx2AqQFucrj5CZ3rAc4ZvFM8nAsoA')
EUR = Asset('Gtb1WRznfchDnTh37ezoDTJ4wcoKaRsKqKjJjy7nm2zU')
USD = Asset('Ft8X1v1LTa1ABafufpaCWyVj8KkaxUWE6xBhW6sNFJck')
VST = Asset('4LHHvYGNKJUg5hj65aGD5vgScvCBmLpdRFtjokvCjSL8')

