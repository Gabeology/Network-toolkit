import os
import sys
import nmap

# 1. Figure out if we are running on Render (Linux) or locally (Windows)
if sys.platform.startswith('win'):
    # You are on Windows (Local VS Code)! Tell it to look at your standard installer path
    nmap_path = r"C:\Program Files (x86)\Nmap\nmap.exe"
    nm = nmap.PortScanner(nmap_search_path=[nmap_path])
else:
    # You are on Linux (Render Cloud)! Use the portable binary we bundled
    nmap_path = os.path.join(os.path.dirname(__file__), 'bin', 'nmap')
    
    # Crucial Render Fix: Force Linux execution permissions on the binary file
    try:
        os.chmod(nmap_path, 0o755)
    except Exception as e:
        print(f"Note: Could not alter permissions: {e}")
        
    nm = nmap.PortScanner(nmap_search_path=[nmap_path])

from flask import Flask, render_template, request
import nmap

app = Flask(__name__)
import os

# Tell python-nmap to use our custom portable binary path
nmap_path = os.path.join(os.path.dirname(__file__), 'bin', 'nmap')
nm = nmap.PortScanner(nmap_search_path=[nmap_path])

@app.route('/', methods=['GET', 'POST'])
def index():
    scan_results = []
    
    target = request.form.get('target') if request.method == 'POST' else ""
    
    if target:
        try:
            nm.scan(hosts=target, arguments='-v -F')
            for host in nm.all_hosts():
                for proto in nm[host].all_protocols():
                    ports = nm[host][proto].keys()
                    for port in ports:
                        state = nm[host][proto][port]['state']
                        name = nm[host][proto][port]['name']
                        scan_results.append({
                            "port": port,
                            "protocol": proto,
                            "state": state,
                            "service": name
                        })
        except Exception as e:
            scan_results = [{"error": str(e)}]


    return render_template('index.html', results=scan_results, target=target)
if __name__ == '__main__':
    app.run(debug=True)