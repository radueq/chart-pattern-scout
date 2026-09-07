"""
Watchlist Chart Pattern Scout - ~90 tickere din XTB + 6 crypto.
Simbolurile sunt mapate la formatul Yahoo Finance.
Cheia e simbolul Yahoo; valoarea e numele afisat + sectorul (pt analiza paralela).
"""

# sector -> ETF/index de referinta pentru analiza paralela
SECTOR_BENCHMARKS = {
    'semiconductors': 'SOXX',
    'networking_fiber': 'SOXX',
    'cooling_electric': 'XLI',
    'chemicals': 'XLB',
    'energy_power': 'XLE',
    'robotics': 'BOTZ',
    'software_cloud': 'XLK',
    'fintech_crypto': 'FDN',
    'healthcare': 'XLV',
    'consumer': 'XLY',
    'crypto': 'BTC-USD',
}

TICKERS = {
    # semiconductors / memory / OSAT
    '000660.KS': {'name': 'SK Hynix', 'sector': 'semiconductors'},  # listat pe KRX (Seul), nu are ADR US lichid
    'MU': {'name': 'Micron', 'sector': 'semiconductors'},
    'AMD': {'name': 'AMD', 'sector': 'semiconductors'},
    'NVDA': {'name': 'Nvidia', 'sector': 'semiconductors'},
    'QCOM': {'name': 'Qualcomm', 'sector': 'semiconductors'},
    'ARM': {'name': 'ARM Holdings', 'sector': 'semiconductors'},
    'AVGO': {'name': 'Broadcom', 'sector': 'semiconductors'},
    'MRVL': {'name': 'Marvell', 'sector': 'semiconductors'},
    'AMKR': {'name': 'Amkor Technology', 'sector': 'semiconductors'},
    'ASX': {'name': 'ASE Technology', 'sector': 'semiconductors'},
    'GFS': {'name': 'GlobalFoundries', 'sector': 'semiconductors'},
    'COHR': {'name': 'Coherent', 'sector': 'semiconductors'},
    'TSEM': {'name': 'Tower Semiconductor', 'sector': 'semiconductors'},
    'AAOI': {'name': 'Applied Optoelectronics', 'sector': 'semiconductors'},
    'MTSI': {'name': 'MACOM Technology', 'sector': 'semiconductors'},

    # networking / fiber / componente
    'LITE': {'name': 'Lumentum', 'sector': 'networking_fiber'},
    'APH': {'name': 'Amphenol', 'sector': 'networking_fiber'},
    'FN': {'name': 'Fabrinet', 'sector': 'networking_fiber'},
    'CRDO': {'name': 'Credo Technology', 'sector': 'networking_fiber'},
    'ROG': {'name': 'Rogers Corp', 'sector': 'networking_fiber'},
    'VICR': {'name': 'Vicor Corp', 'sector': 'networking_fiber'},
    'MPWR': {'name': 'Monolithic Power Systems', 'sector': 'networking_fiber'},

    # cooling & electric / industrial
    'NVT': {'name': 'nVent Electric', 'sector': 'cooling_electric'},
    'TT': {'name': 'Trane Technologies', 'sector': 'cooling_electric'},
    'WDC': {'name': 'Western Digital', 'sector': 'cooling_electric'},
    'SPXC': {'name': 'SPX Technologies', 'sector': 'cooling_electric'},
    'MOD': {'name': 'Modine Manufacturing', 'sector': 'cooling_electric'},
    'EME': {'name': 'EMCOR Group', 'sector': 'cooling_electric'},

    # chemicals
    'CC': {'name': 'Chemours', 'sector': 'chemicals'},
    'ENTG': {'name': 'Entegris', 'sector': 'chemicals'},
    'MRK': {'name': 'Merck', 'sector': 'chemicals'},
    'LIN': {'name': 'Linde', 'sector': 'chemicals'},
    'MRSN': {'name': 'Mersen', 'sector': 'chemicals'},
    'ESI': {'name': 'Element Solutions', 'sector': 'chemicals'},
    'APD': {'name': 'Air Products', 'sector': 'chemicals'},
    'AI.PA': {'name': 'Air Liquide', 'sector': 'chemicals'},
    'FUC.DE': {'name': 'Fuchs', 'sector': 'chemicals'},

    # energy / power
    'CEG': {'name': 'Constellation Energy', 'sector': 'energy_power'},
    'FLNC': {'name': 'Fluence Energy', 'sector': 'energy_power'},
    'NEE': {'name': 'NextEra Energy', 'sector': 'energy_power'},
    'BE': {'name': 'Bloom Energy', 'sector': 'energy_power'},
    'TLN': {'name': 'Talen Energy', 'sector': 'energy_power'},
    'VST': {'name': 'Vistra Energy', 'sector': 'energy_power'},
    'SMR': {'name': 'NuScale Power', 'sector': 'energy_power'},

    # robotics / automation
    'QUBT': {'name': 'Quantum Computing Inc', 'sector': 'robotics'},
    'SONY': {'name': 'Sony', 'sector': 'robotics'},
    'CLS': {'name': 'Celestica', 'sector': 'robotics'},
    'ISRG': {'name': 'Intuitive Surgical', 'sector': 'robotics'},
    'AMBA': {'name': 'Ambarella', 'sector': 'robotics'},
    'SYM': {'name': 'Symbotic', 'sector': 'robotics'},
    'IFX.DE': {'name': 'Infineon', 'sector': 'robotics'},
    'AXON': {'name': 'Axon Enterprise', 'sector': 'robotics'},

    # software / cloud / internet
    'PLTR': {'name': 'Palantir', 'sector': 'software_cloud'},
    'RDDT': {'name': 'Reddit Inc', 'sector': 'software_cloud'},
    'META': {'name': 'Meta', 'sector': 'software_cloud'},
    'GOOGL': {'name': 'Alphabet', 'sector': 'software_cloud'},
    'DOCN': {'name': 'DigitalOcean', 'sector': 'software_cloud'},
    'SNOW': {'name': 'Snowflake', 'sector': 'software_cloud'},
    'PATH': {'name': 'UiPath', 'sector': 'software_cloud'},
    'RBRK': {'name': 'Rubrik Inc', 'sector': 'software_cloud'},
    'ORCL': {'name': 'Oracle', 'sector': 'software_cloud'},
    'MSFT': {'name': 'Microsoft', 'sector': 'software_cloud'},
    'CRWD': {'name': 'Crowdstrike', 'sector': 'software_cloud'},
    'UBER': {'name': 'Uber', 'sector': 'software_cloud'},
    'HOOD': {'name': 'Robinhood', 'sector': 'software_cloud'},
    'ETOR': {'name': 'Etoro', 'sector': 'software_cloud'},
    'MELI': {'name': 'MercadoLibre', 'sector': 'software_cloud'},
    'NOK': {'name': 'Nokia', 'sector': 'software_cloud'},

    # fintech / crypto-adjacent
    'CRCL': {'name': 'Circle', 'sector': 'fintech_crypto'},
    'SOFI': {'name': 'SoFi', 'sector': 'fintech_crypto'},
    'BMNR': {'name': 'BitMine', 'sector': 'fintech_crypto'},
    'SBET': {'name': 'SharpLink', 'sector': 'fintech_crypto'},
    'MSTR': {'name': 'Strategy (MicroStrategy)', 'sector': 'fintech_crypto'},
    'FIGR': {'name': 'Figure Technologies', 'sector': 'fintech_crypto'},

    # healthcare / consumer
    'LLY': {'name': 'Eli Lilly', 'sector': 'healthcare'},
    'UNH': {'name': 'UnitedHealth', 'sector': 'healthcare'},
    'EL': {'name': 'Estee Lauder', 'sector': 'consumer'},
    'NVO': {'name': 'Novo Nordisk', 'sector': 'healthcare'},
    'GLW': {'name': 'Corning', 'sector': 'consumer'},
    'CMG': {'name': 'Chipotle', 'sector': 'consumer'},
    'CAVA': {'name': 'CAVA', 'sector': 'consumer'},
    'SHAK': {'name': 'Shake Shack', 'sector': 'consumer'},
    'LMND': {'name': 'Lemonade', 'sector': 'fintech_crypto'},
    'NFLX': {'name': 'Netflix', 'sector': 'consumer'},
    'AAPL': {'name': 'Apple', 'sector': 'consumer'},
    'BMY': {'name': 'Bristol-Myers Squibb', 'sector': 'healthcare'},
    'NUE': {'name': 'Nucor', 'sector': 'cooling_electric'},
    'IREN': {'name': 'Iris Energy', 'sector': 'fintech_crypto'},
    'CLSK': {'name': 'CleanSpark', 'sector': 'fintech_crypto'},
    'ALAB': {'name': 'Astera Labs', 'sector': 'semiconductors'},

    # crypto
    'BTC-USD': {'name': 'Bitcoin', 'sector': 'crypto'},
    'ETH-USD': {'name': 'Ethereum', 'sector': 'crypto'},
    'SOL-USD': {'name': 'Solana', 'sector': 'crypto'},
    'SUI20947-USD': {'name': 'SUI', 'sector': 'crypto'},
    'ZEC-USD': {'name': 'Zcash', 'sector': 'crypto'},
    'DOGE-USD': {'name': 'Dogecoin', 'sector': 'crypto'},
}


def get_ticker_list():
    return list(TICKERS.keys())


def get_sector(symbol):
    return TICKERS.get(symbol, {}).get('sector')


def get_display_name(symbol):
    return TICKERS.get(symbol, {}).get('name', symbol)
