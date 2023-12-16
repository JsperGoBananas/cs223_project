import socket
import pickle  
from datetime import datetime
import redis
import random
import time
import uuid
import concurrent.futures
import time

# redis act as shared dictionary
redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)
#simulated server port to IpIdentifier mapping
port_dict = {"1": 123, "2": 124, "3": 125}
IP = "127.0.0.1"
#test cases for posts
posts = [
    "3f7fed90-9aaf-11ee-8ffb-0242ac120004",
    "3ff18630-9aaf-11ee-8ffb-0242ac120004",
    "47afeecb-9a42-11ee-a8d0-0242ac120002",
    "93e11ceb-9a44-11ee-a8d0-0242ac120002",
    "c90658ee-9aaf-11ee-8e20-0242ac120003",
    "c969b56b-9aaf-11ee-8e20-0242ac120003",
]
#test cases for users
user_ids = [
    "7ab6ee3e-0857-4ee9-ba60-8da39404cd09",
    "64666529-640f-4f2f-a7dd-087de4942d95",
    "74961034-d9a6-4d33-ad6e-96a908b64608",
]


def execute_remote_query(query, server_address):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    serialized_data = pickle.dumps((query))
    client_socket.send(serialized_data)

    serialized_result = client_socket.recv(1024)
    result = pickle.loads(serialized_result)

    client_socket.close()

    return result


def getServer(user_id):
    return (IP, port_dict[redis_client.get(user_id)])


#Transaction 1
def RegisterUser(username, name, email, birthday):
    if not redis_client.get(username):
        # Simulating the user's location, where IP 1, 2, and 3 represent different geographical positions(NorCal,NoVA,Ohio). 
        ip = random.choice([1, 2, 3])
        print(ip)
        new_uuid = str(uuid.uuid4())
        insert_user_query = "INSERT INTO Users (UserID,Username, Name, Email, Birthday,FriendCount,IpIdentifier) VALUES (%s,%s, %s, %s, %s,0,%s)"
        user_data = (new_uuid, username, name, email, birthday, ip)
        server_address = (IP, port_dict[str(ip)])
        result = execute_remote_query([(insert_user_query, user_data)], server_address)
        print(result)
        # Store the mapping of a user's username, UUID, and IP address in Redis, making it accessible to all programs. All data created by a user with a specific user_id will be stored at the address corresponding to their IP.
        if result:
            redis_client.set(new_uuid, ip)
            redis_client.set(username, new_uuid)
    else:
        print("User Exists")

#Transaction 2
def CreatePost(user_id, content):
    server_address = getServer(user_id)
    insert_post_query = "INSERT INTO Posts (PostID,UserID, CommentCount, Content, Timestamp) VALUES (UUID(),%s, 0, %s, %s)"
    post_data = (user_id, content, datetime.now())
    execute_remote_query([(insert_post_query, post_data)], server_address)



#Transaction 3
def CreateComment(user_id, post_id, content):
    server_address = getServer(user_id)

    # 写入评论的内容
    insert_comment_query = "INSERT INTO Comments (CommentID,UserID, PostID, Content, Timestamp) VALUES (UUID(),%s, %s, %s, %s)"
    comment_data = (user_id, post_id, content, datetime.now())
    # 更新帖子评论数
    update_post_query = (
        "UPDATE Posts SET CommentCount = CommentCount + 1 WHERE PostID = %s"
    )
    update_data = (post_id,)
    execute_remote_query(
        [(insert_comment_query, comment_data), (update_post_query, update_data)],
        server_address,
    )

#Transaction 3 without chopping, for testing
def CreateComment_Seperate(user_id, post_id, content):
    server_address = getServer(user_id)

    # 写入评论的内容
    insert_comment_query = "INSERT INTO Comments (CommentID,UserID, PostID, Content, Timestamp) VALUES (UUID(),%s, %s, %s, %s)"
    comment_data = (user_id, post_id, content, datetime.now())
    # 更新帖子评论数
    update_post_query = (
        "UPDATE Posts SET CommentCount = CommentCount + 1 WHERE PostID = %s"
    )
    update_data = (post_id,)
    execute_remote_query([(insert_comment_query, comment_data)], server_address)
    for portNum in port_dict.values():
        server_address = (IP, portNum)
        execute_remote_query([(update_post_query, update_data)], server_address)


#Transaction 4
def FollowFriend(user_id, friend_id):
    server_address = getServer(user_id)
    insert_friend_query = (
        "INSERT INTO Friendship (FriendshipID,UserID,FriendID) VALUES (UUID(),%s,%s)"
    )
    friend_data = (
        user_id,
        friend_id,
    )
    update_friendcount_query = (
        "Update Users Set FriendCount = FriendCount + 1 where userID = %s"
    )
    user_data = (friend_id,)
    execute_remote_query(
        [
            (insert_friend_query, friend_data),
            (update_friendcount_query, user_data, friend_id),
        ],
        server_address,
    )

#Transaction 4 without chopping, for testing
def FollowFriend_Seperate(user_id, friend_id):
    # 更新朋友关系

    server_address = getServer(user_id)
    insert_friend_query = (
        "INSERT INTO Friendship (FriendshipID,UserID,FriendID) VALUES (UUID(),%s,%s)"
    )
    friend_data = (
        user_id,
        friend_id,
    )
    update_friendcount_query = (
        "Update Users Set FriendCount = FriendCount + 1 where userID = %s"
    )
    user_data = (friend_id,)
    execute_remote_query([(insert_friend_query, friend_data)], server_address)
    server_address = getServer(friend_id)
    execute_remote_query(
        [(update_friendcount_query, user_data, friend_id)], server_address
    )


#Transaction 5
def ViewEmail(user_id):
    server_address = getServer(user_id)
    select_user_query = "SELECT email FROM Users where userID = %s"
    user_data = (user_id,)
    execute_remote_query([(select_user_query, user_data)], server_address)


#Transaction 6
def EditProfile(user_id, new_name, new_email, new_birthday):
    server_address = getServer(user_id)

    update_profile_query = (
        "UPDATE Users SET Name = %s, Email = %s, Birthday = %s WHERE UserID = %s"
    )
    new_profile_data = (new_name, new_email, new_birthday, user_id)
    execute_remote_query([(update_profile_query, new_profile_data)], server_address)


#Transaction 7
def ViewPost(post_id):
    select_post_query = "SELECT * FROM Posts WHERE PostID = %s"
    select_comments_query = "SELECT * FROM Comments WHERE PostID = %s"
    for port in port_dict.values():
        server_address = (IP, port)
        post_data = (post_id,)
        execute_remote_query(
            [(select_post_query, post_data), (select_comments_query, post_data)],
            server_address,
        )

#Transaction 7 without chopping, for testing
def ViewPost_Seperate(post_id):

    select_post_query = "SELECT * FROM Posts WHERE PostID = %s"

    select_comments_query = "SELECT * FROM Comments WHERE PostID = %s"
    for port in port_dict.values():
        server_address = (IP, port)
        post_data = (post_id,)
        execute_remote_query([(select_post_query, post_data)], server_address)
    for port in port_dict.values():
        server_address = (IP, port)
        post_data = (post_id,)
        execute_remote_query([(select_comments_query, post_data)], server_address)




def test_parallel(concurrency):
    # set concurrency
    num_follows = concurrency

    # Use ThreadPoolExecutor to concurrently execute the FollowFriend function.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 记录开始时间
        start_time = time.time()
        # Submit functions to a thread pool and obtain a list of Future objects.
        user_ids = range(num_follows)
        futures = [
            executor.submit(
                CreateComment, random.choice(user_ids), random.choice(posts)
            )
            for _ in range(num_follows)
        ]
        # wait for all tasks completed
        concurrent.futures.wait(futures)
        end_time = time.time()

    # calculate the total elapsed time
    total_time = end_time - start_time
    print(
        f"Total time for {num_follows} CreateComment calls: {total_time/num_follows*1000} milliseconds"
    )

    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        start_time = time.time()

        
        user_ids = range(num_follows)
        futures = [
            executor.submit(
                CreateComment_Seperate, random.choice(user_ids), random.choice(posts)
            )
            for _ in range(num_follows)
        ]
        
        concurrent.futures.wait(futures)
        end_time = time.time()

    # calculate the total elapsed time
    total_time = end_time - start_time
    print(
        f"Total time for {num_follows} CreateComment without chopping calls: {total_time/num_follows*1000} milliseconds"
    )


def test_sequential(repetition):
    # set repitition
    num_follows = repetition


    start_time = time.time()


    for _ in range(num_follows):
        #test functions
        # CreateComment(random.choice(user_ids), random.choice(posts), "Great post!")
        ViewPost(random.choice(posts))
    end_time = time.time()


    total_time = end_time - start_time
    print(
        f"Average time for {num_follows} function calls: {total_time/num_follows*1000} milliseconds"
    )

    start_time = time.time()

    for _ in range(num_follows):
        #test functions
        #    CreateComment_Seperate(random.choice(user_ids), random.choice(posts), "Great post!")
        ViewPost_Seperate(random.choice(posts))
    end_time = time.time()


    total_time = end_time - start_time
    print(
        f"Total time for {num_follows} function without chopping calls: {total_time/num_follows*1000} milliseconds"
    )


if __name__ == "__main__":
    # RegisterUser("jane_doe", "Jane Doe", "jane.doe@example.com", datetime(1990, 1, 1))
    # RegisterUser("jone_dow", "Jone Dow", "jane.dough@example.com", datetime(1992, 1, 1))
    # CreatePost("7ab6ee3e-0857-4ee9-ba60-8da39404cd09","This is a new postaaa.")
    # FollowFriend("7ab6ee3e-0857-4ee9-ba60-8da39404cd09","64666529-640f-4f2f-a7dd-087de4942d95")
    # FollowFriend_Seperate("7ab6ee3e-0857-4ee9-ba60-8da39404cd09","64666529-640f-4f2f-a7dd-087de4942d95")
    # CreateComment("7ab6ee3e-0857-4ee9-ba60-8da39404cd09", "204af367-9a46-11ee-a8d0-0242ac120002", "Great posthahaha!")
    # ViewPost("204af367-9a46-11ee-a8d0-0242ac120002")
    # test_parallel(5000)
    test_sequential(50)
