import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import { Nav } from "@/components/nav";

export const metadata: Metadata = {
  title: "SBGRPS ERP",
  description: "Shree Balaji Groups ERP",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <div className="flex min-h-screen">
            <aside className="w-52 shrink-0 border-r bg-muted/40 p-3">
              <div className="mb-4 px-2 text-sm font-bold">SBGRPS ERP</div>
              <Nav />
            </aside>
            <main className="min-w-0 flex-1 p-6">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
