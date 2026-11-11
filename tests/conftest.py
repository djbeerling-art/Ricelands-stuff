import pytest

def pytest_configure(config):
    config.addinivalue_line('markers', 'slow: real SCEPTER toy runs (about 1-2 min); run with -m slow')

def pytest_collection_modifyitems(config, items):
    if config.getoption('-m'):
        return
    skip = pytest.mark.skip(reason='slow model run: use -m slow')
    for it in items:
        if 'slow' in it.keywords: it.add_marker(skip)
