import streamlit as st
import pandas as pd
import re
import plotly.express as px
from bs4 import BeautifulSoup
from datetime import datetime

from html_scripts import boxkpi,boxnumberpercentage
from datafunctions import propertydata,followup


