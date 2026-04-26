namespace FCCAnalyses {

// ============================================================================
// Z-PRIORITY pairing for H->WW* analysis (lvqq channel)
//
// Physics motivation:
//   In e+e- -> ZH -> Z(qq) + H(WW* -> lv qq), the Z is on-shell (~91 GeV)
//   but one of the W's from H->WW* is OFF-SHELL (W*) with mass << 80 GeV.
//
//   Therefore, we should NOT constrain Whad to 80 GeV. Instead:
//   1. Find the jet pair closest to mZ = 91 GeV (this is the Z from ZH)
//   2. The remaining two jets are the W* (no mass constraint)
//
// Input:  Vec_tlv J with exactly 4 jet TLorentzVectors
// Output: Vec_tlv of size 2: [Zcand, Wstar]
// ============================================================================
Vec_tlv pairing_Zpriority_4jets(Vec_tlv J, float mZ=91.19) {

    Vec_tlv out;
    TLorentzVector Zbest, Wstar;
    double bestDeltaZ = 1e99;

    if(J.size() != 4) {
        out.push_back(Zbest);
        out.push_back(Wstar);
        return out;
    }

    // The 3 unique pairings: (a,b) vs (c,d)
    int pairs[3][4] = {
        {0,1,2,3},
        {0,2,1,3},
        {0,3,1,2}
    };

    for(int ip=0; ip<3; ++ip) {
        int a=pairs[ip][0], b=pairs[ip][1], c=pairs[ip][2], d=pairs[ip][3];
        TLorentzVector p1 = J[a] + J[b];
        TLorentzVector p2 = J[c] + J[d];

        // Check if p1 is closer to Z mass
        double delta1 = std::fabs(p1.M() - mZ);
        if(delta1 < bestDeltaZ) {
            bestDeltaZ = delta1;
            Zbest = p1;
            Wstar = p2;
        }

        // Check if p2 is closer to Z mass
        double delta2 = std::fabs(p2.M() - mZ);
        if(delta2 < bestDeltaZ) {
            bestDeltaZ = delta2;
            Zbest = p2;
            Wstar = p1;
        }
    }

    out.push_back(Zbest);
    out.push_back(Wstar);
    return out;
}

// Returns |mZ_candidate - 91.19| for the best Z pairing
double pairing_Zpriority_deltaZ(Vec_tlv J, float mZ=91.19) {

    if(J.size() != 4) return 1e99;

    double bestDeltaZ = 1e99;
    int pairs[3][4] = {
        {0,1,2,3},
        {0,2,1,3},
        {0,3,1,2}
    };

    for(int ip=0; ip<3; ++ip) {
        int a=pairs[ip][0], b=pairs[ip][1], c=pairs[ip][2], d=pairs[ip][3];
        TLorentzVector p1 = J[a] + J[b];
        TLorentzVector p2 = J[c] + J[d];

        double delta1 = std::fabs(p1.M() - mZ);
        double delta2 = std::fabs(p2.M() - mZ);
        if(delta1 < bestDeltaZ) bestDeltaZ = delta1;
        if(delta2 < bestDeltaZ) bestDeltaZ = delta2;
    }
    return bestDeltaZ;
}

// Total 4-jet invariant mass
double totalJetMass(Vec_tlv J) {
    if(J.size() < 4) return -1.0;
    TLorentzVector sum = J[0] + J[1] + J[2] + J[3];
    return sum.M();
}

// Event thrust (simplified iterative)
double computeThrust(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> rps) {
    if(rps.size() == 0) return 0.0;
    TVector3 nhat(0, 0, 1);
    for(int iter = 0; iter < 20; ++iter) {
        TVector3 newAxis(0, 0, 0);
        for(auto &p : rps) {
            TVector3 pvec(p.momentum.x, p.momentum.y, p.momentum.z);
            if(pvec.Dot(nhat) > 0) newAxis += pvec;
            else newAxis -= pvec;
        }
        if(newAxis.Mag() > 0) nhat = newAxis.Unit();
    }
    double num = 0, den = 0;
    for(auto &p : rps) {
        TVector3 pvec(p.momentum.x, p.momentum.y, p.momentum.z);
        num += std::fabs(pvec.Dot(nhat));
        den += pvec.Mag();
    }
    return den > 0 ? num / den : 0.0;
}

// Angle between lepton and missing energy directions
double angleLeptonMiss(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> lep,
                       ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> miss) {
    if(lep.size() == 0 || miss.size() == 0) return -1.0;
    TVector3 v1(lep[0].momentum.x, lep[0].momentum.y, lep[0].momentum.z);
    TVector3 v2(miss[0].momentum.x, miss[0].momentum.y, miss[0].momentum.z);
    return v1.Angle(v2);
}

}
