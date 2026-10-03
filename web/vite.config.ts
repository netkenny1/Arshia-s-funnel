import { defineConfig } from "vite";
import arshiaData, { loadData } from "./plugins/arshia-data.ts";

export default defineConfig(({ command }) => {
  const { base } = loadData(process.cwd());
  return {
    base: command === "build" ? base : "/",
    plugins: [arshiaData()],
    build: { target: "es2022", outDir: "dist", emptyOutDir: true, sourcemap: false, assetsInlineLimit: 0 },
    server: { port: 5173, host: true },
  };
});
