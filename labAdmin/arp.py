IP_INDEX = 0
MAC_INDEX = 3
NUM_FIELDS = 6


def get_neighbours():
    """
    Returns a generator of ip address, mac address tuples.
    Empty mac addresses are filtered out.
    """
    with open('/proc/net/arp', 'r') as f:
        # skip header
        next(f)
        for row in f:
            fields = row.split()
            if len(fields) < NUM_FIELDS:
                continue
            if fields[MAC_INDEX] == '00:00:00:00:00:00':
                continue
            yield fields[IP_INDEX], fields[MAC_INDEX]
