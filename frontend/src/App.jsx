import { useState } from "react";
import AuthPortal from "./components/AuthPortal";
import JarvisDashboard from "./components/JarvisDashboard";

function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    const storedUser = localStorage.getItem("jarvis.currentUser");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  function handleAuthenticated(user) {
    localStorage.setItem("jarvis.currentUser", JSON.stringify(user));
    setCurrentUser(user);
  }

  function handleLogout() {
    localStorage.removeItem("jarvis.currentUser");
    setCurrentUser(null);
  }

  if (!currentUser) {
    return <AuthPortal onAuthenticated={handleAuthenticated} />;
  }

  return <JarvisDashboard currentUser={currentUser} onLogout={handleLogout} />;
}

export default App;
