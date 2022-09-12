import json
import logging
import os
import traceback
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from textwrap import dedent
from time import sleep

from dotenv import load_dotenv
from telegram import Bot

import lptracker_api as lptracker
import sendpulse_api as sendpulse

logger = logging.getLogger(__file__)
sp_token_expires = datetime.now()
sp_token = None
lpt_token_expires = datetime.now()
lpt_token = None


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
        logger.info(dedent(f'''
        {datetime.now()}: sp_token refreshed.
        '''))
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
        logger.info(dedent(f'''
        {datetime.now()}: lpt_token refreshed.
        '''))


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
        maxBytes=102400,
        backupCount=10,
    )
    logger.addHandler(handler)
    tg_bot = Bot(os.environ['TELEGRAM_BOT_TOKEN'])
    with open('config.json', 'r') as config_json:
        config = json.load(config_json)
    lpt_project_id = config['lpt_project_id']
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
                logger.info(dedent(f'''
                {datetime.now()}: found {len(sp_deals)} new deals.
                '''))
            for deal in sp_deals:
                deal_id = deal['id']
                logger.info(dedent(f'''
                {datetime.now()}: start handle deal {deal_id}.
                '''))
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
                        callback=False,
                        lead_owner_id=config['lpt_lead_owner_id']
                    )
                    if lead_created['status'] == 'success':
                        sp_final_status = config['sp_success_status']
                        logger.info(dedent(f'''
                        {datetime.now()}: created new lead, id {
                        lead_created["result"]["id"]}.
                        '''))
                sendpulse.change_deal_status(
                    sp_token,
                    deal_details['id'],
                    deal_details,
                    sp_final_status,
                )
                logger.info(dedent(f'''
                {datetime.now()}: deal {deal_id} handled.
                '''))
            sleep(config['delay_time'])
        except Exception:
            logger.exception(datetime.now())
            tg_bot.send_message(
                text=f'''
                SP LPT inegration crushed with exception:
                {traceback.format_exc()}
                ''',
                chat_id=os.environ['TELEGRAM_CHAT_ID'],
            )
            sleep(config['exception_delay'])


if __name__ == '__main__':
    main()
