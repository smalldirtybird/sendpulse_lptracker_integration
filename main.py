import os
import lptracker_api as lptracker
import sendpulse_api as sendpulse
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pprint import pprint
import json


sp_token_expires = datetime.now()
sp_token = None
lpt_token_expires = datetime.now()
lpt_token = None


def main():
    # задаём настройки
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

    load_dotenv()

    while Ture:
        #авторизуемся
        global sp_token_expires, sp_token, lpt_token, lpt_token_expires
        current_time = datetime.now()

        # проверяем, жив ли sp_token, получаем новый, если нет
        if current_time >= sp_token_expires:
            sp_authorization = sendpulse.authorization(
                os.environ['SP_ID'],
                os.environ['SP_SECRET'],
            )
            sp_token = sp_authorization['access_token']
            expires_in = sp_authorization['expires_in']
            sp_token_expires = current_time + timedelta(
                seconds=(expires_in - time_reserve)
            )

        # проверяем, жив ли lpt_token, получаем новый, если нет
        if current_time >= lpt_token_expires:
            lpt_authorization = lptracker.authorization(
                os.environ['LPTRACKER_LOGIN'],
                os.environ['LPTRACKER_PASSWORD'],
                'sendpulse_lptracker_integration'
            )
            lpt_token = lpt_authorization['result']['token']
            lpt_token_expires = current_time + timedelta(
                seconds=(lpt_token_lifetime - time_reserve)
            )

        # запрашиваем у sendpulse список новых сделок
        sp_deals = sendpulse.get_deals(
            sp_token,
            [sp_pipeline_id],
            sp_step_id,
            1,
        )
        for deal in sp_deals:
            sp_final_status = sp_fail_status
            # для каждой сделки получаем всю информацию
            deal_details = sendpulse.get_deal(sp_token, deal['id'])

            # вытаскиваем id контакта сделки
            for event in deal_details['history']:
                if event['eventType'] == 'deal_contact_added':
                    contact_id = event['eventData']['contactId']
                    contact_details = sendpulse.get_contact_details(
                        sp_token,
                        contact_id,
                    )
                    break

            # находим хотя бы один телефон и e-mail
            if contact_details['phones']:
                phone = contact_details['phones'][0]['phone']

                # ищем по телефону и почте контакт в lptracker
                lpt_contact_id = lptracker.search_contact(
                    lpt_token,
                    lpt_project_id,
                    phone=phone,
                )

                # если контакт не найден - создаём новый
                if not lpt_contact_id:
                    lpt_contact_id = lptracker.create_person(
                        lpt_token,
                        lpt_project_id,
                        f'{contact_details["lastName"]}'
                        f'{contact_details["firstName"]}',
                        phone=phone,
                    )

                    # создаём в lptracker новый лид
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

            # закрываем сделку в sendpulse
            sendpulse.change_deal_status(
                sp_token,
                deal_details['id'],
                deal_details,
                sp_final_status,
            )


if __name__ == '__main__':
    main()
