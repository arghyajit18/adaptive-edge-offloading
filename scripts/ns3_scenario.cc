#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/5g-nr-module.h"
#include <sstream>
using namespace ns3;
int main (int argc, char *argv[])
{
    CommandLine cmd;
    uint32_t tickMs = 100;
    cmd.AddValue ("tickMs", "Metric emission period (ms)", tickMs);
    cmd.Parse (argc, argv);
NodeContainer gNbNodes, ueNodes;
gNbNodes.Create (1);
ueNodes.Create (1);

MobilityHelper mobility;
mobility.SetMobilityModel ("ns3::RandomWaypointMobilityModel",
                           "Speed", StringValue ("ns3::UniformRandomVariable[Min=0.5|Max=5.0]"),
                           "Pause", StringValue ("ns3::ConstantRandomVariable[Constant=1.0]"));
mobility.Install (ueNodes);
mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
mobility.Install (gNbNodes);

NrHelper nrHelper;
nrHelper.SetSchedulerTypeId (TypeId::LookupByName ("ns3::NrMacSchedulerOfdmaPF"));
NetDeviceContainer gNbDevs = nrHelper.InstallGnbDevice (gNbNodes, {});
NetDeviceContainer ueDevs  = nrHelper.InstallUeDevice (ueNodes, {});

InternetStackHelper internet;
internet.Install (ueNodes);
internet.Install (gNbNodes);

auto emitMetrics = [&] () {
    Ptr<NrUePhy> uePhy = ueDevs.Get (0)->GetObject<NrUeNetDevice>()->GetPhy ();
    double sinr = uePhy->GetSinr ();
    double bw   = uePhy->GetChannelBandwidth ();
    double rtt  = 2.0;
    double loss = uePhy->GetDlPacketErrorRate ();

    std::ostringstream oss;
    oss << "{\"bandwidth_mbps\":" << bw/1e6
        << ",\"rtt_ms\":" << rtt
        << ",\"loss\":" << loss
        << ",\"sinr_db\":" << sinr
        << "}";
    std::cout << oss.str() << std::endl;
    Simulator::Schedule (MilliSeconds (tickMs), emitMetrics);
};
Simulator::Schedule (MilliSeconds (tickMs), emitMetrics);

Simulator::Stop (Seconds (30));
Simulator::Run ();
Simulator::Destroy ();
return 0;
}
