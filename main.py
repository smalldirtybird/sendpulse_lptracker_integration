import os
import lptracker_api as lptracker
import sendpulse_api as sendpulse
from dotenv import load_dotenv
from pprint import pprint


def get_contact_details_from_deal(token, deal):
    phone = None
    email = None
    for event in deal['history']:
        if event['eventType'] == 'deal_contact_added':
            contact_id = event['eventData']['contactId']
            contact_details = sendpulse.get_contact_details(token, contact_id)
            if contact_details['phones']:
                phone = contact_details['phones'][0]['phone']
            if contact_details['emails']:
                email = contact_details['emails'][0]['email']
    return phone, email


def find_best_match(contacts):
    return contacts[0]['id']


def main():
    load_dotenv()
    lpt_authorization = lptracker.authorization(
        os.environ['LPTRACKER_LOGIN'],
        os.environ['LPTRACKER_PASSWORD'],
        'sendpulse_lptracker_integration'
    )
    lpt_token = lpt_authorization['result']['token']
    lpt_project_id = 94698
    sp_authorization = sendpulse.authorization(
        os.environ['SP_ID'],
        os.environ['SP_SECRET'],
    )
    sp_token = sp_authorization['access_token']
    sp_deals = sendpulse.get_deals(sp_token, [43308], 142896, 1)['data']
    for deal in sp_deals:
        deal_details = sendpulse.get_deal(sp_token, deal['id'])
        phone, email = get_contact_details_from_deal(sp_token, deal_details)
        lpt_contact_id = lptracker.search_contact(
            lpt_token,
            lpt_project_id,
            phone=phone,
            email=email,
        )
        lead_name = 'TestLead'
        if not lpt_contact_id:
            lpt_contact_id = lptracker.create_person(
                lpt_token,
                lpt_project_id,
                'NewTest',
                phone=phone,
                email=email,
            )
        lptracker.create_lead(lpt_token, lead_name, contact_id=lpt_contact_id)


if __name__ == '__main__':
    main()
