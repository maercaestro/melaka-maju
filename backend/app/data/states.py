STATES = ['Johor', 'Kedah', 'Kelantan', 'Melaka', 'Negeri Sembilan', 'Pahang', 'Perak', 'Perlis', 'Pulau Pinang', 'Sabah', 'Sarawak', 'Selangor', 'Terengganu']
TERRITORIES = ['W.P. Kuala Lumpur', 'W.P. Putrajaya', 'W.P. Labuan']
ALIASES = {'Penang': 'Pulau Pinang', 'Malacca': 'Melaka', 'Kuala Lumpur': 'W.P. Kuala Lumpur', 'Putrajaya': 'W.P. Putrajaya', 'Labuan': 'W.P. Labuan', 'W.P. Kuala Lumpur1': 'W.P. Kuala Lumpur', 'Supra': 'Supranational', 'Supra2': 'Supranational'}
def normalize_state(value: str) -> str:
    value = value.strip()
    return ALIASES.get(value, value)
def universe(include_federal_territories=False):
    return STATES + TERRITORIES if include_federal_territories else STATES
