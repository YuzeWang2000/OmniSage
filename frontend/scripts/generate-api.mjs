import { mkdir, writeFile } from "node:fs/promises";

import openapiTS, { astToString } from "openapi-typescript";

const source = process.env.VITE_OPENAPI_URL || new URL("../../openapi.json", import.meta.url);
const output = new URL("../src/api/schema.d.ts", import.meta.url);
const schema = await openapiTS(source instanceof URL ? source : new URL(source));

await mkdir(new URL("../src/api/", import.meta.url), { recursive: true });
await writeFile(output, astToString(schema), "utf8");

console.log(`Generated API types from ${source}`);
