import socket
import time
import json
import mysql.connector


create_table_query = """
CREATE TABLE speed_test_record.speed_test_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    jitter_ms FLOAT,
    download_speed FLOAT,
    upload_speed FLOAT
);
"""



def latency_jitter_test(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    for _ in range(5):
        start_time = time.time()
        client_socket.recv(1024)
        client_socket.send("Pong".encode())
        end_time = time.time()

        round_trip_time = (end_time - start_time) * 1000
        print(f"Latency/Jitter Test - Round-trip time: {round_trip_time:.2f} ms")
        time.sleep(0.5)
    
    client_socket.close()    
    return round_trip_time

def download_speed_test(server_ip, server_port):
    
    increase_everytime = 1
    download_speeds = []

    for _ in range(5):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client_socket.connect((server_ip, server_port))
            file_size = 1024 * 1024 * increase_everytime
            client_socket.send(f"Download-{file_size}".encode())
            start_time = time.time()
            received_data = client_socket.recv(file_size)
            end_time = time.time()

            download_speed = file_size / (end_time - start_time)
            download_speeds.append(download_speed)
            print(f"Download Speed Test - Speed: {download_speed / 1024:.2f} KB/s")
            increase_everytime = increase_everytime * 2

        except Exception as e:
            print(f"Error connecting to server: {e}")

        finally:
            client_socket.close()

        time.sleep(0.5)

    return download_speeds
def upload_speed_test(server_ip, server_port):
    
    increase_everytime = 1
    upload_speeds = []

    for _ in range(5):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client_socket.connect((server_ip, server_port))
            file_size = 1024 * 1024 * increase_everytime # 1 MB
            client_socket.recv(1024)
            start_time = time.time()
            client_socket.send(f"Upload-{file_size}".encode())
            end_time = time.time()
            upload_speed = file_size / (end_time - start_time)
            upload_speeds.append(upload_speed)
            increase_everytime = increase_everytime * 2 # Linear increase

            print(f"Upload Speed Test - Speed: {upload_speed / 1024:.2f} KB/s")

        except Exception as e:
            print(f"Error in upload speed test: {e}")

        finally:
            client_socket.close()

        time.sleep(0.5)

    return upload_speeds

def save_results_to_db(config, latency, avg_download_speed, avg_upload_speed):
    try:
        connection_params = config["mysql"].copy()
        #connection_params["database"] = "speed_test_record"
        connection = mysql.connector.connect(**connection_params)

        cursor = connection.cursor()

        # Insert the results into the database
        insert_query = """
        INSERT INTO speed_test_record.speed_test_results (jitter_ms, download_speed_kb_sec, upload_speed_kb_sec)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (latency, avg_download_speed, avg_upload_speed))

        connection.commit()

        print("Done \n")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if connection.is_connected():
            connection.close()
            print("Connection closed")            

def read_config_from_json(file_path="config.json"):
    try:
        with open(file_path, "r") as json_file:
            config_data = json.load(json_file)
            return config_data

    except FileNotFoundError:
        print(f"Error: Config file '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON in '{file_path}'.")
        return None


def get_last_result(config):
    try:
        connection_params = config["mysql"].copy()
        connection_params["database"] = "speed_test_record"
        connection = mysql.connector.connect(**connection_params)

        cursor = connection.cursor()

        # Execute the query
        query = """
        SELECT * FROM speed_test_record.speed_test_results
        ORDER BY id DESC
        LIMIT 1;
        """
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()
        if result:
            print("Last result:")
            print(result)
        else:
            print("No results found.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if connection.is_connected():
            connection.close()
            print("Connection closed")


def main():
    
 config = read_config_from_json()

 while True: 
    print("----------------------------------------------------------------------\n")
    print("HII EVERYONE, WELCOME TO THE SPEED TESTING TOOL\n")
    print("----------------------------------------------------------------------\n")
    print("PRESS 1. PERFORMING SPEED TEST ..\n")
    print("PRESS 2. CHECK YOUR LAST SPEED TEST RESULTS..\n")
    print("PRESS 3. FOR SERVER IP AND PORT..\n")
    print("PRESS 4. EXIT..\n")
    option = int(input("Enter your option: "))
    if option == 1:
      server_ip = input("Enter the server IP: ")
      server_port = int(input("Enter the server port: "))
  
      Final_latancy = latency_jitter_test(server_ip, server_port)
      Download_speed = download_speed_test(server_ip, server_port)
      Upload_speed = upload_speed_test(server_ip, server_port)
      
      print(f"Latency/Jitter Test - Round-trip time: {Final_latancy:.2f} ms")
    
      average_down_speed = sum(Download_speed) / len(Download_speed) / 1024
      print(f"Download Speed Test - Average Speed: {average_down_speed:.2f} KB/s")
    
      average_upload_speed = sum(Upload_speed) / len(Upload_speed) / 1024
      print(f"Upload Speed Test - Average Speed: {average_upload_speed:.2f} KB/s")
    
      save_results_to_db(config, Final_latancy, average_down_speed , average_upload_speed)
      continue
      
    if option == 2:
        #code for last result
        get_last_result(config)
        continue
    if option == 3:
        #code for server ip and port
        print(f"Server IP: {config['server']['ip']}\nServer Port: {config['server']['port']}")
        continue
    if option == 4:
        break
    if option < 1 or option > 4:
      print("Invalid option, please try again.")
      continue
    
if __name__ == "__main__":
    main()
