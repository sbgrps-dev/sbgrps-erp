import { Table, Td, Th } from "@/components/ui/table";
import type { Preview } from "@/lib/types";
import { money, qty } from "@/lib/utils";

/** Mirrors sheet 1 (`Product Details`) of the generated workbook. */
export function PreviewTable({ preview }: { preview: Preview }) {
  if (preview.sites.length === 0) {
    return <p className="text-sm text-muted-foreground">No lines yet.</p>;
  }
  return (
    <div className="space-y-3">
      <div className="text-center text-sm font-bold">{preview.title}</div>
      <Table className="border">
        <thead className="bg-blue-50">
          <tr>
            {["SNO", "Site", "Vendor", "Material", "Qty", "Unit", "Per cost", "Taxable", "GST", "GST amt", "Total"].map(
              (h) => (
                <Th key={h} className="border">
                  {h}
                </Th>
              ),
            )}
          </tr>
        </thead>
        <tbody>
          {preview.sites.map((site) => {
            const siteRows = site.vendors.reduce((n, v) => n + v.lines.length, 0);
            return [
              ...site.vendors.flatMap((vendor, vi) =>
                vendor.lines.map((line, li) => (
                  <tr key={`${site.site_id}-${vendor.vendor_id}-${line.sno}`}>
                    <Td className="border text-center">{line.sno}</Td>
                    {vi === 0 && li === 0 && (
                      <Td rowSpan={siteRows} className="border text-center font-medium">
                        {site.site_name}
                      </Td>
                    )}
                    {li === 0 && (
                      <Td rowSpan={vendor.lines.length} className="border text-center">
                        {vendor.vendor_name}
                      </Td>
                    )}
                    <Td className="border">{line.product_name}</Td>
                    <Td className="border text-center">{qty(line.qty)}</Td>
                    <Td className="border text-center">{line.unit}</Td>
                    <Td className="border text-right">{money(line.price)}</Td>
                    <Td className="border text-right">{money(line.taxable)}</Td>
                    <Td className="border text-center">{Number(line.gst_rate)}%</Td>
                    <Td className="border text-right">{money(line.gst)}</Td>
                    <Td className="border text-right">{money(line.total)}</Td>
                  </tr>
                )),
              ),
              <tr key={`${site.site_id}-total`} className="bg-muted font-semibold">
                <Td colSpan={7} className="border text-right">
                  {site.site_name} TOTAL
                </Td>
                <Td className="border text-right">{money(site.totals.taxable)}</Td>
                <Td className="border" />
                <Td className="border text-right">{money(site.totals.gst)}</Td>
                <Td className="border text-right">{money(site.totals.total)}</Td>
              </tr>,
            ];
          })}
          <tr className="bg-yellow-50 font-bold">
            <Td colSpan={7} className="border text-right">
              GRAND TOTAL
            </Td>
            <Td className="border text-right">{money(preview.totals.taxable)}</Td>
            <Td className="border" />
            <Td className="border text-right">{money(preview.totals.gst)}</Td>
            <Td className="border text-right">{money(preview.totals.total)}</Td>
          </tr>
        </tbody>
      </Table>
      <p className="text-xs text-muted-foreground">
        Sheet 2 lists {preview.vendors.length} vendor{preview.vendors.length === 1 ? "" : "s"}:{" "}
        {preview.vendors.map((v) => v.name).join(", ")}.
      </p>
    </div>
  );
}
