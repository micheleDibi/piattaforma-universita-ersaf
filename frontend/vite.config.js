import process from "node:process";
import { defineConfig, loadEnv } from "vite";
import react, { reactCompilerPreset } from "@vitejs/plugin-react";
import babel from "@rolldown/plugin-babel";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Proxy facoltativo per lo sviluppo. Con ERSAF_API_PROXY impostata, per
  // esempio in un .env.collaudo locale escluso da git, le chiamate a /api
  // partono dal server di sviluppo verso quell'indirizzo: il browser parla
  // solo con localhost, quindi niente CORS. Senza la variabile non cambia nulla.
  const env = loadEnv(mode, process.cwd(), "");
  const proxy = env.ERSAF_API_PROXY
    ? { "/api": { target: env.ERSAF_API_PROXY, changeOrigin: true, secure: true } }
    : undefined;

  return {
    plugins: [
      tailwindcss(),
      react(),
      babel({ presets: [reactCompilerPreset()] }),
    ],
    server: proxy ? { proxy } : undefined,
  };
});
