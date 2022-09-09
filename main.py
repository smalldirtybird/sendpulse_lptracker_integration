from dateutil.parser import isoparse
import os
import lptracker_api as lptracker
import sendpulse_api as sendpulse
from dotenv import load_dotenv
from datetime import datetime
from pprint import pprint


def main():
    # авторизуемся
    load_dotenv()
    lpt_authorization = lptracker.authorization(
        os.environ['LPTRACKER_LOGIN'],
        os.environ['LPTRACKER_PASSWORD'],
        'sendpulse_lptracker_integration'
    )
    lpt_token = lpt_authorization['result']['token']
    sp_authorization = sendpulse.authorization(
        os.environ['SP_ID'],
        os.environ['SP_SECRET'],
    )
    sp_token = sp_authorization['access_token']

    # задаём настройки
    lpt_project_id = 94698
    ltp_new_lead_step = 1708039
    lpt_lead_owner_id = 33327
    sp_step_id = 142896
    sp_pipeline_id = 43308
    sp_final_status = 3

    # запрашиваем у sendpulse список новых сделок
    sp_deals = sendpulse.get_deals(
        sp_token,
        [sp_pipeline_id],
        sp_step_id,
        1,
    )
    for deal in sp_deals:
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
        phone = None
        email = None
        if contact_details['phones']:
            phone = contact_details['phones'][0]['phone']
        if contact_details['emails']:
            email = contact_details['emails'][0]['email']

        # ищем по телефону и почте контакт в lptracker
        lpt_contact_id = lptracker.search_contact(
            lpt_token,
            lpt_project_id,
            phone=phone,
            email=email,
        )

        # если контакт не найден - создаём новый
        if not lpt_contact_id:
            lpt_contact_id = lptracker.create_person(
                lpt_token,
                lpt_project_id,
                f'{contact_details["lastName"]}' 
                f'{contact_details["firstName"]}',
                phone=phone,
                email=email,
            )

        # находим владельца лида в lptracker
        sp_resp_email = sendpulse.get_responsible_email(
            sp_token,
            deal_details['responsibleId'],
        )

        # создаём в lptracker новый лид
        created_at = isoparse(deal_details['createdAt'])
        lead_created = lptracker.create_lead(
            lpt_token,
            deal_details['name'],
            datetime.strftime(created_at, '%d.%m.%Y %H:%M'),
            contact_id=lpt_contact_id,
            funnel_id=ltp_new_lead_step,
        )

        ## закрываем сделку в sendpulse как успешную
        # if lead_created['status'] == 'success':
            # sendpulse.change_deal_status(
            #     sp_token,
            #     deal_details['id'],
            #     deal_details,
            #     sp_final_status,
            # )


if __name__ == '__main__':
    main()
