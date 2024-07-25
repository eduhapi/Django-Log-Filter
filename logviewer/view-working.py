# logviewer/views.py
from django.shortcuts import render
from datetime import datetime, timedelta
import paramiko

def fetch_logs_from_server(server_ip, username, password, log_path):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh_client.connect(server_ip, username=username, password=password)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(f"cat {log_path}")
        logs = ssh_stdout.readlines()
        return logs
    except Exception as e:
        print(f"Error connecting to the server: {e}")
        return []

def filter_logs(request):
    search_query = request.GET.get('search_query')
    logs_to_display = []
    default_message = ""  # Initialize default_message

    if search_query:
        # Update these with your server details
        server_ip = '10.151.1.22'
        username = 'timo'
        password = 'timo123'
        log_path = '/opt/rh/INTERFACE/GBLP/log/logFile.2024-04-26.log'

        logs_from_server = fetch_logs_from_server(server_ip, username, password, log_path)

        if logs_from_server:
            # Get current time and calculate time delta for 10 minutes
            current_time = datetime.now()
            time_threshold = current_time - timedelta(minutes=10)

            # Iterate through logs to find matching lines within the time threshold
            for log_line in logs_from_server:
                # Parse timestamp assuming it's in a specific format (adjust as needed)
                log_parts = log_line.split()
                log_timestamp_str = ' '.join(log_parts[:2])  # Assuming timestamp is in first two parts
                log_timestamp = datetime.strptime(log_timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                if log_timestamp >= time_threshold and search_query in log_line:
                    logs_to_display.append(log_line)

    else:
        # No search query provided, set default message
        default_message = "Enter words to search for in logs."

    return render(request, 'logviewer/logs.html', {'logs': logs_to_display, 'search_query': search_query, 'default_message': default_message})
