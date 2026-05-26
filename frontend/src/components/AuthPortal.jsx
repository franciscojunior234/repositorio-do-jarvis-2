import { useMemo, useState } from "react";

const USERS_KEY = "jarvis.users";

const modes = {
  login: {
    title: "Acesso oficial",
    action: "Entrar",
    helper: "Entre com uma conta cadastrada para abrir o painel JARVIS.",
  },
  register: {
    title: "Cadastro",
    action: "Cadastrar",
    helper: "Crie uma conta para liberar uma nova licenca do sistema.",
  },
  recovery: {
    title: "Recuperacao",
    action: "Enviar acesso",
    helper: "Informe o email cadastrado para iniciar a recuperacao.",
  },
};

export default function AuthPortal({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("info");

  const activeMode = modes[mode];
  const registeredUsers = useMemo(() => readUsers(), []);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function switchMode(nextMode) {
    setMode(nextMode);
    setMessage("");
    setMessageType("info");
  }

  function submit(event) {
    event.preventDefault();

    if (mode === "login") {
      handleLogin();
      return;
    }

    if (mode === "register") {
      handleRegister();
      return;
    }

    handleRecovery();
  }

  function handleLogin() {
    const users = readUsers();
    const email = normalizeEmail(form.email);
    const user = users.find((item) => item.email === email);

    if (!user || user.password !== form.password) {
      showMessage("Email ou senha invalidos.", "error");
      return;
    }

    onAuthenticated({
      id: user.id,
      name: user.name,
      email: user.email,
      plan: user.plan,
    });
  }

  function handleRegister() {
    const users = readUsers();
    const name = form.name.trim();
    const email = normalizeEmail(form.email);

    if (!name || !email || !form.password || !form.confirmPassword) {
      showMessage("Preencha todos os campos para cadastrar.", "error");
      return;
    }

    if (!isValidEmail(email)) {
      showMessage("Informe um email valido.", "error");
      return;
    }

    if (form.password.length < 6) {
      showMessage("A senha precisa ter pelo menos 6 caracteres.", "error");
      return;
    }

    if (form.password !== form.confirmPassword) {
      showMessage("As senhas nao coincidem.", "error");
      return;
    }

    if (users.some((user) => user.email === email)) {
      showMessage("Ja existe uma conta com este email.", "error");
      return;
    }

    const user = {
      id: crypto.randomUUID(),
      name,
      email,
      password: form.password,
      plan: "Licenca inicial",
      createdAt: new Date().toISOString(),
    };

    writeUsers([...users, user]);

    onAuthenticated({
      id: user.id,
      name: user.name,
      email: user.email,
      plan: user.plan,
    });
  }

  function handleRecovery() {
    const email = normalizeEmail(form.email);
    const user = readUsers().find((item) => item.email === email);

    if (!email) {
      showMessage("Informe o email cadastrado.", "error");
      return;
    }

    if (!user) {
      showMessage("Nenhuma conta foi encontrada com este email.", "error");
      return;
    }

    showMessage(
      "Recuperacao registrada. Em producao, o link seria enviado por email.",
      "success",
    );
  }

  function showMessage(text, type) {
    setMessage(text);
    setMessageType(type);
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#030b14] text-cyan-100">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_35%,rgba(0,220,255,0.12),transparent_38%)]" />
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,255,0.035)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,255,0.035)_1px,transparent_1px)] bg-[size:46px_46px] opacity-25" />

      <section className="relative z-10 grid min-h-screen grid-cols-[minmax(360px,520px)_1fr]">
        <div className="flex flex-col justify-between border-r border-cyan-500/15 bg-[#05101b]/75 px-10 py-8 backdrop-blur-xl">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-full border border-cyan-300/40 bg-cyan-400/10 shadow-[0_0_30px_rgba(0,255,255,0.25)]">
                <span className="h-3 w-3 rounded-full bg-cyan-200 shadow-[0_0_18px_rgba(0,255,255,0.9)]" />
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.35em] text-cyan-400/70">
                  Interface oficial
                </p>
                <h1 className="text-3xl font-bold tracking-[0.28em] text-cyan-100">
                  J.A.R.V.I.S
                </h1>
              </div>
            </div>

            <div className="mt-12">
              <div className="grid grid-cols-3 overflow-hidden rounded-xl border border-cyan-500/15 bg-[#020812]/70 p-1">
                <ModeButton
                  active={mode === "login"}
                  label="Login"
                  onClick={() => switchMode("login")}
                />
                <ModeButton
                  active={mode === "register"}
                  label="Cadastro"
                  onClick={() => switchMode("register")}
                />
                <ModeButton
                  active={mode === "recovery"}
                  label="Senha"
                  onClick={() => switchMode("recovery")}
                />
              </div>

              <div className="mt-8">
                <h2 className="text-2xl font-semibold text-cyan-100">
                  {activeMode.title}
                </h2>
                <p className="mt-2 text-sm leading-6 text-cyan-200/60">
                  {activeMode.helper}
                </p>
              </div>

              <form className="mt-8 space-y-4" onSubmit={submit}>
                {mode === "register" && (
                  <Field
                    label="Nome completo"
                    name="name"
                    placeholder="Tony Stark"
                    value={form.name}
                    onChange={updateField}
                  />
                )}

                <Field
                  label="Email"
                  name="email"
                  placeholder="usuario@empresa.com"
                  type="email"
                  value={form.email}
                  onChange={updateField}
                />

                {mode !== "recovery" && (
                  <Field
                    label="Senha"
                    name="password"
                    placeholder="Minimo 6 caracteres"
                    type="password"
                    value={form.password}
                    onChange={updateField}
                  />
                )}

                {mode === "register" && (
                  <Field
                    label="Confirmar senha"
                    name="confirmPassword"
                    placeholder="Repita a senha"
                    type="password"
                    value={form.confirmPassword}
                    onChange={updateField}
                  />
                )}

                {message && (
                  <div
                    className={[
                      "rounded-xl border px-4 py-3 text-sm",
                      messageType === "error"
                        ? "border-red-400/30 bg-red-500/10 text-red-100"
                        : "border-emerald-400/30 bg-emerald-500/10 text-emerald-100",
                    ].join(" ")}
                  >
                    {message}
                  </div>
                )}

                <button className="w-full rounded-xl border border-cyan-300/30 bg-cyan-400/15 px-4 py-3 font-semibold text-cyan-50 shadow-[0_0_28px_rgba(0,255,255,0.14)] transition hover:border-cyan-200/60 hover:bg-cyan-400/25">
                  {activeMode.action}
                </button>
              </form>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 text-center">
            <StatusTile label="Usuarios" value={registeredUsers.length} />
            <StatusTile label="Status" value="Seguro" />
            <StatusTile label="Licenca" value="Ativa" />
          </div>
        </div>

        <div className="relative flex items-center justify-center overflow-hidden px-12">
          <div className="absolute h-[620px] w-[620px] rounded-full border border-cyan-500/10" />
          <div className="absolute h-[500px] w-[500px] animate-spin rounded-full border border-cyan-400/20 [animation-duration:28s]" />
          <div className="absolute h-[360px] w-[360px] animate-spin rounded-full border border-cyan-300/25 [animation-direction:reverse] [animation-duration:18s]" />
          <div className="absolute h-[210px] w-[210px] rounded-full border border-cyan-200/30 bg-cyan-400/5 shadow-[0_0_90px_rgba(0,255,255,0.32)]" />

          <div className="relative max-w-xl text-center">
            <p className="text-sm uppercase tracking-[0.45em] text-cyan-300/70">
              Controle de usuarios
            </p>
            <h2 className="mt-5 text-5xl font-bold tracking-[0.2em] text-cyan-50 drop-shadow-[0_0_20px_rgba(0,255,255,0.38)]">
              ACESSO RESTRITO
            </h2>
            <p className="mx-auto mt-5 max-w-md text-sm leading-7 text-cyan-100/60">
              Area de entrada para clientes, operadores e administradores antes
              da abertura do painel principal.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}

function ModeButton({ active, label, onClick }) {
  return (
    <button
      className={[
        "rounded-lg px-3 py-2 text-xs font-semibold transition",
        active
          ? "bg-cyan-400/18 text-cyan-50 shadow-[0_0_18px_rgba(0,255,255,0.12)]"
          : "text-cyan-300/60 hover:bg-cyan-500/10 hover:text-cyan-100",
      ].join(" ")}
      type="button"
      onClick={onClick}
    >
      {label}
    </button>
  );
}

function Field({ label, name, value, onChange, type = "text", placeholder }) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300/70">
        {label}
      </span>
      <input
        className="w-full rounded-xl border border-cyan-500/15 bg-[#020812]/90 px-4 py-3 text-sm text-cyan-50 outline-none transition placeholder:text-cyan-600/50 focus:border-cyan-300/50 focus:bg-[#05101b]"
        name={name}
        onChange={onChange}
        placeholder={placeholder}
        type={type}
        value={value}
      />
    </label>
  );
}

function StatusTile({ label, value }) {
  return (
    <div className="rounded-xl border border-cyan-500/15 bg-[#020812]/70 px-3 py-4">
      <div className="text-[10px] uppercase tracking-[0.2em] text-cyan-500/60">
        {label}
      </div>
      <div className="mt-2 text-sm font-semibold text-cyan-100">{value}</div>
    </div>
  );
}

function readUsers() {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY)) ?? [];
  } catch {
    return [];
  }
}

function writeUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function normalizeEmail(email) {
  return email.trim().toLowerCase();
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
