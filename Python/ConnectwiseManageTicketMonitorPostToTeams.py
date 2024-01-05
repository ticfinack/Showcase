from pyconnectwise import ConnectWiseManageAPIClient
import pymsteams
import time
from datetime import datetime, timezone
import logging

# define a set to keep track of tickets that have already been posted to Teams
ticketsAlreadyPosted = set()

# specify logging file
logging.basicConfig(format='%(levelname)s:%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='c:\\SecurityTickets.log', encoding='utf-8', filemode="w", level=logging.DEBUG)

print("This application checks the Connectwise Manage Security board for new tickets every 5 minutes\nand posts them to the Security Team Ticket Notifications Microsoft Teams channel\nbetween the hours of 7am and 6pm.\n")

# define a function to check if a value exists in a set
def checkValueInSet(value, set):
    if value in set:
        return True
    else:
        return False

# define a function for checking if value exists in ticketId key within a dictionary
def checkValueInDict(value, dict):
    for key in dict:
        if key['ticketId'] == value:
            return True
        else:
            return False

# get a list of tickets in Security board
#allTickets = manage_api_client.service.tickets.get(params={
#    'condition': 'board=Security'
#    })

while(True):
    while datetime.now().hour >= 18:
        print("It's after 6pm, waiting...", end='\r')
        time.sleep(30)

    while datetime.now().hour <= 7:
        print("It's before 7am, waiting...", end='\r')
        time.sleep(30)
    
    # init client
    manage_api_client = ConnectWiseManageAPIClient(
    # your company name,
    # manage instance url,
    # your api client id,
    # your api public key,
    # your api private key,
    # optionally, a Config object for customizing API interactions. See [Additional Configuration].
        "****companyname****",
        "na.myconnectwise.net",
        "*********-*************-**********-********",
        "****publickey****",
        "****privatekey****"
    )

    # datetime object containing current date and time
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    #print("date and time =", dt_string)

    print("Checking for new tickets... last checked at: " + dt_string, end='\r')
    # get a list of tickets in Security board with status that is not closed
    openTickets = manage_api_client.service.tickets.get(params={
        'conditions': 'board/name="Security" AND closedFlag=False AND status/name="New"'
        })

    # print the ticket number and summary for each ticket
    #for ticket in openTickets:
    #    print(f'{ticket.id} - {ticket.summary} - {ticket.status.name} - {ticket.board.name} - {ticket.company.name} - {ticket.resources}')

    # post to Teams
    teamsMessage = pymsteams.connectorcard('****MS Teams Webhook URL To Channel****')

    teamsMessage.title("New Security Ticket/s")
    teamsMessage.text("The following are new tickets on the Security board that have arrived since the last check, usually 5 minutes!")
    teamsMessage.color("#00ff00")

    # define set for tickets
    messageList = {}

    for ticket in openTickets:
        if checkValueInSet(str(ticket.id), ticketsAlreadyPosted) == False:
            # add ticket.id to a dictionary
            messageList[f'{ticket.id}'] = {'ticketId': f'{ticket.id}', 'summary': f'{ticket.summary}', 'company': f'{ticket.company.name}'}
            # add ticket.id to set
            ticketsAlreadyPosted.add(str(ticket.id))
            # log ticket.id
            logging.info(f'{ticket.id}')

    # iterate over set to add link buttons to teams message
    for message in messageList:
        # add link button to teams message for each message in messageList
        teamsMessage.addLinkButton(f'{messageList[message]["ticketId"]} - {messageList[message]["summary"]} - {messageList[message]["company"]}', f'https://na.myconnectwise.net/v4_6_release/services/system_io/Service/fv_sr100_request.rails?service_recid=' + f'{ticket.id}' + '&companyName=****companyname****')
    
    if len(messageList) > 0:
        teamsMessage.send()
        print(f'Posted new ticket/s to Teams at: {dt_string}')

    time.sleep(300)