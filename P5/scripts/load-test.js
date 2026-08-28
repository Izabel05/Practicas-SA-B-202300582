import http from "k6/http";
import { check } from "k6";

const baseUrl = __ENV.BASE_URL || "http://192.168.49.2:32140";
const endpoints = [
  "/health/auth",
  "/health/catalogo",
  "/health/prestamos",
  "/health/multas",
];

export const options = {
  scenarios: {
    gateway_load: {
      executor: "ramping-vus",
      startVUs: 10,
      stages: [
        { duration: "30s", target: 50 },
        { duration: "45s", target: 200 },
        { duration: "60s", target: 400 },
        { duration: "30s", target: 0 },
      ],
      gracefulRampDown: "10s",
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<1000"],
  },
};

export default function () {
  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const response = http.get(`${baseUrl}${endpoint}`, {
    headers: { Host: "biblioteca.local" },
    timeout: "5s",
  });

  check(response, {
    "respuesta HTTP 200": (result) => result.status === 200,
  });
}
