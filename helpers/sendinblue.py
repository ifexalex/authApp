# ------------------
# Create a campaign\
# ------------------
# Include the Sendinblue library\
from __future__ import print_function
import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
# Instantiate the client\
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'
api_instance = sib_api_v3_sdk.EmailCampaignsApi()
# Define the campaign settings\

def sendbluein(subject, from_email, to_emails):
    email_campaigns = sib_api_v3_sdk.CreateEmailCampaign(
    name= "Campaign sent via the API",
    subject= subject,
    sender= { "name": "From name", "email": from_email},
    type= "classic",
    # Content that will be sent\
    html_content= "Congratulations! You successfully sent this example campaign via the Sendinblue API.",
    # Select the recipients\
    recipients= {"listIds": to_emails}
    )
    # Make the call to the client\
    try:
        api_response = api_instance.create_email_campaign(email_campaigns)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling EmailCampaignsApi->create_email_campaign: %s\n" % e)