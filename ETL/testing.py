# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 16:26:06 2019

@author: Joey-Ward
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 10:27:36 2019

@author: Joey-Ward
"""

import os
import sys
import pandas as pd
import requests
import json
import time
import glob
import datetime
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime
from pandas.io.common import ParserError#, FileNotFoundError
from multiprocessing import Pool

sys.path.append(os.environ['FW_Functions'])
sys.path.append(os.environ['send_email'])
sys.path.append(os.environ['elt_history'])
import FW_Functions as fw
from send_email import send_email
from elt_history import *
import sqlalchemy as sa


