"use client";

import { useQuery } from "@tanstack/react-query";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Table, Td, Th } from "@/components/ui/table";
import { api, downloadUrl } from "@/lib/api";
import type { Product, Vendor } from "@/lib/types";

export default function PriceListsPage() {
  const vendors = useQuery({ queryKey: ["vendors"], queryFn: () => api<Vendor[]>("/vendors") });
  const products = useQuery({ queryKey: ["products", "all"], queryFn: () => api<Product[]>("/products?limit=500") });
  const count = (vendorId: number) =>
    products.data?.filter((p) => p.vendors.some((v) => v.vendor_id === vendorId)).length ?? 0;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Price verification</h1>
      <p className="text-sm text-muted-foreground">
        Download a vendor&apos;s price sheet (SNO, Product, Price, GST %, HSN; no quantities) and email it yourself.
        Sending from the app and accepting replies come in the next slices.
      </p>
      <Table>
        <thead>
          <tr>
            <Th>Vendor</Th>
            <Th>Products linked</Th>
            <Th />
          </tr>
        </thead>
        <tbody>
          {vendors.data?.map((v) => (
            <tr key={v.id}>
              <Td>{v.name}</Td>
              <Td>{count(v.id)}</Td>
              <Td className="text-right">
                {count(v.id) > 0 && (
                  <a href={downloadUrl(`/price-lists/vendors/${v.id}.xlsx`)}>
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4" /> Price sheet
                    </Button>
                  </a>
                )}
              </Td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}
