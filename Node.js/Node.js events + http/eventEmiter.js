const EventEmitter = require('events');

var url = "http://mylogger.io/log";

class Logger extends EventEmitter {
    log(message) {
	    console.log(message);
	    this.emit("messageLogged", {name: "brmbrm", age: 23});
	}
}



module.exports = Logger;
