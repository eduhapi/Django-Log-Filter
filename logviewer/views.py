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

def parse_log_timestamp(log_line):
    # Check if the line contains a valid timestamp format before parsing
    if len(log_line) >= 24 and log_line[4] == '-' and log_line[7] == '-' and log_line[10] == ' ' and log_line[13] == ':' and log_line[16] == ':' and log_line[19] == ',':
        timestamp_str = log_line[:19]  # Extract timestamp string
        try:
            log_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            return log_timestamp.strftime('%H:%M')  # Format to HH:MM only
        except ValueError:
            print(f"Error parsing timestamp: {timestamp_str}")
    return None  # Return None if timestamp parsing fails or line doesn't contain valid format

def filter_logs(request):
    search_query = request.GET.get('search_query')
    logs_to_display = []
    default_message = ""  # Initialize default_message

    if search_query:
        # server details
        server_ip = '1.2.3.'
        username = 'username'
        password = 'password'

        # Get today's date and format it for log file name
        today_date = datetime.now().strftime('%Y-%m-%d')
        log_path = f'/opt/rh/INTERFACE/GBLP/log/logFile.{today_date}.log'

        logs_from_server = fetch_logs_from_server(server_ip, username, password, log_path)

        if logs_from_server:
            # Get current time and calculate time delta for required minutes
            current_time = datetime.now()
            time_threshold = current_time - timedelta(minutes=240)

            # Keep track of latest 3 logs within the time threshold
            latest_logs = []
            for log_line in logs_from_server:
                log_timestamp = parse_log_timestamp(log_line)
                
                if log_timestamp and log_timestamp >= time_threshold.strftime('%H:%M') and search_query in log_line:
                    latest_logs.append(log_line)
                    if len(latest_logs) >= 3:
                        break
            
            # Reverse the order to display latest logs first
            logs_to_display = reversed(latest_logs)

    else:
        # No search query provided, set default message
        default_message = "Enter words to search for in logs."

    # Pass current log file name to template
    current_log_file = f"logFile.{datetime.now().strftime('%Y-%m-%d')}.log"

    return render(request, 'logviewer/logs.html', {'logs': logs_to_display, 'search_query': search_query, 'default_message': default_message, 'current_log_file': current_log_file})
