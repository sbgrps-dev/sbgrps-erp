"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const links = [
  { href: "/stocks/requisitions", label: "Requisitions" },
  { href: "/stocks/products", label: "Products & prices" },
  { href: "/stocks/vendors", label: "Vendors" },
  { href: "/stocks/price-lists", label: "Price lists" },
];

export function Nav() {
  const path = usePathname();
  return (
    <nav className="flex flex-col gap-1 text-sm">
      <div className="px-2 pb-1 text-xs font-semibold uppercase text-muted-foreground">Stocks</div>
      {links.map((l) => (
        <Link
          key={l.href}
          href={l.href}
          className={cn(
            "rounded-md px-2 py-1.5 hover:bg-accent",
            path.startsWith(l.href) && "bg-accent font-medium",
          )}
        >
          {l.label}
        </Link>
      ))}
    </nav>
  );
}
