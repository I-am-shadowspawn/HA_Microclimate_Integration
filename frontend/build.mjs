import { build } from "esbuild";
import { readFile, writeFile } from "node:fs/promises";
await build({
  entryPoints: ["src/index.ts"],
  bundle: true,
  format: "esm",
  target: "es2022",
  minify: true,
  legalComments: "eof",
  outfile:
    "../custom_components/microclimate_integration/frontend/microclimate-cards.js",
});
let notices = "Microclimate cards — bundled third-party notices\n\n";
for (const pkg of ["lit", "lit-element", "lit-html", "@lit/reactive-element"]) {
  const metadata = JSON.parse(
    await readFile(`node_modules/${pkg}/package.json`, "utf8"),
  );
  notices += `${pkg} ${metadata.version}\n${await readFile(`node_modules/${pkg}/LICENSE`, "utf8")}\n\n`;
}
await writeFile(
  "../custom_components/microclimate_integration/frontend/THIRD_PARTY_NOTICES.txt",
  notices,
);
