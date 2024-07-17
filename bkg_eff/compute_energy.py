#!/usr/bin/env python

from glob import glob
import tables as tb
import pandas as pd
import numpy as np
import invisible_cities.io.dst_io as dio

path = '/mnt/lustre/scratch/nlsas//home/usc/ie/mpm/NEXT100/data/full_prod/214Bi/prod/*/nexus/*' 
fileout = '/mnt/lustre/scratch/nlsas//home/usc/ie/mpm/NEXT100/data/full_prod/214Bi/prod/'
clean_spectra = True

key = lambda x: (x.split('/')[-3], int(x.split('_')[-2]))

files = sorted(glob(path), key = key)

def create_clean_spectra(hits, part):
    ener = pd.DataFrame({'event_id': pd.Series(dtype='int'),
                        'energy': pd.Series(dtype='float')})
    for ev_id, df in part.groupby('event_id'):
        #we want to clean the beta electron and all their products from the hits, so we need per event the particle ids
        beta = df[(df.mother_id == 1) & (df.particle_name == 'e-')].particle_id.unique()
        if len(beta) != 1:
            print('Event {}'.format(ev_id), 'had not a beta decay, probably emmited an alpha')
        sons = df[np.isin(df.mother_id, beta)]
        sons_id = np.append(beta, sons.particle_id.values)
        control_len = 0
        while len(sons_id) != control_len:
            control_len = len(sons_id)
            sons = df[np.isin(df.mother_id, sons_id)]
            sons_id = np.append(beta, sons.particle_id.values)
        
        ev_hits = hits[(hits.event_id == ev_id) & ~np.isin(hits.particle_id, sons_id)]
        ener = ener.append(pd.DataFrame([[ev_id, ev_hits.energy.sum()]], columns = ['event_id', 'energy'])).reset_index()[['event_id', 'energy']]
    return ener


for p in files:
    with tb.open_file(p, 'r') as h5in:
        hits = dio.load_dst(p, 'MC', 'hits')
        if clean_spectra:
            part = dio.load_dst(p, 'MC', 'particles')
            ener = create_clean_spectra(hits, part)
            outname = '/events_energy_clean.h5'
        else:
            ener = hits.groupby('event_id').sum().reset_index()[['event_id', 'energy']]
            outname = '/events_energy.h5'
        with tb.open_file(fileout + p.split('/')[-3] + outname, 'a') as h5out:
            dio.df_writer(h5out, ener, 'MC', 'EventEnergy', columns_to_index=['event_id'])
