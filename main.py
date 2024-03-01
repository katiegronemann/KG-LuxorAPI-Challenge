'''
LuxOS Miner Control Application Challenge
Written by Katie Gronemann

This program is designed to demonstrate an example application that manages the daily schedule of a mining fleet.
It makes calls to the provided sample LuxOS API and modifies the run state of a theoretical miner.
The program keeps track of the state of these miners by recording its changes & miner responses in a dictionary list.
'''

from datetime import datetime
import schedule
import time
import requests
import os


#Storing the API Address as a global var
API = "http://127.0.0.1:5000"

#I assume I have access to a list of IP Addresses from user input. Let's say I've converted that to this list of dictionaries.
#I don't seem to have a way to check the existing mode & profile of the miners at start, we won't assume
miners = [
    {"miner_ip": "10.1.1.1", "profile": "", "mode": "", "token":"", "ttl":"Wed, 31 Dec 1969 23:59:59 GMT"},
    {"miner_ip": "10.1.1.2", "profile": "", "mode": "", "token":"", "ttl":"Wed, 31 Dec 1969 23:59:59 GMT"},
    {"miner_ip": "10.1.1.3", "profile": "", "mode": "", "token":"", "ttl":"Wed, 31 Dec 1969 23:59:59 GMT"},
    {"miner_ip": "10.1.1.4", "profile": "", "mode": "", "token":"", "ttl":"Wed, 31 Dec 1969 23:59:59 GMT"},
    {"miner_ip": "10.1.1.5", "profile": "", "mode": "", "token":"", "ttl":"Wed, 31 Dec 1969 23:59:59 GMT"},
]

'''
This helper function is called by our scheduler.
It logs into the LuxOS API to retreive a 'token'
Then it determines which endpoint we need to call.

args[0]='underclock', 'overclock', 'normal', 'sleep','active'
args[1]='profile','mode'
'''
def changeMinerState(args):
    print("Setting all miners'",args[1],"to", args[0],"...")

    for miner in miners:
        login(miner)
        
        if (args[1] == "profile"):
            setProfile(miner, args[0])

        #Note: curtailment needs to be UNSET when profile becomes normal again.
        elif (args[1] == "mode"):
            setMode(miner, args[0])

    return


'''
This method sends a POST Request to the API and checks for a valid auth 'token'
This token is stored in our state dict for use in other methods
'''
def login(miner):
    #We use a try block for our request in case the API is down.
    try:
        response = requests.post(API+'/api/login',json={'miner_ip':miner['miner_ip']})
        
        if response.status_code == 200:
            #We always get this token
            miner['token']=response.json()['token'] #yup!

            #Weird edge case where API does not serve TTL if already logged in
            #Check the response message for "already" and don't attempt to read invalid key
            #It's kinda pointless to store this in this case,
            #1 minute is nearly irrelevant TTL for our commands- which are once every six hours
            if not (response.json()['message'][6:13] == "already"):
                miner['ttl']=response.json()['ttl'] #yup!

            #print("Success. Response: ", response.text)
            '''
                Success. Response:  {
                "message": "Miner logged in.",
                "token": "10.1.1.1_token",
                "ttl": "Thu, 29 Feb 2024 20:10:56 GMT"
                }

                Success. Response:  {
                "message": "Miner already logged in.",
                "token": "10.1.1.5_token"
                }

            '''
        else:
            print("Failed Login. Status Code: ", response.status_code)
        return response
    
    except requests.exceptions.ConnectionError as e:
        print("Error establishing connection to LuxOS API.")
        #print(f"ConnectionError: {e}")

    
'''
This method changes the Performance Profile of a Miner
It has three settings: 'normal, 'overclock' and 'underclock'

We need to assume if the Profile is being switched to a VALID profile, the Miner should be woken from sleep.
This method will NOT set "Mode" to "active" if fed an INVALID profile.
'''
def setProfile(miner, profile):
    #We use a try block for our request in case the API is down.
        try:
            response = requests.post(API+'/api/profileset',json={'token':miner['token'], 'profile':profile})
            #The API does not make a clear distinction between "invalid state" and "already in state" via Status Code
            #I use the first letter of the Message to determine which case we have.
            if response.status_code == 400:
                #"{response.message: 'Miner is already in ...'"
                if (response.json()['message'][0] == "M"):
                    
                    miner["profile"] = profile
                    #Check if we know the Miner's mode, and set it Active if we aren't sure it is.
                    #This brings the Miner's state into our knowledge
                    if(miner['mode'] != 'active'):
                        print("Setting",miner['miner_ip'],"to active...")
                        setMode(miner,'active')


                else: print("Error, Invalid Performance Profile:",profile)
                
            #This status code indicates our token has expired.
            #In this case, we can actually pipe the change back into the changeMinerState method
            elif response.status_code == 401:
                print("Error modifying", miner['miner_ip'], "- login expired.\nAttempting to re-authenticate")
                changeMinerState([profile,"profile"])

            #Our request was successful.
            else:
                #print("Profile updated to", profile, "for", miner['miner_ip'])
                miner["profile"] = profile
                if(miner['mode'] != 'active'):
                    print("Setting",miner['miner_ip'],"to active...")
                    setMode(miner,'active')
        
        
        except requests.exceptions.ConnectionError as e:
            print("Error establishing connection to LuxOS API.")
            #print(f"ConnectionError: {e}")
            
'''
This method changes the Curtailment Mode of a Miner
It has two settings: 'sleep', and 'active'
'''        
def setMode(miner, mode):
    #We use a try block for our request in case the API is down.
        try:
            response = requests.post(API+'/api/curtail',json={'token':miner['token'], 'mode':mode})

            #The API does not make a clear distinction between "invalid state" and "already in state" via Status Code
            #I use the first letter of the Message to determine which case we have.
            if response.status_code == 400:
                #"{response.message: 'Miner is already in ...'"
                if (response.json()['message'][0] == "M"):
                    miner["mode"] = mode
                else: print("Error, Invalid Power Mode:",mode)

            #This status code indicates our token has expired.
            #In this case, we can actually pipe the change back into the changeMinerState method
            elif response.status_code == 401:
                print("Error modifying", miner['miner_ip'], "- login expired.\nAttempting to re-authenticate")
                changeMinerState([mode,"mode"])

            #Our request was successful.
            else:
                #print("Mode updated to", mode, "for", miner['miner_ip'])
                miner["mode"] = mode
        
        except requests.exceptions.ConnectionError as e:
            print("Error establishing connection to LuxOS API.")
            #print(f"ConnectionError: {e}")


'''
I like to use the schedule plugin for tasks like this.

The first three statements set the schedule class to change our profile during "working hours"
The fourth statement puts the Miner into curtailment "sleep" mode.

These statements should satisfy the scheduling requirements of the assignment.
'''
schedule.every().day.at("00:00").do(changeMinerState,['overclock',"profile"])
schedule.every().day.at("06:00").do(changeMinerState,['normal',"profile"])
schedule.every().day.at("12:00").do(changeMinerState,['underclock',"profile"])

#Curtail is a power mode, not a profile. Put to sleep at 18:00
schedule.every().day.at("18:00").do(changeMinerState,['sleep',"mode"]) 


### Below this line are my test methods and demonstrations ###
'''
This section is simply to demonstrate the program's functions.
Kindof like a "DEMO" on an arcade game. 
'''
tasks = [
    lambda: (changeMinerState(['overclock',"profile"])),
    lambda: (changeMinerState(['normal',"profile"])),
    lambda: (changeMinerState(['underclock',"profile"])),
    lambda: (changeMinerState(['sleep',"mode"])),

    lambda: (changeMinerState(['badmode',"mode"])),
    lambda: (changeMinerState(['badprof',"profile"])),

    lambda: (changeMinerState(['normal',"profile"])),
    lambda: (changeMinerState(['sleep',"mode"])),
    lambda: (changeMinerState(['normal',"profile"])),
]
# Index to keep track of the current task
current_profile_index = 0
def stateSwitcher():
    global current_profile_index
    tasks[current_profile_index]()
    current_profile_index = (current_profile_index + 1) % len(tasks)

schedule.every(5).seconds.do(stateSwitcher)


### Above this line are tests and demonstrations ###



'''
This is our main loop that ticks every (10) seconds and checks if any scheduled events need to run.
This prints the tracked miners' states as they change.
'''
os.system('cls')
print("Welcome to the LuxOS Miner Scheduler.")
while True:
    schedule.run_pending()
    print("_______________________________________________________________________________________________________________________________________________________________")
    print("| IP |\t\t   | Profile |\t\t\t| Mode |\t| Token |\t\t| Timestamp |")
    for miner in miners:
        print({miner['miner_ip']},"\t",{miner['profile']},"  \t\t",{miner['mode']},"\t",{miner['token']},"\t",{miner['ttl']})
    print("_______________________________________________________________________________________________________________________________________________________________")
    time.sleep(5)
    os.system('cls')
