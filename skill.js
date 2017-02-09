/* eslint-disable  func-names */
/* eslint quote-props: ["error", "consistent"]*/
'use strict';

const Alexa = require('alexa-sdk');
var AWS = require('aws-sdk');
// Get config from AWS env variables
const config = process.env;

AWS.config.region = config.REGION;
const APP_ID = config.APP_ID
var iotData = new AWS.IotData({endpoint: config.ENDPOINT});

const handlers = {
    'LaunchRequest': function () {
        this.emit('ControlDevice');
    },
    'ControlDeviceIntent': function () {
        this.emit('ControlDevice');
    },
    'ControlDevice': function () {
        const intent = this.event.request.intent;
        var device = intent.slots.Device.value.toLowerCase();
        const state = intent.slots.State.value.toLowerCase();
        const speechOutput = device + ' ' + state;

        if (device == 'air conditioner') {
            device = 'ac';
        }

        var payloadObj={
            state: {
                desired: {
                    // always move projector
                    [device]: (state == "on" || device == "projector") ? true : false
                }
            }
        };
        var paramsUpdate = {
            "thingName" : config.DEVICE_NAME,
            "payload" : JSON.stringify(payloadObj)
        };

        iotData.updateThingShadow(paramsUpdate, (err, data) => {
          if (err){
            console.error("Error updating shadow: " + err + " " + data);
          }
          else {
            console.log("Success: " + speechOutput);
            this.emit(':tellWithCard', speechOutput);
          }
        });
    },
    'AMAZON.HelpIntent': function () {
        const speechOutput = 'You can ask pi to control the lamp, speakers, projector, and ac.';
        const reprompt = 'What would you like pi to do?';
        this.emit(':ask', speechOutput, reprompt);
    },
    'AMAZON.CancelIntent': function () {
        this.emit(':tell', 'See ya!');
    },
    'AMAZON.StopIntent': function () {
        this.emit(':tell', 'See ya!');
    },
    'SessionEndedRequest': function () {
        this.emit(':tell', 'See ya!');
    },
};

exports.handler = (event, context, callback) => {
    const alexa = Alexa.handler(event, context);
    alexa.appId = APP_ID;
    alexa.registerHandlers(handlers);
    alexa.execute();
};
