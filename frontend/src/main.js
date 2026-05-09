import { createRoot } from "https://esm.sh/react-dom@18.2.0/client";
import { e } from "./ui/react.js";
import App from "./App.js";

createRoot(document.getElementById("root")).render(e(App));
