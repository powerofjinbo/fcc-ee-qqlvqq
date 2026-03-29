#ifndef FCCPhysicsFunctionsGen_H
#define FCCPhysicsFunctionsGen_H

namespace FCCAnalyses {



// make Lorentz vectors for a given MC particle collection
Vec_tlv makeLorentzVectors(Vec_mc in) {
    Vec_tlv result;
    for(auto & p: in) {
        TLorentzVector tlv;
        tlv.SetXYZM(p.momentum.x, p.momentum.y, p.momentum.z, p.mass);
        result.push_back(tlv);
    }
    return result;
}

Vec_mc getRP2MC(Vec_rp in, ROOT::VecOps::RVec<int> recind, ROOT::VecOps::RVec<int> mcind, ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> reco, ROOT::VecOps::RVec<edm4hep::MCParticleData> mc) {
    Vec_mc result;
    for (auto & p: in) {
        int track_index = p.tracks_begin;
        int mc_index = ReconstructedParticle2MC::getTrack2MC_index(track_index, recind, mcind, reco);
        if(mc_index >= 0 && mc_index < mc.size() ) {
            result.push_back(mc.at(mc_index));
        }
        else {
            cout << "MC track not found!" << endl;
        }
    }
    return result;
}

}


#endif