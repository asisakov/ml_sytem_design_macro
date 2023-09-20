import json
from pprint import pp
import numpy as np
import math

from statsmodels.tsa.api import ExponentialSmoothing

with open('data/pcps.json', 'r') as myfile:
    data=myfile.read()

# parse file
pcps = json.loads(data)

values = pcps[0]['values']
all_vals = np.asarray(list(map(lambda v: float(v[1]), values)))

#train_start = -len(values)
train_start = 0
train_end = -12
#train_vals = all_vals[train_start:train_end]
train_vals = all_vals[:train_end]
#pp(all_vals)
#holt_winter = ExponentialSmoothing(train_vals, seasonal_periods=12, trend='add', seasonal='mul')


if False:
    min_dis = None
    min_p = None
    min_forecast
    for sp in range(2,48):
        for t in ['add', 'mul', None]:
            for s in ['add', 'mul', None]:
                holt_winter = ExponentialSmoothing(train_vals, seasonal_periods=sp, trend=t, seasonal=t)
                #holt_winter = ExponentialSmoothing(train_vals, seasonal=None, trend='mul')
                hw_fit = holt_winter.fit()
                forecast = hw_fit.predict(0, len(values) - 1)

                dis = math.sqrt(pow(sum(all_vals[-12:] - forecast[-12:]), 2))
                if min_dis is None or dis < min_dis:
                    min_dis = dis
                    min_p = (sp, t, s)
                    min_forecast = forecast
                #print(dis, sp, t, s)

#print(min_dis)
#print(min_p)
#exit(0)


#print(f'len train {len(train_vals)}, len vals: {len(values)}')
holt_winter = ExponentialSmoothing(train_vals, seasonal_periods=12, trend=None, seasonal='add')
hw_fit = holt_winter.fit()
forecast = hw_fit.predict(0, len(values) - 1)


pcps_forecast = [pcps[0]]
pcps_forecast[0]['values'] = []
for i in range(0, len(forecast)):
    #print(i, len(values), train_start)
    #print(i + len(values) + train_start)
    pcps_forecast[0]['values'].append([values[i][0], forecast[i]])

print(json.dumps(pcps_forecast))




