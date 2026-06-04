from flask import Flask, render_template, request
import nmap

app = Flask(__name__)
nm = nmap.PortScanner()

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