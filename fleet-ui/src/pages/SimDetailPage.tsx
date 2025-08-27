import { useEffect, useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  fetchUsage,
  fetchAnomalies,
  fetchWhatIfTop3,
  fetchWhatIf,
} from "../api";
import type { UsagePoint, Anomaly, WhatIfTop3 } from "../types";
import {
  ResponsiveContainer,
  CartesianGrid,
  Tooltip,
  XAxis,
  YAxis,
  Area,
  Line,
  ComposedChart,
} from "recharts";

// Backend id’lerini kendi tablolarınla eşleştir
const PLAN_UPGRADE_ID = "iot_plus_2gb";
const ADDON_200MB_ID = "200mb";

const Pill = ({ children }: { children: React.ReactNode }) => (
  <div className="text-sm rounded px-2 py-1 bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300">
    {children}
  </div>
);

export default function SimDetailPage() {
  const { simId = "" } = useParams();

  // data
  const [usage, setUsage] = useState<UsagePoint[]>([]);
  const [anoms, setAnoms] = useState<Anomaly[]>([]);
  const [top3, setTop3] = useState<WhatIfTop3 | null>(null);
  const [wfCur, setWfCur] = useState<any>(null);
  const [wfUp, setWfUp] = useState<any>(null);
  const [wfAdd, setWfAdd] = useState<any>(null);

  // hatalar (bölüm bazlı)
  const [errUsage, setErrUsage] = useState("");
  const [errAnom, setErrAnom] = useState("");
  const [errTop3, setErrTop3] = useState("");
  const [errWf, setErrWf] = useState("");

  useEffect(() => {
    if (!simId) return;

    // 1) Kullanım
    (async () => {
      try {
        setErrUsage("");
        const u = await fetchUsage(simId, 30, "day");
        setUsage(Array.isArray(u) ? u : []);
        // Debug: konsola bakıp gelen veriyi gör
        console.log("usage", u);
      } catch (e: any) {
        setErrUsage(e?.message || "Kullanım verisi alınamadı");
      }
    })();

    // 2) Anomali
    (async () => {
      try {
        setErrAnom("");
        const a = await fetchAnomalies(simId);
        setAnoms(Array.isArray(a) ? a : []);
      } catch (e: any) {
        setErrAnom(e?.message || "Anomali verisi alınamadı");
      }
    })();

    // 3) Top-3 what-if
    (async () => {
      try {
        setErrTop3("");
        const w = await fetchWhatIfTop3(simId);
        setTop3(w || null);
      } catch (e: any) {
        setErrTop3(e?.message || "What-If Top-3 alınamadı");
      }
    })();

    // 4) Sabit 3 senaryo
    (async () => {
      try {
        setErrWf("");
        const cur = await fetchWhatIf(simId, {});
        const up = await fetchWhatIf(simId, { plan_id: PLAN_UPGRADE_ID });
        const add = await fetchWhatIf(simId, { addons: [ADDON_200MB_ID] });
        setWfCur(cur);
        setWfUp(up);
        setWfAdd(add);
      } catch (e: any) {
        setErrWf(e?.message || "What-If senaryoları alınamadı");
      }
    })();
  }, [simId]);

  // Grafik veri hazırlığı
  const chartData = useMemo(() => {
    const rows =
      (usage ?? []).map((u) => ({
        ts: (u.ts || "").slice(0, 10),
        MB: Number(u.mb_used ?? 0),
        Roaming: Number(u.roaming_mb ?? 0),
      })) ?? [];
    return rows;
  }, [usage]);

  // Küçük dalgalanmada ekseni daralt
  const yDomain = useMemo(() => {
    if (!chartData.length) return ["auto", "auto"] as const;
    const vals = chartData.map((d) => d.MB);
    const min = Math.min(...vals);
    const max = Math.max(...vals);
    if (max - min < 5) {
      const pad = Math.max(0.5, (5 - (max - min)) / 2);
      return [min - pad, max + pad] as const;
    }
    return ["dataMin", "dataMax"] as const;
  }, [chartData]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">SIM {simId}</h2>
        <Link to="/" className="text-sm underline">
          ← Listeye dön
        </Link>
      </div>

      {/* KULLANIM GRAFİĞİ */}
      <section className="space-y-2">
        <div className="flex items-center gap-2">
          <h3 className="font-medium">30 Günlük Kullanım</h3>
          {errUsage && <Pill>{errUsage}</Pill>}
          {!errUsage && chartData.length === 0 && (
            <span className="text-sm opacity-60">(veri yok)</span>
          )}
        </div>
        <div className="h-72 w-full rounded-2xl border dark:border-gray-800 p-3">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="ts" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} domain={yDomain} />
              <Tooltip />
              <Area type="monotone" dataKey="MB" fillOpacity={0.25} />
              <Line type="monotone" dataKey="Roaming" dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* ANOMALİLER */}
      <section className="space-y-2">
        <div className="flex items-center gap-2">
          <h3 className="font-medium">Anomali Rozetleri</h3>
          {errAnom && <Pill>{errAnom}</Pill>}
        </div>
        <div className="flex flex-wrap gap-2">
          {!errAnom && anoms.length === 0 && (
            <span className="text-sm">Anomali yok</span>
          )}
          {anoms.map((a, i) => (
            <span
              key={i}
              title={`${a.ts}: ${a.reason}`}
              className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-white/10"
            >
              {a.type}
            </span>
          ))}
        </div>
      </section>

      {/* WHAT-IF TOP 3 */}
      <section className="space-y-2">
        <div className="flex items-center gap-2">
          <h3 className="font-medium">What-If Kartları (Top 3)</h3>
          {errTop3 && <Pill>{errTop3}</Pill>}
        </div>
        <div className="grid md:grid-cols-3 gap-3">
          {top3?.options?.map((opt, i) => (
            <div key={i} className="rounded-2xl border dark:border-gray-800 p-4">
              <div className="text-sm opacity-70">Seçenek</div>
              <div className="text-lg font-semibold">{opt.label}</div>
              <div className="mt-2 text-sm">
                Toplam: <strong>{opt.total.toFixed(2)}</strong>
              </div>
              <div
                className={`mt-1 text-sm ${
                  opt.saving > 0 ? "text-green-600" : "text-red-600"
                }`}
              >
                Tasarruf: {opt.saving.toFixed(2)}
              </div>
            </div>
          ))}
          {!errTop3 && !top3 && <div className="text-sm">Yükleniyor…</div>}
        </div>
      </section>

      {/* WHAT-IF SABİT 3 */}
      <section className="space-y-2">
        <div className="flex items-center gap-2">
          <h3 className="font-medium">What-If (Sabit 3 Senaryo)</h3>
          {errWf && <Pill>{errWf}</Pill>}
        </div>
        <div className="grid md:grid-cols-3 gap-3">
          {[
            { title: "Mevcut", data: wfCur },
            { title: "Planı Yükselt", data: wfUp },
            { title: "+200MB Ek Paket", data: wfAdd },
          ].map((x, i) => (
            <div key={i} className="rounded-2xl border dark:border-gray-800 p-4">
              <div className="text-sm opacity-70">{x.title}</div>
              {x.data ? (
                <>
                  <div className="mt-1 text-sm">
                    Toplam: <strong>{x.data.candidate_total.toFixed(2)}</strong>
                  </div>
                  <div
                    className={`mt-1 text-sm ${
                      x.data.saving > 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    Tasarruf: {x.data.saving.toFixed(2)}
                  </div>
                </>
              ) : (
                <div className="text-sm opacity-70">Hesaplanıyor…</div>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
