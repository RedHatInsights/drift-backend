import json
import uuid
import random
import hashlib
import string

from drift.constants import MOCK_FACTS_FILE, MOCK_FACT_NAMESPACE


def fetch_mock_facts(seed):
    """
    Load mock data from file as a dict
    """
    with open(MOCK_FACTS_FILE) as f:
        factdata = f.read()
    static_facts = json.loads(factdata)
    dynamic_facts = generate_additional_facts(seed)
    return {'facts': {**static_facts, **dynamic_facts}, 'namespace': MOCK_FACT_NAMESPACE}


def generate_additional_facts(seed):
    """
    Generate a few additional facts
    """
    m = hashlib.sha256()
    seed_bytes = bytes(seed, 'utf-8')
    m.update(seed_bytes)

    facts = {}
    facts['a.random.number'] = random.randint(1_000_000, 9_999_999)
    facts['here.is.a.uuid'] = uuid.uuid4()
    facts['seed.string'] = seed
    facts['seed.hash'] = m.hexdigest()
    facts['here.is.a.uuid'] = uuid.uuid4()

    if seed[0] in string.ascii_lowercase:
        facts['defined.for.seeds.that.start.with.a.letter'] = "True"
    return facts
