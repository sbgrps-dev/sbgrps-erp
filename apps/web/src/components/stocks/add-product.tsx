"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input, Select } from "@/components/ui/input";
import { api } from "@/lib/api";
import type { Product, Requisition, Vendor } from "@/lib/types";
import { money } from "@/lib/utils";

function useDebounced<T>(value: T, ms = 250): T {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), ms);
    return () => clearTimeout(t);
  }, [value, ms]);
  return v;
}

export function AddProduct({ requisition }: { requisition: Requisition }) {
  const qc = useQueryClient();
  const [q, setQ] = useState("");
  const [picked, setPicked] = useState<Product | null>(null);
  const [amount, setAmount] = useState("");
  const [creating, setCreating] = useState(false);
  const term = useDebounced(q.trim());

  const results = useQuery({
    queryKey: ["products", "search", term],
    queryFn: () => api<Product[]>(`/products?q=${encodeURIComponent(term)}&limit=12`),
    enabled: term.length >= 2 && !picked,
  });

  const add = useMutation({
    mutationFn: (body: { product_id: number; qty: string }) =>
      api<Requisition>(`/requisitions/${requisition.id}/lines`, { method: "POST", json: body }),
    onSuccess: (data) => {
      qc.setQueryData(["requisition", requisition.id], data);
      qc.invalidateQueries({ queryKey: ["month"] });
      setQ("");
      setPicked(null);
      setAmount("");
    },
  });

  const submit = () => {
    if (picked && Number(amount) > 0) add.mutate({ product_id: picked.id, qty: amount });
  };

  if (creating) {
    return (
      <NewProductForm
        initialName={q}
        onCancel={() => setCreating(false)}
        onCreated={(p) => {
          setCreating(false);
          setPicked(p);
          setQ(p.name);
        }}
      />
    );
  }

  const preferred = picked?.vendors.find((v) => v.is_preferred) ?? picked?.vendors[0];

  return (
    <div className="relative flex flex-wrap items-end gap-2">
      <div className="relative w-80">
        <label className="text-xs text-muted-foreground">+ Add product</label>
        <Input
          placeholder="Search: apc, gloves, sterix..."
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setPicked(null);
          }}
        />
        {!picked && term.length >= 2 && (
          <div className="absolute z-10 mt-1 w-[28rem] rounded-md border bg-background shadow-lg">
            {results.data?.map((p) => {
              const v = p.vendors.find((x) => x.is_preferred) ?? p.vendors[0];
              return (
                <button
                  key={p.id}
                  className="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-accent"
                  onClick={() => {
                    setPicked(p);
                    setQ(p.name);
                  }}
                >
                  <span>
                    {p.name} <span className="text-muted-foreground">({p.unit})</span>
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {v ? `${v.vendor_name} · ₹${money(v.current_price)}` : "no vendor"}
                  </span>
                </button>
              );
            })}
            {results.data?.length === 0 && (
              <div className="px-3 py-2 text-sm text-muted-foreground">No match.</div>
            )}
            <button
              className="w-full border-t px-3 py-2 text-left text-sm text-primary hover:bg-accent"
              onClick={() => setCreating(true)}
            >
              + New product “{q.trim()}”
            </button>
          </div>
        )}
      </div>
      <div className="w-28">
        <label className="text-xs text-muted-foreground">Qty {picked ? `(${picked.unit})` : ""}</label>
        <Input
          type="number"
          min="0"
          step="any"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          disabled={!picked}
        />
      </div>
      <Button onClick={submit} disabled={!picked || !(Number(amount) > 0) || add.isPending}>
        Add
      </Button>
      {preferred && (
        <span className="pb-2 text-xs text-muted-foreground">
          {preferred.vendor_name} · ₹{money(preferred.current_price)} · GST {Number(picked!.gst_rate)}%
        </span>
      )}
      {add.error && <span className="pb-2 text-xs text-destructive">{add.error.message}</span>}
    </div>
  );
}

function NewProductForm({
  initialName,
  onCancel,
  onCreated,
}: {
  initialName: string;
  onCancel: () => void;
  onCreated: (p: Product) => void;
}) {
  const vendors = useQuery({ queryKey: ["vendors"], queryFn: () => api<Vendor[]>("/vendors") });
  const [form, setForm] = useState({ name: initialName, unit: "Nos", gst_rate: "18", vendor_id: "", price: "" });
  const create = useMutation({
    mutationFn: () =>
      api<Product>("/products", {
        method: "POST",
        json: {
          name: form.name,
          unit: form.unit,
          gst_rate: form.gst_rate,
          vendors: [{ vendor_id: Number(form.vendor_id), price: form.price, is_preferred: true }],
        },
      }),
    onSuccess: onCreated,
  });
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) =>
    setForm({ ...form, [k]: e.target.value });

  return (
    <div className="rounded-md border bg-muted/40 p-3">
      <div className="mb-2 text-sm font-medium">New product (added to the master catalogue)</div>
      <div className="flex flex-wrap items-end gap-2">
        <Input className="w-64" placeholder="Name" value={form.name} onChange={set("name")} />
        <Input className="w-24" placeholder="Unit" value={form.unit} onChange={set("unit")} />
        <Select className="w-24" value={form.gst_rate} onChange={set("gst_rate")}>
          {["18", "12", "5", "28", "0"].map((r) => (
            <option key={r} value={r}>
              GST {r}%
            </option>
          ))}
        </Select>
        <Select className="w-56" value={form.vendor_id} onChange={set("vendor_id")}>
          <option value="">Vendor…</option>
          {vendors.data?.map((v) => (
            <option key={v.id} value={v.id}>
              {v.name}
            </option>
          ))}
        </Select>
        <Input className="w-28" type="number" step="0.01" placeholder="Price ₹" value={form.price} onChange={set("price")} />
        <Button
          onClick={() => create.mutate()}
          disabled={!form.name || !form.unit || !form.vendor_id || form.price === "" || create.isPending}
        >
          Create
        </Button>
        <Button variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
      </div>
      {create.error && <p className="mt-2 text-xs text-destructive">{create.error.message}</p>}
    </div>
  );
}
