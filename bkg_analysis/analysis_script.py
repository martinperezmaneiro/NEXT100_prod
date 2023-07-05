#!/usr/bin/env python

# This script creates for an isotope a file per volume saving the info of the counting experiment, energy spectra (nexus, reco and reco
# after fiducialization), number of tracks and energy of the second blob for the main tracks
import os
os.system('source ../setup.sh')
import numpy as np
import pandas as pd
from glob import glob
from analysis_funcs import remove_spurious_tracks, count_experiment
import invisible_cities.io.dst_io as dio

isotopes = ['214Bi', '208Tl']
sort_files = lambda x: int(x.split('_')[-2])
basedir = '$LUSTRE/NEXT100/data/full_prod/{}/prod/volumes/*/'
outname = 'tracks_info.h5'

for isotope in isotopes:
    base_dir = os.path.expandvars(basedir.format(isotope))
    vol_paths = sorted(glob(base_dir))

    for vol_path in vol_paths:
        vol = vol_path.split('/')[-2]
        print(vol)
        isaura_files = sorted(glob(vol_path + 'prod/isaura/*'), key=sort_files)
        nexus_files = sorted(glob(vol_path + 'prod/nexus/*'), key=sort_files)

        total_counts = np.zeros(14, dtype = int)
        for isaura_file, nexus_file in zip(isaura_files, nexus_files):
            nexus_df = dio.load_dst(nexus_file, 'MC', 'hits')
            isa_df = remove_spurious_tracks(dio.load_dst(isaura_file, 'Tracking', 'Tracks'), 0.01)
            counts, nexus_tot_ene, isa_tot_ene, isa_tot_ene_fid, isa_numtracks, isa_eblob2 = count_experiment(nexus_df, isa_df)
            
            total_counts += counts
            
            outpath= '/'.join(isaura_file.split('/')[:-3]) + '/'
            nexus_tot_ene.to_hdf(outpath + outname, 'MCEner', append=True)
            isa_tot_ene.to_hdf(outpath + outname, 'RecoEner', append=True)
            isa_tot_ene_fid.to_hdf(outpath + outname, 'RecoEnerFid', append=True)
            isa_numtracks.to_hdf(outpath + outname, 'NumTracks', append=True)
            isa_eblob2.to_hdf(outpath + outname, 'EneBlob2', append=True)
            
        df_dct = {'vol': vol, 'nexus':total_counts[0], 'reco':total_counts[1], 'ener':total_counts[2], 
                    'ener_roi':total_counts[3], 'fid':total_counts[4], 'fid_roi':total_counts[5], 'track':total_counts[6], 
                    'track_roi':total_counts[7], 'ovl':total_counts[8], 'ovl_roi':total_counts[9], 'roi':total_counts[10], 
                    'topo':total_counts[11], 'topo_roi':total_counts[12], 'topo_roi_full':total_counts[13]}
        pd.DataFrame([df_dct]).to_hdf(outpath + outname, 'selection_rates', append = True, min_itemsize=20)