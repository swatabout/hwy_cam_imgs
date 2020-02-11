import os, sys, requests, json, time, glob
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from pandas.io.common import ParserError#, FileNotFoundError
from multiprocessing import Pool

sys.path.append(os.environ['FW_Functions'])
sys.path.append(os.environ['send_email'])
sys.path.append(os.environ['elt_history'])
import FW_Functions as fw
from send_email import send_email
from elt_history import *
import sqlalchemy as sa


