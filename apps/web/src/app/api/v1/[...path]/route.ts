// Server-side proxy to the FastAPI service. Keeps API_TOKEN out of the browser.
import { NextRequest } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const PASS_HEADERS = ["content-type", "content-disposition", "content-length"];

export const dynamic = "force-dynamic";

async function proxy(req: NextRequest, { params }: { params: { path: string[] } }) {
  const target = `${API_URL}/api/v1/${params.path.map(encodeURIComponent).join("/")}${req.nextUrl.search}`;
  const headers: Record<string, string> = {};
  const type = req.headers.get("content-type");
  if (type) headers["content-type"] = type;
  if (process.env.API_TOKEN) headers["authorization"] = `Bearer ${process.env.API_TOKEN}`;

  const hasBody = !["GET", "HEAD"].includes(req.method);
  const upstream = await fetch(target, {
    method: req.method,
    headers,
    body: hasBody ? await req.arrayBuffer() : undefined,
    cache: "no-store",
  });
  const out = new Headers();
  for (const name of PASS_HEADERS) {
    const value = upstream.headers.get(name);
    if (value) out.set(name, value);
  }
  return new Response(upstream.body, { status: upstream.status, headers: out });
}

export { proxy as GET, proxy as POST, proxy as PUT, proxy as PATCH, proxy as DELETE };
