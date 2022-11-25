import datetime 
from metpy.units import units
import numpy as np
import pandas as pd
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import SkewT, Hodograph
from metpy.units import units
from metpy.interpolate import interpolate_1d
import matplotlib
from skewt import Skew_T
import matplotlib.pyplot as plt
import matplotlib.transforms as tsf
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from upperair_bufr import SoundingDecoder
from down import Down
# Import Data
# Import Wyoming Data
df = pd.read_csv('45004_2013052200.csv')
df[df == -9999] = np.nan
df = df.dropna(inplace=False)
df.info()
fm = "WyomingArchive"
pres, temp, dwpt, wdir, wspd, alt = df['pressure'].values, df['temperature'].values, df['dewpoint'].values, df['direction'].values, df['speed'].values, df['height'].values
# Import WIS Data
st="45004
def get_pressure_level_index(p, plevel, reverse=False):
    if reverse:
        idx = 0
    else:
        idx = -1
    return np.where(p.magnitude>=plevel)[0][idx]

def get_freezing_level_index(t, freezing, reverse=False):
    if reverse:
        idx = 0
    else:
        idx = -1
    return np.where(t.magnitude>=0)[0][idx]
    
def cal_tt(t850, td850, t500):
    return t850 + td850 - 2 * t500

def execute_sweat(tt, td8, u8, v8, u5, v5):
    s8 = np.sqrt(u8 * u8 + v8 * v8)
    s5 = np.sqrt(u5 * u5 + v5 * v5)
    s = s8 * s5
    z_mask = s == 0
    nz_mask = s != 0
    sdir = np.ndarray(tt.shape, np.float32)
    sdir[z_mask] = 0
    sdir[nz_mask] = (u5[nz_mask] * v8[nz_mask] - v5[nz_mask] * u8[nz_mask]) / s[nz_mask]
    tt49 = np.ndarray(tt.shape, np.float32)
    tt49_mask = tt >= 49
    tt49[tt < 49] = 0
    tt49[tt49_mask] = tt[tt49_mask] - 49.0
    result = 12 * td8
    result += 20 * tt49
    result += 2 * 1.944 * s8
    result += s5 * 1.944
    result += 125 * (sdir + 0.2)
    return result

def c_sweat(t850, td850, t500, u850, v850, u500, v500):
    tt = cal_tt(t850, td850, t500)
    return execute_sweat(tt, td850, u850, v850, u500, v500)

def showalter_index(t850, td850, t500):
    plcl, tlcl = mpcalc.lcl(850 * units('hPa'), t850, td850)
    p = np.array([plcl.magnitude, 500]) * units('hPa')
    out = mpcalc.moist_lapse(p, tlcl)
    return t500.magnitude - out[1].magnitude

def lifted_index(tsfc, tdsfc, psfc, t500):
    plcl, tlcl = mpcalc.lcl(psfc, tsfc, tdsfc)
    p = np.array([plcl.magnitude, 500]) * units('hPa')
    out = mpcalc.moist_lapse(p, tlcl)
    return t500.magnitude - out[1].magnitude

def delta_height(p1, p2):
    h1 = mpcalc.pressure_to_height_std(p1)
    h2 = mpcalc.pressure_to_height_std(p2)
    return h2 - h1
# Tackle Unit
p = pres * units.hPa
T = temp * units.degC
Td = dwpt * units.degC
wind_speed = wspd * units.knots
wind_dir = wdir * units.degrees
z = alt * units.meter
u, v = mpcalc.wind_components(wind_speed * 1.94, wind_dir)
index_p100 = get_pressure_level_index(p, 100)
index_p300 = get_pressure_level_index(p, 300)
# Plot
fig = plt.figure(figsize=(9, 9))
skew = SkewT(fig, rotation=45)
skew.plot(p, T, 'r')
skew.plot(p, Td, 'g')
skew.plot_barbs(p[:index_p100][::5], u[:index_p100][::5], v[:index_p100][::5])
skew.ax.set_ylim(1060, 100)
skew.ax.set_xlim(-50, 50)
skew.ax.set_ylabel('P',fontsize=8)
skew.ax.set_xlabel('T',fontsize=8)
lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
lcl_p, lcl_t = lcl_pressure, lcl_temperature
lfc_p, lfc_t = mpcalc.lfc(p, T, Td)
lcl_h = np.round(mpcalc.pressure_to_height_std(lcl_p), decimals=3).to(units.meter)
lfc_h = np.round(mpcalc.pressure_to_height_std(lfc_p), decimals=3).to(units.meter)
trans = tsf.blended_transform_factory(skew.ax.transAxes, skew.ax.transData)
T0 = get_freezing_level_index(T,0)
fl_h = np.round(mpcalc.pressure_to_height_std(p[T0]), decimals=3).to(units.meter)
skew.ax.text(0.01,lcl_p + 45 * units.hPa,transform=trans,ha='left',s="LCL: " + str('%.1f' % lcl_h.magnitude) + " meter", fontsize=10,color="#009688")
plt.axhline(y=lcl_pressure,xmin=0,xmax=0.17, c="#009688", ls="-", lw=1.5)
skew.ax.text(0.01, lfc_p - 10* units.hPa, s="LFC: " + str('%.1f' % lfc_h.magnitude) + " meter",fontsize=10,color="#A089C6",transform=trans)
plt.axhline(y=lfc_p,xmin=0,xmax=0.17, c="#A089C6", ls="-", lw=1.5)
skew.ax.text(0.01, p[T0] - 5 * units.hPa, "Freezing Level", fontsize=10,color="#3f51b5",transform=trans)
skew.ax.text(0.01, p[T0] + 25 * units.hPa, str('%.1f' % fl_h.magnitude) + " meter", fontsize=10,color="#3f51b5",transform=trans)
plt.axhline(y=p[T0],xmin=0,xmax=0.17, c="#3f51b5", ls="-", lw=1.5)
prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
skew.plot(p, prof, 'k', linewidth=2, color="#ffa500")
# Shade areas of CAPE and CIN
skew.shade_cin(p, T, prof)
skew.shade_cape(p, T, prof)
skew.ax.axvline(0,linestyle='--', linewidth=1)
# Text Add
plt.title('Skew-T\nStation:' + st, fontsize=16, loc='left')
plt.title("DataTime: "+ DataTime +"Z\nFormat: "+fm, loc='right', fontsize=14)
# Calculate
el_p, el_t = mpcalc.el(p, T, Td)
el_h = np.round(mpcalc.pressure_to_height_std(el_p), decimals=3).to(units.meter)
mucape, mucin = mpcalc.most_unstable_cape_cin(p, T, Td)
mlcape, mlcin = mpcalc.mixed_layer_cape_cin(p, T, Td)
if mucin.magnitude < 0:
    chi = -1 * mucin.magnitude
elif mucin.magnitude > 0:
    chi = mucin.magnitude
else:
    chi = 0.
u_shear01, v_shear01 = mpcalc.bulk_shear(p, u.to(units('m/s')), v.to(units('m/s')), depth = 1000 * units.meter)
shear01 = np.round((np.sqrt(u_shear01**2 + v_shear01**2)), 1)
pwat = mpcalc.precipitable_water(p[:index_p300], Td[:index_p300])
i8 = get_pressure_level_index(p, 850)
i7 = get_pressure_level_index(p, 700)
i5 = get_pressure_level_index(p, 500)
(t850,t700,t500),(td850,td700,_) = interpolate_1d(units.Quantity([850,700,500],'hPa'),p,T,Td)
theta850 = mpcalc.equivalent_potential_temperature(850 * units('hPa'), t850, Td[i5])
theta500 = mpcalc.equivalent_potential_temperature(500 * units('hPa'), t500, Td[i5])
thetadiff = theta850 - theta500
k = mpcalc.k_index(p,T,Td)
sw = c_sweat(np.array(t850.magnitude), np.array(td850.magnitude),
             np.array(t500.magnitude), np.array(u[i8].magnitude),
             np.array(v[i8].magnitude), np.array(u[i5].magnitude),
             np.array(v[i5].magnitude))
si = showalter_index(t850, td850, t500)
li = lifted_index(T[0], Td[0], p[0], t500)
srh_pos, srh_neg, srh_tot = mpcalc.storm_relative_helicity(z,u, v,  1000 * units('m'))
sbcape, sbcin = mpcalc.surface_based_cape_cin(p, T, Td)
shr6km = mpcalc.bulk_shear(p, u, v, height=z, depth=6000 * units('m'))
wshr6km = mpcalc.wind_speed(*shr6km)
sigtor = mpcalc.significant_tornado(sbcape, delta_height(p[0], lcl_p), srh_tot, wshr6km)[0]
scp = mucape/1000*(srh_tot/50)*(shear01/20)
namelist = ['LCL', 'LFC', 'EL', 'K', 'MLCAPE', 'SBCAPE', 'MUCAPE', 'MUCIN', 'Precip. Water', 'SWEAT', 'SI', 'LI', 'Shear 0-1km',
            'θse850-500', 'SRH', 'STP', 'SCP']
xcor = -50
ycor = -80
spacing = -9
for nm in namelist:
    ax.text(xcor, ycor, '{}: '.format(nm), fontsize=11)
    ycor += spacing
# Annotate values
varlist = [lcl_h, lfc_h, el_h, k, mlcape, sbcape, mucape, chi, pwat, sw, si, li, shear01, thetadiff,
           srh_tot, sigtor, scp]
xcor = 15
ycor = -80
for v in varlist:
    if hasattr(v, 'magnitude'):
        v = v.magnitude
    ax.text(xcor, ycor, str(np.round_(v, 2)), fontsize=11)
    ycor += spacing
# Annotate units
unitlist = ['m', 'm', 'm', '°C','J/kg', 'J/kg', 'J/kg',  'J/kg', 'mm', '', '°C',  '°C', 'm/s', '°C']
xcor = 38
ycor = -80
for u in unitlist:
    ax.text(xcor, ycor, ' {}'.format(u), fontsize=11)
    ycor += spacing
skew.plot_dry_adiabats(linewidth=1)
skew.plot_moist_adiabats(linewidth=1)
skew.plot_mixing_lines(linewidth=1)
plt.savefig('SKEWT.png')
