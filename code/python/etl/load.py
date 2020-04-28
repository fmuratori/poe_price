
from threading import Thread
import logging
import time

import json

from database.psycopg2_utility import PoeTradeDBSession

# from database import utility.PoePriceDBSession as utility

log = logging.getLogger(__name__)

class Loader(Thread):
    '''
    Basic loader thread. Data is simply saved into a specific folder as a json file.
    '''
    def __init__(self, p_cond, p_list, config):
        Thread.__init__(self)

        self.p_cond = p_cond
        self.p_list = p_list
        self.config = config['LOAD']

        exec('self.policy = self.{}'.format(self.config['LOAD_POLICY']))

        log.info('[L] - Initialized loader thread. Policy: {}'.format(self.config['LOAD_POLICY']))

    def run(self):
        while True:
            # pick an element fron the unprocessed data list
            with self.p_cond:
                self.p_cond.wait_for(self.checkProcessedCond)
                elem = self.p_list.pop(0)
                p_list_size = len(self.p_list)

            a = time.time()
            self.policy(*elem)
            b = time.time()

            log.info('[L] - Stashes loaded in {} seconds.\tP_LIST_SIZE: {}'.format(round(b-a, 2), p_list_size))

    def checkProcessedCond(self):
        with self.p_cond:
            return len(self.p_list)

    def fsLoader(self, curr_nci, content):
        with open(self.config['SAVE_PATH'] + curr_nci + '.json', 'w+') as file:
            json.dump(content, file)

    def dbLoader(self, curr_nci, currency, mitems, mitems_sockets, mitems_prop, mitems_prop_voc, mitems_mods, \
            mitems_mods_voc):
        times = []
        with PoeTradeDBSession() as session:
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

            if self.config['DEBUG']:
                log.info('[L] - Loading times (seconds): {}'.format(times))

if __name__ == '__main__':
    # db cleaning functiona
    pass
