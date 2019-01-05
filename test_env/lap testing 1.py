
# coding: utf-8

# In[270]:


import numpy as np
import pandas as pd
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.models import HoverTool, CrosshairTool, ColumnDataSource


# In[249]:


theta = np.linspace(0, 2*np.pi, 16)
x1 = []
y1 = []
x1, y1 = 1 * np.cos(theta), 1 * np.sin(theta)


# In[250]:


print x1
print y1


# In[251]:


# Second lap
x2, y2 = 1.2 * np.cos(theta), 1.01 * np.sin(theta)


# In[252]:


print x2
print y2


# In[253]:


# Third lap
x3, y3 = 1.1 * np.cos(theta), 1.03 * np.sin(theta)


# In[254]:


print x3
print y3


# In[255]:


x = x1.tolist()[1:] + x2.tolist()[1:] + x3.tolist()[1:]
y = y1.tolist()[1:] + y2.tolist()[1:] + y3.tolist()[1:]
x.insert(0,1.5)
y.insert(0,-1)
x.append(1)
y.append(1)
print x
print y


# In[256]:


times = np.linspace(0,x.__len__(), num=x.__len__()).tolist()
print times


# In[286]:


data = pd.read_csv('laps.csv')
data = data.dropna()
data = data.reset_index(drop=False)
x = data['Lat']
y = data['Long']
times = data['Time']


# In[363]:


output_notebook()


# In[364]:


p = figure()


# In[365]:


source = ColumnDataSource(data=dict(
    sx=x,
    sy=y,
    stimes=times,
))


# In[366]:


print source.data['sx'].__len__()
print source.data['stimes'].__len__()


# In[367]:


def centroidnp(arr):
    length = arr.shape[0]
    sum = np.sum(arr[:])
    return sum/length


# In[368]:


cx = centroidnp(np.asarray(x))
cy = centroidnp(np.asarray(y))
print cx
print cy


# In[369]:


cx = 40.8455
cy = -96.769


# In[370]:


wn = 0
crossings = []

def is_left(x1, y1, x2, y2, x3, y3):
    return ((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1))

for i in range(0, x.__len__()-1):
    if y[i] <= cy:           
        if (y[i+1]  > cy):    
            if (is_left( x[i], y[i], x[i+1], y[i+1], cx,cy) > 0):
                wn = wn + 1
                crossings.append((times[i], x[i], y[i]))

    else:                       
        if (y[i+1]  <= cy):     
            if (is_left( x[i], y[i], x[i+1], y[i+1], cx,cy) < 0):  
                wn = wn -1
                crossings.append((times[i], x[i], y[i]))
    
print wn
print crossings
laptimes = []
for i in range(0,crossings.__len__()-1):
    laptimes.append(crossings[i+1][0]-crossings[i][0])
print laptimes


# In[371]:


p.circle(x='sx',y='sy',source=source,fill_color="blue",fill_alpha=0.6, line_alpha=0.5, line_color="black")
p.line(x='sx',y='sy',source=source)
p.circle(cx,cy)
for i in range(0,crossings.__len__()):
    p.circle(crossings[i][1], crossings[i][2],fill_color="red", radius=0.00005)


# In[372]:


TOOLTIPS = [
    ("time", "@stimes"),
    ("(x,y)", "($x, $y)"),
]


# In[373]:


p.add_tools(HoverTool(tooltips=TOOLTIPS))


# In[374]:


show(p)


# In[375]:


final_laptimes = []
for i in range(0,laptimes.__len__()-1):
    final_laptimes.append(laptimes[i]/1000)
    
print final_laptimes

