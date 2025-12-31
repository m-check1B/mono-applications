// vite.config.ts
import { sveltekit } from "file:///home/adminmatej/github/applications/focus-kraliki/frontend/node_modules/.pnpm/@sveltejs+kit@2.48.5_@sveltejs+vite-plugin-svelte@3.1.2_svelte@4.2.20_vite@5.4.21_@type_33401171a35f7828aeb5619dac2d5661/node_modules/@sveltejs/kit/src/exports/vite/index.js";
import { defineConfig } from "file:///home/adminmatej/github/applications/focus-kraliki/frontend/node_modules/.pnpm/vite@5.4.21_@types+node@24.10.1/node_modules/vite/dist/node/index.js";
var vite_config_default = defineConfig({
  plugins: [sveltekit()],
  server: {
    port: 5e3,
    host: "0.0.0.0",
    strictPort: true,
    allowedHosts: true,
    hmr: {
      clientPort: 443
    },
    proxy: {
      "/api": {
        target: "http://127.0.0.1:3017",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "")
      }
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvaG9tZS9hZG1pbm1hdGVqL2dpdGh1Yi9hcHBsaWNhdGlvbnMvZm9jdXMtbGl0ZS9mcm9udGVuZFwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiL2hvbWUvYWRtaW5tYXRlai9naXRodWIvYXBwbGljYXRpb25zL2ZvY3VzLWxpdGUvZnJvbnRlbmQvdml0ZS5jb25maWcudHNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL2hvbWUvYWRtaW5tYXRlai9naXRodWIvYXBwbGljYXRpb25zL2ZvY3VzLWxpdGUvZnJvbnRlbmQvdml0ZS5jb25maWcudHNcIjtpbXBvcnQgeyBzdmVsdGVraXQgfSBmcm9tICdAc3ZlbHRlanMva2l0L3ZpdGUnO1xuaW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSc7XG5cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG4gICAgICAgIHBsdWdpbnM6IFtzdmVsdGVraXQoKV0sXG4gICAgICAgIHNlcnZlcjoge1xuICAgICAgICAgICAgICAgIHBvcnQ6IDUwMDAsXG4gICAgICAgICAgICAgICAgaG9zdDogJzAuMC4wLjAnLFxuICAgICAgICAgICAgICAgIHN0cmljdFBvcnQ6IHRydWUsXG4gICAgICAgICAgICAgICAgYWxsb3dlZEhvc3RzOiB0cnVlLFxuICAgICAgICAgICAgICAgIGhtcjoge1xuICAgICAgICAgICAgICAgICAgICAgICAgY2xpZW50UG9ydDogNDQzXG4gICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgICAgICBwcm94eToge1xuICAgICAgICAgICAgICAgICAgICAgICAgJy9hcGknOiB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHRhcmdldDogJ2h0dHA6Ly8xMjcuMC4wLjE6MzAxNycsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgcmV3cml0ZTogKHBhdGgpID0+IHBhdGgucmVwbGFjZSgvXlxcL2FwaS8sICcnKVxuICAgICAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgfVxufSk7XG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQTBWLFNBQVMsaUJBQWlCO0FBQ3BYLFNBQVMsb0JBQW9CO0FBRTdCLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQ3BCLFNBQVMsQ0FBQyxVQUFVLENBQUM7QUFBQSxFQUNyQixRQUFRO0FBQUEsSUFDQSxNQUFNO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixZQUFZO0FBQUEsSUFDWixjQUFjO0FBQUEsSUFDZCxLQUFLO0FBQUEsTUFDRyxZQUFZO0FBQUEsSUFDcEI7QUFBQSxJQUNBLE9BQU87QUFBQSxNQUNDLFFBQVE7QUFBQSxRQUNBLFFBQVE7QUFBQSxRQUNSLGNBQWM7QUFBQSxRQUNkLFNBQVMsQ0FBQyxTQUFTLEtBQUssUUFBUSxVQUFVLEVBQUU7QUFBQSxNQUNwRDtBQUFBLElBQ1I7QUFBQSxFQUNSO0FBQ1IsQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K
