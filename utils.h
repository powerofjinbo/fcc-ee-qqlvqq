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
# 定义函数。输入参数 J 是从 Python 传进来的4个喷注的四维动量集合。mZ=91.19 设定了Z玻色子的标准质量是91.19GeV，根本不用管W
    
    Vec_tlv out;                             # 准备空篮子，用来装最后挑出来的两个粒子（交差用）
    TLorentzVector Zbest, Wstar;             # 准备两个空座位，留给最后胜出的“最像 Z 的组合”和“剩下的那个虚 W”。
    double bestDeltaZ = 1e99;     # 初始化一个很大的误差值

    if(J.size() != 4) {               
        out.push_back(Zbest);                # 数一下进来的喷注是不是刚好 4 个。如果不是，直接把空座位塞进篮子退回去，结束运行
        out.push_back(Wstar);                
        return out;
    }

    // The 3 unique pairings: (a,b) vs (c,d)
    int pairs[3][4] = {
        {0,1,2,3},                            # 遍历各种组合，两两配对
        {0,2,1,3},
        {0,3,1,2}
    };

    for(int ip=0; ip<3; ++ip) {
        int a=pairs[ip][0], b=pairs[ip][1], c=pairs[ip][2], d=pairs[ip][3];       # 开启循环，依次尝试上面字典里的 3 种分法。提取当前分法的 4 个编号给 a, b, c, d。
        TLorentzVector p1 = J[a] + J[b];                                          # 物理融合！把喷注 a 和 b 的四维动量加起来变成 p1，把 c 和 d 加起来变成 p2
        TLorentzVector p2 = J[c] + J[d];                                          # 模拟它们是从同一个母粒子衰变出来的，加起来就能还原母粒子的质量和动量

        // Check if p1 is closer to Z mass
        double delta1 = std::fabs(p1.M() - mZ);
        if(delta1 < bestDeltaZ) {
            bestDeltaZ = delta1;
            Zbest = p1;                                                    # 非常简单，算一下p1质量与91.19的绝对值误差，叫做delta1
            Wstar = p2;                                                    # 如果这次的误差 delta1 比历史最低记录 bestDeltaZ 还要小，说明找到了目前为止最像Z的组合！
        }

        // Check if p2 is closer to Z mass
        double delta2 = std::fabs(p2.M() - mZ);
        if(delta2 < bestDeltaZ) {
            bestDeltaZ = delta2;                                        # 同样的逻辑，万一 p2 的质量比 p1 更接近 91.19 呢？算一下 delta2，如果它更小，就再次更新冠军宝座。
            Zbest = p2;
            Wstar = p1;
        }
    }

    out.push_back(Zbest);
    out.push_back(Wstar);                                               # 满载而归！～
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
        int a=pairs[ip][0], b=pairs[ip][1], c=pairs[ip][2], d=pairs[ip][3];        # 这是孪生打分函数，只是把误差的分数交差，只更新数字
        TLorentzVector p1 = J[a] + J[b];
        TLorentzVector p2 = J[c] + J[d];

        double delta1 = std::fabs(p1.M() - mZ);
        double delta2 = std::fabs(p2.M() - mZ);
        if(delta1 < bestDeltaZ) bestDeltaZ = delta1;
        if(delta2 < bestDeltaZ) bestDeltaZ = delta2;
    }
    return bestDeltaZ;
}

// Total 4-jet invariant mass            # 计算 4 喷注总质量， 如果喷注不到 4 个，返回错误代码
double totalJetMass(Vec_tlv J) {
    if(J.size() < 4) return -1.0;
    TLorentzVector sum = J[0] + J[1] + J[2] + J[3];            # 这 4 个喷注的总质量反映了Z玻色子和那个虚W玻色子的总能量
    return sum.M();
}

// Event thrust (simplified iterative)  # 这是一个非常有用的高能物理经典算法，用来区分事件是“像筷子一样笔直”还是“像烟花一样散开”
double computeThrust(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> rps) {
    if(rps.size() == 0) return 0.0;                # 传入所有粒子的集合 rps。没粒子就返回0
    TVector3 nhat(0, 0, 1);
    for(int iter = 0; iter < 20; ++iter) {
        TVector3 newAxis(0, 0, 0);
        for(auto &p : rps) {
            TVector3 pvec(p.momentum.x, p.momentum.y, p.momentum.z);      
            # 这是著名的迭代法寻找推力轴 (Thrust Axis)，它先随便猜一个方向（Z 轴 nhat），
            # 然后把所有粒子的动量往这个方向投影。迭代 20 次后，它能精准找到空间中粒子飞得最密集的一条“主轴线
            if(pvec.Dot(nhat) > 0) newAxis += pvec;
            else newAxis -= pvec;
        }
        if(newAxis.Mag() > 0) nhat = newAxis.Unit();
    }
    double num = 0, den = 0;
    for(auto &p : rps) {
        TVector3 pvec(p.momentum.x, p.momentum.y, p.momentum.z);        # 这是推力的标准数学定义
        num += std::fabs(pvec.Dot(nhat));
        den += pvec.Mag();
    }
    return den > 0 ? num / den : 0.0;
}
# 上面部分解释一下：如果背景噪声是 e^+e^- to qq，粒子都顺着这根轴往两边飞，这个值会接近1
# 而ZH信号因为产生了质量很大的粒子，衰变时粒子会往四面八方飞，比较球形，所以这个值通常会在0.7左右。你可以利用这个差异来做 Cut！



# 轻子与中微子的空间夹角
// Angle between lepton and missing energy directions            # 传入轻子 lep 和代表中微子的缺失能量 miss，缺任何一个就报错返回 -1.0
double angleLeptonMiss(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> lep,
                       ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> miss) {
    if(lep.size() == 0 || miss.size() == 0) return -1.0;
    TVector3 v1(lep[0].momentum.x, lep[0].momentum.y, lep[0].momentum.z);
    TVector3 v2(miss[0].momentum.x, miss[0].momentum.y, miss[0].momentum.z);
    return v1.Angle(v2);
}
# 轻子和中微子因为要守恒动量和自旋（因为他俩来自同一个W），它们之间的夹角通常具有特定的物理分布规律（尤其是当W玻色子有一个极化状态时），这个角度常常被作为区分信号和背景的重要特征
}
