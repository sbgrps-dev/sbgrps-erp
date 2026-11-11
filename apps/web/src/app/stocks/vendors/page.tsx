"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { Vendor } from "@/lib/types";

export default function VendorsPage() {
  const vendors = useQuery({ queryKey: ["vendors"], queryFn: () => api<Vendor[]>("/vendors") });
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Vendors</h1>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {vendors.data?.map((v) => (
          <Card key={v.id}>
            <CardHeader>
              <CardTitle className="text-base">{v.name}</CardTitle>
              {v.gstin && <div className="font-mono text-xs text-muted-foreground">GSTIN {v.gstin}</div>}
            </CardHeader>
            <CardContent className="space-y-1 text-sm">
              {v.address && <div className="whitespace-pre-line">{v.address}</div>}
              {v.emails.length > 0 && <div>{v.emails.join(", ")}</div>}
              {v.phones.length > 0 && <div>{v.phones.join(", ")}</div>}
              {v.website && <div>{v.website}</div>}
              {v.drug_licence && <div>Drug licence: {v.drug_licence}</div>}
              {v.products_supplied && (
                <div className="text-muted-foreground">Supplies: {v.products_supplied.split("\n").join(", ")}</div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
