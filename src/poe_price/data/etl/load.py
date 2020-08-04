
from threading import Thread
import logging
import time

import json


from .session import ETLSession

# from .session import ETLSession

# from database import utility.ETLSession as utility

log = logging.getLogger(__name__)

class Loader(Thread):
    '''
    Basic loader thread. Data is simply saved into a specific folder as a json file.
    '''
    def __init__(self, p_cond, p_list, etl_config, conn_config):
        Thread.__init__(self)

        self.p_cond = p_cond
        self.p_list = p_list

        self.l_policy = etl_config['LOAD']['LOAD_POLICY']
        self.save_path = etl_config['LOAD']['SAVE_PATH']
        self.debug = etl_config['LOAD']['DEBUG']

        self.conn_host = conn_config['postgresql']['host']
        self.conn_dbname = conn_config['postgresql']['database']
        self.conn_user = conn_config['postgresql']['user']
        self.conn_password = conn_config['postgresql']['password']

        exec('self.policy = self.{}'.format(self.l_policy))
        if self.l_policy == 'dbLoader':
            self.db_session = ETLSession(self.conn_host, self.conn_dbname, 
                self.conn_user, self.conn_password)
        log.info('[L] - Initialized loader thread. Policy: {}'.format(self.l_policy))

    def run(self):
        while True:
            # pick an element fron the unprocessed data list
            with self.p_cond:
                self.p_cond.wait_for(self._checkProcessedCond)
                elem = self.p_list.pop(0)
                self.p_cond.notify_all()

            a = time.time()
            self.policy(*elem)
            b = time.time()

            log.info('[L] - Stashes loaded in {} seconds.'.format(round(b-a, 2)))

    def _checkProcessedCond(self):
        return len(self.p_list) > 0

    def fsLoader(self, curr_nci, content):
        with open(self.save_path + curr_nci + '.json', 'w+') as file:
            json.dump(content, file)

    def dbLoader(self, curr_nci, currency, mitems, mitems_sockets, mitems_prop, 
            mitems_prop_voc, mitems_mods, mitems_mods_voc):
        
        times = []
        with self.db_session as session:
            # load currency into the poe_trade database
            a = time.time()
            if currency is not None:
                for v in currency.T.to_dict().values():
                    session.insert_currency(v)
            b = time.time()
            times.append(round(b-a, 2))

            a = time.time()
            if mitems_prop_voc is not None:
                mitems_prop_voc = mitems_prop_voc.T.to_dict()
                for k in mitems_prop_voc.keys():
                    session.insert_property_type(k, mitems_prop_voc[k])
            b = time.time()
            times.append(round(b-a, 2))

            a = time.time()
            if mitems_mods_voc is not None:
                mitems_mods_voc = mitems_mods_voc.T.to_dict()
                for k in mitems_mods_voc.keys():
                    session.insert_modifier_type(k, mitems_mods_voc[k])
            b = time.time()
            times.append(round(b-a, 2))

            a = time.time()
            if mitems is not None:
                mitems = mitems.T.to_dict()
                for k in mitems.keys():
                    session.insert_item(k, mitems[k])
            b = time.time()
            times.append(round(b-a, 2))

            a = time.time()
            if mitems_mods is not None:
                for v in mitems_mods.T.to_dict().values():
                    session.insert_item_modifier(v)
            b = time.time()
            times.append(round(b-a, 2))

            a = time.time()
            if mitems_prop is not None:
                for v in mitems_prop.T.to_dict().values():
                    session.insert_item_property(v)
            b = time.time()
            times.append(round(b-a, 2))

            a = time.time()
            if mitems_sockets is not None:
                for v in mitems_sockets.T.to_dict().values():
                    session.insert_item_socket(v)
            b = time.time()
            times.append(round(b-a, 2))

            if self.debug:
                log.debug('[L] - Loading times (seconds): {}'.format(times))

if __name__ == '__main__':
    # db cleaning functiona
    pass