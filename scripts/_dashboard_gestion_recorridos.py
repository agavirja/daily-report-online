import streamlit as st
import pandas as pd
import re
import plotly.express as px
from bs4 import BeautifulSoup
from datetime import datetime

import sys
sys.path.insert(0, '/scripts')
from html_scripts import boxkpi,boxnumberpercentage
from datafunctions import propertydata,followup


