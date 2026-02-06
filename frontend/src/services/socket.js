import { io } from "socket.io-client";

export const createAnalyticsSocket = () => {
  const token = localStorage.getItem("token");
  return io(import.meta.env.VITE_API_URL || "http://localhost:8000", {
    path: "/ws/analytics",
    transports: ["websocket"],
    auth: {
      token
    }
  });
};
