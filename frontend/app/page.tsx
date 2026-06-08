"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/utils/supabase";

interface JobMatch {
  id: string;
  match_score: number;
  status: string;
  job_id: {
    title: string;
    company: string;
    location: string;
    url: string;
    is_remote: boolean;
  };
}

export default function Dashboard() {
  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchMatches() {
      const { data, error } = await supabase
        .from("job_matches")
        .select(`
          id,
          match_score,
          status,
          job_id (
            title,
            company,
            location,
            url,
            is_remote
          )
        `)
        .order("match_score", { ascending: false });

      if (error) {
        console.error("Error fetching dashboard payload:", JSON.stringify(error));
      } else {
        setMatches(data as unknown as JobMatch[]);
      }
      setLoading(false);
    }

    fetchMatches();
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600 bg-green-50 border-green-200";
    if (score >= 80) return "text-amber-600 bg-amber-50 border-amber-200";
    return "text-gray-600 bg-gray-50 border-gray-200";
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <p className="text-lg font-medium text-gray-500 animate-pulse">Syncing application pipeline state...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8 text-gray-900">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex items-center justify-between border-b border-gray-200 pb-5">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">CareerAutomation-OS</h1>
            <p className="mt-2 text-sm text-gray-500">Real-time aggregate semantic insights and auto-apply staging.</p>
          </div>
          <div className="bg-white px-4 py-2 rounded-lg border border-gray-200 shadow-sm">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Total Evaluated</span>
            <p className="text-2xl font-bold text-indigo-600">{matches.length}</p>
          </div>
        </header>

        {matches.length === 0 ? (
          <div className="rounded-xl border border-dashed border-gray-300 p-12 text-center bg-white">
            <p className="text-gray-500 font-medium">No processed jobs identified. Run your backend pipelines to see metrics.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {matches.map((match) => (
              <div
                key={match.id}
                className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:shadow-md"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <h2 className="text-lg font-bold text-gray-900">{match.job_id?.title}</h2>
                    {match.job_id?.is_remote && (
                      <span className="rounded-md bg-indigo-50 px-2 py-0.5 text-xs font-semibold text-indigo-700 border border-indigo-100">
                        Remote
                      </span>
                    )}
                  </div>
                  <p className="text-sm font-medium text-gray-600">
                    {match.job_id?.company} • <span className="text-gray-400">{match.job_id?.location || "Global"}</span>
                  </p>
                  <div className="pt-2">
                    <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize border bg-gray-100 text-gray-700">
                      Pipeline State: {match.status}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className={`flex flex-col items-center justify-center h-16 w-16 rounded-xl border font-bold ${getScoreColor(match.match_score)}`}>
                    <span className="text-xl">{Math.round(match.match_score)}</span>
                    <span className="text-[10px] uppercase opacity-75 tracking-wider">Match</span>
                  </div>
                  <a
                    href={match.job_id?.url}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm transition-colors hover:bg-gray-50"
                  >
                    View Original
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
