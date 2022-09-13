import json
import os

from dotenv import load_dotenv

from lptracker_api import authorization as lpt_auth
from lptracker_api import get_funnel_steps, get_projects, get_users
from sendpulse_api import authorization as sp_auth
from sendpulse_api import get_pipelines


def main():
    load_dotenv()
    default_data = {
        'time_reserve': 60,
        'delay_time': 1,
        'lpt_token_lifetime': 86400,
        'lpt_new_lead_step': None,
        'lpt_lead_owner_id': 0,
        'lpt_callback': True,
        'sp_search_status_ids': [1],
        'sp_pipeline_ids': [],
        'sp_step_ids': [],
        'sp_success_status': 3,
        'sp_fail_status': 2,
        'exception_delay': 30
    }
    sp_token = sp_auth(
        os.environ['SP_ID'],
        os.environ['SP_SECRET']
    )['access_token']
    lpt_token = lpt_auth(
        os.environ['LPTRACKER_LOGIN'],
        os.environ['LPTRACKER_PASSWORD'],
        'sendpulse_lptracker_integration',
    )['result']['token']
    lpt_project_id = get_projects(
        lpt_token)['result'][0]['id']
    default_data['lpt_project_id'] = lpt_project_id
    print('\nПользователи LPTracker:')
    for user in get_users(lpt_token)['result']:
        print(f'{user["id"]}: {user["name"]}, {user["job"]}')
    print('\nШаги воронки LPTracker:')
    for step in get_funnel_steps(lpt_token, lpt_project_id)['result']:
        print(f'{step["id"]}: {step["name"]}')
        if step["name"] == 'Новый лид':
            default_data['lpt_new_lead_step'] = step["id"]
    print('\nВоронки SendPulse:')
    pipelines = {}
    for pipeline in get_pipelines(sp_token)['data']:
        print(f'{pipeline["id"]}: {pipeline["name"]}')
        print(f'Шаги воронки {pipeline["name"]}:')
        steps = []
        for step in pipeline['steps']:
            print(f'{step["id"]}: {step["name"]}')
            steps.append(step["id"])
        pipelines[pipeline["id"]] = min(steps)
    sp_pipeline_id = min(pipelines.keys())
    default_data['sp_pipeline_ids'].append(sp_pipeline_id)
    default_data['sp_step_ids'].append(pipelines[sp_pipeline_id])
    with open('config.json', 'w') as config_json:
        config_data = json.dumps(default_data)
        config_json.write(config_data)


if __name__ == '__main__':
    main()
