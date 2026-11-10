import { cn } from "@/lib/utils";

const tones: Record<string, string> = {
  draft: "bg-amber-100 text-amber-900",
  saved: "bg-blue-100 text-blue-900",
  sent_to_hq: "bg-green-100 text-green-900",
  sent_manually: "bg-green-100 text-green-900",
  closed: "bg-gray-200 text-gray-800",
};

const labels: Record<string, string> = {
  draft: "Draft",
  saved: "Saved",
  sent_to_hq: "Sent to HQ",
  sent_manually: "Sent manually",
  closed: "Closed",
};

export function StatusBadge({ status, className }: { status: string | null; className?: string }) {
  if (!status) return null;
  return (
    <span className={cn("rounded px-1.5 py-0.5 text-[11px] font-medium", tones[status], className)}>
      {labels[status] ?? status}
    </span>
  );
}
