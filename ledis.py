import time

# helper to remove duplicate for SADD
def remove_duplicates(lst):
    temp = {}
    for i in lst:
        temp[i] = 0
    return list(temp.keys())

print("heee")
global keyErrorMessage
keyErrorMessage = "ERROR: Key not found"  # JIC we want to update for some weird reason


class Ledis:
    def __init__(self):
        self.dic = {}  # key is a string, values will be list type.
        self.expire = {}  # same keys but value are the time stamp and an expiration time
        self.snapShot = {}
        self.snapExpire = {}

    def clean_dict(self):
        # to remove any expired key from dictionary
        try:
            for i in self.expire.keys():
                if self.expire[i][1] == None:  # no expiration set yet
                    pass
                else:
                    current_time = time.time()
                    elapsed_time = current_time - self.expire[i][0]  # how much time passed since item was created
                    if elapsed_time > self.expire[i][1]:  # if time passed > expiration time set
                        self.DEL(i)
        except:
            pass


    def check_string(self,key):
        if type(self.dic[key]) == str:
            return True
        return False


    def SET(self, key, val):  # val is a list but we only care if this list have one element
        if len(val) > 1:
            return "ERROR: Too Many Values Entered"
        if key not in self.dic.keys():
            self.dic[key] = val[0]  # add key,val pair into dictionary
            print(val, val[0])
            self.expire[key] = [0, None]  # set a current time and an expire date as None initially
            return "OK"
        else:
            if self.check_string(key):  # check if passed in a set key
                self.dic[key] = val[0]  # add key,val pair into dictionary
                print(val, val[0])
                self.expire[key] = [0, None]  # set a current time and an expire date as None initially
                return "OK"
            else:
                return "ERROR: Set Key Passed"



    def GET(self, key):
        self.clean_dict()  # clean dict before getting elements
        try:
            if self.check_string(key) == False:
                return "ERROR: Set Key Passed"
            return self.dic[key]
        except:
            return keyErrorMessage


    def SADD(self, key, values):  # value will be a list of element handled in flask
        self.clean_dict()  # clean dict before getting elements

        # store set as a value in the dic
        try:
            if self.check_string(key):
                return "ERROR: String Key Passed"
            count = len(self.dic[key])  # initial count
            self.dic[key] += values  # adding all values
            self.dic[key] = remove_duplicates(self.dic[key])  # removing duplicates

            count = len(self.dic[key]) - count  # new count
            return count

        except:
            self.dic[key] = remove_duplicates(values)  # make a new key and remove any duplicates
            self.expire[key] = [0, None]  # set 0 initially and expiration time as None
            count = len(self.dic[key])  # new count
            return count

    def SREM(self, key, values):
        self.clean_dict()  # clean dict before getting elements
        try:
            if self.check_string(key):
                return "ERROR: String Key Passed"
            count = 0  # how many are being removed
            for val in values:
                if val in self.dic[key]:
                    self.dic[key].remove(val)
                    count += 1
            return count
        except:
            return keyErrorMessage

    def SMEMBERS(self, key):
        self.clean_dict()  # clean dict before getting elements
        try:
            if self.check_string(key):
                return "ERROR: String Key Passed"
            return list(self.dic[key])
        except:
            return keyErrorMessage

    def SINTER(self, keys):  # keys is a list of key strings
        self.clean_dict()  # clean dict before getting elements
        try:
            last_key = keys[-1]
            if self.check_string(last_key):   # check the last key-set first
                return "ERROR: String Key Passed"

        # set last set in dict = interesction set
            lst = list(self.dic[last_key])[::]    # isolate the last key-set for comparison later
            keys.pop()  # no need to check the last key-set again
            for key in keys:
                if self.check_string(key):
                    return "ERROR: String Key Passed"
                i = 0
                while i < len(lst):
                    val = lst[i]
                    if val not in self.dic[key]:
                        lst.remove(val)
                        i -= 1
                    i += 1
            return lst
        except:
            return keyErrorMessage

    def KEYS(self):
        self.clean_dict()  # clean dict before getting elements
        return list(self.dic.keys())

    def DEL(self, key):  # delete a key
        val = self.dic.pop(key, None)  # return None if does not exist
        if val == None:
            return keyErrorMessage
        else:
            del self.expire[key]  # delete from expire as well
            return "OK"

    def EXPIRE(self, key, secs):  # time is a string
        self.clean_dict()
        try:
            self.expire[key] = [time.time(), int(secs)]  # set the expiration date
            return secs
        except:
            return keyErrorMessage

    def TTL(self, key):
        self.clean_dict()
        try:
            if self.expire[key][1] != None:  # there exists an expiration
                # returning expiration time set minus the difference of current time and time when key was created
                # essentially expiration time minus how much time has passed since creation
                return self.expire[key][1] - (time.time() - self.expire[key][0])
        except:
            return keyErrorMessage

    def SAVE(self):
        self.snapshot = {}  # making sure its empty in case a snapshot has already been taken once
        self.snapExpire = {}

        for key in self.dic.keys():
            self.snapshot[key] = list(self.dic[key])[::]
        for key in self.expire.keys():
            self.snapExpire[key] = list(self.expire[key])[::]

        return "OK"

    def RESTORE(self):
        self.dic = {}
        self.expire = {}

        for key in self.snapshot.keys():
            self.dic[key] = list(self.snapshot[key])[::]
        for key in self.snapExpire.keys():
            self.expire[key] = list(self.snapshot[key])[::]

        return "OK"


