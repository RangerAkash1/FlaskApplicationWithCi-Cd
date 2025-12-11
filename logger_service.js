const express = require("express");
const bodyParser = require("body-parser");
const winston = require("winston");
const LokiTransport = require("winston-loki");

const app = express();
app.use(bodyParser.json());

const logger = winston.createLogger({
  transports: [
    new LokiTransport({
      host: "http://localhost:3100",  // loki endpoint
      labels: { job: "flask_app_logs" },
      json: true,
      interval: 5
    })
  ]
});

app.post("/log", (req, res) => {
    const { level, message } = req.body;

    logger.log({
        level: level || "info",
        message: message || "empty message"
    });

    return res.json({ status: "logged" });
});

app.listen(4000, () => {
    console.log("Winston-Loki logger running on port 4000");
});
