import json
import uuid

MOCK_FACTS_FILE = 'drift/mock_data/mockfacts.json'
MOCK_FACT_NAMESPACE = 'mockfacts'


def fetch_mock_facts():
    """
    Load mock data from file as a dict, and add a randomly generated fact value
    in "a.fresh.uuid"
    """
    with open(MOCK_FACTS_FILE) as f:
        factdata = f.read()
    facts = json.loads(factdata)
    facts['a.fresh.uuid'] = uuid.uuid4()
    return {'facts': facts, 'namespace': MOCK_FACT_NAMESPACE}
