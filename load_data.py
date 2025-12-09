import pandas as pd

EXCEL_PATH = "data/Synch_Data.xlsx"                
SHEET = 2                                        

df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET)   

VIDEO_PATH = "/assets/data_video/Dyad_Video.mp4"

VIDEO = VIDEO_PATH                  