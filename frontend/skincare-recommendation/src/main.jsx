import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { AuthProvider } from "./authUser";   // اضافه کن

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AuthProvider>   {/* حتما دور کل اپ پیچیده بشه */}
      <App />
    </AuthProvider>
  </StrictMode>
);
