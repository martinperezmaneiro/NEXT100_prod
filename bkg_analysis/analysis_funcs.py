#!/usr/bin/env python

import numpy as np


def remove_spurious_tracks(tracks, spurious_energy):
    sel_spurious = (tracks.energy < spurious_energy)
    spurious_energies = tracks.loc[sel_spurious].groupby('event').energy.sum().reset_index().rename(columns={'energy':'spurious_ene'})
    spurious_energies['trackID'] = 0

    tracks = tracks.merge(spurious_energies, on = ['event', 'trackID'], how = 'outer')
    tracks['spurious_ene'] = tracks['spurious_ene'].fillna(0)

    tracks['energy'] = tracks['energy'] + tracks['spurious_ene']
    tracks = tracks.loc[~sel_spurious].drop('spurious_ene', axis = 1)
    tracks = tracks.drop('numb_of_tracks', axis = 1).merge(tracks.groupby('event').trackID.nunique().reset_index().rename(columns={'trackID':'numb_of_tracks'}), on = 'event')
    return tracks


def count_experiment(nexus_df, 
                     isa_df,
                     ene_min = 0.8, 
                     ene_range = (2.4, 2.5), 
                     rmax = 450, 
                     zmin = 20, 
                     zmax = 1160, 
                     ntrack = 1, 
                     ovl = 0, 
                     ene_roi = (2.456, 2.472), 
                     eblob2 = 0.57):
    nexus, reco, ener, ener_roi, fid, fid_roi, track, track_roi, ovl, ovl_roi, roi, topo, topo_roi, topo_roi_full = 0,0,0,0,0,0,0,0,0,0,0,0,0,0

    #NEXUS
    nexus += len(nexus_df.event_id.unique())
    nexus_tot_ene = nexus_df.groupby('event_id').sum().reset_index()[['event_id', 'energy']]

    #RECO
    reco += len(isa_df.event.unique())

    #ENE
    # To create the reconstructed energy spectra
    isa_tot_ene = isa_df.groupby('event').sum().reset_index()[['event', 'energy']]
    isa_df_ = isa_df.merge(isa_tot_ene.rename(columns = {'energy':'tot_ener'}), on = ['event'])
    isa_df_ene = isa_df_[isa_df_.tot_ener > ene_min]
    ener += len(isa_df_ene.event.unique())

    isa_df_ene_roi = isa_df_[(isa_df_.tot_ener > ene_range[0]) & (isa_df_.tot_ener < ene_range[1])]
    ener_roi += len(isa_df_ene_roi.event.unique())

    #FID
    isa_df_fid = isa_df_ene[(isa_df_ene.r_max < rmax) & (isa_df_ene.z_min > zmin) & (isa_df_ene.z_max < zmax)]
    fid += len(isa_df_fid.event.unique())

    isa_df_fid_roi = isa_df_ene_roi[(isa_df_ene_roi.r_max < rmax) & (isa_df_ene_roi.z_min > zmin) & (isa_df_ene_roi.z_max < zmax)]
    fid_roi += len(isa_df_fid_roi.event.unique())   
    
    #After the fiducialization, we take a look to the energy spectra and to the track multiplicity (mainly to justify the cuts)
    isa_tot_ene_fid = isa_df_fid.groupby('event').sum().reset_index()[['event', 'energy']]
    isa_numtracks = isa_df_fid[['event', 'numb_of_tracks']].drop_duplicates().numb_of_tracks

    #TRACK
    isa_df_track = isa_df_fid[isa_df_fid.numb_of_tracks == ntrack]
    track += len(isa_df_track)

    isa_df_track_roi = isa_df_fid_roi[isa_df_fid_roi.numb_of_tracks == ntrack]
    track_roi += len(isa_df_track_roi)

    #OVL
    isa_df_ovl = isa_df_track[isa_df_track.ovlp_blob_energy == ovl]
    ovl += len(isa_df_ovl)

    isa_df_ovl_roi = isa_df_track_roi[isa_df_track_roi.ovlp_blob_energy == ovl]
    ovl_roi += len(isa_df_ovl_roi)

    # After track and ovl cuts, we pick the energy distribution of the second blob
    isa_eblob2 = isa_df_ovl[['event', 'eblob2']]

    #ROI
    isa_df_roi = isa_df_ovl[(isa_df_ovl.tot_ener > ene_roi[0]) & (isa_df_ovl.tot_ener < ene_roi[1])]
    roi += len(isa_df_roi)

    #TOPO
    isa_df_topo = isa_df_ovl[isa_df_ovl.eblob2 > eblob2]
    topo += len(isa_df_topo)

    isa_df_topo_roi = isa_df_ovl_roi[isa_df_ovl_roi.eblob2 > eblob2]
    topo_roi += len(isa_df_topo_roi)


    isa_df_topo_full = isa_df_roi[isa_df_roi.eblob2 > eblob2]
    topo_roi_full += len(isa_df_topo_full)

    counts = np.array([nexus, reco, ener, ener_roi, fid, fid_roi, track, track_roi, ovl, ovl_roi, roi, topo, topo_roi, topo_roi_full])
    return counts, nexus_tot_ene, isa_tot_ene, isa_tot_ene_fid, isa_numtracks, isa_eblob2