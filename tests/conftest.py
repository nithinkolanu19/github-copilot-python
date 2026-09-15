import sys
from pathlib import Path

import pytest


STARTER_DIR = Path(__file__).parents[1] / 'starter'
sys.path.insert(0, str(STARTER_DIR))


@pytest.fixture
def client():
    import app

    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None
    app.CURRENT['hints_used'] = 0
    app.app.config['TESTING'] = True
    with app.app.test_client() as test_client:
        yield test_client
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None
    app.CURRENT['hints_used'] = 0