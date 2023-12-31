// vite.config.ts
import { defineConfig } from "file:///C:/Users/LocalUser/Desktop/LeeForster_ElEquantPy/thesis_frontend/node_modules/vite/dist/node/index.js";
import react from "file:///C:/Users/LocalUser/Desktop/LeeForster_ElEquantPy/thesis_frontend/node_modules/@vitejs/plugin-react/dist/index.mjs";
var vite_config_default = defineConfig({
  plugins: [react({
    include: [/\.tsx?$/]
  })],
  server: {
    host: true,
    port: 3e3,
    proxy: {
      "/backend": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/backend/, "")
      }
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxMb2NhbFVzZXJcXFxcRGVza3RvcFxcXFxMZWVGb3JzdGVyX0VsRXF1YW50UHlcXFxcdGhlc2lzX2Zyb250ZW5kXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxMb2NhbFVzZXJcXFxcRGVza3RvcFxcXFxMZWVGb3JzdGVyX0VsRXF1YW50UHlcXFxcdGhlc2lzX2Zyb250ZW5kXFxcXHZpdGUuY29uZmlnLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9DOi9Vc2Vycy9Mb2NhbFVzZXIvRGVza3RvcC9MZWVGb3JzdGVyX0VsRXF1YW50UHkvdGhlc2lzX2Zyb250ZW5kL3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcclxuaW1wb3J0IHJlYWN0IGZyb20gJ0B2aXRlanMvcGx1Z2luLXJlYWN0J1xyXG5cclxuLy8gaHR0cHM6Ly92aXRlanMuZGV2L2NvbmZpZy9cclxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcclxuICBwbHVnaW5zOiBbcmVhY3Qoe1xyXG4gICAgaW5jbHVkZTogWy9cXC50c3g/JC9dLFxyXG4gIH0pXSxcclxuICBzZXJ2ZXI6IHtcclxuICAgIGhvc3Q6IHRydWUsXHJcbiAgICBwb3J0OiAzMDAwLFxyXG4gIHByb3h5OiB7XHJcbiAgICBcIi9iYWNrZW5kXCI6IHtcclxuICAgICAgdGFyZ2V0OiBcImh0dHA6Ly8xMjcuMC4wLjE6NTAwMFwiLFxyXG4gICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXHJcbiAgICAgIHJld3JpdGU6IChwYXRoKSA9PiBwYXRoLnJlcGxhY2UoL15cXC9iYWNrZW5kLywgXCJcIilcclxuICAgIH1cclxuICB9XHJcbn1cclxufSlcclxuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUE4WCxTQUFTLG9CQUFvQjtBQUMzWixPQUFPLFdBQVc7QUFHbEIsSUFBTyxzQkFBUSxhQUFhO0FBQUEsRUFDMUIsU0FBUyxDQUFDLE1BQU07QUFBQSxJQUNkLFNBQVMsQ0FBQyxTQUFTO0FBQUEsRUFDckIsQ0FBQyxDQUFDO0FBQUEsRUFDRixRQUFRO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDUixPQUFPO0FBQUEsTUFDTCxZQUFZO0FBQUEsUUFDVixRQUFRO0FBQUEsUUFDUixjQUFjO0FBQUEsUUFDZCxTQUFTLENBQUMsU0FBUyxLQUFLLFFBQVEsY0FBYyxFQUFFO0FBQUEsTUFDbEQ7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUNBLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
