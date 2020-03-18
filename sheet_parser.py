#
# SheetParser
#
#    gets data out of the main google worksheet.
#
import os
from typing import List, Dict
from loguru import logger

from lxml import html, etree
#from lxml.etree import tostring

import pandas as pd


class SheetParser():
    " parse the google doc sheet that is source-of-truth for the project "

    def __init__(self):
        pass

    def get_config(self, content: bytes, tab: str) -> List[Dict]:
        " gets a tab from the sheet as a data frame"
        tree = html.fromstring(content)
        menu = self.get_menu(tree)

        x_id = menu[tab]
        states_table = tree.get_element_by_id(x_id)[0][0]
        return self.htmltable_to_json(states_table)

    def get_menu(self, tree: etree) -> Dict[str, str]:
        " gets the tabs from a google sheet "
        xmenu = tree.get_element_by_id("sheet-menu")
        menu = {}
        for x in xmenu:
            if x.tag == "li":
                x_id = x.attrib["id"].replace("sheet-button-", "")
                x_label = x[0].text
                menu[x_label] = x_id
        return menu

    def htmltable_to_json(self, table: etree) -> List[Dict]:
        " converts a google sheet tab into List of Dict"
        names = []
        result = []
        cnt = 0
        for row in table[1]:
            if cnt == 0:
                for col in row:
                    names.append(col.text)
            elif cnt == 1:
                pass # freeze-bar
            else:
                i = 0
                vals = {} 
                for col in row:
                    if len(col) == 0: 
                        val = col.text                        
                    elif col[0].tag == 'a':
                        val = col[0].get("href")
                    else:
                        val = html.tostring(col)
                    n = names[i]
                    if n !=None: vals[n] = str(val)
                    i += 1
                result.append(vals)
            cnt += 1

        return result

    def htmltable_to_dataframe(self, table: etree) -> pd.DataFrame:
        " converts a google sheet tab into a data frame"
        names = []
        data = []
        cnt = 0
        for row in table[1]:
            if cnt == 0:
                for col in row:
                    names.append(col.text)
                    data.append([])
            elif cnt == 1:
                pass # freeze-bar
            else:
                i = 0
                for col in row:
                    if len(col) == 0: 
                        val = col.text                        
                    elif col[0].tag == 'a':
                        val = col[0].get("href")
                    else:
                        val = html.tostring(col)
                    data[i].append(val) 
                    i += 1
            cnt += 1

        xcols = {}
        for n, d in zip(names, data):
            if n is None: continue
            xcols[n] = d

        df = pd.DataFrame(xcols)
        return df




