from flask import Flask, render_template, request
from netmiko import ConnectHandler
from netmiko.cisco.cisco_ios import CiscoIosTelnet

app = Flask(__name__)

# Custom class to skip the 'terminal width 511' command that was failing earlier
class CustomCiscoTelnet(CiscoIosTelnet):
    def session_preparation(self):
        pass

@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    error = None

    if request.method == "POST":
        router_device = {
            'device_type': 'cisco_ios_telnet',
            'ip': '192.168.10.60',
            'port': 32770,
            'username': 'admin',
            'password': 'eve123',
            'secret': 'eve123',
            'fast_cli': False,
            'global_delay_factor': 8,       # INCREASED from 4 to 8 to fix Login Failed
            'session_log': 'netmiko_session.log',
        }

        commands_to_run = [
            "show version",
            "show ip interface brief",
            "show running-config",
        ]

        try:
            # Use our custom class instead of ConnectHandler
            net_connect = CustomCiscoTelnet(**router_device)
            
            try:
                net_connect.enable()
            except Exception as e:
                print(f"Enable mode note: {e}")

            # Manually turn off pagination
            net_connect.send_command("terminal length 0", read_timeout=10)

            for cmd in commands_to_run:
                output = net_connect.send_command(cmd, read_timeout=60)
                results[cmd] = output

            net_connect.disconnect()

        except Exception as e:
            error = f"Connection failed: {e}"

    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)