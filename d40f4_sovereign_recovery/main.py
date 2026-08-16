from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "project": "aimetaverse-d40f4",
        "status": "SOVEREIGN RECOVERY",
        "founder": "CyGeL White (#MrGGTP)",
        "agents": 25,
        "message": "Original App Engine build recovered from C25_DEPLOY_MASTER"
    })

@app.route('/agents/<name>')
def agent_status(name):
    return jsonify({"agent": name, "status": "ACTIVE", "local_inference": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
