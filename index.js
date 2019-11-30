let mqtt = require("mqtt");

let client  = mqtt.connect('mqtt://192.168.0.100')

client.on('connect', () => {
    client.subscribe('modbus/rpi/state/door3_opened', (err) => {
        if(err){
            console.log("modbus/rpi/state/door3_opened err", err);
        }
    });
});

client.on('message', (topic, message) => {
    // message is Buffer
    console.log(message.toString());
    // client.end()
})
