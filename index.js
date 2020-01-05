let mqtt = require("mqtt");

let client  = mqtt.connect('mqtt://192.168.0.100', {username:"modbus-gateway", password:"ipR9Lsj8sPZvj2rpzLEtY"});

const topics = [
    "modbus/switchboard_controller_input/state/door1_opened",
    "modbus/switchboard_controller_input/state/door2_opened",
    "modbus/switchboard_controller_input/state/door3_opened",
];

client.on('connect', () => {
    topics.forEach((topic) => {
        client.subscribe(topic, (err) => {
            if(err){
                console.log(topic, "err", err);
            }
        });
    });
});

client.on('message', (topic, message) => {
    // message is Buffer
    console.log(topic, message.toString());
    if(topic === "modbus/switchboard_controller_input/state/door3_opened") {
        if(message.toString() === "True") {
            console.log("open portal, sw on light");
            client.publish('modbus/switchboard_controller_relay/set/portal_light', "True");
        } else {
            console.log("closed portal, sw off light");
            client.publish('modbus/switchboard_controller_relay/set/portal_light', "False");
        }
    }
    // client.end()
})
