import socket
import pickle  # 用于序列化和反序列化数据
import mysql.connector
from datetime import datetime
import redis
import random
import uuid
import time, random

# Data used for simulation purposes.
port_dict = {"1": 123, "2": 124, "3": 125}
IP = "127.0.0.1"


connection = mysql.connector.connect(
    host="localhost", user="root", port=3306, password="123456", database="db1"
)
redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)
cursor = connection.cursor()


def getServer(user_id):
    return (IP, port_dict[redis_client.get(user_id)])

#execute next hop in another sever
def execute_remote_query(query, server_address):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)
    serialized_data = pickle.dumps((query))
    client_socket.send(serialized_data)
    client_socket.close()

    return result

#execute current transaction
def executeQuery(query):
    print(len(query))
    print(f"Receive Query {query}")
    try:
        cursor.execute(query[0][0], query[0][1])
        print(cursor.fetchall())
    except Exception as e:
        connection.rollback()
        return False
    connection.commit()
    return True


def start_server():
    host = "127.0.0.1"
    port = 123

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1000)

    print(f"Server 1 listening on {host}:{port}")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        data = conn.recv(1024)
        query = pickle.loads(data)

        try:
            result = executeQuery(query)
            serialized_result = pickle.dumps(result)
            conn.send(serialized_result)
            # If there is next hop, find next hop's location and execute
            if len(query) > 1:
                print(len(query[1]))
                if len(query[1]) > 2:
                    execute_remote_query(query[1:], getServer(query[1][2]))
                else:
                    print(query[1:])
                    for portNum in port_dict.values():
                        server_address = (IP, portNum)
                        print(server_address)
                        if portNum != port:
                            # time.sleep(random.uniform(0.01, 0.1))
                            execute_remote_query(query[1:], server_address)
                        else:
                            cursor.execute(query[1][0], query[1][1])
        except Exception as e:
            print(f"Error executing query: {e}")
            conn.send(pickle.dumps(None))  # Sending None for error case
        finally:
            connection.close()
            conn.close()


if __name__ == "__main__":
    start_server()
