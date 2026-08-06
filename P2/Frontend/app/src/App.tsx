import SessionExpiredModal from "./components/SessionExpiredModal";
import WelcomeModal from "./components/WelcomeModal";
import AppRoutes from "./routes";

export default function App() {
  return (
    <>
      <AppRoutes />
      <SessionExpiredModal />
      <WelcomeModal />
    </>
  );
}