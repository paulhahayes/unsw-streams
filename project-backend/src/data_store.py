'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

# YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'users': {


    },
    'channels': [#{channelid, all_members[u_id]}

    ],
    #dms[dm_index]{name, message}
    'dms': {


    },
    'owners' : {

    },

    'message': [
    
    ],
    
    'removed_users' : [

    ],

    'standup': {
        #list of dictionaries {channel_id, time_finish}
        'standup_active': [] 
        #channel_id: [{'handle':handle, 'message':message}]
    },

    'user_stats' : {

    },
    'workspace_stats': {
        'channels_exist': [],
        'dms_exist': [],
        'messages_exist':[],
        'utilization_rate': 0
    },
    'workspace_stats_initialised': False
}
# YOU SHOULD MODIFY THIS OBJECT ABOVE


class Datastore:
    "Data"
    def __init__(self):
        "Allows data Access"
        self.__store = initial_object

    def get(self):
        "Returns data upon request"
        return self.__store

    def set(self, store):
        "Check there is available data"
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store


print('Loading Datastore...')

global data_store
data_store = Datastore()
