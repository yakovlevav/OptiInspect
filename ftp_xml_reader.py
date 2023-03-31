# %%
import pandas as pd
from tqdm import tqdm_notebook
import os, io
from os.path import join, abspath
from glob import glob
from lxml import etree
from pandas_profiling import ProfileReport

# %%
root_path = join(r"\\", "balpdaoi01", "AOIData", "VelaPins")
xmlpath = join(root_path, "XML")
topview_img_path = join(root_path, "Component")
xslt_path = abspath("csv_vela.xslt")

# %%
files = glob(join(xmlpath, "*.xml"))
sorted_refine = sorted(files, reverse=False)

# %%
def add_pictures_v2(df,xmlfilepath):
    def hlink(a):
        link = '<a href="{a}" target="_blank"><img src="{a}" height="100"></a>'.format(a = a)
        # if os.path.exists(a):
        #     link = '<a href="{a}" target="_blank"><img src="{a}" height="100"></a>'.format(a = a)
        # else:
        #     link = "NaN"
        return(link)
    ser = topview_img_path+os.sep+df["Barcode"]+"."+df["LotCode"]+"."+df["RecipeName"]+os.sep+df["BoardName"]+"_"+df["ComponentName"]+".jpg"
    df["Img"] = ser
    df["Img_hlink"] = ser.map(hlink)

    picpath = os.path.splitext(xmlfilepath)[0].rsplit(".",1)[0]
    def dfadd(name, df):
        a = picpath+os.sep+df["BoardName"]+"_"+df["ComponentName"]+"_"+name+".png"
        df[name] = a
        df[name+"_hlink"] = a.map(hlink)
        return(df)

    listofnames = [
                    # "1_Illumination1", 
                    "Oblique0_0", 
                    "Oblique90_0", 
                    "Oblique180_0", 
                    "Oblique270_0"
                    ]
    for i in listofnames:
        df = dfadd(i,df)
    return(df)

def xmlparser(path):
    xml_input = etree.parse(path)
    xslt_root = etree.parse(xslt_path)
    transform = etree.XSLT(xslt_root)
    rawdata = io.StringIO(str(transform(xml_input)))
    df = pd.read_csv(rawdata, sep=";", converters = {"Barcode" : str, "LotCode":str}, parse_dates = ["StartTime"])
    df = add_pictures_v2(df, path)
    return(df)

# %%
xmlparser(sorted_refine[0])

# %%
data = []
for i in tqdm_notebook(sorted_refine):
    data.append(xmlparser(i))
    
df = pd.concat(data)
df = df.query("Type == 'BodyInspection'")

# %%
profile = ProfileReport(df, minimal=True,
        title="Pandas Profiling Report",
    )

profile.to_file("Darwin.html")

# %%
df.to_csv("VelaPins.csv", sep=";")



# %%
