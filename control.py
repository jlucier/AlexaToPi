'''
Ported from AWS IoT Python SDK shadow example
'''
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
from logging.handlers import RotatingFileHandler
import json
import time

from RPi import GPIO

logFile = 'log'
INITIAL_STATE = False
GPIO_OFF = True
GPIO_ON = False

TOGGLE_STATE = lambda s: (s[0], not s[1])
# (pin num, curr state, spam)
PINS = {
    'lamp':(11, INITIAL_STATE),
    'speakers':(13, INITIAL_STATE),
    'projector':(15, INITIAL_STATE),
    'ac':(16, INITIAL_STATE)
}


# Configure logging
handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024,
                                 backupCount=1, encoding=None, delay=0)
logger = logging.getLogger("PI.AUTOMATION")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def output_gpios():
    for device, state in PINS.iteritems():
        if device == 'projector' and state[1]:
            # do weird projector nonsense
            PINS[device] = (state[0], False)
            for _ in xrange(2):
                GPIO.output(state[0], GPIO_ON)
                time.sleep(2)
                GPIO.output(state[0], GPIO_OFF)
                time.sleep(2)
        else:
            GPIO.output(state[0], not state[1])

def pins_to_shadow():
    return json.dumps({
        'state': {
            'reported':{device : state[1] for device,state in PINS.iteritems()},
            'desired':None
        }
    })

def update_callback(payload, responseStatus, token):
    logger.info("Update succeeded")

def control_callback(payload, responseStatus, token):
    payload = json.loads(payload)
    for k,v in payload['state'].iteritems():
        if k not in PINS:
            continue
        state = PINS[k]
        PINS[k] = (state[0], v)
        logger.info("{} set to {}".format(k, 'on' if v else 'off'))

    output_gpios()
    device.shadowUpdate(pins_to_shadow(), update_callback, 5)

# Load config
config = None
with open('config.json', 'r') as f:
    config = json.load(f)

logger.info("Started")

# Configure connection
shadow_client = AWSIoTMQTTShadowClient("shadow_delta_listener", useWebsocket=True)
shadow_client.configureEndpoint(config['endpoint'], 443)
shadow_client.configureCredentials(config['path_to_ca'])

# AWSIoTMQTTShadowClient configuration
shadow_client.configureAutoReconnectBackoffTime(1, 32, 20)
shadow_client.configureConnectDisconnectTimeout(10)  # 10 sec
shadow_client.configureMQTTOperationTimeout(5)  # 5 sec

count = 0
while True:
    try:
        # Connect to AWS IoT
        shadow_client.connect()
        logger.info("Connected using config: {}".format(config))
        break
    except:
        count += 1
        logger.warn("Failed connection: {} times".format(count))
        time.sleep(5)
        pass

# Only after success, set up GPIO
GPIO.setmode(GPIO.BOARD)
for pin in map(lambda p: p[0], PINS.values()):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO_OFF)

# Create a deviceShadow with persistent subscription
device = shadow_client.createShadowHandlerWithName(config['device_name'], True)
device.shadowUpdate(pins_to_shadow(), update_callback, 5)

# Listen on deltas
device.shadowRegisterDeltaCallback(control_callback)

try:
    # Loop forever
    while True:
        pass
except:
    GPIO.cleanup()
    logger.warn('Terminated')
    print 'Terminated'
