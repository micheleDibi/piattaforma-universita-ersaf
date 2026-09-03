import { useState } from "react";
import { useNavigate } from "react-router";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          utente_username: username,
          utente_password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          const errorMessages = data.detail
            .map((err) => `${err.loc.join(".")}: ${err.msg}`)
            .join(", ");
          throw new Error(errorMessages);
        }
        throw new Error(data.detail || "Credenziali non valide");
      }

      console.log("Login effettuato con successo:", data);

      localStorage.setItem("utente_id", data.utente_id);
      localStorage.setItem("ruolo_codice", data.ruolo_codice);

      if (data.ruolo_codice === "nazionale") {
        navigate("/nazionale");
      } else {
        navigate("/home");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4">
        <div className="relative w-full max-w-md transform overflow-hidden rounded-2xl bg-white px-14 py-5 text-left shadow-xl transition-all border-2 border-blue-900">
          <div className="mb-6 text-center">
            <h5 className="text-2xl  tracking-tight text-blue-900">Accedi</h5>
          </div>

          {error && (
            <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-200">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm  text-blue-900">Username</label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="janesmith"
                className="mt-1 block w-full rounded-full border border-gray-300 px-3 py-2 text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm  text-blue-900">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1 block w-full rounded-full border border-gray-300 px-3 py-2 text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 rounded-full bg-indigo-600 py-2.5 px-4 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 transition-colors disabled:opacity-50"
            >
              {loading ? "Accesso in corso..." : "Entra"}
            </button>
            <div className="flex items-center justify-center text-sm pt-1">
              <a
                href="#forgot-password"
                onClick={(e) => {
                  e.preventDefault();
                  console.log("Password dimenticata cliccata");
                }}
              >
                Hai dimenticato la password?
              </a>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}

export default Login;
