import os
import re
import subprocess

import netCDF4
import numpy as np

from pdb import set_trace

dl_base = r'/home/data/projects/comp_support/pdp/large_request_investigation'

hydro_base = r'/home/data/climate/hydrology/vic/gen1/'
bcsd_base = r'/home/data/climate/downscale/CMIP5/BCSD/'
bccaq_basil =r'/home/data/climate/downscale/CMIP5/BCCAQ/'

def basedata_dir(fp):
    if '5var' in fp:
        return hydro_base
    if 'BCSD' in fp:
        return bcsd_base
    if 'BCCAQ' in fp:
        return bccaq_base

class DataLogger:
    def __init__(self):
        self.data = []
        self.keys = ['result', 'file', 'can_dump', 'can_open', 'hyperslab', 'variable_test']
    
    def __str__(self):
        if len(self.data) < 1:
            raise LookupError('DataLogger Empty')
        r = [','.join(self.keys)]
        for row in self.data:
            data = [row.get(k, '') for k in self.keys]
            r.append(','.join(data))
        return '\n'.join(r)


    def add(self, r):
        self.data.append(r)
    
    def save(self, f):
        f.write(self.__str__())

pattern = re.compile('-(\d*)-(\d*)--(\d*)-(\d*)--(\d*)-(\d*)-.nc')

report = DataLogger()

for fp in os.listdir(os.path.join(dl_base, 'data')):
    if fp not in ['5var_day_CGCM3_A2_run1_19500101-20991231-bf.nc',
                  '5var_day_CGCM3_A2_run1_19500101-20991231-swe-0-40000--0-162--0-214-.nc',
                  '5var_day_CGCM3_A2_run1_19500101-20991231-swe-0-60--0-162--0-214-.nc',
                  '5var_day_CGCM3_A2_run1_19500101-20991231-swe-0-54786--75-78--100-103-.nc']:
        continue
    print 'Processing: {}'.format(fp)

    r = {'file': fp}

    # Find the file path of the original data
    # Get rid of request params. The '-' should only be used between dates and for request params
    if len(fp.split('-')) > 2:
        base_fp = '-'.join(fp.split('-')[:2])
    base_fp = os.path.splitext(base_fp)[0] + '.nc'
    base_fp = os.path.join(basedata_dir(base_fp), base_fp)

    # Try to open the downloaded file. Calling netCDF4.Dataset on a corrupted file aborts the entire script, so test with ncdump first
    try:
        x = subprocess.check_output(['ncdump', '-h', os.path.join(dl_base, 'data', fp)])
        r['can_dump'] = 'True'
        
    except Exception as e:
        r['can_dump'] = 'False'
        r['result'] = 'FAIL'
        report.add(r)
        continue

    nc = netCDF4.Dataset(os.path.join(dl_base, 'data', fp))
    r['can_open'] = 'True'
    base_nc = netCDF4.Dataset(base_fp)

    # Find what variable(s) were downloaded
    variables = [x for x in nc.variables.keys() if x not in ['lat', 'lon', 'time']]
    # Figure out the spatial/temporal extent
    m = pattern.search(fp)
    hyperslab = False
    if m:
        hyperslab = True
        t_min, t_max, y_min, y_max, x_min, x_max = map(int, pattern.search(fp).groups())
        r['hyperslab'] = '{}:{},{}:{},{}:{}'.format(t_min, t_max, y_min, y_max, x_min, x_max)

    else: 
        r['hyperslab'] = 'None'

    # Check all the variables
    for v in variables:
        print 'Checking variable: {}'.format(v)
        try:
            if 'variable_test' in r.keys():
                r['variable_test'] += '; '
            else:
                r['variable_test'] = ''

            # Extract appropriate hyperslab from base data
            if hyperslab:
                print 'Using hyperslab {}'.format(r['hyperslab'])
                base_data = base_nc.variables[v][t_min : t_max + 1, y_min : y_max + 1, x_min : x_max + 1]
            else:
                base_data = base_nc.variables[v][:,:,:]
            dl_data = nc.variables[v][:,:,:]
        
            # Cannot simply np.all(base_data == dl_data) because we hit memory issues on large arrays
            # Also, np.array_equal(base_data, dl_data) seems to return false all the time (not well tested however)
            print 'Array shapes. Downloaded: {}. Base: {}'.format(dl_data.shape, base_data.shape)
            assert dl_data.shape == base_data.shape
            for x, y in zip(base_data, dl_data):
                # Account for special case that if both masked arrays have all data masked (nodata), this is still 'equal'
                assert (np.all(x == y) or np.all(x == y) is np.ma.masked) 
            r['variable_test'] += '{}: OK'.format(v)

        except AssertionError:
            print 'FAILED data check'
            r['result'] = 'FAIL'
            r['variable_test'] += '{}: FAIL'.format(v)
            continue
    
    nc.close()
    base_nc.close()
    r['result'] = 'PASS'
    report.add(r)
#    gc.collect()

print report
with open('report.csv', 'w') as f:
    report.save(f)
