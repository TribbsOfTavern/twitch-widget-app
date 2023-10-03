###
#   twitch-helper/src/twitch-widget-app.py
#   Written on stream @ twitch.tv/CodeNameTribbs
#
import multiprocessing
import requests
import time
import json
from pystray import Icon, Menu, MenuItem
from PIL import Image

###
#   Globals
exit_flag = None

###
#   Load Config
#
def loadConfig(filename):
    try:
        config = None
        with open(filename) as fo:
            config = json.load(fo)
        
        if config == None: raise Exception("Configuration file failed to load.")
        else: return config
    except Exception as e:
        raise e
    
###
#   Event Checker
#       sub-class of multiprocessing.Process to run independent of main loop
#
class EventChecker(multiprocessing.Process):
    '''
        Create a process that will connect to the SE API and perodically retrive data
        Parse the data and update necessary files (currently a txt file)
        If there is an error, terminate self process
    '''
    token = None
    history = []
    error = None
    new_event = False
    
    def __init__(self, settings:dict, exit_event):
        #TODO Add error handling
        super().__init__()
        if not settings:
            self.error = Exception("Empty dict passed to settings.")
        else:
            self.token = settings['jwt-token']
            self.channel_id = settings['channel-id'] 
            self.wait_time = settings['check-every-seconds'] 
            self.msg_templates = settings['messages']
            self.msg_spacer = settings['message-spacer']
            self.label_file = settings['label-file']
            self.event_limit = settings['event-limit']
            self.exit_flag = exit_event
        print("EventChecker Started")
            
    def _getData(self):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            
            uri = "https://api.streamelements.com/kappa/v2/sessions/"
            uri += f"{self.channel_id}"
            
            response = requests.get(uri, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Bad return code: {response.status_code}")
        except Exception as e:
            self.error = f"Error occured while fetching data: {e}"

    def _updateHistory(self, data:dict={}):        
        if not data:
            raise Exception("No data was passed to parse")
        
        eventTypes = {
            'follower-recent': "follow", 
            'subscriber-recent': "subscribe", 
            'host-recent': "host",
            'cheer-recent': "cheer",
        }
        
        for event_list, event_type in eventTypes.items():
            for item in data['data'][event_list]:
                if item['name'] != '':
                    item['type'] = event_type
                    if item in self.history: break
                    else:
                        self.history.append(item)
                        self.new_event = True
               
        self.history = sorted(self.history, key=lambda x: x['createdAt'], reverse=True)

    def _dropLabelToFile(self):
        # Set default if no message templates found.
        if not self.msg_templates:
            # Default messages if they have not beed set in the config
            self.msg_templates = {
                "follow": "%name followed.",
                "subscribe": "%name subscribed.",
                "host": "%name hosted with %amount.",
                "cheer": "%name cheered %amount bits.",
                "tip": "%name tipped %amount.",
                "merch": "%name somehow found merch!?",
                "raid": "%name brought %amount raiders.",
                "superchat": "%name with the superchat!",
                "charity": "%name gave %amount to a good cause!"
            }
        # prep str for file
        text_event = []
        for event in self.history[:self.event_limit]:
            temp = self.msg_templates[event['type']]
            if 'amount' in event.keys():
                temp = temp.replace('%name', str(event['name']))
                temp = temp.replace('%amount', str(event['amount']))
            else:
                temp = temp.replace('%name', str(event['name']))
            text_event.append(temp)
            
        with open(self.label_file, 'w') as fn:
            fn.write(self.msg_spacer.join(text_event) + self.msg_spacer)    
            
        self.new_event = False            

    def run(self):
        # todo load in saved history... also save history on exit
        while self.is_alive() and not self.error:
            if self.exit_flag.is_set():
                break
                # Wrap Up Functions, Save Data, End Process
            time.sleep(self.wait_time)
            self._updateHistory(self._getData())
            if self.new_event: self._dropLabelToFile()

###
#   System Tray Menu Event Handling
#
def trayItemClicked(icon, query):
    if (str(query) == "Exit"):
        exit_flag.set()

###
#   Main App Loop
#
def app():
# Load config file
    settings = loadConfig("testconfig.json")
    proc_list = []
    ## Start tray menu
    sys_tray_img = Image.open("py-app-icon.png")
    sys_tray = Icon("Twitch Helper App.", sys_tray_img, menu=Menu(
        MenuItem("Exit", trayItemClicked)
    ))
    sys_tray.run_detached()
    ## Create the Process we're using
    if not settings: 
        raise Exception("Error loading config file")
    event_ticker = EventChecker(settings['EventChecker'], exit_flag)
    ## Add Processes To The List
    proc_list.extend([
        event_ticker
    ])
    ## Start Processes
    if proc_list:
        for proc in proc_list:
            proc.start()
    ## Exit the program when no more process are running  
    while proc_list:
        for idx, proc in enumerate(proc_list):
            if not proc.is_alive():
                proc_list.pop(idx)
            break
    ## Stop Tray
    sys_tray.stop()
    
    ## Exit verification
    print("App exited succesfully.")
    exit()

if __name__ == "__main__":
    exit_flag = multiprocessing.Event()
    app()