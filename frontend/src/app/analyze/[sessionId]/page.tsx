"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import {
  fetchOverview, fetchTemporal, fetchNLP, fetchNetwork, fetchEngagement, fetchRetention,
} from "@/lib/api";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { OverviewTab } from "@/components/dashboard/OverviewTab";
import { UsersTab } from "@/components/dashboard/UsersTab";
import { TemporalTab } from "@/components/dashboard/TemporalTab";
import { NLPTab } from "@/components/dashboard/NLPTab";
import { NetworkTab } from "@/components/dashboard/NetworkTab";
import { AdminTab } from "@/components/dashboard/AdminTab";
import { ExportTab } from "@/components/dashboard/ExportTab";

export default function DashboardPage() {
  const params = useParams<{ sessionId: string }>();
  const sid = params.sessionId;
  const [tab, setTab] = useState("overview");

  const overview = useQuery({ queryKey: ["overview", sid], queryFn: () => fetchOverview(sid) });
  const temporal = useQuery({ queryKey: ["temporal", sid], queryFn: () => fetchTemporal(sid), enabled: tab === "temporal" || tab === "overview" });
  const nlp = useQuery({ queryKey: ["nlp", sid], queryFn: () => fetchNLP(sid), enabled: tab === "nlp" });
  const network = useQuery({ queryKey: ["network", sid], queryFn: () => fetchNetwork(sid), enabled: tab === "network" });
  const engagement = useQuery({ queryKey: ["engagement", sid], queryFn: () => fetchEngagement(sid), enabled: tab === "engagement" });
  const retention = useQuery({ queryKey: ["retention", sid], queryFn: () => fetchRetention(sid), enabled: tab === "engagement" });

  return (
    <DashboardLayout tab={tab} onTabChange={setTab} groupName={overview.data?.metadata?.group_name}>
      {tab === "overview" && <OverviewTab overview={overview.data} temporal={temporal.data} loading={overview.isLoading} />}
      {tab === "users" && <UsersTab overview={overview.data} />}
      {tab === "temporal" && <TemporalTab temporal={temporal.data} />}
      {tab === "nlp" && <NLPTab nlp={nlp.data} />}
      {tab === "network" && <NetworkTab network={network.data} />}
      {tab === "engagement" && <AdminTab engagement={engagement.data} retention={retention.data} />}
      {tab === "export" && <ExportTab sessionId={sid} />}
    </DashboardLayout>
  );
}
