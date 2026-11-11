"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input, Select } from "@/components/ui/input";
import { Table, Td, Th } from "@/components/ui/table";
import { api } from "@/lib/api";
import type { Line, Product, Requisition } from "@/lib/types";
import { money, qty } from "@/lib/utils";

type Patch = { qty?: string; vendor_id?: number; price?: string; price_reason?: string };

export function LinesTable({ requisition }: { requisition: Requisition }) {
  const qc = useQueryClient();
  const editable = requisition.status === "draft";
  // Whole catalogue is small (hundreds of rows): load once for the vendor dropdowns.
  const catalogue = useQuery({
    queryKey: ["products", "all"],
    queryFn: () => api<Product[]>("/products?limit=500"),
  });
  const byId = new Map(catalogue.data?.map((p) => [p.id, p]));

  const onDone = (data: Requisition) => {
    qc.setQueryData(["requisition", requisition.id], data);
    qc.invalidateQueries({ queryKey: ["month"] });
  };
  const patch = useMutation({
    mutationFn: ({ id, body }: { id: number; body: Patch }) =>
      api<Requisition>(`/requisitions/${requisition.id}/lines/${id}`, { method: "PATCH", json: body }),
    onSuccess: onDone,
  });
  const remove = useMutation({
    mutationFn: (id: number) =>
      api<Requisition>(`/requisitions/${requisition.id}/lines/${id}`, { method: "DELETE" }),
    onSuccess: onDone,
  });

  if (requisition.lines.length === 0) {
    return <p className="py-6 text-center text-sm text-muted-foreground">No products yet for this site.</p>;
  }

  return (
    <div className="space-y-2">
      {(patch.error || remove.error) && (
        <p className="text-sm text-destructive">{(patch.error ?? remove.error)?.message}</p>
      )}
      <Table>
        <thead>
          <tr>
            <Th>Product</Th>
            <Th className="w-24">Qty</Th>
            <Th>Unit</Th>
            <Th className="w-56">Vendor</Th>
            <Th className="text-right">Per cost</Th>
            <Th className="text-center">GST</Th>
            <Th className="text-right">Taxable</Th>
            <Th className="text-right">GST amt</Th>
            <Th className="text-right">Total</Th>
            <Th />
          </tr>
        </thead>
        <tbody>
          {requisition.lines.map((line) => (
            <LineRow
              key={line.id}
              line={line}
              product={byId.get(line.product_id)}
              editable={editable}
              onPatch={(body) => patch.mutate({ id: line.id, body })}
              onRemove={() => remove.mutate(line.id)}
            />
          ))}
          <tr className="font-semibold">
            <Td colSpan={6} className="text-right">
              Site total
            </Td>
            <Td className="text-right">{money(requisition.totals.taxable)}</Td>
            <Td className="text-right">{money(requisition.totals.gst)}</Td>
            <Td className="text-right">{money(requisition.totals.total)}</Td>
            <Td />
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

function LineRow({
  line,
  product,
  editable,
  onPatch,
  onRemove,
}: {
  line: Line;
  product: Product | undefined;
  editable: boolean;
  onPatch: (body: Patch) => void;
  onRemove: () => void;
}) {
  const [amount, setAmount] = useState(qty(line.qty_required));
  const [priceEdit, setPriceEdit] = useState<{ price: string; reason: string } | null>(null);
  const vendors = product?.vendors ?? [{ vendor_id: line.vendor_id, vendor_name: line.vendor_name }];

  return (
    <>
      <tr>
        <Td>{line.product_name}</Td>
        <Td>
          {editable ? (
            <Input
              type="number"
              min="0"
              step="any"
              className="h-8"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              onBlur={() => Number(amount) > 0 && amount !== qty(line.qty_required) && onPatch({ qty: amount })}
            />
          ) : (
            qty(line.qty_required)
          )}
        </Td>
        <Td>{line.unit}</Td>
        <Td>
          {editable && vendors.length > 1 ? (
            <Select
              className="h-8"
              value={line.vendor_id}
              onChange={(e) => onPatch({ vendor_id: Number(e.target.value) })}
            >
              {vendors.map((v) => (
                <option key={v.vendor_id} value={v.vendor_id}>
                  {v.vendor_name}
                </option>
              ))}
            </Select>
          ) : (
            line.vendor_name
          )}
        </Td>
        <Td className="text-right">
          {editable ? (
            <button
              className="underline decoration-dotted underline-offset-2 hover:text-primary"
              title="Change price (saved to price history)"
              onClick={() => setPriceEdit({ price: line.price, reason: "" })}
            >
              {money(line.price)}
            </button>
          ) : (
            money(line.price)
          )}
        </Td>
        <Td className="text-center">{Number(line.gst_rate)}%</Td>
        <Td className="text-right">{money(line.taxable_amount)}</Td>
        <Td className="text-right">{money(line.gst_amount)}</Td>
        <Td className="text-right">{money(line.line_total)}</Td>
        <Td>
          {editable && (
            <Button variant="ghost" size="icon" onClick={onRemove} title="Remove">
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </Td>
      </tr>
      {priceEdit && (
        <tr className="bg-muted/50">
          <Td colSpan={10}>
            <div className="flex flex-wrap items-center gap-2 text-sm">
              New price for {line.product_name} from {line.vendor_name}:
              <Input
                className="h-8 w-28"
                type="number"
                step="0.01"
                value={priceEdit.price}
                onChange={(e) => setPriceEdit({ ...priceEdit, price: e.target.value })}
              />
              <Input
                className="h-8 w-72"
                placeholder="Reason (required, kept in history)"
                value={priceEdit.reason}
                onChange={(e) => setPriceEdit({ ...priceEdit, reason: e.target.value })}
              />
              <Button
                size="sm"
                disabled={!priceEdit.reason.trim() || priceEdit.price === ""}
                onClick={() => {
                  onPatch({ price: priceEdit.price, price_reason: priceEdit.reason });
                  setPriceEdit(null);
                }}
              >
                Save price
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setPriceEdit(null)}>
                Cancel
              </Button>
            </div>
          </Td>
        </tr>
      )}
    </>
  );
}
