"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, Td, Th } from "@/components/ui/table";
import { api } from "@/lib/api";
import type { Price, Product } from "@/lib/types";
import { money } from "@/lib/utils";

export default function ProductsPage() {
  const [q, setQ] = useState("");
  const [open, setOpen] = useState<number | null>(null);
  const products = useQuery({
    queryKey: ["products", "list", q],
    queryFn: () => api<Product[]>(`/products?limit=500${q ? `&q=${encodeURIComponent(q)}` : ""}`),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Products &amp; prices</h1>
        <Input className="w-72" placeholder="Search name or alias" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <p className="text-sm text-muted-foreground">
        Add new products from a requisition (search → “New product”). Click a row to change prices, HSN or aliases.
      </p>
      <Table>
        <thead>
          <tr>
            <Th>Code</Th>
            <Th>Name</Th>
            <Th>Unit</Th>
            <Th>HSN</Th>
            <Th>GST</Th>
            <Th>Vendors · current price</Th>
          </tr>
        </thead>
        <tbody>
          {products.data?.map((p) => [
            <tr key={p.id} className="cursor-pointer hover:bg-muted/50" onClick={() => setOpen(open === p.id ? null : p.id)}>
              <Td className="font-mono text-xs">{p.code}</Td>
              <Td>
                {p.name}
                {p.aliases.length > 0 && <div className="text-xs text-muted-foreground">aka {p.aliases.join(", ")}</div>}
              </Td>
              <Td>{p.unit}</Td>
              <Td>{p.hsn ?? <span className="text-amber-700">missing</span>}</Td>
              <Td>{Number(p.gst_rate)}%</Td>
              <Td>
                {p.vendors.map((v) => (
                  <div key={v.vendor_id} className={v.is_preferred ? "font-medium" : "text-muted-foreground"}>
                    {v.vendor_name} · ₹{money(v.current_price)} {v.is_preferred && "★"}
                  </div>
                ))}
              </Td>
            </tr>,
            open === p.id && (
              <tr key={`${p.id}-edit`}>
                <Td colSpan={6} className="bg-muted/30">
                  <ProductEditor product={p} />
                </Td>
              </tr>
            ),
          ])}
        </tbody>
      </Table>
    </div>
  );
}

function ProductEditor({ product }: { product: Product }) {
  const qc = useQueryClient();
  const [vendorId, setVendorId] = useState(product.vendors[0]?.vendor_id ?? 0);
  const [price, setPrice] = useState("");
  const [reason, setReason] = useState("");
  const [hsn, setHsn] = useState(product.hsn ?? "");
  const [aliases, setAliases] = useState(product.aliases.join(", "));
  const history = useQuery({
    queryKey: ["prices", product.id],
    queryFn: () => api<Record<string, Price[]>>(`/products/${product.id}/prices`),
  });
  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["products"] });
    qc.invalidateQueries({ queryKey: ["prices", product.id] });
  };
  const newPrice = useMutation({
    mutationFn: () =>
      api<Product>(`/products/${product.id}/vendors/${vendorId}/prices`, { method: "POST", json: { price, reason } }),
    onSuccess: () => {
      setPrice("");
      setReason("");
      refresh();
    },
  });
  const update = useMutation({
    mutationFn: () =>
      api<Product>(`/products/${product.id}`, {
        method: "PATCH",
        json: { hsn: hsn || null, aliases: aliases.split(",").map((a) => a.trim()).filter(Boolean) },
      }),
    onSuccess: refresh,
  });

  return (
    <div className="grid gap-4 py-2 md:grid-cols-2">
      <div className="space-y-2">
        <div className="text-sm font-medium">Change price</div>
        <div className="flex flex-wrap gap-2">
          <select className="h-9 rounded-md border px-2 text-sm" value={vendorId} onChange={(e) => setVendorId(Number(e.target.value))}>
            {product.vendors.map((v) => (
              <option key={v.vendor_id} value={v.vendor_id}>
                {v.vendor_name}
              </option>
            ))}
          </select>
          <Input className="w-28" type="number" step="0.01" placeholder="₹" value={price} onChange={(e) => setPrice(e.target.value)} />
          <Input className="w-56" placeholder="Reason" value={reason} onChange={(e) => setReason(e.target.value)} />
          <Button onClick={() => newPrice.mutate()} disabled={!price || !reason.trim() || newPrice.isPending}>
            Save price
          </Button>
        </div>
        <div className="text-sm font-medium">Details</div>
        <div className="flex flex-wrap gap-2">
          <Input className="w-32" placeholder="HSN" value={hsn} onChange={(e) => setHsn(e.target.value)} />
          <Input className="w-80" placeholder="Aliases, comma separated" value={aliases} onChange={(e) => setAliases(e.target.value)} />
          <Button variant="outline" onClick={() => update.mutate()} disabled={update.isPending}>
            Save details
          </Button>
        </div>
        {(newPrice.error ?? update.error) && (
          <p className="text-sm text-destructive">{(newPrice.error ?? update.error)?.message}</p>
        )}
      </div>
      <div>
        <div className="text-sm font-medium">Price history</div>
        {history.data &&
          Object.entries(history.data).map(([vendor, prices]) => (
            <div key={vendor} className="mt-1 text-sm">
              <div className="font-medium">{vendor}</div>
              {prices.map((p) => (
                <div key={p.id} className="text-muted-foreground">
                  ₹{money(p.price)} from {p.effective_from}
                  {p.effective_to ? ` to ${p.effective_to}` : " (current)"} · {p.source}
                  {p.reason ? ` · ${p.reason}` : ""}
                </div>
              ))}
            </div>
          ))}
      </div>
    </div>
  );
}
