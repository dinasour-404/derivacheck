const express = require("express");
const app = express();
app.use(express.json());

app.post("/detect", (req, res) => {
  const message = req.body.message.toLowerCase();

  const phishingPatterns = [
    "urgent",
    "password",
    "login",
    "click here",
    "verify",
    "bank",
    "account suspended"
  ];

  let detected = phishingPatterns.some(word => message.includes(word));

  res.json({
    safe: !detected,
    reason: detected ? "Phishing pattern detected" : "No issues"
  });
});

app.listen(3000, () => console.log("Server running on port 3000"));