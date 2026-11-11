// Mirrors apps/api/app/schemas. Money and quantities are decimal strings.

export type Totals = { taxable: string; gst: string; total: string };

export type Site = { id: number; code: string; display_name: string; is_active: boolean; sort_order: number };

export type Vendor = {
  id: number;
  name: string;
  address: string | null;
  gstin: string | null;
  emails: string[];
  phones: string[];
  website: string | null;
  drug_licence: string | null;
  products_supplied: string | null;
  is_active: boolean;
};

export type ProductVendor = {
  vendor_id: number;
  vendor_name: string;
  is_preferred: boolean;
  current_price: string | null;
};

export type Product = {
  id: number;
  code: string;
  name: string;
  aliases: string[];
  unit: string;
  hsn: string | null;
  gst_rate: string;
  is_active: boolean;
  vendors: ProductVendor[];
};

export type Price = {
  id: number;
  price: string;
  effective_from: string;
  effective_to: string | null;
  source: string;
  reason: string | null;
};

export type Line = {
  id: number;
  product_id: number;
  product_name: string;
  vendor_id: number;
  vendor_name: string;
  qty_required: string;
  unit: string;
  price: string;
  gst_rate: string;
  taxable_amount: string;
  gst_amount: string;
  line_total: string;
  notes: string | null;
};

export type Requisition = {
  id: number;
  site_id: number;
  site_name: string;
  month: string;
  status: string;
  saved_at: string | null;
  sent_at: string | null;
  sent_via: string | null;
  notes: string | null;
  lines: Line[];
  totals: Totals;
};

export type MonthSiteSummary = {
  site_id: number;
  site_code: string;
  site_name: string;
  requisition_id: number | null;
  status: string | null;
  line_count: number;
  totals: Totals;
};

export type MonthSummary = { month: string; sites: MonthSiteSummary[]; totals: Totals };

export type PreviewLine = {
  sno: number;
  product_name: string;
  qty: string;
  unit: string;
  price: string;
  gst_rate: string;
  taxable: string;
  gst: string;
  total: string;
};

export type Preview = {
  month: string;
  title: string;
  filename: string;
  sites: {
    site_id: number;
    site_name: string;
    vendors: { vendor_id: number; vendor_name: string; lines: PreviewLine[] }[];
    totals: Totals;
  }[];
  vendors: { vendor_id: number; name: string; gstin: string | null; emails: string[]; phones: string[] }[];
  totals: Totals;
};

export type Workbook = {
  id: number;
  month: string;
  scope: "site" | "month";
  requisition_id: number | null;
  site_ids: number[];
  version: number;
  filename: string;
  grand_total: string;
  created_at: string;
};
