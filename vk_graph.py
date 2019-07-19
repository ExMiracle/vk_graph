##url = https://oauth.vk.com/authorize?client_id=6878148&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=2&response_type=token&v=5.92

import requests, time, webbrowser, threading, urllib, socket
import networkx as nx
import matplotlib.pyplot as plt
from timeit import default_timer as timer
#import http.server

class Api_token():
    def __init__(self, url):
        self.code_url = url
        self.token = None
#        self.HOST = 8000
#        self.PORT = '127.0.0.1'
    
#    def http_server(self, server_class=http.server.HTTPServer, handler_class=http.server.BaseHTTPRequestHandler):
#        server_address = ('', 8000)
#        httpd = server_class(server_address, handler_class)
#        httpd.serve_forever()
          
    def server_run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 8000))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                       break
                    conn.sendall(data)
                    d = data.decode()
    ##      transforms d to code, however there might be exceptions
                    parsed = urllib.parse.urlparse(d)
                    code  = urllib.parse.parse_qs(parsed.query).get('code')[0].split()[0]
                    access_t_geturl = 'https://oauth.vk.com/access_token?client_id=6888321&client_secret=localvar&redirect_uri=http://localhost:8000&code='+code
                    token = requests.get(access_t_geturl).json()['access_token']
                    self.token = token
    
    def browser(self):
        webbrowser.open(self.code_url)
    
    def receive_access_token(self):
#        http_start = threading.Thread(target=self.http_server)
        server_listening = threading.Thread(target=self.server_run)
        open_browser = threading.Thread(target=self.browser)
        
        server_listening = threading.Thread(target=self.server_run)
        open_browser = threading.Thread(target=self.browser)
        
        
        print('Starting threads.')
#        http_start.start()
        server_listening.start()
        open_browser.start()
        print('All threads have started.')
        
        while self.token == None:
            time.sleep(1)
            
        print('Closing threads.')
#        http_start.join()
        server_listening.join()
        open_browser.join()
        print('Threads successfully closed.')



def api_query(method, access_token, parameters=''):
#    pass code_contanier
    
    method_url = "https://api.vk.com/method/"
    params = {
        'access_token': access_token,
        'v': '5.92',
    }
    if method == 'friend_list':
        return requests.get(method_url+'friends.get',
                            params=params).json()['response']['items']
    if method == 'friend_info':
#        pass stringified and separated by comas friend_list here
        return requests.get(method_url+'users.get', 
                            params = {**params, **parameters}).json()['response']
    if method == 'mutual_friends':
#        pass mutparams = {'target_uid': plist[i]['id']}
        return requests.get(method_url+'friends.getMutual',
                            params = {**params, **parameters})
    else:
        print('Something is wrong. Check check api_query.')
# =============================================================================
#         
# =============================================================================
def constructor(api_token):
    my_friends = api_query('friend_list', api_token)
    str_my_friends = ','.join(my_friends)
    userparams = {'user_ids':str_my_friends}
    friends_user_info = api_query('friend_info', api_token, userparams)
    
    def deactivated(friends_info):
        deleted=[]
        for person in friends_info:
            if 'error' in person.keys():
                print('Error in friends.')
            if 'deactivated' in person.keys():
                deleted.append(person['id'])
                friends_info.remove(person)
            else:
                pass
        return deleted

    def build_dictionaries(for_deletion):
        mydict, labels = {}
        for friend in friends_user_info:
            time.sleep(0.35)
            mutual_parameters = {'target_uid': friend['id']}
            mutual_friends = api_query('friend_info', api_token, mutual_parameters)
            if mutual_friends.status_code != 200:
                print('Cannot fetch mutual friends.')
            if mutual_friends == '':
                pass
            else:
                clean_mutual_friends = mutual_friends['response']
                for friend in clean_mutual_friends:
                    if friend in for_deletion:
                        clean_mutual_friends.remove(friend)
##                creating a list with deactivated friends that are mutual
##                delete deleted mutual friends from mutuals
                mydict[friend['id']] = clean_mutual_friends
                labels[friend['id']] = ' '.join([friend['first_name'],friend['last_name']])
                return [mydict, labels]
    build_dictionaries(deactivated(friends_user_info))



def drawing_graph(dictionary, label_dictionary):
    G = nx.Graph()
    G = nx.Graph(dictionary)
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=30, cmap=plt.cm.viridis, 
                           node_color=range(len(G.nodes)))
    nx.draw_networkx_edges(G, pos, width=1)
    nx.draw_networkx_labels(G, pos, labels=label_dictionary)
#    limits=plt.axis('off')
    
    def friend_count_legend(dictionary, label_dictionary, graph):
#        , graph in variables but not sure why
#    pass dictionary with friends and get friends with highest mutual connections
        degree_list=[]
        for node in [*dictionary]:
            degree_list.append((node, graph.degree(node)))
#            graph. prefix before degree
        id_degree=sorted(degree_list, key=lambda fr: fr[1], reverse=True)
        legend = str("Максимальное количество общих друзей:"+"\n"+
                     label_dictionary[id_degree[0][0]] + ":" + str(id_degree[0][1])+"\n"+
                     label_dictionary[id_degree[1][0]] + ":" + str(id_degree[1][1])+"\n"+
                     label_dictionary[id_degree[2][0]] + ":" + str(id_degree[2][1]))
        return legend
    
    plt.title(friend_count_legend(dictionary, label_dictionary, G))
    plt.show()
    
    
def main():
    
    start = timer()
    
    url = "https://oauth.vk.com/authorize?client_id=6888321&display=page&redirect_uri=http://localhost:8000&scope=friends&response_type=code&v=5.101"
    dummy = Api_token(url)
    
    access_token = dummy.receive_access_token()
    dictionaries = constructor(access_token)
    drawing_graph(dictionaries[0], dictionaries[1])

    end = timer()
    print("Time elapsed:"+"\n"+str(end - start))
    
    

if __name__ == "__main__":
    main()







#
###url = https://oauth.vk.com/authorize?client_id=6878148&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=2&response_type=token&v=5.92
#
#import requests, time, webbrowser, threading, urllib, socket, subprocess
#import networkx as nx
#import matplotlib.pyplot as plt
#from timeit import default_timer as timer
###import graphviz
###import pydot
#start = timer()
#
###get code for access token
#code = None
#HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
#PORT = 8000
#code_url = "https://oauth.vk.com/authorize?client_id=6888321&display=page&redirect_uri=http://localhost:8000&scope=friends&response_type=code&v=5.92"
#code_container = []
#class myThread (threading.Thread):
#   def __init__(self, threadID, name):
#      threading.Thread.__init__(self)
#      self.threadID = threadID
#      self.name = name
#   def run(self):
#      print ("Starting " + self.name)
#      if self.threadID == 1:
#          server_run(self.name)
###          if code != None:
###              threadName.exit()
#          
#      else:
#          time.sleep(3)
#          browser(self.name,code_url)
#      print ("Exiting " + self.name)
#        
#
#
###listens to server all the time and it will exit if code is received
#def server_run(threadName):
#    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#        s.bind((HOST, PORT))
#        s.listen()
#        conn, addr = s.accept()
#        with conn:
#            print('Connected by', addr)
#            while True:
#                data = conn.recv(1024)
#                if not data:
#                   break
#                conn.sendall(data)
#                d = data.decode()
###      transforms d to code, however there might be exceptions
#                parsed = urllib.parse.urlparse(d)
#                code  = urllib.parse.parse_qs(parsed.query).get('code')[0].split()[0]
#                code_container.append(code)
#                access_t_geturl='https://oauth.vk.com/access_token?client_id=6888321&client_secret=111&redirect_uri=http://localhost:8000&code='+code_container[0]
#                access = requests.get(access_t_geturl).json()['access_token']
#                code_container.append(access)
#
###opens codeurl in browser and exits
#def browser(threadName, code_url):
#    webbrowser.open(code_url)
#    
#    
#
#### Create new threads
#thread1 = myThread(1, "Thread-1")
#thread2 = myThread(2, "Thread-2")
###
#### Start new Threads
#thread1.start()
#thread2.start()
#thread1.join()
#thread2.join()
#
###access_t_geturl='https://oauth.vk.com/access_token?client_id=6888321&client_secret=BxeuIwpjdJcMKAmHmugP1&redirect_uri=http://localhost:8000&code='+code_container[0]
###print(access_t_geturl)
###access = requests.get(access_t_geturl)
###print(access)
#
#
###url building
###code_url = "https://oauth.vk.com/authorize?client_id=6888321&display=page&redirect_uri=http://localhost:8000&scope=friends&response_type=code&v=5.92"
#
#
#method_url = "https://api.vk.com/method/"
#params = {
#    'access_token': code_container[1],
#    'v': '5.92',
#}
#
#
#
#
###my friend count and list
#people = requests.get(method_url+'friends.get', params=params).json()['response']['items']
#
###gets user info and deletes all deleted people
#pstr=""
#for p in people:
#    pstr = pstr+str(p)+","
#userparams = {'user_ids': pstr[:-1]}
#plist = requests.get(method_url+'users.get', params = {**params, **userparams}).json()['response']
###delete deactivated people and make deleted list
#deleted=[]
###newpeople = []
#for i in range(0,len(plist)-1):
#    try:
#        if 'deactivated' in plist[i].keys():
#            deleted.append(plist[i]['id'])
#            del plist[i]
###        newpeople.append(plist[i]['id'])
#    except:
#        break
#
###building dicitonary for graph
###mydict = {83249487:newpeople}
#mydict = {}
#labels = {}
#for i in range (0, len(plist)-1):
###    vk limits my side to 3 api requests per second so every 3 requests i wait 
#    if i % 3 == 0:
#        time.sleep(1)
#    mutparams = {'target_uid': plist[i]['id']}
#    mut = requests.get(method_url+'friends.getMutual', params = {**params, **mutparams})
#    if mut.status_code != 200:
#        print("something is not ok")
#    mut = mut.json()
###    check for no mutual friends
###    check for deactivated mutual friends    
#    dmut = mut['response']
#    fordel = []
###    does this even happen? really it is never empty because if deactivated throws exception
#    if mut == "":
#        print("Surprise! mut is empty.")
#    else:
#        for entry in dmut:
#            if entry in deleted:
###                creating a list with deactivated friends that are mutual
###                delete deleted mutual friends from mutuals
#                fordel.append(entry)
#        for entry in fordel:
#            dmut.remove(entry)
#        mydict[plist[i]['id']] = dmut
#        labels[plist[i]['id']] = str(plist[i]['first_name']) +" "+ str(plist[i]['last_name'])
#
#
##creates a set of labels extracting data from plist
###labels = {83249487:"Илья Самарин"}
#
###for i in range(0,len(plist)-1):
###    labels[plist[i]['id']] = str(plist[i]['first_name']) +" "+ str(plist[i]['last_name'])
#
###draw a graph
