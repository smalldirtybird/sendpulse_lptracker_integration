import json
import logging
import os
import traceback
from datetime import datetime, timedelta
from time import sleep

from dotenv import load_dotenv
from telegram import Bot

import lptracker_api as lptracker
import sendpulse_api as sendpulse

sp_token_expires = datetime.now()
sp_token = None
lpt_token_expires = datetime.now()
lpt_token = None


class TelegramLogsHandler(logging.Handler):

    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = Bot(token=bot_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


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
    logger = logging.getLogger('TelegramLogger')
    logger.addHandler(TelegramLogsHandler(
        os.environ['TELEGRAM_BOT_TOKEN'], os.environ['TELEGRAM_CHAT_ID']))
    with open('config.json', 'r') as config_json:
        config = json.load(config_json)
    time_reserve = config['time_reserve']
    lpt_token_lifetime = config['lpt_token_lifetime']
    lpt_project_id = config['lpt_project_id']
    lpt_new_lead_step = config['lpt_new_lead_step']
    lpt_lead_owner_id = config['lpt_lead_owner_id']
    sp_step_id = config['sp_step_id']
    sp_pipeline_id = config['sp_pipeline_id']
    sp_success_status = config['sp_success_status']
    sp_fail_status = config['sp_fail_status']
    delay_time = config['delay_time']
    exception_delay = config['exception_delay']
    while True:
        try:
            tokens_validation(
                os.environ['SP_ID'],
                os.environ['SP_SECRET'],
                os.environ['LPTRACKER_LOGIN'],
                os.environ['LPTRACKER_PASSWORD'],
                'sendpulse_lptracker_integration',
                lpt_token_lifetime,
                time_reserve,
            )
            sp_deals = sendpulse.get_deals(
                sp_token,
                [sp_pipeline_id],
                sp_step_id,
                1,
            )
            for deal in sp_deals:
                sp_final_status = sp_fail_status
                phone = None
                lpt_contact_id = None
                deal_details = sendpulse.get_deal(sp_token, deal['id'])
                contact_details = get_contact_from_deal(deal_details)
                if contact_details['phones']:
                    phone = contact_details['phones'][0]['phone']
                if phone:
                    lpt_contact_id = lptracker.search_contact(
                        lpt_token,
                        lpt_project_id,
                        phone=phone,
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
                        funnel_id=lpt_new_lead_step,
                        callback=False,
                        lead_owner_id=lpt_lead_owner_id
                    )
                    if lead_created['status'] == 'success':
                        sp_final_status = sp_success_status
                sendpulse.change_deal_status(
                    sp_token,
                    deal_details['id'],
                    deal_details,
                    sp_final_status,
                )
            sleep(delay_time)
        except Exception:
            logger.error(
                f'SP LPT inegration crushed with exception:\n'
                f'{traceback.format_exc()}')
            sleep(exception_delay)


if __name__ == '__main__':
    main()
