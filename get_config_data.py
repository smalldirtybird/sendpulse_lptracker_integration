import os
from pprint import pprint

from dotenv import load_dotenv

from lptracker_api import authorization as lpt_auth
from lptracker_api import get_funnel_steps, get_users
from sendpulse_api import authorization as sp_auth
from sendpulse_api import get_pipelines


def main():
    load_dotenv()
    lpt_project_id = '94698'
    sp_token = sp_auth(
        os.environ['SP_ID'],
        os.environ['SP_SECRET']
    )['access_token']
    lpt_token = lpt_auth(
        os.environ['LPTRACKER_LOGIN'],
        os.environ['LPTRACKER_PASSWORD'],
        'sendpulse_lptracker_integration',
    )['result']['token']
    config_data = {
        'LPT users': get_users(lpt_token),
        'LPT funnel steps': get_funnel_steps(
            lpt_token,
            lpt_project_id,
        )['result'],
        'SP pipelines': get_pipelines(sp_token)['data'],
    }
    pprint(config_data)


if __name__ == '__main__':
    main()
