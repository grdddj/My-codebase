

const Logger = require("./eventEmiter");
const logger = new Logger();

logger.on("messageLogged", (arg) => {
	console.log("Look what is being logged:", arg);
});


logger.log("message");

