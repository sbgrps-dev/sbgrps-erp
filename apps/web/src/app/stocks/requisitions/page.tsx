"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Download, FileSpreadsheet } from "lucide-react";
import { AddProduct } from "@/components/stocks/add-product";
import { LinesTable } from "@/components/stocks/lines-table";
import { PreviewTable } from "@/components/stocks/preview-table";
import { StatusBadge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api, downloadUrl } from "@/lib/api";
import type { MonthSummary, Preview, Requisition, Workbook } from "@/lib/types";
import { cn, currentMonth, money, monthLabel, shiftMonth } from "@/lib/utils";

export default function RequisitionsPage() {
  return (
    <Suspense>
      <Requisitions />
    </Suspense>
  );
}

function Requisitions() {
  const router = useRouter();
  const params = useSearchParams();
  const month = params.get("month") ?? currentMonth();
  const siteParam = params.get("site");
  const setParams = (m: string, site?: number | null) =>
    router.replace(`/stocks/requisitions?month=${m}${site ? `&site=${site}` : ""}`);

  const summary = useQuery({
    queryKey: ["month", month],
    queryFn: () => api<MonthSummary>(`/months/${month}/requisitions`),
  });
  const sites = summary.data?.sites ?? [];
  const siteId = siteParam ? Number(siteParam) : sites[0]?.site_id;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-semibold">Stock requisitions</h1>
          <Button variant="outline" size="icon" onClick={() => setParams(shiftMonth(month, -1), siteId)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="w-36 text-center font-medium">{monthLabel(month)}</span>
          <Button variant="outline" size="icon" onClick={() => setParams(shiftMonth(month, 1), siteId)}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
        {summary.data && <MonthActions summary={summary.data} />}
      </div>

      {summary.error && <p className="text-sm text-destructive">{summary.error.message}</p>}

      <div className="flex flex-wrap gap-1 border-b">
        {sites.map((s) => (
          <button
            key={s.site_id}
            onClick={() => setParams(month, s.site_id)}
            className={cn(
              "-mb-px flex items-center gap-2 rounded-t-md border px-3 py-2 text-sm",
              s.site_id === siteId ? "border-b-background bg-background font-medium" : "border-transparent bg-muted/50 hover:bg-muted",
            )}
          >
            {s.site_name}
            {s.line_count > 0 && <span className="text-xs text-muted-foreground">{s.line_count}</span>}
            <StatusBadge status={s.line_count > 0 ? s.status : null} />
          </button>
        ))}
      </div>

      {siteId && <SiteRequisition key={`${month}-${siteId}`} month={month} siteId={siteId} />}
    </div>
  );
}

function SiteRequisition({ month, siteId }: { month: string; siteId: number }) {
  const qc = useQueryClient();
  const [reqId, setReqId] = useState<number | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [workbook, setWorkbook] = useState<Workbook | null>(null);

  // Opening a site tab gets (or creates) its draft for the month.
  const open = useMutation({
    mutationFn: () => api<Requisition>(`/months/${month}/sites/${siteId}/requisition`, { method: "PUT" }),
    onSuccess: (data) => {
      qc.setQueryData(["requisition", data.id], data);
      setReqId(data.id);
    },
  });
  const { mutate: openDraft } = open;
  useEffect(() => openDraft(), [openDraft]);

  const req = useQuery({
    queryKey: ["requisition", reqId],
    queryFn: () => api<Requisition>(`/requisitions/${reqId}`),
    enabled: reqId !== null,
  });
  const preview = useQuery({
    queryKey: ["preview", reqId, req.data?.lines],
    queryFn: () => api<Preview>(`/requisitions/${reqId}/preview`),
    enabled: showPreview && reqId !== null,
  });

  const action = useMutation({
    mutationFn: (kind: "save" | "reopen") => api<Requisition>(`/requisitions/${reqId}/${kind}`, { method: "POST" }),
    onSuccess: (data) => {
      qc.setQueryData(["requisition", data.id], data);
      qc.invalidateQueries({ queryKey: ["month"] });
    },
  });
  const generate = useMutation({
    mutationFn: () => api<Workbook>(`/requisitions/${reqId}/workbooks`, { method: "POST" }),
    onSuccess: (wb) => {
      setWorkbook(wb);
      setShowPreview(true);
    },
  });

  const r = req.data;
  if (open.error) return <p className="text-sm text-destructive">{open.error.message}</p>;
  if (!r) return <p className="text-sm text-muted-foreground">Loading…</p>;
  const error = action.error ?? generate.error;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle>{r.site_name}</CardTitle>
            <StatusBadge status={r.status} />
          </div>
          <div className="flex items-center gap-2">
            <span className="mr-2 text-sm">
              Total <b>₹{money(r.totals.total)}</b>
            </span>
            <Button variant="outline" onClick={() => generate.mutate()} disabled={r.lines.length === 0 || generate.isPending}>
              <FileSpreadsheet className="h-4 w-4" /> Generate Excel
            </Button>
            {r.status === "draft" && (
              <Button onClick={() => action.mutate("save")} disabled={r.lines.length === 0 || action.isPending}>
                Save
              </Button>
            )}
            {r.status === "saved" && (
              <Button variant="secondary" onClick={() => action.mutate("reopen")} disabled={action.isPending}>
                Reopen to edit
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && <p className="text-sm text-destructive">{error.message}</p>}
          {r.status === "draft" ? (
            <AddProduct requisition={r} />
          ) : (
            <p className="text-sm text-muted-foreground">
              {r.status === "saved" ? "Saved. Nothing has been sent." : "Sent."} Reopen to change lines.
            </p>
          )}
          <LinesTable requisition={r} />
        </CardContent>
      </Card>

      {showPreview && (
        <Card>
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>Review: {r.site_name}</CardTitle>
            <div className="flex gap-2">
              {workbook && (
                <a href={downloadUrl(`/workbooks/${workbook.id}/download`)}>
                  <Button variant="outline">
                    <Download className="h-4 w-4" /> {workbook.filename} (v{workbook.version})
                  </Button>
                </a>
              )}
              <Button variant="ghost" onClick={() => setShowPreview(false)}>
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent>{preview.data ? <PreviewTable preview={preview.data} /> : "Loading…"}</CardContent>
        </Card>
      )}
    </div>
  );
}

function MonthActions({ summary }: { summary: MonthSummary }) {
  const qc = useQueryClient();
  const [review, setReview] = useState(false);
  const [sentOn, setSentOn] = useState<string | null>(null);
  const withLines = summary.sites.filter((s) => s.line_count > 0);
  const savedCount = withLines.filter((s) => s.status === "saved").length;

  const preview = useQuery({
    queryKey: ["month-preview", summary.month, summary.totals.total],
    queryFn: () => api<Preview>(`/months/${summary.month}/preview`),
    enabled: review,
  });
  const generate = useMutation({
    mutationFn: () => api<Workbook>(`/months/${summary.month}/workbooks`, { method: "POST", json: {} }),
    onSuccess: (wb) => {
      window.location.href = downloadUrl(`/workbooks/${wb.id}/download`);
    },
  });
  const markSent = useMutation({
    mutationFn: (date: string) =>
      api<{ updated: number[]; skipped_not_saved: number[] }>(`/months/${summary.month}/mark-sent-manually`, {
        method: "POST",
        json: { sent_on: date },
      }),
    onSuccess: () => {
      setSentOn(null);
      qc.invalidateQueries({ queryKey: ["month"] });
      qc.invalidateQueries({ queryKey: ["requisition"] });
    },
  });

  return (
    <>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-muted-foreground">
          {withLines.length} site{withLines.length === 1 ? "" : "s"} · ₹{money(summary.totals.total)}
        </span>
        <Button variant="outline" onClick={() => setReview(!review)} disabled={withLines.length === 0}>
          Review month
        </Button>
        <Button onClick={() => generate.mutate()} disabled={withLines.length === 0 || generate.isPending}>
          <Download className="h-4 w-4" /> HQ workbook (all sites)
        </Button>
        {sentOn === null ? (
          <Button
            variant="secondary"
            disabled={savedCount === 0}
            title="Use when you emailed the workbook to HQ yourself"
            onClick={() => setSentOn(new Date().toISOString().slice(0, 10))}
          >
            Mark sent manually
          </Button>
        ) : (
          <span className="flex items-center gap-1">
            <Input type="date" className="w-40" value={sentOn} onChange={(e) => setSentOn(e.target.value)} />
            <Button size="sm" onClick={() => markSent.mutate(sentOn)} disabled={markSent.isPending}>
              Confirm ({savedCount} saved)
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setSentOn(null)}>
              Cancel
            </Button>
          </span>
        )}
        {(generate.error ?? markSent.error) && (
          <span className="text-sm text-destructive">{(generate.error ?? markSent.error)?.message}</span>
        )}
      </div>
      {review && (
        <Card className="w-full">
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>Review: {monthLabel(summary.month)}, all sites (the HQ file)</CardTitle>
            <Button variant="ghost" onClick={() => setReview(false)}>
              Close
            </Button>
          </CardHeader>
          <CardContent>{preview.data ? <PreviewTable preview={preview.data} /> : "Loading…"}</CardContent>
        </Card>
      )}
    </>
  );
}
