import json
import logging
import os
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from time import sleep

from dotenv import load_dotenv

import lptracker_api as lptracker
import sendpulse_api as sendpulse

logger = logging.getLogger(__file__)
sp_token_expires = datetime.now()
sp_token = None
lpt_token_expires = datetime.now()
lpt_token = None
lpt_users = []


def create_users_list(users, users_to_exclude):
    for user in users:
        user_id = int(user['id'])
        if user_id not in users_to_exclude:
            lpt_users.append(user_id)


def tokens_validation(sp_id, sp_secret, lpt_login, lpt_password, lpt_grant,
                      lpt_token_lifetime, time_reserve):
    global sp_token_expires, sp_token, lpt_token, lpt_token_expires
    current_time = datetime.now()
    if current_time >= sp_token_expires:
        sp_authorization = sendpulse.authorization(sp_id, sp_secret)
        sp_token = sp_authorization['access_token']
        expires_in = sp_authorization['expires_in']
        sp_token_expires = current_time + timedelta(
            seconds=(expires_in - time_reserve)
        )
        logger.info(f'{datetime.now()}: sp_token refreshed.')
    if current_time >= lpt_token_expires:
        lpt_authorization = lptracker.authorization(
            lpt_login,
            lpt_password,
            lpt_grant,
        )
        lpt_token = lpt_authorization['result']['token']
        lpt_token_expires = current_time + timedelta(
            seconds=(lpt_token_lifetime - time_reserve)
        )
        logger.info(f'{datetime.now()}: lpt_token refreshed.')


def get_contact_from_deal(deal_details):
    for event in deal_details['history']:
        if event['eventType'] == 'deal_contact_added':
            contact_id = event['eventData']['contactId']
            return sendpulse.get_contact_details(
                sp_token,
                contact_id,
            )


def main():
    load_dotenv()
    log_folder = 'logs/'
    os.makedirs(log_folder, exist_ok=True)
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(
        os.path.join(log_folder, 'app.log'),
        maxBytes=1024000,
        backupCount=10,
    )
    logger.addHandler(handler)
    with open('config.json', 'r') as config_json:
        config = json.load(config_json)
    lpt_project_id = config['lpt_project_id']
    users_to_exclude = [0]
    while True:
        try:
            tokens_validation(
                os.environ['SP_ID'],
                os.environ['SP_SECRET'],
                os.environ['LPTRACKER_LOGIN'],
                os.environ['LPTRACKER_PASSWORD'],
                'sendpulse_lptracker_integration',
                config['lpt_token_lifetime'],
                config['time_reserve'],
            )
            sp_deals = sendpulse.get_deals(
                sp_token,
                config['sp_pipeline_ids'],
                config['sp_step_ids'],
                config['sp_search_status_ids'],
            )
            if sp_deals:
                logger.info(f'{datetime.now()}: found deals: {len(sp_deals)}.')
            for deal in sp_deals:
                if not lpt_users:
                    create_users_list(lptracker.get_users(lpt_token),
                                      users_to_exclude)
                print(lpt_users)
                deal_id = deal['id']
                logger.info(f'{datetime.now()}: start handle deal {deal_id}.')
                sp_final_status = config['sp_fail_status']
                phone = None
                lpt_contact_id = None
                deal_details = sendpulse.get_deal(sp_token, deal_id)
                contact_details = get_contact_from_deal(deal_details)
                if contact_details['phones']:
                    phone = contact_details['phones'][0]['phone']
                if phone:
                    lpt_contact_id = lptracker.search_contact(
                        lpt_token,
                        lpt_project_id,
                        phone=contact_details['phones'][0]['phone'],
                    )
                if not lpt_contact_id:
                    lpt_contact_id = lptracker.create_person(
                        lpt_token,
                        lpt_project_id,
                        f'{contact_details["lastName"]} '
                        f'{contact_details["firstName"]}',
                        phone=phone,
                    )
                    lead_created = lptracker.create_lead(
                        lpt_token,
                        deal_details['name'],
                        contact_id=lpt_contact_id,
                        funnel_id=config['lpt_new_lead_step'],
                        callback=config['lpt_callback'],
                        lead_owner_id=config['lpt_lead_owner_id']
                    )
                    if lead_created['status'] == 'success':
                        sp_final_status = config['sp_success_status']
                        lead_id = lead_created["result"]["id"]
                        logger.info(f'{datetime.now()}: created lead'
                                    f' {lead_id}.')
                        lead_owner_id = lpt_users[0]
                        new_lead_owner_id = lptracker.change_lead_owner(
                            lpt_token,
                            lead_id,
                            lead_owner_id,
                        )['result']['owner_id']
                        lpt_users.remove(new_lead_owner_id)
                        logger.info(f'{datetime.now()}: lead owner changed to'
                                    f' {new_lead_owner_id}.')
                sendpulse.change_deal_status(
                    sp_token,
                    deal_details['id'],
                    deal_details,
                    sp_final_status,
                )
                logger.info(f'{datetime.now()}: deal {deal_id} handled.')
            sleep(config['delay_time'])
        except Exception:
            logger.exception(datetime.now())
            sleep(config['exception_delay'])


if __name__ == '__main__':
    main()
