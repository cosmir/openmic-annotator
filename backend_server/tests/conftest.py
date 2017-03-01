import pytest

import os
import yaml


@pytest.fixture()
def sample_app():
    import main

    cfg_file = os.path.join(os.path.dirname(__file__), os.pardir,
                            'configs', 'local.DEFAULT.yaml')
    with open(cfg_file) as fp:
        cfg = yaml.load(fp)

    main.app.config.update(cloud=cfg['cloud'], oauth=cfg['oauth'], noauth=True)
    main.app.testing = True
    with main.app.test_client() as client:
        # This forces the app to pass authentication; however, it doesn't (yet)
        # let us test that authenticated routes are blocked.
        with client.session_transaction() as sess:
            sess['access_token'] = ('fluflu', None)
        return client
