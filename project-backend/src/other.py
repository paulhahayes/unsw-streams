"""
hansol choi z5338373 - clear_v1
"""
from src.data_store import data_store
import pickle

def clear_v1():
    """
    this function will reset data to initial state
    """

    try:
        store = pickle.load(open("data.p", "wb")) #disable=E0602
    except Exception:
        store = data_store.get()    
        
    store['users'].clear()
    store['channels'].clear()
    store['owners'].clear()
    store['dms'].clear()
    store['removed_users'].clear()
    store['message'].clear()
    store['standup'] = {'standup_active':[]}
    store['workspace_stats'] = {
        'channels_exist': [],
        'dms_exist': [],
        'messages_exist':[],
        'utilization_rate': 0
    }
    store['workspace_stats_initialised'] = False
    data_store.set(store)
