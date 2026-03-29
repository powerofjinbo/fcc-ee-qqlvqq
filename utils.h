

namespace FCCAnalyses {

bool is_ww_hadronic(Vec_mc mc, Vec_i ind) {
   int l1 = 0;
   int l2 = 0;
   //cout << "*********" << endl;
   for(size_t i = 0; i < mc.size(); ++i) {
        auto & p = mc[i];
        if(std::abs(p.PDG) == 24) {
            int ds = p.daughters_begin;
            int de = p.daughters_end;
            for(int k=ds; k<de; k++) {
                int pdg = abs(mc[ind[k]].PDG);
                if(pdg == 24) continue;
                //std::cout << "W " << pdg << endl;
                if(l1 == 0) l1 = pdg;
                else l2 = pdg;
            }
        }
   }
   if((l1 < 6 && l2 < 6)) {
       //std::cout << "HADRONIC-----------" << l1 << " " << l2 << endl;
       return true;
   }
   return false;
}

bool is_zz_hadronic(Vec_mc mc, Vec_i ind) {
   int l1 = 0;
   int l2 = 0;
   //cout << "*********" << endl;
   for(size_t i = 0; i < mc.size(); ++i) {
        auto & p = mc[i];
        if(std::abs(p.PDG) == 23) {
            int ds = p.daughters_begin;
            int de = p.daughters_end;
            for(int k=ds; k<de; k++) {
                int pdg = abs(mc[ind[k]].PDG);
                if(pdg == 24) continue;
                //std::cout << "W " << pdg << endl;
                if(l1 == 0) l1 = pdg;
                else l2 = pdg;
            }
        }
   }
   if((l1 < 6 && l2 < 6)) {
       //std::cout << "HADRONIC-----------" << l1 << " " << l2 << endl;
       return true;
   }
   return false;
}

Vec_tlv pairing_WW(Vec_tlv J, float target=80.385) {

    int nJets6=6;
    float d1W[6][6], dW1[6][6], d2W[6][6],dW2[6][6], d1Z[6][6],d2Z[6][6], d1H[6][6][6][6],d2H[6][6][6][6];

    for(int i=0;i<6;i++) {
        for(int j=0;j<6;j++) {
            d1W[i][j]=-1000.;
            d2W[i][j]=-1000.;
            d1Z[i][j]=-1000.;
            d2Z[i][j]=-1000.;
            dW1[i][j]=-1000.;
            dW2[i][j]=-1000.;
        }
    }

    for(int i=0;i<6;i++){
        for(int j=0;j<6;j++){
            for(int k=0;k<6;k++){
                for(int s=0;s<6;s++) {
                    d1H[i][j][k][s]=-1000.;
                    d2H[i][j][k][s]=-1000.;
                }
            }
        }
    }

    double DWmin_1=1000.,DWmin_2=1000.,chi2_1=10000000000., chi2_2=10000000000.,chi2M=10000000000.,chi2min=100000000.,chi2First=10000000.,chi2Second=100000000;float dmin=1000000.,DZmin=1000000.;

    int iW1=-1.,jW1=-1.,iW2=-1.,jW2=-1.,iZ=-1.,jZ=-1.;
    int iW1_Z=-1.,jW1_Z=-1.,iW2_Z=-1.,jW2_Z=-1.,iZ_Z=-1.,jZ_Z=-1.;
    int iW1_1=-1.,jW1_1=-1.,iW2_1=-1.,jW2_1=-1.,iZ_1=-1.,jZ_1=-1.;
    int iW1_2=-1.,jW1_2=-1.,iW2_2=-1.,jW2_2=-1.,iZ_2=-1.,jZ_2=-1.;
    int iW1_3=-1.,jW1_3=-1.,iW2_3=-1.,jW2_3=-1.,iZ_3=-1.,jZ_3=-1.;


    for(int i=0;i<nJets6;i++) {
        for(int j=i+1;j<nJets6;j++) {
            for(int k=i+1;k<nJets6;k++) {
                if(!(k==i)&&!(k==j)) {
                    for(int s=k+1;s<nJets6;s++) {
                        if(!(s==i)&&!(s==j)&&!(s==k)) {
                            for(int l=0;l<nJets6;l++) {
                                if(!(l==i)&&!(l==j)&&!(l==k)&&!(l==s)) {
                                    for(int m=l+1;m<nJets6;m++) {
                                        if(!(m==i)&&!(m==j)&&!(m==k)&&!(m==s)&&!(m==l)) {

                                            d1W[i][j]      =fabs( target -((J[i]+J[j]).M()));
                                            dW1[l][m]      =fabs( target -((J[l]+J[m]).M()));
                                            d1Z[k][s]      =fabs( 91.19  -((J[k]+J[s]).M()));
                                            d1H[i][j][l][m]=fabs(125.0   -((J[i]+J[j]+J[l]+J[m]).M()));
                                      
                                            chi2First=(d1W[i][j])*(d1W[i][j])+(d1Z[k][s])*(d1Z[k][s]); 
                                            chi2_1   =(d1W[i][j])*(d1W[i][j])+(d1Z[k][s])*(d1Z[k][s])+d1H[i][j][l][m]*d1H[i][j][l][m]; 

                                            if(d1Z[k][s]<DZmin) {
                                                DZmin=d1Z[k][s];
                                                iZ_Z=k;
                                                jZ_Z=s;
                                                if(d1W[i][j]<dW1[l][m]) { iW1_Z=i; jW1_Z=j; iW2_Z=l;jW2_Z=m;}
                                                else                    { iW1_Z=l; jW1_Z=m; iW2_Z=i;jW2_Z=j;}
                                            }
                                            if(chi2First<chi2min) {chi2min=chi2First;iW1_1=i;jW1_1=j; iZ_1=k; jZ_1=s;iW2_1=l;jW2_1=m;}
                                            if(chi2_1<chi2M)      {chi2M=chi2_1;     iW1_2=i;jW1_2=j; iZ_2=k; jZ_2=s;iW2_2=l;jW2_2=m;}
                                            if( DWmin_1<dmin)     {dmin= DWmin_1;    iW1_3=i;jW1_3=j; iZ_3=k; jZ_3=s;iW2_3=l;jW2_3=m;}

                                            d2W[k][s]      =fabs( target -((J[k]+J[s]).M()));
                                            dW2[l][m]      =fabs( target -((J[l]+J[m]).M()));
                                            d2Z[i][j]      =fabs( 91.19  -((J[i]+J[j]).M()));
                                            d2H[k][s][l][m]=fabs(125.0   -((J[k]+J[s]+J[l]+J[m]).M()));
                                      
                                          
                                            chi2Second=(d2W[k][s])*(d2W[k][s])+(d2Z[i][j])*(d2Z[i][j]); 
                                            chi2_2=(d2W[k][s])*(d2W[k][s])+(d2Z[i][j])*(d2Z[i][j])+(d2H[k][s][l][m]*d2H[k][s][l][m]); 

                                            if(d2Z[i][j]<DZmin) {
                                                DZmin=d2Z[i][j];
                                                iZ_Z=i;
                                                jZ_Z=j; 

                                                if(d2W[k][s]<dW2[l][m]) {iW1_Z=k; jW1_Z=s; iW2_Z=l; jW2_Z=m;}   
                                                else {iW1_Z=l; jW1_Z=m; iW2_Z=k; jW2_Z=s;}
                                            }

                                            if(chi2Second<chi2min) {chi2min=chi2Second;iW1_1=k;jW1_1=s;iZ_1=i; jZ_1=j;iW2_1=l;jW2_1=m;}
                                            if(chi2_2<chi2M)       {chi2M  =chi2_2;    iW1_2=k;jW1_2=s;iZ_2=i; jZ_2=j;iW2_2=l;jW2_2=m;}
                                            if( DWmin_2<dmin)      {dmin   =DWmin_2;   iW1_3=k;jW1_3=s; iZ_3=i;jZ_3=j;iW2_3=l;jW2_3=m;}
                                        }
                                    } // m
                                }
                            }// l
                        }
                    } // s
                }
            }// k
        } // j
    
    }// i

    TLorentzVector JHiggs,JW1,JW2,JZ;
    JW1=J[iW1_2]+J[jW1_2];
    JW2=J[iW2_2]+J[jW2_2];
    JZ=J[iZ_2]+J[jZ_2];
    JHiggs=JW1+JW2;

    Vec_tlv out;
    out.push_back(JW1);
    out.push_back(JW2);
    out.push_back(JZ);
    out.push_back(JHiggs);
    return out;

}

// ============================================================================
// 4-jet pairing for Z(qq) + W(qq) hypotheses (lvqq channel helper)
//
// Input:  Vec_tlv J with exactly 4 jet TLorentzVectors
// Output: Vec_tlv out of size 2: [Zcand, Whad]
//
// We enumerate the 3 unique disjoint pairings of 4 objects and, for each,
// the 2 possible Z/W assignments (total 6 combinations). We select the
// assignment that minimises a simple chi2:
//   chi2 = ((mZcand - mZ)/sigZ)^2 + ((mWcand - mW)/sigW)^2
//
// This is intentionally simple/robust for a baseline analysis.
// ============================================================================
Vec_tlv pairing_ZW_4jets(Vec_tlv J, float mZ=91.19, float mW=80.385, float sigZ=15., float sigW=15.) {

    Vec_tlv out;
    TLorentzVector Zbest, Wbest;
    double best = 1e99;

    if(J.size() != 4) {
        out.push_back(Zbest);
        out.push_back(Wbest);
        return out;
    }

    // The 3 unique pairings (a,b) and (c,d)
    int pairs[3][4] = {
        {0,1,2,3},
        {0,2,1,3},
        {0,3,1,2}
    };

    for(int ip=0; ip<3; ++ip) {
        int a=pairs[ip][0], b=pairs[ip][1], c=pairs[ip][2], d=pairs[ip][3];
        TLorentzVector p1 = J[a] + J[b];
        TLorentzVector p2 = J[c] + J[d];

        // assignment 1: p1=Z, p2=W
        double chi2_1 = std::pow((p1.M()-mZ)/sigZ, 2) + std::pow((p2.M()-mW)/sigW, 2);
        if(chi2_1 < best) {
            best = chi2_1;
            Zbest = p1;
            Wbest = p2;
        }

        // assignment 2: p1=W, p2=Z
        double chi2_2 = std::pow((p2.M()-mZ)/sigZ, 2) + std::pow((p1.M()-mW)/sigW, 2);
        if(chi2_2 < best) {
            best = chi2_2;
            Zbest = p2;
            Wbest = p1;
        }
    }

    out.push_back(Zbest);
    out.push_back(Wbest);
    return out;
}

double pairing_ZW_4jets_chi2(Vec_tlv J, float mZ=91.19, float mW=80.385, float sigZ=15., float sigW=15.) {

    if(J.size() != 4) return 1e99;

    double best = 1e99;
    int pairs[3][4] = {
        {0,1,2,3},
        {0,2,1,3},
        {0,3,1,2}
    };

    for(int ip=0; ip<3; ++ip) {
        int a=pairs[ip][0], b=pairs[ip][1], c=pairs[ip][2], d=pairs[ip][3];
        TLorentzVector p1 = J[a] + J[b];
        TLorentzVector p2 = J[c] + J[d];

        double chi2_1 = std::pow((p1.M()-mZ)/sigZ, 2) + std::pow((p2.M()-mW)/sigW, 2);
        double chi2_2 = std::pow((p2.M()-mZ)/sigZ, 2) + std::pow((p1.M()-mW)/sigW, 2);
        if(chi2_1 < best) best = chi2_1;
        if(chi2_2 < best) best = chi2_2;
    }
    return best;
}

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